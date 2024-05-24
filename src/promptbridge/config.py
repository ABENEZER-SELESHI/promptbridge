from __future__ import annotations

import configparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings


class EnvSettings(BaseSettings):
    promptbridge_config: Path | None = None
    promptbridge_api_key: str | None = None

    model_config = {"env_file": ".env", "extra": "ignore"}


@dataclass
class ProviderConfig:
    name: str
    options: dict[str, str] = field(default_factory=dict)


@dataclass
class AppConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    api_key: str = "change-me-in-production"
    require_auth: bool = True
    default_provider: str = "mock"
    enabled_providers: list[str] = field(default_factory=lambda: ["mock", "echo"])
    provider_configs: dict[str, ProviderConfig] = field(default_factory=dict)
    database_path: Path = Path("./data/conversations.sqlite3")
    persist_conversations: bool = True
    token_budget: int = 8192
    enforce_token_budget: bool = True
    rate_limit_enabled: bool = True
    rate_limit_max_requests: int = 60
    rate_limit_window_seconds: int = 60
    routing_rules: list[dict[str, str | int]] = field(default_factory=list)
    circuit_failure_threshold: int = 3
    circuit_recovery_seconds: float = 30.0
    retry_max_attempts: int = 3


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_config(path: Path | None = None) -> AppConfig:
    env = EnvSettings()
    config_path = path or env.promptbridge_config or Path("config.conf")
    parser = configparser.ConfigParser()
    if config_path.exists():
        parser.read(config_path)

    server = parser["server"] if parser.has_section("server") else {}
    auth = parser["auth"] if parser.has_section("auth") else {}
    providers = parser["providers"] if parser.has_section("providers") else {}
    storage = parser["storage"] if parser.has_section("storage") else {}
    limits = parser["limits"] if parser.has_section("limits") else {}
    rate_limit = parser["rate_limit"] if parser.has_section("rate_limit") else {}
    resilience = parser["resilience"] if parser.has_section("resilience") else {}
    routing = parser["routing"] if parser.has_section("routing") else {}

    enabled_raw = providers.get("enabled", "mock,echo")
    enabled = [item.strip() for item in enabled_raw.split(",") if item.strip()]

    provider_configs: dict[str, ProviderConfig] = {}
    for section in parser.sections():
        if section.startswith("provider."):
            name = section.split(".", 1)[1]
            provider_configs[name] = ProviderConfig(name=name, options=dict(parser[section]))

    cfg = AppConfig(
        host=server.get("host", "0.0.0.0"),
        port=int(server.get("port", "8080")),
        debug=_parse_bool(server.get("debug", "false")),
        api_key=env.promptbridge_api_key or auth.get("api_key", "change-me-in-production"),
        require_auth=_parse_bool(auth.get("require_auth", "true")),
        default_provider=providers.get("default", "mock"),
        enabled_providers=enabled,
        provider_configs=provider_configs,
        database_path=Path(storage.get("database_path", "./data/conversations.sqlite3")),
        persist_conversations=_parse_bool(storage.get("persist_conversations", "true")),
        token_budget=int(limits.get("token_budget", "8192")),
        enforce_token_budget=_parse_bool(limits.get("enforce_token_budget", "true")),
        rate_limit_enabled=_parse_bool(rate_limit.get("enabled", "true")),
        rate_limit_max_requests=int(rate_limit.get("max_requests", "60")),
        rate_limit_window_seconds=int(rate_limit.get("window_seconds", "60")),
        routing_rules=_parse_routing_rules(routing.get("rules", "")),
        circuit_failure_threshold=int(resilience.get("failure_threshold", "3")),
        circuit_recovery_seconds=float(resilience.get("recovery_seconds", "30")),
        retry_max_attempts=int(resilience.get("retry_max_attempts", "3")),
    )
    return cfg


def _parse_routing_rules(raw: str) -> list[dict[str, str | int]]:
    if not raw.strip():
        return []
    rules: list[dict[str, str | int]] = []
    for entry in raw.split(";"):
        entry = entry.strip()
        if not entry:
            continue
        parts = [part.strip() for part in entry.split("|")]
        if len(parts) != 3:
            continue
        pattern, provider, priority = parts
        rules.append({"pattern": pattern, "provider": provider, "priority": int(priority)})
    return rules


def provider_options(cfg: AppConfig, name: str) -> dict[str, Any]:
    provider = cfg.provider_configs.get(name)
    return dict(provider.options) if provider else {}
