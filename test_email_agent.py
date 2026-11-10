"""Small offline test suite. Run: python -m unittest -v"""

import unittest
from email_agent_core import analyze_offline, validate_ai_result


class InboxGuardTests(unittest.TestCase):
    def test_ordinary_course_announcement_is_low_risk(self):
        result = analyze_offline(
            "Tutorial room update",
            "Course Team <course-team@university.example>",
            "The tutorial is in Room 2407 on Friday. No reply is required.",
        )
        self.assertEqual(result["risk_level"], "Low")
        self.assertEqual(result["category"], "School / Work")

    def test_password_request_with_pressure_and_link_is_high_risk(self):
        body = "Verify your account immediately at https://login.example.net."
        result = analyze_offline("Account warning", "IT <it@example.net>", body)
        self.assertEqual(result["risk_level"], "High")
        self.assertTrue(any(s["evidence"] == "Verify your account" for s in result["signals"]))

    def test_bank_detail_change_is_flagged(self):
        result = analyze_offline(
            "Invoice update",
            "Finance <finance@example.org>",
            "We have new bank details. Please confirm by replying.",
        )
        self.assertIn(result["risk_level"], {"Medium", "High"})
        self.assertTrue(any("financial" in s["why_it_matters"].lower() for s in result["signals"]))

    def test_link_is_not_described_as_proof_of_maliciousness(self):
        result = analyze_offline(
            "Event page",
            "Society <events@example.org>",
            "Details are here: https://events.example.org/meeting",
        )
        link_signal = next(s for s in result["signals"] if s["signal"] == "A link is included")
        self.assertIn("not automatically malicious", link_signal["why_it_matters"])

    def test_newsletter_is_low_priority(self):
        result = analyze_offline(
            "Weekly newsletter",
            "Society <updates@example.org>",
            "Weekly update. Unsubscribe from future newsletters.",
        )
        self.assertEqual(result["priority"], "Low")
        self.assertEqual(result["category"], "Marketing")

    def test_ai_evidence_not_in_email_is_removed(self):
        result = validate_ai_result(
            {
                "category": "School / Work",
                "priority": "Urgent",
                "risk_level": "High",
                "summary": "Check this email.",
                "requested_actions": ["Verify your password"],
                "signals": [
                    {"signal": "Password request", "evidence": "invented phrase", "why_it_matters": "Could be risky."},
                    {"signal": "Urgency", "evidence": "urgent", "why_it_matters": "Pressure."},
                ],
                "recommended_action": "Verify independently.",
                "reply_draft": "Please confirm through our usual channel.",
            },
            "quick note",
            "sender@example.com",
            "Please call me.",
        )
        self.assertEqual(len(result["signals"]), 0)
        self.assertEqual(result["risk_level"], "Medium")


if __name__ == "__main__":
    unittest.main()
