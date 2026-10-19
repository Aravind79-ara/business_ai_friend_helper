from __future__ import annotations

import re
from typing import Any

from app.db import SessionLocal
from app.models import MeetingRequirement, MeetingTranscript, ProposalDocument

CAPABILITY_CATALOG = [
    "AI support assistant",
    "email triage",
    "knowledge brain",
    "proposal generation",
    "client-facing onboarding",
    "automation review",
]


def _extract_requirements(transcript_text: str) -> list[dict[str, Any]]:
    sentences = re.split(r"(?<=[.!?])\s+", transcript_text)
    requirements = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        lowered = sentence.lower()
        if any(keyword in lowered for keyword in ["need", "require", "must", "want", "should", "expect", "goal", "aim"]):
            category = "general"
            if any(keyword in lowered for keyword in ["assistant", "chatbot", "reply", "email"]):
                category = "ai_support"
            elif any(keyword in lowered for keyword in ["proposal", "estimate", "scope", "budget"]):
                category = "proposal"
            elif any(keyword in lowered for keyword in ["security", "login", "access", "authentication"]):
                category = "security"
            requirements.append({"requirement_text": sentence, "category": category, "confidence": 0.82})
    if not requirements:
        for phrase in ["AI workflow for support operations", "Proposal automation", "Customer email triage"]:
            requirements.append({"requirement_text": phrase, "category": "general", "confidence": 0.65})
    return requirements


def process_meeting(title: str, transcript_text: str, client_name: str = "") -> dict[str, Any]:
    meeting = MeetingTranscript(title=title, source_url="", transcript_text=transcript_text)
    requirements = _extract_requirements(transcript_text)
    meeting_id = None
    capability_mentions: list[str] = []
    estimate_hours = 10
    requirement_snippets: list[str] = []
    scope_summary = "General AI support workflow"
    proposal_text = ""

    with SessionLocal() as db:
        db.add(meeting)
        db.commit()
        db.refresh(meeting)
        meeting_id = meeting.id

        req_rows = [
            MeetingRequirement(
                transcript_id=meeting.id,
                requirement_text=item["requirement_text"],
                category=item["category"],
                confidence=item["confidence"],
            )
            for item in requirements
        ]
        db.add_all(req_rows)
        db.commit()

        capability_mentions = [capability for capability in CAPABILITY_CATALOG if capability.lower() in transcript_text.lower()]
        estimate_hours = max(10, len(requirements) * 8 + (8 if capability_mentions else 0))
        requirement_snippets = [item["requirement_text"] for item in requirements[:3]]
        scope_summary = ", ".join(requirement_snippets) if requirement_snippets else "General AI support workflow"
        proposal_text = (
            f"Project: {title}\n"
            f"Client: {client_name or 'Prospective client'}\n"
            f"Scope summary: {scope_summary}\n"
            f"Estimated effort: {estimate_hours} hours\n"
            "Key assumptions: support workflow uses AI-powered knowledge retrieval, human approval for high-risk actions, and reviewable outputs before sending."
        )
        proposal = ProposalDocument(
            transcript_id=meeting.id,
            client_name=client_name or "Prospective client",
            scope_summary=scope_summary,
            estimate_hours=estimate_hours,
            proposal_text=proposal_text,
        )
        db.add(proposal)
        db.commit()

    return {
        "meeting_id": meeting_id,
        "requirements": requirements,
        "capability_checks": capability_mentions,
        "estimate_hours": estimate_hours,
        "scope_summary": scope_summary,
        "proposal": proposal_text,
        "status": "completed",
    }
