import pytest


@pytest.mark.asyncio
async def test_batch_completions(client, auth_headers):
    payload = {
        "requests": [
            {
                "model": "mock-gpt-4",
                "messages": [{"role": "user", "content": "one"}],
            },
            {
                "model": "echo-default",
                "provider": "echo",
                "messages": [{"role": "user", "content": "two"}],
            },
        ]
    }
    response = await client.post("/v1/chat/completions/batch", json=payload, headers=auth_headers)
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 2
    assert results[0]["success"] is True
    assert results[1]["success"] is True
    assert "echo:" in results[1]["response"]["choices"][0]["message"]["content"]
