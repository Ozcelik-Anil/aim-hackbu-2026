"""Research audit trail, rerun and failure regression checks."""
import json
import os
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from guard import GuardResult
from research_agent import Finding, Plan, Report, Source, investigate


def source(number, status, verdict=None):
    return {"number": number, "title": "Fictional lesson", "url": "https://example.invalid/lesson",
            "status": status, "excerpt": "<script>untrusted example</script>", "verdict": verdict}


@patch("research_agent.wait_for_model", lambda progress: None)
class ResearchEvidenceTests(unittest.TestCase):
    @patch("research_agent.genai.Client")
    @patch("research_agent.model_json")
    @patch("research_agent.scholarly", return_value=[])
    @patch("research_agent.encyclopedia")
    @patch("research_agent.analyze_page")
    @patch("research_agent.MAX_SOURCES", 3)
    def test_evidence_records_match_guard_input_and_fail_closed(self, guard, wiki, papers, model, client):
        wiki.return_value = [Source("Lesson", f"https://example.invalid/{i}", str(i)) for i in range(3)]
        verdict = GuardResult(has_malicious_instruction=True, blocked_action="Send credentials",
                              reason="Outside read-only task", safe_extracted_content="A useful fact")
        guard.side_effect = [verdict, ValueError("private error"), ValueError("private error"),
                             GuardResult(has_malicious_instruction=False, blocked_action="",
                                         reason="No lesson facts", safe_extracted_content="")]
        model.return_value = Plan(queries=["topic"])
        sources, findings, _ = investigate("topic", "fictional-key", lambda _: None)
        self.assertEqual(len(sources), 3)
        self.assertEqual(sources[0]["excerpt"], guard.call_args_list[0].args[0])
        self.assertEqual(sources[0]["verdict"], verdict.model_dump())
        self.assertIsNone(sources[1]["verdict"])
        self.assertNotIn("private error", str(sources))
        self.assertIn("no usable notes", sources[2]["status"])
        self.assertFalse(findings)
        model.assert_called_once()  # No unapproved evidence reaches synthesis.

    @patch.dict(os.environ, GEMINI_API_KEY="fictional-key")
    @patch("research_agent.investigate")
    def test_research_displays_audit_without_extra_calls(self, run):
        verdict = {"has_malicious_instruction": True, "blocked_action": "Send password",
                   "reason": "Beyond read-only permissions", "safe_extracted_content": "Lesson fact"}
        run.return_value = ([source(1, "Excluded: suspicious instruction", verdict)], [], [])
        app = AppTest.from_file("app.py").run()
        app.text_input[0].set_value("Explain binary search")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertIn(verdict, [j.value if isinstance(j.value, dict) else json.loads(j.value) for j in app.json])
        self.assertIn("<script>untrusted example</script>", [t.value for t in app.text])
        app.run()
        run.assert_called_once()

    @patch.dict(os.environ, GEMINI_API_KEY="fictional-key")
    @patch("research_agent.investigate")
    def test_failed_research_clears_prior_evidence(self, run):
        run.return_value = ([source(1, "Checked")], [Finding(text="Old finding", source_numbers=[1])], [])
        app = AppTest.from_file("app.py").run()
        app.text_input[0].set_value("A question")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        run.side_effect = RuntimeError("private-key-marker")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.json)
        self.assertFalse(app.text)
        self.assertNotIn("research_result", app.session_state)
        self.assertFalse(any("private-key-marker" in e.value for e in app.error))

    @patch.dict(os.environ, GEMINI_API_KEY="fictional-key")
    @patch("research_agent.investigate")
    def test_failed_guard_is_not_shown_as_clean(self, run):
        run.return_value = ([source(1, "Excluded: guard unavailable")], [], [])
        app = AppTest.from_file("app.py").run()
        app.text_input[0].set_value("A question")
        app.button[0].click().run()
        self.assertFalse(app.exception)
        self.assertTrue(any("INSPECTION UNAVAILABLE" in w.value for w in app.warning))
        self.assertFalse(app.success)
        self.assertFalse(app.json)
