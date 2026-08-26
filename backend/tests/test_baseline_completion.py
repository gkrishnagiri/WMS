"""Read-only Baseline 1.0 completion and handover tests."""

import pytest

from app.bff.app_factory import create_bff_app
from app.bff.experience_registry import get_experience
from app.services.ui_acceptance_service import seed_catalog
from app.db.session import get_db
from app.main import app


@pytest.mark.anyio
async def test_baseline_read_only_endpoints_and_content(warehouse_client):
    seed_catalog(next(app.dependency_overrides[get_db]()))
    endpoints = ("summary", "requirements", "walkthroughs", "demo-journeys", "reset-guide", "testing-guide", "model-guide", "stage-modes", "known-limitations", "signoff-checklist", "handover-pack")
    responses = {endpoint: await warehouse_client.get(f"/api/v1/baseline-completion/{endpoint}") for endpoint in endpoints}
    assert all(response.status_code == 200 for response in responses.values())
    summary = responses["summary"].json()
    assert summary["completion_status"] == "BASELINE_READY_WITH_WARNINGS"
    assert summary["real_model_default_enabled"] is False
    assert summary["stage3_autonomous_execution_default_enabled"] is False
    assert summary["read_only"] is True
    requirements = responses["requirements"].json()
    categories = {item["category"] for item in requirements["requirements"]}
    assert "Agentic Stage 1 – Assisted Investigation" in categories
    assert {item["status"] for item in requirements["requirements"]} >= {"COVERED", "OUT_OF_SCOPE"}
    walkthroughs = responses["walkthroughs"].json()["walkthroughs"]
    assert len(walkthroughs) == 8
    assert {"STUCK_FULFILLMENT_ORDER", "BATCH_FAILURE_RECOVERY", "USER_REPORTED_SHIPMENT_DELAY", "OBSERVABILITY_ALERT_NOISE_ROOT_CAUSE"} <= {item["walkthrough_id"] for item in walkthroughs}
    assert {item["mode"] for item in responses["stage-modes"].json()["stage_modes"]} == {"STAGE_1_READ_ONLY", "STAGE_2_APPROVAL_GATED", "STAGE_3_AUTONOMOUS_SANDBOX"}
    assert any("ServiceNow" in item["description"] for item in responses["known-limitations"].json()["limitations"])
    assert len(responses["signoff-checklist"].json()["sections"]) >= 15
    markdown = await warehouse_client.get("/api/v1/baseline-completion/handover-pack.md")
    assert markdown.status_code == 200
    assert markdown.headers["content-type"].startswith("text/markdown")
    assert "Baseline 1.0" in markdown.text
    assert "Requirements traceability" in markdown.text
    assert "STAGE_3_AUTONOMOUS_SANDBOX" in markdown.text


def test_baseline_bff_exposure_is_read_only():
    business = create_bff_app(get_experience("business")).routes
    operations = create_bff_app(get_experience("operations")).routes
    simulation = create_bff_app(get_experience("simulation")).routes
    agentic = create_bff_app(get_experience("agentic")).routes
    observability = create_bff_app(get_experience("observability")).routes
    business_paths = {(route.path, tuple(sorted(getattr(route, "methods", set())))) for route in business}
    assert ("/api/v1/baseline-completion/summary", ("GET",)) in business_paths
    assert all(getattr(route, "methods", set()) <= {"GET"} for route in business if route.path.startswith("/api/v1/baseline-completion"))
    for routes in (operations, simulation, agentic):
        assert "/api/v1/baseline-completion/handover-pack" in {route.path for route in routes}
        assert all(getattr(route, "methods", set()) <= {"GET"} for route in routes if route.path.startswith("/api/v1/baseline-completion"))
    assert "/api/v1/baseline-completion/summary" not in {route.path for route in observability}
