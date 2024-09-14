# PromptBridge

**PromptBridge** is a lightweight OpenAI-compatible API gateway that routes chat completion requests to pluggable backend providers.

Built for local development, testing, and self-hosted AI proxy workflows without tying you to a single vendor.

## Features

- OpenAI-compatible `POST /v1/chat/completions` endpoint
- Batch completions via `POST /v1/chat/completions/batch`
- Provider factory with swappable backends (`mock`, `echo`, `template`)
- Model routing rules (pattern → provider)
- Server-sent events (SSE) streaming responses
- API key authentication and per-client rate limiting
- Token budget enforcement
- SQLite conversation persistence with list/get/delete API
- Circuit breaker and retry policies for provider resilience
- Request metrics and circuit breaker status endpoint
- Request ID tracing (`X-Request-ID`)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp config.conf.example config.conf
promptbridge
```

Send a request:

```bash
curl -X POST http://127.0.0.1:8080/v1/chat/completions \
  -H "Authorization: Bearer change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-gpt-4",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Configuration

Copy `config.conf.example` to `config.conf` and adjust:

- `[server]` — bind host/port
- `[auth]` — API key and auth requirement
- `[providers]` — default and enabled providers
- `[storage]` — SQLite path and persistence toggle
- `[limits]` — token budget enforcement
- `[rate_limit]` — sliding-window request limits
- `[routing]` — model pattern routing rules
- `[resilience]` — circuit breaker and retry settings

## API overview

| Endpoint | Description |
|---|---|
| `GET /health` | Liveness probe |
| `GET /ready` | Readiness + provider/storage stats |
| `POST /v1/chat/completions` | OpenAI-compatible chat |
| `POST /v1/chat/completions/batch` | Up to 10 parallel chat requests |
| `GET /v1/models` | List routed models |
| `GET /v1/conversations` | List stored conversations |
| `GET /v1/conversations/{id}` | Fetch conversation transcript |
| `DELETE /v1/conversations/{id}` | Delete a conversation |
| `GET /v1/metrics` | Request metrics + circuit breaker snapshot |

## Development

```bash
pytest
```

## License

MIT — see [LICENSE](LICENSE).
