from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def with_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    base_delay_seconds: float = 0.05,
) -> T:
    last_error: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return await operation()
        except Exception as exc:  # noqa: BLE001 - retry boundary
            last_error = exc
            if attempt + 1 >= max_attempts:
                break
            await asyncio.sleep(base_delay_seconds * (2**attempt))
    assert last_error is not None
    raise last_error
