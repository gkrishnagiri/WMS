"""Read-only executive dashboard aggregation tests."""

import pytest

from app.bff.app_factory import create_bff_app
from app.bff.experience_registry import get_experience


@pytest.mark.anyio
async def test_executive_demo_read_only_aggregate_endpoints(warehouse_client):
    before = await warehouse_client.get("/api/v1/demo-scenarios/runs")
    endpoints = ("summary", "value-metrics", "storyboard", "scenario-outcomes", "governance", "operating-model", "commercial-model", "deep-links")
    responses = {endpoint: await warehouse_client.get(f"/api/v1/executive-demo/{endpoint}") for endpoint in endpoints}
    assert all(response.status_code == 200 for response in responses.values())
    after = await warehouse_client.get("/api/v1/demo-scenarios/runs")
    assert len(after.json()) == len(before.json())
    assert responses["summary"].json()["read_only"] is True
    assert responses["summary"].json()["disclaimer"].startswith("Value estimates are demo estimates")


@pytest.mark.anyio
async def test_value_metrics_and_storyboard_are_labeled_and_governed(warehouse_client):
    metrics = (await warehouse_client.get("/api/v1/executive-demo/value-metrics")).json()
    assert metrics["metric_classification"] == "Scenario-derived metric"
    assert metrics["effort_impact"]["label"] == "Demo estimate"
    assert metrics["effort_impact"]["assumptions"]
    assert all(item["is_demo_assumption"] is True for item in metrics["effort_impact"]["assumptions"])
    governance = (await warehouse_client.get("/api/v1/executive-demo/governance")).json()
    assert governance["real_model_default"] == "Off"
    assert governance["api_key_required_for_demo"] is False
    assert governance["autonomous_remediation"] is False
    assert "shell commands" in governance["prohibited_execution"]
    storyboard = (await warehouse_client.get("/api/v1/executive-demo/storyboard")).json()
    assert [section["title"] for section in storyboard["sections"]] == [
        "The Traditional AMS Challenge", "The AI-Native AMS Operating Model", "Scenario-Based Proof Points",
        "Governance by Design", "Commercial Model Implications", "Roadmap to Production",
    ]


@pytest.mark.anyio
async def test_scenario_outcomes_operating_model_commercial_model_and_links(warehouse_client):
    outcomes = (await warehouse_client.get("/api/v1/executive-demo/scenario-outcomes")).json()
    assert len(outcomes) == 4
    assert {item["scenario_code"] for item in outcomes} == {"STUCK_FULFILLMENT_ORDER", "BATCH_FAILURE_RECOVERY", "USER_REPORTED_SHIPMENT_DELAY", "OBSERVABILITY_ALERT_NOISE_ROOT_CAUSE"}
    operating = (await warehouse_client.get("/api/v1/executive-demo/operating-model")).json()
    assert [item["step"] for item in operating["value_chain"]] == ["Signal", "Contextual Handoff", "Evidence + Knowledge", "Stage 1 Guidance", "Approval-Gated Action", "Audit + Learning"]
    commercial = (await warehouse_client.get("/api/v1/executive-demo/commercial-model")).json()
    assert commercial["rows"]
    assert any("Outcome-based" in row["ai_native_alternative"] for row in commercial["rows"])
    links = (await warehouse_client.get("/api/v1/executive-demo/deep-links")).json()["links"]
    assert "/demo-scenarios" in {item["path"] for item in links}
    assert "/agent-investigations" in {item["path"] for item in links}


def test_executive_demo_bff_exposure_boundaries():
    business = {route.path for route in create_bff_app(get_experience("business")).routes}
    operations = {route.path for route in create_bff_app(get_experience("operations")).routes}
    agentic = {route.path for route in create_bff_app(get_experience("agentic")).routes}
    simulation = {route.path for route in create_bff_app(get_experience("simulation")).routes}
    observability = {route.path for route in create_bff_app(get_experience("observability")).routes}
    expected = "/api/v1/executive-demo/summary"
    assert expected in business
    assert expected in operations
    assert expected in agentic
    assert expected in simulation
    assert expected not in observability
