import pytest


@pytest.mark.anyio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "application": "Enterprise Operations Suite",
        "platform": "AI-Native AMS Research Platform",
        "status": "running",
    }
    assert response.headers["X-Request-ID"]


@pytest.mark.anyio
async def test_request_id_is_preserved(client):
    response = await client.get("/", headers={"X-Request-ID": "test-request-123"})
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"


@pytest.mark.anyio
async def test_health_shape_and_dependency_status(client):
    response = await client.get("/health")
    assert response.status_code in (200, 503)
    body = response.json()
    assert body["application"] == "Enterprise Operations Suite"
    assert body["checks"]["api"] == "healthy"
    assert body["checks"]["database"] in ("healthy", "unhealthy")
    assert body["checks"]["redis"] in ("healthy", "unhealthy")
    assert body["status"] in ("healthy", "unhealthy")


@pytest.mark.anyio
async def test_version(client):
    response = await client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert body["application"] == "Enterprise Operations Suite"
    assert body["platform"] == "AI-Native AMS Research Platform"
    assert body["version"] == "0.1.0"
    assert body["environment"] == "development"
    assert body["python_version"]
    assert body["git_commit"]
    assert body["build_timestamp"]
