"""Local Tempo, Loki, Prometheus, and Collector integration APIs."""

from fastapi import APIRouter, Request

from app.schemas.observability_stack import StackHealth, StackSummary, TestActionResponse, TestAllResponse
from app.services import observability_stack_service

router = APIRouter(prefix="/api/v1/observability-stack", tags=["observability-stack"])


@router.get("/summary", response_model=StackSummary)
def stack_summary(request: Request) -> StackSummary:
    return observability_stack_service.summary(request)


@router.get("/health", response_model=StackHealth)
def stack_health(request: Request) -> StackHealth:
    return observability_stack_service.health(request)


@router.get("/config")
def stack_config(request: Request) -> dict[str, object]:
    return observability_stack_service.config(request)


@router.post("/test-span", response_model=TestActionResponse)
def test_span() -> TestActionResponse:
    return observability_stack_service.test_span()


@router.post("/test-log", response_model=TestActionResponse)
def test_log() -> TestActionResponse:
    return observability_stack_service.test_log()


@router.post("/test-metric", response_model=TestActionResponse)
def test_metric() -> TestActionResponse:
    return observability_stack_service.test_metric()


@router.post("/test-all", response_model=TestAllResponse)
def test_all() -> TestAllResponse:
    return observability_stack_service.test_all()
