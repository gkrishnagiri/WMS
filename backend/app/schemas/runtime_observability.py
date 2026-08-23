"""Schemas for runtime request observability."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.observability import TraceResponse


class RuntimeSummary(BaseModel):
    runtime_traces: int
    successful_requests: int
    degraded_requests: int
    error_requests: int
    average_latency_ms: float
    max_latency_ms: int
    slow_request_threshold_ms: int
    runtime_logs: int
    runtime_metric_samples: int
    last_runtime_trace_at: datetime | None


class RuntimeTraceDetail(TraceResponse):
    request_id: str | None = None
    correlation_id: str | None = None
    traceparent: str | None = None


class RuntimeProbeResponse(BaseModel):
    status: str
    trace_id: UUID
    trace_identifier: str
    database_status: str
    redis_status: str
    duration_ms: int
    db_latency_ms: int
    redis_latency_ms: int
