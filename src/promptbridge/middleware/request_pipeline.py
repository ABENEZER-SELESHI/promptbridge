from __future__ import annotations

import uuid

from starlette.requests import Request
from starlette.responses import JSONResponse


async def attach_request_id(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or f"req-{uuid.uuid4().hex[:12]}"
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


async def enforce_rate_limit(request: Request, call_next):
    config = request.app.state.config
    if not config.rate_limit_enabled:
        return await call_next(request)

    public_paths = {"/health", "/ready", "/docs", "/openapi.json", "/redoc"}
    if request.url.path in public_paths:
        return await call_next(request)

    limiter = request.app.state.rate_limiter
    client_key = request.headers.get("x-api-key") or request.headers.get("authorization", "anonymous")
    if not limiter.allow(client_key):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded"},
            headers={"X-RateLimit-Remaining": "0"},
        )
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(limiter.remaining(client_key))
    return response
