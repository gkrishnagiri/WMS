"""Tests for presenter-controlled, local-only guided demo scenarios."""

import pytest

from app.bff.app_factory import create_bff_app
from app.bff.experience_registry import get_experience


@pytest.mark.anyio
async def test_catalog_summary_and_all_required_scenarios(warehouse_client):
    catalog = await warehouse_client.get("/api/v1/demo-scenarios/catalog")
    assert catalog.status_code == 200
    assert {item["scenario_code"] for item in catalog.json()} == {"STUCK_FULFILLMENT_ORDER", "BATCH_FAILURE_RECOVERY", "USER_REPORTED_SHIPMENT_DELAY", "OBSERVABILITY_ALERT_NOISE_ROOT_CAUSE"}
    summary = await warehouse_client.get("/api/v1/demo-scenarios/summary")
    assert summary.status_code == 200
    assert summary.json()["safe_local_only"] is True
    assert summary.json()["real_model_called_by_readiness"] is False


@pytest.mark.anyio
@pytest.mark.parametrize("scenario_code", ["STUCK_FULFILLMENT_ORDER", "BATCH_FAILURE_RECOVERY", "USER_REPORTED_SHIPMENT_DELAY", "OBSERVABILITY_ALERT_NOISE_ROOT_CAUSE"])
async def test_each_scenario_starts_with_local_artifacts(warehouse_client, scenario_code):
    response = await warehouse_client.post(f"/api/v1/demo-scenarios/{scenario_code}/start", json={"created_by_role": "DEMO_PRESENTER"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "IN_PROGRESS"
    assert len(body["steps"]) >= 8
    assert body["steps"][0]["status"] == "ACTIVE"
    assert body["timeline"][0]["event_type"] in {"ISSUE_INDUCED", "SCENARIO_STARTED"}
    assert body["artifacts"]


@pytest.mark.anyio
async def test_scenario_advance_links_agent_workspace_and_reset_preserves_timeline(warehouse_client):
    started = await warehouse_client.post("/api/v1/demo-scenarios/STUCK_FULFILLMENT_ORDER/start", json={})
    run_id = started.json()["run_id"]
    for _ in range(4):
        advanced = await warehouse_client.post(f"/api/v1/demo-scenarios/runs/{run_id}/advance", json={})
        assert advanced.status_code == 200
    body = advanced.json()
    artifact_types = {item["artifact_type"] for item in body["artifacts"]}
    assert {"AGENT_CASE", "AGENT_SESSION", "INVESTIGATION_WORKSPACE", "ACTION_PROPOSAL"} <= artifact_types
    case_id = next(item["artifact_id"] for item in body["artifacts"] if item["artifact_type"] == "AGENT_CASE")
    workspace = await warehouse_client.get(f"/api/v1/agent-investigations/cases/{case_id}")
    assert workspace.status_code == 200
    assert workspace.json()["scenario_context"]["run_id"] == run_id
    assert workspace.json()["scenario_context"]["url"] == f"/demo-scenarios/runs/{run_id}"
    timeline_before = await warehouse_client.get(f"/api/v1/demo-scenarios/runs/{run_id}/timeline")
    reset = await warehouse_client.post(f"/api/v1/demo-scenarios/runs/{run_id}/reset", json={"reset_reason": "test reset"})
    assert reset.status_code == 200
    assert reset.json()["status"] == "RESET"
    timeline_after = await warehouse_client.get(f"/api/v1/demo-scenarios/runs/{run_id}/timeline")
    assert len(timeline_after.json()) > len(timeline_before.json())
    assert timeline_after.json()[-1]["event_type"] == "SCENARIO_RESET"


def test_demo_scenario_bff_exposure_boundaries():
    operations = {route.path for route in create_bff_app(get_experience("operations")).routes}
    simulation = {route.path for route in create_bff_app(get_experience("simulation")).routes}
    agentic = {route.path for route in create_bff_app(get_experience("agentic")).routes}
    business = {route.path for route in create_bff_app(get_experience("business")).routes}
    observability = {route.path for route in create_bff_app(get_experience("observability")).routes}
    assert "/api/v1/demo-scenarios/summary" in operations
    assert "/api/v1/demo-scenarios/{scenario_code}/start" in operations
    assert "/api/v1/demo-scenarios/{scenario_code}/start" in simulation
    assert "/api/v1/demo-scenarios/{scenario_code}/start" in agentic
    assert "/api/v1/demo-scenarios/catalog" in business
    assert "/api/v1/demo-scenarios/{scenario_code}/start" not in business
    assert "/api/v1/demo-scenarios/summary" not in observability
