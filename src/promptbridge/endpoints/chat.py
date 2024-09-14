from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from promptbridge.middleware.auth import sse_event_stream
from promptbridge.schemas.chat import ChatCompletionRequest, ChatCompletionResponse
from promptbridge.schemas.conversations import BatchChatRequest, BatchChatResponse, BatchChatResult
from promptbridge.services.providers.base import ProviderError
from promptbridge.services.retry import with_retry
from promptbridge.services.tokens import validate_token_budget

router = APIRouter(prefix="/v1", tags=["chat"])


def _resolve_provider_name(request: ChatCompletionRequest, app_request: Request) -> str:
    router_service = app_request.app.state.model_router
    config = app_request.app.state.config
    return router_service.resolve(
        model=request.model,
        explicit_provider=request.provider,
        default_provider=config.default_provider,
    )


async def _execute_completion(
    body: ChatCompletionRequest,
    request: Request,
    provider_name: str,
) -> ChatCompletionResponse:
    factory = request.app.state.provider_factory
    breakers = request.app.state.circuit_breakers
    config = request.app.state.config
    breaker = breakers.get(provider_name)

    if not breaker.allow_request():
        raise ProviderError(f"Provider '{provider_name}' circuit is open")

    provider = factory.create(provider_name)

    async def operation() -> ChatCompletionResponse:
        return await provider.complete(body)

    try:
        response = await with_retry(operation, max_attempts=config.retry_max_attempts)
        breaker.record_success()
        return response
    except Exception:
        breaker.record_failure()
        raise


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(body: ChatCompletionRequest, request: Request):
    started = time.perf_counter()
    config = request.app.state.config
    store = request.app.state.conversation_store
    metrics = request.app.state.metrics
    provider_name = _resolve_provider_name(body, request)

    try:
        if config.enforce_token_budget:
            validate_token_budget(body, config.token_budget)
        provider = request.app.state.provider_factory.create(provider_name)
    except ValueError as exc:
        metrics.record(
            path=str(request.url.path),
            provider=provider_name,
            status_code=413,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except ProviderError as exc:
        metrics.record(
            path=str(request.url.path),
            provider=provider_name,
            status_code=400,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if body.stream:
        async def event_generator():
            async for chunk in provider.stream(body):
                yield chunk

        metrics.record(
            path=str(request.url.path),
            provider=provider_name,
            status_code=200,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        return EventSourceResponse(sse_event_stream(event_generator()))

    try:
        response = await _execute_completion(body, request, provider_name)
    except ProviderError as exc:
        metrics.record(
            path=str(request.url.path),
            provider=provider_name,
            status_code=503,
            latency_ms=(time.perf_counter() - started) * 1000,
        )
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    conversation_id = body.conversation_id or f"conv-{uuid.uuid4().hex[:12]}"
    await store.save_exchange(conversation_id, provider_name, body, response)
    metrics.record(
        path=str(request.url.path),
        provider=provider_name,
        status_code=200,
        latency_ms=(time.perf_counter() - started) * 1000,
    )
    return response


@router.post("/chat/completions/batch", response_model=BatchChatResponse)
async def batch_chat_completions(body: BatchChatRequest, request: Request):
    results: list[BatchChatResult] = []
    for index, raw in enumerate(body.requests):
        try:
            item = ChatCompletionRequest.model_validate(raw)
            provider_name = _resolve_provider_name(item, request)
            response = await _execute_completion(item, request, provider_name)
            results.append(
                BatchChatResult(
                    index=index,
                    success=True,
                    response=response.model_dump(),
                )
            )
        except Exception as exc:  # noqa: BLE001 - batch isolates per-item failures
            results.append(
                BatchChatResult(index=index, success=False, error=str(exc))
            )
    return BatchChatResponse(results=results)


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
        elif provider_name == "template":
            models.append({"id": "template-assistant", "provider": provider_name})
        else:
            models.append({"id": f"{provider_name}-default", "provider": provider_name})
    return {"object": "list", "data": models}
