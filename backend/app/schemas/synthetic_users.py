"""Schemas for synthetic users, journeys, and deterministic journey runs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SyntheticUserResponse(BaseModel):
    id: UUID
    user_code: str
    display_name: str
    persona: str
    department: str
    role: str
    email: str | None
    active: bool
    created_at: datetime
    updated_at: datetime


class SyntheticJourneyResponse(BaseModel):
    id: UUID
    journey_code: str
    name: str
    description: str
    persona: str
    journey_type: str
    expected_outcome: str
    creates_user_report_on_failure: bool
    creates_ticket_on_failure: bool
    enabled: bool
    default_payload: dict | None
    created_at: datetime
    updated_at: datetime


class RunJourneyRequest(BaseModel):
    synthetic_user_id: UUID | None = None
    create_ticket: bool = True
    input_payload: dict = Field(default_factory=dict)


class RunSuiteRequest(BaseModel):
    create_ticket: bool = True


class JourneyRunResponse(BaseModel):
    id: UUID
    run_number: str
    journey_id: UUID
    journey_code: str
    journey_name: str
    synthetic_user_id: UUID
    synthetic_user_name: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    input_payload: dict | None
    result_payload: dict | None
    failure_type: str | None
    failure_message: str | None
    order_id: UUID | None
    task_id: UUID | None
    shipment_id: UUID | None
    user_report_id: UUID | None
    user_report_number: str | None
    ticket_id: UUID | None
    ticket_number: str | None
    created_at: datetime
    updated_at: datetime


class RunSuiteResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    runs: list[JourneyRunResponse]

