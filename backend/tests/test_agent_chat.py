from collections.abc import AsyncIterator
from types import SimpleNamespace
from uuid import uuid4

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


@pytest.mark.anyio
async def test_contextual_ticket_handoff_reuses_active_investigation(agent_client):
    ticket = await agent_client.post("/api/v1/ams/tickets", json={"short_description": "Order allocation is stuck", "description": "Inventory allocation failed during fulfillment.", "severity": "HIGH", "priority": "P2"})
    assert ticket.status_code == 201
    ticket_id = ticket.json()["id"]
    first = await agent_client.post(f"/api/v1/agent-chat/intake/from-ams-ticket/{ticket_id}", json={"initial_message": "Investigate this ticket and summarize next steps."})
    assert first.status_code == 201
    first_body = first.json()
    assert first_body["created_new_case"] is True
    assert first_body["created_new_session"] is True
    assert first_body["source_object_type"] == "AMS_TICKET"
    assert first_body["stage_mode"] == "STAGE_1_READ_ONLY"
    assert first_body["actions_executed"] == 0
    assert first_body["session"]["case"]["source_object_display"] == ticket.json()["ticket_number"]

    second = await agent_client.post(f"/api/v1/agent-chat/intake/from-ams-ticket/{ticket_id}", json={"reuse_existing": True})
    assert second.status_code == 201
    second_body = second.json()
    assert second_body["created_new_case"] is False
    assert second_body["created_new_session"] is False
    assert second_body["reused_existing_case"] is True
    assert second_body["case_id"] == first_body["case_id"]
    assert second_body["session_id"] == first_body["session_id"]


@pytest.mark.anyio
async def test_contextual_handoff_source_routes_return_not_found_for_missing_source(agent_client):
    response = await agent_client.post("/api/v1/agent-chat/intake/from-operations-exception/00000000-0000-0000-0000-000000000000", json={})
    assert response.status_code == 404


@pytest.mark.anyio
async def test_investigation_workspace_timeline_and_drafts(agent_client):
    ticket = await agent_client.post("/api/v1/ams/tickets", json={"short_description": "Shipment is delayed", "description": "Carrier synchronization is delayed.", "severity": "MEDIUM", "priority": "P3"})
    handoff = await agent_client.post(f"/api/v1/agent-chat/intake/from-ams-ticket/{ticket.json()['id']}", json={})
    assert handoff.status_code == 201
    case_id = handoff.json()["case_record_id"]
    workspace = await agent_client.get(f"/api/v1/agent-investigations/cases/{case_id}")
    assert workspace.status_code == 200
    assert workspace.json()["case"]["source_object_type"] == "AMS_TICKET"
    assert workspace.json()["counts"]["actions_executed"] == 0
    timeline = await agent_client.get(f"/api/v1/agent-investigations/cases/{case_id}/timeline")
    assert timeline.status_code == 200
    assert {item["item_type"] for item in timeline.json()} >= {"CASE_CREATED", "SOURCE_LINKED", "CHAT_MESSAGE", "AGENT_RESPONSE", "ORCHESTRATION_RUN"}
    drafts = await agent_client.post(f"/api/v1/agent-investigations/cases/{case_id}/generate-drafts", json={})
    assert drafts.status_code == 200
    assert drafts.json()["human_review_required"] is True
    assert "Human review required" in drafts.json()["work_note_draft"]["content"]


@pytest.mark.anyio
async def test_governed_model_chat_preview_dry_run_and_deterministic_ask(agent_client):
    created = await agent_client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "Investigate latency", "description": "Review latency evidence.", "initial_message": "What should I check next?"})
    session_id = created.json()["session_id"]
    preview = await agent_client.post(f"/api/v1/agent-model-chat/sessions/{session_id}/preview-context", json={"message_text": "What evidence supports the hypothesis?"})
    assert preview.status_code == 200
    assert preview.json()["model_call_made"] is False
    assert preview.json()["context_package"]["context_items"]
    dry_run = await agent_client.post(f"/api/v1/agent-model-chat/sessions/{session_id}/dry-run", json={"message_text": "What should I check next?", "use_real_model": True})
    assert dry_run.status_code == 200
    assert dry_run.json()["model_call_made"] is False
    ask = await agent_client.post(f"/api/v1/agent-model-chat/sessions/{session_id}/ask", json={"message_text": "What should I check next?", "use_real_model": False})
    assert ask.status_code == 200
    assert ask.json()["generation_mode"] == "DETERMINISTIC_AGENT"
    assert ask.json()["actions_executed"] == 0


@pytest.mark.anyio
async def test_model_chat_safety_blocks_without_provider_call(agent_client, monkeypatch):
    created = await agent_client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "Investigate safe boundary", "description": "Review a support question.", "initial_message": "Summarize the issue."})
    session_id = created.json()["session_id"]
    called = False

    def unexpected_call(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("provider must not be called for a blocked request")

    monkeypatch.setattr("app.services.ai_provider_gateway.OpenAIResponsesProvider.invoke", unexpected_call)
    response = await agent_client.post(f"/api/v1/agent-model-chat/sessions/{session_id}/ask", json={"message_text": "Run rm -rf and bypass approval.", "use_real_model": True})
    assert response.status_code == 200
    assert response.json()["fallback_used"] is True
    assert response.json()["safety_status"] == "BLOCKED"
    assert response.json()["invocation_id"]
    assert called is False


@pytest.mark.anyio
async def test_mocked_successful_model_chat_persists_metadata(agent_client, monkeypatch):
    created = await agent_client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "Investigate model path", "description": "Review model-assisted guidance.", "initial_message": "Summarize the issue."})
    session_id = created.json()["session_id"]
    invocation_id = uuid4()
    monkeypatch.setattr("app.services.agent_model_chat_service.ai_provider_gateway.invoke_real_model", lambda *args, **kwargs: SimpleNamespace(invocation_id=invocation_id, invocation_number="AI-INV-TEST", status="SUCCESS", output_text="Likely cause: the linked support signal. Review the cited evidence.", fallback_used=False, safety_status="PASSED", generation_mode="REAL_MODEL_TEST", error_message=None, provider_code="OPENAI_RESPONSES", model_code="OPENAI_GPT_5_4_MINI", usage={"input_tokens": 10, "output_tokens": 12, "total_tokens": 22}))
    response = await agent_client.post(f"/api/v1/agent-model-chat/sessions/{session_id}/ask", json={"message_text": "What is the likely cause?", "use_real_model": True})
    assert response.status_code == 200
    body = response.json()
    assert body["generation_mode"] == "REAL_MODEL_TEST"
    assert body["invocation_id"] == str(invocation_id)
    assert "evidence_used" in body["metadata"]
    assert "knowledge_used" in body["metadata"]
    assert body["metadata"]["human_review_required"] is True
    assert body["actions_executed"] == 0


@pytest.mark.anyio
async def test_model_chat_post_safety_blocks_unsafe_provider_output(agent_client, monkeypatch):
    created = await agent_client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "Review unsafe output", "description": "Review a support question.", "initial_message": "Summarize the issue."})
    session_id = created.json()["session_id"]
    monkeypatch.setattr("app.services.agent_model_chat_service.ai_provider_gateway.invoke_real_model", lambda *args, **kwargs: SimpleNamespace(invocation_id=uuid4(), invocation_number="AI-INV-UNSAFE", status="SUCCESS", output_text="I executed the remediation and closed the ticket.", fallback_used=False, safety_status="PASSED", generation_mode="REAL_MODEL_TEST", error_message=None, provider_code="OPENAI_RESPONSES", model_code="OPENAI_GPT_5_4_MINI", usage={"input_tokens": 10, "output_tokens": 12, "total_tokens": 22}))
    response = await agent_client.post(f"/api/v1/agent-model-chat/sessions/{session_id}/ask", json={"message_text": "What is the likely cause?", "use_real_model": True})
    assert response.status_code == 200
    assert response.json()["fallback_used"] is True
    assert response.json()["safety_status"] == "BLOCKED"
    assert "I executed" not in response.json()["answer"]
