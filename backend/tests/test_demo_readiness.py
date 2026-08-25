"""Readiness and showcase hardening tests for the local EOS demo."""

import pytest

from app.bff.app_factory import create_bff_app
from app.bff.experience_registry import get_experience
from app.services.demo_control_service import urls as demo_control_urls


@pytest.mark.anyio
async def test_readiness_reporting_endpoints_are_read_only(warehouse_client):
    before = (await warehouse_client.get("/api/v1/demo-scenarios/runs")).json()
    endpoints = ("summary", "checks", "showcase", "urls", "ui-test-guide", "smoke-report", "reset-profiles")
    responses = {endpoint: await warehouse_client.get(f"/api/v1/demo-readiness/{endpoint}") for endpoint in endpoints}
    assert all(response.status_code == 200 for response in responses.values())
    after = (await warehouse_client.get("/api/v1/demo-scenarios/runs")).json()
    assert len(after) == len(before)
    summary = responses["summary"].json()
    assert summary["real_model_default_enabled"] is False
    assert summary["autonomous_remediation_enabled"] is False
    assert summary["service_now_enabled"] is False
    assert responses["urls"].json()["urls"]
    assert responses["ui-test-guide"].json()["sections"]


@pytest.mark.anyio
async def test_showcase_reset_ensures_catalog_without_preparing_runs(warehouse_client):
    response = await warehouse_client.post("/api/v1/demo-readiness/prepare-showcase", json={"profile": "SHOWCASE_RESET", "create_prepared_runs": False, "created_by_role": "DEMO_PRESENTER"})
    assert response.status_code == 200
    body = response.json()
    assert body["prepared_run_count"] == 0
    assert body["model_called"] is False
    assert body["actions_approved"] is False
    assert body["actions_executed"] is False
    assert body["readiness"]["real_model_default_enabled"] is False
    assert len((await warehouse_client.get("/api/v1/demo-scenarios/catalog")).json()) == 4


@pytest.mark.anyio
async def test_prepare_showcase_can_create_prepared_runs_without_actions(warehouse_client):
    response = await warehouse_client.post("/api/v1/demo-readiness/prepare-showcase", json={"profile": "SHOWCASE_RESET", "create_prepared_runs": True, "created_by_role": "DEMO_PRESENTER"})
    assert response.status_code == 200
    body = response.json()
    assert body["prepared_run_count"] == 4
    assert all(run["status"] == "IN_PROGRESS" for run in body["prepared_runs"])
    assert body["model_called"] is False
    assert body["actions_approved"] is False
    assert body["actions_executed"] is False


@pytest.mark.anyio
async def test_reset_profiles_are_guarded_and_preserve_audit_history(warehouse_client):
    blocked = await warehouse_client.post("/api/v1/demo-readiness/reset", json={"profile": "LOCAL_DEV_GENERATED_DATA_RESET", "reset_reason": "missing confirmation"})
    assert blocked.status_code == 400
    reset = await warehouse_client.post("/api/v1/demo-readiness/reset", json={"profile": "LOCAL_DEV_GENERATED_DATA_RESET", "confirmation": "RESET_LOCAL_DEMO_GENERATED_DATA", "reset_reason": "test cleanup"})
    assert reset.status_code == 200
    body = reset.json()
    assert body["generated_data_archived"] is True
    assert body["audit_history_preserved"] is True
    assert body["seed_data_deleted"] is False
    assert body["schema_dropped"] is False


def test_readiness_bff_exposure_boundaries():
    business = create_bff_app(get_experience("business")).routes
    operations = {route.path for route in create_bff_app(get_experience("operations")).routes}
    simulation = {route.path for route in create_bff_app(get_experience("simulation")).routes}
    agentic = {route.path for route in create_bff_app(get_experience("agentic")).routes}
    observability = {route.path for route in create_bff_app(get_experience("observability")).routes}
    business_paths = {(route.path, tuple(sorted(getattr(route, "methods", set())))) for route in business}
    assert ("/api/v1/demo-readiness/summary", ("GET",)) in business_paths
    assert ("/api/v1/demo-readiness/reset", ("POST",)) not in business_paths
    assert "/api/v1/demo-readiness/summary" in operations
    assert "/api/v1/demo-readiness/reset" in operations
    assert "/api/v1/demo-readiness/summary" in simulation
    assert "/api/v1/demo-readiness/summary" in agentic
    assert "/api/v1/demo-readiness/summary" not in observability


def test_demo_control_advertises_readiness_capabilities():
    capabilities = demo_control_urls()["capabilities"]
    assert {"Demo Readiness", "Showcase Mode", "Reset Profiles", "UI Test Guide", "Smoke Report"} <= set(capabilities)
