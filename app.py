"""InboxGuard — a Streamlit email triage and safety-checking demo."""

from __future__ import annotations

import os
import streamlit as st

from email_agent_core import analyze_offline, analyze_with_ai

st.set_page_config(
    page_title="InboxGuard | Email Check Agent",
    page_icon="📬",
    layout="wide",
)

SAMPLES = {
    "Course announcement (low-risk example)": {
        "subject": "COMP2711 tutorial room update",
        "sender": "Course Team <course-team@university.example>",
        "body": (
            "Hello everyone,\n\n"
            "This week's tutorial will take place in Room 2407 on Friday at 2:00 pm. "
            "Please bring your lecture notes. No reply is required.\n\n"
            "Best,\nCourse Team"
        ),
    },
    "Account warning (suspicious example)": {
        "subject": "URGENT: account suspended — verify your account",
        "sender": "IT Helpdesk <helpdesk@university-login.example.net>",
        "body": (
            "Your account will be locked. Verify your account immediately and sign in "
            "within 24 hours using this link: https://university-login.example.net/verify\n\n"
            "If you do not act now, access may be suspended.\nIT Support"
        ),
    },
    "Unexpected payment request (suspicious example)": {
        "subject": "Urgent payment update",
        "sender": "Finance Office <finance-office@example.org>",
        "body": (
            "Please arrange the payment today. We have new bank details for this invoice. "
            "Send payment to the updated account immediately and reply when complete.\n\n"
            "Thank you."
        ),
    },
    "Promotional newsletter (low-priority example)": {
        "subject": "Weekly student society newsletter",
        "sender": "Student Society <updates@society.example>",
        "body": (
            "Here is this week's society newsletter with upcoming events and announcements. "
            "You can unsubscribe from future weekly updates using the preferences page."
        ),
    },
}


def get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "")
    try:
        key = key or st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        # No local secrets file is normal during first-time setup.
        pass
    return str(key).strip()


def render_analysis(result: dict, mode_label: str) -> None:
    st.markdown("### Analysis")
    st.caption(mode_label)

    risk = result.get("risk_level", "Unknown")
    priority = result.get("priority", "Unknown")
    category = result.get("category", "Unknown")
    c1, c2, c3 = st.columns(3)
    c1.metric("Risk assessment", risk)
    c2.metric("Priority", priority)
    c3.metric("Category", category)

    st.markdown("**Summary**")
    st.write(result.get("summary") or "No summary returned.")

    st.markdown("**Requested actions detected**")
    actions = result.get("requested_actions") or []
    if actions:
        for action in actions:
            st.markdown(f"- {action}")
    else:
        st.write("No clear requested action was detected.")

    st.markdown("**Signals and supporting evidence**")
    signals = result.get("signals") or []
    if signals:
        for index, signal in enumerate(signals, start=1):
            with st.expander(f"{index}. {signal.get('signal', 'Observation')}", expanded=True):
                evidence = signal.get("evidence") or "No direct quotation supplied."
                st.markdown(f"> {evidence}")
                st.write(signal.get("why_it_matters", ""))
    else:
        st.success("No specific warning signals were identified in the supplied text.")

    st.markdown("**Recommended next action**")
    st.write(result.get("recommended_action") or "No recommendation was returned.")

    draft = result.get("reply_draft", "")
    if draft:
        st.markdown("**Suggested reply (review before using)**")
        st.code(draft, language=None)

    st.warning(
        "This is a decision-support tool, not an email-authentication service. "
        "A low-risk result does not prove that a message is genuine. Do not click links, "
        "open unexpected attachments, or share passwords or payment details based only on this analysis."
    )


st.title("📬 InboxGuard")
st.subheader("Email triage and safety-checking agent")
st.write(
    "Paste an email to identify its likely purpose, priority, possible risk indicators, "
    "and a cautious next step. InboxGuard only analyzes text that you provide."
)

api_key = get_api_key()
with st.sidebar:
    st.header("Settings")
    mode_options = ["AI analysis (OpenAI API)", "Offline checks (no AI API call)"]
    default_mode = 0 if api_key else 1
    mode = st.radio("Analysis mode", mode_options, index=default_mode)
    model_name = st.text_input(
        "Model",
        value=os.getenv("EMAIL_AGENT_MODEL", "gpt-5.5"),
        help="Used only in AI analysis mode. The API may incur usage charges.",
    )
    if api_key:
        st.success("OpenAI API key detected")
    else:
        st.info("No API key detected. Offline checks are ready; add a key to enable AI analysis.")
    st.divider()
    st.markdown("**Limitations**")
    st.caption(
        "The prototype does not access Gmail or Outlook, verify sender domains, "
        "visit websites, inspect attachments, or send replies."
    )

st.markdown("### Try a sample email")
sc1, sc2 = st.columns([3, 1])
with sc1:
    sample_name = st.selectbox("Sample scenario", list(SAMPLES.keys()))
with sc2:
    st.write("")
    st.write("")
    if st.button("Load sample", use_container_width=True):
        sample = SAMPLES[sample_name]
        st.session_state["email_subject"] = sample["subject"]
        st.session_state["email_sender"] = sample["sender"]
        st.session_state["email_body"] = sample["body"]
        st.session_state.pop("last_result", None)
        st.rerun()

st.markdown("### Email to check")
subject = st.text_input("Subject", key="email_subject", placeholder="Enter the email subject")
sender = st.text_input("Sender name or email address", key="email_sender", placeholder="sender@example.com")
body = st.text_area(
    "Email body",
    key="email_body",
    height=250,
    placeholder="Paste the email text here. Remove private information before using real messages.",
)

st.caption(
    "Privacy: use fictional or anonymized emails for the class demo. In AI mode, the text "
    "you submit is sent to the configured OpenAI API for analysis. In Offline mode, no AI API is called."
)

if st.button("Check this email", type="primary", use_container_width=True):
    st.session_state.pop("last_result", None)
    if not (subject.strip() or sender.strip() or body.strip()):
        st.error("Enter at least a subject, sender, or email body first.")
    elif len(body) > 12000:
        st.error("Please shorten the email body to 12,000 characters or fewer.")
    else:
        with st.spinner("Checking the email..."):
            try:
                if mode == "AI analysis (OpenAI API)":
                    if not api_key:
                        st.error("AI analysis needs an OpenAI API key. Add OPENAI_API_KEY in your app secrets or choose Offline checks.")
                        st.stop()
                    result = analyze_with_ai(subject, sender, body, api_key=api_key, model=model_name.strip() or "gpt-5.5")
                    mode_label = f"AI-assisted analysis · {model_name.strip() or 'gpt-5.5'}"
                else:
                    result = analyze_offline(subject, sender, body)
                    mode_label = "Offline heuristic checks · not an AI model"
                st.session_state["last_result"] = result
                st.session_state["last_mode_label"] = mode_label
            except Exception as exc:
                st.error(f"The analysis could not be completed: {exc}")

if "last_result" in st.session_state:
    st.divider()
    render_analysis(st.session_state["last_result"], st.session_state.get("last_mode_label", ""))

with st.expander("How to interpret the result"):
    st.markdown(
        "- **High risk:** multiple or serious warning indicators were found. Pause and verify through a channel you already trust.\n"
        "- **Medium risk:** at least one indicator needs checking. Do not rely on the email's own links or contact details.\n"
        "- **Low risk:** the checker found few matching indicators; this is not proof of authenticity.\n\n"
        "The offline mode uses simple phrase and URL patterns. It can miss new scams and can flag legitimate messages. "
        "The AI mode can also make mistakes. A human should compare each warning with the original email and a trusted source."
    )

st.markdown("---")
st.caption("InboxGuard prototype · Built for reviewer testing · No automatic email actions")
