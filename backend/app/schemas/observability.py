"""Schemas for deterministic observability evidence and diagnosis."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SpanResponse(BaseModel):
    id: UUID
    span_id: str
    parent_span_id: str | None
    span_name: str
    service_name: str
    component_code: str | None
    operation_type: str
    status: str
    started_at: datetime
    ended_at: datetime | None
    duration_ms: int | None
    error_type: str | None
    error_message: str | None
    attributes: dict | None


class LogEventResponse(BaseModel):
    id: UUID
    log_number: str
    trace_id: UUID | None
    span_id: UUID | None
    level: str
    logger_name: str
    message: str
    event_type: str
    source_module: str
    component_code: str | None
    entity_type: str | None
    entity_id: UUID | None
    linked_alert_id: UUID | None
    linked_ticket_id: UUID | None
    context: dict | None
    logged_at: datetime
    created_at: datetime


class MetricSampleResponse(BaseModel):
    id: UUID
    sample_number: str
    metric_name: str
    metric_value: float
    metric_unit: str
    component_code: str | None
    severity: str | None
    trace_id: UUID | None
    linked_alert_id: UUID | None
    recorded_at: datetime
    attributes: dict | None
    created_at: datetime


class TraceResponse(BaseModel):
    id: UUID
    trace_id: str
    trace_name: str
    trace_type: str
    status: str
    source_module: str
    root_entity_type: str | None
    root_entity_id: UUID | None
    root_reference: str | None
    linked_alert_id: UUID | None
    linked_triage_case_id: UUID | None
    linked_ticket_id: UUID | None
    started_at: datetime
    ended_at: datetime | None
    duration_ms: int | None
    summary: str
    spans: list[SpanResponse] = Field(default_factory=list)
    logs: list[LogEventResponse] = Field(default_factory=list)
    metrics: list[MetricSampleResponse] = Field(default_factory=list)


class EvidenceResponse(BaseModel):
    id: UUID
    evidence_type: str
    source_table: str
    source_id: UUID
    title: str
    details: str
    weight: float
    created_at: datetime


class DiagnosticCaseResponse(BaseModel):
    id: UUID
    diagnostic_number: str
    title: str
    description: str
    status: str
    severity: str
    source_type: str
    source_id: UUID | None
    linked_alert_id: UUID | None
    linked_triage_case_id: UUID | None
    linked_ticket_id: UUID | None
    primary_trace_id: UUID | None
    primary_trace_identifier: str | None = None
    probable_cause: str
    confidence_level: str
    recommended_next_steps: str
    diagnosis_summary: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    evidence: list[EvidenceResponse] = Field(default_factory=list)


class DiagnosticSummary(BaseModel):
    traces: int
    error_traces: int
    slow_spans: int
    error_logs: int
    metric_samples: int
    open_diagnostic_cases: int
    high_confidence_diagnoses: int
    linked_tickets: int


class DiagnosticTicketRequest(BaseModel):
    ticket_id: UUID | None = None


class DiagnosticResolveRequest(BaseModel):
    resolution_notes: str = Field(min_length=1, max_length=2000)


class SimulationRequest(BaseModel):
    create_ticket: bool = False


class SimulationResult(BaseModel):
    simulation_code: str
    trace_id: UUID | None
    trace_identifier: str | None
    diagnostic_case_id: UUID | None
    diagnostic_number: str | None
    alert_ids: list[UUID] = Field(default_factory=list)
    ticket_id: UUID | None
    tickets_created_or_linked: int
    summary: str


class SuiteResult(BaseModel):
    simulation_code: str
    traces_created: int
    diagnostic_cases_created: int
    alerts_created_or_reused: int
    tickets_created_or_linked: int
    highest_severity: str | None
    summary: str
    results: list[SimulationResult]
