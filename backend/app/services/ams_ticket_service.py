"""Deterministic AMS ticket creation and lifecycle services."""

from __future__ import annotations

from datetime import datetime, time, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ams import AmsTicket, AmsTicketEvent
from app.models.batch import BatchRun
from app.models.monitoring import MonAlert, MonAlertEvent, MonTriageCase, MonTriageCaseAlert
from app.models.observability import ObsDiagnosticCase, ObsTrace
from app.models.operations import OpsException
from app.models.user_reports import AmsUserReport
from app.schemas.ams import AmsSummary, TicketEventResponse, TicketResponse
from app.services.operations_exception_service import exception_to_response

ACTIVE_TICKET_STATUSES = ("NEW", "ACKNOWLEDGED", "IN_PROGRESS")
VALID_TICKET_TYPES = ("INCIDENT", "SERVICE_REQUEST", "PROBLEM")
VALID_SEVERITIES = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
VALID_PRIORITIES = ("P1", "P2", "P3", "P4")


class AmsError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_number(db: Session, ticket_type: str) -> str:
    code = {"INCIDENT": "INC", "SERVICE_REQUEST": "SR", "PROBLEM": "PROB"}[ticket_type]
    prefix = f"AMS-{code}-{_now():%Y%m%d}-"
    current = db.scalar(select(func.max(AmsTicket.ticket_number)).where(AmsTicket.ticket_number.like(f"{prefix}%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            sequence = 1
    return f"{prefix}{sequence:04d}"


def _validate_ticket_fields(ticket_type: str, severity: str, priority: str) -> tuple[str, str, str]:
    ticket_type, severity, priority = ticket_type.upper(), severity.upper(), priority.upper()
    if ticket_type not in VALID_TICKET_TYPES:
        raise AmsError("Unsupported ticket type.", 400)
    if severity not in VALID_SEVERITIES:
        raise AmsError("Unsupported ticket severity.", 400)
    if priority not in VALID_PRIORITIES:
        raise AmsError("Unsupported ticket priority.", 400)
    return ticket_type, severity, priority


def _event(db: Session, ticket: AmsTicket, event_type: str, message: str, from_status: str | None = None, to_status: str | None = None, payload: dict | None = None) -> None:
    db.add(AmsTicketEvent(ticket_id=ticket.id, event_type=event_type, from_status=from_status, to_status=to_status, message=message, event_payload=payload, created_by="system", created_at=_now()))


def _ticket_response(db: Session, ticket: AmsTicket, include_details: bool = False) -> TicketResponse:
    exception = db.get(OpsException, ticket.exception_id) if include_details and ticket.exception_id else None
    events = db.scalars(select(AmsTicketEvent).where(AmsTicketEvent.ticket_id == ticket.id).order_by(AmsTicketEvent.created_at, AmsTicketEvent.id)).all() if include_details else []
    return TicketResponse(
        id=ticket.id, ticket_number=ticket.ticket_number, ticket_type=ticket.ticket_type, severity=ticket.severity,
        priority=ticket.priority, status=ticket.status, source=ticket.source, source_module=ticket.source_module,
        exception_id=ticket.exception_id, user_report_id=ticket.user_report_id, affected_entity_type=ticket.affected_entity_type, affected_entity_id=ticket.affected_entity_id,
        short_description=ticket.short_description, description=ticket.description, assignment_group=ticket.assignment_group,
        assigned_to=ticket.assigned_to, business_service=ticket.business_service, application_name=ticket.application_name,
        environment=ticket.environment, opened_at=ticket.opened_at, acknowledged_at=ticket.acknowledged_at,
        resolved_at=ticket.resolved_at, closed_at=ticket.closed_at, resolution_code=ticket.resolution_code,
        resolution_notes=ticket.resolution_notes, created_at=ticket.created_at, updated_at=ticket.updated_at,
        exception=exception_to_response(db, exception) if exception else None,
        events=[TicketEventResponse.model_validate(event, from_attributes=True) for event in events],
    )


def get_ticket(db: Session, ticket_id: UUID, include_details: bool = True) -> TicketResponse:
    ticket = db.get(AmsTicket, ticket_id)
    if ticket is None:
        raise AmsError("AMS ticket not found.", 404)
    return _ticket_response(db, ticket, include_details)


def list_tickets(db: Session, status: str | None = None, severity: str | None = None, priority: str | None = None) -> list[TicketResponse]:
    open_first = case((AmsTicket.status.in_(ACTIVE_TICKET_STATUSES), 0), else_=1)
    statement = select(AmsTicket).order_by(open_first, AmsTicket.opened_at.desc(), AmsTicket.ticket_number.desc())
    if status:
        statement = statement.where(AmsTicket.status == status.upper())
    if severity:
        statement = statement.where(AmsTicket.severity == severity.upper())
    if priority:
        statement = statement.where(AmsTicket.priority == priority.upper())
    return [_ticket_response(db, ticket) for ticket in db.scalars(statement).all()]


def create_manual_ticket(db: Session, request: Any) -> TicketResponse:
    ticket_type, severity, priority = _validate_ticket_fields(request.ticket_type, request.severity, request.priority)
    now = _now()
    ticket_number = request.ticket_number.strip() if request.ticket_number else _next_number(db, ticket_type)
    if db.scalar(select(AmsTicket.id).where(AmsTicket.ticket_number == ticket_number)) is not None:
        raise AmsError("Ticket number already exists.", 409)
    ticket = AmsTicket(
        ticket_number=ticket_number, ticket_type=ticket_type, severity=severity, priority=priority,
        status="NEW", source="MANUAL", source_module="WAREHOUSE_FULFILLMENT", affected_entity_type=request.affected_entity_type,
        affected_entity_id=request.affected_entity_id, short_description=request.short_description.strip(), description=request.description.strip(),
        assignment_group=request.assignment_group.strip(), business_service="Warehouse & Fulfillment Operations",
        application_name="Enterprise Operations Suite", environment=get_settings().app_env, opened_at=now, created_at=now, updated_at=now,
    )
    db.add(ticket)
    db.flush()
    _event(db, ticket, "TICKET_CREATED", "AMS ticket created.", to_status="NEW")
    db.commit()
    return get_ticket(db, ticket.id)


def create_ticket_from_exception(db: Session, exception_id: UUID) -> TicketResponse:
    exception = db.get(OpsException, exception_id)
    if exception is None:
        raise AmsError("Operational exception not found.", 404)
    existing = db.scalar(
        select(AmsTicket).where(AmsTicket.exception_id == exception.id, AmsTicket.status.not_in(("CLOSED", "CANCELLED"))).order_by(AmsTicket.created_at.desc())
    )
    if existing is not None:
        return get_ticket(db, existing.id)
    priority = {"CRITICAL": "P1", "HIGH": "P2", "MEDIUM": "P3", "LOW": "P4"}.get(exception.severity, "P3")
    now = _now()
    ticket = AmsTicket(
        ticket_number=_next_number(db, "INCIDENT"), ticket_type="INCIDENT", severity=exception.severity, priority=priority,
        status="NEW", source="EXCEPTION", source_module=exception.source_module, exception_id=exception.id,
        affected_entity_type=exception.source_entity_type, affected_entity_id=exception.source_entity_id,
        short_description=exception.title, description=exception.description, assignment_group="AMS-WAREHOUSE-SUPPORT",
        business_service="Warehouse & Fulfillment Operations", application_name="Enterprise Operations Suite",
        environment=get_settings().app_env, opened_at=now, created_at=now, updated_at=now,
    )
    db.add(ticket)
    exception.status = "LINKED_TO_TICKET"
    exception.updated_at = now
    db.flush()
    _event(db, ticket, "TICKET_CREATED", f"Ticket created from exception {exception.exception_number}.", to_status="NEW", payload={"exception_id": str(exception.id)})
    db.commit()
    return get_ticket(db, ticket.id)


def create_ticket_from_user_report(db: Session, report_id: UUID) -> TicketResponse:
    report = db.get(AmsUserReport, report_id)
    if report is None:
        raise AmsError("User report not found.", 404)
    if report.ticket_id:
        existing = db.get(AmsTicket, report.ticket_id)
        if existing is not None and existing.status in ACTIVE_TICKET_STATUSES:
            return get_ticket(db, existing.id)
    if report.status == "CANCELLED":
        raise AmsError("Cancelled user reports cannot create tickets.", 409)
    severity = report.severity.upper()
    if severity not in VALID_SEVERITIES:
        raise AmsError("Unsupported user report severity.", 400)
    priority = {"CRITICAL": "P1", "HIGH": "P2", "MEDIUM": "P3", "LOW": "P4"}[severity]
    source = "SYNTHETIC_USER" if report.report_channel.upper() == "SYNTHETIC_USER" else "USER_REPORTED"
    now = _now()
    ticket = AmsTicket(
        ticket_number=_next_number(db, "INCIDENT"), ticket_type="INCIDENT", severity=severity, priority=priority,
        status="NEW", source=source, source_module=report.source_module, user_report_id=report.id,
        affected_entity_type=report.affected_entity_type, affected_entity_id=report.affected_entity_id,
        short_description=report.title, description=(f"Reported by {report.reporter_name}. {report.description}\n\nBusiness impact: {report.business_impact}")[:2000],
        assignment_group="AMS-WAREHOUSE-SUPPORT", business_service="Warehouse & Fulfillment Operations",
        application_name="Enterprise Operations Suite", environment=get_settings().app_env,
        opened_at=now, created_at=now, updated_at=now,
    )
    db.add(ticket)
    db.flush()
    report.ticket_id = ticket.id
    report.status = "TICKET_CREATED"
    report.updated_at = now
    _event(db, ticket, "TICKET_CREATED", f"Ticket created from user report {report.report_number}.", to_status="NEW", payload={"user_report_id": str(report.id)})
    db.commit()
    return get_ticket(db, ticket.id)


def create_ticket_from_alert(db: Session, alert_id: UUID) -> TicketResponse:
    alert = db.get(MonAlert, alert_id)
    if alert is None:
        raise AmsError("Monitoring alert not found.", 404)
    if alert.linked_ticket_id:
        existing = db.get(AmsTicket, alert.linked_ticket_id)
        if existing is not None and existing.status not in ("CLOSED", "CANCELLED"):
            return get_ticket(db, existing.id)
    component = alert.component
    priority = {"CRITICAL": "P1", "HIGH": "P2", "MEDIUM": "P3", "LOW": "P4"}.get(alert.severity, "P3")
    now = _now()
    description = (
        f"Monitoring alert {alert.alert_number} was generated by component {component.component_code if component else 'UNKNOWN'}. "
        f"Metric: {alert.metric_name}; observed value: {alert.observed_value}; threshold: {alert.threshold_value}; severity: {alert.severity}.\n\n"
        "No observability traces, logs, or automated root-cause context are available for this symptom. Manual triage is required."
    )[:2000]
    ticket = AmsTicket(
        ticket_number=_next_number(db, "INCIDENT"), ticket_type="INCIDENT", severity=alert.severity, priority=priority,
        status="NEW", source="MONITORING", source_module="MONITORING", affected_entity_type="COMPONENT", affected_entity_id=alert.component_id,
        short_description=f"{alert.alert_number}: {alert.title}"[:200], description=description, assignment_group="AMS-WAREHOUSE-SUPPORT",
        business_service="Warehouse & Fulfillment Operations", application_name="Enterprise Operations Suite", environment=get_settings().app_env,
        opened_at=now, created_at=now, updated_at=now,
    )
    db.add(ticket)
    db.flush()
    alert.linked_ticket_id, alert.status, alert.updated_at = ticket.id, "LINKED_TO_TICKET", now
    _event(db, ticket, "TICKET_CREATED", f"Ticket created from monitoring alert {alert.alert_number}.", to_status="NEW", payload={"alert_id": str(alert.id)})
    db.add(MonAlertEvent(alert_id=alert.id, event_type="ALERT_LINKED_TO_TICKET", from_status="OPEN", to_status="LINKED_TO_TICKET", message="Monitoring alert linked to an AMS ticket.", event_payload={"ticket_id": str(ticket.id)}, created_by="system", created_at=now))
    db.commit()
    return get_ticket(db, ticket.id)


def create_ticket_from_triage_case(db: Session, case_id: UUID) -> TicketResponse:
    triage = db.get(MonTriageCase, case_id)
    if triage is None:
        raise AmsError("Triage case not found.", 404)
    if triage.linked_ticket_id:
        existing = db.get(AmsTicket, triage.linked_ticket_id)
        if existing is not None and existing.status not in ("CLOSED", "CANCELLED"):
            return get_ticket(db, existing.id)
    links = db.scalars(select(MonTriageCaseAlert).where(MonTriageCaseAlert.triage_case_id == triage.id)).all()
    alert_lines = []
    for link in links:
        alert = db.get(MonAlert, link.alert_id)
        if alert:
            component = alert.component
            alert_lines.append(f"{alert.alert_number} ({component.component_code if component else 'UNKNOWN'}): {alert.title}")
    priority = {"CRITICAL": "P1", "HIGH": "P2", "MEDIUM": "P3", "LOW": "P4"}.get(triage.severity, "P3")
    now = _now()
    description = (
        f"Manual monitoring triage case {triage.case_number}.\n{triage.description}\n\n"
        f"Suspected impact: {triage.suspected_impact}\nSuspected root cause: {triage.suspected_root_cause or 'Unknown'}\n"
        "The case contains symptoms only; no automated root-cause diagnosis is available.\n\nIncluded alerts:\n" + "\n".join(alert_lines)
    )[:2000]
    ticket = AmsTicket(
        ticket_number=_next_number(db, "INCIDENT"), ticket_type="INCIDENT", severity=triage.severity, priority=priority, status="NEW",
        source="MONITORING", source_module="MONITORING", affected_entity_type="TRIAGE_CASE", affected_entity_id=triage.id,
        short_description=f"{triage.case_number}: {triage.title}"[:200], description=description,
        assignment_group="AMS-WAREHOUSE-SUPPORT", business_service="Warehouse & Fulfillment Operations", application_name="Enterprise Operations Suite",
        environment=get_settings().app_env, opened_at=now, created_at=now, updated_at=now,
    )
    db.add(ticket)
    db.flush()
    triage.linked_ticket_id, triage.status, triage.updated_at = ticket.id, "LINKED_TO_TICKET", now
    _event(db, ticket, "TICKET_CREATED", f"Ticket created from triage case {triage.case_number}.", to_status="NEW", payload={"triage_case_id": str(triage.id)})
    for link in links:
        alert = db.get(MonAlert, link.alert_id)
        if alert and not alert.linked_ticket_id:
            old_status = alert.status
            alert.linked_ticket_id, alert.status, alert.updated_at = ticket.id, "LINKED_TO_TICKET", now
            db.add(MonAlertEvent(alert_id=alert.id, event_type="ALERT_LINKED_TO_TICKET", from_status=old_status, to_status="LINKED_TO_TICKET", message="Alert linked to the triage case AMS ticket.", event_payload={"ticket_id": str(ticket.id), "triage_case_id": str(triage.id)}, created_by="system", created_at=now))
    db.commit()
    return get_ticket(db, ticket.id)


def create_ticket_from_diagnostic(db: Session, case_id: UUID, commit: bool = True) -> TicketResponse:
    diagnostic = db.get(ObsDiagnosticCase, case_id)
    if diagnostic is None:
        raise AmsError("Diagnostic case not found.", 404)
    if diagnostic.linked_ticket_id:
        existing = db.get(AmsTicket, diagnostic.linked_ticket_id)
        if existing is not None and existing.status not in ("CLOSED", "CANCELLED"):
            return get_ticket(db, existing.id)
    priority = {"CRITICAL": "P1", "HIGH": "P2", "MEDIUM": "P3", "LOW": "P4"}.get(diagnostic.severity, "P3")
    now = _now()
    description = (
        f"Diagnostic case {diagnostic.diagnostic_number}.\n{diagnostic.diagnosis_summary}\n\n"
        f"Probable cause: {diagnostic.probable_cause}\nConfidence: {diagnostic.confidence_level}\n"
        f"Recommended next steps:\n{diagnostic.recommended_next_steps}"
    )[:2000]
    ticket = AmsTicket(
        ticket_number=_next_number(db, "INCIDENT"), ticket_type="INCIDENT", severity=diagnostic.severity, priority=priority,
        status="NEW", source="OBSERVABILITY", source_module="OBSERVABILITY", affected_entity_type="DIAGNOSTIC_CASE", affected_entity_id=diagnostic.id,
        short_description=f"{diagnostic.diagnostic_number}: {diagnostic.title}"[:200], description=description,
        assignment_group="AMS-WAREHOUSE-SUPPORT", business_service="Warehouse & Fulfillment Operations",
        application_name="Enterprise Operations Suite", environment=get_settings().app_env, opened_at=now, created_at=now, updated_at=now,
    )
    db.add(ticket)
    db.flush()
    diagnostic.linked_ticket_id, diagnostic.status, diagnostic.updated_at = ticket.id, "LINKED_TO_TICKET", now
    if diagnostic.primary_trace_id:
        trace = db.get(ObsTrace, diagnostic.primary_trace_id)
        if trace is not None:
            trace.linked_ticket_id, trace.updated_at = ticket.id, now
    _event(db, ticket, "TICKET_CREATED", f"Ticket created from diagnostic case {diagnostic.diagnostic_number}.", to_status="NEW", payload={"diagnostic_case_id": str(diagnostic.id)})
    if commit:
        db.commit()
    return get_ticket(db, ticket.id)


def create_ticket_from_batch_run(db: Session, run_id: UUID) -> TicketResponse:
    run = db.get(BatchRun, run_id)
    if run is None:
        raise AmsError("Batch run not found.", 404)
    if run.linked_ticket_id:
        existing = db.get(AmsTicket, run.linked_ticket_id)
        if existing is not None and existing.status not in ("CLOSED", "CANCELLED"):
            return get_ticket(db, existing.id)
    if run.status == "SUCCESS":
        raise AmsError("Successful batch runs cannot create support tickets.", 409)
    severity = "HIGH" if run.status in ("FAILED", "TIMEOUT") else "MEDIUM"
    priority = "P2" if run.status in ("FAILED", "TIMEOUT") else "P3"
    now = _now()
    description = (
        f"Batch job: {run.job.name} ({run.job.job_code})\nRun: {run.run_number}\n"
        f"Failed step: {next((step.step_code for step in run.step_runs if step.status in ('FAILED', 'TIMEOUT', 'PARTIAL_SUCCESS')), 'not available')}\n"
        f"Failure type: {run.failure_type or 'UNKNOWN'}\nFailure message: {run.failure_message or run.summary}\n"
        f"Records processed/succeeded/failed: {run.records_processed}/{run.records_succeeded}/{run.records_failed}"
    )[:2000]
    ticket = AmsTicket(
        ticket_number=_next_number(db, "INCIDENT"), ticket_type="INCIDENT", severity=severity, priority=priority, status="NEW",
        source="BATCH", source_module="BATCH_OPERATIONS", affected_entity_type="BATCH_RUN", affected_entity_id=run.id,
        short_description=f"{run.job.job_code} {run.run_number}: batch support issue"[:200], description=description,
        assignment_group="AMS-WAREHOUSE-SUPPORT", business_service="Warehouse & Fulfillment Operations", application_name="Enterprise Operations Suite",
        environment=get_settings().app_env, opened_at=now, created_at=now, updated_at=now,
    )
    db.add(ticket)
    db.flush()
    run.linked_ticket_id, run.updated_at = ticket.id, now
    _event(db, ticket, "TICKET_CREATED", f"Ticket created from batch run {run.run_number}.", to_status="NEW", payload={"batch_run_id": str(run.id)})
    from app.models.batch import BatchRunEvent
    db.add(BatchRunEvent(batch_run_id=run.id, event_type="BATCH_TICKET_CREATED", message=f"AMS ticket {ticket.ticket_number} created.", event_payload={"ticket_id": str(ticket.id)}, created_by="system", created_at=now))
    db.commit()
    return get_ticket(db, ticket.id)


def acknowledge_ticket(db: Session, ticket_id: UUID) -> TicketResponse:
    return _transition(db, ticket_id, "ACKNOWLEDGED", ("NEW",), "TICKET_ACKNOWLEDGED", "AMS ticket acknowledged.", set_acknowledged=True)


def start_work(db: Session, ticket_id: UUID) -> TicketResponse:
    return _transition(db, ticket_id, "IN_PROGRESS", ("NEW", "ACKNOWLEDGED"), "TICKET_STATUS_CHANGED", "AMS ticket work started.")


def _transition(db: Session, ticket_id: UUID, new_status: str, allowed: tuple[str, ...], event_type: str, message: str, set_acknowledged: bool = False) -> TicketResponse:
    ticket = db.get(AmsTicket, ticket_id)
    if ticket is None:
        raise AmsError("AMS ticket not found.", 404)
    if ticket.status not in allowed:
        raise AmsError(f"Ticket cannot transition from {ticket.status} to {new_status}.")
    old_status = ticket.status
    now = _now()
    ticket.status = new_status
    ticket.updated_at = now
    if set_acknowledged:
        ticket.acknowledged_at = now
    _event(db, ticket, event_type, message, from_status=old_status, to_status=new_status)
    db.commit()
    return get_ticket(db, ticket.id)


def resolve_ticket(db: Session, ticket_id: UUID, resolution_code: str, resolution_notes: str) -> TicketResponse:
    ticket = db.get(AmsTicket, ticket_id)
    if ticket is None:
        raise AmsError("AMS ticket not found.", 404)
    if ticket.status not in ("NEW", "ACKNOWLEDGED", "IN_PROGRESS"):
        raise AmsError(f"Ticket cannot transition from {ticket.status} to RESOLVED.")
    old_status = ticket.status
    now = _now()
    ticket.status = "RESOLVED"
    ticket.resolved_at = now
    ticket.resolution_code = resolution_code.strip()
    ticket.resolution_notes = resolution_notes.strip()
    ticket.updated_at = now
    if ticket.exception_id:
        exception = db.get(OpsException, ticket.exception_id)
        if exception is not None:
            exception.status = "RESOLVED"
            exception.resolved_at = now
            exception.updated_at = now
    _event(db, ticket, "TICKET_RESOLVED", "AMS ticket resolved.", from_status=old_status, to_status="RESOLVED", payload={"resolution_code": ticket.resolution_code})
    db.commit()
    return get_ticket(db, ticket.id)


def close_ticket(db: Session, ticket_id: UUID) -> TicketResponse:
    return _transition(db, ticket_id, "CLOSED", ("RESOLVED",), "TICKET_CLOSED", "AMS ticket closed.")


def list_events(db: Session, ticket_id: UUID) -> list[TicketEventResponse]:
    if db.get(AmsTicket, ticket_id) is None:
        raise AmsError("AMS ticket not found.", 404)
    return [TicketEventResponse.model_validate(event, from_attributes=True) for event in db.scalars(select(AmsTicketEvent).where(AmsTicketEvent.ticket_id == ticket_id).order_by(AmsTicketEvent.created_at, AmsTicketEvent.id)).all()]


def get_summary(db: Session) -> AmsSummary:
    open_exceptions = db.scalar(select(func.count(OpsException.id)).where(OpsException.status.in_(("OPEN", "ACKNOWLEDGED", "LINKED_TO_TICKET")))) or 0
    critical_exceptions = db.scalar(select(func.count(OpsException.id)).where(OpsException.status.in_(("OPEN", "ACKNOWLEDGED", "LINKED_TO_TICKET")), OpsException.severity == "CRITICAL")) or 0
    open_tickets = db.scalar(select(func.count(AmsTicket.id)).where(AmsTicket.status.in_(ACTIVE_TICKET_STATUSES))) or 0
    p1_tickets = db.scalar(select(func.count(AmsTicket.id)).where(AmsTicket.status.in_(ACTIVE_TICKET_STATUSES), AmsTicket.priority == "P1")) or 0
    p2_tickets = db.scalar(select(func.count(AmsTicket.id)).where(AmsTicket.status.in_(ACTIVE_TICKET_STATUSES), AmsTicket.priority == "P2")) or 0
    tickets_in_progress = db.scalar(select(func.count(AmsTicket.id)).where(AmsTicket.status == "IN_PROGRESS")) or 0
    start_today = datetime.combine(_now().date(), time.min, tzinfo=timezone.utc)
    resolved_today = db.scalar(select(func.count(AmsTicket.id)).where(AmsTicket.resolved_at >= start_today)) or 0
    return AmsSummary(open_exceptions=open_exceptions, critical_exceptions=critical_exceptions, open_tickets=open_tickets, p1_tickets=p1_tickets, p2_tickets=p2_tickets, tickets_in_progress=tickets_in_progress, resolved_today=resolved_today)
