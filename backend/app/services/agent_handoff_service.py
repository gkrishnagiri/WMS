"""Contextual handoff from operational records into Stage 1 agent chat."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.agent_chat import AgentCase, AgentChatSession
from app.models.ams import AmsTicket
from app.models.batch import BatchRun
from app.models.observability import ObsDiagnosticCase
from app.models.observability_alerts import ObsAlertEvent
from app.models.monitoring import MonTriageCase
from app.models.operations import OpsException
from app.models.user_reports import AmsUserReport
from app.schemas.agent_chat import AgentChatSessionResponse, AgentHandoffRequest, AgentHandoffResponse
from app.services import agent_orchestrator_service


@dataclass
class SourceContext:
    source_object_type: str
    source_object_id: UUID
    source_object_display: str
    title: str
    description: str
    case_type: str
    priority: str = "P3"
    source_object_url: str | None = None
    links: dict[str, UUID | None] = field(default_factory=dict)


class AgentHandoffError(Exception):
    def __init__(self, message: str, status_code: int = 404) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _priority(value: str | None) -> str:
    return {"CRITICAL": "P1", "HIGH": "P2", "MEDIUM": "P3", "LOW": "P4"}.get((value or "MEDIUM").upper(), "P3")


def _context(db: Session, source_type: str, source_id: UUID) -> SourceContext:
    if source_type == "AMS_TICKET":
        row = db.get(AmsTicket, source_id)
        if not row: raise AgentHandoffError("AMS ticket not found.")
        return SourceContext(source_type, row.id, row.ticket_number, f"Investigate {row.ticket_number}: {row.short_description}", row.description, "AMS_TICKET", row.priority, f"/ams/tickets/{row.id}", {"linked_ams_ticket_id": row.id, "linked_user_report_id": row.user_report_id})
    if source_type == "OBSERVABILITY_ALERT":
        row = db.get(ObsAlertEvent, source_id)
        if not row: raise AgentHandoffError("Observability alert event not found.")
        return SourceContext(source_type, row.id, row.event_id, f"Investigate {row.event_id}: {row.title}", row.description or row.condition_summary, "OBSERVABILITY_ALERT", _priority(row.severity), f"/observability-alerts/events/{row.id}", {"linked_alert_event_id": row.id, "linked_ams_ticket_id": row.created_ticket_id})
    if source_type == "BATCH_FAILURE":
        row = db.get(BatchRun, source_id)
        if not row: raise AgentHandoffError("Batch run not found.")
        return SourceContext(source_type, row.id, row.run_number, f"Investigate {row.run_number}: {row.scenario_code}", row.failure_message or row.summary, "BATCH_FAILURE", _priority(row.status), f"/batch/runs/{row.id}", {"linked_batch_run_id": row.id, "linked_ams_ticket_id": row.linked_ticket_id, "linked_diagnostic_case_id": row.linked_diagnostic_case_id})
    if source_type == "USER_ISSUE":
        row = db.get(AmsUserReport, source_id)
        if not row: raise AgentHandoffError("User report not found.")
        return SourceContext(source_type, row.id, row.report_number, f"Investigate {row.report_number}: {row.title}", f"{row.description}\nBusiness impact: {row.business_impact}", "USER_ISSUE", _priority(row.severity), f"/ams/user-reports/{row.id}", {"linked_user_report_id": row.id, "linked_ams_ticket_id": row.ticket_id})
    if source_type == "DIAGNOSTIC_CASE":
        row = db.get(ObsDiagnosticCase, source_id)
        if not row: raise AgentHandoffError("Diagnostic case not found.")
        return SourceContext(source_type, row.id, row.diagnostic_number, f"Investigate {row.diagnostic_number}: {row.title}", f"{row.description}\n{row.diagnosis_summary}\nProbable cause: {row.probable_cause}", "DIAGNOSTIC_CASE", _priority(row.severity), f"/observability/diagnostics/{row.id}", {"linked_diagnostic_case_id": row.id, "linked_ams_ticket_id": row.linked_ticket_id})
    if source_type == "MONITORING_TRIAGE":
        row = db.get(MonTriageCase, source_id)
        if not row: raise AgentHandoffError("Monitoring triage case not found.")
        return SourceContext(source_type, row.id, row.case_number, f"Investigate {row.case_number}: {row.title}", f"{row.description}\nImpact: {row.suspected_impact}", "MONITORING_TRIAGE", _priority(row.severity), f"/monitoring/triage/{row.id}", {"linked_ams_ticket_id": row.linked_ticket_id})
    if source_type == "OPERATIONS_EXCEPTION":
        row = db.get(OpsException, source_id)
        if not row: raise AgentHandoffError("Operations exception not found.")
        ticket = db.scalar(select(AmsTicket.id).where(AmsTicket.exception_id == row.id).order_by(AmsTicket.opened_at.desc()).limit(1))
        return SourceContext(source_type, row.id, row.exception_number, f"Investigate {row.exception_number}: {row.title}", f"{row.description}\nBusiness impact: {row.business_impact}", "OPERATIONS_EXCEPTION", _priority(row.severity), f"/operations/exceptions/{row.id}", {"linked_ams_ticket_id": ticket})
    raise AgentHandoffError(f"Unsupported handoff source type: {source_type}.", 400)


def _active_case(db: Session, source: SourceContext) -> AgentCase | None:
    explicit = source.links.get({"AMS_TICKET": "linked_ams_ticket_id", "OBSERVABILITY_ALERT": "linked_alert_event_id", "BATCH_FAILURE": "linked_batch_run_id", "USER_ISSUE": "linked_user_report_id", "DIAGNOSTIC_CASE": "linked_diagnostic_case_id"}.get(source.source_object_type, ""))
    conditions = [and_(AgentCase.source_object_type == source.source_object_type, AgentCase.source_object_id == source.source_object_id)]
    if explicit:
        field_name = {"AMS_TICKET": "linked_ams_ticket_id", "OBSERVABILITY_ALERT": "linked_alert_event_id", "BATCH_FAILURE": "linked_batch_run_id", "USER_ISSUE": "linked_user_report_id", "DIAGNOSTIC_CASE": "linked_diagnostic_case_id"}.get(source.source_object_type)
        if field_name: conditions.append(getattr(AgentCase, field_name) == explicit)
    return db.scalar(select(AgentCase).where(AgentCase.status != "CLOSED", or_(*conditions)).order_by(AgentCase.updated_at.desc()).limit(1))


def handoff(db: Session, source_type: str, source_id: UUID, request: AgentHandoffRequest) -> AgentHandoffResponse:
    source = _context(db, source_type, source_id)
    case = _active_case(db, source) if request.reuse_existing else None
    created_case = case is None
    if case is None:
        case = AgentCase(case_id=agent_orchestrator_service._next(db, AgentCase, AgentCase.case_id, "AGENT-CASE-"), case_type=source.case_type, title=source.title, description=source.description, status="OPEN", priority=source.priority, source="CONTEXTUAL_HANDOFF", stage_mode=agent_orchestrator_service.STAGE_1, created_by_role="SERVICE_ENGINEER", source_object_type=source.source_object_type, source_object_id=source.source_object_id, source_object_display=source.source_object_display, source_object_url=source.source_object_url, **source.links)
        db.add(case); db.flush()
    session = db.scalar(select(AgentChatSession).where(AgentChatSession.case_id == case.id, AgentChatSession.status == "ACTIVE").order_by(AgentChatSession.updated_at.desc()).limit(1))
    created_session = session is None
    if session is None:
        now = datetime.now(timezone.utc)
        session = AgentChatSession(session_id=agent_orchestrator_service._next(db, AgentChatSession, AgentChatSession.session_id, "AGENT-CHAT-"), case_id=case.id, audience="SERVICE_ENGINEER", title=source.title, status="ACTIVE", started_by_role="SERVICE_ENGINEER", experience="agentic", created_at=now, updated_at=now)
        db.add(session); db.flush()
        from app.models.agent_chat import AgentChatMessage
        trigger = AgentChatMessage(message_id=agent_orchestrator_service._next(db, AgentChatMessage, AgentChatMessage.message_id, "AGENT-MSG-"), session_id=session.id, sender_type="SERVICE_ENGINEER", sender_role="SERVICE_ENGINEER", message_text=request.initial_message, message_format="PLAIN_TEXT", generation_mode="HUMAN_ENTERED", safety_status="NOT_APPLICABLE", created_at=now)
        db.add(trigger); db.flush()
        agent_orchestrator_service._orchestrate(db, session, case, trigger, use_real_model=request.use_real_model, provider_code=request.provider_code, model_code=request.model_code, dry_run=request.dry_run)
        db.commit()
    session_response = agent_orchestrator_service.get_session(db, session.id)
    last_agent = next((item for item in reversed(session_response.messages) if item.sender_type == "AGENT"), None)
    return AgentHandoffResponse(case_id=case.case_id, case_record_id=case.id, session_id=session.session_id, session_record_id=session.id, source_object_type=source.source_object_type, source_object_id=source.source_object_id, source_object_display=source.source_object_display, source_object_url=source.source_object_url, created_new_case=created_case, created_new_session=created_session, reused_existing_case=not created_case, stage_mode=case.stage_mode, generation_mode=last_agent.generation_mode if last_agent else "DETERMINISTIC_AGENT", actions_executed=0, agent_chat_url=f"/agent-chat/sessions/{session.id}", agent_investigation_url=f"/agent-investigations/{case.id}", message="Agent investigation started in Stage 1 read-only mode." if created_case else "Existing agent investigation reused.", session=session_response.model_dump(mode="json"))
