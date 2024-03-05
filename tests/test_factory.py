import pytest

from promptbridge.config import AppConfig
from promptbridge.services.factory import ProviderFactory
from promptbridge.services.providers.base import ProviderError


def test_factory_creates_mock():
    cfg = AppConfig(enabled_providers=["mock", "echo"], default_provider="mock")
    factory = ProviderFactory(cfg)
    provider = factory.create("mock")
    assert provider.name == "mock"


def test_factory_rejects_disabled_provider():
    cfg = AppConfig(enabled_providers=["mock"], default_provider="mock")
    factory = ProviderFactory(cfg)
    with pytest.raises(ProviderError):
        factory.create("echo")


def test_factory_lists_enabled():
    cfg = AppConfig(enabled_providers=["mock", "echo"])
    factory = ProviderFactory(cfg)
    assert set(factory.list_providers()) == {"mock", "echo"}
