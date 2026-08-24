from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.bff.agentic_main import app as agentic_app
from app.bff.business_main import app as business_app
from app.bff.experience_registry import get_experience
from app.bff.observability_main import app as observability_app
from app.bff.operations_main import app as operations_app
from app.bff.simulation_main import app as simulation_app
from app.core.config import Settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app as full_app


class UnavailableDatabase:
    git_commit = "test-commit"

    def check_connection(self) -> bool:
        return False


class UnavailableRedis:
    async def ping(self) -> bool:
        return False


BFF_CASES = [
    (business_app, "business"),
    (operations_app, "operations"),
    (simulation_app, "simulation"),
    (observability_app, "observability"),
    (agentic_app, "agentic"),
]


@pytest.fixture(params=BFF_CASES)
async def bff_client(request) -> AsyncIterator[tuple[AsyncClient, str]]:
    application, code = request.param
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = factory()

    application.state.settings = Settings(_env_file=None)
    application.state.database = UnavailableDatabase()
    application.state.redis = UnavailableRedis()
    application.state.build_timestamp = "test-build"

    def override_get_db():
        yield session

    application.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://testserver") as client:
        yield client, code

    application.dependency_overrides.pop(get_db, None)
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
async def each_bff_client(bff_client) -> AsyncIterator[tuple[AsyncClient, str]]:
    yield bff_client


@pytest.mark.anyio
async def test_platform_metadata_is_available_on_full_backend():
    async with AsyncClient(transport=ASGITransport(app=full_app), base_url="http://testserver") as client:
        experiences = await client.get("/api/v1/platform/experiences")
        current = await client.get("/api/v1/platform/current-experience")
        topology = await client.get("/api/v1/platform/topology")

    assert experiences.status_code == 200
    assert {item["code"] for item in experiences.json()} == {"full", "business", "operations", "simulation", "observability", "agentic"}
    assert current.json()["code"] == "full"
    assert topology.json()["backends"]
    assert topology.json()["observability"]["grafana"] == "http://localhost:3001"


@pytest.mark.anyio
@pytest.mark.parametrize("application,code", [(business_app, "business"), (agentic_app, "agentic")])
async def test_platform_current_experience_is_specific_to_bff(application, code):
    application.state.settings = Settings(_env_file=None)
    async with AsyncClient(transport=ASGITransport(app=application), base_url="http://testserver") as client:
        response = await client.get("/api/v1/platform/current-experience")
    assert response.status_code == 200
    assert response.json()["code"] == code
    assert response.json()["backend_url"] == get_experience(code).backend_url


@pytest.mark.anyio
async def test_bff_health_includes_experience_metadata(each_bff_client):
    client, code = each_bff_client
    response = await client.get("/health")
    assert response.status_code in (200, 503)
    body = response.json()
    assert isinstance(body, dict)
    assert set(("status", "application", "experience", "experience_name", "backend_port", "checks")).issubset(body)
    assert body["status"] in ("healthy", "unhealthy")
    assert body["application"] == "Enterprise Operations Suite"
    assert body["experience"] == code
    assert body["experience_name"] == get_experience(code).name
    assert body["backend_port"] == int(get_experience(code).backend_url.rsplit(":", 1)[1])
    assert body["checks"]["api"] == "healthy"
    assert body["checks"]["database"] in ("healthy", "unhealthy")
    assert body["checks"]["redis"] in ("healthy", "unhealthy")


@pytest.mark.anyio
async def test_each_bff_facade_summary_is_available(each_bff_client):
    client, code = each_bff_client
    path = {
        "business": "/api/v1/business/summary",
        "operations": "/api/v1/operations-console/summary",
        "simulation": "/api/v1/simulation-lab/summary",
        "observability": "/api/v1/observability-control/summary",
        "agentic": "/api/v1/agentic-console/summary",
    }[code]
    response = await client.get(path)
    assert response.status_code == 200
    assert response.json()["experience"] == code


@pytest.mark.anyio
async def test_bff_route_boundaries(each_bff_client):
    client, code = each_bff_client
    allowed, disallowed = {
        "business": ("/api/v1/warehouse/summary", "/api/v1/copilot/summary"),
        "operations": ("/api/v1/operations-console/summary", "/api/v1/warehouse/summary"),
        "simulation": ("/api/v1/simulation-lab/summary", "/api/v1/ai-config/providers"),
        "observability": ("/api/v1/observability-control/summary", "/api/v1/warehouse/summary"),
        "agentic": ("/api/v1/agentic-console/summary", "/api/v1/warehouse/summary"),
    }[code]
    assert (await client.get(allowed)).status_code == 200
    assert (await client.get(disallowed)).status_code == 404


@pytest.mark.anyio
async def test_observability_alert_route_boundaries(each_bff_client):
    client, code = each_bff_client
    response = await client.get("/api/v1/observability-alerts/summary")
    if code == "business":
        assert response.status_code == 404
    elif code in ("operations", "observability"):
        assert response.status_code == 200
    else:
        assert response.status_code == 404


@pytest.mark.anyio
async def test_agent_chat_bff_route_boundaries(each_bff_client):
    client, code = each_bff_client
    summary = await client.get("/api/v1/agent-chat/summary")
    if code in ("business", "operations", "agentic"):
        assert summary.status_code == 200
    else:
        assert summary.status_code == 404
    if code == "business":
        intake = await client.post("/api/v1/agent-chat/intake/user-issue", json={"title": "Need help", "description": "User issue", "initial_message": "My order is stuck."})
        assert intake.status_code == 201
    elif code == "simulation":
        assert (await client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "No access", "description": "Should be blocked", "initial_message": "Investigate this."})).status_code == 404


@pytest.mark.anyio
async def test_contextual_handoff_bff_boundaries(each_bff_client):
    client, code = each_bff_client
    response = await client.post("/api/v1/agent-chat/intake/from-ams-ticket/00000000-0000-0000-0000-000000000000", json={})
    if code in ("operations", "agentic"):
        assert response.status_code == 404  # route is exposed; the source record is absent
    else:
        assert response.status_code == 404


@pytest.mark.anyio
async def test_agent_knowledge_bff_route_boundaries(each_bff_client):
    client, code = each_bff_client
    response = await client.get("/api/v1/agent-knowledge/summary")
    if code in ("business", "operations", "agentic"):
        assert response.status_code == 200
    else:
        assert response.status_code == 404


@pytest.mark.anyio
async def test_bff_cors_preflight_allows_its_frontend(each_bff_client):
    client, code = each_bff_client
    origin = get_experience(code).allowed_origins[0]
    response = await client.options(
        "/api/v1/platform/current-experience",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Request-ID",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin


@pytest.mark.anyio
async def test_full_backend_cors_preflight_allows_full_frontend():
    full_app.state.settings = Settings(_env_file=None)
    async with AsyncClient(transport=ASGITransport(app=full_app), base_url="http://testserver") as client:
        response = await client.options(
            "/api/v1/platform/current-experience",
            headers={
                "Origin": "http://localhost:4001",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:4001"
