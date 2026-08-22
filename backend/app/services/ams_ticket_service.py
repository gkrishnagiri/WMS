"""Deterministic AMS ticket creation and lifecycle services."""

from __future__ import annotations

from datetime import datetime, time, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ams import AmsTicket, AmsTicketEvent
from app.models.operations import OpsException
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
        exception_id=ticket.exception_id, affected_entity_type=ticket.affected_entity_type, affected_entity_id=ticket.affected_entity_id,
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
