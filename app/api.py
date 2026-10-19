from __future__ import annotations

from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from openai import OpenAIError
from pydantic import BaseModel, Field, field_validator

from app.services.chat_agent import ChatConfigurationError, complete_chat, prepare_chat
from app.services.inbox_agent import process_email
from app.services.knowledge_brain import answer_question, create_escalation, get_ingestion_status, list_escalations, resolve_escalation, run_ingestion
from app.services.meeting_agent import process_meeting

app = FastAPI(title="AI Tech Consultant", version="0.1.0")


class QueryRequest(BaseModel):
    question: str = Field(..., description="Question to answer using the knowledge brain")
    session_id: str | None = None
    strict: bool = False


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Chat history content cannot be empty.")
        return value.strip()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Chat message cannot be empty.")
        return value.strip()


class IngestionRequest(BaseModel):
    test_batch_only: bool = False
    limit: int = 10


class EscalationCreateRequest(BaseModel):
    question: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    reason: str = ""


class EscalationResolveRequest(BaseModel):
    approved_answer: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    reviewer: str = "human-reviewer"


class EmailRequest(BaseModel):
    email_id: str | None = None
    sender: str | None = None
    recipient: str | None = None
    subject: str = ""
    body: str = ""
    thread_id: str | None = None
    timestamp: str | None = None
    previous_messages: list[str] = Field(default_factory=list)


class MeetingRequest(BaseModel):
    title: str
    transcript_text: str
    client_name: str | None = None
    follow_up_to_id: str | None = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/query")
def query_knowledge(payload: QueryRequest) -> dict[str, Any]:
    result = answer_question(payload.question, payload.strict)
    return result


@app.post("/api/v1/chat")
def knowledge_chat(payload: ChatRequest) -> dict[str, Any]:
    try:
        prepared = prepare_chat(
            payload.message,
            [item.model_dump() for item in payload.history],
        )
        return complete_chat(prepared)
    except ChatConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except OpenAIError as exc:
        raise HTTPException(status_code=502, detail=f"AI provider request failed: {exc}") from exc


@app.post("/api/v1/ingestion/run")
def ingestion_run(payload: IngestionRequest) -> dict[str, Any]:
    return run_ingestion(payload.test_batch_only, payload.limit)


@app.get("/api/v1/ingestion/status")
def ingestion_status() -> dict[str, Any]:
    return get_ingestion_status()


@app.post("/api/v1/escalations")
def create_escalation_endpoint(payload: EscalationCreateRequest) -> dict[str, Any]:
    return create_escalation(payload.question, payload.evidence, payload.reason)


@app.get("/api/v1/escalations")
def list_escalation_endpoint() -> dict[str, Any]:
    return {"items": list_escalations()}


@app.post("/api/v1/escalations/{escalation_id}/resolve")
def resolve_escalation_endpoint(escalation_id: int, payload: EscalationResolveRequest) -> dict[str, Any]:
    return resolve_escalation(escalation_id, payload.approved_answer, payload.sources, payload.reviewer)


@app.post("/api/v1/inbox/process")
def process_inbox_email(payload: EmailRequest) -> dict[str, Any]:
    result = process_email(payload.model_dump())
    return result


@app.post("/api/v1/meetings/process")
def process_meeting_endpoint(payload: MeetingRequest) -> dict[str, Any]:
    return process_meeting(payload.title, payload.transcript_text, payload.client_name or "")
