from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from promptbridge import __version__
from promptbridge.config import AppConfig, load_config
from promptbridge.endpoints import auth, chat, system
from promptbridge.logger import setup_logging
from promptbridge.middleware.auth import require_api_key
from promptbridge.services.factory import ProviderFactory
from promptbridge.services.storage import ConversationStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    store: ConversationStore = app.state.conversation_store
    await store.initialize()
    yield


def create_app(config: AppConfig | None = None) -> FastAPI:
    cfg = config or load_config()
    setup_logging(cfg.debug)

    app = FastAPI(
        title="PromptBridge",
        description="OpenAI-compatible gateway for pluggable LLM providers",
        version=__version__,
        lifespan=lifespan,
    )
    app.state.config = cfg
    app.state.provider_factory = ProviderFactory(cfg)
    app.state.conversation_store = ConversationStore(cfg)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(require_api_key)

    app.include_router(system.router)
    app.include_router(chat.router)
    app.include_router(auth.router)
    return app


app = create_app()
