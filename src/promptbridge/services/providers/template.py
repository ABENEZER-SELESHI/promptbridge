from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from string import Template

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
from promptbridge.services.providers.base import BaseProvider, ProviderError


class TemplateProvider(BaseProvider):
    """Applies a system prompt template then delegates to a wrapped provider."""

    name = "template"

    def __init__(
        self,
        inner: BaseProvider,
        system_template: str = "You are a helpful assistant. Context: $context",
    ) -> None:
        self._inner = inner
        self._system_template = system_template

    def _apply_template(self, request: ChatCompletionRequest) -> ChatCompletionRequest:
        user_text = next(
            (message.content for message in reversed(request.messages) if message.role == "user"),
            "",
        )
        rendered = Template(self._system_template).safe_substitute(context=user_text)
        messages = [ChatMessage(role="system", content=rendered), *request.messages]
        return request.model_copy(update={"messages": messages})

    async def complete(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        if not request.messages:
            raise ProviderError("Template provider requires at least one message")
        prepared = self._apply_template(request)
        response = await self._inner.complete(prepared)
        return response.model_copy(update={"model": request.model})

    async def stream(self, request: ChatCompletionRequest) -> AsyncIterator[str]:
        if not request.messages:
            raise ProviderError("Template provider requires at least one message")
        prepared = self._apply_template(request)
        async for chunk in self._inner.stream(prepared):
            yield chunk

    async def health(self) -> dict[str, str]:
        inner_health = await self._inner.health()
        return {"status": "ok", "provider": self.name, "inner": inner_health.get("provider", "")}
