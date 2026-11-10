# InboxGuard — Email Triage and Safety-Checking Agent

A Streamlit prototype for a chatbot/agent competition. A reviewer pastes an email and receives:

- likely category and priority;
- a risk assessment;
- the actions requested by the email;
- warning signals supported by exact quotations from the submitted text;
- a cautious next step and an optional reply draft.

## Important scope

This version analyzes text pasted by the reviewer. It does **not** connect to Gmail or Outlook, authenticate senders, look up domain reputation, browse links, inspect attachments, or send replies. The score is decision support, not a guarantee that an email is genuine.

There are two modes:

1. **AI analysis:** uses the OpenAI Responses API. The pasted email text is sent to the API. API usage may incur charges.
2. **Offline checks:** uses simple keyword and URL heuristics. It does not call an AI API and is available without an API key. This is not an AI model and is deliberately labelled as such.

Use fictional or anonymized content for reviewer testing. Never commit an API key to GitHub.

## Run locally

Use Python 3.10 or newer.

```bash
python -m venv .venv
```

Activate it:

- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\\Scripts\\Activate.ps1`

Install packages and start the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app opens at the local URL shown in the terminal. Without a key, choose **Offline checks**.

To enable AI analysis, set an environment variable before starting Streamlit:

macOS/Linux:

```bash
export OPENAI_API_KEY="your-key"
streamlit run app.py
```

Windows PowerShell:

```powershell
$env:OPENAI_API_KEY="your-key"
streamlit run app.py
```

The default model is `gpt-5.5`. To use another model available to your API account, set `EMAIL_AGENT_MODEL` or change the Model field in the sidebar. Model/API availability and pricing depend on your account.

## Deploy a public reviewer demo

1. Create a GitHub repository and upload `app.py`, `email_agent_core.py`, and `requirements.txt` (the test and documentation files can also be included).
2. Open Streamlit Community Cloud at <https://share.streamlit.io/> and choose **Create app**.
3. Select the repository, branch, and `app.py` as the entrypoint.
4. In **Advanced settings → Secrets**, add the following only if you want AI mode:

   ```toml
   OPENAI_API_KEY = "your-key"
   EMAIL_AGENT_MODEL = "gpt-5.5"
   ```

5. Deploy, open the public app URL in a private/incognito window, and test it without being signed in as the developer. Keep the app available throughout the review window.

Do not put `.streamlit/secrets.toml` or any API key in the GitHub repository. Streamlit documents its dependency and secrets handling here:

- <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy>
- <https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management>

## Run the offline tests

```bash
python -m unittest -v
```

These tests cover the offline logic and evidence validation. The AI API path needs a valid key and was not covered by the offline test suite.
