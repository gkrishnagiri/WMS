from datetime import datetime, timezone

import pytest

from app.schemas.demo_control import DemoReadinessItem, DemoReadinessResponse
from app.services import demo_control_service


@pytest.fixture
def demo_readiness(monkeypatch):
    value = DemoReadinessResponse(
        overall_status="HEALTHY",
        checked_at=datetime.now(timezone.utc),
        items=[DemoReadinessItem(name="Test component", kind="test", url="http://test", expected_status=200, actual_status=200, healthy=True, message="reachable")],
    )
    monkeypatch.setattr(demo_control_service, "readiness", lambda: value)
    return value


@pytest.mark.anyio
async def test_demo_control_read_only_endpoints(client, demo_readiness):
    summary = await client.get("/api/v1/demo-control/summary")
    components = await client.get("/api/v1/demo-control/components")
    urls = await client.get("/api/v1/demo-control/urls")
    readiness = await client.get("/api/v1/demo-control/readiness")

    assert summary.status_code == 200
    assert summary.json()["mode"] == "local-demo"
    assert summary.json()["summary"] == {"frontends": 6, "backends": 6, "infrastructure_components": 7}
    assert len(summary.json()["experiences"]) == 6
    assert components.status_code == 200
    assert components.json()["overall_status"] == "HEALTHY"
    assert urls.status_code == 200
    assert urls.json()["observability"]["grafana"] == "http://localhost:3001"
    assert readiness.status_code == 200
    assert readiness.json()["items"][0]["healthy"] is True
