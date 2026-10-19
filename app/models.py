from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_url: Mapped[str] = mapped_column(String(500), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    ingested_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    content: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[str | None] = mapped_column(JSON, nullable=True)

    sections: Mapped[list[KnowledgeSection]] = relationship(back_populates="document", cascade="all, delete-orphan")
    images: Mapped[list[KnowledgeImage]] = relationship(back_populates="document", cascade="all, delete-orphan")
    chunks: Mapped[list[KnowledgeChunk]] = relationship(back_populates="document", cascade="all, delete-orphan")


class KnowledgeSection(Base):
    __tablename__ = "knowledge_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("knowledge_documents.id"), nullable=False)
    heading: Mapped[str] = mapped_column(String(255), default="")
    section_order: Mapped[int] = mapped_column(Integer, default=0)
    content: Mapped[str] = mapped_column(Text, default="")

    document: Mapped[KnowledgeDocument] = relationship(back_populates="sections")


class KnowledgeImage(Base):
    __tablename__ = "knowledge_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("knowledge_documents.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    nearby_text: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(default=0.0)

    document: Mapped[KnowledgeDocument] = relationship(back_populates="images")


class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("knowledge_documents.id"), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    section_id: Mapped[int | None] = mapped_column(ForeignKey("knowledge_sections.id"), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(JSON, nullable=True)

    document: Mapped[KnowledgeDocument] = relationship(back_populates="chunks")


class IngestionManifest(Base):
    __tablename__ = "ingestion_manifest"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    last_seen: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_successful_fetch: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_count: Mapped[int] = mapped_column(Integer, default=0)


class EscalationRecord(Base):
    __tablename__ = "escalation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_json: Mapped[str] = mapped_column(JSON, default=list)
    reason: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ApprovedKnowledgeAnswer(Base):
    __tablename__ = "approved_knowledge_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    sources_json: Mapped[str | None] = mapped_column(JSON, nullable=True)
    approved_by: Mapped[str] = mapped_column(String(255), default="human")
    approved_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    version: Mapped[int] = mapped_column(Integer, default=1)


class EmailMessage(Base):
    __tablename__ = "email_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    sender: Mapped[str] = mapped_column(String(255), default="")
    recipient: Mapped[str] = mapped_column(String(255), default="")
    subject: Mapped[str] = mapped_column(String(255), default="")
    body: Mapped[str] = mapped_column(Text, default="")
    thread_id: Mapped[str] = mapped_column(String(255), default="")
    timestamp: Mapped[str] = mapped_column(String(50), default="")
    category: Mapped[str] = mapped_column(String(80), default="unknown")
    risk: Mapped[str] = mapped_column(String(40), default="low")
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    drafts: Mapped[list[EmailDraft]] = relationship(back_populates="email", cascade="all, delete-orphan")


class EmailDraft(Base):
    __tablename__ = "email_drafts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email_id: Mapped[int] = mapped_column(ForeignKey("email_messages.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="unknown")
    risk: Mapped[str] = mapped_column(String(40), default="low")
    retrieved_knowledge_json: Mapped[str | None] = mapped_column(JSON, nullable=True)
    suggested_reply: Mapped[str] = mapped_column(Text, default="")
    approval_required: Mapped[bool] = mapped_column(Boolean, default=True)
    prompt_version: Mapped[str] = mapped_column(String(80), default="v1")
    model_id: Mapped[str] = mapped_column(String(80), default="mock")

    email: Mapped[EmailMessage] = relationship(back_populates="drafts")
    review_decisions: Mapped[list[ReviewDecision]] = relationship(back_populates="draft", cascade="all, delete-orphan")


class ReviewDecision(Base):
    __tablename__ = "review_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("email_drafts.id"), nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    replacement_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    correction_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_name: Mapped[str] = mapped_column(String(255), default="reviewer")
    decided_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    draft: Mapped[EmailDraft] = relationship(back_populates="review_decisions")


class MeetingTranscript(Base):
    __tablename__ = "meeting_transcripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), default="")
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    transcript_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    requirements: Mapped[list[MeetingRequirement]] = relationship(back_populates="transcript", cascade="all, delete-orphan")
    proposals: Mapped[list[ProposalDocument]] = relationship(back_populates="transcript", cascade="all, delete-orphan")


class MeetingRequirement(Base):
    __tablename__ = "meeting_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transcript_id: Mapped[int] = mapped_column(ForeignKey("meeting_transcripts.id"), nullable=False)
    requirement_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), default="general")
    confidence: Mapped[float] = mapped_column(default=0.0)

    transcript: Mapped[MeetingTranscript] = relationship(back_populates="requirements")


class ProposalDocument(Base):
    __tablename__ = "proposal_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    transcript_id: Mapped[int] = mapped_column(ForeignKey("meeting_transcripts.id"), nullable=False)
    client_name: Mapped[str] = mapped_column(String(255), default="")
    scope_summary: Mapped[str] = mapped_column(Text, default="")
    estimate_hours: Mapped[int] = mapped_column(Integer, default=0)
    proposal_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    transcript: Mapped[MeetingTranscript] = relationship(back_populates="proposals")


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_name: Mapped[str] = mapped_column(String(80), nullable=False)
    case_id: Mapped[str] = mapped_column(String(120), default="")
    score: Mapped[float] = mapped_column(default=0.0)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    model_name: Mapped[str] = mapped_column(String(120), default="")
