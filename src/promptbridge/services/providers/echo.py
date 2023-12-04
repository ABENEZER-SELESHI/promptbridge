from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

from promptbridge.schemas.chat import (
    ChatCompletionChoice,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    UsageInfo,
)
from promptbridge.services.providers.base import BaseProvider


class EchoProvider(BaseProvider):
    name = "echo"

    def __init__(self, prefix: str = "echo:") -> None:
        self.prefix = prefix

    async def complete(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        last_user = next(
            (m.content for m in reversed(request.messages) if m.role == "user"),
            "",
        )
        reply = f"{self.prefix} {last_user}".strip()
        prompt_tokens = sum(len(m.content.split()) for m in request.messages)
        completion_tokens = len(reply.split())
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=reply),
                )
            ],
            usage=UsageInfo(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )

    async def stream(self, request: ChatCompletionRequest) -> AsyncIterator[str]:
        response = await self.complete(request)
        content = response.choices[0].message.content
        chunk_id = response.id
        model = response.model
        for char in content:
            chunk = ChatCompletionChunk(
                id=chunk_id,
                model=model,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(content=char),
                        finish_reason=None,
                    )
                ],
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
        final = ChatCompletionChunk(
            id=chunk_id,
            model=model,
            choices=[
                ChatCompletionChunkChoice(
                    index=0,
                    delta=ChatCompletionChunkDelta(),
                    finish_reason="stop",
                )
            ],
        )
        yield f"data: {final.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"
