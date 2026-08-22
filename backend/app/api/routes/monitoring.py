"""Monitoring alert-noise simulations and manual triage APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.monitoring import AddAlertsRequest, AlertEventResponse, AlertResponse, AlertRuleResponse, MonitoringComponentResponse, MonitoringSummary, SimulationResult, TriageCaseCreate, TriageCaseResponse, TriageResolveRequest
from app.services import ams_ticket_service, monitoring_service

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


def _error(error: Exception) -> HTTPException:
    return HTTPException(status_code=getattr(error, "status_code", 409), detail=getattr(error, "message", str(error)))


@router.get("/summary", response_model=MonitoringSummary)
def summary(db: Session = Depends(get_db)) -> MonitoringSummary:
    return monitoring_service.get_monitoring_summary(db)


@router.get("/components", response_model=list[MonitoringComponentResponse])
def components(db: Session = Depends(get_db)) -> list[MonitoringComponentResponse]:
    return monitoring_service.list_components(db)


@router.get("/rules", response_model=list[AlertRuleResponse])
def rules(db: Session = Depends(get_db)) -> list[AlertRuleResponse]:
    return monitoring_service.list_rules(db)


@router.get("/alerts", response_model=list[AlertResponse])
def alerts(status_filter: str | None = Query(default=None, alias="status"), severity: str | None = None, component_id: UUID | None = None, component_code: str | None = None, signal_type: str | None = None, metric_name: str | None = None, db: Session = Depends(get_db)) -> list[AlertResponse]:
    return monitoring_service.list_alerts(db, status_filter, severity, component_id, component_code, signal_type, metric_name)


@router.get("/alerts/{alert_id}", response_model=AlertResponse)
def alert_detail(alert_id: UUID, db: Session = Depends(get_db)) -> AlertResponse:
    try:
        return monitoring_service.get_alert(db, alert_id)
    except monitoring_service.MonitoringError as error:
        raise _error(error) from error


@router.post("/alerts/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(alert_id: UUID, db: Session = Depends(get_db)) -> AlertResponse:
    try:
        return monitoring_service.acknowledge_alert(db, alert_id)
    except monitoring_service.MonitoringError as error:
        db.rollback(); raise _error(error) from error


@router.post("/alerts/{alert_id}/suppress", response_model=AlertResponse)
def suppress_alert(alert_id: UUID, db: Session = Depends(get_db)) -> AlertResponse:
    try:
        return monitoring_service.suppress_alert(db, alert_id)
    except monitoring_service.MonitoringError as error:
        db.rollback(); raise _error(error) from error


@router.post("/alerts/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: UUID, db: Session = Depends(get_db)) -> AlertResponse:
    try:
        return monitoring_service.resolve_alert(db, alert_id)
    except monitoring_service.MonitoringError as error:
        db.rollback(); raise _error(error) from error


@router.post("/alerts/{alert_id}/create-ticket", response_model=object, status_code=status.HTTP_201_CREATED)
def alert_ticket(alert_id: UUID, db: Session = Depends(get_db)):
    try:
        return ams_ticket_service.create_ticket_from_alert(db, alert_id)
    except ams_ticket_service.AmsError as error:
        db.rollback(); raise _error(error) from error


@router.get("/alerts/{alert_id}/events", response_model=list[AlertEventResponse])
def alert_events(alert_id: UUID, db: Session = Depends(get_db)) -> list[AlertEventResponse]:
    try:
        return monitoring_service.list_alert_events(db, alert_id)
    except monitoring_service.MonitoringError as error:
        raise _error(error) from error


def _run_simulation(simulation_code: str, db: Session) -> SimulationResult:
    try:
        return monitoring_service.run_simulation(db, simulation_code)
    except monitoring_service.MonitoringError as error:
        db.rollback(); raise _error(error) from error


@router.post("/simulations/api-latency-cascade", response_model=SimulationResult)
def api_latency_cascade(db: Session = Depends(get_db)) -> SimulationResult:
    return _run_simulation("api-latency-cascade", db)


@router.post("/simulations/database-degradation", response_model=SimulationResult)
def database_degradation(db: Session = Depends(get_db)) -> SimulationResult:
    return _run_simulation("database-degradation", db)


@router.post("/simulations/redis-flapping", response_model=SimulationResult)
def redis_flapping(db: Session = Depends(get_db)) -> SimulationResult:
    return _run_simulation("redis-flapping", db)


@router.post("/simulations/frontend-error-burst", response_model=SimulationResult)
def frontend_error_burst(db: Session = Depends(get_db)) -> SimulationResult:
    return _run_simulation("frontend-error-burst", db)


@router.post("/simulations/warehouse-workflow-noise", response_model=SimulationResult)
def warehouse_workflow_noise(db: Session = Depends(get_db)) -> SimulationResult:
    return _run_simulation("warehouse-workflow-noise", db)


@router.post("/simulations/noisy-alert-storm", response_model=SimulationResult)
def noisy_alert_storm(db: Session = Depends(get_db)) -> SimulationResult:
    return _run_simulation("noisy-alert-storm", db)


@router.post("/simulations/{simulation_code}", response_model=SimulationResult)
def simulation(simulation_code: str, db: Session = Depends(get_db)) -> SimulationResult:
    return _run_simulation(simulation_code, db)


@router.get("/triage-cases", response_model=list[TriageCaseResponse])
def triage_cases(db: Session = Depends(get_db)) -> list[TriageCaseResponse]:
    return monitoring_service.list_triage_cases(db)


@router.post("/triage-cases", response_model=TriageCaseResponse, status_code=status.HTTP_201_CREATED)
def create_triage_case(request: TriageCaseCreate, db: Session = Depends(get_db)) -> TriageCaseResponse:
    try:
        return monitoring_service.create_triage_case(db, request)
    except monitoring_service.MonitoringError as error:
        db.rollback(); raise _error(error) from error


@router.get("/triage-cases/{case_id}", response_model=TriageCaseResponse)
def triage_case_detail(case_id: UUID, db: Session = Depends(get_db)) -> TriageCaseResponse:
    try:
        return monitoring_service.get_triage_case(db, case_id)
    except monitoring_service.MonitoringError as error:
        raise _error(error) from error


@router.post("/triage-cases/{case_id}/add-alerts", response_model=TriageCaseResponse)
def add_alerts(case_id: UUID, request: AddAlertsRequest, db: Session = Depends(get_db)) -> TriageCaseResponse:
    try:
        return monitoring_service.add_alerts_to_case(db, case_id, request.alert_ids)
    except monitoring_service.MonitoringError as error:
        db.rollback(); raise _error(error) from error


@router.post("/triage-cases/{case_id}/start-investigation", response_model=TriageCaseResponse)
def investigate(case_id: UUID, db: Session = Depends(get_db)) -> TriageCaseResponse:
    try:
        return monitoring_service.start_investigation(db, case_id)
    except monitoring_service.MonitoringError as error:
        db.rollback(); raise _error(error) from error


@router.post("/triage-cases/{case_id}/resolve", response_model=TriageCaseResponse)
def resolve_case(case_id: UUID, request: TriageResolveRequest, db: Session = Depends(get_db)) -> TriageCaseResponse:
    try:
        return monitoring_service.resolve_triage_case(db, case_id, request.analysis_notes)
    except monitoring_service.MonitoringError as error:
        db.rollback(); raise _error(error) from error


@router.post("/triage-cases/{case_id}/create-ticket", response_model=object, status_code=status.HTTP_201_CREATED)
def triage_ticket(case_id: UUID, db: Session = Depends(get_db)):
    try:
        return ams_ticket_service.create_ticket_from_triage_case(db, case_id)
    except ams_ticket_service.AmsError as error:
        db.rollback(); raise _error(error) from error
