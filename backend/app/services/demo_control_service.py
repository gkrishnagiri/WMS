"""Read-only status and topology helpers for the local EOS demo stack."""

from __future__ import annotations

import socket
from datetime import datetime, timezone

import httpx
from fastapi import Request

from app.bff.experience_registry import EXPERIENCE_DEFINITIONS
from app.schemas.demo_control import DemoReadinessItem, DemoReadinessResponse


OBSERVABILITY_URLS = {
    "grafana": "http://localhost:3001",
    "prometheus": "http://localhost:9090",
    "tempo_ready": "http://localhost:3200/ready",
    "loki_ready": "http://localhost:3100/ready",
    "otel_collector_health": "http://localhost:13133/",
}


def _experience_payload() -> list[dict[str, str]]:
    return [
        {
            "code": item.code,
            "name": item.name,
            "frontend_url": item.frontend_url,
            "backend_url": item.backend_url,
            "purpose": item.description,
        }
        for item in EXPERIENCE_DEFINITIONS.values()
    ]


def urls() -> dict[str, object]:
    return {
        "experiences": _experience_payload(),
        "observability": OBSERVABILITY_URLS,
        "capabilities": ["Stage 2 Action Catalog", "Approval-Gated Actions", "Action Execution Audit", "Governed Stage 1 Model Chat", "Model Context Preview", "Model Invocation Audit", "AI Costing Model Catalog", "AI Pricing Configuration", "AI Usage Metering", "Cost Guardrails", "One-Shot Smoke Test", "Demo Scenario Catalog", "Guided Scenario Runs", "Scenario Artifact Linking", "Scenario Timeline", "Executive Demo Dashboard", "Value Metrics", "Executive Storyboard", "Governance Dashboard", "Commercial Model View", "Demo Readiness", "Showcase Mode", "Reset Profiles", "UI Test Guide", "Smoke Report", "UI Acceptance Catalog", "UI Acceptance Run Tracker", "Evidence Report"],
        "logs_directory": "/tmp/eos-demo/logs",
        "runtime_directory": "/tmp/eos-demo",
    }


def _http_item(name: str, kind: str, url: str, expected_status: int = 200) -> DemoReadinessItem:
    try:
        response = httpx.get(url, timeout=0.75)
        healthy = response.status_code == expected_status
        return DemoReadinessItem(
            name=name,
            kind=kind,
            url=url,
            expected_status=expected_status,
            actual_status=response.status_code,
            healthy=healthy,
            message="reachable" if healthy else f"HTTP {response.status_code}",
        )
    except httpx.HTTPError as error:
        return DemoReadinessItem(
            name=name,
            kind=kind,
            url=url,
            expected_status=expected_status,
            healthy=False,
            message=f"unreachable: {str(error)[:180]}",
        )


def _tcp_item(name: str, url: str, port: int) -> DemoReadinessItem:
    try:
        with socket.create_connection(("localhost", port), timeout=0.75):
            return DemoReadinessItem(name=name, kind="infrastructure", url=url, expected_status="reachable", actual_status="reachable", healthy=True, message="TCP connection accepted")
    except OSError as error:
        return DemoReadinessItem(name=name, kind="infrastructure", url=url, expected_status="reachable", healthy=False, message=f"unreachable: {str(error)[:180]}")


def readiness() -> DemoReadinessResponse:
    items = [
        _tcp_item("PostgreSQL", "tcp://localhost:15432", 15432),
        _tcp_item("Redis", "tcp://localhost:6379", 6379),
        _http_item("OpenTelemetry Collector", "infrastructure", OBSERVABILITY_URLS["otel_collector_health"]),
        _http_item("Prometheus", "infrastructure", "http://localhost:9090/-/ready"),
        _http_item("Grafana", "infrastructure", "http://localhost:3001/api/health"),
        _http_item("Tempo", "infrastructure", OBSERVABILITY_URLS["tempo_ready"]),
        _http_item("Loki", "infrastructure", OBSERVABILITY_URLS["loki_ready"]),
    ]
    for item in EXPERIENCE_DEFINITIONS.values():
        items.append(_http_item(f"{item.name} backend", "backend", f"{item.backend_url}/health"))
    items.append(_http_item("Observability Alerting", "backend", "http://localhost:8050/api/v1/observability-alerts/summary"))
    items.append(_http_item("Agent Chat", "backend", "http://localhost:8050/api/v1/agent-chat/summary"))
    items.append(_http_item("Agentic Case Intake", "backend", "http://localhost:8065/api/v1/agent-chat/summary"))
    items.append(_http_item("Stage 1 Orchestrator", "backend", "http://localhost:8050/api/v1/agent-chat/summary"))
    items.append(_http_item("Contextual Agent Handoff", "backend", "http://localhost:8050/api/v1/agent-chat/summary"))
    items.append(_http_item("AMS-to-Agent Handoff", "backend", "http://localhost:8050/api/v1/agent-chat/summary"))
    items.append(_http_item("Alert-to-Agent Handoff", "backend", "http://localhost:8050/api/v1/agent-chat/summary"))
    items.append(_http_item("Batch-to-Agent Handoff", "backend", "http://localhost:8050/api/v1/agent-chat/summary"))
    items.append(_http_item("Agent Investigation Workspace", "backend", "http://localhost:8050/api/v1/agent-investigations/summary"))
    items.append(_http_item("Evidence Timeline", "backend", "http://localhost:8050/api/v1/agent-investigations/summary"))
    items.append(_http_item("Investigation Drafts", "backend", "http://localhost:8050/api/v1/agent-investigations/summary"))
    items.append(_http_item("Stage 2 Action Catalog", "backend", "http://localhost:8050/api/v1/agent-actions/summary"))
    items.append(_http_item("Approval-Gated Actions", "backend", "http://localhost:8050/api/v1/agent-actions/summary"))
    items.append(_http_item("Action Execution Audit", "backend", "http://localhost:8050/api/v1/agent-actions/executions"))
    items.append(_http_item("Governed Stage 1 Model Chat", "backend", "http://localhost:8050/api/v1/agent-model-chat/status"))
    items.append(_http_item("Model Context Preview", "backend", "http://localhost:8050/api/v1/agent-model-chat/status"))
    items.append(_http_item("Model Invocation Audit", "backend", "http://localhost:8050/api/v1/agent-model-chat/invocations"))
    items.append(_http_item("Demo Scenario Catalog", "backend", "http://localhost:8050/api/v1/demo-scenarios/catalog"))
    items.append(_http_item("Guided Scenario Runs", "backend", "http://localhost:8050/api/v1/demo-scenarios/summary"))
    items.append(_http_item("Scenario Artifact Linking", "backend", "http://localhost:8050/api/v1/demo-scenarios/summary"))
    items.append(_http_item("Scenario Timeline", "backend", "http://localhost:8050/api/v1/demo-scenarios/summary"))
    items.append(_http_item("Executive Demo Dashboard", "backend", "http://localhost:8050/api/v1/executive-demo/summary"))
    items.append(_http_item("Value Metrics", "backend", "http://localhost:8050/api/v1/executive-demo/value-metrics"))
    items.append(_http_item("Executive Storyboard", "backend", "http://localhost:8050/api/v1/executive-demo/storyboard"))
    items.append(_http_item("Governance Dashboard", "backend", "http://localhost:8050/api/v1/executive-demo/governance"))
    items.append(_http_item("Commercial Model View", "backend", "http://localhost:8050/api/v1/executive-demo/commercial-model"))
    items.append(_http_item("Demo Readiness", "backend", "http://localhost:8050/api/v1/demo-readiness/summary"))
    items.append(_http_item("Showcase Mode", "backend", "http://localhost:8050/api/v1/demo-readiness/showcase"))
    items.append(_http_item("Reset Profiles", "backend", "http://localhost:8050/api/v1/demo-readiness/reset-profiles"))
    items.append(_http_item("UI Test Guide", "backend", "http://localhost:8050/api/v1/demo-readiness/ui-test-guide"))
    items.append(_http_item("Smoke Report", "backend", "http://localhost:8050/api/v1/demo-readiness/smoke-report"))
    items.append(_http_item("UI Acceptance Catalog", "backend", "http://localhost:8050/api/v1/ui-acceptance/summary"))
    items.append(_http_item("UI Acceptance Run Tracker", "backend", "http://localhost:8050/api/v1/ui-acceptance/runs"))
    items.append(_http_item("Evidence Report", "backend", "http://localhost:8050/api/v1/ui-acceptance/coverage"))
    items.append(_http_item("Agent Knowledge", "backend", "http://localhost:8050/api/v1/agent-knowledge/summary"))
    items.append(_http_item("Deterministic Retrieval", "backend", "http://localhost:8050/api/v1/agent-knowledge/summary"))
    items.append(_http_item("RAG Foundation", "backend", "http://localhost:8050/api/v1/agent-knowledge/summary"))
    items.append(_http_item("Real Model Provider", "backend", "http://localhost:8050/api/v1/ai-config/real-model/status"))
    items.append(_http_item("OpenAI Responses Provider", "backend", "http://localhost:8050/api/v1/ai-config/real-model/status"))
    items.append(_http_item("Real Model Feature Flag", "backend", "http://localhost:8050/api/v1/ai-config/real-model/status"))
    items.append(_http_item("AI Costing Model Catalog", "backend", "http://localhost:8050/api/v1/ai-costing/models"))
    items.append(_http_item("AI Usage Metering", "backend", "http://localhost:8050/api/v1/ai-costing/summary"))
    items.append(_http_item("Cost Guardrails", "backend", "http://localhost:8050/api/v1/ai-costing/guardrails"))
    items.append(_http_item("Real Model Smoke Test Controls", "backend", "http://localhost:8050/api/v1/ai-costing/summary"))
    for item in EXPERIENCE_DEFINITIONS.values():
        items.append(_http_item(f"{item.name} frontend", "frontend", item.frontend_url))
    return DemoReadinessResponse(
        overall_status="HEALTHY" if all(item.healthy for item in items) else "DEGRADED",
        checked_at=datetime.now(timezone.utc),
        items=items,
    )


def summary(request: Request) -> dict[str, object]:
    status = readiness()
    return {
        "application": request.app.state.settings.app_name,
        "mode": "local-demo",
        "summary": {"frontends": 6, "backends": 6, "infrastructure_components": 7},
        "overall_status": status.overall_status,
        "experiences": _experience_payload(),
        "observability": {
            "grafana": OBSERVABILITY_URLS["grafana"],
            "prometheus": OBSERVABILITY_URLS["prometheus"],
            "tempo_ready": OBSERVABILITY_URLS["tempo_ready"],
            "loki_ready": OBSERVABILITY_URLS["loki_ready"],
        },
    }


def components() -> dict[str, object]:
    status = readiness()
    return {"overall_status": status.overall_status, "components": [item.model_dump(mode="json") for item in status.items]}
