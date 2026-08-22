"""Schemas for user-reported functional issues."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserReportCreate(BaseModel):
    reporter_user_id: UUID | None = None
    reporter_name: str = Field(min_length=1, max_length=160)
    reporter_email: str | None = Field(default=None, max_length=200)
    reporter_persona: str | None = Field(default=None, max_length=40)
    report_channel: str = Field(default="USER_PORTAL", max_length=30)
    source_module: str = Field(default="WAREHOUSE_FULFILLMENT", max_length=80)
    affected_entity_type: str = Field(default="UNKNOWN", max_length=40)
    affected_entity_id: UUID | None = None
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    business_impact: str = Field(min_length=1, max_length=1000)
    severity: str = "MEDIUM"
    journey_run_id: UUID | None = None
    create_ticket: bool = True


class ReportTicketSummary(BaseModel):
    id: UUID
    ticket_number: str
    status: str
    priority: str


class UserReportResponse(BaseModel):
    id: UUID
    report_number: str
    reporter_user_id: UUID | None
    reporter_name: str
    reporter_email: str | None
    reporter_persona: str | None
    report_channel: str
    source_module: str
    affected_entity_type: str
    affected_entity_id: UUID | None
    title: str
    description: str
    business_impact: str
    severity: str
    status: str
    journey_run_id: UUID | None
    journey_run_number: str | None
    journey_code: str | None
    ticket_id: UUID | None
    ticket: ReportTicketSummary | None
    submitted_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

