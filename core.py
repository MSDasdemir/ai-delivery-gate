"""Deterministic release controls for AI-assisted software delivery."""
from datetime import datetime, timezone
import hashlib
import json


RISK_LEVELS = ("Low", "Medium", "High")
DATA_CLASSES = ("Public", "Internal", "Confidential", "Personal data")


def clean_lines(text, limit=20):
    lines = [line.strip().lstrip("-•* ").strip() for line in str(text).splitlines()]
    result = [line for line in lines if line]
    if len(result) > limit:
        raise ValueError(f"Use at most {limit} list items.")
    return result


def fingerprint(value):
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def _check(check_id, area, label, passed, critical, evidence, remediation):
    return {
        "id": check_id,
        "area": area,
        "label": label,
        "passed": bool(passed),
        "critical": bool(critical),
        "evidence": evidence,
        "remediation": remediation,
    }


def build_packet(brief, evidence):
    title = str(brief.get("title", "")).strip()
    change_id = str(brief.get("change_id", "")).strip()
    goal = str(brief.get("goal", "")).strip()
    owner = str(brief.get("owner", "")).strip()
    rollback = str(evidence.get("rollback_plan", "")).strip()
    acceptance = clean_lines(brief.get("acceptance_criteria", ""))
    metrics = clean_lines(evidence.get("monitoring_metrics", ""))
    changed_areas = clean_lines(brief.get("changed_areas", ""))
    risk = brief.get("risk_level")
    data_class = brief.get("data_classification")
    if risk not in RISK_LEVELS:
        raise ValueError("Choose a valid risk level.")
    if data_class not in DATA_CLASSES:
        raise ValueError("Choose a valid data classification.")
    try:
        tests_total = int(evidence.get("tests_total", 0))
        tests_failed = int(evidence.get("tests_failed", 0))
    except (TypeError, ValueError) as error:
        raise ValueError("Test counts must be whole numbers.") from error
    if tests_total < 0 or tests_failed < 0 or tests_failed > tests_total:
        raise ValueError("Test counts are inconsistent.")

    checks = [
        _check("brief.goal", "Definition", "Business outcome is explicit", len(goal) >= 20, True,
               goal or "No outcome supplied", "Describe the user or operational outcome and how success will be observed."),
        _check("brief.acceptance", "Definition", "Acceptance criteria are testable", len(acceptance) >= 2, True,
               f"{len(acceptance)} criterion/criteria", "Add at least two observable pass/fail criteria."),
        _check("brief.scope", "Definition", "Changed areas are bounded", 1 <= len(changed_areas) <= 10, False,
               f"{len(changed_areas)} changed area(s)", "List the services, screens or workflows affected by this change."),
        _check("quality.tests", "Quality", "Automated tests ran", tests_total > 0, True,
               f"{tests_total} executed", "Run automated tests that cover the changed behavior."),
        _check("quality.failures", "Quality", "Automated tests pass", tests_total > 0 and tests_failed == 0, True,
               f"{tests_failed} failed", "Resolve every failing test or document an approved exception outside this demo."),
        _check("quality.review", "Quality", "Change was independently reviewed", evidence.get("peer_reviewed") is True,
               risk == "High", "Confirmed" if evidence.get("peer_reviewed") else "Not confirmed",
               "Record an independent review, especially for a high-risk change."),
        _check("security.scan", "Data & security", "Secret scan passes", evidence.get("secret_scan_passed") is True, True,
               "Passed" if evidence.get("secret_scan_passed") else "Missing or failed",
               "Run a secret scan and remove exposed credentials before release."),
        _check("security.data", "Data & security", "Data handling was reviewed", evidence.get("data_reviewed") is True,
               data_class in ("Confidential", "Personal data"),
               f"Classification: {data_class}; review: {'yes' if evidence.get('data_reviewed') else 'no'}",
               "Review collection, access, retention and logging for the selected data class."),
        _check("operations.rollback", "Operations", "Rollback plan is actionable", len(rollback) >= 20, True,
               rollback or "No rollback plan", "Describe the trigger, owner and concrete rollback action."),
        _check("operations.monitoring", "Operations", "Post-release metrics are defined", len(metrics) >= 1, True,
               f"{len(metrics)} metric(s)", "Define at least one metric or alert and its observation window."),
        _check("ownership.owner", "Ownership", "Release owner is named", bool(owner), True,
               owner or "No owner", "Assign one person accountable for the release decision and follow-up."),
    ]
    failed_critical = [item for item in checks if item["critical"] and not item["passed"]]
    warnings = [item for item in checks if not item["critical"] and not item["passed"]]
    score = round(100 * sum(item["passed"] for item in checks) / len(checks))
    packet = {
        "schema_version": 1,
        "brief": {
            "change_id": change_id,
            "title": title,
            "goal": goal,
            "owner": owner,
            "risk_level": risk,
            "data_classification": data_class,
            "changed_areas": changed_areas,
            "acceptance_criteria": acceptance,
        },
        "evidence": {
            "tests_total": tests_total,
            "tests_failed": tests_failed,
            "peer_reviewed": evidence.get("peer_reviewed") is True,
            "secret_scan_passed": evidence.get("secret_scan_passed") is True,
            "data_reviewed": evidence.get("data_reviewed") is True,
            "rollback_plan": rollback,
            "monitoring_metrics": metrics,
        },
        "checks": checks,
        "summary": {
            "score": score,
            "passed": sum(item["passed"] for item in checks),
            "total": len(checks),
            "critical_failures": len(failed_critical),
            "warnings": len(warnings),
        },
        "mode": "Portfolio simulation — no deployment is triggered",
    }
    packet["packet_sha256"] = fingerprint(packet)
    return packet


def decision(packet, approval=None):
    failures = [item for item in packet["checks"] if item["critical"] and not item["passed"]]
    if failures:
        return {"status": "BLOCKED", "reason": f"{len(failures)} critical control(s) failed", "ready": False}
    if not approval or approval.get("packet_sha256") != packet.get("packet_sha256"):
        return {"status": "REVIEW REQUIRED", "reason": "Controls pass; this exact version needs human approval", "ready": False}
    return {"status": "READY", "reason": "Controls pass and this exact version is approved", "ready": True}


def approve(packet, reviewer, confirmed):
    if decision(packet)["status"] == "BLOCKED":
        raise ValueError("Resolve critical controls before approval.")
    reviewer = str(reviewer).strip()
    if not reviewer or not confirmed:
        raise ValueError("Reviewer name and explicit confirmation are required.")
    return {
        "packet_sha256": packet["packet_sha256"],
        "reviewer": reviewer,
        "approved_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Approval of this portfolio release packet only; no deployment authority",
    }


def export_json(packet, approval):
    if decision(packet, approval)["status"] != "READY":
        raise ValueError("Only the approved current version can be exported.")
    return json.dumps({"packet": packet, "approval": approval}, ensure_ascii=False, indent=2, allow_nan=False)


def export_markdown(packet, approval=None):
    verdict = decision(packet, approval)
    lines = [
        f"# Release gate — {packet['brief']['change_id'] or 'Unnumbered change'}",
        "",
        f"**{packet['brief']['title'] or 'Untitled change'}**",
        "",
        f"- Decision: **{verdict['status']}**",
        f"- Readiness score: **{packet['summary']['score']}%**",
        f"- Risk: {packet['brief']['risk_level']}",
        f"- Owner: {packet['brief']['owner'] or 'Unassigned'}",
        f"- Version: `{packet['packet_sha256'][:12]}`",
        "",
        "## Controls",
        "",
    ]
    for item in packet["checks"]:
        mark = "x" if item["passed"] else " "
        critical = " · critical" if item["critical"] else ""
        lines.append(f"- [{mark}] **{item['label']}**{critical} — {item['evidence']}")
    lines.extend(["", "## Decision rationale", "", verdict["reason"], ""])
    if approval and approval.get("packet_sha256") == packet["packet_sha256"]:
        lines.extend([f"Approved by **{approval['reviewer']}** at `{approval['approved_at']}`.", ""])
    return "\n".join(lines)


def ai_payload(packet):
    """Only bounded metadata goes to the optional local model; no source code or secrets."""
    return {
        "title": packet["brief"]["title"],
        "goal": packet["brief"]["goal"],
        "risk_level": packet["brief"]["risk_level"],
        "data_classification": packet["brief"]["data_classification"],
        "changed_areas": packet["brief"]["changed_areas"],
        "acceptance_criteria": packet["brief"]["acceptance_criteria"],
        "failed_control_ids": [item["id"] for item in packet["checks"] if not item["passed"]],
    }


def ai_schema():
    item = {
        "type": "object",
        "properties": {
            "scenario": {"type": "string"},
            "expected_result": {"type": "string"},
            "priority": {"type": "string", "enum": ["High", "Medium", "Low"]},
        },
        "required": ["scenario", "expected_result", "priority"],
        "additionalProperties": False,
    }
    return {"type": "object", "properties": {"test_ideas": {"type": "array", "minItems": 3, "maxItems": 6, "items": item}},
            "required": ["test_ideas"], "additionalProperties": False}


def parse_ai(text):
    try:
        data = json.loads(text)
        ideas = data["test_ideas"]
        if not isinstance(ideas, list) or not 3 <= len(ideas) <= 6:
            raise ValueError("Wrong item count")
        for idea in ideas:
            if idea.get("priority") not in ("High", "Medium", "Low"):
                raise ValueError("Invalid priority")
            for key in ("scenario", "expected_result"):
                if not isinstance(idea.get(key), str) or not idea[key].strip() or len(idea[key]) > 500:
                    raise ValueError("Invalid text")
        return data
    except (ValueError, KeyError, TypeError) as error:
        raise ValueError("AI output did not match the test-idea format. The deterministic gate remains available.") from error
