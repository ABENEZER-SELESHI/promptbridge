from promptbridge.services.router import ModelRouter, RouteRule


def test_router_prefers_explicit_provider():
    router = ModelRouter([RouteRule(pattern="mock-.*", provider="mock", priority=10)])
    assert router.resolve("anything", explicit_provider="echo", default_provider="mock") == "echo"


def test_router_matches_pattern():
    router = ModelRouter([RouteRule(pattern="echo-.*", provider="echo", priority=5)])
    assert router.resolve("echo-fast", None, "mock") == "echo"


def test_router_falls_back_to_default():
    router = ModelRouter()
    assert router.resolve("unknown-model", None, "mock") == "mock"


def test_router_from_config():
    router = ModelRouter.from_config(
        [{"pattern": "template-.*", "provider": "template", "priority": 8}]
    )
    assert router.resolve("template-assistant", None, "mock") == "template"
