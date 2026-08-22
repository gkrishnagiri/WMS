import pytest


@pytest.mark.anyio
async def test_batch_catalog_and_job_detail(warehouse_client):
    jobs = await warehouse_client.get("/api/v1/batch/jobs")
    assert jobs.status_code == 200 and len(jobs.json()) == 5
    assert all(item["step_count"] >= 4 for item in jobs.json())
    detail = await warehouse_client.get(f"/api/v1/batch/jobs/{jobs.json()[0]['job_code']}")
    assert detail.status_code == 200 and detail.json()["steps"]


@pytest.mark.anyio
async def test_success_batch_run_has_steps_and_events(warehouse_client):
    response = await warehouse_client.post("/api/v1/batch/simulations/inventory-reconciliation-success", json={})
    assert response.status_code == 200
    result = response.json()
    assert result["run"]["status"] == "SUCCESS"
    assert len(result["run"]["steps"]) == 5
    assert any(event["event_type"] == "BATCH_RUN_COMPLETED" for event in result["run"]["events"])


@pytest.mark.anyio
async def test_failed_batch_creates_exception_ticket_and_diagnostic(warehouse_client):
    response = await warehouse_client.post("/api/v1/batch/simulations/inventory-reconciliation-failure", json={"create_exception": True, "create_ticket": True, "create_observability": True})
    assert response.status_code == 200
    result = response.json()
    assert result["run"]["status"] == "FAILED"
    assert result["run"]["failure_type"] == "DATA_VALIDATION_ERROR"
    assert any(step["status"] == "FAILED" for step in result["run"]["steps"])
    assert result["exception_id"] and result["ticket_id"] and result["diagnostic_case_id"]
    assert result["run"]["linked_ticket_number"]
    duplicate = await warehouse_client.post(f"/api/v1/batch/runs/{result['run']['id']}/create-ticket")
    assert duplicate.status_code == 200 and duplicate.json()["id"] == result["ticket_id"]


@pytest.mark.anyio
async def test_batch_failure_scenarios_and_suite(warehouse_client):
    order = await warehouse_client.post("/api/v1/batch/simulations/order-release-validation-failure", json={})
    shipment = await warehouse_client.post("/api/v1/batch/simulations/shipment-sync-timeout", json={})
    partial = await warehouse_client.post("/api/v1/batch/simulations/low-stock-notification-partial-failure", json={})
    assert order.json()["run"]["status"] == "FAILED"
    assert shipment.json()["run"]["status"] == "TIMEOUT"
    assert partial.json()["run"]["status"] == "PARTIAL_SUCCESS"
    suite = await warehouse_client.post("/api/v1/batch/simulations/batch-failure-suite", json={"create_exception": True, "create_ticket": True, "create_observability": True})
    assert suite.status_code == 200
    assert suite.json()["runs_created"] == 5
    assert suite.json()["successful_runs"] >= 1 and suite.json()["failed_runs"] >= 2


@pytest.mark.anyio
async def test_batch_run_endpoints_and_summary(warehouse_client):
    created = await warehouse_client.post("/api/v1/batch/simulations/shipment-sync-timeout", json={})
    run = created.json()["run"]
    by_number = await warehouse_client.get(f"/api/v1/batch/runs/{run['run_number']}")
    assert by_number.status_code == 200 and by_number.json()["run_number"] == run["run_number"]
    events = await warehouse_client.get(f"/api/v1/batch/runs/{run['run_number']}/events")
    assert events.status_code == 200 and events.json()
    exception = await warehouse_client.post(f"/api/v1/batch/runs/{run['id']}/create-exception")
    assert exception.status_code == 200 and exception.json()["source_module"] == "BATCH_OPERATIONS"
    ticket = await warehouse_client.post(f"/api/v1/batch/runs/{run['id']}/create-ticket")
    assert ticket.status_code == 200 and ticket.json()["source"] == "BATCH"
    diagnostic = await warehouse_client.post(f"/api/v1/batch/runs/{run['id']}/create-diagnostic")
    assert diagnostic.status_code == 200
    summary = await warehouse_client.get("/api/v1/batch/summary")
    assert summary.status_code == 200 and summary.json()["runs_total"] == 1
