"""Schemas for deterministic batch jobs and batch failure scenarios."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class BatchStepResponse(BaseModel):
    id: UUID
    step_code: str
    step_name: str
    step_order: int
    step_type: str
    description: str
    enabled: bool
    expected_duration_ms: int


class BatchRunBrief(BaseModel):
    id: UUID
    run_number: str
    status: str
    duration_ms: int | None
    records_processed: int
    records_failed: int
    started_at: datetime


class BatchJobResponse(BaseModel):
    id: UUID
    job_code: str
    name: str
    description: str
    job_type: str
    module: str
    business_service: str
    application_name: str
    enabled: bool
    default_severity: str
    sla_minutes: int
    step_count: int
    steps: list[BatchStepResponse] = Field(default_factory=list)
    recent_runs: list[BatchRunBrief] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class BatchStepRunResponse(BaseModel):
    id: UUID
    job_step_id: UUID
    step_code: str
    step_name: str
    step_order: int
    status: str
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    records_processed: int
    records_succeeded: int
    records_failed: int
    failure_type: str | None
    failure_message: str | None
    technical_context: dict | None


class BatchRunEventResponse(BaseModel):
    id: UUID
    batch_run_id: UUID
    event_type: str
    from_status: str | None
    to_status: str | None
    message: str
    event_payload: dict | None
    created_by: str
    created_at: datetime


class BatchRunResponse(BaseModel):
    id: UUID
    run_number: str
    job_id: UUID
    job_code: str
    job_name: str
    status: str
    trigger_type: str
    scenario_code: str
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    records_processed: int
    records_succeeded: int
    records_failed: int
    failure_type: str | None
    failure_message: str | None
    summary: str
    linked_exception_id: UUID | None
    linked_exception_number: str | None = None
    linked_ticket_id: UUID | None
    linked_ticket_number: str | None = None
    linked_alert_id: UUID | None
    linked_diagnostic_case_id: UUID | None
    linked_diagnostic_number: str | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime
    steps: list[BatchStepRunResponse] = Field(default_factory=list)
    events: list[BatchRunEventResponse] = Field(default_factory=list)


class BatchSummary(BaseModel):
    batch_jobs: int
    runs_total: int
    runs_success: int
    runs_failed: int
    runs_partial: int
    runs_timeout: int
    open_batch_tickets: int
    open_batch_exceptions: int
    last_run_status: str | None


class BatchSimulationRequest(BaseModel):
    create_exception: bool = False
    create_ticket: bool = False
    create_observability: bool = False


class BatchSimulationResult(BaseModel):
    run: BatchRunResponse
    exception_id: UUID | None
    exception_number: str | None
    ticket_id: UUID | None
    ticket_number: str | None
    diagnostic_case_id: UUID | None
    diagnostic_number: str | None


class BatchSuiteResult(BaseModel):
    runs_created: int
    successful_runs: int
    failed_runs: int
    partial_runs: int
    tickets_created: int
    exceptions_created: int
    diagnostics_created: int
    summary: str
    results: list[BatchSimulationResult] = Field(default_factory=list)
