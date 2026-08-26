"""Read-only executive value aggregation for the EOS demo storyboard."""

from __future__ import annotations

from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agent_chat import AgentActionAuditEvent, AgentActionExecution, AgentActionProposal, AgentCase, AgentEvidenceItem, AgentOrchestrationRun
from app.models.agent_knowledge import AgentKnownError, AgentRetrievalQuery, AgentRetrievalResult
from app.models.ai_config import AiGuardrailEvent, AiInvocationLog, AiSafetyPolicy
from app.models.demo_scenario import DemoScenario, DemoScenarioArtifact, DemoScenarioEvent, DemoScenarioRun
from app.models.stage3_autonomy import Stage3AutonomousRun
from app.services.demo_scenario_service import SCENARIO_DEFINITIONS
from app.services import agent_model_chat_service, stage3_autonomous_service


DISCLAIMER = "Value estimates are demo estimates based on local EOS scenario data and configurable assumptions. They are not production measurements."
ASSUMPTIONS = [
    {"assumption_code": "MANUAL_TRIAGE_MINUTES_BASELINE", "title": "Manual triage baseline", "description": "Illustrative time for a human to triage one issue before contextual agent support.", "value": 30, "unit": "minutes", "label": "Illustrative assumption", "is_demo_assumption": True},
    {"assumption_code": "MANUAL_EVIDENCE_COLLECTION_MINUTES_BASELINE", "title": "Manual evidence collection baseline", "description": "Illustrative time to gather and correlate ticket, alert, batch, and user-report evidence.", "value": 45, "unit": "minutes", "label": "Illustrative assumption", "is_demo_assumption": True},
    {"assumption_code": "MANUAL_WORK_NOTE_DRAFT_MINUTES_BASELINE", "title": "Manual work-note drafting baseline", "description": "Illustrative time to prepare one internal work-note draft.", "value": 15, "unit": "minutes", "label": "Illustrative assumption", "is_demo_assumption": True},
    {"assumption_code": "MANUAL_CUSTOMER_UPDATE_MINUTES_BASELINE", "title": "Manual customer-update drafting baseline", "description": "Illustrative time to prepare one customer-update draft; no message is sent by this dashboard.", "value": 10, "unit": "minutes", "label": "Illustrative assumption", "is_demo_assumption": True},
    {"assumption_code": "ASSISTED_TRIAGE_MINUTES", "title": "Agent-assisted triage", "description": "Illustrative review time after EOS packages context.", "value": 10, "unit": "minutes", "label": "Illustrative assumption", "is_demo_assumption": True},
    {"assumption_code": "ASSISTED_REVIEW_MINUTES", "title": "Agent-assisted evidence review", "description": "Illustrative human review time for grounded evidence and knowledge.", "value": 20, "unit": "minutes", "label": "Illustrative assumption", "is_demo_assumption": True},
    {"assumption_code": "APPROVAL_REVIEW_MINUTES", "title": "Safe-action approval review", "description": "Illustrative time to review one narrowly scoped local action proposal.", "value": 5, "unit": "minutes", "label": "Illustrative assumption", "is_demo_assumption": True},
]


def _count(db: Session, model: Any, *criteria: Any) -> int:
    statement = select(func.count(model.id))
    if criteria:
        statement = statement.where(*criteria)
    return int(db.scalar(statement) or 0)


def _model_status(db: Session) -> dict[str, Any]:
    try:
        status = agent_model_chat_service.status(db)
    except Exception as error:  # Status is informational and must not break the read-only dashboard.
        return {"real_model_enabled": False, "provider_configured": False, "model_configured": False, "api_key_present": False, "provider_enabled": False, "model_enabled": False, "safe_to_invoke": False, "reason": f"Status unavailable: {str(error)[:160]}"}
    return {"real_model_enabled": bool(status.get("real_model_enabled", False)), "provider_code": status.get("provider_code"), "model_code": status.get("model_code"), "default_model": status.get("default_model"), "provider_configured": bool(status.get("provider_configured", False)), "model_configured": bool(status.get("model_configured", False)), "api_key_present": bool(status.get("api_key_present", False)), "provider_enabled": bool(status.get("provider_enabled", False)), "model_enabled": bool(status.get("model_enabled", False)), "safe_to_invoke": bool(status.get("safe_to_invoke", False)), "reason": status.get("reason"), "allowed_task_types": status.get("allowed_task_types", []), "daily_usage": status.get("daily_usage", {})}


def _snapshot(db: Session) -> dict[str, Any]:
    seeded_scenarios = db.scalars(select(DemoScenario).where(DemoScenario.is_enabled.is_(True))).all()
    scenario_count = len(seeded_scenarios) if seeded_scenarios else len(SCENARIO_DEFINITIONS)
    total_scenarios = _count(db, DemoScenario) or len(SCENARIO_DEFINITIONS)
    scenario_runs = _count(db, DemoScenarioRun)
    completed_runs = _count(db, DemoScenarioRun, DemoScenarioRun.status == "COMPLETED")
    active_runs = _count(db, DemoScenarioRun, DemoScenarioRun.status == "IN_PROGRESS")
    reset_runs = _count(db, DemoScenarioRun, DemoScenarioRun.status == "RESET")
    artifacts = _count(db, DemoScenarioArtifact)
    scenario_events = _count(db, DemoScenarioEvent)
    investigations = _count(db, AgentCase)
    handoffs = _count(db, AgentOrchestrationRun)
    evidence = _count(db, AgentEvidenceItem)
    knowledge = _count(db, AgentRetrievalResult)
    known_errors = _count(db, AgentKnownError)
    retrieval_queries = _count(db, AgentRetrievalQuery)
    proposals = _count(db, AgentActionProposal)
    approved = _count(db, AgentActionProposal, AgentActionProposal.approval_status == "APPROVED")
    rejected = _count(db, AgentActionProposal, AgentActionProposal.approval_status == "REJECTED")
    executions = _count(db, AgentActionExecution)
    succeeded = _count(db, AgentActionExecution, AgentActionExecution.status == "SUCCEEDED")
    duplicates = _count(db, AgentActionExecution, AgentActionExecution.status == "SKIPPED_DUPLICATE")
    action_audit = _count(db, AgentActionAuditEvent)
    invocations = _count(db, AiInvocationLog)
    fallback = _count(db, AiInvocationLog, AiInvocationLog.status.in_(("FALLBACK", "BLOCKED", "DISABLED", "FAILED")))
    guardrails = _count(db, AiGuardrailEvent)
    zero_action_cases = _count(db, AgentCase, ~AgentCase.runs.any(AgentOrchestrationRun.actions_executed > 0))
    linked = {"ams_tickets": _count(db, DemoScenarioArtifact, DemoScenarioArtifact.artifact_type == "AMS_TICKET"), "alerts": _count(db, DemoScenarioArtifact, DemoScenarioArtifact.artifact_type == "OBSERVABILITY_ALERT"), "batch_runs": _count(db, DemoScenarioArtifact, DemoScenarioArtifact.artifact_type == "BATCH_RUN"), "user_reports": _count(db, DemoScenarioArtifact, DemoScenarioArtifact.artifact_type == "USER_REPORT")}
    model = _model_status(db)
    return {"scenario_execution": {"total_scenarios": total_scenarios, "enabled_scenarios": scenario_count, "scenario_runs": scenario_runs, "completed_runs": completed_runs, "active_runs": active_runs, "reset_runs": reset_runs, "scenario_artifacts_created": artifacts}, "issue_to_investigation": {"issues_induced": _count(db, DemoScenarioEvent, DemoScenarioEvent.event_type == "ISSUE_INDUCED"), "ams_tickets_linked": linked["ams_tickets"], "alerts_linked": linked["alerts"], "batch_runs_linked": linked["batch_runs"], "user_reports_linked": linked["user_reports"], "agent_investigations_created": investigations, "investigation_handoffs": handoffs}, "evidence_and_knowledge": {"evidence_items_collected": evidence, "knowledge_items_retrieved": knowledge, "known_errors_matched": known_errors, "timeline_events_created": scenario_events, "retrieval_queries_recorded": retrieval_queries}, "model_assisted_readiness": {**model, "real_model_calls_default_enabled": False, "model_invocations_recorded": invocations, "fallback_responses_recorded": fallback}, "approval_gated_actions": {"action_proposals_created": proposals, "actions_approved": approved, "actions_rejected": rejected, "actions_executed": executions, "actions_succeeded": succeeded, "duplicate_executions_prevented": duplicates}, "governance_and_audit": {"invocation_audit_records": invocations, "guardrail_events": guardrails, "action_audit_events": action_audit, "scenario_timeline_events": scenario_events, "cases_with_actions_executed_zero": zero_action_cases}, "linked_artifacts": linked}


def _effort(snapshot: dict[str, Any]) -> dict[str, Any]:
    values = {item["assumption_code"]: item["value"] for item in ASSUMPTIONS}
    investigations = snapshot["issue_to_investigation"]["agent_investigations_created"]
    proposals = snapshot["approval_gated_actions"]["action_proposals_created"]
    approved = snapshot["approval_gated_actions"]["actions_approved"]
    drafts = proposals
    manual = investigations * (values["MANUAL_TRIAGE_MINUTES_BASELINE"] + values["MANUAL_EVIDENCE_COLLECTION_MINUTES_BASELINE"]) + drafts * values["MANUAL_WORK_NOTE_DRAFT_MINUTES_BASELINE"]
    assisted = investigations * (values["ASSISTED_TRIAGE_MINUTES"] + values["ASSISTED_REVIEW_MINUTES"]) + approved * values["APPROVAL_REVIEW_MINUTES"]
    avoided = max(manual - assisted, 0)
    return {"estimated_manual_effort_baseline_minutes": manual, "estimated_agent_assisted_effort_minutes": assisted, "estimated_effort_avoided_minutes": avoided, "estimated_effort_avoided_percent": round((avoided / manual) * 100, 1) if manual else 0, "label": "Demo estimate", "disclaimer": DISCLAIMER, "assumptions": ASSUMPTIONS}


def value_metrics(db: Session) -> dict[str, Any]:
    snapshot = _snapshot(db)
    return {"metric_classification": "Scenario-derived metric", "disclaimer": DISCLAIMER, "scenario_execution": snapshot["scenario_execution"], "issue_to_investigation": snapshot["issue_to_investigation"], "evidence_and_knowledge": snapshot["evidence_and_knowledge"], "model_assisted_readiness": snapshot["model_assisted_readiness"], "approval_gated_actions": snapshot["approval_gated_actions"], "governance_and_audit": snapshot["governance_and_audit"], "effort_impact": _effort(snapshot)}


def scenario_outcomes(db: Session) -> list[dict[str, Any]]:
    rows = db.scalars(select(DemoScenario).where(DemoScenario.is_enabled.is_(True)).order_by(DemoScenario.sort_order, DemoScenario.scenario_code)).all()
    catalog = [(row.scenario_code, row.title, row.description, row.business_value) for row in rows] or [(code, definition["title"], definition["description"], definition["business_value"]) for code, definition in sorted(SCENARIO_DEFINITIONS.items(), key=lambda item: item[1]["sort_order"])]
    outcomes = []
    for scenario_code, title, description, business_value in catalog:
        runs = db.scalars(select(DemoScenarioRun).where(DemoScenarioRun.scenario_code == scenario_code).order_by(DemoScenarioRun.started_at.desc()).limit(1)).all()
        latest = runs[0] if runs else None
        run_count = _count(db, DemoScenarioRun, DemoScenarioRun.scenario_code == scenario_code)
        artifact_count = _count(db, DemoScenarioArtifact, DemoScenarioArtifact.run_id == latest.id) if latest else 0
        outcomes.append({"scenario_code": scenario_code, "title": title, "business_problem": description, "business_value": business_value, "source_signals": [item.artifact_type for item in (db.scalars(select(DemoScenarioArtifact).where(DemoScenarioArtifact.run_id == latest.id)).all() if latest else [])], "agent_capabilities": ["contextual handoff", "evidence timeline", "knowledge retrieval", "Stage 1 read-only guidance", "approval-gated local actions"], "generated_artifacts": artifact_count, "run_count": run_count, "latest_run_status": latest.status if latest else "NOT_STARTED", "latest_run_id": latest.run_id if latest else None, "deep_link": f"/demo-scenarios/runs/{latest.run_id}" if latest else "/demo-scenarios"})
    return outcomes


def governance(db: Session) -> dict[str, Any]:
    snapshot = _snapshot(db)
    model = snapshot["model_assisted_readiness"]
    sandbox = stage3_autonomous_service.status(db)
    sandbox_summary = stage3_autonomous_service.summary(db)
    return {"title": "Governance by design", "real_model_default": "Off", "real_model_enabled": model["real_model_enabled"], "api_key_required_for_demo": False, "api_key_present": model["api_key_present"], "provider_model_readiness": {"provider_code": model.get("provider_code"), "model_code": model.get("model_code"), "provider_enabled": model["provider_enabled"], "model_enabled": model["model_enabled"], "safe_to_invoke": model["safe_to_invoke"], "reason": model.get("reason")}, "stage_1": "Read-only model assistance with deterministic fallback.", "stage_2": "Predefined local actions require explicit human approval and separate execution.", "stage_3": {"available": True, "sandbox_enabled": sandbox["sandbox_enabled"], "kill_switch_enabled": sandbox["kill_switch_enabled"], "runs": sandbox_summary["run_count"], "human_handbacks": sandbox_summary["needs_human_review"], "production_remediation": False, "label": "Local sandbox only"}, "autonomous_remediation": False, "prohibited_execution": ["shell commands", "arbitrary SQL", "user-provided code", "external systems", "ServiceNow", "customer sends"], "audit": snapshot["governance_and_audit"], "safety_controls": ["deterministic/mock default", "bounded context and prompt governance", "input/output safety checks", "approval-gated action catalog", "timeline and invocation audit", "fallback-safe behavior", "Stage 3 dry-run-first and kill switch"]}


def operating_model(db: Session) -> dict[str, Any]:
    snapshot = _snapshot(db)
    return {"title": "AI-native AMS operating model", "maturity": "Governed Stage 1 + Stage 2 + local Stage 3 sandbox", "value_chain": [{"step": "Signal", "description": "Issues arrive from tickets, alerts, batches, and user reports.", "link": "/demo-scenarios"}, {"step": "Contextual Handoff", "description": "EOS creates an investigation with source context.", "link": "/agent-investigations"}, {"step": "Evidence + Knowledge", "description": "The agent gathers bounded evidence and reusable knowledge.", "link": "/agent-knowledge"}, {"step": "Stage 1 Guidance", "description": "Read-only deterministic guidance and optional governed model chat.", "link": "/agent-chat"}, {"step": "Approval-Gated Action", "description": "A human reviews predefined local safe actions.", "link": "/agent-actions/proposals"}, {"step": "Audit + Learning", "description": "Scenario, action, model, and sandbox decisions remain traceable.", "link": "/demo-control"}], "stage3_sandbox": {"description": "A bounded, dry-run-first local sandbox can demonstrate future autonomy without production remediation.", "link": "/stage3-autonomy", "local_only": True}, "speed": "Context packaging reduces repeated manual searching in the demo.", "quality": "Evidence and knowledge citations separate facts from hypotheses.", "reuse": "Curated knowledge and scenario patterns are reusable across sources.", "governance": "Read-only model assistance, approval-gated actions, and sandbox kill switches keep people in control.", "auditability": snapshot["governance_and_audit"]}


def commercial_model(db: Session) -> dict[str, Any]:
    return {"title": "Commercial model implications", "disclaimer": "Narrative only. This view does not implement billing, contracts, pricing, or production savings measurement.", "rows": [{"traditional_model": "Ticket-volume pricing", "ai_native_alternative": "Outcome-based incident avoidance and faster restoration", "value_lever": "Less repeated triage and clearer ownership", "demo_metric": "Scenario-derived investigations and effort estimate", "risk_allocation_impact": "Shared focus on measurable service outcomes"}, {"traditional_model": "Fixed capacity", "ai_native_alternative": "Platform plus governed agent operations", "value_lever": "Reusable context, knowledge, and safe workflows", "demo_metric": "Knowledge reuse and action governance", "risk_allocation_impact": "Governance and operating controls become explicit"}, {"traditional_model": "Application-based pricing", "ai_native_alternative": "Digital operations pod / product-aligned support", "value_lever": "Cross-source investigation continuity", "demo_metric": "Tickets, alerts, batches, and reports linked to cases", "risk_allocation_impact": "Accountability follows business service outcomes"}, {"traditional_model": "SLA penalty model", "ai_native_alternative": "SLA plus experience and automation assurance", "value_lever": "Speed, quality, and auditability", "demo_metric": "Evidence, timeline, approval, and fallback coverage", "risk_allocation_impact": "Automation remains measurable and reviewable"}, {"traditional_model": "Manual L1/L2 support", "ai_native_alternative": "Human-supervised agentic operations", "value_lever": "Human attention moves to judgment and exceptions", "demo_metric": "Approval-gated actions with zero autonomous remediation", "risk_allocation_impact": "Human control remains a defined operating boundary"}]}


def storyboard(db: Session) -> dict[str, Any]:
    outcomes = scenario_outcomes(db)
    return {"title": "From ticket handling to AI-native operations", "disclaimer": DISCLAIMER, "sections": [{"section_code": "TRADITIONAL_AMS_CHALLENGE", "title": "The Traditional AMS Challenge", "message": "Ticket-centric operations depend on manual triage, fragmented knowledge, slow handoffs, and limited auditability of AI assistance.", "proof_points": ["manual evidence gathering", "knowledge fragmentation", "handoff delay", "limited governance visibility"]}, {"section_code": "AI_NATIVE_AMS_OPERATING_MODEL", "title": "The AI-Native AMS Operating Model", "message": "EOS connects signals to contextual investigations, evidence, knowledge, governed Stage 1 guidance, approval-gated actions, and an audit trail.", "proof_points": ["signal-to-investigation flow", "evidence timeline", "knowledge retrieval", "human-supervised action"]}, {"section_code": "SCENARIO_BASED_PROOF_POINTS", "title": "Scenario-Based Proof Points", "message": "Four guided local scenarios demonstrate the operating model across warehouse, batch, user, and observability journeys.", "scenarios": outcomes}, {"section_code": "GOVERNANCE_BY_DESIGN", "title": "Governance by Design", "message": "Deterministic defaults, bounded context, read-only model assistance, approval-gated actions, and audit records reduce operational risk.", "proof_points": ["real model off by default", "Stage 1 read-only", "Stage 2 approval required", "no autonomous remediation"]}, {"section_code": "COMMERCIAL_MODEL_IMPLICATIONS", "title": "Commercial Model Implications", "message": "The platform supports a narrative shift from ticket volume and capacity to outcomes, governed agent operations, and automation assurance.", "proof_points": ["outcome/value orientation", "platform plus services", "experience and automation assurance"]}, {"section_code": "ROADMAP_TO_PRODUCTION", "title": "Roadmap to Production", "message": "Future phases can add enterprise identity, production integrations, hardened approvals, real model activation, and a controlled remediation sandbox.", "proof_points": ["ServiceNow connector", "enterprise authorization", "real observability integrations", "controlled Stage 3 boundary"]}]}


def deep_links() -> dict[str, Any]:
    return {"links": [{"label": "Guided Demo Scenarios", "path": "/demo-scenarios", "experiences": ["full", "business", "operations", "simulation", "agentic"]}, {"label": "Scenario Runs", "path": "/demo-scenarios/runs", "experiences": ["full", "operations", "simulation", "agentic"]}, {"label": "Agent Investigations", "path": "/agent-investigations", "experiences": ["full", "operations", "agentic"]}, {"label": "Action Proposals", "path": "/agent-actions/proposals", "experiences": ["full", "operations", "agentic"]}, {"label": "Agent Chat Sessions", "path": "/agent-chat/sessions", "experiences": ["full", "operations", "agentic"]}, {"label": "Real-Model Status", "path": "/ai-config/real-model", "experiences": ["full", "agentic"]}, {"label": "Demo Control", "path": "/demo-control", "experiences": ["full"]}]}


def summary(db: Session) -> dict[str, Any]:
    snapshot = _snapshot(db)
    sandbox = stage3_autonomous_service.summary(db)
    return {"title": "Executive Demo Dashboard", "headline": "From reactive ticket handling to governed, outcome-oriented AI-native AMS operations.", "read_only": True, "disclaimer": DISCLAIMER, "kpis": {"guided_scenarios": snapshot["scenario_execution"]["total_scenarios"], "investigations_created": snapshot["issue_to_investigation"]["agent_investigations_created"], "evidence_items_collected": snapshot["evidence_and_knowledge"]["evidence_items_collected"], "knowledge_items_reused": snapshot["evidence_and_knowledge"]["knowledge_items_retrieved"], "safe_actions_proposed": snapshot["approval_gated_actions"]["action_proposals_created"], "approved_local_actions": snapshot["approval_gated_actions"]["actions_approved"], "audit_records": snapshot["governance_and_audit"]["invocation_audit_records"] + snapshot["governance_and_audit"]["action_audit_events"] + snapshot["governance_and_audit"]["scenario_timeline_events"], "estimated_effort_avoided_minutes": _effort(snapshot)["estimated_effort_avoided_minutes"], "real_model_default": "Off", "autonomous_remediation": "Disabled", "stage3_sandbox_available": True, "stage3_sandbox_enabled": sandbox["sandbox_enabled"], "stage3_sandbox_runs": sandbox["run_count"], "stage3_human_handbacks": sandbox["needs_human_review"]}, "operating_model": "Governed Stage 1 + Stage 2 + local Stage 3 sandbox", "scenario_status": snapshot["scenario_execution"], "governance_status": {"real_model_default": "Off", "stage_1": "Read-only", "stage_2": "Approval-gated", "stage3": "Local sandbox only", "stage3_kill_switch": sandbox["kill_switch_enabled"], "autonomous_remediation": "Disabled"}}
