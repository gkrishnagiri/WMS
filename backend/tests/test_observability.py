import pytest


@pytest.mark.anyio
async def test_database_degradation_creates_correlated_evidence(warehouse_client):
    response = await warehouse_client.post("/api/v1/observability/simulations/database-degradation", json={})
    assert response.status_code == 200
    result = response.json()
    assert result["trace_identifier"] and result["diagnostic_number"]
    trace = await warehouse_client.get(f"/api/v1/observability/traces/{result['trace_identifier']}")
    assert len(trace.json()["spans"]) == 4
    assert len(trace.json()["logs"]) == 2
    assert len(trace.json()["metrics"]) == 3
    diagnostic = await warehouse_client.get(f"/api/v1/observability/diagnostic-cases/{result['diagnostic_case_id']}")
    assert diagnostic.json()["confidence_level"] == "HIGH"
    assert len(diagnostic.json()["evidence"]) >= 9


@pytest.mark.anyio
async def test_other_simulations_and_demo_suite(warehouse_client):
    redis = await warehouse_client.post("/api/v1/observability/simulations/redis-cache-failure", json={})
    allocation = await warehouse_client.post("/api/v1/observability/simulations/allocation-failure", json={})
    shipment = await warehouse_client.post("/api/v1/observability/simulations/shipment-integration-failure", json={})
    assert redis.json()["diagnostic_case_id"] and allocation.json()["diagnostic_case_id"] and shipment.json()["diagnostic_case_id"]
    assert (await warehouse_client.get(f"/api/v1/observability/diagnostic-cases/{redis.json()['diagnostic_case_id']}")).json()["confidence_level"] == "MEDIUM"
    allocation_case = (await warehouse_client.get(f"/api/v1/observability/diagnostic-cases/{allocation.json()['diagnostic_case_id']}")).json()
    assert allocation_case["confidence_level"] == "HIGH"
    assert "business rule" in allocation_case["diagnosis_summary"]
    suite = await warehouse_client.post("/api/v1/observability/simulations/observability-demo-suite", json={})
    assert suite.status_code == 200 and suite.json()["traces_created"] == 4


@pytest.mark.anyio
async def test_observability_lists_and_summary(warehouse_client):
    await warehouse_client.post("/api/v1/observability/simulations/database-degradation", json={})
    summary = await warehouse_client.get("/api/v1/observability/summary")
    assert summary.status_code == 200 and summary.json()["traces"] == 1
    assert summary.json()["slow_spans"] >= 2
    assert (await warehouse_client.get("/api/v1/observability/traces")).status_code == 200
    assert len((await warehouse_client.get("/api/v1/observability/log-events")).json()) == 2
    assert len((await warehouse_client.get("/api/v1/observability/metric-samples")).json()) == 3
    assert len((await warehouse_client.get("/api/v1/observability/diagnostic-cases")).json()) == 1


@pytest.mark.anyio
async def test_diagnosis_from_alert_and_triage(warehouse_client):
    simulation = await warehouse_client.post("/api/v1/monitoring/simulations/frontend-error-burst", json={})
    alert_id = simulation.json()["alerts"][0]["id"]
    diagnosis = await warehouse_client.post(f"/api/v1/observability/diagnostics/from-alert/{alert_id}")
    assert diagnosis.status_code == 201 and diagnosis.json()["confidence_level"] == "LOW"
    noisy = await warehouse_client.post("/api/v1/monitoring/simulations/api-latency-cascade", json={})
    alerts = [item["id"] for item in noisy.json()["alerts"][:2]]
    triage = await warehouse_client.post("/api/v1/monitoring/triage-cases", json={"title": "Manual alert grouping", "description": "Support triage.", "severity": "HIGH", "suspected_impact": "API degraded.", "alert_ids": alerts})
    from_triage = await warehouse_client.post(f"/api/v1/observability/diagnostics/from-triage-case/{triage.json()['id']}")
    assert from_triage.status_code == 201 and from_triage.json()["linked_triage_case_id"] == triage.json()["id"]


@pytest.mark.anyio
async def test_diagnostic_ticket_linking_idempotency_and_resolution(warehouse_client):
    simulation = await warehouse_client.post("/api/v1/observability/simulations/database-degradation", json={})
    diagnostic_id = simulation.json()["diagnostic_case_id"]
    first = await warehouse_client.post(f"/api/v1/observability/diagnostic-cases/{diagnostic_id}/link-ticket", json={})
    second = await warehouse_client.post(f"/api/v1/observability/diagnostic-cases/{diagnostic_id}/link-ticket", json={})
    assert first.status_code == second.status_code == 200
    assert first.json()["linked_ticket_id"] == second.json()["linked_ticket_id"]
    ticket_id = first.json()["linked_ticket_id"]
    ticket = await warehouse_client.get(f"/api/v1/ams/tickets/{ticket_id}")
    assert ticket.json()["source"] == "OBSERVABILITY"
    resolved = await warehouse_client.post(f"/api/v1/observability/diagnostic-cases/{diagnostic_id}/resolve", json={"resolution_notes": "Database response time returned to normal."})
    assert resolved.json()["status"] == "RESOLVED"
    invalid = await warehouse_client.post(f"/api/v1/observability/diagnostic-cases/{diagnostic_id}/resolve", json={"resolution_notes": "Again"})
    assert invalid.status_code == 409


@pytest.mark.anyio
async def test_diagnosis_from_ticket(warehouse_client):
    simulation = await warehouse_client.post("/api/v1/observability/simulations/redis-cache-failure", json={"create_ticket": True})
    ticket_id = simulation.json()["ticket_id"]
    response = await warehouse_client.post(f"/api/v1/observability/diagnostics/from-ticket/{ticket_id}")
    assert response.status_code == 201
    assert response.json()["linked_ticket_id"] == ticket_id
