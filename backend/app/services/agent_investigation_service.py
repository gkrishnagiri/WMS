"""Computed investigation workspace views for Stage 1 agent cases."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agent_chat import AgentActionAuditEvent, AgentActionExecution, AgentActionProposal, AgentCase, AgentChatMessage, AgentChatSession, AgentEvidenceItem, AgentOrchestrationRun
from app.models.agent_knowledge import AgentKnowledgeArticle, AgentKnownError, AgentRetrievalQuery, AgentRetrievalResult
from app.models.ams import AmsTicket, AmsTicketEvent
from app.models.batch import BatchRun, BatchRunEvent
from app.models.monitoring import MonTriageCase
from app.models.observability import ObsDiagnosticCase, ObsDiagnosticEvidence
from app.models.observability_alerts import ObsAlertEvent, ObsAlertEventEvidence
from app.models.operations import OpsException
from app.models.user_reports import AmsUserReport
from app.models.demo_scenario import DemoScenario, DemoScenarioArtifact, DemoScenarioRun


class AgentInvestigationError(Exception):
    def __init__(self, message: str, status_code: int = 404) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _case(db: Session, case_id: UUID) -> AgentCase:
    item = db.get(AgentCase, case_id)
    if item is None:
        raise AgentInvestigationError("Agent investigation case not found.")
    return item


def _iso(value: datetime | None) -> datetime | None:
    return value


def _record(model: Any, fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: getattr(model, field, None) for field in fields}


def _linked_objects(db: Session, case: AgentCase) -> dict[str, dict[str, Any] | None]:
    result: dict[str, dict[str, Any] | None] = {"ams_ticket": None, "user_report": None, "observability_alert": None, "batch_run": None, "diagnostic_case": None, "monitoring_triage": None, "operations_exception": None}
    if case.linked_ams_ticket_id:
        ticket = db.get(AmsTicket, case.linked_ams_ticket_id)
        if ticket:
            result["ams_ticket"] = _record(ticket, ("id", "ticket_number", "status", "priority", "severity", "short_description", "description"))
    if case.linked_user_report_id:
        report = db.get(AmsUserReport, case.linked_user_report_id)
        if report:
            result["user_report"] = _record(report, ("id", "report_number", "status", "severity", "title", "description", "business_impact"))
    if case.linked_alert_event_id:
        alert = db.get(ObsAlertEvent, case.linked_alert_event_id)
        if alert:
            result["observability_alert"] = _record(alert, ("id", "event_id", "rule_code", "status", "severity", "title", "description", "condition_summary", "source_url"))
    if case.linked_batch_run_id:
        run = db.get(BatchRun, case.linked_batch_run_id)
        if run:
            result["batch_run"] = _record(run, ("id", "run_number", "status", "scenario_code", "failure_type", "failure_message", "summary", "records_failed"))
    if case.linked_diagnostic_case_id:
        diagnostic = db.get(ObsDiagnosticCase, case.linked_diagnostic_case_id)
        if diagnostic:
            result["diagnostic_case"] = _record(diagnostic, ("id", "diagnostic_number", "status", "severity", "title", "description", "probable_cause", "diagnosis_summary", "recommended_next_steps"))
    if case.source_object_type == "MONITORING_TRIAGE" and case.source_object_id:
        triage = db.get(MonTriageCase, case.source_object_id)
        if triage:
            result["monitoring_triage"] = _record(triage, ("id", "case_number", "status", "severity", "title", "description", "suspected_impact", "suspected_root_cause"))
    if case.source_object_type == "OPERATIONS_EXCEPTION" and case.source_object_id:
        exception = db.get(OpsException, case.source_object_id)
        if exception:
            result["operations_exception"] = _record(exception, ("id", "exception_number", "status", "severity", "exception_type", "title", "description", "business_impact", "technical_context"))
    return result


def _evidence(item: AgentEvidenceItem) -> dict[str, Any]:
    return {"id": item.id, "evidence_id": item.evidence_id, "evidence_type": item.evidence_type, "source_type": item.source_type, "source_id": item.source_id, "title": item.title, "summary": item.summary, "source_url": item.source_url, "relevance_score": item.relevance_score, "created_at": item.created_at, "payload": item.payload_json}


def _knowledge(db: Session, items: list[AgentEvidenceItem]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    knowledge: list[dict[str, Any]] = []
    known_errors: list[dict[str, Any]] = []
    for item in items:
        if item.evidence_type == "KNOWLEDGE_CHUNK":
            article_id = (item.payload_json or {}).get("article_id")
            article = db.scalar(select(AgentKnowledgeArticle).where(AgentKnowledgeArticle.article_id == article_id)) if article_id else None
            knowledge.append({"id": item.id, "title": article.title if article else item.title, "article_id": article.article_id if article else article_id, "article_type": article.article_type if article else None, "domain": article.domain if article else None, "summary": item.summary, "source_url": item.source_url, "score": item.relevance_score})
        elif item.evidence_type == "KNOWN_ERROR":
            known = db.get(AgentKnownError, item.source_id) if item.source_id else None
            known_errors.append({"id": item.id, "known_error_id": known.known_error_id if known else item.title, "error_code": known.error_code if known else item.title, "title": known.title if known else item.title, "summary": item.summary, "likely_cause": known.likely_cause if known else (item.payload_json or {}).get("likely_cause"), "workaround": known.workaround if known else (item.payload_json or {}).get("workaround")})
    return knowledge, known_errors


def _base(db: Session, case: AgentCase) -> dict[str, Any]:
    evidence_rows = db.scalars(select(AgentEvidenceItem).where(AgentEvidenceItem.case_id == case.id).order_by(AgentEvidenceItem.created_at, AgentEvidenceItem.id)).all()
    runs = db.scalars(select(AgentOrchestrationRun).where(AgentOrchestrationRun.case_id == case.id).order_by(AgentOrchestrationRun.started_at)).all()
    proposals = db.scalars(select(AgentActionProposal).where(AgentActionProposal.case_id == case.id).order_by(AgentActionProposal.created_at)).all()
    executions = db.scalars(select(AgentActionExecution).where(AgentActionExecution.case_id == case.id).order_by(AgentActionExecution.created_at)).all()
    sessions = db.scalars(select(AgentChatSession).where(AgentChatSession.case_id == case.id).order_by(AgentChatSession.created_at)).all()
    messages = [message for session in sessions for message in db.scalars(select(AgentChatMessage).where(AgentChatMessage.session_id == session.id).order_by(AgentChatMessage.created_at, AgentChatMessage.id)).all()]
    knowledge, known_errors = _knowledge(db, evidence_rows)
    latest_agent = next((message for message in reversed(messages) if message.sender_type == "AGENT"), None)
    case_payload = {"id": case.id, "case_id": case.case_id, "case_type": case.case_type, "title": case.title, "description": case.description, "status": case.status, "priority": case.priority, "source": case.source, "stage_mode": case.stage_mode, "created_by_role": case.created_by_role, "source_object_type": case.source_object_type, "source_object_id": case.source_object_id, "source_object_display": case.source_object_display, "source_object_url": case.source_object_url, "linked_ams_ticket_id": case.linked_ams_ticket_id, "linked_user_report_id": case.linked_user_report_id, "linked_alert_event_id": case.linked_alert_event_id, "linked_batch_run_id": case.linked_batch_run_id, "linked_diagnostic_case_id": case.linked_diagnostic_case_id, "created_at": case.created_at, "updated_at": case.updated_at, "closed_at": case.closed_at}
    scenario_artifact = db.scalar(select(DemoScenarioArtifact).where(DemoScenarioArtifact.artifact_type == "AGENT_CASE", DemoScenarioArtifact.artifact_id == case.id).order_by(DemoScenarioArtifact.created_at.desc()).limit(1))
    scenario_context = None
    if scenario_artifact:
        scenario_run = db.get(DemoScenarioRun, scenario_artifact.run_id)
        scenario = db.scalar(select(DemoScenario).where(DemoScenario.scenario_code == scenario_run.scenario_code)) if scenario_run else None
        if scenario_run:
            scenario_context = {"scenario_code": scenario_run.scenario_code, "scenario_title": scenario.title if scenario else scenario_run.scenario_code, "run_id": scenario_run.run_id, "status": scenario_run.status, "current_step_code": scenario_run.current_step_code, "url": f"/demo-scenarios/runs/{scenario_run.run_id}"}
    return {"case": case_payload, "source": {"type": case.source_object_type, "display": case.source_object_display, "id": case.source_object_id, "url": case.source_object_url, "summary": case.description}, "scenario_context": scenario_context, "linked_objects": _linked_objects(db, case), "sessions": [{"id": session.id, "session_id": session.session_id, "title": session.title, "status": session.status, "audience": session.audience} for session in sessions], "messages": [{"id": message.id, "message_id": message.message_id, "sender_type": message.sender_type, "generation_mode": message.generation_mode, "safety_status": message.safety_status, "message_text": message.message_text, "created_at": message.created_at, "session_id": message.session_id} for message in messages], "evidence": [_evidence(item) for item in evidence_rows], "knowledge": knowledge, "known_errors": known_errors, "orchestration_runs": [{"id": run.id, "run_id": run.run_id, "status": run.status, "stage_mode": run.stage_mode, "orchestrator_mode": run.orchestrator_mode, "summary": run.summary, "started_at": run.started_at, "completed_at": run.completed_at, "actions_proposed": run.actions_proposed, "actions_executed": run.actions_executed} for run in runs], "action_proposals": [{"id": proposal.id, "proposal_id": proposal.proposal_id, "title": proposal.title, "description": proposal.description, "action_type": proposal.action_type, "safe_action_code": proposal.safe_action_code, "status": proposal.status, "requires_approval": proposal.requires_approval, "approval_status": proposal.approval_status, "approved_by_role": proposal.approved_by_role, "approved_at": proposal.approved_at, "rejected_by_role": proposal.rejected_by_role, "rejected_at": proposal.rejected_at, "approval_comment": proposal.approval_comment, "execution_status": proposal.execution_status, "execution_mode": proposal.execution_mode, "execution_started_at": proposal.execution_started_at, "execution_completed_at": proposal.execution_completed_at, "execution_error": proposal.execution_error, "execution_result_json": proposal.execution_result_json, "action_payload_json": proposal.action_payload_json, "created_at": proposal.created_at, "updated_at": proposal.updated_at} for proposal in proposals], "executions": [{"id": execution.id, "execution_id": execution.execution_id, "proposal_id": execution.proposal_id, "safe_action_code": execution.safe_action_code, "status": execution.status, "requested_by_role": execution.requested_by_role, "approved_by_role": execution.approved_by_role, "started_at": execution.started_at, "completed_at": execution.completed_at, "result_summary": execution.result_summary, "result_json": execution.result_json, "error_message": execution.error_message, "created_at": execution.created_at} for execution in executions], "latest_guidance": latest_agent.message_text if latest_agent else None, "counts": {"evidence_items": len(evidence_rows), "knowledge_items": len(knowledge), "known_errors": len(known_errors), "orchestration_runs": len(runs), "action_proposals": len(proposals), "actions_executed": sum(execution.status == "SUCCEEDED" for execution in executions)}, "stage_safety": {"mode": case.stage_mode, "action_mode": "STAGE_2_APPROVAL_GATED", "real_model_default": False, "remediation_execution_enabled": False, "message": "Stage 2 approval-gated mode. Only predefined safe local actions can execute after explicit human approval; autonomous remediation remains disabled."}}


def get_workspace(db: Session, case_id: UUID) -> dict[str, Any]:
    return _base(db, _case(db, case_id))


def list_workspaces(db: Session) -> list[dict[str, Any]]:
    return [_base(db, item) for item in db.scalars(select(AgentCase).order_by(AgentCase.updated_at.desc())).all()]


def summary(db: Session) -> dict[str, Any]:
    cases = db.scalars(select(AgentCase)).all()
    return {"investigations": len(cases), "open_investigations": sum(item.status != "CLOSED" for item in cases), "stage_1_investigations": sum(item.stage_mode == "STAGE_1_READ_ONLY" for item in cases), "evidence_items": sum(int(_base(db, item)["counts"]["evidence_items"]) for item in cases), "actions_executed": int(db.scalar(select(func.count(AgentActionExecution.id)).where(AgentActionExecution.status == "SUCCEEDED")) or 0)}


def evidence(db: Session, case_id: UUID) -> list[dict[str, Any]]:
    case = _case(db, case_id)
    return [_evidence(item) for item in db.scalars(select(AgentEvidenceItem).where(AgentEvidenceItem.case_id == case.id).order_by(AgentEvidenceItem.created_at)).all()]


def knowledge(db: Session, case_id: UUID) -> dict[str, list[dict[str, Any]]]:
    case = _case(db, case_id)
    items = db.scalars(select(AgentEvidenceItem).where(AgentEvidenceItem.case_id == case.id).order_by(AgentEvidenceItem.created_at)).all()
    articles, errors = _knowledge(db, items)
    return {"knowledge": articles, "known_errors": errors}


def drafts(db: Session, case_id: UUID) -> dict[str, Any]:
    workspace = get_workspace(db, case_id)
    case = workspace["case"]
    operational = workspace["evidence"][:8]
    knowledge_items = workspace["knowledge"][:6]
    summary = workspace["latest_guidance"] or f"Investigation of {case['title']} remains within the Stage 1 read-only boundary."
    evidence_text = "\n".join(f"- {item['summary']}" for item in operational) or "- No additional linked operational evidence was found."
    knowledge_text = "\n".join(f"- {item['title']}" for item in knowledge_items) or "- No matching curated knowledge was retrieved."
    checklist = "\n".join(["1. Review the source ticket, alert, batch run, or reported issue.", "2. Verify the current status and business impact.", "3. Check the evidence items and retrieved runbook guidance.", "4. Perform manual validation with the responsible service engineer.", "5. Update the AMS ticket and communicate status after human review."])
    return {"generation_mode": "DETERMINISTIC", "human_review_required": True, "generated_at": datetime.now(timezone.utc), "investigation_summary": {"artifact_type": "INVESTIGATION_SUMMARY", "title": "Investigation summary draft", "content": summary + "\n\nDraft only. Human review required."}, "work_note_draft": {"artifact_type": "WORK_NOTE_DRAFT", "title": "AMS work-note draft", "content": f"Investigation source: {case['source_object_display'] or case['case_id']}\nIssue: {case['title']}\n\nEvidence reviewed:\n{evidence_text}\n\nKnowledge retrieved:\n{knowledge_text}\n\nStage mode: {case['stage_mode']}\nActions executed: 0\n\nDraft only. Human review required. No action has been executed by the agent."}, "customer_update_draft": {"artifact_type": "CUSTOMER_UPDATE_DRAFT", "title": "Customer-update draft", "content": "We are investigating the reported issue. Current findings suggest that the support team should continue reviewing the linked operational evidence and runbook guidance. No customer-impacting action has been performed by the agent.\n\nDraft only. Human review required."}, "next_steps_checklist": {"artifact_type": "NEXT_STEPS_CHECKLIST", "title": "Human next-steps checklist", "content": checklist + "\n\nDraft only. Human review required; the agent cannot execute these steps."}}


def timeline(db: Session, case_id: UUID, descending: bool = False) -> list[dict[str, Any]]:
    case = _case(db, case_id)
    items: list[dict[str, Any]] = [{"timestamp": case.created_at, "item_type": "CASE_CREATED", "title": case.case_id, "description": case.title, "source_type": "agent_cases", "source_id": case.id, "severity": case.priority, "status": case.status, "link_url": f"/agent-chat/cases/{case.id}", "metadata": {}}]
    if case.source_object_type:
        items.append({"timestamp": case.created_at, "item_type": "SOURCE_LINKED", "title": case.source_object_display or case.source_object_type, "description": case.description, "source_type": case.source_object_type, "source_id": case.source_object_id, "severity": case.priority, "status": case.status, "link_url": case.source_object_url, "metadata": {}})
    sessions = db.scalars(select(AgentChatSession).where(AgentChatSession.case_id == case.id)).all()
    for session in sessions:
        items.append({"timestamp": session.created_at, "item_type": "CHAT_SESSION", "title": session.session_id, "description": session.title, "source_type": "agent_chat_sessions", "source_id": session.id, "severity": None, "status": session.status, "link_url": f"/agent-chat/sessions/{session.id}", "metadata": {}})
        for message in db.scalars(select(AgentChatMessage).where(AgentChatMessage.session_id == session.id)).all():
            items.append({"timestamp": message.created_at, "item_type": "AGENT_RESPONSE" if message.sender_type == "AGENT" else "CHAT_MESSAGE", "title": message.sender_type, "description": message.message_text[:500], "source_type": "agent_chat_messages", "source_id": message.id, "severity": None, "status": message.safety_status, "link_url": f"/agent-chat/sessions/{session.id}", "metadata": {"generation_mode": message.generation_mode}})
    for run in db.scalars(select(AgentOrchestrationRun).where(AgentOrchestrationRun.case_id == case.id)).all():
        items.append({"timestamp": run.started_at, "item_type": "ORCHESTRATION_RUN", "title": run.run_id, "description": run.summary, "source_type": "agent_orchestration_runs", "source_id": run.id, "severity": None, "status": run.status, "link_url": None, "metadata": {"actions_executed": run.actions_executed}})
    for item in db.scalars(select(AgentEvidenceItem).where(AgentEvidenceItem.case_id == case.id)).all():
        event_type = {"KNOWLEDGE_CHUNK": "KNOWLEDGE_RETRIEVED", "KNOWN_ERROR": "KNOWN_ERROR_MATCHED"}.get(item.evidence_type, "EVIDENCE_CAPTURED")
        items.append({"timestamp": item.created_at, "item_type": event_type, "title": item.title, "description": item.summary, "source_type": item.source_type, "source_id": item.source_id, "severity": None, "status": None, "link_url": item.source_url, "metadata": {"evidence_type": item.evidence_type, "relevance_score": item.relevance_score}})
    for query in db.scalars(select(AgentRetrievalQuery).where(AgentRetrievalQuery.case_id == case.id)).all():
        items.append({"timestamp": query.created_at, "item_type": "KNOWLEDGE_RETRIEVED", "title": query.query_id, "description": query.query_text, "source_type": "agent_retrieval_queries", "source_id": query.id, "severity": None, "status": query.retrieval_mode, "link_url": "/agent-knowledge/retrieval-queries", "metadata": {"top_k": query.top_k}})
    for proposal in db.scalars(select(AgentActionProposal).where(AgentActionProposal.case_id == case.id)).all():
        items.append({"timestamp": proposal.created_at, "item_type": "ACTION_PROPOSED", "title": proposal.title, "description": proposal.description, "source_type": "agent_action_proposals", "source_id": proposal.id, "severity": proposal.risk_level, "status": proposal.execution_status, "link_url": None, "metadata": {"requires_approval": proposal.requires_approval}})
    for event in db.scalars(select(AgentActionAuditEvent).where(AgentActionAuditEvent.case_id == case.id)).all():
        items.append({"timestamp": event.created_at, "item_type": event.event_type, "title": event.event_type.replace("_", " ").title(), "description": event.comment or "Agent action audit event.", "source_type": "agent_action_audit_events", "source_id": event.id, "severity": None, "status": "AUDITED", "link_url": None, "metadata": event.metadata_json or {}})
    items.sort(key=lambda item: (item["timestamp"] or datetime.min.replace(tzinfo=timezone.utc), str(item["source_id"])))
    return list(reversed(items)) if descending else items
