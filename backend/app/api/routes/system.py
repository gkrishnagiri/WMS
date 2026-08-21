"""System and platform identity endpoints."""

from __future__ import annotations

import platform
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.core.config import Settings

router = APIRouter(tags=["system"])


def _settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/")
async def root(request: Request) -> dict[str, str]:
    settings = _settings(request)
    return {
        "application": settings.app_name,
        "platform": settings.platform_name,
        "status": "running",
    }


@router.get("/health")
async def health(request: Request) -> JSONResponse:
    settings = _settings(request)
    database_healthy = request.app.state.database.check_connection()
    redis_healthy = await request.app.state.redis.ping()
    checks = {
        "api": "healthy",
        "database": "healthy" if database_healthy else "unhealthy",
        "redis": "healthy" if redis_healthy else "unhealthy",
    }
    body = {
        "status": "healthy" if database_healthy and redis_healthy else "unhealthy",
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "checks": checks,
    }
    return JSONResponse(
        status_code=200 if body["status"] == "healthy" else 503,
        content=body,
    )


@router.get("/version")
async def version(request: Request) -> dict[str, str]:
    settings = _settings(request)
    return {
        "application": settings.app_name,
        "platform": settings.platform_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "python_version": platform.python_version(),
        "git_commit": request.app.state.database.git_commit,
        "build_timestamp": request.app.state.build_timestamp
        or datetime.now(timezone.utc).isoformat(),
    }
