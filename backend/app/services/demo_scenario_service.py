"""Deterministic, presenter-controlled demo scenario orchestration."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agent_chat import AgentActionExecution, AgentActionProposal, AgentCase, AgentChatSession
from app.models.ams import AmsTicket
from app.models.batch import BatchRun
from app.models.demo_scenario import DemoScenario, DemoScenarioArtifact, DemoScenarioEvent, DemoScenarioRun, DemoScenarioStep
from app.models.monitoring import MonAlert
from app.models.operations import OpsException
from app.models.synthetic_users import SyntheticUser
from app.models.user_reports import AmsUserReport
from app.models.warehouse import Order
from app.schemas.agent_chat import AgentHandoffRequest, AgentIntakeRequest
from app.schemas.monitoring import TriageCaseCreate
from app.schemas.user_reports import UserReportCreate
from app.services import agent_orchestrator_service, ams_ticket_service, batch_service, monitoring_service, operations_exception_service, user_report_service


class DemoScenarioError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _run_number(db: Session) -> str:
    current = db.scalar(select(func.max(DemoScenarioRun.run_id)).where(DemoScenarioRun.run_id.like("DEMO-RUN-%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            pass
    return f"DEMO-RUN-{sequence:04d}"


SCENARIO_DEFINITIONS: dict[str, dict[str, Any]] = {
    "STUCK_FULFILLMENT_ORDER": {
        "title": "Stuck Fulfillment Order",
        "description": "A warehouse order cannot progress because allocation or picking is blocked.",
        "business_value": "Connect an operational exception to an agent-ready investigation and a human-approved local work-note draft.",
        "default_experience": "operations",
        "sort_order": 10,
        "steps": [
            ("INDUCE_ORDER_ISSUE", "Induce stuck order", "Create a safe local fulfillment exception for a synthetic order.", "Show that EOS can reproduce an operational symptom without changing inventory or shipping state.", "CREATE_ARTIFACTS", "Operations sees a local exception and linked AMS ticket."),
            ("REVIEW_EXCEPTION", "Review operations exception", "Open the exception and explain the business impact.", "Point out the evidence that allocation or picking is blocked.", "OPEN_LINK", "The exception detail is available."),
            ("REVIEW_TICKET", "Review AMS ticket", "Open the linked local AMS ticket.", "Explain how the issue becomes an agent-ready support case.", "OPEN_LINK", "The ticket references the originating exception."),
            ("START_AGENT_INVESTIGATION", "Investigate with Agent", "Start the deterministic agent handoff from the ticket.", "Show evidence, knowledge, timeline, and approval controls in one workspace.", "START_AGENT_INVESTIGATION", "An agent case, session, workspace, and safe proposals are linked."),
            ("REVIEW_WORKSPACE", "Review investigation workspace", "Open the workspace and review evidence and knowledge.", "Call out that Stage 1 guidance is read-only and model assistance is off by default.", "OPEN_LINK", "The workspace shows source context and proposed safe actions."),
            ("REVIEW_DRAFTS", "Review work-note draft", "Open the action proposals and dry-run a draft action.", "Demonstrate that a draft is local and requires explicit approval.", "GENERATE_DRAFTS", "A deterministic draft preview is available."),
            ("APPROVE_SAFE_ACTION", "Approve one safe action", "Approve and, if desired, execute one predefined local action.", "Read the safety warning before using the Stage 2 controls.", "APPROVE_SAFE_ACTION", "Only the explicitly approved action may execute."),
            ("VIEW_AUDIT", "Review action audit", "Open the action audit and timeline.", "Show who approved the action and the local result.", "VIEW_AUDIT", "Approval and execution events are visible."),
            ("COMPLETE_SCENARIO", "Complete storyline", "Summarize the business outcome for the audience.", "Close with the human-in-the-loop boundary.", "COMPLETE_SCENARIO", "The scenario is marked completed by the presenter."),
        ],
    },
    "BATCH_FAILURE_RECOVERY": {
        "title": "Batch Failure Recovery",
        "description": "A warehouse replenishment or fulfillment batch job fails and creates downstream operational risk.",
        "business_value": "Show how a failed batch becomes explainable through operational evidence and a human-reviewed checklist.",
        "default_experience": "operations",
        "sort_order": 20,
        "steps": [
            ("INDUCE_BATCH_FAILURE", "Trigger failed batch", "Run the deterministic local batch failure simulation.", "Introduce the failure as an operational event, not an autonomous repair.", "CREATE_ARTIFACTS", "A failed batch run and local exception are created."),
            ("REVIEW_BATCH", "Review batch failure", "Open the failed batch run and its event history.", "Identify the failed step and downstream business risk.", "OPEN_LINK", "Batch evidence and failure details are visible."),
            ("REVIEW_ALERT", "Review alert context", "Open the linked local alert or diagnostic context.", "Show how operational signals support the investigation.", "OPEN_LINK", "The alert context is linked to the scenario."),
            ("START_AGENT_INVESTIGATION", "Investigate with Agent", "Start the agent handoff from the AMS ticket.", "Review deterministic evidence and runbook knowledge.", "START_AGENT_INVESTIGATION", "An agent workspace is linked."),
            ("REVIEW_KNOWLEDGE", "Review runbook knowledge", "Review retrieved knowledge and known errors.", "Explain the likely cause while keeping remediation human-controlled.", "OPEN_LINK", "Knowledge citations are visible."),
            ("APPROVE_CHECKLIST", "Approve checklist draft", "Review and approve a next-steps checklist proposal.", "Emphasize that the checklist is a local draft and not an execution command.", "APPROVE_SAFE_ACTION", "The presenter controls approval and execution."),
            ("VIEW_TIMELINE", "Review timeline", "Review evidence, approval, and action events.", "Connect the batch symptom to a traceable support outcome.", "VIEW_AUDIT", "The timeline is complete and auditable."),
            ("COMPLETE_SCENARIO", "Complete storyline", "Summarize the recovery plan and ownership.", "Close with the Stage 1 and Stage 2 boundaries.", "COMPLETE_SCENARIO", "The scenario is marked completed."),
        ],
    },
    "USER_REPORTED_SHIPMENT_DELAY": {
        "title": "User-Reported Shipment Delay",
        "description": "A business user reports that a shipment is delayed or missing from expected status.",
        "business_value": "Demonstrate a user-reported issue becoming a grounded investigation with a customer-update draft.",
        "default_experience": "agentic",
        "sort_order": 30,
        "steps": [
            ("CREATE_USER_REPORT", "Create user report", "Create a synthetic report for a shipment delay.", "Start from the user experience and keep the report entirely local.", "CREATE_ARTIFACTS", "A synthetic report and local AMS ticket are linked."),
            ("REVIEW_REPORT", "Review user report", "Open the report and confirm the business impact.", "Show the original user wording as source context.", "OPEN_LINK", "The report is available with its ticket link."),
            ("REVIEW_TICKET", "Review linked ticket", "Open the local AMS ticket.", "Explain the handoff from user report to AMS support.", "OPEN_LINK", "The local ticket is linked to the report."),
            ("START_AGENT_INVESTIGATION", "Investigate with Agent", "Start the agent investigation from the ticket.", "Review evidence and ask a read-only Stage 1 question.", "START_AGENT_INVESTIGATION", "An agent workspace is linked."),
            ("REVIEW_DRAFT", "Review customer-update draft", "Review the deterministic customer-update draft.", "Clarify that this is a draft and nothing is sent externally.", "GENERATE_DRAFTS", "A local draft proposal is available."),
            ("APPROVE_INTERNAL_NOTE", "Approve internal note", "Approve an internal EOS case note if appropriate.", "Use explicit approval and show the audit entry.", "APPROVE_SAFE_ACTION", "Only the approved local note can be recorded."),
            ("VIEW_AUDIT", "Review audit", "Review the action result and timeline.", "Show complete traceability for the support decision.", "VIEW_AUDIT", "The audit records approval and local result."),
            ("COMPLETE_SCENARIO", "Complete storyline", "Summarize the customer-facing outcome without sending a message.", "Reinforce the no-external-send boundary.", "COMPLETE_SCENARIO", "The scenario is marked completed."),
        ],
    },
    "OBSERVABILITY_ALERT_NOISE_ROOT_CAUSE": {
        "title": "Observability Alert Noise to Root Cause",
        "description": "Multiple alerts appear, but the agent helps group evidence and identify the likely operational cause.",
        "business_value": "Show signal grouping, evidence-based reasoning, and a local acknowledgement action without resolving production objects.",
        "default_experience": "observability",
        "sort_order": 40,
        "steps": [
            ("GENERATE_ALERT_NOISE", "Generate alert noise", "Create a deterministic local alert cluster.", "Explain that alerts are symptoms and are not automatically resolved.", "CREATE_ARTIFACTS", "Multiple local alerts are available."),
            ("GROUP_ALERTS", "Group alert context", "Open the local triage case and grouped alerts.", "Show how related signals narrow investigation scope.", "OPEN_LINK", "A monitoring triage case links the alert cluster."),
            ("REVIEW_ALERT", "Review alert evidence", "Review alert events and known errors.", "Separate signal correlation from an unverified root cause.", "OPEN_LINK", "Alert evidence is visible in the investigation context."),
            ("START_AGENT_INVESTIGATION", "Investigate with Agent", "Start the agent investigation from the local AMS ticket.", "Show the evidence timeline and safe action proposals.", "START_AGENT_INVESTIGATION", "An agent workspace is linked."),
            ("REVIEW_EVIDENCE", "Review grouped evidence", "Review the evidence and knowledge citations.", "Keep the model-assisted path optional and read-only.", "OPEN_LINK", "Evidence and knowledge support the likely cause."),
            ("ACKNOWLEDGE_LOCAL_ALERT", "Acknowledge local alert", "Review and approve a local acknowledgement proposal.", "Clarify that acknowledgement is not resolution or remediation.", "APPROVE_SAFE_ACTION", "Only a human-approved local acknowledgement may execute."),
            ("VIEW_AUDIT", "Review audit", "Open the action audit and scenario timeline.", "Show the complete chain from signal to human decision.", "VIEW_AUDIT", "Audit events are visible."),
            ("COMPLETE_SCENARIO", "Complete storyline", "Summarize the root-cause hypothesis and next human action.", "Close without claiming production remediation.", "COMPLETE_SCENARIO", "The scenario is marked completed."),
        ],
    },
}


def _definition(code: str) -> dict[str, Any]:
    definition = SCENARIO_DEFINITIONS.get(code.upper())
    if definition is None:
        raise DemoScenarioError("Unknown demo scenario.", 404)
    return definition


def _scenario_row(db: Session, code: str) -> DemoScenario:
    row = db.scalar(select(DemoScenario).where(DemoScenario.scenario_code == code.upper()))
    if row is None:
        definition = _definition(code)
        row = DemoScenario(scenario_code=code.upper(), title=definition["title"], description=definition["description"], business_value=definition["business_value"], default_experience=definition["default_experience"], sort_order=definition["sort_order"], is_enabled=True)
        db.add(row)
        db.flush()
    if not row.is_enabled:
        raise DemoScenarioError("Demo scenario is disabled.", 409)
    return row


def _step_dict(step: DemoScenarioStep) -> dict[str, Any]:
    return {"id": step.id, "step_code": step.step_code, "step_title": step.step_title, "step_description": step.step_description, "presenter_instruction": step.presenter_instruction, "expected_result": step.expected_result, "action_type": step.action_type, "step_order": step.step_order, "status": step.status, "started_at": step.started_at, "completed_at": step.completed_at, "target_url": step.target_url, "target_object_type": step.target_object_type, "target_object_id": step.target_object_id, "instructions": step.instructions}


def _artifact_dict(item: DemoScenarioArtifact) -> dict[str, Any]:
    return {"id": item.id, "artifact_type": item.artifact_type, "artifact_id": item.artifact_id, "artifact_display": item.artifact_display, "artifact_url": item.artifact_url, "metadata_json": item.metadata_json, "created_at": item.created_at}


def _event_dict(item: DemoScenarioEvent) -> dict[str, Any]:
    return {"id": item.id, "event_type": item.event_type, "event_title": item.event_title, "event_description": item.event_description, "event_timestamp": item.event_timestamp, "source_type": item.source_type, "source_id": item.source_id, "metadata_json": item.metadata_json, "created_at": item.created_at}


def _next_action(db: Session, run: DemoScenarioRun) -> dict[str, Any] | None:
    step = db.scalar(select(DemoScenarioStep).where(DemoScenarioStep.run_id == run.id, DemoScenarioStep.status == "ACTIVE").order_by(DemoScenarioStep.step_order))
    if step is None:
        return None
    return {"step_code": step.step_code, "title": step.step_title, "action_type": step.action_type, "presenter_instruction": step.presenter_instruction, "expected_result": step.expected_result, "target_url": step.target_url, "safe_boundary": "Presenter-controlled local EOS demo data only. No real model, external send, shell command, SQL, or autonomous remediation."}


def _run_dict(db: Session, run: DemoScenarioRun, include_children: bool = True) -> dict[str, Any]:
    steps = db.scalars(select(DemoScenarioStep).where(DemoScenarioStep.run_id == run.id).order_by(DemoScenarioStep.step_order)).all() if include_children else []
    artifacts = db.scalars(select(DemoScenarioArtifact).where(DemoScenarioArtifact.run_id == run.id).order_by(DemoScenarioArtifact.created_at, DemoScenarioArtifact.id)).all() if include_children else []
    events = db.scalars(select(DemoScenarioEvent).where(DemoScenarioEvent.run_id == run.id).order_by(DemoScenarioEvent.event_timestamp, DemoScenarioEvent.id)).all() if include_children else []
    scenario = db.scalar(select(DemoScenario).where(DemoScenario.scenario_code == run.scenario_code))
    return {"id": run.id, "run_id": run.run_id, "scenario_code": run.scenario_code, "scenario_title": scenario.title if scenario else run.scenario_code, "status": run.status, "current_step_code": run.current_step_code, "started_at": run.started_at, "completed_at": run.completed_at, "reset_at": run.reset_at, "created_by_role": run.created_by_role, "summary": run.summary, "outcome_summary": run.outcome_summary, "steps": [_step_dict(x) for x in steps], "artifacts": [_artifact_dict(x) for x in artifacts], "timeline": [_event_dict(x) for x in events], "next_action": _next_action(db, run)}


def _event(db: Session, run: DemoScenarioRun, event_type: str, title: str, description: str, source_type: str | None = None, source_id: UUID | None = None, metadata: dict | None = None) -> None:
    db.add(DemoScenarioEvent(run_id=run.id, event_type=event_type, event_title=title, event_description=description, event_timestamp=_now(), source_type=source_type, source_id=source_id, metadata_json=metadata))


def _artifact(db: Session, run: DemoScenarioRun, artifact_type: str, artifact_id: UUID, display: str, url: str | None, metadata: dict | None = None) -> DemoScenarioArtifact:
    existing = db.scalar(select(DemoScenarioArtifact).where(DemoScenarioArtifact.run_id == run.id, DemoScenarioArtifact.artifact_type == artifact_type, DemoScenarioArtifact.artifact_id == artifact_id))
    if existing:
        return existing
    item = DemoScenarioArtifact(run_id=run.id, artifact_type=artifact_type, artifact_id=artifact_id, artifact_display=display[:240], artifact_url=url, metadata_json=metadata)
    db.add(item)
    db.flush()
    return item


def _target(run: DemoScenarioRun, step_code: str, object_type: str, object_id: UUID, url: str) -> None:
    step = next((item for item in run.steps if item.step_code == step_code), None)
    if step:
        step.target_object_type, step.target_object_id, step.target_url = object_type, object_id, url


def _initial_artifacts(db: Session, run: DemoScenarioRun, role: str) -> None:
    code = run.scenario_code
    if code == "STUCK_FULFILLMENT_ORDER":
        order = db.scalar(select(Order).order_by(Order.created_at).limit(1))
        if order is None:
            order = Order(order_number=f"DEMO-ORDER-{run.run_id}", customer_name="EOS Demo Customer", order_type="STANDARD", priority="HIGH", status="ALLOCATING")
            db.add(order)
            db.flush()
        exception = operations_exception_service.create_or_refresh_exception(db, exception_type="ALLOCATION_BLOCKED", severity="HIGH", source_entity_type="ORDER", source_entity_id=order.id, source_reference=order.order_number, title=f"Fulfillment is stuck for {order.order_number}", description="Synthetic demo order cannot progress because allocation evidence is incomplete.", detection_method="DEMO_SCENARIO", business_impact="Shipment fulfillment is delayed for the demo order.", technical_context={"scenario_run_id": run.run_id})
        db.flush()
        ticket_response = ams_ticket_service.create_ticket_from_exception(db, exception.id)
        ticket = db.get(AmsTicket, ticket_response.id)
        _artifact(db, run, "WAREHOUSE_ORDER", order.id, order.order_number, f"/operations/orders/{order.id}")
        _artifact(db, run, "OPERATIONS_EXCEPTION", exception.id, exception.exception_number, f"/operations/exceptions/{exception.id}")
        if ticket:
            _artifact(db, run, "AMS_TICKET", ticket.id, ticket.ticket_number, f"/ams/tickets/{ticket.id}")
        _target(run, "REVIEW_EXCEPTION", "OPERATIONS_EXCEPTION", exception.id, f"/operations/exceptions/{exception.id}")
        _target(run, "REVIEW_TICKET", "AMS_TICKET", ticket.id if ticket else exception.id, f"/ams/tickets/{ticket.id if ticket else exception.id}")
        _event(db, run, "ISSUE_INDUCED", "Synthetic fulfillment issue created", "A local allocation-blocked exception and AMS ticket were created for demo use.", "OPS_EXCEPTION", exception.id)
    elif code == "BATCH_FAILURE_RECOVERY":
        result = batch_service.run_simulation(db, "inventory-reconciliation-failure", create_exception=True, create_ticket=True, create_observability=True)
        batch = db.get(BatchRun, result.run.id)
        if batch is None:
            raise DemoScenarioError("Batch failure simulation did not return a batch run.")
        _artifact(db, run, "BATCH_RUN", batch.id, batch.run_number, f"/batch/runs/{batch.id}")
        if result.exception_id:
            _artifact(db, run, "OPERATIONS_EXCEPTION", result.exception_id, result.exception_number or "Operations exception", f"/operations/exceptions/{result.exception_id}")
        if result.ticket_id:
            _artifact(db, run, "AMS_TICKET", result.ticket_id, result.ticket_number or "AMS ticket", f"/ams/tickets/{result.ticket_id}")
        if result.diagnostic_case_id:
            _artifact(db, run, "DIAGNOSTIC_CASE", result.diagnostic_case_id, result.diagnostic_number or "Diagnostic case", f"/observability/diagnostic-cases/{result.diagnostic_case_id}")
        _target(run, "REVIEW_BATCH", "BATCH_RUN", batch.id, f"/batch/runs/{batch.id}")
        _event(db, run, "ISSUE_INDUCED", "Synthetic batch failure created", "A deterministic failed batch, local exception, ticket, and diagnostic context were created.", "BATCH_RUN", batch.id)
    elif code == "USER_REPORTED_SHIPMENT_DELAY":
        reporter = db.scalar(select(SyntheticUser).order_by(SyntheticUser.created_at).limit(1))
        request = UserReportCreate(reporter_user_id=reporter.id if reporter else None, reporter_name=reporter.display_name if reporter else "Synthetic Demo User", reporter_email=reporter.email if reporter else "demo.user@eos.local", reporter_persona=reporter.persona if reporter else "BUSINESS_USER", report_channel="SYNTHETIC_USER", source_module="SHIPMENT_TRACKING", affected_entity_type="SHIPMENT", title="Shipment has not progressed", description="The shipment remains in the expected handoff status longer than the business user expected.", business_impact="Customer delivery confidence is at risk and support needs an evidence-based update.", severity="HIGH", create_ticket=True)
        response = user_report_service.create_report(db, request)
        report = db.get(AmsUserReport, response.id)
        if report is None:
            raise DemoScenarioError("Synthetic user report was not created.")
        _artifact(db, run, "USER_REPORT", report.id, report.report_number, f"/user-reports/{report.id}")
        if report.ticket_id:
            ticket = db.get(AmsTicket, report.ticket_id)
            _artifact(db, run, "AMS_TICKET", report.ticket_id, ticket.ticket_number if ticket else "AMS ticket", f"/ams/tickets/{report.ticket_id}")
            _target(run, "REVIEW_TICKET", "AMS_TICKET", report.ticket_id, f"/ams/tickets/{report.ticket_id}")
        _target(run, "REVIEW_REPORT", "USER_REPORT", report.id, f"/user-reports/{report.id}")
        _event(db, run, "ISSUE_INDUCED", "Synthetic shipment delay report created", "A local user report and linked AMS ticket were created; no customer communication was sent.", "USER_REPORT", report.id)
    elif code == "OBSERVABILITY_ALERT_NOISE_ROOT_CAUSE":
        result = monitoring_service.run_simulation(db, "api-latency-cascade")
        alert_ids = [item.id for item in result.alerts]
        for item in result.alerts:
            _artifact(db, run, "OBSERVABILITY_ALERT", item.id, item.alert_number, f"/monitoring/alerts/{item.id}", {"rule_code": item.rule_code, "severity": item.severity})
        triage = monitoring_service.create_triage_case(db, TriageCaseCreate(title="Grouped demo alert noise", description="Synthetic alert symptoms are grouped for deterministic investigation.", severity="HIGH", suspected_impact="Warehouse workflow latency may affect order progress.", suspected_root_cause="Shared application dependency degradation is a hypothesis only.", confidence_level="MEDIUM", analysis_notes="Created by the guided EOS demo scenario.", alert_ids=alert_ids))
        _artifact(db, run, "MONITORING_TRIAGE", triage.id, triage.case_number, f"/monitoring/triage-cases/{triage.id}")
        ticket_response = ams_ticket_service.create_ticket_from_triage_case(db, triage.id)
        if ticket_response:
            _artifact(db, run, "AMS_TICKET", ticket_response.id, ticket_response.ticket_number, f"/ams/tickets/{ticket_response.id}")
        _target(run, "GROUP_ALERTS", "MONITORING_TRIAGE", triage.id, f"/monitoring/triage-cases/{triage.id}")
        _target(run, "REVIEW_ALERT", "MONITORING_TRIAGE", triage.id, f"/monitoring/triage-cases/{triage.id}")
        _event(db, run, "ISSUE_INDUCED", "Synthetic observability alert cluster created", "A deterministic local alert cluster and monitoring triage case were created; alerts remain unresolved.", "MONITORING_TRIAGE", triage.id)
    else:
        raise DemoScenarioError("Unsupported demo scenario.")
    db.flush()


def _handoff(db: Session, run: DemoScenarioRun) -> None:
    ticket = db.scalar(select(AmsTicket).join(DemoScenarioArtifact, DemoScenarioArtifact.artifact_id == AmsTicket.id).where(DemoScenarioArtifact.run_id == run.id, DemoScenarioArtifact.artifact_type == "AMS_TICKET").order_by(DemoScenarioArtifact.created_at).limit(1))
    if ticket is None:
        raise DemoScenarioError("Scenario has no local AMS ticket to hand off.")
    existing = db.scalar(select(DemoScenarioArtifact).where(DemoScenarioArtifact.run_id == run.id, DemoScenarioArtifact.artifact_type == "AGENT_CASE"))
    if existing:
        return
    response = agent_orchestrator_service.intake(db, AgentIntakeRequest(title=f"Investigation for {ticket.ticket_number}", description=ticket.description, initial_message="Investigate this demo issue and summarize evidence, likely cause, and safe human-reviewed next steps.", priority=ticket.priority, created_by_role="DEMO_PRESENTER", linked_ams_ticket_id=ticket.id), "SERVICE_ENGINEER", engineer=True)
    case = db.get(AgentCase, response.case_id)
    session = db.get(AgentChatSession, response.id)
    if case is None or session is None:
        raise DemoScenarioError("Agent handoff did not return a usable case and session.")
    _artifact(db, run, "AGENT_CASE", case.id, case.case_id, f"/agent-investigations/{case.id}")
    _artifact(db, run, "AGENT_SESSION", session.id, session.session_id, f"/agent-chat/sessions/{session.id}")
    _artifact(db, run, "INVESTIGATION_WORKSPACE", case.id, f"Investigation workspace {case.case_id}", f"/agent-investigations/{case.id}")
    _target(run, "REVIEW_WORKSPACE", "INVESTIGATION_WORKSPACE", case.id, f"/agent-investigations/{case.id}")
    _target(run, "START_AGENT_INVESTIGATION", "INVESTIGATION_WORKSPACE", case.id, f"/agent-investigations/{case.id}")
    for proposal in db.scalars(select(AgentActionProposal).where(AgentActionProposal.case_id == case.id)).all():
        _artifact(db, run, "ACTION_PROPOSAL", proposal.id, proposal.title, f"/agent-investigations/{case.id}", {"proposal_id": proposal.proposal_id, "safe_action_code": proposal.safe_action_code})
    _event(db, run, "AGENT_INVESTIGATION_LINKED", "Agent investigation linked", "The local AMS ticket now has an agent case, session, workspace, evidence, knowledge, and safe proposals.", "AGENT_CASE", case.id)
    db.flush()


def refresh_links(db: Session, run: DemoScenarioRun) -> None:
    case_artifact = db.scalar(select(DemoScenarioArtifact).where(DemoScenarioArtifact.run_id == run.id, DemoScenarioArtifact.artifact_type == "AGENT_CASE"))
    if case_artifact is None:
        return
    for execution in db.scalars(select(AgentActionExecution).where(AgentActionExecution.case_id == case_artifact.artifact_id)).all():
        _artifact(db, run, "ACTION_EXECUTION", execution.id, execution.execution_id, f"/agent-actions/executions/{execution.id}", {"status": execution.status, "safe_action_code": execution.safe_action_code})


def list_catalog(db: Session) -> list[dict[str, Any]]:
    rows = db.scalars(select(DemoScenario).where(DemoScenario.is_enabled.is_(True)).order_by(DemoScenario.sort_order, DemoScenario.scenario_code)).all()
    if not rows:
        rows = [_scenario_row(db, code) for code in SCENARIO_DEFINITIONS]
        db.commit()
    return [{"id": row.id, "scenario_code": row.scenario_code, "title": row.title, "description": row.description, "business_value": row.business_value, "default_experience": row.default_experience, "is_enabled": row.is_enabled, "sort_order": row.sort_order, "step_count": len(_definition(row.scenario_code)["steps"])} for row in rows]


def summary(db: Session) -> dict[str, Any]:
    catalog = list_catalog(db)
    counts = {status: db.scalar(select(func.count(DemoScenarioRun.id)).where(DemoScenarioRun.status == status)) or 0 for status in ("IN_PROGRESS", "COMPLETED", "RESET", "FAILED")}
    return {"scenario_count": len(catalog), "enabled_scenarios": [item["scenario_code"] for item in catalog], "run_counts": counts, "active_runs": counts["IN_PROGRESS"], "safe_local_only": True, "real_model_called_by_readiness": False, "autonomous_remediation_enabled": False}


def list_runs(db: Session) -> list[dict[str, Any]]:
    return [_run_dict(db, row, include_children=False) for row in db.scalars(select(DemoScenarioRun).order_by(DemoScenarioRun.started_at.desc()).limit(100)).all()]


def get_run(db: Session, run_id: str) -> DemoScenarioRun:
    row = db.scalar(select(DemoScenarioRun).where(DemoScenarioRun.run_id == run_id))
    if row is None:
        raise DemoScenarioError("Demo scenario run not found.", 404)
    return row


def start(db: Session, scenario_code: str, created_by_role: str = "DEMO_PRESENTER") -> dict[str, Any]:
    scenario = _scenario_row(db, scenario_code)
    active = db.scalar(select(DemoScenarioRun).where(DemoScenarioRun.scenario_code == scenario.scenario_code, DemoScenarioRun.status == "IN_PROGRESS").order_by(DemoScenarioRun.started_at.desc()).limit(1))
    if active:
        return _run_dict(db, active)
    now = _now()
    run = DemoScenarioRun(run_id=_run_number(db), scenario_code=scenario.scenario_code, status="IN_PROGRESS", current_step_code=_definition(scenario.scenario_code)["steps"][0][0], started_at=now, created_by_role=created_by_role, summary=scenario.description, outcome_summary="Presenter has not completed the storyline yet.", created_at=now, updated_at=now)
    db.add(run)
    db.flush()
    for index, (code, title, description, presenter, action_type, expected) in enumerate(_definition(scenario.scenario_code)["steps"], start=1):
        db.add(DemoScenarioStep(run_id=run.id, step_code=code, step_title=title, step_description=description, presenter_instruction=presenter, expected_result=expected, action_type=action_type, step_order=index, status="ACTIVE" if index == 1 else "PENDING", started_at=now if index == 1 else None, instructions=presenter))
    db.flush()
    _event(db, run, "SCENARIO_STARTED", f"{scenario.title} started", "The presenter started a local, guided EOS storyline.", metadata={"scenario_code": scenario.scenario_code, "created_by_role": created_by_role})
    _initial_artifacts(db, run, created_by_role)
    db.commit()
    return _run_dict(db, db.get(DemoScenarioRun, run.id))


def _activate_next(db: Session, run: DemoScenarioRun) -> None:
    next_step = db.scalar(select(DemoScenarioStep).where(DemoScenarioStep.run_id == run.id, DemoScenarioStep.status == "PENDING").order_by(DemoScenarioStep.step_order).limit(1))
    if next_step:
        next_step.status, next_step.started_at = "ACTIVE", _now()
        run.current_step_code = next_step.step_code
    else:
        run.current_step_code = None


def _complete_current(db: Session, run: DemoScenarioRun, actor: str = "DEMO_PRESENTER") -> DemoScenarioStep:
    step = db.scalar(select(DemoScenarioStep).where(DemoScenarioStep.run_id == run.id, DemoScenarioStep.status == "ACTIVE").order_by(DemoScenarioStep.step_order).limit(1))
    if step is None:
        raise DemoScenarioError("Scenario has no active step.", 409)
    step.status, step.completed_at, step.updated_at = "COMPLETED", _now(), _now()
    _event(db, run, "STEP_COMPLETED", f"Step completed: {step.step_title}", f"The presenter marked {step.step_title} complete.", "DEMO_SCENARIO_STEP", step.id, {"step_code": step.step_code, "actor": actor})
    return step


def advance(db: Session, run_id: str) -> dict[str, Any]:
    run = get_run(db, run_id)
    if run.status != "IN_PROGRESS":
        raise DemoScenarioError("Only an in-progress scenario can advance.", 409)
    current = _complete_current(db, run)
    if current.action_type == "START_AGENT_INVESTIGATION":
        _handoff(db, run)
    _activate_next(db, run)
    run.updated_at = _now()
    _event(db, run, "STEP_ACTIVATED", f"Next step activated: {run.current_step_code or 'complete'}", "The next presenter-controlled storyline step is ready.", metadata={"current_step_code": run.current_step_code})
    db.commit()
    return _run_dict(db, db.get(DemoScenarioRun, run.id))


def complete_step(db: Session, run_id: str, step_code: str) -> dict[str, Any]:
    run = get_run(db, run_id)
    if run.status != "IN_PROGRESS":
        raise DemoScenarioError("Only an in-progress scenario can complete steps.", 409)
    step = db.scalar(select(DemoScenarioStep).where(DemoScenarioStep.run_id == run.id, DemoScenarioStep.step_code == step_code.upper()))
    if step is None:
        raise DemoScenarioError("Scenario step not found.", 404)
    if step.status == "COMPLETED":
        return _run_dict(db, run)
    if step.status != "ACTIVE":
        raise DemoScenarioError("Only the active scenario step can be completed.", 409)
    _complete_current(db, run)
    if step.action_type == "START_AGENT_INVESTIGATION":
        _handoff(db, run)
    _activate_next(db, run)
    if run.current_step_code is None:
        run.status, run.completed_at, run.outcome_summary = "COMPLETED", _now(), "The presenter completed the guided storyline with local evidence, human approval controls, and auditable outcomes."
        _event(db, run, "SCENARIO_COMPLETED", "Scenario completed", "The presenter completed the guided local EOS demo storyline.")
    run.updated_at = _now()
    db.commit()
    return _run_dict(db, db.get(DemoScenarioRun, run.id))


def reset(db: Session, run_id: str, reason: str = "Presenter reset the guided demo.") -> dict[str, Any]:
    run = get_run(db, run_id)
    if run.status == "RESET":
        return _run_dict(db, run)
    run.status, run.reset_at, run.current_step_code, run.updated_at = "RESET", _now(), None, _now()
    run.outcome_summary = f"Reset without deleting shared data: {reason[:1500]}"
    _event(db, run, "SCENARIO_RESET", "Scenario reset", run.outcome_summary)
    db.commit()
    return _run_dict(db, db.get(DemoScenarioRun, run.id))


def timeline(db: Session, run_id: str) -> list[dict[str, Any]]:
    run = get_run(db, run_id)
    return [_event_dict(item) for item in db.scalars(select(DemoScenarioEvent).where(DemoScenarioEvent.run_id == run.id).order_by(DemoScenarioEvent.event_timestamp, DemoScenarioEvent.id)).all()]


def artifacts(db: Session, run_id: str) -> list[dict[str, Any]]:
    run = get_run(db, run_id)
    refresh_links(db, run)
    db.commit()
    return [_artifact_dict(item) for item in db.scalars(select(DemoScenarioArtifact).where(DemoScenarioArtifact.run_id == run.id).order_by(DemoScenarioArtifact.created_at, DemoScenarioArtifact.id)).all()]


def next_action(db: Session, run_id: str) -> dict[str, Any] | None:
    return _next_action(db, get_run(db, run_id))
