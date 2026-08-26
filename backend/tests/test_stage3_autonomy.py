import pytest


@pytest.mark.anyio
async def test_stage3_status_is_disabled_by_default(warehouse_client):
    response = await warehouse_client.get("/api/v1/stage3-autonomy/status")
    assert response.status_code == 200
    body = response.json()
    assert body["sandbox_enabled"] is False
    assert body["safe_to_execute"] is False
    assert body["production_autonomous_remediation"] is False


@pytest.mark.anyio
async def test_stage3_profiles_and_dry_run_are_local_only(warehouse_client):
    profiles = await warehouse_client.get("/api/v1/stage3-autonomy/profiles")
    assert profiles.status_code == 200
    assert {item["profile_code"] for item in profiles.json()} >= {"DRY_RUN_ONLY", "LOCAL_DRAFT_AUTONOMY", "LOCAL_ACKNOWLEDGEMENT_AUTONOMY", "HUMAN_HANDOFF_ON_UNCERTAINTY"}
    denied = await warehouse_client.post("/api/v1/stage3-autonomy/runs", json={"profile_code": "DRY_RUN_ONLY"})
    assert denied.status_code == 400
    created = await warehouse_client.post("/api/v1/stage3-autonomy/runs", json={"profile_code": "DRY_RUN_ONLY", "created_by_role": "TESTER", "max_steps": 1, "max_estimated_cost": 0.1, "acknowledge_sandbox_only": True})
    assert created.status_code == 200
    run_id = created.json()["run_id"]
    dry_run = await warehouse_client.post(f"/api/v1/stage3-autonomy/runs/{run_id}/dry-run", json={"requested_by_role": "TESTER"})
    assert dry_run.status_code == 200
    body = dry_run.json()
    assert body["run"]["dry_run_completed"] is True
    assert body["run"]["status"] == "DRY_RUN_COMPLETED"
    assert body["run"]["steps"] == []
    assert "external" in body["what_will_not_be_done"]


@pytest.mark.anyio
async def test_stage3_execution_is_blocked_by_default_and_kill_switch_is_persistent(warehouse_client):
    created = await warehouse_client.post("/api/v1/stage3-autonomy/runs", json={"profile_code": "DRY_RUN_ONLY", "created_by_role": "TESTER", "max_steps": 1, "max_estimated_cost": 0.1, "acknowledge_sandbox_only": True})
    run_id = created.json()["run_id"]
    await warehouse_client.post(f"/api/v1/stage3-autonomy/runs/{run_id}/dry-run", json={})
    started = await warehouse_client.post(f"/api/v1/stage3-autonomy/runs/{run_id}/start", json={"acknowledge_autonomous_sandbox": True, "acknowledge_no_external_systems": True, "acknowledge_cost": True})
    assert started.status_code == 200
    assert started.json()["status"] == "BLOCKED_BY_POLICY"
    enabled = await warehouse_client.post("/api/v1/stage3-autonomy/kill-switch", json={"enabled": True, "requested_by_role": "TESTER", "reason": "test"})
    assert enabled.status_code == 200
    assert (await warehouse_client.get("/api/v1/stage3-autonomy/status")).json()["kill_switch_enabled"] is True
    disabled = await warehouse_client.post("/api/v1/stage3-autonomy/kill-switch", json={"enabled": False, "requested_by_role": "TESTER", "reason": "test cleanup"})
    assert disabled.status_code == 200
