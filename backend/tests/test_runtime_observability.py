from collections.abc import AsyncIterator

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.main import app
from app.models.observability import ObsLogEvent, ObsMetricSample, ObsSpan, ObsTrace


class _RuntimeDatabase:
    git_commit = "runtime-test"

    def __init__(self, factory):
        self.session_factory = factory

    def check_connection(self) -> bool:
        return True


@pytest.fixture
async def runtime_client(client: AsyncClient) -> AsyncIterator[AsyncClient]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    app.state.database = _RuntimeDatabase(factory)
    app.state.runtime_observability_session_factory = factory
    try:
        yield client
    finally:
        app.state.runtime_observability_session_factory = None
        engine.dispose()


@pytest.mark.anyio
async def test_runtime_middleware_adds_headers_and_records_request(runtime_client: AsyncClient):
    response = await runtime_client.get(
        "/",
        headers={"X-Request-ID": "req-runtime-test", "X-Correlation-ID": "corr-runtime-test", "traceparent": "00-test"},
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-runtime-test"
    assert response.headers["X-Correlation-ID"] == "corr-runtime-test"
    runtime_trace_id = response.headers["X-EOS-Runtime-Trace-ID"]

    with app.state.database.session_factory() as db:
        trace = db.scalar(select(ObsTrace).where(ObsTrace.trace_id == runtime_trace_id))
        assert trace is not None
        assert trace.status == "SUCCESS"
        assert len(db.scalars(select(ObsSpan).where(ObsSpan.trace_id == trace.id)).all()) == 1
        assert len(db.scalars(select(ObsLogEvent).where(ObsLogEvent.trace_id == trace.id)).all()) == 2
        assert len(db.scalars(select(ObsMetricSample).where(ObsMetricSample.trace_id == trace.id)).all()) == 2

    detail = await runtime_client.get(f"/api/v1/runtime-observability/traces/{runtime_trace_id}")
    assert detail.status_code == 200
    assert detail.json()["request_id"] == "req-runtime-test"
    assert detail.json()["correlation_id"] == "corr-runtime-test"
    assert detail.json()["spans"] and detail.json()["logs"] and detail.json()["metrics"]


@pytest.mark.anyio
async def test_runtime_read_apis_and_excluded_docs_path(runtime_client: AsyncClient):
    before = await runtime_client.get("/api/v1/runtime-observability/summary")
    assert before.status_code == 200
    docs = await runtime_client.get("/docs")
    assert docs.status_code == 200
    after = await runtime_client.get("/api/v1/runtime-observability/summary")
    assert after.status_code == 200
    assert after.json()["runtime_traces"] >= before.json()["runtime_traces"]
    assert (await runtime_client.get("/api/v1/runtime-observability/traces")).status_code == 200
    assert (await runtime_client.get("/api/v1/runtime-observability/logs")).status_code == 200
    assert (await runtime_client.get("/api/v1/runtime-observability/metrics")).status_code == 200


@pytest.mark.anyio
async def test_backend_health_probe_records_probe_telemetry(runtime_client: AsyncClient):
    response = await runtime_client.post("/api/v1/runtime-observability/probes/backend-health", json={})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "DEGRADED"
    assert body["database_status"] == "healthy"
    assert body["redis_status"] == "unhealthy"
    detail = await runtime_client.get(f"/api/v1/runtime-observability/traces/{body['trace_identifier']}")
    assert detail.status_code == 200
    assert {span["span_name"] for span in detail.json()["spans"]} == {"Backend probe request", "PostgreSQL connectivity check", "Redis connectivity check"}
    assert len(detail.json()["logs"]) == 4
    assert len(detail.json()["metrics"]) == 3


@pytest.mark.anyio
async def test_runtime_telemetry_failure_does_not_break_request(runtime_client: AsyncClient, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("telemetry unavailable")

    monkeypatch.setattr("app.services.runtime_observability_service.record_http_request_trace", fail)
    response = await runtime_client.get("/")
    assert response.status_code == 200
