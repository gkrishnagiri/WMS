import pytest


@pytest.mark.anyio
async def test_stack_summary_and_sanitized_config(client):
    summary = await client.get("/api/v1/observability-stack/summary")
    assert summary.status_code == 200
    body = summary.json()
    assert body["service_name"] == "eos-backend"
    assert body["otel_enabled"] is False
    config = await client.get("/api/v1/observability-stack/config")
    assert config.status_code == 200
    assert "password" not in str(config.json()).lower()


@pytest.mark.anyio
async def test_stack_health_tolerates_unavailable_services(client):
    response = await client.get("/api/v1/observability-stack/health")
    assert response.status_code == 200
    assert response.json()["status"] in {"healthy", "degraded"}
    assert len(response.json()["components"]) == 5


@pytest.mark.anyio
async def test_stack_test_actions_are_safe_when_otel_disabled(client):
    response = await client.post("/api/v1/observability-stack/test-all", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["span"]["status"] == "SKIPPED"
    assert body["metric"]["status"] == "SKIPPED"
