from __future__ import annotations

from collections.abc import AsyncIterator

from starlette.requests import Request
from starlette.responses import JSONResponse


async def require_api_key(request: Request, call_next):
    app = request.app
    config = app.state.config
    if not config.require_auth:
        return await call_next(request)
    public_paths = {"/health", "/ready", "/docs", "/openapi.json", "/redoc"}
    if request.url.path in public_paths:
        return await call_next(request)
    header = request.headers.get("authorization", "")
    token = header.removeprefix("Bearer ").strip()
    if not token:
        token = request.headers.get("x-api-key", "")
    if token != config.api_key:
        return JSONResponse(status_code=401, content={"detail": "Invalid API key"})
    return await call_next(request)


async def sse_event_stream(source: AsyncIterator[str]) -> AsyncIterator[str]:
    async for event in source:
        yield event
