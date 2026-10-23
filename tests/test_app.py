import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run(timeout=30)

    def test_default_flow_approval_and_invalidation(self):
        self.assertFalse(self.app.exception)
        self.assertTrue(any("REVIEW REQUIRED" in item.value for item in self.app.markdown))
        approve_button = next(button for button in self.app.button if button.label == "Approve this release packet")
        self.assertTrue(approve_button.disabled)
        next(field for field in self.app.text_input if field.label == "Reviewer name").set_value("Demo reviewer").run()
        next(box for box in self.app.checkbox if box.label.startswith("I reviewed the change")).check().run()
        next(button for button in self.app.button if button.label == "Approve this release packet").click().run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("exact version is approved" in item.value for item in self.app.success))
        next(area for area in self.app.text_area if area.label == "Business outcome").set_value(
            "A changed business outcome that requires a fresh review and approval."
        ).run()
        self.assertTrue(any("changed after approval" in item.value for item in self.app.warning))

    def test_failed_test_blocks_approval(self):
        next(number for number in self.app.number_input if number.label == "Automated tests failed").set_value(1).run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("BLOCKED" in item.value for item in self.app.markdown))
        approve_button = next(button for button in self.app.button if button.label == "Approve this release packet")
        self.assertTrue(approve_button.disabled)


if __name__ == "__main__":
    unittest.main()
