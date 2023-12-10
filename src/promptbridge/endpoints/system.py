from __future__ import annotations

from fastapi import APIRouter, Request

from promptbridge import __version__

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": "promptbridge"}


@router.get("/ready")
async def ready(request: Request) -> dict[str, object]:
    factory = request.app.state.provider_factory
    store = request.app.state.conversation_store
    stats = await store.stats()
    return {
        "status": "ready",
        "version": __version__,
        "providers": factory.list_providers(),
        "storage": stats,
    }
