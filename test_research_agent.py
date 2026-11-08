import unittest
from unittest.mock import patch
from google.genai.errors import APIError

from guard import GuardResult
from research_agent import Finding, Plan, Report, Source, investigate


class ResearchTests(unittest.TestCase):
    @patch("research_agent.genai.Client")
    @patch("research_agent.model_json")
    @patch("research_agent.encyclopedia")
    @patch("research_agent.scholarly", return_value=[])
    @patch("research_agent.analyze_page")
    def test_only_checked_notes_reach_report(self, guard, papers, wiki, model, client):
        wiki.return_value = [Source(str(i), f"https://en.wikipedia.org/?curid={i}", text)
                             for i, text in enumerate(["article", "attack", "unreadable"], 1)]
        guard.side_effect = [
            GuardResult(has_malicious_instruction=False, blocked_action="", reason="Lesson", safe_extracted_content="Useful fact"),
            GuardResult(has_malicious_instruction=True, blocked_action="Send data", reason="Outside task", safe_extracted_content="Excluded text"),
            ValueError("invalid guard response"),
            ValueError("invalid guard response"),
        ]
        model.side_effect = [Plan(queries=["research topic"]), Report(findings=[
            Finding(text="Supported", source_numbers=[1]), Finding(text="Invalid citation", source_numbers=[2])])]
        sources, findings, _ = investigate("question", "test-key", lambda msg: None)
        self.assertEqual([f.text for f in findings], ["Supported"])
        self.assertEqual(model.call_args.args[2]["evidence"], {1: "Useful fact"})
        self.assertEqual(guard.call_count, len(sources) + 1)
        self.assertIn("invalid response after retry", sources[2]["status"])

    @patch("research_agent.genai.Client")
    @patch("research_agent.model_json")
    @patch("research_agent.scholarly", return_value=[])
    @patch("research_agent.encyclopedia")
    @patch("research_agent.analyze_page")
    def test_quota_switches_once_and_rechecks_the_same_source(self, guard, wiki, papers, model, clients):
        wiki.return_value = [Source("Title", "https://en.wikipedia.org/?curid=1", "Excerpt")]
        model.side_effect = [Plan(queries=["topic"]), Report(findings=[])]
        quota = APIError(429, {"error": {"message": "Rate limit"}})
        guard.side_effect = [quota, quota]
        sources, findings, warnings = investigate("topic", "primary", lambda _: None, "backup")
        self.assertEqual([c.args[1] for c in guard.call_args_list], ["primary", "backup"])
        self.assertEqual(guard.call_args_list[0].args[0], guard.call_args_list[1].args[0])
        self.assertIn("HTTP 429", sources[0]["status"])
        self.assertTrue(warnings)
        self.assertFalse(findings)

        guard.reset_mock(side_effect=True)
        guard.side_effect = [quota, GuardResult(has_malicious_instruction=False, blocked_action="",
            reason="OK", safe_extracted_content="Checked fact")]
        model.side_effect = [Plan(queries=["topic"]), Report(findings=[Finding(text="Fact", source_numbers=[1])])]
        sources, findings, _ = investigate("topic", "primary", lambda _: None, "backup")
        self.assertEqual(sources[0]["status"], "Checked")
        self.assertEqual(findings[0].text, "Fact")

        wiki.return_value.append(Source("Second", "https://en.wikipedia.org/?curid=2", "Unchecked text"))
        guard.side_effect = [GuardResult(has_malicious_instruction=False, blocked_action="",
            reason="OK", safe_extracted_content="Checked fact"), quota, quota]
        model.side_effect = [Plan(queries=["topic"])]
        sources, findings, warnings = investigate("topic", "primary", lambda _: None, "backup")
        self.assertEqual([(f.text, f.source_numbers) for f in findings], [("Checked fact", [1])])
        self.assertIn("HTTP 429", sources[1]["status"])
