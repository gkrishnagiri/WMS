"""Deterministic observability alert evaluation and AMS integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ams import AmsTicket
from app.models.batch import BatchRun
from app.models.observability import ObsMetricSample
from app.models.observability_alerts import ObsAlertEvaluationRun, ObsAlertEvent, ObsAlertEventEvidence, ObsAlertRule, ObsAlertTicketLink
from app.schemas.ams import TicketResponse
from app.schemas.observability_alerts import AlertEvaluationRunResponse, AlertEventResponse, AlertRuleResponse, ObservabilityAlertSummary
from app.services import ams_ticket_service

ACTIVE_EVENT_STATUSES = ("OPEN", "ACKNOWLEDGED", "TICKETED")


class ObservabilityAlertError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass
class Signal:
    triggered: bool
    observed_value: float | None
    source_signal: str
    source_url: str | None
    condition_summary: str
    evidence: list[dict]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_number(db: Session, prefix: str) -> str:
    day = _now().strftime("%Y%m%d")
    current = db.scalar(select(func.max(ObsAlertEvaluationRun.run_id)).where(ObsAlertEvaluationRun.run_id.like(f"{prefix}-{day}-%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            pass
    return f"{prefix}-{day}-{sequence:04d}"


def _next_event_number(db: Session) -> str:
    day = _now().strftime("%Y%m%d")
    current = db.scalar(select(func.max(ObsAlertEvent.event_id)).where(ObsAlertEvent.event_id.like(f"ALERT-EVENT-{day}-%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            pass
    return f"ALERT-EVENT-{day}-{sequence:04d}"


def list_rules(db: Session) -> list[AlertRuleResponse]:
    return [AlertRuleResponse.model_validate(item) for item in db.scalars(select(ObsAlertRule).order_by(ObsAlertRule.rule_code)).all()]


def get_rule(db: Session, rule_id: UUID) -> AlertRuleResponse:
    rule = db.get(ObsAlertRule, rule_id)
    if rule is None:
        raise ObservabilityAlertError("Observability alert rule not found.", 404)
    return AlertRuleResponse.model_validate(rule)


def set_rule_enabled(db: Session, rule_id: UUID, enabled: bool) -> AlertRuleResponse:
    rule = db.get(ObsAlertRule, rule_id)
    if rule is None:
        raise ObservabilityAlertError("Observability alert rule not found.", 404)
    rule.enabled = enabled
    rule.updated_at = _now()
    db.commit()
    return AlertRuleResponse.model_validate(rule)


def _compare(value: float | None, operator: str, threshold: float | None) -> bool:
    if value is None or threshold is None:
        return False
    return {"GT": value > threshold, "GTE": value >= threshold, "LT": value < threshold, "LTE": value <= threshold, "EQ": value == threshold, "NE": value != threshold}.get(operator.upper(), False)


def _http_signal(rule: ObsAlertRule) -> Signal:
    url = rule.query_text
    try:
        response = httpx.get(url, timeout=0.75) if url else None
        value = float(response.status_code) if response else None
        triggered = response is None or response.status_code != 200
        summary = f"HTTP status {int(value) if value is not None else 'unavailable'}; expected 200."
        payload = {"status_code": int(value) if value is not None else None, "url": url}
    except httpx.HTTPError as error:
        value, triggered = None, True
        summary, payload = f"Health endpoint unavailable: {type(error).__name__}.", {"error": type(error).__name__, "url": url}
    return Signal(triggered, value, "HTTP_HEALTH", url, summary, [{"evidence_type": "BFF_HEALTH", "title": rule.name, "summary": summary, "payload_json": payload, "source_url": url}])


def _metric_signal(db: Session, rule: ObsAlertRule) -> Signal:
    cutoff = _now() - timedelta(minutes=rule.evaluation_window_minutes)
    value: float = 0
    evidence_type = "PROMETHEUS_METRIC"
    if rule.metric_name in ("api_error_count", "api_latency_ms"):
        samples = db.scalars(select(ObsMetricSample).where(ObsMetricSample.metric_name == rule.metric_name, ObsMetricSample.recorded_at >= cutoff)).all()
        value = float(sum(float(x.metric_value) for x in samples)) if rule.metric_name == "api_error_count" else float(max((float(x.metric_value) for x in samples), default=0))
    elif rule.metric_name == "batch_failed_runs":
        value = float(db.scalar(select(func.count(BatchRun.id)).where(BatchRun.status.in_(("FAILED", "TIMEOUT")), BatchRun.started_at >= cutoff)) or 0)
        evidence_type = "BATCH_RUN"
    elif rule.metric_name == "ams_open_tickets":
        value = float(db.scalar(select(func.count(AmsTicket.id)).where(AmsTicket.status.in_(ams_ticket_service.ACTIVE_TICKET_STATUSES))) or 0)
        evidence_type = "AMS_BACKLOG"
    triggered = _compare(value, rule.condition_operator, rule.threshold_value)
    summary = f"Observed {value:g}; condition {rule.condition_operator} {rule.threshold_value:g}." if rule.threshold_value is not None else f"Observed {value:g}."
    return Signal(triggered, value, rule.metric_name or "METRIC", None, summary, [{"evidence_type": evidence_type, "title": rule.name, "summary": summary, "payload_json": {"metric_name": rule.metric_name, "observed_value": value, "window_minutes": rule.evaluation_window_minutes}}])


def _signal(db: Session, rule: ObsAlertRule) -> Signal:
    return _http_signal(rule) if rule.signal_type == "AVAILABILITY" else _metric_signal(db, rule)


def _event_response(db: Session, event: ObsAlertEvent) -> AlertEventResponse:
    ticket_number = db.scalar(select(AmsTicket.ticket_number).where(AmsTicket.id == event.created_ticket_id)) if event.created_ticket_id else None
    return AlertEventResponse(id=event.id, event_id=event.event_id, rule_id=event.rule_id, rule_code=event.rule_code, title=event.title, description=event.description, severity=event.severity, status=event.status, deduplication_key=event.deduplication_key, source_signal=event.source_signal, source_url=event.source_url, observed_value=event.observed_value, threshold_value=event.threshold_value, condition_summary=event.condition_summary, first_seen_at=event.first_seen_at, last_seen_at=event.last_seen_at, occurrence_count=event.occurrence_count, suppressed_count=event.suppressed_count, ticket_creation_status=event.ticket_creation_status, created_ticket_id=event.created_ticket_id, linked_ticket_number=ticket_number, evidence=event.evidence, created_at=event.created_at, updated_at=event.updated_at)


def _create_event(db: Session, rule: ObsAlertRule, signal: Signal) -> tuple[ObsAlertEvent | None, bool]:
    source = signal.source_url or signal.source_signal
    dedupe = rule.deduplication_key_template.replace("{source}", source)
    now = _now()
    existing = db.scalar(select(ObsAlertEvent).where(ObsAlertEvent.deduplication_key == dedupe, ObsAlertEvent.status.in_(ACTIVE_EVENT_STATUSES), ObsAlertEvent.last_seen_at >= now - timedelta(minutes=rule.cooldown_minutes)).order_by(ObsAlertEvent.last_seen_at.desc()))
    if existing:
        existing.occurrence_count += 1
        existing.suppressed_count += 1
        existing.last_seen_at = now
        existing.updated_at = now
        return existing, True
    event = ObsAlertEvent(event_id=_next_event_number(db), rule_id=rule.id, rule_code=rule.rule_code, title=rule.name, description=rule.description, severity=rule.severity, status="OPEN", deduplication_key=dedupe, source_signal=signal.source_signal, source_url=signal.source_url, observed_value=signal.observed_value, threshold_value=rule.threshold_value, condition_summary=signal.condition_summary, first_seen_at=now, last_seen_at=now, occurrence_count=1, suppressed_count=0, ticket_creation_status="PENDING" if rule.create_ticket_by_default else "NOT_REQUIRED", created_at=now, updated_at=now)
    db.add(event)
    db.flush()
    for item in signal.evidence:
        db.add(ObsAlertEventEvidence(event_id=event.id, created_at=now, **item))
    return event, False


def _run_response(run: ObsAlertEvaluationRun, event_ids: list[UUID] | None = None) -> AlertEvaluationRunResponse:
    return AlertEvaluationRunResponse(id=run.id, run_id=run.run_id, trigger_source=run.trigger_source, status=run.status, started_at=run.started_at, completed_at=run.completed_at, rules_evaluated=run.rules_evaluated, events_created=run.events_created, events_suppressed=run.events_suppressed, tickets_created=run.tickets_created, error_message=run.error_message, event_ids=event_ids or [])


def evaluate(db: Session, trigger_source: str = "MANUAL", rule_id: UUID | None = None) -> AlertEvaluationRunResponse:
    rules = [db.get(ObsAlertRule, rule_id)] if rule_id else db.scalars(select(ObsAlertRule).where(ObsAlertRule.enabled.is_(True)).order_by(ObsAlertRule.rule_code)).all()
    if rule_id and rules[0] is None:
        raise ObservabilityAlertError("Observability alert rule not found.", 404)
    now = _now()
    run = ObsAlertEvaluationRun(run_id=_next_number(db, "ALERT-EVAL"), trigger_source=trigger_source.upper(), status="RUNNING", started_at=now, rules_evaluated=0, events_created=0, events_suppressed=0, tickets_created=0)
    db.add(run)
    db.flush()
    event_ids: list[UUID] = []
    try:
        for rule in rules:
            if rule is None or not rule.enabled:
                continue
            run.rules_evaluated += 1
            signal = _signal(db, rule)
            if not signal.triggered:
                continue
            event, suppressed = _create_event(db, rule, signal)
            if event is None:
                continue
            event_ids.append(event.id)
            if suppressed:
                run.events_suppressed += 1
            else:
                run.events_created += 1
            if rule.create_ticket_by_default and not suppressed:
                ticket = _create_ticket(db, event)
                run.tickets_created += 1 if ticket else 0
        run.status, run.completed_at = "COMPLETED", _now()
        db.commit()
    except Exception as error:
        db.rollback()
        raise ObservabilityAlertError(f"Alert evaluation failed: {error}", 500) from error
    return _run_response(run, event_ids)


def list_evaluation_runs(db: Session) -> list[AlertEvaluationRunResponse]:
    return [_run_response(item) for item in db.scalars(select(ObsAlertEvaluationRun).order_by(ObsAlertEvaluationRun.started_at.desc())).all()]


def get_evaluation_run(db: Session, run_id: str) -> AlertEvaluationRunResponse:
    run = db.scalar(select(ObsAlertEvaluationRun).where(ObsAlertEvaluationRun.run_id == run_id))
    if run is None:
        raise ObservabilityAlertError("Alert evaluation run not found.", 404)
    return _run_response(run)


def list_events(db: Session, status: str | None = None) -> list[AlertEventResponse]:
    statement = select(ObsAlertEvent).order_by(ObsAlertEvent.last_seen_at.desc())
    if status:
        statement = statement.where(ObsAlertEvent.status == status.upper())
    return [_event_response(db, event) for event in db.scalars(statement).all()]


def get_event(db: Session, event_id: UUID) -> AlertEventResponse:
    event = db.get(ObsAlertEvent, event_id)
    if event is None:
        raise ObservabilityAlertError("Observability alert event not found.", 404)
    return _event_response(db, event)


def transition_event(db: Session, event_id: UUID, target: str) -> AlertEventResponse:
    event = db.get(ObsAlertEvent, event_id)
    if event is None:
        raise ObservabilityAlertError("Observability alert event not found.", 404)
    allowed = {"ACKNOWLEDGED": ("OPEN",), "RESOLVED": ("OPEN", "ACKNOWLEDGED", "TICKETED")}
    if event.status not in allowed[target]:
        raise ObservabilityAlertError(f"Alert event cannot transition from {event.status} to {target}.", 409)
    event.status, event.updated_at = target, _now()
    db.commit()
    return _event_response(db, event)


def _create_ticket(db: Session, event: ObsAlertEvent) -> TicketResponse | None:
    if event.created_ticket_id:
        return ams_ticket_service.get_ticket(db, event.created_ticket_id)
    now = _now()
    priority = {"CRITICAL": "P1", "HIGH": "P2", "MEDIUM": "P3", "LOW": "P4"}.get(event.severity, "P3")
    evidence = "; ".join(item.summary for item in event.evidence)
    ticket = AmsTicket(ticket_number=ams_ticket_service._next_number(db, "INCIDENT"), ticket_type="INCIDENT", severity=event.severity, priority=priority, status="NEW", source="OBSERVABILITY_ALERT", source_module="OBSERVABILITY_ALERTING", affected_entity_type="OBSERVABILITY_ALERT_EVENT", affected_entity_id=event.id, short_description=f"[Observability Alert] {event.title}"[:200], description=(f"Rule: {event.rule_code}\nSeverity: {event.severity}\nCondition: {event.condition_summary}\nObserved: {event.observed_value}\nThreshold: {event.threshold_value}\nFirst seen: {event.first_seen_at}\nLast seen: {event.last_seen_at}\nEvidence: {evidence}\nSource: {event.source_url or 'internal runtime telemetry'}")[:2000], assignment_group="AMS-WAREHOUSE-SUPPORT", business_service="Warehouse & Fulfillment Operations", application_name="Enterprise Operations Suite", environment=get_settings().app_env, opened_at=now, created_at=now, updated_at=now)
    db.add(ticket)
    db.flush()
    ams_ticket_service._event(db, ticket, "TICKET_CREATED", f"Ticket created from observability alert {event.event_id}.", to_status="NEW", payload={"observability_alert_event_id": str(event.id), "rule_code": event.rule_code})
    event.created_ticket_id, event.ticket_creation_status, event.status, event.updated_at = ticket.id, "CREATED", "TICKETED", now
    db.add(ObsAlertTicketLink(event_id=event.id, ams_ticket_id=ticket.id, link_type="AUTO_CREATED", created_by="system"))
    db.commit()
    return ams_ticket_service.get_ticket(db, ticket.id)


def create_ticket(db: Session, event_id: UUID) -> TicketResponse:
    event = db.get(ObsAlertEvent, event_id)
    if event is None:
        raise ObservabilityAlertError("Observability alert event not found.", 404)
    if event.status == "RESOLVED":
        raise ObservabilityAlertError("Resolved alert events cannot create tickets.", 409)
    ticket = _create_ticket(db, event)
    assert ticket is not None
    return ticket


def get_summary(db: Session) -> ObservabilityAlertSummary:
    count = lambda condition: int(db.scalar(select(func.count(ObsAlertEvent.id)).where(condition)) or 0)
    return ObservabilityAlertSummary(rules=int(db.scalar(select(func.count(ObsAlertRule.id))) or 0), enabled_rules=int(db.scalar(select(func.count(ObsAlertRule.id)).where(ObsAlertRule.enabled.is_(True))) or 0), open_events=count(ObsAlertEvent.status == "OPEN"), ticketed_events=count(ObsAlertEvent.status == "TICKETED"), acknowledged_events=count(ObsAlertEvent.status == "ACKNOWLEDGED"), resolved_events=count(ObsAlertEvent.status == "RESOLVED"), evaluation_runs=int(db.scalar(select(func.count(ObsAlertEvaluationRun.id))) or 0), tickets_created=int(db.scalar(select(func.count(ObsAlertEvent.id)).where(ObsAlertEvent.ticket_creation_status == "CREATED")) or 0))
