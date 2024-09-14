import pytest


@pytest.mark.asyncio
async def test_list_and_get_conversation(client, auth_headers):
    payload = {
        "model": "mock-gpt-4",
        "messages": [{"role": "user", "content": "store this"}],
        "conversation_id": "conv-test-001",
    }
    create = await client.post("/v1/chat/completions", json=payload, headers=auth_headers)
    assert create.status_code == 200

    listed = await client.get("/v1/conversations", headers=auth_headers)
    assert listed.status_code == 200
    ids = [item["id"] for item in listed.json()["data"]]
    assert "conv-test-001" in ids

    detail = await client.get("/v1/conversations/conv-test-001", headers=auth_headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["provider"] == "mock"
    assert len(body["messages"]) >= 2


@pytest.mark.asyncio
async def test_delete_conversation(client, auth_headers):
    payload = {
        "model": "mock-gpt-4",
        "messages": [{"role": "user", "content": "delete me"}],
        "conversation_id": "conv-delete-001",
    }
    await client.post("/v1/chat/completions", json=payload, headers=auth_headers)
    deleted = await client.delete("/v1/conversations/conv-delete-001", headers=auth_headers)
    assert deleted.status_code == 200
    missing = await client.get("/v1/conversations/conv-delete-001", headers=auth_headers)
    assert missing.status_code == 404
