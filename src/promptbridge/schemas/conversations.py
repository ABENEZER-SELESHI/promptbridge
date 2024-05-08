from __future__ import annotations

from pydantic import BaseModel, Field


class ConversationSummary(BaseModel):
    id: str
    provider: str
    model: str
    created_at: str
    updated_at: str
    message_count: int = 0


class ConversationListResponse(BaseModel):
    object: str = "list"
    data: list[ConversationSummary]


class ConversationMessage(BaseModel):
    role: str
    content: str
    created_at: str


class ConversationDetail(BaseModel):
    id: str
    provider: str
    model: str
    created_at: str
    updated_at: str
    messages: list[ConversationMessage]


class BatchChatRequest(BaseModel):
    requests: list[dict] = Field(min_length=1, max_length=10)


class BatchChatResult(BaseModel):
    index: int
    success: bool
    response: dict | None = None
    error: str | None = None


class BatchChatResponse(BaseModel):
    object: str = "batch"
    results: list[BatchChatResult]
