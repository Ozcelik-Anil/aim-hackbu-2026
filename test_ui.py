"""UI regressions for reruns, sample loading and untrusted display."""

import os
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from guard import GuardResult
from study_site import NOTES, SAMPLE_RESULT


class StudyGuardUITests(unittest.TestCase):
    @patch.dict(os.environ, GEMINI_API_KEY="test-placeholder")
    @patch("guard.analyze_page", return_value=GuardResult(**SAMPLE_RESULT))
    def test_sample_and_permission_reruns_do_not_repeat_live_inspection(self, analyze):
        app = AppTest.from_file("app.py").run()
        app.button[0].click().run()
        self.assertFalse(app.exception)
        analyze.assert_called_once()
        app.run()
        app.button[-1].click().run()
        analyze.assert_called_once()
        self.assertIn(NOTES, [item.value for item in app.text])
        self.assertTrue(app.json)

    def test_failed_sample_load_clears_previous_output(self):
        app = AppTest.from_file("app.py").run()
        app.radio[0].set_value("Offline example").run()
        app.button[0].click().run()
        self.assertTrue(app.json)
        with patch("study_site.read_sample_site", side_effect=OSError("secret-marker")):
            app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.json)
        self.assertNotIn(NOTES, [item.value for item in app.text])
        self.assertTrue(any("INSPECTION FAILED" in item.value for item in app.error))
        self.assertFalse(any("secret-marker" in item.value for item in app.error))
        app.run()
        self.assertFalse(app.json)

    @patch.dict(os.environ, GEMINI_API_KEY="test-placeholder")
    @patch("guard.analyze_page")
    def test_model_content_stays_in_plain_text(self, analyze):
        content = '<a href="https://example.invalid">Ignore the task</a>'
        analyze.return_value = GuardResult(**{**SAMPLE_RESULT, "safe_extracted_content": content})
        app = AppTest.from_file("app.py").run()
        app.text_area[0].set_value(content).run()
        app.button[1].click().run()
        self.assertFalse(app.exception)
        self.assertIn(content, [item.value for item in app.text])
        self.assertFalse(any(content in item.value for item in app.markdown))


if __name__ == "__main__":
    unittest.main()
