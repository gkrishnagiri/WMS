"""Deterministic, governed support copilot services.

This module deliberately produces context, recommendations, and drafts only.
It never executes ticket, alert, diagnostic, batch, or warehouse mutations as a
side effect of analysis.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.ams import AmsTicket, AmsTicketEvent
from app.models.batch import BatchRun, BatchRunEvent, BatchStepRun
from app.models.copilot import CopilotActionEvent, CopilotActionPlan, CopilotContextSnapshot, CopilotMessage, CopilotRecommendation, CopilotSafeAction, CopilotSession
from app.models.monitoring import MonAlert, MonAlertEvent, MonTriageCase, MonTriageCaseAlert
from app.models.observability import ObsDiagnosticCase, ObsDiagnosticEvidence, ObsLogEvent, ObsMetricSample, ObsSpan, ObsTrace
from app.models.operations import OpsException
from app.models.synthetic_users import SyntheticJourneyRun
from app.models.user_reports import AmsUserReport
from app.schemas.copilot import CopilotActionEventResponse, CopilotActionPlanResponse, CopilotContextResponse, CopilotMessageResponse, CopilotRecommendationResponse, CopilotSafeActionResponse, CopilotSessionResponse, CopilotSummary

ACTIVE_RECOMMENDATION_STATUSES = ("PROPOSED", "ACCEPTED")
OPEN_SESSION_STATUSES = ("OPEN", "ANALYZING", "RECOMMENDATIONS_READY", "ACTION_PLAN_READY")
VALID_ENTITY_TYPES = ("AMS_TICKET", "OPERATIONAL_EXCEPTION", "USER_REPORT", "MONITORING_ALERT", "MONITORING_TRIAGE_CASE", "OBSERVABILITY_DIAGNOSTIC", "BATCH_RUN", "MANUAL")
SEVERITIES = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


class CopilotError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_number(db: Session, field: Any, prefix: str) -> str:
    current = db.scalar(select(func.max(field)).where(field.like(f"{prefix}%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            sequence = 1
    return f"{prefix}{sequence:04d}"


def _text(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _entity_ref(entity_type: str, entity_id: UUID | None, label: str) -> dict[str, Any]:
    return {"entity_type": entity_type, "id": str(entity_id) if entity_id else None, "label": label}


def _ticket_context(db: Session, ticket: AmsTicket) -> dict[str, Any]:
    events = db.scalars(select(AmsTicketEvent).where(AmsTicketEvent.ticket_id == ticket.id).order_by(AmsTicketEvent.created_at)).all()
    exceptions = []
    if ticket.exception_id:
        row = db.get(OpsException, ticket.exception_id)
        if row:
            exceptions.append({"id": str(row.id), "number": row.exception_number, "title": row.title, "status": row.status, "severity": row.severity})
    reports = []
    if ticket.user_report_id:
        row = db.get(AmsUserReport, ticket.user_report_id)
        if row:
            reports.append({"id": str(row.id), "number": row.report_number, "title": row.title, "business_impact": row.business_impact, "status": row.status})
    alerts = db.scalars(select(MonAlert).where(MonAlert.linked_ticket_id == ticket.id).order_by(MonAlert.last_seen_at.desc())).all()
    triage = db.scalars(select(MonTriageCase).where(MonTriageCase.linked_ticket_id == ticket.id)).all()
    diagnostics = db.scalars(select(ObsDiagnosticCase).where(ObsDiagnosticCase.linked_ticket_id == ticket.id)).all()
    batches = db.scalars(select(BatchRun).where(BatchRun.linked_ticket_id == ticket.id).order_by(BatchRun.created_at.desc())).all()
    traces = db.scalars(select(ObsTrace).where(ObsTrace.linked_ticket_id == ticket.id).order_by(ObsTrace.started_at.desc())).all()
    logs = db.scalars(select(ObsLogEvent).where(ObsLogEvent.linked_ticket_id == ticket.id).order_by(ObsLogEvent.logged_at.desc()).limit(50)).all()
    return {
        "entity": {"id": str(ticket.id), "number": ticket.ticket_number, "status": ticket.status, "priority": ticket.priority, "severity": ticket.severity, "source": ticket.source, "source_module": ticket.source_module, "short_description": ticket.short_description, "description": ticket.description},
        "events": [{"event_type": e.event_type, "from_status": e.from_status, "to_status": e.to_status, "message": e.message, "created_at": _text(e.created_at)} for e in events],
        "exceptions": exceptions,
        "user_reports": reports,
        "alerts": [_alert_dict(a) for a in alerts],
        "triage_cases": [{"id": str(t.id), "number": t.case_number, "title": t.title, "status": t.status, "severity": t.severity, "confidence_level": t.confidence_level} for t in triage],
        "diagnostics": [{"id": str(d.id), "number": d.diagnostic_number, "title": d.title, "status": d.status, "probable_cause": d.probable_cause, "confidence_level": d.confidence_level} for d in diagnostics],
        "batch_runs": [_batch_dict(b) for b in batches],
        "traces": [{"id": str(t.id), "trace_id": t.trace_id, "status": t.status, "trace_name": t.trace_name, "duration_ms": t.duration_ms} for t in traces],
        "logs": [{"id": str(l.id), "log_number": l.log_number, "level": l.level, "event_type": l.event_type, "message": l.message} for l in logs],
    }


def _alert_dict(alert: MonAlert) -> dict[str, Any]:
    component = alert.component
    return {"id": str(alert.id), "number": alert.alert_number, "status": alert.status, "severity": alert.severity, "metric_name": alert.metric_name, "observed_value": alert.observed_value, "threshold_value": alert.threshold_value, "title": alert.title, "component_code": component.component_code if component else None, "occurrence_count": alert.occurrence_count}


def _batch_dict(run: BatchRun) -> dict[str, Any]:
    return {"id": str(run.id), "run_number": run.run_number, "status": run.status, "scenario_code": run.scenario_code, "failure_type": run.failure_type, "failure_message": run.failure_message, "records_processed": run.records_processed, "records_succeeded": run.records_succeeded, "records_failed": run.records_failed, "job_code": run.job.job_code if run.job else None, "job_name": run.job.name if run.job else None}


def _context_for(db: Session, entity_type: str, entity_id: UUID | None) -> dict[str, Any]:
    entity_type = entity_type.upper()
    if entity_type not in VALID_ENTITY_TYPES:
        raise CopilotError(f"Unsupported copilot entity type: {entity_type}.", 400)
    if entity_type == "MANUAL":
        return {"entity": {"id": str(entity_id) if entity_id else None, "label": "Manual support investigation"}, "events": [], "alerts": [], "diagnostics": [], "batch_runs": [], "traces": [], "logs": [], "exceptions": [], "user_reports": [], "triage_cases": [], "facts": {"manual": True}}
    if entity_id is None:
        raise CopilotError(f"{entity_type} requires an entity_id.", 400)
    if entity_type == "AMS_TICKET":
        row = db.get(AmsTicket, entity_id)
        if row is None: raise CopilotError("AMS ticket not found.", 404)
        data = _ticket_context(db, row)
    elif entity_type == "OPERATIONAL_EXCEPTION":
        row = db.get(OpsException, entity_id)
        if row is None: raise CopilotError("Operational exception not found.", 404)
        ticket = db.scalar(select(AmsTicket).where(AmsTicket.exception_id == row.id).order_by(AmsTicket.created_at.desc()))
        alerts = db.scalars(select(MonAlert).where(MonAlert.linked_exception_id == row.id)).all()
        batches = db.scalars(select(BatchRun).where(BatchRun.linked_exception_id == row.id)).all()
        data = {"entity": {"id": str(row.id), "number": row.exception_number, "status": row.status, "severity": row.severity, "type": row.exception_type, "title": row.title, "description": row.description, "business_impact": row.business_impact, "source_module": row.source_module, "source_entity_type": row.source_entity_type}, "events": [], "alerts": [_alert_dict(a) for a in alerts], "batch_runs": [_batch_dict(b) for b in batches], "diagnostics": [], "traces": [], "logs": [], "exceptions": [], "user_reports": [], "triage_cases": [], "ticket": {"id": str(ticket.id), "number": ticket.ticket_number, "status": ticket.status} if ticket else None}
    elif entity_type == "USER_REPORT":
        row = db.get(AmsUserReport, entity_id)
        if row is None: raise CopilotError("User report not found.", 404)
        ticket = db.get(AmsTicket, row.ticket_id) if row.ticket_id else None
        journey = db.get(SyntheticJourneyRun, row.journey_run_id) if row.journey_run_id else None
        data = {"entity": {"id": str(row.id), "number": row.report_number, "status": row.status, "severity": row.severity, "title": row.title, "description": row.description, "business_impact": row.business_impact, "reporter_name": row.reporter_name, "reporter_persona": row.reporter_persona, "source_module": row.source_module}, "events": [], "alerts": [], "diagnostics": [], "batch_runs": [], "traces": [], "logs": [], "exceptions": [], "user_reports": [], "triage_cases": [], "ticket": {"id": str(ticket.id), "number": ticket.ticket_number, "status": ticket.status} if ticket else None, "journey_run": {"id": str(journey.id), "run_number": journey.run_number, "status": journey.status, "failure_message": journey.failure_message} if journey else None}
    elif entity_type == "MONITORING_ALERT":
        row = db.get(MonAlert, entity_id)
        if row is None: raise CopilotError("Monitoring alert not found.", 404)
        events = db.scalars(select(MonAlertEvent).where(MonAlertEvent.alert_id == row.id).order_by(MonAlertEvent.created_at)).all()
        ticket = db.get(AmsTicket, row.linked_ticket_id) if row.linked_ticket_id else None
        diagnostics = db.scalars(select(ObsDiagnosticCase).where(ObsDiagnosticCase.linked_alert_id == row.id)).all()
        traces = db.scalars(select(ObsTrace).where(ObsTrace.linked_alert_id == row.id)).all()
        data = {"entity": _alert_dict(row), "events": [{"event_type": e.event_type, "from_status": e.from_status, "to_status": e.to_status, "message": e.message, "created_at": _text(e.created_at)} for e in events], "alerts": [_alert_dict(row)], "diagnostics": [{"id": str(d.id), "number": d.diagnostic_number, "title": d.title, "status": d.status, "probable_cause": d.probable_cause, "confidence_level": d.confidence_level} for d in diagnostics], "traces": [{"id": str(t.id), "trace_id": t.trace_id, "status": t.status, "trace_name": t.trace_name, "duration_ms": t.duration_ms} for t in traces], "logs": [], "batch_runs": [], "exceptions": [], "user_reports": [], "triage_cases": [], "ticket": {"id": str(ticket.id), "number": ticket.ticket_number, "status": ticket.status} if ticket else None}
    elif entity_type == "MONITORING_TRIAGE_CASE":
        row = db.get(MonTriageCase, entity_id)
        if row is None: raise CopilotError("Monitoring triage case not found.", 404)
        links = db.scalars(select(MonTriageCaseAlert).where(MonTriageCaseAlert.triage_case_id == row.id)).all()
        alerts = [db.get(MonAlert, link.alert_id) for link in links]
        alerts = [a for a in alerts if a]
        ticket = db.get(AmsTicket, row.linked_ticket_id) if row.linked_ticket_id else None
        diagnostics = db.scalars(select(ObsDiagnosticCase).where(ObsDiagnosticCase.linked_triage_case_id == row.id)).all()
        traces = db.scalars(select(ObsTrace).where(ObsTrace.linked_triage_case_id == row.id)).all()
        data = {"entity": {"id": str(row.id), "number": row.case_number, "title": row.title, "description": row.description, "status": row.status, "severity": row.severity, "suspected_impact": row.suspected_impact, "suspected_root_cause": row.suspected_root_cause, "confidence_level": row.confidence_level}, "events": [], "alerts": [_alert_dict(a) for a in alerts], "diagnostics": [{"id": str(d.id), "number": d.diagnostic_number, "title": d.title, "status": d.status, "probable_cause": d.probable_cause, "confidence_level": d.confidence_level} for d in diagnostics], "traces": [{"id": str(t.id), "trace_id": t.trace_id, "status": t.status, "trace_name": t.trace_name, "duration_ms": t.duration_ms} for t in traces], "logs": [], "batch_runs": [], "exceptions": [], "user_reports": [], "triage_cases": [], "ticket": {"id": str(ticket.id), "number": ticket.ticket_number, "status": ticket.status} if ticket else None}
    elif entity_type == "OBSERVABILITY_DIAGNOSTIC":
        row = db.get(ObsDiagnosticCase, entity_id)
        if row is None: raise CopilotError("Observability diagnostic case not found.", 404)
        trace = db.get(ObsTrace, row.primary_trace_id) if row.primary_trace_id else None
        alert = db.get(MonAlert, row.linked_alert_id) if row.linked_alert_id else None
        ticket = db.get(AmsTicket, row.linked_ticket_id) if row.linked_ticket_id else None
        evidence = db.scalars(select(ObsDiagnosticEvidence).where(ObsDiagnosticEvidence.diagnostic_case_id == row.id)).all()
        data = {"entity": {"id": str(row.id), "number": row.diagnostic_number, "title": row.title, "description": row.description, "status": row.status, "severity": row.severity, "probable_cause": row.probable_cause, "confidence_level": row.confidence_level, "recommended_next_steps": row.recommended_next_steps, "diagnosis_summary": row.diagnosis_summary}, "events": [], "alerts": [_alert_dict(alert)] if alert else [], "diagnostics": [{"id": str(row.id), "number": row.diagnostic_number, "title": row.title, "status": row.status, "probable_cause": row.probable_cause, "confidence_level": row.confidence_level}], "traces": [{"id": str(trace.id), "trace_id": trace.trace_id, "status": trace.status, "trace_name": trace.trace_name, "duration_ms": trace.duration_ms}] if trace else [], "logs": [], "batch_runs": [], "exceptions": [], "user_reports": [], "triage_cases": [], "ticket": {"id": str(ticket.id), "number": ticket.ticket_number, "status": ticket.status} if ticket else None, "evidence": [{"type": e.evidence_type, "title": e.title, "details": e.details, "weight": e.weight} for e in evidence]}
    elif entity_type == "BATCH_RUN":
        row = db.get(BatchRun, entity_id)
        if row is None: raise CopilotError("Batch run not found.", 404)
        steps = db.scalars(select(BatchStepRun).where(BatchStepRun.batch_run_id == row.id).order_by(BatchStepRun.step_order)).all()
        events = db.scalars(select(BatchRunEvent).where(BatchRunEvent.batch_run_id == row.id).order_by(BatchRunEvent.created_at)).all()
        ticket = db.get(AmsTicket, row.linked_ticket_id) if row.linked_ticket_id else None
        exception = db.get(OpsException, row.linked_exception_id) if row.linked_exception_id else None
        diagnostic = db.get(ObsDiagnosticCase, row.linked_diagnostic_case_id) if row.linked_diagnostic_case_id else None
        data = {"entity": _batch_dict(row), "events": [{"event_type": e.event_type, "from_status": e.from_status, "to_status": e.to_status, "message": e.message, "created_at": _text(e.created_at)} for e in events], "steps": [{"step_code": s.step_code, "step_name": s.step_name, "status": s.status, "failure_type": s.failure_type, "failure_message": s.failure_message, "records_processed": s.records_processed, "records_failed": s.records_failed} for s in steps], "alerts": [], "diagnostics": [{"id": str(diagnostic.id), "number": diagnostic.diagnostic_number, "title": diagnostic.title, "status": diagnostic.status, "probable_cause": diagnostic.probable_cause, "confidence_level": diagnostic.confidence_level}] if diagnostic else [], "traces": [], "logs": [], "batch_runs": [_batch_dict(row)], "exceptions": [{"id": str(exception.id), "number": exception.exception_number, "title": exception.title, "status": exception.status, "severity": exception.severity}] if exception else [], "user_reports": [], "triage_cases": [], "ticket": {"id": str(ticket.id), "number": ticket.ticket_number, "status": ticket.status} if ticket else None}
    else:
        raise CopilotError("Unsupported copilot entity type.", 400)
    data["facts"] = _facts(data, entity_type)
    return data


def _facts(data: dict[str, Any], entity_type: str) -> dict[str, Any]:
    entity = data.get("entity", {})
    return {"entity_type": entity_type, "status": entity.get("status"), "severity": entity.get("severity"), "has_ticket": bool(data.get("ticket") or data.get("batch_runs") and any(r.get("ticket_id") for r in data.get("batch_runs", []))), "has_alert": bool(data.get("alerts")), "has_diagnostic": bool(data.get("diagnostics")), "has_batch_failure": any(r.get("status") in ("FAILED", "TIMEOUT", "PARTIAL_SUCCESS") for r in data.get("batch_runs", [])), "has_business_impact": bool(entity.get("business_impact") or entity.get("suspected_impact")), "has_evidence": bool(data.get("evidence") or data.get("traces") or data.get("logs")), "manual": entity_type == "MANUAL"}


def _summary_text(data: dict[str, Any]) -> tuple[str, str, str, str, str, str]:
    entity = data.get("entity", {})
    entity_type = data.get("facts", {}).get("entity_type", "MANUAL")
    label = entity.get("number") or entity.get("title") or entity.get("label") or entity_type
    summary = f"Copilot context for {entity_type.replace('_', ' ').title()} {label}."
    if entity.get("title") or entity.get("short_description"):
        summary += f" {entity.get('title') or entity.get('short_description')}"
    impact = entity.get("business_impact") or entity.get("suspected_impact") or "Business impact is not explicitly recorded in the source artifact."
    technical = entity.get("description") or entity.get("failure_message") or entity.get("probable_cause") or "No additional technical detail is recorded in the source artifact."
    business = f"Source status is {entity.get('status', 'UNKNOWN')} with severity {entity.get('severity', 'UNKNOWN')}. {impact}"
    timeline_items = data.get("events", [])
    timeline = "\n".join(f"{item.get('created_at', 'time unavailable')}: {item.get('event_type', 'EVENT')} — {item.get('message', '')}" for item in timeline_items[:20]) or "No source event timeline is available."
    evidence_parts = []
    for key, label_name in (("alerts", "alerts"), ("diagnostics", "diagnostic cases"), ("traces", "traces"), ("logs", "logs"), ("steps", "batch steps"), ("evidence", "diagnostic evidence")):
        if data.get(key): evidence_parts.append(f"{len(data[key])} {label_name}")
    evidence = "Evidence available: " + (", ".join(evidence_parts) if evidence_parts else "source record only") + "."
    return summary[:2000], impact[:1500], technical[:2500], business[:2000], timeline[:3000], evidence[:3000]


def _snapshot_response(row: CopilotContextSnapshot) -> CopilotContextResponse:
    return CopilotContextResponse.model_validate(row, from_attributes=True)


def _recommendation_response(row: CopilotRecommendation) -> CopilotRecommendationResponse:
    return CopilotRecommendationResponse.model_validate(row, from_attributes=True)


def _plan_response(row: CopilotActionPlan) -> CopilotActionPlanResponse:
    return CopilotActionPlanResponse.model_validate(row, from_attributes=True)


def _message_response(row: CopilotMessage) -> CopilotMessageResponse:
    return CopilotMessageResponse.model_validate(row, from_attributes=True)


def _event_response(row: CopilotActionEvent) -> CopilotActionEventResponse:
    return CopilotActionEventResponse.model_validate(row, from_attributes=True)


def get_session(db: Session, session_id: UUID) -> CopilotSessionResponse:
    session = db.get(CopilotSession, session_id)
    if session is None: raise CopilotError("Copilot session not found.", 404)
    snapshots = db.scalars(select(CopilotContextSnapshot).where(CopilotContextSnapshot.session_id == session.id).order_by(CopilotContextSnapshot.created_at.desc())).all()
    recommendations = db.scalars(select(CopilotRecommendation).where(CopilotRecommendation.session_id == session.id).order_by(CopilotRecommendation.created_at)).all()
    plans = db.scalars(select(CopilotActionPlan).where(CopilotActionPlan.session_id == session.id).order_by(CopilotActionPlan.created_at.desc())).all()
    messages = db.scalars(select(CopilotMessage).where(CopilotMessage.session_id == session.id).order_by(CopilotMessage.created_at)).all()
    events = db.scalars(select(CopilotActionEvent).where(CopilotActionEvent.session_id == session.id).order_by(CopilotActionEvent.created_at)).all()
    primary_summary = None
    if snapshots:
        primary_summary = snapshots[0].summary
    return CopilotSessionResponse(id=session.id, session_number=session.session_number, title=session.title, description=session.description, status=session.status, primary_entity_type=session.primary_entity_type, primary_entity_id=session.primary_entity_id, primary_ticket_id=session.primary_ticket_id, severity=session.severity, confidence_level=session.confidence_level, created_by=session.created_by, created_at=session.created_at, updated_at=session.updated_at, closed_at=session.closed_at, latest_context_snapshot=_snapshot_response(snapshots[0]) if snapshots else None, recommendations=[_recommendation_response(r) for r in recommendations], latest_action_plan=_plan_response(plans[0]) if plans else None, messages=[_message_response(m) for m in messages], action_events=[_event_response(e) for e in events], primary_entity_summary=primary_summary)


def list_sessions(db: Session) -> list[CopilotSessionResponse]:
    return [get_session(db, row.id) for row in db.scalars(select(CopilotSession).order_by(CopilotSession.created_at.desc())).all()]


def create_session(db: Session, request: Any) -> CopilotSessionResponse:
    entity_type = request.primary_entity_type.upper()
    if entity_type not in VALID_ENTITY_TYPES: raise CopilotError("Unsupported copilot entity type.", 400)
    severity = request.severity.upper()
    if severity not in SEVERITIES: raise CopilotError("Unsupported copilot severity.", 400)
    if entity_type != "MANUAL" and request.primary_entity_id is None: raise CopilotError(f"{entity_type} requires an entity_id.", 400)
    now = _now()
    row = CopilotSession(session_number=_next_number(db, CopilotSession.session_number, f"COPILOT-{now:%Y%m%d}-"), title=request.title.strip(), description=request.description.strip(), status="OPEN", primary_entity_type=entity_type, primary_entity_id=request.primary_entity_id, primary_ticket_id=request.primary_ticket_id, severity=severity, confidence_level="UNKNOWN", created_by=request.created_by.strip(), created_at=now, updated_at=now)
    db.add(row); db.flush()
    db.commit()
    if request.build_context:
        build_context(db, row.id)
    if request.generate_recommendations:
        if not request.build_context: build_context(db, row.id)
        generate_recommendations(db, row.id)
    return get_session(db, row.id)


def build_context(db: Session, session_id: UUID) -> CopilotContextResponse:
    session = db.get(CopilotSession, session_id)
    if session is None: raise CopilotError("Copilot session not found.", 404)
    data = _context_for(db, session.primary_entity_type, session.primary_entity_id)
    summary, impact, technical, business, timeline, evidence = _summary_text(data)
    now = _now()
    row = CopilotContextSnapshot(session_id=session.id, snapshot_number=_next_number(db, CopilotContextSnapshot.snapshot_number, f"CTX-{now:%Y%m%d}-"), source_entity_type=session.primary_entity_type, source_entity_id=session.primary_entity_id, summary=summary, impact_summary=impact, technical_summary=technical, business_summary=business, timeline_summary=timeline, evidence_summary=evidence, related_entities={"alerts": data.get("alerts", []), "diagnostics": data.get("diagnostics", []), "batch_runs": data.get("batch_runs", []), "ticket": data.get("ticket")}, raw_context=data, created_by=session.created_by, created_at=now)
    db.add(row)
    facts = data.get("facts", {})
    session.confidence_level = "HIGH" if facts.get("has_evidence") and facts.get("has_diagnostic") else "MEDIUM" if facts.get("has_evidence") else "LOW" if session.primary_entity_type != "MANUAL" else "UNKNOWN"
    session.status = "ANALYZING"
    session.updated_at = now
    db.commit()
    return _snapshot_response(row)


def _latest_snapshot(db: Session, session: CopilotSession) -> CopilotContextSnapshot:
    row = db.scalar(select(CopilotContextSnapshot).where(CopilotContextSnapshot.session_id == session.id).order_by(CopilotContextSnapshot.created_at.desc()))
    if row is None: raise CopilotError("Build a copilot context snapshot before generating assistance.", 409)
    return row


def _recommendation_specs(data: dict[str, Any]) -> list[dict[str, Any]]:
    facts = data.get("facts", {})
    entity_type = facts.get("entity_type") or "MANUAL"
    entity = data.get("entity", {})
    specs: list[dict[str, Any]] = []
    def add(kind: str, title: str, details: str, priority: str, confidence: str, rationale: str, sources: list[str]) -> None:
        specs.append({"recommendation_type": kind, "title": title, "details": details, "priority": priority, "confidence_level": confidence, "rationale": rationale, "source_evidence": {"sources": sources}})
    if facts.get("has_alert") and not facts.get("has_diagnostic"):
        add("CHECK_OBSERVABILITY", "Create or review a diagnostic case from the alert", "Correlate the alert with available traces, logs, and metric samples before assigning a cause.", "HIGH", "MEDIUM", "An alert is present but no linked diagnostic case is recorded.", ["mon_alerts"])
        if entity.get("status") == "OPEN": add("ACKNOWLEDGE_ALERT", "Acknowledge the open monitoring alert", "Record that a support engineer has accepted the alert for investigation.", "HIGH", "HIGH", "The source alert remains OPEN.", ["mon_alerts"])
    if facts.get("has_batch_failure"):
        add("CHECK_BATCH_RUN", "Review the failed batch step", "Inspect failed step status, failure type, record counts, and persisted batch events.", "HIGH", "HIGH", "The context contains a failed, timed-out, or partial batch run.", ["batch_runs", "batch_step_runs", "batch_run_events"])
        if not facts.get("has_ticket"): add("CREATE_TICKET", "Create an AMS ticket for the batch failure", "Review the batch impact and explicitly create a ticket through the batch support action when appropriate.", "HIGH", "MEDIUM", "The batch failure has no linked ticket in the assembled context.", ["batch_runs"])
    if entity_type == "USER_REPORT" and facts.get("has_business_impact") and not facts.get("has_ticket"):
        add("CREATE_TICKET", "Create an AMS ticket from the user report", "Review the reported business impact and explicitly create a linked incident if support work is required.", "HIGH", "HIGH", "The user report describes business impact but has no linked ticket.", ["ams_user_reports"])
    if facts.get("has_diagnostic") and not facts.get("has_ticket"):
        add("CREATE_TICKET", "Create an AMS ticket from the diagnostic case", "Review the evidence-backed probable cause and explicitly link or create an AMS incident.", "MEDIUM", "HIGH", "A diagnostic case has a probable cause or evidence but no linked ticket.", ["obs_diagnostic_cases"])
    if entity_type == "AMS_TICKET" or data.get("ticket"):
        add("UPDATE_TICKET", "Generate a ticket work note draft", "Prepare an internal support update for engineer review; do not apply it automatically.", "MEDIUM", "MEDIUM", "The context includes an AMS ticket and work-note drafting is a safe governed action.", ["ams_tickets"])
    if facts.get("has_diagnostic") or facts.get("has_business_impact"):
        add("COMMUNICATE_STATUS", "Generate a customer update draft", "Prepare a plain-language acknowledgement and investigation status update for human review.", "MEDIUM", "MEDIUM", "The context contains either business impact or a deterministic diagnosis.", ["ams_tickets", "obs_diagnostic_cases", "ams_user_reports"])
    add("GENERATE_INVESTIGATION_CHECKLIST", "Generate an investigation checklist", "Create a reviewable checklist based on the source artifact and available evidence.", "LOW", "HIGH", "A checklist is a non-destructive support aid and does not execute any underlying action.", [entity_type.lower()])
    return specs


def generate_recommendations(db: Session, session_id: UUID) -> list[CopilotRecommendationResponse]:
    session = db.get(CopilotSession, session_id)
    if session is None: raise CopilotError("Copilot session not found.", 404)
    snapshot = _latest_snapshot(db, session)
    data = snapshot.raw_context or {}
    for spec in _recommendation_specs(data):
        existing = db.scalar(select(CopilotRecommendation).where(CopilotRecommendation.session_id == session.id, CopilotRecommendation.recommendation_type == spec["recommendation_type"], CopilotRecommendation.title == spec["title"], CopilotRecommendation.status.in_(ACTIVE_RECOMMENDATION_STATUSES)).order_by(CopilotRecommendation.created_at.desc()))
        if existing: continue
        db.add(CopilotRecommendation(session_id=session.id, snapshot_id=snapshot.id, **spec, status="PROPOSED", created_at=_now(), updated_at=_now()))
    session.status = "RECOMMENDATIONS_READY"; session.updated_at = _now()
    db.commit()
    return [_recommendation_response(row) for row in db.scalars(select(CopilotRecommendation).where(CopilotRecommendation.session_id == session.id).order_by(CopilotRecommendation.created_at)).all()]


def generate_action_plan(db: Session, session_id: UUID) -> CopilotActionPlanResponse:
    session = db.get(CopilotSession, session_id)
    if session is None: raise CopilotError("Copilot session not found.", 404)
    snapshot = _latest_snapshot(db, session)
    existing = db.scalar(select(CopilotActionPlan).where(CopilotActionPlan.session_id == session.id, CopilotActionPlan.status.in_(('DRAFT', 'READY_FOR_REVIEW', 'APPROVED'))).order_by(CopilotActionPlan.created_at.desc()))
    if existing: return _plan_response(existing)
    recommendations = db.scalars(select(CopilotRecommendation).where(CopilotRecommendation.session_id == session.id, CopilotRecommendation.status.in_(ACTIVE_RECOMMENDATION_STATUSES)).order_by(CopilotRecommendation.created_at)).all()
    steps = [{"order": index, "action": r.recommendation_type, "title": r.title, "requires_human_approval": True, "status": "PENDING_REVIEW"} for index, r in enumerate(recommendations, 1)]
    if not steps: steps = [{"order": 1, "action": "REVIEW_CONTEXT", "title": "Review assembled support context", "requires_human_approval": True, "status": "PENDING_REVIEW"}]
    severity = session.severity
    risk = "HIGH" if severity == "CRITICAL" else "MEDIUM" if severity == "HIGH" else "LOW"
    now = _now()
    row = CopilotActionPlan(session_id=session.id, snapshot_id=snapshot.id, plan_number=_next_number(db, CopilotActionPlan.plan_number, f"PLAN-{now:%Y%m%d}-"), title=f"Support investigation plan for {session.title}", summary="Review the deterministic recommendations in order. Every step requires explicit human approval and this plan does not execute underlying support actions.", status="READY_FOR_REVIEW", steps=steps, risk_level=risk, requires_human_approval=True, created_at=now, updated_at=now)
    db.add(row); db.flush()
    db.add(CopilotActionEvent(session_id=session.id, action_code="GENERATE_ACTION_PLAN", event_type="ACTION_PLAN_CREATED", message=f"Action plan {row.plan_number} created for human review.", event_payload={"plan_id": str(row.id)}, created_by=session.created_by, created_at=now))
    session.status = "ACTION_PLAN_READY"; session.updated_at = now
    db.commit()
    return _plan_response(row)


def _message_content(message_type: str, data: dict[str, Any]) -> tuple[str, str]:
    entity = data.get("entity", {})
    facts = data.get("facts", {})
    label = entity.get("number") or entity.get("title") or "the support artifact"
    diagnostic = (data.get("diagnostics") or [{}])[0]
    if message_type == "WORK_NOTE_DRAFT":
        content = (f"Support investigation update:\nCurrent status: {entity.get('status', 'UNKNOWN')}.\nImpacted module: {entity.get('source_module', 'EOS support modules')}.\nObserved symptoms: {entity.get('description') or entity.get('failure_message') or entity.get('short_description') or 'See the assembled context snapshot.'}\nEvidence reviewed: {data.get('facts', {}).get('has_evidence', False) and 'deterministic source, event, and evidence records.' or 'source record only.'}\nCurrent hypothesis: {diagnostic.get('probable_cause') or entity.get('probable_cause') or 'No cause is confirmed from the available evidence.'}\nNext action: Review the generated checklist and have a support engineer validate each recommendation.")
        return "Ticket work note draft", content
    if message_type == "CUSTOMER_UPDATE_DRAFT":
        content = (f"We acknowledge the reported issue associated with {label}. The support team is reviewing the available business and technical evidence. Current impact: {entity.get('business_impact') or entity.get('suspected_impact') or 'Impact is still being assessed.'} The next update will follow after the support engineer validates the investigation findings.")
        return "Customer update draft", content
    if message_type == "INVESTIGATION_CHECKLIST":
        items = ["- Review the source status, severity, and business impact."]
        if facts.get("has_alert"): items += ["- Confirm alert occurrence count and last seen time.", "- Review linked monitoring and observability evidence."]
        if facts.get("has_batch_failure"): items += ["- Review the failed batch step and record counts.", "- Confirm whether exception, ticket, and diagnostic records exist.", "- Confirm whether any rerun decision is safe for a human operator."]
        if facts.get("has_diagnostic"): items += ["- Validate the probable cause against the evidence records.", "- Review recommended next steps before communicating externally."]
        if entity.get("status") in ("OPEN", "NEW", "SUBMITTED"): items.append("- Record acknowledgement and current owner through the existing support module.")
        return "Investigation checklist", "\n".join(items)
    return "Support context summary", f"Deterministic support context assembled for {label}. Review the snapshot and related evidence before taking manual action."


def generate_message(db: Session, session_id: UUID, message_type: str) -> CopilotMessageResponse:
    session = db.get(CopilotSession, session_id)
    if session is None: raise CopilotError("Copilot session not found.", 404)
    snapshot = _latest_snapshot(db, session)
    message_type = message_type.upper()
    if message_type not in ("WORK_NOTE_DRAFT", "CUSTOMER_UPDATE_DRAFT", "INVESTIGATION_CHECKLIST"):
        raise CopilotError("Unsupported copilot message type.", 400)
    existing = db.scalar(select(CopilotMessage).where(CopilotMessage.session_id == session.id, CopilotMessage.message_type == message_type, CopilotMessage.status == "DRAFT").order_by(CopilotMessage.created_at.desc()))
    if existing: return _message_response(existing)
    title, content = _message_content(message_type, snapshot.raw_context or {})
    now = _now()
    row = CopilotMessage(session_id=session.id, message_type=message_type, title=title, content=content, status="DRAFT", target_entity_type=session.primary_entity_type, target_entity_id=session.primary_entity_id, created_by=session.created_by, created_at=now, updated_at=now)
    db.add(row); db.flush()
    db.add(CopilotActionEvent(session_id=session.id, action_code=f"GENERATE_{message_type}", event_type="DRAFT_CREATED", target_entity_type=session.primary_entity_type, target_entity_id=session.primary_entity_id, message=f"{title} created for human review.", event_payload={"message_id": str(row.id)}, created_by=session.created_by, created_at=now))
    db.commit()
    return _message_response(row)


def accept_recommendation(db: Session, recommendation_id: UUID) -> CopilotRecommendationResponse:
    row = db.get(CopilotRecommendation, recommendation_id)
    if row is None: raise CopilotError("Copilot recommendation not found.", 404)
    if row.status != "PROPOSED": raise CopilotError(f"Recommendation cannot be accepted from {row.status}.")
    now = _now(); old = row.status; row.status = "ACCEPTED"; row.accepted_at = now; row.updated_at = now
    db.add(CopilotActionEvent(session_id=row.session_id, action_code=row.recommendation_type, event_type="ACTION_ACCEPTED", from_status=old, to_status="ACCEPTED", message=f"Recommendation accepted for human follow-up: {row.title}.", event_payload={"recommendation_id": str(row.id), "execution": "not_performed"}, created_by="support-engineer", created_at=now))
    db.commit()
    return _recommendation_response(row)


def dismiss_recommendation(db: Session, recommendation_id: UUID) -> CopilotRecommendationResponse:
    row = db.get(CopilotRecommendation, recommendation_id)
    if row is None: raise CopilotError("Copilot recommendation not found.", 404)
    if row.status != "PROPOSED": raise CopilotError(f"Recommendation cannot be dismissed from {row.status}.")
    now = _now(); old = row.status; row.status = "DISMISSED"; row.dismissed_at = now; row.updated_at = now
    db.add(CopilotActionEvent(session_id=row.session_id, action_code=row.recommendation_type, event_type="ACTION_DISMISSED", from_status=old, to_status="DISMISSED", message=f"Recommendation dismissed: {row.title}.", event_payload={"recommendation_id": str(row.id), "execution": "not_performed"}, created_by="support-engineer", created_at=now))
    db.commit()
    return _recommendation_response(row)


def close_session(db: Session, session_id: UUID) -> CopilotSessionResponse:
    row = db.get(CopilotSession, session_id)
    if row is None: raise CopilotError("Copilot session not found.", 404)
    if row.status == "CLOSED": return get_session(db, row.id)
    now = _now(); row.status = "CLOSED"; row.closed_at = now; row.updated_at = now
    db.add(CopilotActionEvent(session_id=row.id, action_code="CLOSE_SESSION", event_type="MANUAL_ACTION_RECORDED", from_status="OPEN", to_status="CLOSED", message="Copilot session closed by support engineer.", event_payload={"execution": "session_only"}, created_by=row.created_by, created_at=now))
    db.commit()
    return get_session(db, row.id)


def get_summary(db: Session) -> CopilotSummary:
    return CopilotSummary(open_sessions=db.scalar(select(func.count(CopilotSession.id)).where(CopilotSession.status.in_(OPEN_SESSION_STATUSES))) or 0, recommendations_proposed=db.scalar(select(func.count(CopilotRecommendation.id)).where(CopilotRecommendation.status == "PROPOSED")) or 0, recommendations_accepted=db.scalar(select(func.count(CopilotRecommendation.id)).where(CopilotRecommendation.status == "ACCEPTED")) or 0, action_plans_ready=db.scalar(select(func.count(CopilotActionPlan.id)).where(CopilotActionPlan.status.in_(("READY_FOR_REVIEW", "APPROVED")))) or 0, draft_messages=db.scalar(select(func.count(CopilotMessage.id)).where(CopilotMessage.status == "DRAFT")) or 0, safe_actions_enabled=db.scalar(select(func.count(CopilotSafeAction.id)).where(CopilotSafeAction.enabled.is_(True))) or 0)


def list_safe_actions(db: Session) -> list[CopilotSafeActionResponse]:
    return [CopilotSafeActionResponse.model_validate(row, from_attributes=True) for row in db.scalars(select(CopilotSafeAction).order_by(CopilotSafeAction.action_code)).all()]


def analyze(db: Session, request: Any) -> CopilotSessionResponse:
    session_request = type("AnalyzeSession", (), {"title": request.title, "description": "Deterministic copilot analysis session.", "primary_entity_type": request.entity_type, "primary_entity_id": request.entity_id, "primary_ticket_id": None, "severity": "MEDIUM", "created_by": "support-engineer", "build_context": False, "generate_recommendations": False})()
    session = create_session(db, session_request)
    build_context(db, session.id)
    generate_recommendations(db, session.id)
    generate_action_plan(db, session.id)
    generate_message(db, session.id, "INVESTIGATION_CHECKLIST")
    return get_session(db, session.id)
