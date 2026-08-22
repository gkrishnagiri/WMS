import pytest

from app.models.monitoring import MonAlert, MonAlertEvent, MonTriageCaseAlert


@pytest.mark.anyio
async def test_monitoring_catalog_and_simulations(warehouse_client):
    response = await warehouse_client.get("/api/v1/monitoring/components")
    assert response.status_code == 200 and len(response.json()) == 7
    response = await warehouse_client.get("/api/v1/monitoring/rules")
    assert response.status_code == 200 and len(response.json()) == 10
    response = await warehouse_client.post("/api/v1/monitoring/simulations/api-latency-cascade", json={})
    assert response.status_code == 200 and response.json()["alerts_created"] == 4
    response = await warehouse_client.post("/api/v1/monitoring/simulations/database-degradation", json={})
    assert response.status_code == 200 and response.json()["alerts_created"] == 2
    response = await warehouse_client.post("/api/v1/monitoring/simulations/noisy-alert-storm", json={})
    assert response.status_code == 200 and response.json()["alerts_repeated"] >= 1


@pytest.mark.anyio
async def test_alert_deduplication_and_lifecycle(warehouse_client):
    first = await warehouse_client.post("/api/v1/monitoring/simulations/frontend-error-burst", json={})
    second = await warehouse_client.post("/api/v1/monitoring/simulations/frontend-error-burst", json={})
    assert first.status_code == second.status_code == 200
    alert = second.json()["alerts"][0]
    assert alert["occurrence_count"] == 2
    acknowledged = await warehouse_client.post(f"/api/v1/monitoring/alerts/{alert['id']}/acknowledge")
    assert acknowledged.json()["status"] == "ACKNOWLEDGED"
    suppressed = await warehouse_client.post(f"/api/v1/monitoring/alerts/{alert['id']}/suppress")
    assert suppressed.json()["status"] == "SUPPRESSED"
    resolved = await warehouse_client.post(f"/api/v1/monitoring/alerts/{alert['id']}/resolve")
    assert resolved.json()["status"] == "RESOLVED"


@pytest.mark.anyio
async def test_alert_ticket_and_duplicate_protection(warehouse_client):
    simulation = await warehouse_client.post("/api/v1/monitoring/simulations/api-latency-cascade", json={})
    alert_id = simulation.json()["alerts"][0]["id"]
    first = await warehouse_client.post(f"/api/v1/monitoring/alerts/{alert_id}/create-ticket")
    second = await warehouse_client.post(f"/api/v1/monitoring/alerts/{alert_id}/create-ticket")
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["source"] == "MONITORING"


@pytest.mark.anyio
async def test_triage_case_lifecycle_and_ticket(warehouse_client):
    simulation = await warehouse_client.post("/api/v1/monitoring/simulations/api-latency-cascade", json={})
    ids = [item["id"] for item in simulation.json()["alerts"][:2]]
    created = await warehouse_client.post("/api/v1/monitoring/triage-cases", json={"title": "Noisy warehouse symptoms", "description": "Manual support grouping.", "severity": "HIGH", "suspected_impact": "Allocation may be degraded.", "confidence_level": "LOW", "alert_ids": ids})
    assert created.status_code == 201 and created.json()["alert_count"] == 2
    case_id = created.json()["id"]
    added = await warehouse_client.post(f"/api/v1/monitoring/triage-cases/{case_id}/add-alerts", json={"alert_ids": ids})
    assert added.json()["alert_count"] == 2
    started = await warehouse_client.post(f"/api/v1/monitoring/triage-cases/{case_id}/start-investigation")
    assert started.json()["status"] == "INVESTIGATING"
    ticket = await warehouse_client.post(f"/api/v1/monitoring/triage-cases/{case_id}/create-ticket")
    assert ticket.status_code == 201 and ticket.json()["source_module"] == "MONITORING"
    resolved = await warehouse_client.post(f"/api/v1/monitoring/triage-cases/{case_id}/resolve", json={"analysis_notes": "Symptoms cleared after manual analysis."})
    assert resolved.json()["status"] == "RESOLVED"


@pytest.mark.anyio
async def test_monitoring_summary_and_invalid_transition(warehouse_client):
    simulation = await warehouse_client.post("/api/v1/monitoring/simulations/redis-flapping", json={})
    alert_id = simulation.json()["alerts"][0]["id"]
    assert (await warehouse_client.post(f"/api/v1/monitoring/alerts/{alert_id}/resolve")).status_code == 200
    assert (await warehouse_client.post(f"/api/v1/monitoring/alerts/{alert_id}/acknowledge")).status_code == 409
    summary = await warehouse_client.get("/api/v1/monitoring/summary")
    assert summary.status_code == 200 and "open_alerts" in summary.json()
    alerts = await warehouse_client.get("/api/v1/monitoring/alerts")
    assert alerts.status_code == 200
