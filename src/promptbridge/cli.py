from __future__ import annotations

import argparse

import uvicorn

from promptbridge.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PromptBridge API server")
    parser.add_argument("--config", default="config.conf", help="Path to config file")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    config = load_config()
    host = args.host or config.host
    port = args.port or config.port
    uvicorn.run(
        "promptbridge.main:app",
        host=host,
        port=port,
        reload=config.debug,
    )


if __name__ == "__main__":
    main()
