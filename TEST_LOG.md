# InboxGuard — Prototype Test Log

**Test scope:** Six unit tests were run on the offline checker and AI-output evidence validator using fictional emails. The live AI API path was not tested because it requires an API key; the team must test it separately before enabling AI mode for reviewers.

A routine course announcement with a room number and date was classified as low risk and School / Work, as expected. An account-verification email combining a password request, urgent wording, and a URL was rated high risk; the checker displayed an exact phrase from the message. A changed-bank-details request was flagged for review, not called a confirmed scam. An ordinary event-page URL generated a link warning, but the explanation stated that a link alone does not prove malicious activity. A student-society newsletter was categorized as Marketing and assigned low priority.

The sixth test checked evidence validation. It supplied quotations absent from the source email. The validator removed them and downgraded the High-risk label when no directly supported evidence remained. This helps reviewers compare each warning with the original message rather than accept fabricated evidence.

A key limitation is that keyword rules can miss unfamiliar wording and flag legitimate messages. The interface labels offline mode as heuristic, not AI, and warns that low risk does not prove authenticity. The prototype also cannot verify sender identity, inspect attachments, or determine a link's destination. These features were excluded because they require extra integrations and raise privacy and security concerns. Instead, the agent recommends confirmation through a previously trusted channel and never opens links or sends replies.

**Release decision:** The offline logic passed all six unit tests and is suitable for a controlled classroom demo. Before release, the team should test AI mode with its own API key, check the hosted app in a private browser window, and confirm that no credentials are committed to GitHub.
