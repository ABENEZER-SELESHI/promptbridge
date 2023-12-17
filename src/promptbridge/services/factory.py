from __future__ import annotations

from promptbridge.config import AppConfig, provider_options
from promptbridge.services.providers.base import BaseProvider, ProviderError
from promptbridge.services.providers.echo import EchoProvider
from promptbridge.services.providers.mock import MockProvider


class ProviderFactory:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._registry: dict[str, type[BaseProvider]] = {
            "mock": MockProvider,
            "echo": EchoProvider,
        }

    def create(self, name: str | None = None) -> BaseProvider:
        provider_name = name or self._config.default_provider
        if provider_name not in self._config.enabled_providers:
            raise ProviderError(f"Provider '{provider_name}' is not enabled")
        cls = self._registry.get(provider_name)
        if cls is None:
            raise ProviderError(f"Unknown provider '{provider_name}'")
        options = provider_options(self._config, provider_name)
        if provider_name == "mock":
            return MockProvider(
                model=options.get("model", "mock-gpt-4"),
                max_tokens=int(options.get("max_tokens", "4096")),
            )
        if provider_name == "echo":
            return EchoProvider(prefix=options.get("prefix", "echo:"))
        return cls()

    def list_providers(self) -> list[str]:
        return list(self._config.enabled_providers)
