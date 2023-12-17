from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from promptbridge.middleware.auth import sse_event_stream
from promptbridge.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from promptbridge.services.providers.base import ProviderError

router = APIRouter(prefix="/v1", tags=["chat"])


def _resolve_provider_name(request: ChatCompletionRequest, app_request: Request) -> str:
    config = app_request.app.state.config
    if request.provider:
        return request.provider
    if request.model.startswith("echo"):
        return "echo"
    return config.default_provider


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(body: ChatCompletionRequest, request: Request):
    factory = request.app.state.provider_factory
    store = request.app.state.conversation_store
    provider_name = _resolve_provider_name(body, request)
    try:
        provider = factory.create(provider_name)
    except ProviderError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if body.stream:
        async def event_generator():
            async for chunk in provider.stream(body):
                yield chunk

        return EventSourceResponse(sse_event_stream(event_generator()))

    response = await provider.complete(body)
    conversation_id = body.conversation_id or f"conv-{uuid.uuid4().hex[:12]}"
    await store.save_exchange(conversation_id, provider_name, body, response)
    return response


@router.get("/models")
async def list_models(request: Request):
    factory = request.app.state.provider_factory
    config = request.app.state.config
    models = []
    for provider_name in factory.list_providers():
        if provider_name == "mock":
            model_id = config.provider_configs.get("mock", None)
            default_model = "mock-gpt-4"
            if model_id:
                default_model = model_id.options.get("model", default_model)
            models.append({"id": default_model, "provider": provider_name})
        else:
            models.append({"id": f"{provider_name}-default", "provider": provider_name})
    return {"object": "list", "data": models}
