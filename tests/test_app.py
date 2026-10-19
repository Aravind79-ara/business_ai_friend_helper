from pathlib import Path

from app.services.inbox_agent import classify_email, process_email
from app.services.knowledge_brain import answer_question
from app.services.meeting_agent import process_meeting


def test_streamlit_ui_has_high_contrast_chat_styles():
    from streamlit.testing.v1 import AppTest

    ui_path = Path(__file__).resolve().parents[1] / "app" / "ui.py"
    app = AppTest.from_file(ui_path, default_timeout=30).run()

    assert not app.exception
    styles = app.markdown[0].value
    assert "[data-testid=\"stChatInput\"] textarea" in styles
    assert "-webkit-text-fill-color: #111827 !important;" in styles
    assert "[data-testid=\"stChatMessage\"] [data-testid=\"stMarkdownContainer\"] *" in styles
    assert "color: #000000 !important;" in styles


def test_knowledge_brain_answers_questions():
    cases = [
        "How do I enable AI assistant replies?",
        "What is the cancellation policy?",
        "Can a refund be issued without human review?",
        "What is the scope estimation workflow?",
        "How does this system handle security-related requests?",
        "When should a proposal be created?",
        "Is it safe to auto-send a refund email?",
        "Why do we require review for high-risk categories?",
        "Where do I adjust my invoice preferences?",
        "Can I approve a quote request automatically?",
    ]
    for question in cases:
        result = answer_question(question)
        assert result["status"] in {"answered", "insufficient evidence"}
        assert "request_id" in result


def test_email_classification_categories():
    pairs = [
        ("How do I enable AI assistant replies?", "product_how_to"),
        ("My login is broken and I cannot access my account.", "account_security"),
        ("I want to cancel my subscription", "refunds_and_cancellations"),
        ("Need a quote for a new AI agent rollout", "quote_request"),
        ("The feature is failing and I see an error", "technical_troubleshooting"),
    ]
    for subject, expected in pairs:
        category, _ = classify_email(subject, subject)
        assert category == expected


def test_inbox_processing_generates_draft():
    payload = {
        "email_id": "mail-101",
        "sender": "customer@example.com",
        "recipient": "support@example.com",
        "subject": "How do I enable AI assistant replies?",
        "body": "I want to enable the AI assistant but I do not see the toggle.",
    }
    result = process_email(payload)
    assert result["category"] == "product_how_to"
    assert result["human_approval_required"] is False
    assert "suggested_reply" in result


def test_meeting_processing_generates_scope():
    transcript = "We need an AI support assistant for customer email triage. The project should include knowledge retrieval and proposal generation. We also require human review for security and refund cases."
    result = process_meeting("Discovery call", transcript, "Acme Labs")
    assert result["status"] == "completed"
    assert result["estimate_hours"] > 0
    assert "proposal" in result
