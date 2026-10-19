import uuid

import pytest
from sqlalchemy import select

from app.db import SessionLocal
from app.models import MeetingRequirement, MeetingTranscript, ProposalDocument


@pytest.mark.parametrize(
    "transcript",
    [
        "We need an email triage assistant with AI automation and a knowledge base.",
        "We want proposal generation, estimates, and a client-facing interview flow.",
        "We need a high-risk review step for refunds, security, and legal approval.",
        "The system must support AI support workflows and customer education.",
        "Our project needs a proposal template for recurring support engagements.",
        "We need a bot that checks customer knowledge and drafts replies.",
        "We want to automate low-risk responses while keeping invoice exceptions manual.",
        "The client expects accurate scope boundaries and estimate ranges.",
        "We need AI triage for incoming service requests and account issues.",
        "The workflow should integrate with a knowledge base and review queue.",
        "We need to estimate effort for a custom onboarding experience.",
        "We want an AI assistant that reads help docs before drafting replies.",
        "We need secure access controls and a review policy for sensitive requests.",
        "Client requirements include a proposal generator and scope history.",
        "We want to automate the simple how-to questions but keep billing changes human.",
        "The product should support email drafts, knowledge retrieval, and support summaries.",
        "We need a project proposal after the discovery meeting.",
        "The deliverable should include secure access, AI automation, and pricing estimates.",
        "We want the system to classify support issues and escalate exceptional cases.",
        "We need to estimate the effort for a knowledge adviser and review layer.",
    ],
)
def test_meeting_creates_persisted_scope_and_proposal(api_client, transcript):
    title = f"Discovery {uuid.uuid4()}"
    client_name = "Test Client"
    response = api_client.post(
        "/api/v1/meetings/process",
        json={"title": title, "transcript_text": transcript, "client_name": client_name},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "completed"
    assert result["meeting_id"]
    assert result["requirements"]
    assert result["estimate_hours"] > 0
    assert result["scope_summary"].strip()
    assert client_name in result["proposal"]

    with SessionLocal() as db:
        meeting = db.scalar(select(MeetingTranscript).where(MeetingTranscript.id == result["meeting_id"]))
        assert meeting is not None
        assert meeting.transcript_text == transcript
        requirements = db.scalars(
            select(MeetingRequirement).where(MeetingRequirement.transcript_id == meeting.id)
        ).all()
        assert len(requirements) == len(result["requirements"])
        proposal = db.scalar(select(ProposalDocument).where(ProposalDocument.transcript_id == meeting.id))
        assert proposal is not None
        assert proposal.estimate_hours == result["estimate_hours"]
        assert proposal.proposal_text == result["proposal"]
