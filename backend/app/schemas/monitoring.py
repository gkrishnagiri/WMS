"""Schemas for deterministic monitoring alerts and manual triage."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class MonitoringComponentResponse(BaseModel):
    id: UUID
    component_code: str
    name: str
    component_type: str
    layer: str
    environment: str
    owner_team: str
    business_service: str
    application_name: str
    status: str
    description: str
    created_at: datetime
    updated_at: datetime


class AlertRuleResponse(BaseModel):
    id: UUID
    rule_code: str
    name: str
    description: str
    component_id: UUID
    component_code: str
    metric_name: str
    condition_operator: str
    threshold_value: float
    severity: str
    enabled: bool
    dedupe_window_minutes: int
    created_at: datetime
    updated_at: datetime


class AlertEventResponse(BaseModel):
    id: UUID
    alert_id: UUID
    event_type: str
    from_status: str | None
    to_status: str | None
    message: str
    event_payload: dict | None
    created_by: str
    created_at: datetime


class AlertResponse(BaseModel):
    id: UUID
    alert_number: str
    rule_id: UUID
    rule_code: str
    component_id: UUID
    component_code: str
    component_name: str
    severity: str
    status: str
    signal_type: str
    metric_name: str
    observed_value: float
    threshold_value: float
    dedupe_key: str
    title: str
    description: str
    first_seen_at: datetime
    last_seen_at: datetime
    occurrence_count: int
    acknowledged_at: datetime | None
    suppressed_at: datetime | None
    resolved_at: datetime | None
    linked_exception_id: UUID | None
    linked_ticket_id: UUID | None
    linked_ticket_number: str | None = None
    created_at: datetime
    updated_at: datetime


class MonitoringSummary(BaseModel):
    open_alerts: int
    critical_alerts: int
    high_alerts: int
    acknowledged_alerts: int
    suppressed_alerts: int
    open_triage_cases: int
    alerts_linked_to_tickets: int
    noisiest_component: str | None


class SimulationResult(BaseModel):
    simulation_code: str
    alerts_created: int
    alerts_repeated: int
    alerts_open: int
    highest_severity: str | None
    simulation_summary: str
    alerts: list[AlertResponse]


class TriageAlertSummary(BaseModel):
    id: UUID
    alert_number: str
    component_code: str
    severity: str
    status: str
    metric_name: str
    title: str


class TriageCaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=1500)
    severity: str = Field(default="MEDIUM", max_length=20)
    suspected_impact: str = Field(min_length=1, max_length=1000)
    suspected_root_cause: str | None = Field(default=None, max_length=1000)
    confidence_level: str = Field(default="UNKNOWN", max_length=20)
    analysis_notes: str | None = Field(default=None, max_length=2000)
    alert_ids: list[UUID] = Field(default_factory=list)


class AddAlertsRequest(BaseModel):
    alert_ids: list[UUID] = Field(min_length=1)


class TriageResolveRequest(BaseModel):
    analysis_notes: str = Field(default="Support engineer resolved the symptom after manual analysis.", min_length=1, max_length=2000)


class TriageCaseResponse(BaseModel):
    id: UUID
    case_number: str
    title: str
    description: str
    status: str
    severity: str
    suspected_impact: str
    suspected_root_cause: str | None
    confidence_level: str
    analysis_notes: str | None
    linked_ticket_id: UUID | None
    linked_ticket_number: str | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    closed_at: datetime | None
    alert_count: int
    alerts: list[TriageAlertSummary] = Field(default_factory=list)
