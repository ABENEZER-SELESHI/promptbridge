from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from promptbridge import __version__
from promptbridge.config import AppConfig, load_config
from promptbridge.endpoints import auth, chat, conversations, metrics, system
from promptbridge.logger import setup_logging
from promptbridge.middleware.auth import require_api_key
from promptbridge.middleware.request_pipeline import attach_request_id, enforce_rate_limit
from promptbridge.services.circuit_breaker import CircuitBreakerConfig, CircuitBreakerRegistry
from promptbridge.services.factory import ProviderFactory
from promptbridge.services.metrics import MetricsCollector
from promptbridge.services.rate_limiter import RateLimitConfig, RateLimiter
from promptbridge.services.router import ModelRouter
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
    app.state.model_router = ModelRouter.from_config(cfg.routing_rules)
    app.state.metrics = MetricsCollector()
    app.state.rate_limiter = RateLimiter(
        RateLimitConfig(
            max_requests=cfg.rate_limit_max_requests,
            window_seconds=cfg.rate_limit_window_seconds,
        )
    )
    app.state.circuit_breakers = CircuitBreakerRegistry(
        CircuitBreakerConfig(
            failure_threshold=cfg.circuit_failure_threshold,
            recovery_timeout_seconds=cfg.circuit_recovery_seconds,
        )
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware("http")(attach_request_id)
    app.middleware("http")(enforce_rate_limit)
    app.middleware("http")(require_api_key)

    app.include_router(system.router)
    app.include_router(chat.router)
    app.include_router(auth.router)
    app.include_router(conversations.router)
    app.include_router(metrics.router)
    return app


app = create_app()
