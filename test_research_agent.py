import unittest
from unittest.mock import patch

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
        ]
        model.side_effect = [Plan(queries=["research topic"]), Report(findings=[
            Finding(text="Supported", source_numbers=[1]), Finding(text="Invalid citation", source_numbers=[2])])]
        sources, findings, _ = investigate("question", "test-key", lambda msg: None)
        self.assertEqual([f.text for f in findings], ["Supported"])
        self.assertEqual(model.call_args.args[2]["evidence"], {1: "Useful fact"})
        self.assertEqual(guard.call_count, len(sources))
        self.assertIn("unavailable", sources[2]["status"])
