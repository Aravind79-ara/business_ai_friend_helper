import streamlit as st
from openai import OpenAIError

from app.services.chat_agent import ChatConfigurationError, prepare_chat, stream_chat_answer
from app.services.inbox_agent import process_email
from app.services.knowledge_brain import answer_question
from app.services.meeting_agent import process_meeting


st.set_page_config(
    page_title="AI Tech Consultant",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        --background-color: #f7f8fc;
        --secondary-background-color: #ffffff;
        --primary-color: #5c65d8;
        --text-color: #111827;
        color-scheme: light;
        background:
            radial-gradient(ellipse at 8% 0%, rgba(90, 112, 255, 0.10), transparent 34rem),
            #f7f8fc;
        color: #111827;
    }
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        --background-color: #f7f8fc;
        --secondary-background-color: #ffffff;
        --text-color: #111827;
        background-color: #f7f8fc !important;
        color: #111827 !important;
    }
    [data-testid="stHeader"] {
        background: rgba(247, 248, 252, 0.96) !important;
    }
    [data-testid="stSidebar"] {
        background: #10172a;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #9ba6bf;
    }
    .sidebar-brand {
        padding: 0.5rem 0 1rem;
    }
    .sidebar-brand-mark {
        display: inline-grid;
        width: 2.5rem;
        height: 2.5rem;
        margin-bottom: 0.8rem;
        place-items: center;
        border: 1px solid rgba(174, 187, 255, 0.25);
        border-radius: 12px;
        background: linear-gradient(145deg, #6e78f7, #8e65e8);
        color: white;
        font-size: 1.35rem;
        font-weight: 700;
    }
    .sidebar-brand-name {
        color: #f4f6ff;
        font-size: 1.05rem;
        font-weight: 700;
    }
    .sidebar-section-label {
        margin: 1.25rem 0 0.55rem;
        color: #77839e;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.14em;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] {
        margin: 0.2rem 0;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        min-height: 2.9rem;
        justify-content: flex-start;
        border: 1px solid transparent;
        border-radius: 10px;
        background: transparent;
        color: #bdc6d9;
        font-weight: 500;
        text-align: left;
        transition: background 120ms ease, border-color 120ms ease, color 120ms ease;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        border-color: rgba(174, 187, 255, 0.16);
        background: rgba(255, 255, 255, 0.07);
        color: #ffffff;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
        border-color: rgba(151, 160, 255, 0.24);
        background: linear-gradient(100deg, rgba(103, 115, 244, 0.25), rgba(139, 98, 229, 0.16));
        color: #ffffff;
        font-weight: 650;
        box-shadow: inset 3px 0 #858cff;
    }
    .main-header {
        padding: 0.25rem 0 0.25rem;
    }
    .eyebrow {
        color: #5c65d8;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }
    .main-header h1 {
        margin: 0.2rem 0 0.35rem;
        color: #18213b;
        font-size: 2.35rem;
        letter-spacing: -0.04em;
    }
    .main-header p {
        margin: 0;
        color: #69738b;
        font-size: 1rem;
    }
    [data-testid="stMain"] [data-testid="stVerticalBlock"] {
        gap: 0.75rem;
    }
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3 {
        color: #18213b;
        margin-top: 0.15rem;
        margin-bottom: 0.15rem;
    }
    [data-testid="stMain"] label,
    [data-testid="stMain"] [data-testid="stWidgetLabel"] p {
        color: #34405a;
    }
    [data-testid="stMain"] input,
    [data-testid="stMain"] textarea,
    [data-testid="stChatInput"] textarea {
        border-color: #cbd2e1 !important;
        background-color: #ffffff !important;
        color: #111827 !important;
        caret-color: #5c65d8;
        -webkit-text-fill-color: #111827 !important;
    }
    [data-testid="stMain"] input::placeholder,
    [data-testid="stMain"] textarea::placeholder,
    [data-testid="stChatInput"] textarea::placeholder {
        color: #65718a !important;
        opacity: 1;
        -webkit-text-fill-color: #65718a !important;
    }
    [data-testid="stChatInput"] button {
        background-color: #5c65d8 !important;
        color: #ffffff !important;
    }
    [data-testid="stAlert"] [data-testid="stMarkdownContainer"] * {
        color: #18213b !important;
    }
    [data-testid="stExpander"] {
        border-color: #dce1ec !important;
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] [data-testid="stMarkdownContainer"] * {
        color: #111827 !important;
    }
    [data-testid="stChatMessage"] {
        --text-color: #000000;
        color: #000000 !important;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] *,
    [data-testid="stChatMessage"] [data-testid="stCaptionContainer"],
    [data-testid="stChatMessage"] [data-testid="stExpander"] [data-testid="stMarkdownContainer"] * {
        color: #000000 !important;
    }
    [data-testid="stChatMessage"] a {
        color: #4b55c5 !important;
    }
    div[data-testid="stForm"] {
        border: 1px solid #e5e8f1;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.88);
        padding: 1rem;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #e5e8f1;
        border-radius: 16px;
        background: rgba(255, 255, 255, 0.88);
    }
    div[data-testid="stMetric"] {
        border: 1px solid #e5e8f1;
        border-radius: 14px;
        background: white;
        padding: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-mark">✦</div>
            <div class="sidebar-brand-name">AI Consultant</div>
        </div>
        <div class="sidebar-section-label">DELIVERY</div>
        """,
        unsafe_allow_html=True,
    )
    workflow_options = [
        ("Knowledge Brain", "🧠", "Knowledge Brain"),
        ("Inbox Agent", "✉️", "Inbox Agent"),
        ("Meeting to Scope", "📋", "Meeting to Scope"),
    ]
    if "selected_workflow" not in st.session_state:
        st.session_state["selected_workflow"] = "Knowledge Brain"
    for workflow, icon, label in workflow_options:
        if st.button(
            f"{icon}   {label}",
            key=f"workflow-{workflow}",
            type="primary" if st.session_state["selected_workflow"] == workflow else "secondary",
            use_container_width=True,
        ):
            st.session_state["selected_workflow"] = workflow
            st.rerun()
    selected_workflow = st.session_state["selected_workflow"]
    st.divider()
    st.caption("Grounded answers. Thoughtful drafts. Human review for sensitive actions.")

st.markdown(
    """
    <div class="main-header">
        <div class="eyebrow">AI Tech Consultant · Workspace</div>
        <h1>Work smarter, with clarity.</h1>
        <p>Find trusted answers, prepare thoughtful replies, and turn discovery into a clear project scope.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def render_sources(sources: list[dict]) -> None:
    if not sources:
        st.caption("No source citations were returned.")
        return

    for index, source in enumerate(sources, start=1):
        title = source.get("title") or "Knowledge source"
        url = source.get("url")
        with st.container(border=True):
            st.markdown(f"**{index:02d} · {title}**")
            if url:
                st.link_button("Open source ↗", url, key=f"source-{index}-{url}")


def render_images(images: list[dict]) -> None:
    if not images:
        return

    st.markdown("#### Related visuals")
    for index, image in enumerate(images, start=1):
        with st.container(border=True):
            st.markdown(f"**{image.get('document_title') or f'Visual reference {index}'}**")
            st.write(image.get("description") or "Related image reference")
            image_url = image.get("url")
            if image_url:
                st.link_button("View image ↗", image_url, key=f"image-{index}-{image_url}")


if selected_workflow == "Knowledge Brain":
    st.subheader("Chat with your Knowledge Brain")
    st.write("Ask follow-up questions in a live conversation grounded in your knowledge base.")

    history = st.session_state.setdefault("knowledge_chat_history", [])
    if st.button("＋ New conversation", key="new-knowledge-chat"):
        st.session_state["knowledge_chat_history"] = []
        st.rerun()

    if not history:
        st.info("Ask about product policies, setup, security, or project proposals to get started.")

    for index, entry in enumerate(history):
        with st.chat_message(entry["role"]):
            st.markdown(entry["content"])
            if entry["role"] == "assistant" and entry.get("sources"):
                with st.expander(f"Sources · {len(entry['sources'])}"):
                    render_sources(entry["sources"])
            if entry["role"] == "assistant" and entry.get("human_escalation_required"):
                st.warning("Please ask a human reviewer to verify this answer.")

    prompt = st.chat_input("Ask a question about your knowledge base...")
    if prompt and prompt.strip():
        prompt = prompt.strip()
        history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        knowledge = answer_question(prompt)
        try:
            prepared = prepare_chat(prompt, history[:-1], knowledge)
        except ChatConfigurationError as exc:
            response_text = knowledge["answer"]
            with st.chat_message("assistant"):
                st.warning(str(exc))
                st.caption("Showing the Knowledge Brain retrieval result; this response was not generated by a live AI model.")
                st.markdown(response_text)
                with st.expander(f"Sources · {len(knowledge.get('sources', []))}"):
                    render_sources(knowledge.get("sources", []))
            history.append(
                {
                    "role": "assistant",
                    "content": response_text,
                    "sources": knowledge.get("sources", []),
                    "human_escalation_required": knowledge.get("human_escalation_required", False),
                }
            )
        else:
            with st.chat_message("assistant"):
                if prepared.client is None:
                    st.caption("Knowledge retrieval only · No AI-generated answer was produced.")
                try:
                    response_text = st.write_stream(stream_chat_answer(prepared))
                except OpenAIError as exc:
                    st.error(f"The live AI request failed: {exc}")
                    response_text = ""
                if response_text:
                    with st.expander(f"Sources · {len(knowledge.get('sources', []))}"):
                        render_sources(knowledge.get("sources", []))
                    if knowledge.get("human_escalation_required"):
                        st.warning("Please ask a human reviewer to verify this answer.")
                    history.append(
                        {
                            "role": "assistant",
                            "content": response_text,
                            "sources": knowledge.get("sources", []),
                            "human_escalation_required": knowledge.get("human_escalation_required", False),
                        }
                    )

elif selected_workflow == "Inbox Agent":
    st.subheader("Prepare an email response")
    st.write("Classify an incoming message and create a reviewable reply draft.")

    with st.form("inbox-email-form"):
        sender = st.text_input("Sender email", placeholder="customer@example.com")
        subject = st.text_input("Subject", placeholder="What can we help with?")
        body = st.text_area("Email message", placeholder="Paste the customer's message here.", height=180)
        _, search_col = st.columns([4, 1])
        with search_col:
            submitted = st.form_submit_button(
                "🔍 Search email",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        if subject.strip() or body.strip():
            st.session_state["inbox_result"] = process_email(
                {
                    "sender": sender.strip(),
                    "recipient": "support@example.com",
                    "subject": subject.strip(),
                    "body": body.strip(),
                }
            )
        else:
            st.warning("Enter an email subject or message to search.")

    result = st.session_state.get("inbox_result")
    if result:
        st.markdown("---")
        st.markdown("### Triage summary")
        category_col, risk_col, urgency_col = st.columns(3)
        category_col.metric("Category", result.get("category", "Uncategorized").replace("_", " ").title())
        risk_col.metric("Risk level", (result.get("risk") or "unknown").title())
        urgency_col.metric("Urgency", (result.get("urgency") or "normal").title())

        if result.get("human_approval_required"):
            st.warning("Human review required · Review this draft before sending.")
        else:
            st.success("Low-risk draft · Review before sending as usual.")

        st.markdown("### Suggested reply")
        st.text_area(
            "Draft reply",
            value=result.get("suggested_reply", ""),
            height=220,
            disabled=True,
            label_visibility="collapsed",
        )
        st.caption(result.get("recommended_next_action", "Review the response before taking action."))

        knowledge = result.get("retrieved_knowledge")
        if knowledge:
            with st.expander("Retrieved knowledge and citations"):
                st.markdown(knowledge.get("answer", "No supporting answer was returned."))
                render_sources(knowledge.get("sources", []))

        with st.expander("Processing details"):
            st.write(result.get("reasoning_summary", ""))
            st.caption(f"Email ID: {result.get('email_id', 'Unavailable')}")
            st.caption(f"Model: {result.get('model_id', 'Unavailable')} · Prompt: {result.get('prompt_version', 'Unavailable')}")

else:
    st.subheader("Turn a discovery meeting into a scope")
    st.write("Extract requirements and prepare an initial effort estimate and proposal.")

    with st.form("meeting-transcript-form"):
        title = st.text_input("Meeting title", placeholder="Customer support automation discovery")
        client_name = st.text_input("Client name", placeholder="Acme Labs")
        transcript = st.text_area(
            "Meeting transcript",
            placeholder="Paste the meeting transcript or discovery notes here.",
            height=220,
        )
        _, search_col = st.columns([4, 1])
        with search_col:
            submitted = st.form_submit_button(
                "🔍 Search meeting",
                type="primary",
                use_container_width=True,
            )

    if submitted:
        if transcript.strip():
            st.session_state["meeting_result"] = process_meeting(
                title.strip() or "Discovery meeting",
                transcript.strip(),
                client_name.strip(),
            )
        else:
            st.warning("Add a transcript or discovery notes to search.")

    result = st.session_state.get("meeting_result")
    if result:
        st.markdown("---")
        estimate_col, requirement_col, capability_col = st.columns(3)
        estimate_col.metric("Estimated effort", f"{result.get('estimate_hours', 0)} hours")
        requirement_col.metric("Requirements found", len(result.get("requirements", [])))
        capability_col.metric("Capabilities matched", len(result.get("capability_checks", [])))

        st.markdown("### Scope summary")
        with st.container(border=True):
            st.write(result.get("scope_summary") or "No scope summary was returned.")

        requirements = result.get("requirements", [])
        if requirements:
            st.markdown("### Extracted requirements")
            for index, requirement in enumerate(requirements, start=1):
                with st.container(border=True):
                    st.markdown(
                        f"**{index:02d} · {(requirement.get('category') or 'general').replace('_', ' ').title()}**"
                    )
                    st.write(requirement.get("requirement_text", ""))
                    st.caption(f"Confidence · {requirement.get('confidence', 0):.0%}")

        capabilities = result.get("capability_checks", [])
        if capabilities:
            st.markdown("**Capabilities mentioned**")
            st.write(" · ".join(capabilities))

        st.markdown("### Proposal draft")
        st.text_area(
            "Proposal",
            value=result.get("proposal", ""),
            height=250,
            disabled=True,
            label_visibility="collapsed",
        )
        st.caption("Review the assumptions and effort estimate with the client before treating this draft as final.")
