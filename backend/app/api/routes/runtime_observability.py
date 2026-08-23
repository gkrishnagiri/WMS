"""Runtime request observability APIs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import get_db
from app.schemas.observability import LogEventResponse, MetricSampleResponse, TraceResponse
from app.schemas.runtime_observability import RuntimeProbeResponse, RuntimeSummary, RuntimeTraceDetail
from app.services import runtime_observability_service

router = APIRouter(prefix="/api/v1/runtime-observability", tags=["runtime-observability"])


def _settings(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/summary", response_model=RuntimeSummary)
def summary(request: Request, db: Session = Depends(get_db)) -> RuntimeSummary:
    settings = _settings(request)
    return runtime_observability_service.runtime_summary(db, settings.runtime_observability_slow_request_ms)


@router.get("/traces", response_model=list[TraceResponse])
def traces(status: str | None = None, method: str | None = None, path: str | None = None, correlation_id: str | None = None, request_id: str | None = None, db: Session = Depends(get_db)) -> list[TraceResponse]:
    return runtime_observability_service.list_runtime_traces(db, status, method, path, correlation_id, request_id)


@router.get("/traces/{trace_identifier}", response_model=RuntimeTraceDetail)
def trace_detail(trace_identifier: str, db: Session = Depends(get_db)) -> RuntimeTraceDetail:
    try: return runtime_observability_service.get_runtime_trace(db, trace_identifier)
    except ValueError as error: raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/logs", response_model=list[LogEventResponse])
def logs(level: str | None = None, event_type: str | None = None, trace_id: str | None = None, correlation_id: str | None = None, db: Session = Depends(get_db)) -> list[LogEventResponse]:
    return runtime_observability_service.list_runtime_logs(db, level, event_type, trace_id, correlation_id)


@router.get("/metrics", response_model=list[MetricSampleResponse])
def metrics(metric_name: str | None = None, trace_id: str | None = None, component_code: str | None = None, severity: str | None = None, db: Session = Depends(get_db)) -> list[MetricSampleResponse]:
    return runtime_observability_service.list_runtime_metrics(db, metric_name, trace_id, component_code, severity)


@router.post("/probes/backend-health", response_model=RuntimeProbeResponse)
async def backend_health_probe(request: Request, db: Session = Depends(get_db)) -> RuntimeProbeResponse:
    return await runtime_observability_service.run_backend_health_probe(db, request.app.state.redis)
