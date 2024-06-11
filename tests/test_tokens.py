import pytest

from promptbridge.schemas.chat import ChatCompletionRequest, ChatMessage
from promptbridge.services.tokens import estimate_tokens, estimate_request_tokens, validate_token_budget


def test_estimate_tokens_empty():
    assert estimate_tokens("") == 0


def test_estimate_tokens_non_empty():
    assert estimate_tokens("hello world") >= 1


def test_estimate_request_tokens_includes_max_tokens():
    request = ChatCompletionRequest(
        model="mock-gpt-4",
        messages=[ChatMessage(role="user", content="hi")],
        max_tokens=100,
    )
    total = estimate_request_tokens(request)
    assert total >= 100


def test_validate_token_budget_rejects_large_request():
    request = ChatCompletionRequest(
        model="mock-gpt-4",
        messages=[ChatMessage(role="user", content="x" * 40000)],
    )
    with pytest.raises(ValueError, match="exceeds configured budget"):
        validate_token_budget(request, budget=100)
