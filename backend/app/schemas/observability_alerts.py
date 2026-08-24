"""API schemas for governed observability alerting."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AlertRuleResponse(BaseModel):
    id: UUID
    rule_code: str
    name: str
    description: str
    signal_type: str
    source_system: str
    metric_name: str | None
    query_text: str | None
    condition_operator: str
    threshold_value: float | None
    severity: str
    enabled: bool
    deduplication_key_template: str
    cooldown_minutes: int
    evaluation_window_minutes: int
    target_experience: str
    recommended_owner: str
    create_ticket_by_default: bool

    model_config = {"from_attributes": True}


class AlertEvidenceResponse(BaseModel):
    id: UUID
    evidence_type: str
    title: str
    summary: str
    payload_json: dict | None
    source_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertEventResponse(BaseModel):
    id: UUID
    event_id: str
    rule_id: UUID
    rule_code: str
    title: str
    description: str
    severity: str
    status: str
    deduplication_key: str
    source_signal: str
    source_url: str | None
    observed_value: float | None
    threshold_value: float | None
    condition_summary: str
    first_seen_at: datetime
    last_seen_at: datetime
    occurrence_count: int
    suppressed_count: int
    ticket_creation_status: str
    created_ticket_id: UUID | None
    linked_ticket_number: str | None = None
    evidence: list[AlertEvidenceResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertEvaluationRunResponse(BaseModel):
    id: UUID
    run_id: str
    trigger_source: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    rules_evaluated: int
    events_created: int
    events_suppressed: int
    tickets_created: int
    error_message: str | None
    event_ids: list[UUID] = Field(default_factory=list)


class ObservabilityAlertSummary(BaseModel):
    rules: int
    enabled_rules: int
    open_events: int
    ticketed_events: int
    acknowledged_events: int
    resolved_events: int
    evaluation_runs: int
    tickets_created: int


class EvaluateAlertsRequest(BaseModel):
    trigger_source: str = Field(default="MANUAL", max_length=40)
