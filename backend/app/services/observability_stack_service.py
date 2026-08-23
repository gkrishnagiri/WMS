"""Configuration and deterministic test actions for the local OTel stack."""

from __future__ import annotations

import httpx
from fastapi import Request

from app.core import opentelemetry
from app.core.config import Settings
from app.schemas.observability_stack import StackHealth, StackHealthComponent, StackSummary, TestActionResponse, TestAllResponse


def summary(request: Request) -> StackSummary:
    settings: Settings = request.app.state.settings
    return StackSummary(
        otel_enabled=settings.otel_enabled,
        otel_available=bool(getattr(request.app.state, "otel_available", False)),
        service_name=settings.otel_service_name,
        collector_endpoint=settings.otel_exporter_otlp_endpoint,
        traces_enabled=settings.otel_traces_enabled,
        logs_enabled=settings.otel_logs_enabled,
        metrics_enabled=settings.otel_metrics_enabled,
        tempo_url=settings.otel_tempo_url,
        loki_url=settings.otel_loki_url,
        prometheus_url=settings.otel_prometheus_url,
        grafana_url=settings.otel_grafana_url,
        initialization_error=getattr(request.app.state, "otel_initialization_error", None),
    )


def config(request: Request) -> dict[str, object]:
    settings: Settings = request.app.state.settings
    return {
        "otel_enabled": settings.otel_enabled,
        "service_name": settings.otel_service_name,
        "service_namespace": settings.otel_service_namespace,
        "service_version": settings.otel_service_version,
        "environment": settings.otel_environment,
        "exporter_endpoint": settings.otel_exporter_otlp_endpoint,
        "exporter_protocol": settings.otel_exporter_otlp_protocol,
        "traces_enabled": settings.otel_traces_enabled,
        "logs_enabled": settings.otel_logs_enabled,
        "metrics_enabled": settings.otel_metrics_enabled,
        "sample_ratio": settings.otel_sample_ratio,
        "note": "No secrets, credentials, request bodies, or authorization headers are exposed.",
    }


def health(request: Request) -> StackHealth:
    settings: Settings = request.app.state.settings
    targets = [
        ("OpenTelemetry Collector", settings.otel_collector_health_url, "/"),
        ("Prometheus", settings.otel_prometheus_url, "/-/ready"),
        ("Grafana", settings.otel_grafana_url, "/api/health"),
        ("Tempo", settings.otel_tempo_url, "/ready"),
        ("Loki", settings.otel_loki_url, "/ready"),
    ]
    components = []
    for name, base_url, path in targets:
        url = base_url.rstrip("/") + path
        try:
            response = httpx.get(url, timeout=1.0)
            status = "healthy" if response.is_success else "unhealthy"
            detail = f"HTTP {response.status_code}"
        except httpx.HTTPError as error:
            status = "unknown"
            detail = str(error)[:240]
        components.append(StackHealthComponent(name=name, url=url, status=status, detail=detail))
    overall = "healthy" if all(item.status == "healthy" for item in components) else "degraded"
    return StackHealth(status=overall, components=components)


def test_span() -> TestActionResponse:
    data = opentelemetry.test_span()
    status = "RECORDED" if data["trace_id"] else "SKIPPED"
    return TestActionResponse(status=status, message="Deterministic test span processed by the OpenTelemetry SDK.", **data)


def test_log() -> TestActionResponse:
    data = opentelemetry.test_log()
    status = "EMITTED" if opentelemetry.is_available() else "SKIPPED"
    return TestActionResponse(status=status, message="Deterministic structured test log emitted to the application logger.", **data)


def test_metric() -> TestActionResponse:
    data = opentelemetry.test_metric()
    return TestActionResponse(status=data["status"], message="Deterministic test metric processed by the OpenTelemetry SDK.", metric_name=data["metric_name"])


def test_all() -> TestAllResponse:
    return TestAllResponse(span=test_span(), log=test_log(), metric=test_metric())
