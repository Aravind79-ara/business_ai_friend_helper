import uuid

import pytest
from sqlalchemy import select

from app.db import SessionLocal
from app.models import EmailDraft, EmailMessage


@pytest.mark.parametrize(
    ("subject", "expected_category", "approval_required"),
    [
        ("How do I turn on AI replies?", "product_how_to", False),
        ("The app shows an error when I try to send", "technical_troubleshooting", False),
        ("I need a refund for my subscription", "refunds_and_cancellations", True),
        ("Can you give me a quote for AI support setup?", "quote_request", True),
        ("I am locked out of my account", "account_security", True),
        ("The feature is completely broken", "technical_troubleshooting", False),
        ("I want to cancel my plan", "refunds_and_cancellations", True),
        ("Can we build a proposal bot?", "project_request", False),
        ("I am not happy with the service", "complaint", True),
        ("Where is the settings page?", "product_how_to", False),
        ("I need pricing for onboarding work", "quote_request", True),
        ("My login session keeps failing", "account_security", True),
        ("How do I add AI to the inbox?", "product_how_to", False),
        ("The billing page is broken", "technical_troubleshooting", False),
        ("Please cancel my subscription", "refunds_and_cancellations", True),
        ("What is the cost of your AI support?", "quote_request", True),
        ("I think someone hacked my account", "account_security", True),
        ("I want a new project with AI automation", "project_request", False),
        ("This was unacceptable", "complaint", True),
        ("How to set up low-risk automation?", "product_how_to", False),
    ],
)
def test_inbox_processes_and_persists_email_draft(
    api_client, subject, expected_category, approval_required
):
    email_id = f"test-{uuid.uuid4()}"
    response = api_client.post(
        "/api/v1/inbox/process",
        json={
            "email_id": email_id,
            "sender": "customer@example.com",
            "recipient": "support@example.com",
            "subject": subject,
            "body": subject,
        }
    )

    assert response.status_code == 200
    result = response.json()
    assert result["email_id"] == email_id
    assert result["category"] == expected_category
    assert result["human_approval_required"] is approval_required
    assert result["suggested_reply"].strip()

    with SessionLocal() as db:
        email = db.scalar(select(EmailMessage).where(EmailMessage.email_id == email_id))
        assert email is not None
        assert email.category == expected_category
        draft = db.scalar(select(EmailDraft).where(EmailDraft.email_id == email.id))
        assert draft is not None
        assert draft.suggested_reply == result["suggested_reply"]
        assert draft.approval_required is approval_required
