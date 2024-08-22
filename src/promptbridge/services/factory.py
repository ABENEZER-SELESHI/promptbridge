from __future__ import annotations

from promptbridge.config import AppConfig, provider_options
from promptbridge.services.providers.base import BaseProvider, ProviderError
from promptbridge.services.providers.echo import EchoProvider
from promptbridge.services.providers.mock import MockProvider
from promptbridge.services.providers.template import TemplateProvider


class ProviderFactory:
    def __init__(self, config: AppConfig) -> None:
        self._config = config
        self._registry: dict[str, type[BaseProvider]] = {
            "mock": MockProvider,
            "echo": EchoProvider,
        }

    def _build_core(self, provider_name: str) -> BaseProvider:
        options = provider_options(self._config, provider_name)
        if provider_name == "mock":
            return MockProvider(
                model=options.get("model", "mock-gpt-4"),
                max_tokens=int(options.get("max_tokens", "4096")),
            )
        if provider_name == "echo":
            return EchoProvider(prefix=options.get("prefix", "echo:"))
        cls = self._registry.get(provider_name)
        if cls is None:
            raise ProviderError(f"Unknown provider '{provider_name}'")
        return cls()

    def create(self, name: str | None = None) -> BaseProvider:
        provider_name = name or self._config.default_provider
        if provider_name not in self._config.enabled_providers:
            raise ProviderError(f"Provider '{provider_name}' is not enabled")
        if provider_name == "template":
            options = provider_options(self._config, "template")
            inner_name = options.get("inner_provider", self._config.default_provider)
            inner = self._build_core(inner_name)
            return TemplateProvider(
                inner=inner,
                system_template=options.get(
                    "system_template",
                    "You are a helpful assistant. Context: $context",
                ),
            )
        return self._build_core(provider_name)

    def list_providers(self) -> list[str]:
        return list(self._config.enabled_providers)
