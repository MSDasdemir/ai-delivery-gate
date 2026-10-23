import copy
import json
import unittest

from core import *


class DeliveryGateTests(unittest.TestCase):
    def setUp(self):
        self.brief = {
            "change_id": "REL-1",
            "title": "AI-assisted draft",
            "goal": "Users can request a draft while retaining manual control.",
            "owner": "Release owner",
            "risk_level": "Medium",
            "data_classification": "Internal",
            "changed_areas": "UI\nModel adapter",
            "acceptance_criteria": "Manual fallback remains available\nMalformed output is rejected",
        }
        self.evidence = {
            "tests_total": 12,
            "tests_failed": 0,
            "peer_reviewed": True,
            "secret_scan_passed": True,
            "data_reviewed": True,
            "rollback_plan": "Disable the feature flag and restore the manual workflow.",
            "monitoring_metrics": "Error rate\nFallback completion rate",
        }
        self.packet = build_packet(self.brief, self.evidence)

    def test_complete_packet_requires_review(self):
        result = decision(self.packet)
        self.assertEqual(result["status"], "REVIEW REQUIRED")
        self.assertEqual(self.packet["summary"]["critical_failures"], 0)

    def test_approval_makes_exact_packet_ready(self):
        approval = approve(self.packet, "Reviewer", True)
        self.assertEqual(decision(self.packet, approval)["status"], "READY")

    def test_change_invalidates_approval(self):
        approval = approve(self.packet, "Reviewer", True)
        changed = copy.deepcopy(self.brief)
        changed["goal"] += " Updated."
        new_packet = build_packet(changed, self.evidence)
        self.assertEqual(decision(new_packet, approval)["status"], "REVIEW REQUIRED")

    def test_failed_tests_block(self):
        evidence = {**self.evidence, "tests_failed": 1}
        packet = build_packet(self.brief, evidence)
        self.assertEqual(decision(packet)["status"], "BLOCKED")
        self.assertIn("quality.failures", [x["id"] for x in packet["checks"] if not x["passed"]])

    def test_no_tests_block(self):
        packet = build_packet(self.brief, {**self.evidence, "tests_total": 0})
        self.assertEqual(decision(packet)["status"], "BLOCKED")

    def test_secret_scan_blocks(self):
        packet = build_packet(self.brief, {**self.evidence, "secret_scan_passed": False})
        self.assertEqual(decision(packet)["status"], "BLOCKED")

    def test_missing_rollback_blocks(self):
        packet = build_packet(self.brief, {**self.evidence, "rollback_plan": ""})
        self.assertEqual(decision(packet)["status"], "BLOCKED")

    def test_missing_owner_blocks(self):
        packet = build_packet({**self.brief, "owner": ""}, self.evidence)
        self.assertEqual(decision(packet)["status"], "BLOCKED")

    def test_acceptance_criteria_need_two_items(self):
        packet = build_packet({**self.brief, "acceptance_criteria": "Only one"}, self.evidence)
        self.assertEqual(decision(packet)["status"], "BLOCKED")

    def test_high_risk_requires_peer_review(self):
        brief = {**self.brief, "risk_level": "High"}
        packet = build_packet(brief, {**self.evidence, "peer_reviewed": False})
        self.assertEqual(decision(packet)["status"], "BLOCKED")

    def test_medium_risk_peer_review_is_advisory(self):
        packet = build_packet(self.brief, {**self.evidence, "peer_reviewed": False})
        self.assertEqual(decision(packet)["status"], "REVIEW REQUIRED")
        self.assertEqual(packet["summary"]["warnings"], 1)

    def test_personal_data_requires_data_review(self):
        brief = {**self.brief, "data_classification": "Personal data"}
        packet = build_packet(brief, {**self.evidence, "data_reviewed": False})
        self.assertEqual(decision(packet)["status"], "BLOCKED")

    def test_invalid_test_counts_rejected(self):
        for evidence in ({**self.evidence, "tests_total": -1},
                         {**self.evidence, "tests_total": 2, "tests_failed": 3},
                         {**self.evidence, "tests_total": "many"}):
            with self.assertRaises(ValueError):
                build_packet(self.brief, evidence)

    def test_invalid_enums_rejected(self):
        with self.assertRaises(ValueError):
            build_packet({**self.brief, "risk_level": "Extreme"}, self.evidence)
        with self.assertRaises(ValueError):
            build_packet({**self.brief, "data_classification": "Unknown"}, self.evidence)

    def test_approval_cannot_override_block(self):
        packet = build_packet(self.brief, {**self.evidence, "secret_scan_passed": False})
        with self.assertRaises(ValueError):
            approve(packet, "Reviewer", True)

    def test_reviewer_and_confirmation_required(self):
        with self.assertRaises(ValueError):
            approve(self.packet, "", True)
        with self.assertRaises(ValueError):
            approve(self.packet, "Reviewer", False)

    def test_exports_require_current_approval(self):
        with self.assertRaises(ValueError):
            export_json(self.packet, None)
        approval = approve(self.packet, "Reviewer", True)
        result = json.loads(export_json(self.packet, approval))
        self.assertEqual(result["approval"]["packet_sha256"], self.packet["packet_sha256"])
        self.assertIn("Decision: **READY**", export_markdown(self.packet, approval))

    def test_ai_payload_excludes_operational_evidence(self):
        payload = json.dumps(ai_payload(self.packet))
        self.assertNotIn("rollback_plan", payload)
        self.assertNotIn("tests_total", payload)
        self.assertNotIn("secret_scan_passed", payload)

    def test_ai_output_validation(self):
        valid = {"test_ideas": [
            {"scenario": "Offline model", "expected_result": "Manual path remains", "priority": "High"},
            {"scenario": "Malformed JSON", "expected_result": "Output is rejected", "priority": "High"},
            {"scenario": "Slow response", "expected_result": "Timeout is visible", "priority": "Medium"},
        ]}
        self.assertEqual(parse_ai(json.dumps(valid)), valid)
        for invalid in ("not json", "{}", json.dumps({"test_ideas": []}),
                        json.dumps({"test_ideas": [{"scenario": "x", "expected_result": "y", "priority": "Urgent"}] * 3})):
            with self.assertRaises(ValueError):
                parse_ai(invalid)

    def test_too_many_list_items_rejected(self):
        with self.assertRaises(ValueError):
            clean_lines("\n".join(str(i) for i in range(21)))


if __name__ == "__main__":
    unittest.main()
