from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(prefix="/v1/metrics", tags=["metrics"])


@router.get("")
async def metrics_summary(request: Request) -> dict[str, object]:
    metrics = request.app.state.metrics
    breakers = request.app.state.circuit_breakers
    return {
        "metrics": metrics.summary(),
        "circuit_breakers": breakers.snapshot(),
    }


@router.post("/reset")
async def reset_metrics(request: Request) -> dict[str, str]:
    request.app.state.metrics.reset()
    return {"status": "reset"}
