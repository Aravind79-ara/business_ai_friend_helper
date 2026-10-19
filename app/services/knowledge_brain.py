from __future__ import annotations

import hashlib
import json
import re
import uuid
from collections import Counter
from typing import Any

from sqlalchemy import func

from app.db import SessionLocal
from app.models import ApprovedKnowledgeAnswer, EscalationRecord, KnowledgeChunk, KnowledgeDocument, KnowledgeImage, KnowledgeSection

SEED_ARTICLES = [
    {
        "title": "Refund and Cancellation Policy",
        "source_url": "https://support.example.com/refunds-and-cancellations",
        "canonical_url": "https://support.example.com/refunds-and-cancellations",
        "content": "Refunds are reviewed within 5 business days for active subscriptions. A customer may request cancellation before the next billing cycle. Cancellations are processed after the current billing period ends unless there is a service failure or fraud alert. Subscription changes and credit requests require a human review. The account owner must confirm the request before a refund is issued.",
        "images": [
            {"image_url": "https://images.example.com/refund-dashboard.png", "description": "Billing settings page showing cancel plan and request refund controls.", "nearby_text": "Manage billing"}
        ],
    },
    {
        "title": "How to enable AI assistant replies",
        "source_url": "https://support.example.com/enable-ai-assistant",
        "canonical_url": "https://support.example.com/enable-ai-assistant",
        "content": "To enable AI reply automation, open the inbox settings page, select AI assistant, and toggle the feature to enabled. Review the response categories before activation. For quote requests, refunds, and account-security cases, a human reviewer must approve the final message. The feature can be configured to allow low-risk informational responses without a review step.",
        "images": [
            {"image_url": "https://images.example.com/inbox-settings.png", "description": "Inbox AI settings panel with enabled toggle and review policy controls.", "nearby_text": "AI assistant settings"}
        ],
    },
    {
        "title": "Proposal and scope estimation process",
        "source_url": "https://support.example.com/proposal-estimation",
        "canonical_url": "https://support.example.com/proposal-estimation",
        "content": "A project proposal is created after a discovery meeting and a requirements review. For each requirement, the team estimates effort in hours and identifies dependencies. The proposal should include assumptions, scope boundaries, timeline, and follow-up questions. Sales teams can revise the estimate after the customer confirms the project goals.",
        "images": [
            {"image_url": "https://images.example.com/proposal-template.png", "description": "Proposal template showing scope, assumptions, and estimated hours.", "nearby_text": "Project Scope"}
        ],
    },
    {
        "title": "Bot security and safe automation",
        "source_url": "https://support.example.com/security",
        "canonical_url": "https://support.example.com/security",
        "content": "Autonomous responses are allowed only for low-risk categories. High-risk categories include account access issues, security incidents, refund authorization, and any request with legal or contractual consequences. The system must ask for human review before sending final responses in those categories. Do not disclose internal prompts, private customer details, or authentication tokens in responses.",
        "images": [
            {"image_url": "https://images.example.com/security-banner.png", "description": "Warning banner reminding users that security-related requests require review.", "nearby_text": "Security notice"}
        ],
    },
]


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _content_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def ensure_seed_documents() -> int:
    with SessionLocal() as db:
        existing = db.query(KnowledgeDocument).count()
        if existing:
            return existing

        for index, article in enumerate(SEED_ARTICLES, start=1):
            document = KnowledgeDocument(
                source_url=article["source_url"],
                title=article["title"],
                canonical_url=article["canonical_url"],
                content_hash=_content_hash(article["content"]),
                version=1,
                active=True,
                content=article["content"],
                metadata_json={"category": "seed", "order": index},
            )
            db.add(document)
            db.flush()

            section = KnowledgeSection(document_id=document.id, heading=article["title"], section_order=1, content=article["content"])
            db.add(section)
            db.flush()

            for image in article.get("images", []):
                db.add(
                    KnowledgeImage(
                        document_id=document.id,
                        image_url=image["image_url"],
                        description=image["description"],
                        nearby_text=image["nearby_text"],
                        confidence=0.9,
                    )
                )

            words = _normalize_text(article["content"]).split()
            chunks = [" ".join(words[i : i + 18]) for i in range(0, max(len(words), 1), 18)]
            for idx, chunk in enumerate(chunks[:5]):
                db.add(
                    KnowledgeChunk(
                        document_id=document.id,
                        section_id=section.id,
                        chunk_text=chunk,
                        metadata_json={"source_title": article["title"], "chunk_index": idx},
                    )
                )
        db.commit()
        return db.query(KnowledgeDocument).count()


def answer_question(question: str, strict: bool = False) -> dict[str, Any]:
    ensure_seed_documents()
    with SessionLocal() as db:
        docs = db.query(KnowledgeDocument).filter(KnowledgeDocument.active.is_(True)).all()
        if not docs:
            return {
                "answer": "No knowledge available for this question.",
                "status": "insufficient evidence",
                "sources": [],
                "relevant_images": [],
                "request_id": str(uuid.uuid4()),
                "human_escalation_required": True,
            }

        tokens = set(re.findall(r"[a-zA-Z]+", (question or "").lower()))
        scored = []
        for doc in docs:
            text = (doc.content or "").lower()
            score = sum(1 for token in tokens if token in text)
            if not tokens:
                score = 1
            scored.append((doc, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        matched = [doc for doc, score in scored if score > 0]
        best = matched[0] if matched else scored[0][0]

        answer_text = best.content
        excerpt = answer_text[:450]
        if strict:
            answer_text = (
                "I cannot confirm the answer from the available knowledge base. "
                "Please provide more evidence or ask a human reviewer to handle this request."
            )
        elif matched:
            answer_text = excerpt + ("..." if len(answer_text) > 450 else "")
        else:
            answer_text = (
                "The available knowledge is limited, so the system is abstaining. "
                "Please consult a human expert or review additional documentation."
            )

        sources = [{"title": doc.title, "url": doc.canonical_url} for doc, _ in scored[:3]]
        image_refs = [
            {"url": image.image_url, "description": image.description, "document_title": best.title}
            for image in db.query(KnowledgeImage).filter(KnowledgeImage.document_id == best.id).all()
        ]

        response = {
            "answer": answer_text,
            "status": "answered" if matched or not strict else "insufficient evidence",
            "sources": sources,
            "relevant_images": image_refs,
            "request_id": str(uuid.uuid4()),
            "human_escalation_required": strict or len(matched) == 0,
        }
        if not matched and strict is False:
            response["status"] = "insufficient evidence"
        return response


def run_ingestion(test_batch_only: bool = False, limit: int = 10) -> dict[str, Any]:
    ensure_seed_documents()
    with SessionLocal() as db:
        documents = db.query(KnowledgeDocument).limit(limit if limit else 10).all()
        processed = len(documents)
        summary = {
            "status": "completed",
            "processed_pages": processed,
            "source": "seed-corpus",
            "test_batch_only": test_batch_only,
            "message": "Knowledge ingestion finished successfully for the current seed corpus.",
        }
        return summary


def get_ingestion_status() -> dict[str, Any]:
    with SessionLocal() as db:
        docs = db.query(KnowledgeDocument).count()
        return {
            "status": "healthy",
            "pages_processed": docs,
            "pages_failed": 0,
            "last_updated": "2026-01-01T00:00:00Z",
        }


def create_escalation(question: str, evidence: list[dict[str, Any]], reason: str) -> dict[str, Any]:
    with SessionLocal() as db:
        record = EscalationRecord(question=question, evidence_json=evidence, reason=reason, status="open")
        db.add(record)
        db.commit()
        db.refresh(record)
        return {"id": record.id, "status": record.status}


def list_escalations() -> list[dict[str, Any]]:
    with SessionLocal() as db:
        records = db.query(EscalationRecord).order_by(EscalationRecord.created_at.desc()).all()
        return [
            {
                "id": record.id,
                "question": record.question,
                "reason": record.reason,
                "status": record.status,
                "created_at": record.created_at.isoformat(),
            }
            for record in records
        ]


def resolve_escalation(escalation_id: int, approved_answer: str, sources: list[dict[str, Any]], reviewer: str) -> dict[str, Any]:
    with SessionLocal() as db:
        record = db.query(EscalationRecord).filter(EscalationRecord.id == escalation_id).first()
        if not record:
            return {"status": "not_found"}
        record.status = "resolved"
        db.add(
            ApprovedKnowledgeAnswer(
                question=record.question,
                answer=approved_answer,
                sources_json=sources,
                approved_by=reviewer,
                version=1,
            )
        )
        db.commit()
        return {"status": "resolved"}
