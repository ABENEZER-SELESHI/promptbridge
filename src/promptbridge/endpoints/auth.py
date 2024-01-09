from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.get("/status")
async def auth_status(request: Request) -> dict[str, object]:
    config = request.app.state.config
    return {
        "require_auth": config.require_auth,
        "auth_mode": "api_key",
    }


@router.post("/verify")
async def verify_key(request: Request) -> dict[str, str]:
    config = request.app.state.config
    header = request.headers.get("authorization", "")
    token = header.removeprefix("Bearer ").strip() or request.headers.get("x-api-key", "")
    if config.require_auth and token != config.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {"status": "verified"}
