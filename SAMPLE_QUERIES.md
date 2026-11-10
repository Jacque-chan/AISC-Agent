# Reviewer Starting Scenarios

1. **Routine course email:** Load “Course announcement (low-risk example)”. Does the agent correctly identify the main information and avoid inventing a warning?
2. **Account-verification email:** Load “Account warning (suspicious example)”. Which exact phrases and URL make the message worth checking? Does the agent avoid claiming that the sender has been verified?
3. **Changed bank details:** Load “Unexpected payment request (suspicious example)”. Does it identify the payment request and recommend confirmation through a known channel?
4. **Newsletter:** Load “Promotional newsletter (low-priority example)”. Does it distinguish low priority from security risk?
5. **Reviewer-created edge case:** Paste a legitimate email that contains an ordinary link, then one that uses urgent language but asks for no password or payment. Compare the evidence and note any false positive or missed warning.

For AI mode, run the same inputs again and compare the AI's specific quotations and recommended actions with the original email text. Do not treat the AI's own confidence or explanation as proof; the reviewer must verify each claim against the supplied message.
