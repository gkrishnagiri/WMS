"""FastAPI application entry point for Enterprise Operations Suite."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware
from app.middleware.runtime_observability import RuntimeObservabilityMiddleware
from app.db.session import DatabaseManager
from app.services.redis import RedisManager
from app.telemetry import initialize_telemetry, shutdown_telemetry


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Initialize and release application resources."""
    settings = get_settings()
    configure_logging(settings.log_level)
    application.state.settings = settings
    application.state.database = DatabaseManager(settings)
    application.state.redis = RedisManager(settings)
    application.state.build_timestamp = datetime.now(timezone.utc).isoformat()

    # Resource creation is intentionally lazy. Health checks determine whether
    # external services are reachable without preventing the API from starting.
    application.state.database.initialize()
    application.state.runtime_observability_session_factory = application.state.database.session_factory
    await application.state.redis.connect()
    initialize_telemetry(settings)

    try:
        yield
    finally:
        await application.state.redis.disconnect()
        application.state.database.dispose()
        shutdown_telemetry()


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.platform_name,
    lifespan=lifespan,
)
app.add_middleware(RequestIDMiddleware, header_name=settings.request_id_header)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RuntimeObservabilityMiddleware)
app.include_router(router)
register_exception_handlers(app)
