"""API routes for deterministic observability alerting."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.observability_alerts import AlertEvaluationRunResponse, AlertEventResponse, AlertRuleResponse, EvaluateAlertsRequest, ObservabilityAlertSummary
from app.services import observability_alert_service as service

router = APIRouter(prefix="/api/v1/observability-alerts", tags=["observability-alerts"])


def _error(error: Exception) -> HTTPException:
    return HTTPException(status_code=getattr(error, "status_code", 409), detail=getattr(error, "message", str(error)))


@router.get("/summary", response_model=ObservabilityAlertSummary)
def summary(db: Session = Depends(get_db)) -> ObservabilityAlertSummary:
    return service.get_summary(db)


@router.get("/rules", response_model=list[AlertRuleResponse])
def rules(db: Session = Depends(get_db)) -> list[AlertRuleResponse]:
    return service.list_rules(db)


@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
def rule_detail(rule_id: UUID, db: Session = Depends(get_db)) -> AlertRuleResponse:
    try:
        return service.get_rule(db, rule_id)
    except service.ObservabilityAlertError as error:
        raise _error(error) from error


@router.post("/rules/{rule_id}/enable", response_model=AlertRuleResponse)
def enable_rule(rule_id: UUID, db: Session = Depends(get_db)) -> AlertRuleResponse:
    try:
        return service.set_rule_enabled(db, rule_id, True)
    except service.ObservabilityAlertError as error:
        db.rollback(); raise _error(error) from error


@router.post("/rules/{rule_id}/disable", response_model=AlertRuleResponse)
def disable_rule(rule_id: UUID, db: Session = Depends(get_db)) -> AlertRuleResponse:
    try:
        return service.set_rule_enabled(db, rule_id, False)
    except service.ObservabilityAlertError as error:
        db.rollback(); raise _error(error) from error


@router.post("/evaluate", response_model=AlertEvaluationRunResponse)
def evaluate(request: EvaluateAlertsRequest, db: Session = Depends(get_db)) -> AlertEvaluationRunResponse:
    try:
        return service.evaluate(db, request.trigger_source)
    except service.ObservabilityAlertError as error:
        db.rollback(); raise _error(error) from error


@router.post("/evaluate/{rule_id}", response_model=AlertEvaluationRunResponse)
def evaluate_rule(rule_id: UUID, request: EvaluateAlertsRequest | None = None, db: Session = Depends(get_db)) -> AlertEvaluationRunResponse:
    try:
        return service.evaluate(db, (request or EvaluateAlertsRequest()).trigger_source, rule_id)
    except service.ObservabilityAlertError as error:
        db.rollback(); raise _error(error) from error


@router.get("/evaluation-runs", response_model=list[AlertEvaluationRunResponse])
def evaluation_runs(db: Session = Depends(get_db)) -> list[AlertEvaluationRunResponse]:
    return service.list_evaluation_runs(db)


@router.get("/evaluation-runs/{run_id}", response_model=AlertEvaluationRunResponse)
def evaluation_run_detail(run_id: str, db: Session = Depends(get_db)) -> AlertEvaluationRunResponse:
    try:
        return service.get_evaluation_run(db, run_id)
    except service.ObservabilityAlertError as error:
        raise _error(error) from error


@router.get("/events", response_model=list[AlertEventResponse])
def events(status: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[AlertEventResponse]:
    return service.list_events(db, status)


@router.get("/events/{event_id}", response_model=AlertEventResponse)
def event_detail(event_id: UUID, db: Session = Depends(get_db)) -> AlertEventResponse:
    try:
        return service.get_event(db, event_id)
    except service.ObservabilityAlertError as error:
        raise _error(error) from error


@router.post("/events/{event_id}/acknowledge", response_model=AlertEventResponse)
def acknowledge(event_id: UUID, db: Session = Depends(get_db)) -> AlertEventResponse:
    try:
        return service.transition_event(db, event_id, "ACKNOWLEDGED")
    except service.ObservabilityAlertError as error:
        db.rollback(); raise _error(error) from error


@router.post("/events/{event_id}/resolve", response_model=AlertEventResponse)
def resolve(event_id: UUID, db: Session = Depends(get_db)) -> AlertEventResponse:
    try:
        return service.transition_event(db, event_id, "RESOLVED")
    except service.ObservabilityAlertError as error:
        db.rollback(); raise _error(error) from error


@router.post("/events/{event_id}/create-ticket", response_model=object)
def create_ticket(event_id: UUID, db: Session = Depends(get_db)):
    try:
        return service.create_ticket(db, event_id)
    except service.ObservabilityAlertError as error:
        db.rollback(); raise _error(error) from error
