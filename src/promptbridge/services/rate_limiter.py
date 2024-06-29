from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass
class RateLimitConfig:
    max_requests: int = 60
    window_seconds: int = 60


class RateLimiter:
    """Sliding-window in-memory rate limiter keyed by client identifier."""

    def __init__(self, config: RateLimitConfig) -> None:
        self._config = config
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        window_start = now - self._config.window_seconds
        bucket = self._hits[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= self._config.max_requests:
            return False
        bucket.append(now)
        return True

    def remaining(self, key: str) -> int:
        now = time.monotonic()
        window_start = now - self._config.window_seconds
        bucket = self._hits[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        return max(0, self._config.max_requests - len(bucket))

    def reset(self, key: str | None = None) -> None:
        if key is None:
            self._hits.clear()
            return
        self._hits.pop(key, None)
