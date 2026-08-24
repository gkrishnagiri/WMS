from collections.abc import AsyncIterator
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.observability import ObsMetricSample
from app.models.observability_alerts import ObsAlertRule
from app.db.seed_observability_alerts import RULES, seed_rules


@pytest.fixture
async def alert_client() -> AsyncIterator[tuple[AsyncClient, object]]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = factory()
    rule = ObsAlertRule(rule_code="TEST_API_ERRORS", name="Test API errors", description="Test alert", signal_type="METRIC", source_system="EOS_RUNTIME", metric_name="api_error_count", condition_operator="GT", threshold_value=1, severity="HIGH", enabled=True, deduplication_key_template="TEST_API_ERRORS:{source}", cooldown_minutes=30, evaluation_window_minutes=15, target_experience="operations", recommended_owner="TEST", create_ticket_by_default=False)
    session.add(rule)
    session.add(ObsMetricSample(sample_number="TEST-METRIC-001", metric_name="api_error_count", metric_value=3, metric_unit="count", component_code="EOS-BACKEND-API", recorded_at=datetime.now(timezone.utc), attributes={}))
    session.commit()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client, rule.id
    app.dependency_overrides.pop(get_db, None)
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.anyio
async def test_alert_rules_evaluate_and_deduplicate(alert_client):
    client, rule_id = alert_client
    assert (await client.get("/api/v1/observability-alerts/rules")).status_code == 200
    first = await client.post(f"/api/v1/observability-alerts/evaluate/{rule_id}", json={"trigger_source": "MANUAL"})
    assert first.status_code == 200
    assert first.json()["events_created"] == 1
    second = await client.post(f"/api/v1/observability-alerts/evaluate/{rule_id}", json={"trigger_source": "MANUAL"})
    assert second.status_code == 200
    assert second.json()["events_suppressed"] == 1
    events = (await client.get("/api/v1/observability-alerts/events")).json()
    assert len(events) == 1
    assert events[0]["suppressed_count"] == 1


@pytest.mark.anyio
async def test_alert_event_lifecycle_and_duplicate_ticket_prevention(alert_client):
    client, rule_id = alert_client
    await client.post(f"/api/v1/observability-alerts/evaluate/{rule_id}", json={})
    event = (await client.get("/api/v1/observability-alerts/events")).json()[0]
    acknowledged = await client.post(f"/api/v1/observability-alerts/events/{event['id']}/acknowledge")
    assert acknowledged.status_code == 200
    ticket = await client.post(f"/api/v1/observability-alerts/events/{event['id']}/create-ticket")
    assert ticket.status_code == 200
    duplicate = await client.post(f"/api/v1/observability-alerts/events/{event['id']}/create-ticket")
    assert duplicate.status_code == 200
    assert duplicate.json()["id"] == ticket.json()["id"]
    resolved = await client.post(f"/api/v1/observability-alerts/events/{event['id']}/resolve")
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "RESOLVED"


@pytest.mark.anyio
async def test_alert_summary_is_database_derived(alert_client):
    client, _ = alert_client
    summary = await client.get("/api/v1/observability-alerts/summary")
    assert summary.status_code == 200
    assert summary.json()["rules"] == 1


def test_alert_seed_is_idempotent():
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    seed_rules(session)
    session.commit()
    seed_rules(session)
    session.commit()
    assert len(session.scalars(select(ObsAlertRule)).all()) == len(RULES)
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()
