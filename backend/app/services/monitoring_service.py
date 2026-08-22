"""Deterministic monitoring alert generation and manual triage services."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.ams import AmsTicket
from app.models.monitoring import MonAlert, MonAlertEvent, MonAlertRule, MonComponent, MonTriageCase, MonTriageCaseAlert
from app.schemas.monitoring import (
    AlertEventResponse, AlertResponse, AlertRuleResponse, MonitoringComponentResponse, MonitoringSummary,
    SimulationResult, TriageAlertSummary, TriageCaseCreate, TriageCaseResponse,
)

DEDUPE_STATUSES = ("OPEN", "ACKNOWLEDGED")
OPEN_STATUSES = ("OPEN", "ACKNOWLEDGED", "LINKED_TO_TICKET")
SEVERITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
VALID_SEVERITIES = tuple(SEVERITY_RANK)
VALID_CASE_STATUSES = ("OPEN", "INVESTIGATING", "LINKED_TO_TICKET")


class MonitoringError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_number(db: Session, model: type, field: object, prefix: str) -> str:
    current = db.scalar(select(func.max(field)).where(field.like(f"{prefix}%")))  # type: ignore[union-attr]
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            sequence = 1
    return f"{prefix}{sequence:04d}"


def _alert_event(db: Session, alert: MonAlert, event_type: str, message: str, from_status: str | None = None, to_status: str | None = None, payload: dict | None = None) -> None:
    db.add(MonAlertEvent(alert_id=alert.id, event_type=event_type, from_status=from_status, to_status=to_status, message=message, event_payload=payload, created_by="system", created_at=_now()))


def _alert_response(db: Session, alert: MonAlert) -> AlertResponse:
    rule = db.get(MonAlertRule, alert.rule_id)
    component = db.get(MonComponent, alert.component_id)
    ticket = db.get(AmsTicket, alert.linked_ticket_id) if alert.linked_ticket_id else None
    return AlertResponse(
        id=alert.id, alert_number=alert.alert_number, rule_id=alert.rule_id, rule_code=rule.rule_code if rule else "UNKNOWN",
        component_id=alert.component_id, component_code=component.component_code if component else "UNKNOWN", component_name=component.name if component else "Unknown",
        severity=alert.severity, status=alert.status, signal_type=alert.signal_type, metric_name=alert.metric_name,
        observed_value=alert.observed_value, threshold_value=alert.threshold_value, dedupe_key=alert.dedupe_key, title=alert.title, description=alert.description,
        first_seen_at=alert.first_seen_at, last_seen_at=alert.last_seen_at, occurrence_count=alert.occurrence_count,
        acknowledged_at=alert.acknowledged_at, suppressed_at=alert.suppressed_at, resolved_at=alert.resolved_at,
        linked_exception_id=alert.linked_exception_id, linked_ticket_id=alert.linked_ticket_id, linked_ticket_number=ticket.ticket_number if ticket else None,
        created_at=alert.created_at, updated_at=alert.updated_at,
    )


def list_components(db: Session) -> list[MonitoringComponentResponse]:
    return [MonitoringComponentResponse.model_validate(row, from_attributes=True) for row in db.scalars(select(MonComponent).order_by(MonComponent.component_code)).all()]


def list_rules(db: Session) -> list[AlertRuleResponse]:
    rows = db.scalars(select(MonAlertRule).order_by(MonAlertRule.rule_code)).all()
    return [AlertRuleResponse.model_validate({**row.__dict__, "component_code": row.component.component_code}) for row in rows]


def create_alert(db: Session, rule_code: str, observed_value: float, title: str, description: str, signal_type: str = "METRIC_THRESHOLD", dedupe_key: str | None = None) -> tuple[MonAlert, bool, bool]:
    rule = db.scalar(select(MonAlertRule).where(MonAlertRule.rule_code == rule_code))
    if rule is None:
        raise MonitoringError(f"Monitoring rule {rule_code} not found.", 404)
    if not rule.enabled:
        raise MonitoringError(f"Monitoring rule {rule_code} is disabled.", 409)
    key = dedupe_key or rule.rule_code
    existing = db.scalar(select(MonAlert).where(MonAlert.dedupe_key == key, MonAlert.status.in_(DEDUPE_STATUSES)).order_by(MonAlert.created_at.desc()))
    now = _now()
    if existing:
        old_status = existing.status
        existing.occurrence_count += 1
        existing.last_seen_at = now
        existing.updated_at = now
        existing.observed_value = observed_value
        _alert_event(db, existing, "ALERT_REPEATED", "Monitoring signal repeated for the same dedupe key.", from_status=old_status, to_status=old_status, payload={"occurrence_count": existing.occurrence_count})
        return existing, False, True
    alert = MonAlert(
        alert_number=_next_number(db, MonAlert, MonAlert.alert_number, f"ALT-{now:%Y%m%d}-"), rule_id=rule.id, component_id=rule.component_id,
        severity=rule.severity, status="OPEN", signal_type=signal_type, metric_name=rule.metric_name, observed_value=observed_value,
        threshold_value=rule.threshold_value, dedupe_key=key, title=title[:200], description=description[:1000],
        first_seen_at=now, last_seen_at=now, occurrence_count=1, created_at=now, updated_at=now,
    )
    db.add(alert)
    db.flush()
    _alert_event(db, alert, "ALERT_CREATED", "Monitoring alert created.", to_status="OPEN")
    return alert, True, False


def list_alerts(db: Session, status: str | None = None, severity: str | None = None, component_id: UUID | None = None, component_code: str | None = None, signal_type: str | None = None, metric_name: str | None = None) -> list[AlertResponse]:
    active_first = case((MonAlert.status.in_(OPEN_STATUSES), 0), else_=1)
    severity_first = case((MonAlert.severity == "CRITICAL", 0), (MonAlert.severity == "HIGH", 1), (MonAlert.severity == "MEDIUM", 2), else_=3)
    statement = select(MonAlert).join(MonComponent, MonComponent.id == MonAlert.component_id).order_by(active_first, severity_first, MonAlert.last_seen_at.desc())
    if status:
        statement = statement.where(MonAlert.status == status.upper())
    if severity:
        statement = statement.where(MonAlert.severity == severity.upper())
    if component_id:
        statement = statement.where(MonAlert.component_id == component_id)
    if component_code:
        statement = statement.where(MonComponent.component_code == component_code)
    if signal_type:
        statement = statement.where(MonAlert.signal_type == signal_type.upper())
    if metric_name:
        statement = statement.where(MonAlert.metric_name == metric_name)
    return [_alert_response(db, row) for row in db.scalars(statement).all()]


def get_alert(db: Session, alert_id: UUID) -> AlertResponse:
    alert = db.get(MonAlert, alert_id)
    if alert is None:
        raise MonitoringError("Monitoring alert not found.", 404)
    return _alert_response(db, alert)


def _transition_alert(db: Session, alert_id: UUID, new_status: str, allowed: tuple[str, ...], event_type: str, message: str) -> AlertResponse:
    alert = db.get(MonAlert, alert_id)
    if alert is None:
        raise MonitoringError("Monitoring alert not found.", 404)
    if alert.status not in allowed:
        raise MonitoringError(f"Alert cannot transition from {alert.status} to {new_status}.")
    old_status, now = alert.status, _now()
    alert.status, alert.updated_at = new_status, now
    if new_status == "ACKNOWLEDGED":
        alert.acknowledged_at = now
    elif new_status == "SUPPRESSED":
        alert.suppressed_at = now
    elif new_status == "RESOLVED":
        alert.resolved_at = now
    _alert_event(db, alert, event_type, message, from_status=old_status, to_status=new_status)
    db.commit()
    return get_alert(db, alert.id)


def acknowledge_alert(db: Session, alert_id: UUID) -> AlertResponse:
    return _transition_alert(db, alert_id, "ACKNOWLEDGED", ("OPEN",), "ALERT_ACKNOWLEDGED", "Monitoring alert acknowledged.")


def suppress_alert(db: Session, alert_id: UUID) -> AlertResponse:
    return _transition_alert(db, alert_id, "SUPPRESSED", ("OPEN", "ACKNOWLEDGED"), "ALERT_SUPPRESSED", "Monitoring alert suppressed.")


def resolve_alert(db: Session, alert_id: UUID) -> AlertResponse:
    return _transition_alert(db, alert_id, "RESOLVED", ("OPEN", "ACKNOWLEDGED", "SUPPRESSED", "LINKED_TO_TICKET"), "ALERT_RESOLVED", "Monitoring alert resolved.")


def list_alert_events(db: Session, alert_id: UUID) -> list[AlertEventResponse]:
    if db.get(MonAlert, alert_id) is None:
        raise MonitoringError("Monitoring alert not found.", 404)
    rows = db.scalars(select(MonAlertEvent).where(MonAlertEvent.alert_id == alert_id).order_by(MonAlertEvent.created_at, MonAlertEvent.id)).all()
    return [AlertEventResponse.model_validate(row, from_attributes=True) for row in rows]


SIMULATIONS = {
    "api-latency-cascade": ("Generated API, frontend, and workflow latency symptoms without observability context.", [
        ("MON-API-LATENCY", 850, "API latency is above threshold", "Backend API response latency is high."),
        ("MON-API-ERROR", 8, "API error rate is elevated", "Backend API errors are elevated alongside latency."),
        ("MON-FRONTEND-API", 14, "Frontend API failures are elevated", "Frontend requests are failing while API symptoms are present."),
        ("MON-WORKFLOW-FAILURE", 6, "Order workflow failures are elevated", "Warehouse order workflow failures are being observed."),
    ]),
    "database-degradation": ("Generated database and downstream application symptoms; root cause remains unconfirmed.", [
        ("MON-DB-LATENCY", 620, "Database response time is high", "PostgreSQL response time is above threshold."),
        ("MON-API-LATENCY", 740, "API latency is above threshold", "Backend API latency may be affected by data-layer symptoms."),
        ("MON-INV-ALLOC", 9, "Allocation failures are elevated", "Inventory allocation failures are being observed."),
        ("MON-WORKFLOW-FAILURE", 5, "Order workflow failures are elevated", "Warehouse workflow failures are being observed."),
    ]),
    "redis-flapping": ("Generated intermittent cache connection symptoms without infrastructure diagnosis.", [
        ("MON-REDIS-FLAP", 11, "Redis connection failures are elevated", "Redis connections are intermittently failing."),
        ("MON-API-ERROR", 5, "API error rate is elevated", "API errors coincide with cache connection symptoms."),
        ("MON-WORKFLOW-LOW", 2, "Workflow failures detected", "A small number of workflow failures are being observed."),
    ]),
    "frontend-error-burst": ("Generated user-facing frontend failure symptoms without deeper request context.", [
        ("MON-FRONTEND-API", 22, "Frontend API failures are elevated", "Frontend API failures are occurring in a burst."),
        ("MON-API-ERROR", 7, "API error rate is elevated", "Backend API errors accompany the frontend failure burst."),
    ]),
    "warehouse-workflow-noise": ("Generated business-process alert noise across warehouse workflow components.", [
        ("MON-WORKFLOW-HIGH", 12, "Order workflow failures are elevated", "Warehouse order workflow failures are being observed."),
        ("MON-INV-ALLOC", 8, "Allocation failures are elevated", "Inventory allocation failures are being observed."),
        ("MON-SHIPMENT-EXC", 4, "Shipment exceptions are elevated", "Shipment exceptions are being observed."),
    ]),
}


def run_simulation(db: Session, simulation_code: str) -> SimulationResult:
    if simulation_code == "noisy-alert-storm":
        codes = ["api-latency-cascade", "database-degradation", "redis-flapping", "frontend-error-burst", "warehouse-workflow-noise"]
        summary = "Generated a deterministic multi-component alert storm. Alerts are symptoms only; no root cause was inferred."
    elif simulation_code in SIMULATIONS:
        codes, summary = [simulation_code], SIMULATIONS[simulation_code][0]
    else:
        raise MonitoringError("Unknown monitoring simulation.", 404)
    created = repeated = 0
    generated: list[MonAlert] = []
    for code in codes:
        for rule_code, value, title, description in SIMULATIONS[code][1]:
            alert, was_created, was_repeated = create_alert(db, rule_code, value, title, description, signal_type="METRIC_THRESHOLD", dedupe_key=f"{rule_code}:demo")
            generated.append(alert)
            created += int(was_created)
            repeated += int(was_repeated)
    db.commit()
    alerts_open = db.scalar(select(func.count(MonAlert.id)).where(MonAlert.status.in_(OPEN_STATUSES))) or 0
    highest = min((a.severity for a in generated), key=lambda value: SEVERITY_RANK[value], default=None)
    return SimulationResult(simulation_code=simulation_code, alerts_created=created, alerts_repeated=repeated, alerts_open=alerts_open, highest_severity=highest, simulation_summary=summary, alerts=[_alert_response(db, alert) for alert in generated])


def _next_case_number(db: Session) -> str:
    now = _now()
    return _next_number(db, MonTriageCase, MonTriageCase.case_number, f"TRIAGE-{now:%Y%m%d}-")


def _case_response(db: Session, row: MonTriageCase) -> TriageCaseResponse:
    links = db.scalars(select(MonTriageCaseAlert).where(MonTriageCaseAlert.triage_case_id == row.id).order_by(MonTriageCaseAlert.created_at)).all()
    alerts = []
    for link in links:
        alert = db.get(MonAlert, link.alert_id)
        component = db.get(MonComponent, alert.component_id) if alert else None
        if alert:
            alerts.append(TriageAlertSummary(id=alert.id, alert_number=alert.alert_number, component_code=component.component_code if component else "UNKNOWN", severity=alert.severity, status=alert.status, metric_name=alert.metric_name, title=alert.title))
    ticket = db.get(AmsTicket, row.linked_ticket_id) if row.linked_ticket_id else None
    return TriageCaseResponse(
        id=row.id, case_number=row.case_number, title=row.title, description=row.description, status=row.status, severity=row.severity,
        suspected_impact=row.suspected_impact, suspected_root_cause=row.suspected_root_cause, confidence_level=row.confidence_level, analysis_notes=row.analysis_notes,
        linked_ticket_id=row.linked_ticket_id, linked_ticket_number=ticket.ticket_number if ticket else None, created_by=row.created_by,
        created_at=row.created_at, updated_at=row.updated_at, acknowledged_at=row.acknowledged_at, resolved_at=row.resolved_at, closed_at=row.closed_at,
        alert_count=len(alerts), alerts=alerts,
    )


def list_triage_cases(db: Session) -> list[TriageCaseResponse]:
    return [_case_response(db, row) for row in db.scalars(select(MonTriageCase).order_by(MonTriageCase.created_at.desc())).all()]


def get_triage_case(db: Session, case_id: UUID) -> TriageCaseResponse:
    row = db.get(MonTriageCase, case_id)
    if row is None:
        raise MonitoringError("Triage case not found.", 404)
    return _case_response(db, row)


def add_alerts_to_case(db: Session, case_id: UUID, alert_ids: list[UUID]) -> TriageCaseResponse:
    row = db.get(MonTriageCase, case_id)
    if row is None:
        raise MonitoringError("Triage case not found.", 404)
    for alert_id in alert_ids:
        if db.get(MonAlert, alert_id) is None:
            raise MonitoringError("One or more monitoring alerts were not found.", 404)
        exists = db.scalar(select(MonTriageCaseAlert.id).where(MonTriageCaseAlert.triage_case_id == case_id, MonTriageCaseAlert.alert_id == alert_id))
        if exists is None:
            db.add(MonTriageCaseAlert(triage_case_id=case_id, alert_id=alert_id, created_at=_now()))
    db.commit()
    return get_triage_case(db, case_id)


def create_triage_case(db: Session, request: TriageCaseCreate) -> TriageCaseResponse:
    severity, confidence = request.severity.upper(), request.confidence_level.upper()
    if severity not in VALID_SEVERITIES:
        raise MonitoringError("Unsupported triage case severity.", 400)
    if confidence not in ("LOW", "MEDIUM", "HIGH", "UNKNOWN"):
        raise MonitoringError("Unsupported triage confidence level.", 400)
    now = _now()
    row = MonTriageCase(case_number=_next_case_number(db), title=request.title.strip(), description=request.description.strip(), status="OPEN", severity=severity, suspected_impact=request.suspected_impact.strip(), suspected_root_cause=request.suspected_root_cause.strip() if request.suspected_root_cause else "Unknown - no observability traces available", confidence_level=confidence, analysis_notes=request.analysis_notes, created_by="support-engineer", created_at=now, updated_at=now)
    db.add(row)
    db.flush()
    if request.alert_ids:
        for alert_id in request.alert_ids:
            if db.get(MonAlert, alert_id) is None:
                raise MonitoringError("One or more monitoring alerts were not found.", 404)
            db.add(MonTriageCaseAlert(triage_case_id=row.id, alert_id=alert_id, created_at=now))
    db.commit()
    return get_triage_case(db, row.id)


def start_investigation(db: Session, case_id: UUID) -> TriageCaseResponse:
    row = db.get(MonTriageCase, case_id)
    if row is None:
        raise MonitoringError("Triage case not found.", 404)
    if row.status != "OPEN":
        raise MonitoringError(f"Triage case cannot transition from {row.status} to INVESTIGATING.")
    row.status, row.acknowledged_at, row.updated_at = "INVESTIGATING", _now(), _now()
    db.commit()
    return get_triage_case(db, row.id)


def resolve_triage_case(db: Session, case_id: UUID, analysis_notes: str) -> TriageCaseResponse:
    row = db.get(MonTriageCase, case_id)
    if row is None:
        raise MonitoringError("Triage case not found.", 404)
    if row.status not in VALID_CASE_STATUSES:
        raise MonitoringError(f"Triage case cannot transition from {row.status} to RESOLVED.")
    row.status, row.analysis_notes, row.resolved_at, row.updated_at = "RESOLVED", analysis_notes.strip(), _now(), _now()
    db.commit()
    return get_triage_case(db, row.id)


def get_monitoring_summary(db: Session) -> MonitoringSummary:
    open_alerts = db.scalar(select(func.count(MonAlert.id)).where(MonAlert.status.in_(OPEN_STATUSES))) or 0
    critical = db.scalar(select(func.count(MonAlert.id)).where(MonAlert.status.in_(OPEN_STATUSES), MonAlert.severity == "CRITICAL")) or 0
    high = db.scalar(select(func.count(MonAlert.id)).where(MonAlert.status.in_(OPEN_STATUSES), MonAlert.severity == "HIGH")) or 0
    acknowledged = db.scalar(select(func.count(MonAlert.id)).where(MonAlert.status == "ACKNOWLEDGED")) or 0
    suppressed = db.scalar(select(func.count(MonAlert.id)).where(MonAlert.status == "SUPPRESSED")) or 0
    cases = db.scalar(select(func.count(MonTriageCase.id)).where(MonTriageCase.status.in_(("OPEN", "INVESTIGATING", "LINKED_TO_TICKET")))) or 0
    linked = db.scalar(select(func.count(MonAlert.id)).where(MonAlert.linked_ticket_id.is_not(None))) or 0
    noisiest = db.execute(select(MonComponent.component_code).join(MonAlert, MonAlert.component_id == MonComponent.id).group_by(MonComponent.component_code).order_by(func.sum(MonAlert.occurrence_count).desc()).limit(1)).scalar_one_or_none()
    return MonitoringSummary(open_alerts=open_alerts, critical_alerts=critical, high_alerts=high, acknowledged_alerts=acknowledged, suppressed_alerts=suppressed, open_triage_cases=cases, alerts_linked_to_tickets=linked, noisiest_component=noisiest)
