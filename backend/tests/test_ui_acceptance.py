"""Manual UI acceptance catalog, evidence, report, and boundary tests."""

import os
from pathlib import Path

import pytest
from sqlalchemy import select

from app.bff.app_factory import create_bff_app
from app.bff.experience_registry import get_experience
from app.db.session import get_db
from app.main import app
from app.services.ui_acceptance_service import seed_catalog


@pytest.fixture
def seeded_ui_catalog(warehouse_client):
    db = next(app.dependency_overrides[get_db]())
    seed_catalog(db)
    db.commit()
    return warehouse_client


@pytest.mark.anyio
async def test_ui_acceptance_catalog_seed_is_idempotent_and_summary(seeded_ui_catalog):
    summary = (await seeded_ui_catalog.get("/api/v1/ui-acceptance/summary")).json()
    assert summary["enabled_suites"] == 9
    assert summary["total_cases"] >= 8
    assert summary["total_steps"] >= 60
    assert summary["browser_automation_enabled"] is False
    suites = (await seeded_ui_catalog.get("/api/v1/ui-acceptance/suites")).json()
    assert len(suites) == 9
    cases = (await seeded_ui_catalog.get("/api/v1/ui-acceptance/cases")).json()
    assert "STUCK_FULFILLMENT_ORDER_FLOW" in {item["case_code"] for item in cases}
    assert "OPEN_SCENARIO_CATALOG" in {step["step_code"] for item in cases for step in item["steps"]}


@pytest.mark.anyio
async def test_ui_acceptance_run_evidence_and_markdown_report(seeded_ui_catalog):
    started = await seeded_ui_catalog.post("/api/v1/ui-acceptance/runs/start", json={"run_title": "Prompt 28 test", "tester_role": "DEMO_TESTER", "suite_codes": ["EXECUTIVE_DEMO_VALIDATION"]})
    assert started.status_code == 200
    run_id = started.json()["run_id"]
    result = await seeded_ui_catalog.post(f"/api/v1/ui-acceptance/runs/{run_id}/step-results", json={"suite_code": "EXECUTIVE_DEMO_VALIDATION", "case_code": "EXECUTIVE_DASHBOARD_READ_ONLY", "step_code": "OPEN_EXECUTIVE_DEMO", "status": "PASSED", "observed_result": "Dashboard opened.", "evidence_note": "KPI cards visible.", "screenshot_reference": "screenshots/prompt28/executive.png", "defect_note": "", "tested_by_role": "DEMO_TESTER"})
    assert result.status_code == 200
    completed = await seeded_ui_catalog.post(f"/api/v1/ui-acceptance/runs/{run_id}/complete", json={"summary": "Evidence recorded."})
    assert completed.status_code == 200
    assert completed.json()["status"] == "FAILED"  # remaining steps are intentionally untested
    report = await seeded_ui_catalog.get(f"/api/v1/ui-acceptance/runs/{run_id}/report")
    assert report.status_code == 200
    assert report.json()["step_results"][0]["screenshot_reference"].endswith("executive.png")
    markdown = await seeded_ui_catalog.get(f"/api/v1/ui-acceptance/runs/{run_id}/report.md")
    assert markdown.status_code == 200
    assert markdown.headers["content-type"].startswith("text/markdown")
    assert "UI Acceptance Report" in markdown.text


@pytest.mark.anyio
async def test_complete_and_abort_run_and_coverage(seeded_ui_catalog):
    started = await seeded_ui_catalog.post("/api/v1/ui-acceptance/runs/start", json={"run_title": "Abort test", "tester_role": "DEMO_TESTER", "suite_codes": ["GOVERNANCE_BOUNDARY_VALIDATION"]})
    run_id = started.json()["run_id"]
    aborted = await seeded_ui_catalog.post(f"/api/v1/ui-acceptance/runs/{run_id}/abort", json={"summary": "Stopped for test."})
    assert aborted.status_code == 200
    assert aborted.json()["status"] == "ABORTED"
    coverage = await seeded_ui_catalog.get("/api/v1/ui-acceptance/coverage")
    assert coverage.status_code == 200
    assert coverage.json()["classification"].startswith("Manual browser")


def test_ui_acceptance_bff_exposure_boundaries():
    business = {(route.path, tuple(sorted(getattr(route, "methods", set())))) for route in create_bff_app(get_experience("business")).routes}
    operations = {route.path for route in create_bff_app(get_experience("operations")).routes}
    simulation = {route.path for route in create_bff_app(get_experience("simulation")).routes}
    agentic = {route.path for route in create_bff_app(get_experience("agentic")).routes}
    observability = {route.path for route in create_bff_app(get_experience("observability")).routes}
    assert ("/api/v1/ui-acceptance/summary", ("GET",)) in business
    assert ("/api/v1/ui-acceptance/runs/start", ("POST",)) not in business
    assert "/api/v1/ui-acceptance/runs/start" in operations
    assert "/api/v1/ui-acceptance/runs/start" in simulation
    assert "/api/v1/ui-acceptance/runs/start" in agentic
    assert "/api/v1/ui-acceptance/summary" not in observability


def test_acceptance_scripts_are_executable():
    root = Path(__file__).resolve().parents[2]
    for name in ("ui-acceptance-summary.sh", "ui-acceptance-start-run.sh", "ui-acceptance-report.sh"):
        path = root / "scripts" / name
        assert path.exists()
        assert os.access(path, os.X_OK)
