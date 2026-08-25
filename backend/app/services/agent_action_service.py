"""Stage 2 approval-gated, deterministic, local-only agent actions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agent_chat import AgentActionAuditEvent, AgentActionExecution, AgentActionProposal, AgentCase, AgentChatMessage, AgentChatSession, AgentOrchestrationRun
from app.models.ams import AmsTicket, AmsTicketEvent
from app.models.monitoring import MonAlert, MonTriageCase
from app.models.observability_alerts import ObsAlertEvent
from app.models.operations import OpsException
from app.schemas.agent_actions import ActionApprovalRequest, ActionExecutionRequest, ActionRejectionRequest, AgentActionExecutionResponse, AgentActionProposalResponse


STAGE_2 = "STAGE_2_APPROVAL_GATED"
EXECUTION_MODE = STAGE_2
SAFETY_NOTES = "Predefined local EOS demo action only. No shell commands, external API calls, ServiceNow updates, customer sends, or autonomous remediation."


class AgentActionError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next(db: Session, model: Any, field: Any, prefix: str) -> str:
    current = db.scalar(select(func.max(field)).where(field.like(f"{prefix}%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            pass
    return f"{prefix}{sequence:04d}"


_CATALOG: tuple[dict[str, Any], ...] = (
    {"code": "CREATE_AMS_WORK_NOTE_DRAFT", "name": "Create AMS work-note draft", "description": "Create a deterministic local work-note draft for human review; never posts to an external AMS.", "risk_level": "LOW", "handler": "local_draft"},
    {"code": "ADD_INTERNAL_CASE_NOTE", "name": "Add internal case note", "description": "Append a system note to the linked local EOS agent chat case.", "risk_level": "LOW", "handler": "internal_note"},
    {"code": "UPDATE_AGENT_CASE_STATUS", "name": "Update agent case status", "description": "Update only the local EOS agent investigation case to an allowed status.", "risk_level": "LOW", "handler": "case_status"},
    {"code": "MARK_AGENT_PROPOSAL_REVIEWED", "name": "Mark proposal reviewed", "description": "Record that a proposal was reviewed; this does not change business or infrastructure state.", "risk_level": "LOW", "handler": "mark_reviewed"},
    {"code": "CREATE_NEXT_STEPS_CHECKLIST", "name": "Create next-steps checklist", "description": "Create a deterministic local checklist for human follow-up.", "risk_level": "LOW", "handler": "local_draft"},
    {"code": "LINK_EVIDENCE_TO_CASE", "name": "Link evidence to case", "description": "Return the already-linked local evidence references for the investigation.", "risk_level": "LOW", "handler": "link_evidence"},
    {"code": "CREATE_FOLLOW_UP_TASK_DRAFT", "name": "Create follow-up task draft", "description": "Create a local draft of a follow-up task; no task is dispatched externally.", "risk_level": "LOW", "handler": "local_draft"},
    {"code": "CREATE_CUSTOMER_UPDATE_DRAFT", "name": "Create customer-update draft", "description": "Create a deterministic customer-update draft for human review; never sends it.", "risk_level": "LOW", "handler": "local_draft"},
    {"code": "ACKNOWLEDGE_OBSERVABILITY_ALERT", "name": "Acknowledge observability alert", "description": "Acknowledge a linked local EOS observability alert without resolving it.", "risk_level": "LOW", "handler": "ack_observability"},
    {"code": "ACKNOWLEDGE_MONITORING_ALERT", "name": "Acknowledge monitoring alert", "description": "Acknowledge a linked local EOS monitoring alert without resolving it.", "risk_level": "LOW", "handler": "ack_monitoring"},
    {"code": "ACKNOWLEDGE_OPERATIONS_EXCEPTION", "name": "Acknowledge operations exception", "description": "Acknowledge a linked local EOS operations exception without closing it.", "risk_level": "LOW", "handler": "ack_exception"},
    # Kept as a compatibility proposal from Stage 1. It becomes executable only
    # after the same explicit approval gate as every other local action.
    {"code": "REVIEW_EVIDENCE", "name": "Review and document support evidence", "description": "Record a human review of the gathered support evidence.", "risk_level": "LOW", "handler": "mark_reviewed"},
)
CATALOG_BY_CODE = {item["code"]: item for item in _CATALOG}


def catalog() -> list[dict[str, Any]]:
    return [{**item, "handler": None, "enabled": True, "execution_mode": EXECUTION_MODE, "safety_notes": SAFETY_NOTES} for item in _CATALOG]


def _proposal_dict(row: AgentActionProposal) -> dict[str, Any]:
    return AgentActionProposalResponse.model_validate(row, from_attributes=True).model_dump(mode="json")


def _execution_dict(row: AgentActionExecution) -> dict[str, Any]:
    return AgentActionExecutionResponse.model_validate(row, from_attributes=True).model_dump(mode="json")


def _proposal(db: Session, proposal_id: str) -> AgentActionProposal:
    row = db.scalar(select(AgentActionProposal).where(AgentActionProposal.proposal_id == proposal_id))
    if row is None:
        raise AgentActionError("Agent action proposal not found.", 404)
    return row


def _audit(db: Session, proposal: AgentActionProposal, event_type: str, actor_role: str, comment: str | None = None, metadata: dict[str, Any] | None = None) -> None:
    db.add(AgentActionAuditEvent(event_id=_next(db, AgentActionAuditEvent, AgentActionAuditEvent.event_id, "AGENT-AUDIT-"), proposal_id=proposal.id, case_id=proposal.case_id, run_id=proposal.run_id, event_type=event_type, actor_role=actor_role, comment=comment, metadata_json=metadata, created_at=_now()))


def _system_message(db: Session, case: AgentCase, text: str) -> None:
    session = db.scalar(select(AgentChatSession).where(AgentChatSession.case_id == case.id, AgentChatSession.status == "ACTIVE").order_by(AgentChatSession.updated_at.desc()).limit(1))
    if session is None:
        return
    now = _now()
    db.add(AgentChatMessage(message_id=_next(db, AgentChatMessage, AgentChatMessage.message_id, "AGENT-MSG-"), session_id=session.id, sender_type="SYSTEM", sender_role="SYSTEM", message_text=text[:6000], message_format="PLAIN_TEXT", generation_mode="ACTION_AUDIT", safety_status="SAFE", created_at=now, metadata_json={"stage_mode": STAGE_2}))
    session.updated_at = now
    # A single execution can append both a handler note and an execution
    # result message. Flush here so the deterministic message sequence cannot
    # reuse the same identifier within one transaction.
    db.flush()


def _specs_for_case(case: AgentCase) -> list[str]:
    return {
        "AMS_TICKET": ["CREATE_AMS_WORK_NOTE_DRAFT", "ADD_INTERNAL_CASE_NOTE", "CREATE_NEXT_STEPS_CHECKLIST"],
        "OBSERVABILITY_ALERT": ["ACKNOWLEDGE_OBSERVABILITY_ALERT", "CREATE_AMS_WORK_NOTE_DRAFT", "LINK_EVIDENCE_TO_CASE"],
        "BATCH_FAILURE": ["CREATE_NEXT_STEPS_CHECKLIST", "CREATE_AMS_WORK_NOTE_DRAFT", "ADD_INTERNAL_CASE_NOTE"],
        "USER_ISSUE": ["CREATE_CUSTOMER_UPDATE_DRAFT", "CREATE_AMS_WORK_NOTE_DRAFT", "ADD_INTERNAL_CASE_NOTE"],
        "MONITORING_TRIAGE": ["ACKNOWLEDGE_MONITORING_ALERT", "CREATE_AMS_WORK_NOTE_DRAFT", "LINK_EVIDENCE_TO_CASE"],
        "OPERATIONS_EXCEPTION": ["ACKNOWLEDGE_OPERATIONS_EXCEPTION", "CREATE_AMS_WORK_NOTE_DRAFT", "ADD_INTERNAL_CASE_NOTE"],
        "DIAGNOSTIC_CASE": ["CREATE_AMS_WORK_NOTE_DRAFT", "CREATE_NEXT_STEPS_CHECKLIST", "LINK_EVIDENCE_TO_CASE"],
    }.get(case.case_type, ["CREATE_NEXT_STEPS_CHECKLIST", "CREATE_AMS_WORK_NOTE_DRAFT", "ADD_INTERNAL_CASE_NOTE", "UPDATE_AGENT_CASE_STATUS"])


def generate_proposals(db: Session, case: AgentCase, run: AgentOrchestrationRun) -> int:
    """Create deterministic suggestions; this function never executes one."""
    specs = ["REVIEW_EVIDENCE", *_specs_for_case(case)]
    now = _now()
    for code in specs:
        item = CATALOG_BY_CODE[code]
        payload = {"case_id": str(case.id), "target": case.source_object_display or case.case_id}
        row = AgentActionProposal(proposal_id=_next(db, AgentActionProposal, AgentActionProposal.proposal_id, "AGENT-PROP-"), case_id=case.id, run_id=run.id, title=item["name"], description=item["description"], action_type=code, safe_action_code=code, risk_level=item["risk_level"], status="PROPOSED", requires_approval=True, approval_status="PENDING_APPROVAL", execution_status="DISABLED_IN_STAGE_1" if code == "REVIEW_EVIDENCE" else "PENDING_APPROVAL", execution_mode=EXECUTION_MODE, idempotency_key=f"agent-action:{case.id}:{code}:{run.id}", action_payload_json=payload, created_at=now, updated_at=now)
        db.add(row)
        # Flush each generated identifier so the deterministic sequence remains
        # unique even when a run proposes several actions in one transaction.
        db.flush()
    return len(specs)


def list_proposals(db: Session, case_id: UUID | None = None, status: str | None = None) -> list[dict[str, Any]]:
    statement = select(AgentActionProposal).order_by(AgentActionProposal.created_at, AgentActionProposal.id)
    if case_id:
        statement = statement.where(AgentActionProposal.case_id == case_id)
    if status:
        statement = statement.where(AgentActionProposal.execution_status == status.upper())
    return [_proposal_dict(row) for row in db.scalars(statement).all()]


def get_proposal(db: Session, proposal_id: str) -> dict[str, Any]:
    return _proposal_dict(_proposal(db, proposal_id))


def approve_proposal(db: Session, proposal_id: str, request: ActionApprovalRequest) -> dict[str, Any]:
    row = _proposal(db, proposal_id)
    if row.approval_status == "REJECTED" or row.execution_status == "REJECTED":
        raise AgentActionError("Rejected action proposals cannot be approved.")
    if row.execution_status in ("SUCCEEDED", "EXECUTING"):
        raise AgentActionError("This action proposal has already been executed or is executing.")
    now = _now()
    row.status, row.approval_status, row.execution_status = "APPROVED", "APPROVED", "APPROVED"
    row.approved_by_role, row.approved_at, row.approval_comment, row.updated_at = request.approved_by_role, now, request.approval_comment, now
    _audit(db, row, "ACTION_APPROVED", request.approved_by_role, request.approval_comment)
    _system_message(db, row.case, f"Action proposal approved: {row.title} ({row.proposal_id}).")
    db.commit()
    result: dict[str, Any] = {"proposal": _proposal_dict(row), "execution": None}
    if request.execute_after_approval:
        result = execute_proposal(db, proposal_id, ActionExecutionRequest(requested_by_role=request.approved_by_role, execution_comment="Executed after explicit approval."))
    return result


def reject_proposal(db: Session, proposal_id: str, request: ActionRejectionRequest) -> dict[str, Any]:
    row = _proposal(db, proposal_id)
    if row.execution_status in ("SUCCEEDED", "EXECUTING"):
        raise AgentActionError("Executed action proposals cannot be rejected.")
    if row.approval_status == "APPROVED":
        raise AgentActionError("Approved action proposals cannot be rejected; execute or leave the approval audit intact.")
    now = _now()
    row.status, row.approval_status, row.execution_status = "REJECTED", "REJECTED", "REJECTED"
    row.rejected_by_role, row.rejected_at, row.approval_comment, row.updated_at = request.rejected_by_role, now, request.rejection_comment, now
    _audit(db, row, "ACTION_REJECTED", request.rejected_by_role, request.rejection_comment)
    _system_message(db, row.case, f"Action proposal rejected: {row.title} ({row.proposal_id}).")
    db.commit()
    return {"proposal": _proposal_dict(row), "execution": None}


def _target(proposal: AgentActionProposal) -> dict[str, Any]:
    case = proposal.case
    return {"case_id": str(case.id), "case_number": case.case_id, "source_type": case.source_object_type, "source_id": str(case.source_object_id) if case.source_object_id else None, "source_display": case.source_object_display}


def _execute_handler(db: Session, proposal: AgentActionProposal) -> tuple[str, dict[str, Any]]:
    code = proposal.safe_action_code or proposal.action_type
    catalog_item = CATALOG_BY_CODE.get(code)
    if catalog_item is None:
        raise AgentActionError(f"Safe action code {code} is not in the catalog.", 400)
    case = proposal.case
    if code in ("CREATE_AMS_WORK_NOTE_DRAFT", "CREATE_CUSTOMER_UPDATE_DRAFT", "CREATE_NEXT_STEPS_CHECKLIST", "CREATE_FOLLOW_UP_TASK_DRAFT"):
        from app.services import agent_investigation_service
        drafts = agent_investigation_service.drafts(db, case.id)
        key = {"CREATE_AMS_WORK_NOTE_DRAFT": "work_note_draft", "CREATE_CUSTOMER_UPDATE_DRAFT": "customer_update_draft", "CREATE_NEXT_STEPS_CHECKLIST": "next_steps_checklist", "CREATE_FOLLOW_UP_TASK_DRAFT": "next_steps_checklist"}[code]
        content = drafts[key]["content"]
        return f"Created local {catalog_item['name']} for human review.", {"artifact_type": key.upper(), "draft": content, "external_send": False}
    if code == "ADD_INTERNAL_CASE_NOTE":
        text = f"Approved local action note for {case.case_id}: {case.title}. Evidence and next steps were reviewed by the service engineer."
        _system_message(db, case, text)
        return "Added an internal system note to the local agent case.", {"message": text, "external_send": False}
    if code == "UPDATE_AGENT_CASE_STATUS":
        target = (proposal.action_payload_json or {}).get("target_status", "IN_PROGRESS")
        if target not in ("IN_PROGRESS", "WAITING_FOR_USER", "GUIDANCE_PROVIDED", "CLOSED"):
            raise AgentActionError("Agent case status is outside the allowed local status set.", 400)
        case.status, case.updated_at = target, _now()
        return f"Updated local agent case status to {target}.", {"case_id": str(case.id), "status": target}
    if code in ("MARK_AGENT_PROPOSAL_REVIEWED", "REVIEW_EVIDENCE"):
        return "Recorded the human review of this proposal; no external or business-system change was made.", {"reviewed": True}
    if code == "LINK_EVIDENCE_TO_CASE":
        from app.models.agent_chat import AgentEvidenceItem
        evidence = db.scalars(select(AgentEvidenceItem).where(AgentEvidenceItem.case_id == case.id)).all()
        return f"Confirmed {len(evidence)} local evidence item(s) linked to the case.", {"evidence_ids": [str(item.evidence_id) for item in evidence], "mutated_business_data": False}
    if code == "ACKNOWLEDGE_OBSERVABILITY_ALERT":
        alert = db.get(ObsAlertEvent, case.linked_alert_event_id) if case.linked_alert_event_id else None
        if alert is None:
            raise AgentActionError("No linked observability alert is available for acknowledgement.", 400)
        if alert.status == "RESOLVED":
            raise AgentActionError("Resolved observability alerts cannot be acknowledged.", 409)
        if alert.status == "OPEN":
            alert.status, alert.updated_at = "ACKNOWLEDGED", _now()
        return f"Acknowledged local observability alert {alert.event_id}; it was not resolved.", {"alert_id": str(alert.id), "status": alert.status, "resolved": False}
    if code == "ACKNOWLEDGE_MONITORING_ALERT":
        triage = db.get(MonTriageCase, case.source_object_id) if case.source_object_type == "MONITORING_TRIAGE" and case.source_object_id else None
        alert = db.get(MonAlert, triage.alert_links[0].alert_id) if triage and triage.alert_links else None
        if alert is None:
            raise AgentActionError("No linked monitoring alert is available for acknowledgement.", 400)
        if alert.status == "OPEN":
            alert.status, alert.acknowledged_at, alert.updated_at = "ACKNOWLEDGED", _now(), _now()
        if alert.status == "RESOLVED":
            raise AgentActionError("Resolved monitoring alerts cannot be acknowledged.", 409)
        return f"Acknowledged local monitoring alert {alert.alert_number}; it was not resolved.", {"alert_id": str(alert.id), "status": alert.status, "resolved": False}
    if code == "ACKNOWLEDGE_OPERATIONS_EXCEPTION":
        exception = db.get(OpsException, case.source_object_id) if case.source_object_type == "OPERATIONS_EXCEPTION" else None
        if exception is None:
            raise AgentActionError("No linked operations exception is available for acknowledgement.", 400)
        if exception.status == "OPEN":
            exception.status, exception.updated_at = "ACKNOWLEDGED", _now()
        return f"Acknowledged local operations exception {exception.exception_number}; it was not closed.", {"exception_id": str(exception.id), "status": exception.status, "closed": False}
    raise AgentActionError(f"No safe local handler is defined for {code}.", 400)


def dry_run_proposal(db: Session, proposal_id: str, requested_by_role: str) -> dict[str, Any]:
    row = _proposal(db, proposal_id)
    code = row.safe_action_code or row.action_type
    if code not in CATALOG_BY_CODE:
        raise AgentActionError("Proposal is not backed by the safe action catalog.", 400)
    result = {"proposal": _proposal_dict(row), "what_would_happen": CATALOG_BY_CODE[code]["description"], "executable": row.approval_status == "APPROVED" and row.execution_status not in ("REJECTED", "SUCCEEDED"), "required_approval_state": "APPROVED", "target_object": _target(row), "expected_local_changes": "Execution audit and, for the selected handler, only the explicitly described local EOS change.", "safety_notes": SAFETY_NOTES, "requested_by_role": requested_by_role, "dry_run": True}
    _audit(db, row, "ACTION_DRY_RUN", requested_by_role, metadata={"executable": result["executable"]})
    db.commit()
    return result


def execute_proposal(db: Session, proposal_id: str, request: ActionExecutionRequest) -> dict[str, Any]:
    row = _proposal(db, proposal_id)
    existing = db.scalar(select(AgentActionExecution).where(AgentActionExecution.idempotency_key == row.idempotency_key)) if row.idempotency_key else None
    if existing is not None or row.execution_status in ("SUCCEEDED", "FAILED", "SKIPPED_DUPLICATE"):
        return {"proposal": _proposal_dict(row), "execution": _execution_dict(existing) if existing else None, "duplicate_prevented": True, "message": "Duplicate execution prevented; the proposal has already been attempted."}
    if row.approval_status != "APPROVED" or row.execution_status not in ("APPROVED", "EXECUTION_PENDING"):
        raise AgentActionError("Only explicitly approved action proposals can execute.")
    code = row.safe_action_code or row.action_type
    if code not in CATALOG_BY_CODE:
        raise AgentActionError("Proposal is not backed by the safe action catalog.", 400)
    now = _now()
    row.execution_status, row.execution_started_at, row.updated_at = "EXECUTING", now, now
    execution = AgentActionExecution(execution_id=_next(db, AgentActionExecution, AgentActionExecution.execution_id, "AGENT-EXEC-"), proposal_id=row.id, case_id=row.case_id, run_id=row.run_id, safe_action_code=code, status="EXECUTING", requested_by_role=request.requested_by_role, approved_by_role=row.approved_by_role, started_at=now, idempotency_key=row.idempotency_key or f"agent-action:{row.proposal_id}", created_at=now, updated_at=now)
    db.add(execution)
    _audit(db, row, "ACTION_EXECUTION_STARTED", request.requested_by_role, request.execution_comment)
    db.flush()
    try:
        result_summary, result_json = _execute_handler(db, row)
        completed = _now()
        execution.status, execution.completed_at, execution.result_summary, execution.result_json, execution.updated_at = "SUCCEEDED", completed, result_summary, result_json, completed
        row.status, row.execution_status, row.execution_completed_at, row.execution_result_json, row.execution_error, row.updated_at = "SUCCEEDED", "SUCCEEDED", completed, result_json, None, completed
        row.case.updated_at = completed
        run = db.get(AgentOrchestrationRun, row.run_id)
        if run is not None:
            run.actions_executed += 1
        _audit(db, row, "ACTION_EXECUTION_SUCCEEDED", request.requested_by_role, result_summary, result_json)
        _system_message(db, row.case, f"Approved action executed: {row.title} ({row.proposal_id}). Result: {result_summary}")
    except AgentActionError as error:
        completed = _now()
        execution.status, execution.completed_at, execution.error_message, execution.updated_at = "FAILED", completed, error.message, completed
        row.status, row.execution_status, row.execution_completed_at, row.execution_error, row.updated_at = "FAILED", "FAILED", completed, error.message, completed
        _audit(db, row, "ACTION_EXECUTION_FAILED", request.requested_by_role, error.message)
        _system_message(db, row.case, f"Approved action execution failed: {row.title} ({row.proposal_id}). {error.message}")
    db.commit()
    return {"proposal": _proposal_dict(row), "execution": _execution_dict(execution), "duplicate_prevented": False}


def list_executions(db: Session, case_id: UUID | None = None, status: str | None = None) -> list[dict[str, Any]]:
    statement = select(AgentActionExecution).order_by(AgentActionExecution.created_at.desc())
    if case_id:
        statement = statement.where(AgentActionExecution.case_id == case_id)
    if status:
        statement = statement.where(AgentActionExecution.status == status.upper())
    return [_execution_dict(row) for row in db.scalars(statement).all()]


def get_execution(db: Session, execution_id: str) -> dict[str, Any]:
    row = db.scalar(select(AgentActionExecution).where(AgentActionExecution.execution_id == execution_id))
    if row is None:
        raise AgentActionError("Agent action execution not found.", 404)
    return _execution_dict(row)


def summary(db: Session) -> dict[str, Any]:
    count = lambda condition: int(db.scalar(select(func.count(AgentActionProposal.id)).where(condition)) or 0)
    return {"stage_mode": STAGE_2, "execution_mode": EXECUTION_MODE, "catalog_actions": len(_CATALOG), "proposals": count(True), "pending_approval": count(AgentActionProposal.approval_status == "PENDING_APPROVAL"), "approved": count(AgentActionProposal.approval_status == "APPROVED"), "rejected": count(AgentActionProposal.approval_status == "REJECTED"), "executions": int(db.scalar(select(func.count(AgentActionExecution.id))) or 0), "succeeded": int(db.scalar(select(func.count(AgentActionExecution.id)).where(AgentActionExecution.status == "SUCCEEDED")) or 0), "failed": int(db.scalar(select(func.count(AgentActionExecution.id)).where(AgentActionExecution.status == "FAILED")) or 0), "autonomous_remediation_enabled": False, "real_model_default": False, "safety_notes": SAFETY_NOTES}
