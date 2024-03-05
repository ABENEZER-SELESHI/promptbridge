import pytest


@pytest.mark.asyncio
async def test_health_no_auth(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_ready_reports_providers(client):
    response = await client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert "mock" in body["providers"]


@pytest.mark.asyncio
async def test_chat_requires_auth(client):
    payload = {
        "model": "mock-gpt-4",
        "messages": [{"role": "user", "content": "hello"}],
    }
    response = await client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_completion_mock(client, auth_headers):
    payload = {
        "model": "mock-gpt-4",
        "messages": [{"role": "user", "content": "ping"}],
    }
    response = await client.post("/v1/chat/completions", json=payload, headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["choices"][0]["message"]["content"] == "[mock] ping"
    assert body["usage"]["total_tokens"] > 0


@pytest.mark.asyncio
async def test_echo_provider(client, auth_headers):
    payload = {
        "model": "echo-default",
        "provider": "echo",
        "messages": [{"role": "user", "content": "test"}],
    }
    response = await client.post("/v1/chat/completions", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["choices"][0]["message"]["content"] == "echo: test"


@pytest.mark.asyncio
async def test_list_models(client, auth_headers):
    response = await client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert any(item["provider"] == "mock" for item in data)
