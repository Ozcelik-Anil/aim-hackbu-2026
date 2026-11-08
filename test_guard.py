import unittest

from streamlit.testing.v1 import AppTest

from guard import GuardResult, run_action
from study_site import NOTES, SAMPLE_RESULT, TRAP


class StudyGuardTests(unittest.TestCase):
    def test_false_negative_cannot_authorize_a_form(self):
        missed_attack = GuardResult(**{**SAMPLE_RESULT, "has_malicious_instruction": False, "blocked_action": ""})
        with self.assertRaises(PermissionError):
            run_action("submit_form", missed_attack)

    def test_offline_sample_and_changed_input(self):
        app = AppTest.from_file("pages/1_Source_Inspector.py").run()
        app.radio[0].set_value("Offline example").run()
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertIn(NOTES, [entry.value for entry in app.text])
        self.assertFalse(any(TRAP in entry.value for entry in app.text))
        app.button[-1].click().run()
        self.assertIn("The study task only permits local note display.", [x.value for x in app.error])
        app.text_area[0].set_value("different page").run()
        self.assertFalse(app.json)


if __name__ == "__main__":
    unittest.main()
