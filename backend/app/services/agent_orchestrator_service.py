"""Deterministic Stage 1 agent orchestration and evidence retrieval."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agent_chat import AgentActionProposal, AgentCase, AgentChatMessage, AgentChatSession, AgentEvidenceItem, AgentOrchestrationRun
from app.models.ams import AmsTicket, AmsTicketEvent
from app.models.batch import BatchRun, BatchRunEvent
from app.models.observability import ObsDiagnosticCase
from app.models.observability_alerts import ObsAlertEvent, ObsAlertEventEvidence
from app.models.user_reports import AmsUserReport
from app.models.monitoring import MonTriageCase
from app.models.operations import OpsException
from app.schemas.agent_chat import AgentActionProposalResponse, AgentCaseCreate, AgentCaseResponse, AgentChatMessageResponse, AgentChatSessionResponse, AgentEvidenceResponse, AgentIntakeRequest, AgentMessageCreate, AgentRunResponse, AgentSessionCreate
from app.schemas.ai_config import RealModelRequest
from app.services import ai_provider_gateway
from app.services import agent_knowledge_service
from app.services import agent_action_service

STAGE_1 = "STAGE_1_READ_ONLY"
ACTIVE_SESSION = "ACTIVE"


class AgentChatError(Exception):
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


def _case_response(case: AgentCase) -> AgentCaseResponse:
    return AgentCaseResponse.model_validate(case, from_attributes=True)


def _message_response(message: AgentChatMessage) -> AgentChatMessageResponse:
    return AgentChatMessageResponse.model_validate(message, from_attributes=True)


def _run_response(run: AgentOrchestrationRun) -> AgentRunResponse:
    return AgentRunResponse.model_validate(run, from_attributes=True)


def _evidence_response(item: AgentEvidenceItem) -> AgentEvidenceResponse:
    return AgentEvidenceResponse.model_validate(item, from_attributes=True)


def _proposal_response(item: AgentActionProposal) -> AgentActionProposalResponse:
    return AgentActionProposalResponse.model_validate(item, from_attributes=True)


def _session_response(db: Session, session: AgentChatSession) -> AgentChatSessionResponse:
    messages = db.scalars(select(AgentChatMessage).where(AgentChatMessage.session_id == session.id).order_by(AgentChatMessage.created_at, AgentChatMessage.id)).all()
    runs = db.scalars(select(AgentOrchestrationRun).where(AgentOrchestrationRun.session_id == session.id).order_by(AgentOrchestrationRun.started_at)).all()
    evidence = db.scalars(select(AgentEvidenceItem).where(AgentEvidenceItem.case_id == session.case_id).order_by(AgentEvidenceItem.created_at)).all()
    proposals = db.scalars(select(AgentActionProposal).where(AgentActionProposal.case_id == session.case_id).order_by(AgentActionProposal.created_at)).all()
    return AgentChatSessionResponse(id=session.id, session_id=session.session_id, case_id=session.case_id, audience=session.audience, title=session.title, status=session.status, started_by_role=session.started_by_role, experience=session.experience, created_at=session.created_at, updated_at=session.updated_at, closed_at=session.closed_at, case=_case_response(session.case), messages=[_message_response(x) for x in messages], evidence=[_evidence_response(x) for x in evidence], orchestration_runs=[_run_response(x) for x in runs], action_proposals=[_proposal_response(x) for x in proposals])


def _classify(text: str, linked: dict[str, UUID | None] | None = None, audience: str = "SERVICE_ENGINEER") -> str:
    linked = linked or {}
    if linked.get("linked_alert_event_id"): return "OBSERVABILITY_ALERT"
    if linked.get("linked_batch_run_id"): return "BATCH_FAILURE"
    if linked.get("linked_ams_ticket_id"): return "AMS_TICKET"
    if linked.get("linked_diagnostic_case_id"): return "DIAGNOSTIC_CASE"
    lower = text.lower()
    if "batch" in lower and ("fail" in lower or "stuck" in lower): return "BATCH_FAILURE"
    if "alert" in lower or "observability" in lower: return "OBSERVABILITY_ALERT"
    if "diagnostic" in lower: return "DIAGNOSTIC_CASE"
    if "ticket" in lower: return "AMS_TICKET"
    if any(word in lower for word in ("slow", "latency", "error", "investigate", "root cause")) and audience == "SERVICE_ENGINEER": return "SERVICE_ENGINEER_INVESTIGATION"
    if any(word in lower for word in ("order", "allocation", "inventory", "shipment", "stuck")): return "USER_ISSUE"
    return "SERVICE_ENGINEER_INVESTIGATION" if audience == "SERVICE_ENGINEER" else "USER_ISSUE"


def _add_evidence(db: Session, case: AgentCase, run: AgentOrchestrationRun, evidence_type: str, source_type: str, title: str, summary: str, source_id: UUID | None = None, payload: dict | None = None, source_url: str | None = None, score: float = 1.0) -> AgentEvidenceItem:
    item = AgentEvidenceItem(evidence_id=_next(db, AgentEvidenceItem, AgentEvidenceItem.evidence_id, "AGENT-EVID-"), case_id=case.id, run_id=run.id, evidence_type=evidence_type, source_type=source_type, source_id=source_id, title=title[:200], summary=summary[:1500], payload_json=payload, source_url=source_url, relevance_score=score)
    db.add(item)
    db.flush()
    return item


def _retrieve_evidence(db: Session, case: AgentCase, run: AgentOrchestrationRun) -> list[AgentEvidenceItem]:
    items: list[AgentEvidenceItem] = []
    if case.linked_ams_ticket_id:
        ticket = db.get(AmsTicket, case.linked_ams_ticket_id)
        if ticket:
            items.append(_add_evidence(db, case, run, "AMS_TICKET", "ams_tickets", ticket.ticket_number, f"{ticket.status} {ticket.priority} ticket: {ticket.short_description}", ticket.id, {"status": ticket.status, "priority": ticket.priority, "source": ticket.source}))
            for event in db.scalars(select(AmsTicketEvent).where(AmsTicketEvent.ticket_id == ticket.id).order_by(AmsTicketEvent.created_at.desc()).limit(3)).all():
                items.append(_add_evidence(db, case, run, "GENERAL_GUIDANCE", "ams_ticket_events", event.event_type, event.message, event.id, {"to_status": event.to_status}))
    if case.linked_user_report_id:
        report = db.get(AmsUserReport, case.linked_user_report_id)
        if report:
            items.append(_add_evidence(db, case, run, "USER_REPORT", "ams_user_reports", report.report_number, f"{report.title}: {report.business_impact}", report.id, {"status": report.status, "severity": report.severity, "reporter": report.reporter_name}))
    if case.linked_alert_event_id:
        alert = db.get(ObsAlertEvent, case.linked_alert_event_id)
        if alert:
            items.append(_add_evidence(db, case, run, "OBSERVABILITY_ALERT", "obs_alert_events", alert.event_id, f"{alert.status} {alert.severity} alert: {alert.condition_summary}", alert.id, {"rule_code": alert.rule_code, "observed_value": alert.observed_value, "threshold_value": alert.threshold_value}, alert.source_url))
            for evidence in db.scalars(select(ObsAlertEventEvidence).where(ObsAlertEventEvidence.event_id == alert.id)).all():
                items.append(_add_evidence(db, case, run, "ALERT_EVIDENCE", "obs_alert_event_evidence", evidence.title, evidence.summary, evidence.id, evidence.payload_json, evidence.source_url))
    if case.linked_batch_run_id:
        batch = db.get(BatchRun, case.linked_batch_run_id)
        if batch:
            items.append(_add_evidence(db, case, run, "BATCH_RUN", "batch_runs", batch.run_number, f"{batch.status} batch {batch.job.name if batch.job else ''}: {batch.failure_message or batch.summary}", batch.id, {"status": batch.status, "failure_type": batch.failure_type, "records_failed": batch.records_failed}))
            for event in db.scalars(select(BatchRunEvent).where(BatchRunEvent.batch_run_id == batch.id).order_by(BatchRunEvent.created_at.desc()).limit(5)).all():
                items.append(_add_evidence(db, case, run, "BATCH_EVENT", "batch_run_events", event.event_type, event.message, event.id, event.event_payload))
    if case.linked_diagnostic_case_id:
        diagnostic = db.get(ObsDiagnosticCase, case.linked_diagnostic_case_id)
        if diagnostic:
            items.append(_add_evidence(db, case, run, "DIAGNOSTIC_CASE", "obs_diagnostic_cases", diagnostic.diagnostic_number, f"{diagnostic.confidence_level} confidence: {diagnostic.probable_cause}", diagnostic.id, {"status": diagnostic.status, "next_steps": diagnostic.recommended_next_steps}))
    if case.source_object_type == "MONITORING_TRIAGE" and case.source_object_id:
        triage = db.get(MonTriageCase, case.source_object_id)
        if triage:
            items.append(_add_evidence(db, case, run, "MONITORING_TRIAGE", "mon_triage_cases", triage.case_number, f"{triage.status} triage case: {triage.description}", triage.id, {"impact": triage.suspected_impact, "root_cause": triage.suspected_root_cause}))
    if case.source_object_type == "OPERATIONS_EXCEPTION" and case.source_object_id:
        exception = db.get(OpsException, case.source_object_id)
        if exception:
            items.append(_add_evidence(db, case, run, "OPERATIONS_EXCEPTION", "ops_exceptions", exception.exception_number, f"{exception.status} exception: {exception.description}", exception.id, {"type": exception.exception_type, "impact": exception.business_impact}))
    existing_ids = {item.source_id for item in items if item.source_id}
    for alert in db.scalars(select(ObsAlertEvent).where(ObsAlertEvent.status.in_(("OPEN", "ACKNOWLEDGED", "TICKETED"))).order_by(ObsAlertEvent.last_seen_at.desc()).limit(2)).all():
        if alert.id not in existing_ids:
            items.append(_add_evidence(db, case, run, "OBSERVABILITY_ALERT", "obs_alert_events", alert.event_id, f"Recent {alert.severity} alert: {alert.condition_summary}", alert.id, {"rule_code": alert.rule_code}, alert.source_url, .7))
    for batch in db.scalars(select(BatchRun).where(BatchRun.status.in_(("FAILED", "TIMEOUT", "PARTIAL_SUCCESS"))).order_by(BatchRun.started_at.desc()).limit(2)).all():
        if batch.id not in existing_ids:
            items.append(_add_evidence(db, case, run, "BATCH_RUN", "batch_runs", batch.run_number, f"Recent {batch.status} batch: {batch.failure_message or batch.summary}", batch.id, {"failure_type": batch.failure_type}, score=.7))
    for ticket in db.scalars(select(AmsTicket).where(AmsTicket.status.in_(("NEW", "ACKNOWLEDGED", "IN_PROGRESS"))).order_by(AmsTicket.opened_at.desc()).limit(2)).all():
        if ticket.id not in existing_ids:
            items.append(_add_evidence(db, case, run, "AMS_TICKET", "ams_tickets", ticket.ticket_number, f"Open {ticket.priority} ticket: {ticket.short_description}", ticket.id, {"status": ticket.status, "source": ticket.source}, score=.6))
    return items


def _add_knowledge_evidence(db: Session, case: AgentCase, run: AgentOrchestrationRun, matches: list[agent_knowledge_service.KnowledgeMatch]) -> list[AgentEvidenceItem]:
    items: list[AgentEvidenceItem] = []
    for match in matches:
        if match.known_error:
            items.append(_add_evidence(db, case, run, "KNOWN_ERROR", "agent_known_errors", match.known_error.error_code, f"{match.known_error.title}: {match.known_error.symptoms}", match.known_error.id, {"likely_cause": match.known_error.likely_cause, "workaround": match.known_error.workaround}, score=match.score))
        elif match.article and match.chunk:
            items.append(_add_evidence(db, case, run, "KNOWLEDGE_CHUNK", "agent_knowledge_chunks", match.chunk.chunk_id, f"{match.article.title} — {match.chunk.heading}: {match.snippet}", match.chunk.id, {"article_id": match.article.article_id, "article_type": match.article.article_type, "domain": match.article.domain}, score=match.score))
    return items


def _guidance(case: AgentCase, message: str, evidence: list[AgentEvidenceItem], knowledge: list[AgentEvidenceItem]) -> str:
    case_label = case.case_type.replace("_", " ").lower()
    lines = [f"Understanding:\nYou are reporting a {case_label}: {case.title}.", "\nRelevant Operational Evidence:"]
    if evidence:
        lines.extend(f"- {item.summary}" for item in evidence[:8])
    else:
        lines.append("- No linked support artifact was found; the issue description is the current evidence.")
    lines.append("\nRelevant Knowledge:")
    if knowledge:
        lines.extend(f"- {item.summary}" for item in knowledge[:6])
    else:
        lines.append("- No matching curated knowledge article or known error was found.")
    if case.case_type == "BATCH_FAILURE":
        cause = "A failed or delayed batch step is the leading hypothesis; review its failure type and record counts before considering a rerun."
        steps = ["Review the failed batch step and its lifecycle events.", "Confirm records processed, succeeded, and failed.", "Check whether an exception, alert, diagnostic, or AMS ticket is linked.", "Confirm whether any rerun is safe with a service engineer."]
    elif case.case_type == "OBSERVABILITY_ALERT":
        cause = "The alert evidence is the leading signal; correlate its condition with runtime traces, logs, metrics, and the affected business workflow."
        steps = ["Review the alert condition and occurrence history.", "Open linked evidence and runtime telemetry.", "Check the related AMS ticket or create one through the operations workflow.", "Document findings before any human-approved action."]
    elif case.case_type == "AMS_TICKET":
        cause = "The ticket and its linked operational evidence should be treated as the current investigation boundary."
        steps = ["Review ticket events and current status.", "Check linked exceptions, alerts, diagnostics, and batch runs.", "Validate business impact with the reporter or service owner.", "Add a reviewed work note manually if needed."]
    else:
        cause = "The issue may be related to the reported business workflow or a recent support signal; evidence is not sufficient for certainty."
        steps = ["Confirm the affected business entity and current status.", "Review relevant inventory, order, shipment, batch, and support evidence.", "Check for a related alert or diagnostic case.", "Create or update an AMS ticket if the issue is blocking work."]
    return "\n".join(lines + [f"\nLikely Cause:\n{cause}", "\nRecommended Next Steps:"] + [f"{index}. {step}" for index, step in enumerate(steps, 1)] + ["\nWhat I Cannot Do Yet:\nThis agent is currently Stage 1 read-only. It cannot execute remediation actions, change business data, close tickets, resolve alerts, or send external messages."])


def _orchestrate(db: Session, session: AgentChatSession, case: AgentCase, trigger: AgentChatMessage, *, use_real_model: bool = False, provider_code: str | None = None, model_code: str | None = None, dry_run: bool = False) -> AgentOrchestrationRun:
    now = _now()
    run = AgentOrchestrationRun(run_id=_next(db, AgentOrchestrationRun, AgentOrchestrationRun.run_id, "AGENT-RUN-"), case_id=case.id, session_id=session.id, trigger_message_id=trigger.id, status="STARTED", stage_mode=STAGE_1, orchestrator_mode="DETERMINISTIC_STAGE_1", started_at=now, summary="Deterministic Stage 1 context gathering started.", tools_planned={"retrieval": ["linked_support_artifacts", "recent_open_alerts", "recent_failed_batches", "recent_ams_tickets"]}, tools_used={}, actions_proposed=0, actions_executed=0)
    db.add(run)
    db.flush()
    evidence = _retrieve_evidence(db, case, run)
    retrieval = agent_knowledge_service.retrieve_for_agent(db, case, session, trigger)
    knowledge = _add_knowledge_evidence(db, case, run, retrieval.matches)
    deterministic_guidance = _guidance(case, trigger.message_text, evidence, knowledge)
    generation_mode = "DETERMINISTIC_AGENT"
    safety_status = "SAFE"
    message_metadata: dict[str, Any] = {"stage_mode": STAGE_1, "evidence_count": len(evidence), "orchestration_run_id": str(run.id)}
    response_text = deterministic_guidance
    if use_real_model:
        context_items = [{"type": item.evidence_type, "title": item.title, "summary": item.summary} for item in [*evidence, *knowledge][:14]]
        real_request = RealModelRequest(provider_code=provider_code or "OPENAI_RESPONSES", model_code=model_code or "OPENAI_GPT_5_4_MINI", task_type="AGENT_STAGE_1_GUIDANCE", request_source="AGENT_CHAT", request_source_id=session.id, input_text=f"Case: {case.title}\nEngineer/user message: {trigger.message_text}", context_items=context_items, allow_real_model=True, dry_run=dry_run, metadata={"template_code": "TPL-AGENT-STAGE-1-GUIDANCE", "case_type": case.case_type}, created_by=case.created_by_role)
        real_result = ai_provider_gateway.invoke_real_model(db, real_request)
        message_metadata.update({"ai_invocation_id": str(real_result.invocation_id) if real_result.invocation_id else None, "invocation_number": real_result.invocation_number, "fallback_used": real_result.fallback_used, "real_model_status": real_result.status, "real_model_error": real_result.error_message})
        generation_mode = real_result.generation_mode
        safety_status = real_result.safety_status
        if real_result.status == "SUCCESS" and real_result.output_text:
            response_text = real_result.output_text
        else:
            generation_mode = "FALLBACK_DETERMINISTIC" if real_result.fallback_used else real_result.generation_mode
    response = AgentChatMessage(message_id=_next(db, AgentChatMessage, AgentChatMessage.message_id, "AGENT-MSG-"), session_id=session.id, sender_type="AGENT", sender_role="SUPPORT_AGENT", message_text=response_text[:6000], message_format="PLAIN_TEXT", generation_mode=generation_mode, safety_status=safety_status, created_at=_now(), metadata_json=message_metadata)
    db.add(response)
    run.actions_proposed = agent_action_service.generate_proposals(db, case, run)
    run.orchestrator_mode = "GOVERNED_REAL_MODEL_STAGE_1" if use_real_model else "DETERMINISTIC_STAGE_1"
    run.tools_used = {"operational_evidence": len(evidence), "knowledge_query_id": retrieval.query.query_id, "knowledge_results": len(knowledge), "real_model_requested": use_real_model, "actions_executed": 0}
    run.status, run.completed_at, run.summary = "COMPLETED", _now(), f"Gathered {len(evidence)} operational and {len(knowledge)} knowledge evidence item(s) and produced read-only guidance."
    case.status, case.updated_at = "GUIDANCE_PROVIDED", _now()
    session.updated_at = _now()
    return run


def create_case(db: Session, request: AgentCaseCreate) -> AgentCaseResponse:
    case = AgentCase(case_id=_next(db, AgentCase, AgentCase.case_id, "AGENT-CASE-"), case_type=(request.case_type or _classify(request.title + " " + request.description, request.model_dump(), request.created_by_role)).upper(), title=request.title, description=request.description, status="OPEN", priority=request.priority.upper(), source=request.source.upper(), stage_mode=STAGE_1, created_by_role=request.created_by_role, **{key: getattr(request, key) for key in ("linked_ams_ticket_id", "linked_user_report_id", "linked_alert_event_id", "linked_batch_run_id", "linked_diagnostic_case_id", "linked_order_id", "linked_shipment_id", "linked_inventory_item_id")})
    db.add(case); db.commit()
    return _case_response(case)


def create_session(db: Session, request: AgentSessionCreate) -> AgentChatSessionResponse:
    case = db.get(AgentCase, request.case_id) if request.case_id else None
    if request.case_id and case is None: raise AgentChatError("Agent case not found.", 404)
    if case is None:
        case = AgentCase(case_id=_next(db, AgentCase, AgentCase.case_id, "AGENT-CASE-"), case_type="SERVICE_ENGINEER_INVESTIGATION", title=request.title, description=request.title, status="OPEN", priority="P3", source="CHAT", stage_mode=STAGE_1, created_by_role=request.started_by_role)
        db.add(case); db.flush()
    now = _now()
    session = AgentChatSession(session_id=_next(db, AgentChatSession, AgentChatSession.session_id, "AGENT-CHAT-"), case_id=case.id, audience=request.audience.upper(), title=request.title, status=ACTIVE_SESSION, started_by_role=request.started_by_role, experience=request.experience, created_at=now, updated_at=now)
    db.add(session); db.commit()
    return _session_response(db, session)


def intake(db: Session, request: AgentIntakeRequest, audience: str, engineer: bool = False) -> AgentChatSessionResponse:
    role = request.created_by_role or ("SERVICE_ENGINEER" if engineer else "BUSINESS_USER")
    links = {key: getattr(request, key) for key in ("linked_ams_ticket_id", "linked_user_report_id", "linked_alert_event_id", "linked_batch_run_id", "linked_diagnostic_case_id")}
    case = AgentCase(case_id=_next(db, AgentCase, AgentCase.case_id, "AGENT-CASE-"), case_type=_classify(request.initial_message, links, audience), title=request.title, description=request.description, status="OPEN", priority=request.priority.upper(), source="ENGINEER_INTAKE" if engineer else "USER_INTAKE", stage_mode=STAGE_1, created_by_role=role, **links)
    db.add(case); db.flush()
    now = _now()
    session = AgentChatSession(session_id=_next(db, AgentChatSession, AgentChatSession.session_id, "AGENT-CHAT-"), case_id=case.id, audience=audience.upper(), title=request.title, status=ACTIVE_SESSION, started_by_role=role, experience="agentic" if engineer else "business", created_at=now, updated_at=now)
    db.add(session); db.flush()
    message = AgentChatMessage(message_id=_next(db, AgentChatMessage, AgentChatMessage.message_id, "AGENT-MSG-"), session_id=session.id, sender_type="SERVICE_ENGINEER" if engineer else "USER", sender_role=role, message_text=request.initial_message, message_format="PLAIN_TEXT", generation_mode="HUMAN_ENTERED", safety_status="NOT_APPLICABLE", created_at=now)
    db.add(message); db.flush()
    _orchestrate(db, session, case, message)
    db.commit()
    return _session_response(db, session)


def send_message(db: Session, session_id: UUID, request: AgentMessageCreate) -> AgentChatSessionResponse:
    session = db.get(AgentChatSession, session_id)
    if session is None: raise AgentChatError("Agent chat session not found.", 404)
    if session.status != ACTIVE_SESSION: raise AgentChatError("Closed chat sessions cannot receive messages.", 409)
    role = request.sender_role or ("BUSINESS_USER" if request.sender_type.upper() == "USER" else "SERVICE_ENGINEER")
    message = AgentChatMessage(message_id=_next(db, AgentChatMessage, AgentChatMessage.message_id, "AGENT-MSG-"), session_id=session.id, sender_type=request.sender_type.upper(), sender_role=role, message_text=request.message_text, message_format="PLAIN_TEXT", generation_mode="HUMAN_ENTERED", safety_status="NOT_APPLICABLE", created_at=_now())
    db.add(message); db.flush()
    _orchestrate(db, session, session.case, message, use_real_model=request.use_real_model, provider_code=request.provider_code, model_code=request.model_code, dry_run=request.dry_run)
    db.commit()
    return _session_response(db, session)


def get_case(db: Session, case_id: UUID) -> AgentCaseResponse:
    case = db.get(AgentCase, case_id)
    if case is None: raise AgentChatError("Agent case not found.", 404)
    return _case_response(case)


def list_cases(db: Session) -> list[AgentCaseResponse]:
    return [_case_response(x) for x in db.scalars(select(AgentCase).order_by(AgentCase.created_at.desc())).all()]


def list_sessions(db: Session) -> list[AgentChatSessionResponse]:
    return [_session_response(db, x) for x in db.scalars(select(AgentChatSession).order_by(AgentChatSession.created_at.desc())).all()]


def get_session(db: Session, session_id: UUID) -> AgentChatSessionResponse:
    session = db.get(AgentChatSession, session_id)
    if session is None: raise AgentChatError("Agent chat session not found.", 404)
    return _session_response(db, session)


def close_session(db: Session, session_id: UUID) -> AgentChatSessionResponse:
    session = db.get(AgentChatSession, session_id)
    if session is None: raise AgentChatError("Agent chat session not found.", 404)
    session.status, session.closed_at, session.updated_at = "CLOSED", _now(), _now()
    session.case.status, session.case.closed_at, session.case.updated_at = "CLOSED", session.closed_at, _now()
    db.commit()
    return _session_response(db, session)


def close_case(db: Session, case_id: UUID) -> AgentCaseResponse:
    case = db.get(AgentCase, case_id)
    if case is None: raise AgentChatError("Agent case not found.", 404)
    case.status, case.closed_at, case.updated_at = "CLOSED", _now(), _now()
    for session in case.sessions: session.status, session.closed_at, session.updated_at = "CLOSED", case.closed_at, _now()
    db.commit()
    return _case_response(case)


def get_messages(db: Session, session_id: UUID) -> list[AgentChatMessageResponse]:
    if db.get(AgentChatSession, session_id) is None: raise AgentChatError("Agent chat session not found.", 404)
    return [_message_response(x) for x in db.scalars(select(AgentChatMessage).where(AgentChatMessage.session_id == session_id).order_by(AgentChatMessage.created_at, AgentChatMessage.id)).all()]


def get_evidence(db: Session, case_id: UUID) -> list[AgentEvidenceResponse]:
    if db.get(AgentCase, case_id) is None: raise AgentChatError("Agent case not found.", 404)
    return [_evidence_response(x) for x in db.scalars(select(AgentEvidenceItem).where(AgentEvidenceItem.case_id == case_id).order_by(AgentEvidenceItem.created_at)).all()]


def get_runs(db: Session, case_id: UUID) -> list[AgentRunResponse]:
    if db.get(AgentCase, case_id) is None: raise AgentChatError("Agent case not found.", 404)
    return [_run_response(x) for x in db.scalars(select(AgentOrchestrationRun).where(AgentOrchestrationRun.case_id == case_id).order_by(AgentOrchestrationRun.started_at)).all()]


def get_proposals(db: Session, case_id: UUID) -> list[AgentActionProposalResponse]:
    if db.get(AgentCase, case_id) is None: raise AgentChatError("Agent case not found.", 404)
    return [_proposal_response(x) for x in db.scalars(select(AgentActionProposal).where(AgentActionProposal.case_id == case_id).order_by(AgentActionProposal.created_at)).all()]


def summary(db: Session) -> dict[str, int]:
    return {"open_cases": int(db.scalar(select(func.count(AgentCase.id)).where(AgentCase.status != "CLOSED")) or 0), "active_sessions": int(db.scalar(select(func.count(AgentChatSession.id)).where(AgentChatSession.status == "ACTIVE")) or 0), "orchestration_runs": int(db.scalar(select(func.count(AgentOrchestrationRun.id))) or 0), "evidence_items": int(db.scalar(select(func.count(AgentEvidenceItem.id))) or 0), "action_proposals": int(db.scalar(select(func.count(AgentActionProposal.id))) or 0), "actions_executed": int(db.scalar(select(func.coalesce(func.sum(AgentOrchestrationRun.actions_executed), 0))) or 0), "stage_mode": STAGE_1}
