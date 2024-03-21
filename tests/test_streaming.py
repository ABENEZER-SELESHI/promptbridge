import pytest


@pytest.mark.asyncio
async def test_streaming_chat_returns_event_stream(client, auth_headers):
    payload = {
        "model": "mock-gpt-4",
        "messages": [{"role": "user", "content": "stream me"}],
        "stream": True,
    }
    response = await client.post("/v1/chat/completions", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    body = response.text
    assert "data:" in body
    assert "[DONE]" in body


@pytest.mark.asyncio
async def test_auth_verify(client, auth_headers):
    response = await client.post("/v1/auth/verify", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "verified"
