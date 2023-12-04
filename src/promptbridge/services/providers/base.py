from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from promptbridge.schemas.chat import ChatCompletionRequest, ChatCompletionResponse


class ProviderError(Exception):
    """Raised when a provider cannot fulfill a request."""


class BaseProvider(ABC):
    name: str

    @abstractmethod
    async def complete(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        raise NotImplementedError

    @abstractmethod
    async def stream(self, request: ChatCompletionRequest) -> AsyncIterator[str]:
        raise NotImplementedError

    async def health(self) -> dict[str, str]:
        return {"status": "ok", "provider": self.name}
