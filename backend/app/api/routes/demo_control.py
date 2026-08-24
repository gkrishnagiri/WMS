"""Read-only APIs for local demo stack status and navigation."""

from fastapi import APIRouter, Request

from app.schemas.demo_control import DemoReadinessResponse
from app.services import demo_control_service

router = APIRouter(prefix="/api/v1/demo-control", tags=["demo-control"])


@router.get("/summary")
def summary(request: Request) -> dict[str, object]:
    return demo_control_service.summary(request)


@router.get("/components")
def components() -> dict[str, object]:
    return demo_control_service.components()


@router.get("/urls")
def demo_urls() -> dict[str, object]:
    return demo_control_service.urls()


@router.get("/readiness", response_model=DemoReadinessResponse)
def readiness() -> DemoReadinessResponse:
    return demo_control_service.readiness()
