from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class RequestMetric:
    path: str
    provider: str
    status_code: int
    latency_ms: float
    timestamp: float = field(default_factory=time.time)


class MetricsCollector:
    def __init__(self) -> None:
        self._records: list[RequestMetric] = []
        self._totals: dict[str, int] = {
            "requests": 0,
            "errors": 0,
            "completions": 0,
        }

    def record(
        self,
        *,
        path: str,
        provider: str,
        status_code: int,
        latency_ms: float,
    ) -> None:
        self._records.append(
            RequestMetric(
                path=path,
                provider=provider,
                status_code=status_code,
                latency_ms=latency_ms,
            )
        )
        self._totals["requests"] += 1
        if status_code >= 400:
            self._totals["errors"] += 1
        if path.endswith("/chat/completions"):
            self._totals["completions"] += 1

    def summary(self) -> dict[str, object]:
        latencies = [record.latency_ms for record in self._records]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        by_provider: dict[str, int] = {}
        for record in self._records:
            by_provider[record.provider] = by_provider.get(record.provider, 0) + 1
        return {
            "totals": dict(self._totals),
            "average_latency_ms": round(avg_latency, 2),
            "requests_by_provider": by_provider,
            "recent_count": len(self._records),
        }

    def reset(self) -> None:
        self._records.clear()
        self._totals = {"requests": 0, "errors": 0, "completions": 0}
