"""Application-level observability evidence and diagnosis APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.observability import DiagnosticCaseResponse, DiagnosticResolveRequest, DiagnosticSummary, DiagnosticTicketRequest, LogEventResponse, MetricSampleResponse, SimulationRequest, SimulationResult, SuiteResult, TraceResponse
from app.services import observability_service

router = APIRouter(prefix="/api/v1/observability", tags=["observability"])


def _error(error: observability_service.ObservabilityError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("/summary", response_model=DiagnosticSummary)
def summary(db: Session = Depends(get_db)) -> DiagnosticSummary:
    return observability_service.get_summary(db)


@router.get("/traces", response_model=list[TraceResponse])
def traces(status_filter: str | None = Query(default=None, alias="status"), trace_type: str | None = None, source_module: str | None = None, linked_ticket_id: UUID | None = None, linked_alert_id: UUID | None = None, db: Session = Depends(get_db)) -> list[TraceResponse]:
    return observability_service.list_traces(db, status_filter, trace_type, source_module, linked_ticket_id, linked_alert_id)


@router.get("/traces/{trace_identifier}", response_model=TraceResponse)
def trace_detail(trace_identifier: str, db: Session = Depends(get_db)) -> TraceResponse:
    try:
        return observability_service.get_trace(db, trace_identifier)
    except observability_service.ObservabilityError as error:
        raise _error(error) from error


@router.get("/log-events", response_model=list[LogEventResponse])
def log_events(level: str | None = None, event_type: str | None = None, trace_id: UUID | None = None, component_code: str | None = None, linked_ticket_id: UUID | None = None, db: Session = Depends(get_db)) -> list[LogEventResponse]:
    return observability_service.list_logs(db, level, event_type, trace_id, component_code, linked_ticket_id)


@router.get("/metric-samples", response_model=list[MetricSampleResponse])
def metric_samples(metric_name: str | None = None, component_code: str | None = None, severity: str | None = None, trace_id: UUID | None = None, linked_alert_id: UUID | None = None, db: Session = Depends(get_db)) -> list[MetricSampleResponse]:
    return observability_service.list_metrics(db, metric_name, component_code, severity, trace_id, linked_alert_id)


@router.get("/diagnostic-cases", response_model=list[DiagnosticCaseResponse])
def diagnostic_cases(status_filter: str | None = Query(default=None, alias="status"), severity: str | None = None, confidence_level: str | None = None, source_type: str | None = None, linked_ticket_id: UUID | None = None, db: Session = Depends(get_db)) -> list[DiagnosticCaseResponse]:
    return observability_service.list_diagnostics(db, status_filter, severity, confidence_level, source_type, linked_ticket_id)


@router.get("/diagnostic-cases/{case_id}", response_model=DiagnosticCaseResponse)
def diagnostic_detail(case_id: UUID, db: Session = Depends(get_db)) -> DiagnosticCaseResponse:
    try:
        return observability_service.get_diagnostic(db, case_id)
    except observability_service.ObservabilityError as error:
        raise _error(error) from error


@router.post("/diagnostic-cases/{case_id}/link-ticket", response_model=DiagnosticCaseResponse)
def link_ticket(case_id: UUID, request: DiagnosticTicketRequest = DiagnosticTicketRequest(), db: Session = Depends(get_db)) -> DiagnosticCaseResponse:
    try:
        return observability_service.link_diagnostic_ticket(db, case_id, request.ticket_id)
    except observability_service.ObservabilityError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/diagnostic-cases/{case_id}/resolve", response_model=DiagnosticCaseResponse)
def resolve_diagnostic(case_id: UUID, request: DiagnosticResolveRequest, db: Session = Depends(get_db)) -> DiagnosticCaseResponse:
    try:
        return observability_service.resolve_diagnostic(db, case_id, request.resolution_notes)
    except observability_service.ObservabilityError as error:
        db.rollback(); raise _error(error) from error


@router.post("/diagnostics/from-alert/{alert_id}", response_model=DiagnosticCaseResponse, status_code=status.HTTP_201_CREATED)
def diagnosis_from_alert(alert_id: UUID, db: Session = Depends(get_db)) -> DiagnosticCaseResponse:
    try: return observability_service.diagnosis_from_alert(db, alert_id)
    except observability_service.ObservabilityError as error: db.rollback(); raise _error(error) from error


@router.post("/diagnostics/from-triage-case/{case_id}", response_model=DiagnosticCaseResponse, status_code=status.HTTP_201_CREATED)
def diagnosis_from_triage(case_id: UUID, db: Session = Depends(get_db)) -> DiagnosticCaseResponse:
    try: return observability_service.diagnosis_from_triage(db, case_id)
    except observability_service.ObservabilityError as error: db.rollback(); raise _error(error) from error


@router.post("/diagnostics/from-ticket/{ticket_id}", response_model=DiagnosticCaseResponse, status_code=status.HTTP_201_CREATED)
def diagnosis_from_ticket(ticket_id: UUID, db: Session = Depends(get_db)) -> DiagnosticCaseResponse:
    try: return observability_service.diagnosis_from_ticket(db, ticket_id)
    except observability_service.ObservabilityError as error: db.rollback(); raise _error(error) from error


def _simulation(code: str, request: SimulationRequest, db: Session) -> SimulationResult:
    try: return observability_service.run_simulation(db, code, request.create_ticket)
    except observability_service.ObservabilityError as error: db.rollback(); raise _error(error) from error


@router.post("/simulations/database-degradation", response_model=SimulationResult)
def database_degradation(request: SimulationRequest = SimulationRequest(), db: Session = Depends(get_db)) -> SimulationResult: return _simulation("database-degradation", request, db)


@router.post("/simulations/redis-cache-failure", response_model=SimulationResult)
def redis_cache_failure(request: SimulationRequest = SimulationRequest(), db: Session = Depends(get_db)) -> SimulationResult: return _simulation("redis-cache-failure", request, db)


@router.post("/simulations/allocation-failure", response_model=SimulationResult)
def allocation_failure(request: SimulationRequest = SimulationRequest(), db: Session = Depends(get_db)) -> SimulationResult: return _simulation("allocation-failure", request, db)


@router.post("/simulations/shipment-integration-failure", response_model=SimulationResult)
def shipment_integration_failure(request: SimulationRequest = SimulationRequest(), db: Session = Depends(get_db)) -> SimulationResult: return _simulation("shipment-integration-failure", request, db)


@router.post("/simulations/observability-demo-suite", response_model=SuiteResult)
def observability_demo_suite(request: SimulationRequest = SimulationRequest(), db: Session = Depends(get_db)) -> SuiteResult:
    return observability_service.run_suite(db, request.create_ticket)
