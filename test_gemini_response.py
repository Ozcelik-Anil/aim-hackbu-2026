"""Exercise the Gemini response boundary without a network call or real key."""

import json
import os
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

from guard import analyze_page
from study_site import NOTES, SAMPLE_RESULT


class GeminiResponseTests(unittest.TestCase):
    @patch.dict(os.environ, GEMINI_API_KEY="unit-test-placeholder")
    @patch("google.genai.Client")
    def test_rejects_invalid_responses(self, client):
        generate = client.return_value.__enter__.return_value.models.generate_content
        for response in (
            None,
            "broken json",
            json.dumps({"has_malicious_instruction": True}),
            json.dumps({**SAMPLE_RESULT, "has_malicious_instruction": "true"}),
            json.dumps({**SAMPLE_RESULT, "blocked_action": ""}),
            json.dumps({**SAMPLE_RESULT, "reason": " "}),
            json.dumps({**SAMPLE_RESULT, "extra": "untrusted instruction"}),
        ):
            with self.subTest(response=response):
                generate.return_value.text = response
                with self.assertRaises(ValueError):
                    analyze_page("A fictional study page.")

    @patch.dict(os.environ, GEMINI_API_KEY="unit-test-placeholder")
    @patch("google.genai.Client")
    def test_failed_second_inspection_clears_previous_notes(self, client):
        generate = client.return_value.__enter__.return_value.models.generate_content
        clean = {**SAMPLE_RESULT, "has_malicious_instruction": False, "blocked_action": "", "reason": "Lesson facts only."}
        generate.return_value.text = json.dumps(clean)
        ui = AppTest.from_file("app.py").run()
        ui.text_area[0].set_value(NOTES).run()
        ui.button[1].click().run()
        self.assertTrue(ui.success)
        self.assertIn(NOTES, [entry.value for entry in ui.text])

        generate.return_value.text = "{"
        ui.button[1].click().run()
        self.assertTrue(ui.error)
        self.assertFalse(ui.exception)
        self.assertFalse(ui.json)
        self.assertNotIn(NOTES, [entry.value for entry in ui.text])
        self.assertEqual(generate.call_count, 2)
