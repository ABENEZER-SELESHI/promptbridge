import pytest

from promptbridge.config import AppConfig
from promptbridge.schemas.chat import ChatCompletionRequest, ChatMessage
from promptbridge.services.providers.mock import MockProvider
from promptbridge.services.providers.template import TemplateProvider


@pytest.mark.asyncio
async def test_template_provider_injects_system_prompt():
    provider = TemplateProvider(
        inner=MockProvider(),
        system_template="System context: $context",
    )
    request = ChatCompletionRequest(
        model="template-assistant",
        messages=[ChatMessage(role="user", content="deploy api")],
    )
    response = await provider.complete(request)
    assert "[mock] deploy api" in response.choices[0].message.content
