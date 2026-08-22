"""Request and response schemas for the deterministic AMS ticket APIs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    ticket_number: str | None = Field(default=None, min_length=1, max_length=60)
    ticket_type: str = "INCIDENT"
    severity: str = "MEDIUM"
    priority: str = "P3"
    short_description: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    affected_entity_type: str | None = Field(default=None, max_length=40)
    affected_entity_id: UUID | None = None
    assignment_group: str = Field(default="AMS-WAREHOUSE-SUPPORT", max_length=120)


class TicketResolveRequest(BaseModel):
    resolution_code: str = Field(min_length=1, max_length=80)
    resolution_notes: str = Field(min_length=1, max_length=2000)


class TicketEventResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    event_type: str
    from_status: str | None
    to_status: str | None
    message: str
    event_payload: dict | None
    created_by: str
    created_at: datetime


class TicketResponse(BaseModel):
    id: UUID
    ticket_number: str
    ticket_type: str
    severity: str
    priority: str
    status: str
    source: str
    source_module: str
    exception_id: UUID | None
    affected_entity_type: str | None
    affected_entity_id: UUID | None
    short_description: str
    description: str
    assignment_group: str
    assigned_to: str | None
    business_service: str
    application_name: str
    environment: str
    opened_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    closed_at: datetime | None
    resolution_code: str | None
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime
    exception: "ExceptionResponse | None" = None
    events: list[TicketEventResponse] = Field(default_factory=list)


class AmsSummary(BaseModel):
    open_exceptions: int
    critical_exceptions: int
    open_tickets: int
    p1_tickets: int
    p2_tickets: int
    tickets_in_progress: int
    resolved_today: int


from app.schemas.operations import ExceptionResponse  # noqa: E402

TicketResponse.model_rebuild()
