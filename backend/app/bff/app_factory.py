"""Factory for local experience-specific BFF applications."""

from __future__ import annotations

from typing import Iterable

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse

from app.api.routes import agent_chat_router, agent_knowledge_router, agent_investigations_router, ai_config_router, ams_router, batch_router, copilot_router, monitoring_router, observability_router, observability_alerts_router, operations_router, runtime_observability_router, observability_stack_router, synthetic_users_router, user_reports_router, warehouse_router
from app.api.routes.facades import agentic_router, business_router, observability_router as observability_facade_router, operations_router as operations_facade_router, simulation_router
from app.api.routes.platform import router as platform_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.lifespan import application_lifespan
from app.core.middleware import RequestIDMiddleware
from app.middleware.opentelemetry_runtime import OpenTelemetryRuntimeMiddleware
from app.middleware.runtime_observability import RuntimeObservabilityMiddleware
from app.bff.experience_registry import ExperienceDefinition


ROUTERS = {
    "warehouse": warehouse_router,
    "operations": operations_router,
    "ams": ams_router,
    "synthetic_users": synthetic_users_router,
    "user_reports": user_reports_router,
    "monitoring": monitoring_router,
    "observability": observability_router,
    "runtime_observability": runtime_observability_router,
    "observability_stack": observability_stack_router,
    "observability_alerts": observability_alerts_router,
    "agent_chat": agent_chat_router,
    "agent_knowledge": agent_knowledge_router,
    "agent_investigations": agent_investigations_router,
    "batch": batch_router,
    "copilot": copilot_router,
    "ai_config": ai_config_router,
}


def _filtered_router(source: APIRouter, allowed_prefixes: Iterable[str]) -> APIRouter:
    prefixes = tuple(allowed_prefixes)
    filtered = APIRouter()
    filtered.routes = [
        route for route in source.routes
        if isinstance(route, APIRoute) and any(route.path == prefix or route.path.startswith(f"{prefix}/") for prefix in prefixes)
    ]
    return filtered


def _include_group(application: FastAPI, group: str, prefixes: Iterable[str] | None = None) -> None:
    source = ROUTERS[group]
    application.include_router(source if prefixes is None else _filtered_router(source, prefixes))


def _bff_health(application: FastAPI, definition: ExperienceDefinition) -> None:
    @application.get("/health", tags=["system"])
    async def health() -> JSONResponse:
        database_healthy = application.state.database.check_connection()
        redis_healthy = await application.state.redis.ping()
        body = {
            "status": "healthy" if database_healthy and redis_healthy else "unhealthy",
            "application": application.state.settings.app_name,
            "version": application.state.settings.app_version,
            "environment": application.state.settings.app_env,
            "experience": definition.code,
            "experience_name": definition.name,
            "backend_port": int(definition.backend_url.rsplit(":", 1)[1]),
            "checks": {"api": "healthy", "database": "healthy" if database_healthy else "unhealthy", "redis": "healthy" if redis_healthy else "unhealthy"},
        }
        return JSONResponse(
            status_code=200 if body["status"] == "healthy" else 503,
            content=body,
        )


def create_bff_app(definition: ExperienceDefinition) -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=definition.name, version=settings.app_version, description=definition.description, lifespan=application_lifespan)
    application.state.experience = definition
    application.add_middleware(RequestIDMiddleware, header_name=settings.request_id_header)
    application.add_middleware(CORSMiddleware, allow_origins=list(definition.allowed_origins), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    application.add_middleware(RuntimeObservabilityMiddleware)
    application.add_middleware(OpenTelemetryRuntimeMiddleware)
    _bff_health(application, definition)
    application.include_router(platform_router)

    if definition.code == "business":
        application.include_router(business_router)
        _include_group(application, "warehouse")
        _include_group(application, "agent_chat", ("/api/v1/agent-chat/summary", "/api/v1/agent-chat/intake/user-issue", "/api/v1/agent-chat/intake/from-user-report", "/api/v1/agent-chat/sessions"))
        _include_group(application, "agent_knowledge", ("/api/v1/agent-knowledge/summary", "/api/v1/agent-knowledge/search"))
    elif definition.code == "operations":
        application.include_router(operations_facade_router)
        _include_group(application, "operations", ("/api/v1/operations/exceptions",))
        _include_group(application, "ams")
        _include_group(application, "user_reports")
        _include_group(application, "monitoring", ("/api/v1/monitoring/summary", "/api/v1/monitoring/components", "/api/v1/monitoring/rules", "/api/v1/monitoring/alerts", "/api/v1/monitoring/triage-cases"))
        _include_group(application, "batch", ("/api/v1/batch/runs",))
        _include_group(application, "observability", ("/api/v1/observability/diagnostic-cases", "/api/v1/observability/diagnostics"))
        _include_group(application, "copilot", ("/api/v1/copilot/sessions",))
        _include_group(application, "observability_alerts")
        _include_group(application, "agent_chat")
        _include_group(application, "agent_knowledge")
        _include_group(application, "ai_config", ("/api/v1/ai-config/real-model/status", "/api/v1/ai-config/real-model/dry-run"))
        _include_group(application, "agent_investigations")
    elif definition.code == "simulation":
        application.include_router(simulation_router)
        _include_group(application, "synthetic_users")
        _include_group(application, "batch")
        _include_group(application, "monitoring", ("/api/v1/monitoring/simulations",))
        _include_group(application, "observability", ("/api/v1/observability/simulations",))
        _include_group(application, "observability_stack", ("/api/v1/observability-stack/test",))
    elif definition.code == "observability":
        application.include_router(observability_facade_router)
        _include_group(application, "runtime_observability")
        _include_group(application, "observability")
        _include_group(application, "observability_stack")
        _include_group(application, "observability_alerts")
        _include_group(application, "agent_chat", ("/api/v1/agent-chat/intake/from-observability-alert", "/api/v1/agent-chat/intake/from-diagnostic-case"))
    elif definition.code == "agentic":
        application.include_router(agentic_router)
        _include_group(application, "copilot")
        _include_group(application, "ai_config")
        _include_group(application, "agent_chat")
        _include_group(application, "agent_knowledge")
        _include_group(application, "agent_investigations")
    else:
        raise ValueError(f"Unsupported BFF experience: {definition.code}")

    register_exception_handlers(application)
    return application
