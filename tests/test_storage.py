import pytest

from promptbridge.config import AppConfig
from promptbridge.schemas.chat import ChatCompletionRequest, ChatMessage
from promptbridge.services.storage import ConversationStore


@pytest.mark.asyncio
async def test_conversation_store_persists_exchange(tmp_path):
    cfg = AppConfig(
        database_path=tmp_path / "conv.sqlite3",
        persist_conversations=True,
    )
    store = ConversationStore(cfg)
    await store.initialize()

    request = ChatCompletionRequest(
        model="mock-gpt-4",
        messages=[ChatMessage(role="user", content="hello")],
    )
    from promptbridge.services.providers.mock import MockProvider

    provider = MockProvider()
    response = await provider.complete(request)
    await store.save_exchange("conv-1", "mock", request, response)

    saved = await store.get_conversation("conv-1")
    assert saved is not None
    assert saved["provider"] == "mock"
    assert len(saved["messages"]) == 2
    stats = await store.stats()
    assert stats["conversations"] == 1
    assert stats["messages"] == 2
