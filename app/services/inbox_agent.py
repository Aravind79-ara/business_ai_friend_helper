from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from app.db import SessionLocal
from app.models import EmailDraft, EmailMessage, ReviewDecision
from app.services.knowledge_brain import answer_question

CATEGORY_KEYWORDS = {
    "product_how_to": ["how do i", "how to", "where is", "how can i", "settings"],
    "technical_troubleshooting": ["error", "bug", "not working", "issue", "failed", "broken", "not loading"],
    "refunds_and_cancellations": ["refund", "cancel", "cancellation", "billing", "chargeback"],
    "quote_request": ["quote", "pricing", "proposal", "estimate", "budget"],
    "project_request": ["project", "engagement", "implementation", "new website", "build"],
    "account_security": ["password", "security", "access", "locked", "hacked", "login"],
    "complaint": ["terrible", "unacceptable", "angry", "frustrated", "poor"],
}

CATEGORY_WEIGHTS = {
    "account_security": 100,
    "refunds_and_cancellations": 90,
    "technical_troubleshooting": 80,
    "complaint": 70,
    "quote_request": 60,
    "project_request": 50,
    "product_how_to": 30,
}


def classify_email(subject: str, body: str) -> tuple[str, str]:
    content = f"{subject} {body}".lower()

    if any(token in content for token in ["password", "security", "access", "locked", "hacked", "login", "account compromised", "account hacked"]):
        return "account_security", "high"
    if any(token in content for token in ["terrible", "unacceptable", "angry", "frustrated", "poor", "not happy"]):
        return "complaint", "high"
    if any(token in content for token in ["error", "bug", "not working", "issue", "failed", "broken", "not loading", "button is broken", "app shows an error"]):
        return "technical_troubleshooting", "medium"
    if any(token in content for token in ["refund", "cancel", "cancellation", "chargeback", "charged twice", "cancel my plan", "cancel my subscription", "subscription", "refund request"]):
        return "refunds_and_cancellations", "high"
    if any(token in content for token in ["how do i", "how to", "where is", "how can i", "settings", "turn on", "add ai"]):
        return "product_how_to", "medium"
    if any(token in content for token in ["quote", "pricing", "estimate", "budget", "cost"]) and not any(token in content for token in ["build", "project", "automation", "implementation", "new project", "custom", "pilot"]):
        return "quote_request", "medium"
    if any(token in content for token in ["build", "project", "implementation", "automation", "new project", "custom", "engagement", "pilot"]):
        return "project_request", "medium"

    return "unclear_or_unsupported", "medium"


def process_email(email_payload: dict[str, Any]) -> dict[str, Any]:
    email_id = email_payload.get("email_id") or str(uuid.uuid4())
    subject = email_payload.get("subject", "")
    body = email_payload.get("body", "")
    category, risk = classify_email(subject, body)

    with SessionLocal() as db:
        email_record = db.query(EmailMessage).filter(EmailMessage.email_id == email_id).first()
        if email_record is None:
            email_record = EmailMessage(
                email_id=email_id,
                sender=email_payload.get("sender", ""),
                recipient=email_payload.get("recipient", ""),
                subject=subject,
                body=body,
                thread_id=email_payload.get("thread_id", ""),
                timestamp=email_payload.get("timestamp", datetime.now(timezone.utc).replace(tzinfo=None).isoformat()),
                category=category,
                risk=risk,
            )
            db.add(email_record)
            db.commit()
            db.refresh(email_record)

    knowledge = None
    if category in {"product_how_to", "technical_troubleshooting", "project_request"}:
        knowledge = answer_question(f"{subject} {body}")

    draft_text = _compose_draft(category, subject, body, knowledge)
    approval_required = risk == "high" or category in {"refunds_and_cancellations", "account_security", "quote_request", "complaint"}

    with SessionLocal() as db:
        draft = EmailDraft(
            email_id=email_record.id,
            category=category,
            risk=risk,
            retrieved_knowledge_json=knowledge,
            suggested_reply=draft_text,
            approval_required=approval_required,
            prompt_version="v1",
            model_id="rules-v1",
        )
        db.add(draft)
        db.commit()
        db.refresh(draft)

    return {
        "email_id": email_id,
        "category": category,
        "subcategory": category,
        "customer_request_summary": subject,
        "urgency": "high" if "urgent" in body.lower() else "normal",
        "risk": risk,
        "missing_information": [],
        "retrieved_knowledge": knowledge,
        "suggested_reply": draft_text,
        "reasoning_summary": "Classified from the incoming email text and checked the Knowledge Brain when product facts were required.",
        "recommended_next_action": "Review and edit before approval." if approval_required else "Send with normal automation.",
        "human_approval_required": approval_required,
        "escalation_reason": "High-risk or unsupported category" if approval_required else "No escalation needed",
        "prompt_version": "v1",
        "model_id": "rules-v1",
    }


def _compose_draft(category: str, subject: str, body: str, knowledge: dict[str, Any] | None) -> str:
    if category == "refunds_and_cancellations":
        return (
            "Hi there,\n\nThank you for reaching out. We reviewed the request and must confirm the account details before processing any refund or cancellation. "
            "Our policy requires a human review for billing changes. We can continue once you confirm the affected order or subscription and the preferred resolution."
        )
    if category == "quote_request":
        return (
            "Hi there,\n\nThanks for your interest in working with us. We can share a project estimate after a short discovery conversation. "
            "Please confirm the scope, timeline, and success criteria so we can prepare a tailored proposal."
        )
    if category == "account_security":
        return (
            "Hi there,\n\nWe take account security seriously. Please confirm the exact account or email involved and whether you are seeing a login issue, lockout, or suspicious activity. "
            "A human reviewer will need to validate the next steps before any access changes are made."
        )
    if category == "technical_troubleshooting":
        base = "Hi there,\n\nThanks for flagging this issue. We reviewed the available guidance and the safest next step is to confirm the exact error condition and reproduce it with the current environment."
        if knowledge and knowledge.get("status") == "answered":
            return base + " The relevant support article confirms the expected configuration steps."
        return base
    if category == "project_request":
        return (
            "Hi there,\n\nThanks for the project request. We can help evaluate scope, dependencies, and timing. Please share the main goals, stakeholders, and any existing system constraints so we can prepare a concise proposal."
        )
    if category == "complaint":
        return (
            "Hi there,\n\nWe are sorry to hear that the experience did not meet your expectations. We appreciate the feedback and will review the issue carefully. "
            "A human reviewer will assess the resolution and follow-up steps before finalizing the response."
        )
    return (
        "Hi there,\n\nThank you for contacting us. We reviewed the request and will follow up with the next steps. "
        "If needed, we will ask for any missing information before finalizing a response."
    )


def submit_review(draft_id: int, approved: bool, reviewer_name: str, replacement_text: str | None = None, correction_reason: str | None = None) -> dict[str, Any]:
    with SessionLocal() as db:
        decision = ReviewDecision(
            draft_id=draft_id,
            approved=approved,
            rejected=not approved,
            replacement_text=replacement_text,
            correction_reason=correction_reason,
            reviewer_name=reviewer_name,
        )
        db.add(decision)
        db.commit()
        return {"status": "ok", "decision_id": decision.id}
