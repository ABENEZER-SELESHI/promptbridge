import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint(client, auth_headers):
    payload = {
        "model": "mock-gpt-4",
        "messages": [{"role": "user", "content": "metrics please"}],
    }
    await client.post("/v1/chat/completions", json=payload, headers=auth_headers)
    response = await client.get("/v1/metrics", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["metrics"]["totals"]["completions"] >= 1


@pytest.mark.asyncio
async def test_request_id_header(client, auth_headers):
    response = await client.get("/v1/models", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")
