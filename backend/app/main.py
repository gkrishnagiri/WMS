"""FastAPI application entry point for Enterprise Operations Suite."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.bff.experience_registry import get_experience
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import application_lifespan
from app.core.middleware import RequestIDMiddleware
from app.middleware.runtime_observability import RuntimeObservabilityMiddleware
from app.middleware.opentelemetry_runtime import OpenTelemetryRuntimeMiddleware


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=settings.platform_name,
    lifespan=application_lifespan,
)
app.state.experience = get_experience("full")
app.add_middleware(RequestIDMiddleware, header_name=settings.request_id_header)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RuntimeObservabilityMiddleware)
app.add_middleware(OpenTelemetryRuntimeMiddleware)
app.include_router(router)
register_exception_handlers(app)
