from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class RouteRule:
    pattern: str
    provider: str
    priority: int = 0


class ModelRouter:
    """Maps model names to providers using ordered pattern rules."""

    def __init__(self, rules: list[RouteRule] | None = None) -> None:
        self._rules = sorted(rules or [], key=lambda rule: rule.priority, reverse=True)

    def resolve(self, model: str, explicit_provider: str | None, default_provider: str) -> str:
        if explicit_provider:
            return explicit_provider
        for rule in self._rules:
            if re.fullmatch(rule.pattern, model):
                return rule.provider
        if model.startswith("echo"):
            return "echo"
        if model.startswith("mock"):
            return "mock"
        if model.startswith("template"):
            return "template"
        return default_provider

    @classmethod
    def from_config(cls, raw_rules: list[dict[str, str | int]]) -> ModelRouter:
        rules = [
            RouteRule(
                pattern=str(item["pattern"]),
                provider=str(item["provider"]),
                priority=int(item.get("priority", 0)),
            )
            for item in raw_rules
        ]
        return cls(rules)
