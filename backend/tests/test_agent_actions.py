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
async def action_client() -> AsyncIterator[AsyncClient]:
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
async def test_catalog_proposals_approval_execution_audit_and_duplicate_guard(action_client):
    created = await action_client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "Investigate ticket", "description": "A support ticket needs review.", "initial_message": "Investigate this ticket and propose safe next actions."})
    assert created.status_code == 201
    case_id = created.json()["case"]["id"]

    catalog = await action_client.get("/api/v1/agent-actions/catalog")
    assert catalog.status_code == 200
    assert {item["code"] for item in catalog.json()} >= {"CREATE_AMS_WORK_NOTE_DRAFT", "ADD_INTERNAL_CASE_NOTE", "CREATE_NEXT_STEPS_CHECKLIST"}
    proposals = await action_client.get(f"/api/v1/agent-actions/proposals?case_id={case_id}")
    assert proposals.status_code == 200
    work_note = next(item for item in proposals.json() if item["safe_action_code"] == "CREATE_AMS_WORK_NOTE_DRAFT")

    dry_run = await action_client.post(f"/api/v1/agent-actions/proposals/{work_note['proposal_id']}/dry-run", json={"requested_by_role": "SERVICE_ENGINEER"})
    assert dry_run.status_code == 200
    assert dry_run.json()["dry_run"] is True
    assert dry_run.json()["executable"] is False
    unchanged = (await action_client.get(f"/api/v1/agent-actions/proposals/{work_note['proposal_id']}")) .json()
    assert unchanged["execution_status"] == "PENDING_APPROVAL"

    blocked = await action_client.post(f"/api/v1/agent-actions/proposals/{work_note['proposal_id']}/execute", json={"requested_by_role": "SERVICE_ENGINEER"})
    assert blocked.status_code == 409
    approved = await action_client.post(f"/api/v1/agent-actions/proposals/{work_note['proposal_id']}/approve", json={"approved_by_role": "SERVICE_ENGINEER", "approval_comment": "Evidence reviewed."})
    assert approved.status_code == 200
    assert approved.json()["proposal"]["approval_status"] == "APPROVED"
    executed = await action_client.post(f"/api/v1/agent-actions/proposals/{work_note['proposal_id']}/execute", json={"requested_by_role": "SERVICE_ENGINEER"})
    assert executed.status_code == 200
    assert executed.json()["execution"]["status"] == "SUCCEEDED"
    assert executed.json()["execution"]["result_json"]["external_send"] is False
    duplicate = await action_client.post(f"/api/v1/agent-actions/proposals/{work_note['proposal_id']}/execute", json={"requested_by_role": "SERVICE_ENGINEER"})
    assert duplicate.status_code == 200
    assert duplicate.json()["duplicate_prevented"] is True
    executions = await action_client.get(f"/api/v1/agent-actions/executions?case_id={case_id}")
    assert len(executions.json()) == 1
    timeline = await action_client.get(f"/api/v1/agent-investigations/cases/{case_id}/timeline")
    assert {item["item_type"] for item in timeline.json()} >= {"ACTION_PROPOSED", "ACTION_DRY_RUN", "ACTION_APPROVED", "ACTION_EXECUTION_STARTED", "ACTION_EXECUTION_SUCCEEDED"}
    assert any(message["sender_type"] == "SYSTEM" and "approved" in message["message_text"] for message in (await action_client.get(f"/api/v1/agent-chat/sessions/{created.json()['id']}/messages")).json())


@pytest.mark.anyio
async def test_rejected_and_unapproved_actions_cannot_execute(action_client):
    created = await action_client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "Investigate batch failure", "description": "A batch failed.", "initial_message": "Investigate the batch failure."})
    proposal = (await action_client.get(f"/api/v1/agent-actions/proposals?case_id={created.json()['case']['id']}")) .json()[1]
    rejected = await action_client.post(f"/api/v1/agent-actions/proposals/{proposal['proposal_id']}/reject", json={"rejected_by_role": "SERVICE_ENGINEER", "rejection_comment": "Keep this as guidance only."})
    assert rejected.status_code == 200
    attempt = await action_client.post(f"/api/v1/agent-actions/proposals/{proposal['proposal_id']}/execute", json={"requested_by_role": "SERVICE_ENGINEER"})
    assert attempt.status_code == 409


@pytest.mark.anyio
async def test_customer_checklist_and_internal_note_handlers_are_local(action_client):
    user = await action_client.post("/api/v1/agent-chat/intake/user-issue", json={"title": "Order is stuck", "description": "A customer cannot see progress.", "initial_message": "My order is stuck and needs support."})
    user_case = user.json()["case"]["id"]
    user_proposals = (await action_client.get(f"/api/v1/agent-actions/proposals?case_id={user_case}")).json()
    for code in ("CREATE_CUSTOMER_UPDATE_DRAFT", "ADD_INTERNAL_CASE_NOTE"):
        proposal = next(item for item in user_proposals if item["safe_action_code"] == code)
        await action_client.post(f"/api/v1/agent-actions/proposals/{proposal['proposal_id']}/approve", json={"approved_by_role": "SERVICE_ENGINEER"})
        result = await action_client.post(f"/api/v1/agent-actions/proposals/{proposal['proposal_id']}/execute", json={"requested_by_role": "SERVICE_ENGINEER"})
        assert result.status_code == 200
        assert result.json()["execution"]["status"] == "SUCCEEDED"

    batch = await action_client.post("/api/v1/agent-chat/intake/engineer-investigation", json={"title": "Batch failed", "description": "A batch failed.", "initial_message": "Investigate the batch failure."})
    batch_case = batch.json()["case"]["id"]
    checklist = next(item for item in (await action_client.get(f"/api/v1/agent-actions/proposals?case_id={batch_case}")).json() if item["safe_action_code"] == "CREATE_NEXT_STEPS_CHECKLIST")
    await action_client.post(f"/api/v1/agent-actions/proposals/{checklist['proposal_id']}/approve", json={"approved_by_role": "SERVICE_ENGINEER"})
    result = await action_client.post(f"/api/v1/agent-actions/proposals/{checklist['proposal_id']}/execute", json={"requested_by_role": "SERVICE_ENGINEER"})
    assert result.json()["execution"]["status"] == "SUCCEEDED"
