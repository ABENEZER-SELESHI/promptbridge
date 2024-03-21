# PromptBridge

**PromptBridge** is a lightweight OpenAI-compatible API gateway that routes chat completion requests to pluggable backend providers.

Built for local development, testing, and self-hosted AI proxy workflows without tying you to a single vendor.

## Features

- OpenAI-compatible `POST /v1/chat/completions` endpoint
- Provider factory with swappable backends (`mock`, `echo`)
- Server-sent events (SSE) streaming responses
- API key authentication
- SQLite conversation persistence
- Health and readiness probes

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

## Development

```bash
pytest
```

## License

MIT — see [LICENSE](LICENSE).
