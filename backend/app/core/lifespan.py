"""Shared EOS application resource lifecycle."""

from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.opentelemetry import initialize_opentelemetry, shutdown_opentelemetry
from app.db.session import DatabaseManager
from app.services.redis import RedisManager
from app.telemetry import initialize_telemetry, shutdown_telemetry


@asynccontextmanager
async def application_lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Initialize shared database, Redis, and telemetry resources."""
    settings = get_settings()
    configure_logging(settings.log_level)
    application.state.settings = settings
    application.state.database = DatabaseManager(settings)
    application.state.redis = RedisManager(settings)
    application.state.build_timestamp = datetime.now(timezone.utc).isoformat()

    # Resource creation is intentionally lazy. Health checks determine whether
    # external services are reachable without preventing an app from starting.
    application.state.database.initialize()
    application.state.runtime_observability_session_factory = application.state.database.session_factory
    await application.state.redis.connect()
    initialize_telemetry(settings)
    initialize_opentelemetry(application, settings)

    try:
        yield
    finally:
        await application.state.redis.disconnect()
        application.state.database.dispose()
        shutdown_telemetry()
        shutdown_opentelemetry()
