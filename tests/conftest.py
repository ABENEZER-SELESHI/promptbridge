from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from promptbridge.config import AppConfig
from promptbridge.main import create_app


@pytest.fixture
def test_config(tmp_path: Path) -> AppConfig:
    db_path = tmp_path / "test.sqlite3"
    return AppConfig(
        api_key="test-secret-key",
        require_auth=True,
        database_path=db_path,
        persist_conversations=True,
        rate_limit_enabled=False,
        enforce_token_budget=True,
        token_budget=8192,
        enabled_providers=["mock", "echo", "template"],
    )


@pytest.fixture
async def client(test_config: AppConfig):
    app = create_app(test_config)
    await app.state.conversation_store.initialize()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-secret-key"}
