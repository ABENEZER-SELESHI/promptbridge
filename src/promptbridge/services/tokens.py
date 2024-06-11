from __future__ import annotations

from promptbridge.schemas.chat import ChatCompletionRequest


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 characters per token for English text."""
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def estimate_request_tokens(request: ChatCompletionRequest) -> int:
    total = sum(estimate_tokens(message.content) for message in request.messages)
    if request.max_tokens:
        total += request.max_tokens
    return total


def validate_token_budget(request: ChatCompletionRequest, budget: int) -> None:
    used = estimate_request_tokens(request)
    if used > budget:
        raise ValueError(
            f"Estimated token usage {used} exceeds configured budget {budget}"
        )
