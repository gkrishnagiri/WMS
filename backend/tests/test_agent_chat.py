from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture
async def agent_client() -> AsyncIterator[AsyncClient]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autoflush=False, autocommit=False)()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.pop(get_db, None)
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.mark.anyio
async def test_engineer_intake_creates_guidance_run_evidence_and_disabled_proposal(agent_client):
    response = await agent_client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "Investigate batch failure", "description": "Review the recent batch failure.", "initial_message": "Why did this batch fail and what should I check next?"})
    assert response.status_code == 201
    body = response.json()
    assert body["case"]["stage_mode"] == "STAGE_1_READ_ONLY"
    assert len(body["messages"]) == 2
    assert body["messages"][-1]["generation_mode"] == "DETERMINISTIC_AGENT"
    assert "What I Cannot Do Yet" in body["messages"][-1]["message_text"]
    assert len(body["orchestration_runs"]) == 1
    assert body["orchestration_runs"][0]["actions_executed"] == 0
    assert body["action_proposals"][0]["execution_status"] == "DISABLED_IN_STAGE_1"


@pytest.mark.anyio
async def test_send_message_and_close_session(agent_client):
    created = await agent_client.post("/api/v1/agent-chat/intake/user-issue", json={"title": "Order is stuck", "description": "The order cannot progress.", "initial_message": "My order is stuck. What should I check?"})
    session_id = created.json()["id"]
    sent = await agent_client.post(f"/api/v1/agent-chat/sessions/{session_id}/messages", json={"message_text": "The issue is still happening."})
    assert sent.status_code == 200
    assert len(sent.json()["messages"]) == 4
    closed = await agent_client.post(f"/api/v1/agent-chat/sessions/{session_id}/close")
    assert closed.status_code == 200
    assert closed.json()["status"] == "CLOSED"
    assert closed.json()["case"]["status"] == "CLOSED"


@pytest.mark.anyio
async def test_agent_real_model_request_falls_back_safely_and_is_audited(agent_client):
    created = await agent_client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "Investigate an order issue", "description": "Review the issue without changing data.", "initial_message": "The order is slow; what should I check?"})
    session_id = created.json()["id"]
    sent = await agent_client.post(f"/api/v1/agent-chat/sessions/{session_id}/messages", json={"message_text": "Use the governed real model if available.", "use_real_model": True})
    assert sent.status_code == 200
    agent_message = sent.json()["messages"][-1]
    assert agent_message["generation_mode"] == "FALLBACK_DETERMINISTIC"
    assert agent_message["metadata_json"]["ai_invocation_id"]
    assert sent.json()["orchestration_runs"][-1]["actions_executed"] == 0


@pytest.mark.anyio
async def test_agent_summary_and_simulation_bff_boundary(agent_client):
    summary = await agent_client.get("/api/v1/agent-chat/summary")
    assert summary.status_code == 200
    assert summary.json()["stage_mode"] == "STAGE_1_READ_ONLY"
