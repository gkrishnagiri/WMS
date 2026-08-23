"""Schemas for the local external observability stack."""

from __future__ import annotations

from pydantic import BaseModel


class StackSummary(BaseModel):
    otel_enabled: bool
    otel_available: bool
    service_name: str
    collector_endpoint: str
    traces_enabled: bool
    logs_enabled: bool
    metrics_enabled: bool
    tempo_url: str
    loki_url: str
    prometheus_url: str
    grafana_url: str
    initialization_error: str | None = None


class StackHealthComponent(BaseModel):
    name: str
    url: str
    status: str
    detail: str | None = None


class StackHealth(BaseModel):
    status: str
    components: list[StackHealthComponent]


class TestActionResponse(BaseModel):
    status: str
    message: str
    trace_id: str | None = None
    span_id: str | None = None
    metric_name: str | None = None


class TestAllResponse(BaseModel):
    span: TestActionResponse
    log: TestActionResponse
    metric: TestActionResponse
