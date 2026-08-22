import pytest


@pytest.mark.anyio
async def test_copilot_seed_catalog_and_summary(warehouse_client):
    actions = await warehouse_client.get("/api/v1/copilot/safe-actions")
    assert actions.status_code == 200
    assert len(actions.json()) >= 10
    summary = await warehouse_client.get("/api/v1/copilot/summary")
    assert summary.status_code == 200
    assert summary.json()["safe_actions_enabled"] >= 10


@pytest.mark.anyio
async def test_analyze_batch_run_builds_governed_copilot_artifacts(warehouse_client):
    batch = await warehouse_client.post(
        "/api/v1/batch/simulations/inventory-reconciliation-failure",
        json={"create_exception": True, "create_ticket": True, "create_observability": True},
    )
    assert batch.status_code == 200
    run_id = batch.json()["run"]["id"]
    analyzed = await warehouse_client.post(
        "/api/v1/copilot/analyze",
        json={"entity_type": "BATCH_RUN", "entity_id": run_id, "title": "Analyze failed inventory reconciliation"},
    )
    assert analyzed.status_code == 200
    body = analyzed.json()
    assert body["primary_entity_type"] == "BATCH_RUN"
    assert body["latest_context_snapshot"] is not None
    assert body["recommendations"]
    assert body["latest_action_plan"]["requires_human_approval"] is True
    assert any(message["message_type"] == "INVESTIGATION_CHECKLIST" for message in body["messages"])
    assert any("failed batch step" in recommendation["title"].lower() for recommendation in body["recommendations"])


@pytest.mark.anyio
async def test_copilot_context_for_alert_and_diagnostic(warehouse_client):
    simulation = await warehouse_client.post("/api/v1/observability/simulations/database-degradation", json={})
    trace = await warehouse_client.get(f"/api/v1/observability/traces/{simulation.json()['trace_identifier']}")
    alert_id = simulation.json()["alert_ids"][0]
    diagnostic_id = simulation.json()["diagnostic_case_id"]
    alert_session = await warehouse_client.post(
        "/api/v1/copilot/sessions",
        json={"title": "Review database alert", "description": "Support review", "primary_entity_type": "MONITORING_ALERT", "primary_entity_id": alert_id, "build_context": True, "generate_recommendations": True},
    )
    assert alert_session.status_code == 201
    assert alert_session.json()["latest_context_snapshot"]["raw_context"]["alerts"]
    diagnostic_session = await warehouse_client.post(
        "/api/v1/copilot/sessions",
        json={"title": "Review diagnostic", "description": "Support review", "primary_entity_type": "OBSERVABILITY_DIAGNOSTIC", "primary_entity_id": diagnostic_id},
    )
    assert diagnostic_session.status_code == 201
    built = await warehouse_client.post(f"/api/v1/copilot/sessions/{diagnostic_session.json()['id']}/build-context")
    assert built.status_code == 200
    assert built.json()["raw_context"]["evidence"]
    assert trace.status_code == 200


@pytest.mark.anyio
async def test_recommendation_deduplication_drafts_and_manual_lifecycle(warehouse_client):
    created = await warehouse_client.post("/api/v1/copilot/sessions", json={"title": "Manual support review", "description": "Review a reported issue"})
    session_id = created.json()["id"]
    await warehouse_client.post(f"/api/v1/copilot/sessions/{session_id}/build-context")
    first = await warehouse_client.post(f"/api/v1/copilot/sessions/{session_id}/generate-recommendations")
    second = await warehouse_client.post(f"/api/v1/copilot/sessions/{session_id}/generate-recommendations")
    assert first.status_code == second.status_code == 200
    assert len(first.json()) == len(second.json())
    plan = await warehouse_client.post(f"/api/v1/copilot/sessions/{session_id}/generate-action-plan")
    assert plan.status_code == 200 and plan.json()["status"] == "READY_FOR_REVIEW"
    note = await warehouse_client.post(f"/api/v1/copilot/sessions/{session_id}/generate-work-note")
    update = await warehouse_client.post(f"/api/v1/copilot/sessions/{session_id}/generate-customer-update")
    checklist = await warehouse_client.post(f"/api/v1/copilot/sessions/{session_id}/generate-investigation-checklist")
    assert note.status_code == update.status_code == checklist.status_code == 200
    recommendation_id = first.json()[0]["id"]
    accepted = await warehouse_client.post(f"/api/v1/copilot/recommendations/{recommendation_id}/accept")
    assert accepted.status_code == 200 and accepted.json()["status"] == "ACCEPTED"
    invalid = await warehouse_client.post(f"/api/v1/copilot/recommendations/{recommendation_id}/dismiss")
    assert invalid.status_code == 409
    closed = await warehouse_client.post(f"/api/v1/copilot/sessions/{session_id}/close")
    assert closed.status_code == 200 and closed.json()["status"] == "CLOSED"


@pytest.mark.anyio
async def test_copilot_does_not_execute_support_actions(warehouse_client):
    batch = await warehouse_client.post("/api/v1/batch/simulations/inventory-reconciliation-failure", json={"create_ticket": True})
    ticket_id = batch.json()["ticket_id"]
    before = await warehouse_client.get(f"/api/v1/ams/tickets/{ticket_id}")
    analysis = await warehouse_client.post("/api/v1/copilot/analyze", json={"entity_type": "AMS_TICKET", "entity_id": ticket_id, "title": "Review ticket"})
    assert analysis.status_code == 200
    after = await warehouse_client.get(f"/api/v1/ams/tickets/{ticket_id}")
    assert before.json()["status"] == after.json()["status"] == "NEW"
