"""Governed mock-AI draft generation for copilot sessions.

This service is an optional parallel path to the deterministic Prompt 09 draft
generation. It sends only a summarized context snapshot to the Prompt 10
gateway and never applies the returned content to a support artifact.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_config import AiInvocationLog
from app.models.copilot import CopilotContextSnapshot, CopilotMessage, CopilotSession
from app.schemas.ai_config import InvocationResponse
from app.schemas.copilot import CopilotGovernedDraftResponse, CopilotMessageResponse
from app.services import ai_config_service, ai_provider_gateway
from app.services.copilot_service import CopilotError


GOVERNED_DRAFTS = {
    "CONTEXT_SUMMARY": ("COPILOT_CONTEXT_SUMMARY", "TPL-COPILOT-CONTEXT-SUMMARY", "Context summary"),
    "WORK_NOTE_DRAFT": ("WORK_NOTE_DRAFT", "TPL-WORK-NOTE-DRAFT", "Governed work note draft"),
    "CUSTOMER_UPDATE_DRAFT": ("CUSTOMER_UPDATE_DRAFT", "TPL-CUSTOMER-UPDATE-DRAFT", "Governed customer update draft"),
    "INVESTIGATION_CHECKLIST": ("INVESTIGATION_CHECKLIST", "TPL-INVESTIGATION-CHECKLIST", "Governed investigation checklist"),
}


def _latest_snapshot(db: Session, session: CopilotSession) -> CopilotContextSnapshot:
    snapshot = db.scalar(
        select(CopilotContextSnapshot)
        .where(CopilotContextSnapshot.session_id == session.id)
        .order_by(CopilotContextSnapshot.created_at.desc())
    )
    if snapshot is None:
        raise CopilotError("Build a copilot context snapshot before generating governed AI assistance.", 409)
    return snapshot


def _safe_payload(session: CopilotSession, snapshot: CopilotContextSnapshot) -> dict:
    """Build a summarized, secret-free payload rather than passing raw_context."""
    return {
        "message": snapshot.summary,
        "session_number": session.session_number,
        "session_title": session.title,
        "primary_entity_type": session.primary_entity_type,
        "severity": session.severity,
        "confidence_level": session.confidence_level,
        "context_summary": snapshot.summary,
        "impact_summary": snapshot.impact_summary,
        "technical_summary": snapshot.technical_summary,
        "business_summary": snapshot.business_summary,
        "timeline_summary": snapshot.timeline_summary,
        "evidence_summary": snapshot.evidence_summary,
        "related_entities": snapshot.related_entities or {},
    }


def _message_response(row: CopilotMessage) -> CopilotMessageResponse:
    return CopilotMessageResponse.model_validate(row, from_attributes=True)


def generate_governed_draft(db: Session, session_id: UUID, draft_type: str) -> CopilotGovernedDraftResponse:
    session = db.get(CopilotSession, session_id)
    if session is None:
        raise CopilotError("Copilot session not found.", 404)
    normalized_type = draft_type.upper()
    config = GOVERNED_DRAFTS.get(normalized_type)
    if config is None:
        raise CopilotError("Unsupported governed copilot draft type.", 400)
    task_type, template_code, title = config
    snapshot = _latest_snapshot(db, session)
    try:
        invocation = ai_provider_gateway.invoke(
            db,
            task_type=task_type,
            input_payload=_safe_payload(session, snapshot),
            request_source="COPILOT_SESSION",
            request_source_id=session.id,
            template_code=template_code,
            model_code="MOCK-SUPPORT-COPILOT-001",
            created_by=session.created_by,
        )
    except ai_provider_gateway.AiGatewayError as error:
        raise CopilotError(error.message, error.status_code) from error

    blocked = invocation.status == "BLOCKED"
    if blocked:
        message_type = "GOVERNED_AI_BLOCKED"
        message_status = "DISCARDED"
        message_title = f"Governed AI blocked: {title}"
        content = f"Governed AI draft was blocked before provider response. Reason: {invocation.blocked_reason or 'Safety policy blocked this request.'} Invocation: {invocation.invocation_number}."
        event_type = "GOVERNED_AI_BLOCKED"
    else:
        message_type = normalized_type
        message_status = "DRAFT"
        message_title = title
        content = invocation.response_text or "No governed response was returned."
        event_type = "GOVERNED_AI_DRAFT_CREATED"

    row = CopilotMessage(
        session_id=session.id,
        message_type=message_type,
        title=message_title,
        content=content,
        status=message_status,
        target_entity_type=session.primary_entity_type,
        target_entity_id=session.primary_entity_id,
        ai_invocation_id=invocation.id,
        generation_mode="GOVERNED_AI_MOCK",
        created_by=session.created_by,
    )
    db.add(row)
    db.flush()
    from app.models.copilot import CopilotActionEvent

    db.add(
        CopilotActionEvent(
            session_id=session.id,
            action_code=f"GOVERNED_AI_{normalized_type}",
            event_type=event_type,
            target_entity_type=session.primary_entity_type,
            target_entity_id=session.primary_entity_id,
            message=f"{message_title} recorded for human review." if not blocked else content,
            event_payload={
                "message_id": str(row.id),
                "invocation_id": str(invocation.id),
                "invocation_number": invocation.invocation_number,
                "safety_status": invocation.safety_status,
                "execution": "not_performed",
            },
            created_by=session.created_by,
        )
    )
    db.commit()
    return CopilotGovernedDraftResponse(message=_message_response(row), invocation=invocation)


def list_session_invocations(db: Session, session_id: UUID) -> list[InvocationResponse]:
    if db.get(CopilotSession, session_id) is None:
        raise CopilotError("Copilot session not found.", 404)
    rows = db.scalars(
        select(AiInvocationLog)
        .where(
            AiInvocationLog.request_source == "COPILOT_SESSION",
            AiInvocationLog.request_source_id == session_id,
        )
        .order_by(AiInvocationLog.created_at.desc())
    ).all()
    return [ai_config_service.invocation_response(db, row) for row in rows]
