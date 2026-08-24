"""Local frontend/backend experience topology metadata."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.bff.experience_registry import EXPERIENCE_DEFINITIONS, ExperienceDefinition

router = APIRouter(prefix="/api/v1/platform", tags=["platform"])


def _current_experience(request: Request) -> ExperienceDefinition:
    return getattr(request.app.state, "experience", EXPERIENCE_DEFINITIONS["full"])


def _experience_payload(experience: ExperienceDefinition) -> dict[str, object]:
    return {
        "code": experience.code,
        "name": experience.name,
        "frontend_url": experience.frontend_url,
        "backend_url": experience.backend_url,
        "description": experience.description,
    }


@router.get("/experiences")
async def experiences() -> list[dict[str, object]]:
    return [_experience_payload(experience) for experience in EXPERIENCE_DEFINITIONS.values()]


@router.get("/current-experience")
async def current_experience(request: Request) -> dict[str, object]:
    experience = _current_experience(request)
    return {
        **_experience_payload(experience),
        "shared_database": True,
        "shared_codebase": True,
        "physical_service_split": False,
    }


@router.get("/topology")
async def topology() -> dict[str, object]:
    return {
        "mode": "local-demo",
        "database": {"type": "postgresql", "host_port": 15432},
        "cache": {"type": "redis", "host_port": 6379},
        "frontends": [{"experience": item.code, "url": item.frontend_url} for item in EXPERIENCE_DEFINITIONS.values()],
        "backends": [{"experience": item.code, "url": item.backend_url} for item in EXPERIENCE_DEFINITIONS.values()],
        "observability": {
            "grafana": "http://localhost:3001",
            "prometheus": "http://localhost:9090",
            "tempo": "http://localhost:3200",
            "loki": "http://localhost:3100",
            "otel_collector_grpc": "http://localhost:4317",
            "otel_collector_http": "http://localhost:4318",
        },
    }
