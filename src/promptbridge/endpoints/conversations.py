from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Request

from promptbridge.schemas.conversations import (
    ConversationDetail,
    ConversationListResponse,
    ConversationMessage,
    ConversationSummary,
)

router = APIRouter(prefix="/v1/conversations", tags=["conversations"])


@router.get("", response_model=ConversationListResponse)
async def list_conversations(request: Request, limit: int = 50, offset: int = 0):
    store = request.app.state.conversation_store
    rows = await store.list_conversations(limit=min(limit, 100), offset=max(offset, 0))
    data = [
        ConversationSummary(
            id=row["id"],
            provider=row["provider"],
            model=row["model"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            message_count=int(row.get("message_count", 0)),
        )
        for row in rows
    ]
    return ConversationListResponse(data=data)


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str, request: Request):
    store = request.app.state.conversation_store
    row = await store.get_conversation(conversation_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = [
        ConversationMessage(
            role=message["role"],
            content=message["content"],
            created_at=message["created_at"],
        )
        for message in row["messages"]
    ]
    return ConversationDetail(
        id=row["id"],
        provider=row["provider"],
        model=row["model"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        messages=messages,
    )


@router.delete("/{conversation_id}")
async def delete_conversation(conversation_id: str, request: Request):
    store = request.app.state.conversation_store
    deleted = await store.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted", "id": conversation_id}
