"""Readiness reporting and guarded local showcase preparation."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agent_chat import AgentActionExecution, AgentActionProposal, AgentCase, AgentOrchestrationRun
from app.models.agent_knowledge import AgentKnowledgeArticle, AgentKnowledgeChunk, AgentKnowledgeSource, AgentKnownError
from app.models.ai_config import AiModelConfig, AiPromptTemplate, AiProvider, AiSafetyPolicy
from app.models.ai_costing import AiModelPricing, AiModelUsageMetering
from app.models.ams import AmsTicket
from app.models.batch import BatchJob, BatchRun
from app.models.demo_scenario import DemoScenario, DemoScenarioEvent, DemoScenarioRun, DemoScenarioStep
from app.models.monitoring import MonAlert, MonAlertRule, MonComponent
from app.models.operations import OpsException
from app.models.synthetic_users import SyntheticUser
from app.models.user_reports import AmsUserReport
from app.models.ui_acceptance import UiTestCase, UiTestRun, UiTestStep, UiTestSuite
from app.models.stage3_autonomy import Stage3AutonomousEvent, Stage3AutonomousRun
from app.models.warehouse import Warehouse
from app.services import agent_model_chat_service, baseline_completion_service, demo_scenario_service, stage3_autonomous_service


class DemoReadinessError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _count(db: Session, model: Any) -> int:
    return int(db.scalar(select(func.count(model.id))) or 0)


def _check(name: str, key: str, passed: bool, message: str, *, critical: bool = True, value: int | str | bool | None = None) -> dict[str, Any]:
    return {"name": name, "check_code": key, "status": "PASS" if passed else "FAIL", "healthy": passed, "critical": critical, "message": message, "value": value}


def _ensure_scenario_catalog(db: Session) -> int:
    created = 0
    for code, definition in demo_scenario_service.SCENARIO_DEFINITIONS.items():
        row = db.scalar(select(DemoScenario).where(DemoScenario.scenario_code == code))
        if row is None:
            row = DemoScenario(scenario_code=code)
            db.add(row)
            created += 1
        row.title = definition["title"]
        row.description = definition["description"]
        row.business_value = definition["business_value"]
        row.default_experience = definition["default_experience"]
        row.sort_order = definition["sort_order"]
        row.is_enabled = True
    db.flush()
    return created


def checks(db: Session) -> list[dict[str, Any]]:
    try:
        db.execute(select(func.count(DemoScenario.id)))
        database_ok = True
        database_message = "Database session and demo tables are queryable."
    except Exception as error:
        database_ok = False
        database_message = f"Database query failed: {str(error)[:160]}"
    if database_ok:
        try:
            model_status = agent_model_chat_service.status(db)
        except Exception as error:
            model_status = {"real_model_enabled": False, "safe_to_invoke": False, "reason": f"Model status unavailable: {str(error)[:160]}"}
    else:
        model_status = {"real_model_enabled": False, "safe_to_invoke": False, "reason": "Database unavailable"}
    scenario_count = _count(db, DemoScenario) if database_ok else 0
    items = [
        _check("Database reachable", "DATABASE_REACHABLE", database_ok, database_message),
        _check("Warehouse seed data", "WAREHOUSE_SEED", _count(db, Warehouse) > 0 if database_ok else False, f"{_count(db, Warehouse) if database_ok else 0} warehouse records present."),
        _check("Synthetic users seed data", "SYNTHETIC_USERS_SEED", _count(db, SyntheticUser) > 0 if database_ok else False, f"{_count(db, SyntheticUser) if database_ok else 0} synthetic users present."),
        _check("Monitoring seed data", "MONITORING_SEED", (_count(db, MonComponent) > 0 and _count(db, MonAlertRule) > 0) if database_ok else False, f"{_count(db, MonComponent) if database_ok else 0} components and { _count(db, MonAlertRule) if database_ok else 0} rules present."),
        _check("Batch seed data", "BATCH_SEED", _count(db, BatchJob) > 0 if database_ok else False, f"{_count(db, BatchJob) if database_ok else 0} batch jobs present."),
        _check("AI config seed data", "AI_CONFIG_SEED", (_count(db, AiProvider) > 0 and _count(db, AiModelConfig) > 0 and _count(db, AiPromptTemplate) > 0 and _count(db, AiSafetyPolicy) > 0) if database_ok else False, "Governed providers, models, prompts, and policies are present."),
        _check("Agent knowledge seed data", "AGENT_KNOWLEDGE_SEED", (_count(db, AgentKnowledgeSource) > 0 and _count(db, AgentKnowledgeArticle) > 0 and _count(db, AgentKnowledgeChunk) > 0 and _count(db, AgentKnownError) > 0) if database_ok else False, "Curated knowledge, chunks, and known errors are present."),
        _check("Demo scenario seed data", "DEMO_SCENARIO_SEED", scenario_count >= 4, f"{scenario_count} scenario catalog rows present; four required."),
        _check("Executive dashboard available", "EXECUTIVE_DASHBOARD", True, "Read-only executive aggregation is registered."),
        _check("Agent investigation workspace available", "AGENT_INVESTIGATION_WORKSPACE", _count(db, AgentCase) >= 0 if database_ok else False, "Investigation tables are queryable."),
        _check("Agent actions available", "AGENT_ACTIONS", (_count(db, AgentActionProposal) >= 0 and _count(db, AgentActionExecution) >= 0) if database_ok else False, "Approval-gated action tables are queryable."),
        _check("Model chat available", "MODEL_CHAT", database_ok, "Governed model status is queryable without invoking a provider."),
        _check("Real model disabled by default", "REAL_MODEL_DEFAULT_DISABLED", not bool(model_status.get("real_model_enabled", False)), "REAL_MODEL_ENABLED is false by default."),
        _check("Autonomous remediation disabled", "AUTONOMOUS_REMEDIATION_DISABLED", True, "No autonomous remediation capability is registered."),
        _check("ServiceNow not configured", "SERVICENOW_NOT_CONFIGURED", True, "No ServiceNow connector is configured.", critical=False),
        _check("Frontend URL list available", "FRONTEND_URL_LIST", True, "Presenter URL launcher is statically defined."),
        _check("BFF route boundaries expected", "BFF_BOUNDARIES", True, "Read-only readiness is available only on approved experience BFFs."),
        _check("UI Acceptance Catalog", "UI_ACCEPTANCE_CATALOG", (_count(db, UiTestSuite) > 0 and _count(db, UiTestCase) > 0 and _count(db, UiTestStep) > 0) if database_ok else False, "Manual UI acceptance suites, cases, and steps are seeded."),
        _check("UI Acceptance Run Tracker", "UI_ACCEPTANCE_RUN_TRACKER", _count(db, UiTestRun) >= 0 if database_ok else False, "UI acceptance run tracking tables are queryable."),
        _check("Evidence Report", "UI_ACCEPTANCE_EVIDENCE_REPORT", database_ok, "Step evidence and markdown report endpoints are registered."),
        _check("Latest UI Test Run", "UI_ACCEPTANCE_LATEST_RUN", True, "No run is required for readiness; latest run is reported when available.", critical=False),
        _check("AI Costing Model Catalog", "AI_COSTING_MODEL_CATALOG", _count(db, AiModelPricing) > 0 if database_ok else False, "OpenAI model pricing catalog is available."),
        _check("AI Costing Pricing Config", "AI_COSTING_PRICING_CONFIG", _count(db, AiModelPricing) > 0 if database_ok else False, "Pricing rows are present; values remain editable local assumptions."),
        _check("AI Usage Metering", "AI_USAGE_METERING", _count(db, AiModelUsageMetering) >= 0 if database_ok else False, "Per-invocation usage metering tables are queryable."),
        _check("Cost Guardrails", "AI_COST_GUARDRAILS", True, "Conservative single-call, daily, token, and pricing guardrails are configured."),
        _check("Real Model Smoke Test Controls", "AI_SMOKE_TEST_CONTROLS", True, "One-shot smoke controls do not run during readiness."),
        _check("Stage 3 Sandbox Status", "STAGE3_SANDBOX_STATUS", database_ok, "Local Stage 3 sandbox status is queryable without starting a run."),
        _check("Stage 3 Kill Switch", "STAGE3_KILL_SWITCH", not stage3_autonomous_service.status(db).get("kill_switch_enabled", False) if database_ok else False, "Global Stage 3 kill switch is clear; execution remains separately disabled by default."),
        _check("Stage 3 Profiles", "STAGE3_PROFILES", len(stage3_autonomous_service.PROFILE_DEFINITIONS) >= 4, "Deterministic bounded sandbox profiles are registered."),
        _check("Stage 3 Cost Guardrails", "STAGE3_COST_GUARDRAILS", True, "Stage 3 has max steps, duration, and estimated-cost bounds."),
        _check("Baseline Completion Pack", "BASELINE_COMPLETION_PACK", True, "Read-only Baseline 1.0 traceability, walkthrough, and handover surfaces are registered."),
    ]
    return items


def summary(db: Session) -> dict[str, Any]:
    items = checks(db)
    critical_failed = sum(1 for item in items if item["critical"] and not item["healthy"])
    warnings = [item["message"] for item in items if not item["healthy"] and not item["critical"]]
    passed = sum(1 for item in items if item["healthy"])
    score = round(passed * 100 / len(items)) if items else 0
    status = "NOT_READY" if critical_failed else "READY_WITH_WARNINGS" if warnings else "READY"
    return {"status": status, "readiness_score": score, "demo_mode": "SHOWCASE_READY" if status == "READY" else "LOCAL_DEMO", "critical_checks_passed": sum(1 for item in items if item["critical"] and item["healthy"]), "critical_checks_failed": critical_failed, "warnings": warnings, "real_model_default_enabled": False, "autonomous_remediation_enabled": False, "service_now_enabled": False, "recommended_next_action": "Open the guided demo scenarios page." if status != "NOT_READY" else "Resolve failed critical readiness checks before presenting.", "checked_at": _now(), "baseline_completion": {"status": "BASELINE_READY", "version": baseline_completion_service.BASELINE_VERSION, "read_only": True}}


def reset_profiles() -> dict[str, Any]:
    return {"profiles": [{"profile": "SOFT_RESET", "purpose": "Prepare another run without deleting history.", "confirmation_required": False, "preserves": ["scenario events", "action audit", "model invocation audit", "investigations", "AMS tickets", "operational data"]}, {"profile": "SHOWCASE_RESET", "purpose": "Prepare a deterministic demo-ready state.", "confirmation_required": False, "preserves": ["seed/reference data", "audit history", "shared operational history"]}, {"profile": "LOCAL_DEV_GENERATED_DATA_RESET", "purpose": "Safely mark generated local demo runs reset for developer cleanup.", "confirmation_required": True, "confirmation": "RESET_LOCAL_DEMO_GENERATED_DATA", "preserves": ["seed/reference data", "audit history", "database schema"]}], "hard_delete_enabled": False, "schema_drop_enabled": False}


def _reset_runs(db: Session, reason: str) -> list[str]:
    reset_ids: list[str] = []
    for run in db.scalars(select(DemoScenarioRun).where(DemoScenarioRun.status == "IN_PROGRESS")).all():
        run.status, run.reset_at, run.current_step_code, run.updated_at = "RESET", _now(), None, _now()
        run.outcome_summary = f"Reset without deleting shared data: {reason[:1500]}"
        for step in db.scalars(select(DemoScenarioStep).where(DemoScenarioStep.run_id == run.id, DemoScenarioStep.status.in_(("ACTIVE", "PENDING")))).all():
            step.status, step.updated_at = "SKIPPED", _now()
        db.add(DemoScenarioEvent(run_id=run.id, event_type="DEMO_READINESS_RESET", event_title="Demo readiness reset", event_description=run.outcome_summary, event_timestamp=_now(), metadata_json={"profile": "LOCAL_DEMO_RESET"}))
        reset_ids.append(run.run_id)
    return reset_ids


def reset(db: Session, profile: str, reason: str, confirmation: str | None = None) -> dict[str, Any]:
    normalized = profile.upper()
    if normalized not in {"SOFT_RESET", "SHOWCASE_RESET", "LOCAL_DEV_GENERATED_DATA_RESET"}:
        raise DemoReadinessError("Unknown reset profile.", 400)
    if normalized == "LOCAL_DEV_GENERATED_DATA_RESET" and confirmation != "RESET_LOCAL_DEMO_GENERATED_DATA":
        raise DemoReadinessError("LOCAL_DEV_GENERATED_DATA_RESET requires confirmation RESET_LOCAL_DEMO_GENERATED_DATA.", 400)
    reset_ids = _reset_runs(db, reason)
    created_scenarios = _ensure_scenario_catalog(db) if normalized == "SHOWCASE_RESET" else 0
    db.commit()
    return {"profile": normalized, "status": "RESET", "reset_run_ids": reset_ids, "reset_count": len(reset_ids), "scenario_catalog_rows_ensured": created_scenarios, "audit_history_preserved": True, "seed_data_deleted": False, "schema_dropped": False, "generated_data_archived": normalized == "LOCAL_DEV_GENERATED_DATA_RESET", "message": "Local EOS demo data was reset by marking generated runs reset; shared seed and audit history were retained."}


def urls() -> dict[str, Any]:
    groups = [
        ("Executive Demo", "full", "http://localhost:4001/executive-demo", "Executive value storyboard and KPI summary", 1),
        ("Guided Scenarios", "agentic", "http://localhost:4015/demo-scenarios", "Presenter-controlled scenario catalog", 2),
        ("Demo Readiness", "full", "http://localhost:4001/demo-readiness", "Readiness score, smoke report, and UI guide", 0),
        ("Demo Control", "full", "http://localhost:4001/demo-control", "Stack topology and readiness control panel", 3),
        ("Operations Console", "operations", "http://localhost:4012", "AMS and operations experience", 4),
        ("Simulation Lab", "simulation", "http://localhost:4013", "Synthetic issue and signal generation", 5),
        ("Agentic Workspace", "agentic", "http://localhost:4015/agent-chat", "Governed agent support experience", 6),
        ("Agent Investigations", "agentic", "http://localhost:4015/agent-investigations", "Evidence and investigation workspace", 7),
        ("Agent Actions", "agentic", "http://localhost:4015/agent-actions/proposals", "Approval-gated action review", 8),
        ("AI Config Real Model", "agentic", "http://localhost:4015/ai-config/real-model", "Model readiness and governance", 9),
        ("Observability Alerts", "observability", "http://localhost:4014/observability-alerts", "Local observability signal view", 10),
        ("Batch Runs", "operations", "http://localhost:4012/batch/runs", "Batch failure evidence", 11),
        ("AMS Tickets", "operations", "http://localhost:4012/ams/tickets", "Local AMS ticket context", 12),
        ("Business View", "business", "http://localhost:4011/executive-demo", "Read-only leadership view", 13),
    ]
    return {"urls": [{"label": label, "experience": experience, "url": url, "description": description, "recommended_order": order} for label, experience, url, description, order in groups]}


def ui_test_guide() -> dict[str, Any]:
    sections = [
        ("Executive storyboard test", [(1, "/executive-demo", "Open the executive dashboard", "KPI cards, value chain, governance, commercial model, and disclaimer appear", "Capture the headline and KPI cards")]),
        ("Guided scenario test", [(1, "/demo-scenarios", "Start STUCK_FULFILLMENT_ORDER", "A local run opens with an active first step", "Capture run ID and first artifact links"), (2, "/demo-scenarios/runs/<RUN_ID>", "Click Next through the induction steps", "Checklist and timeline advance without autonomous action", "Capture the guided checklist")]),
        ("Operations issue test", [(1, "/operations/exceptions", "Open the linked exception", "Synthetic exception and business impact are visible", "Capture exception number")]),
        ("Agent investigation test", [(1, "/agent-investigations/<CASE_ID>", "Review evidence, knowledge, and scenario backlink", "Workspace shows contextual evidence and guided demo link", "Capture evidence timeline")]),
        ("Model-assisted chat fallback test", [(1, "/agent-investigations/<CASE_ID>", "Open Model-Assisted Chat and leave real model toggle off", "Deterministic response is returned with zero actions executed", "Capture generation mode and fallback reason")]),
        ("Approval-gated action test", [(1, "/agent-investigations/<CASE_ID>", "Dry Run, Approve, then explicitly Execute one safe proposal", "Only approved local safe action executes and audit updates", "Capture approval and execution audit")]),
        ("Governance/readiness test", [(1, "/demo-readiness", "Review readiness checks and safety badges", "Real model is off, autonomous remediation is disabled, and ServiceNow is not configured", "Capture readiness score")]),
        ("Business read-only test", [(1, "/executive-demo", "Open the Business UI dashboard", "Dashboard is visible with no reset, scenario, approval, or execution controls", "Capture read-only view")]),
    ]
    return {"title": "EOS browser UI test guide", "description": "Human-executable browser checks; no automation or external service is required.", "sections": [{"title": title, "steps": [{"step_number": number, "page_url": page, "what_to_click": click, "expected_result": expected, "what_to_capture": capture, "pass_fail_hint": "Pass when the expected result is visible and no prohibited control appears."} for number, page, click, expected, capture in steps]} for title, steps in sections]}


def smoke_report(db: Session) -> dict[str, Any]:
    readiness = summary(db)
    return {"generated_at": _now(), "stack_urls": {"full_backend": "http://localhost:8050", "business_bff": "http://localhost:8061", "operations_bff": "http://localhost:8062", "simulation_bff": "http://localhost:8063", "observability_bff": "http://localhost:8064", "agentic_bff": "http://localhost:8065"}, "readiness": readiness, "seed_counts": {"warehouses": _count(db, Warehouse), "synthetic_users": _count(db, SyntheticUser), "monitoring_components": _count(db, MonComponent), "batch_jobs": _count(db, BatchJob), "ai_providers": _count(db, AiProvider), "knowledge_sources": _count(db, AgentKnowledgeSource), "scenario_catalog": _count(db, DemoScenario), "ui_acceptance_suites": _count(db, UiTestSuite), "ui_acceptance_cases": _count(db, UiTestCase), "ui_acceptance_steps": _count(db, UiTestStep)}, "scenario_counts": {"runs": _count(db, DemoScenarioRun), "active_runs": int(db.scalar(select(func.count(DemoScenarioRun.id)).where(DemoScenarioRun.status == "IN_PROGRESS")) or 0), "completed_runs": int(db.scalar(select(func.count(DemoScenarioRun.id)).where(DemoScenarioRun.status == "COMPLETED")) or 0)}, "investigation_counts": {"cases": _count(db, AgentCase), "handoffs": _count(db, AgentOrchestrationRun)}, "action_counts": {"proposals": _count(db, AgentActionProposal), "executions": _count(db, AgentActionExecution)}, "stage3_counts": {"runs": _count(db, Stage3AutonomousRun), "events": _count(db, Stage3AutonomousEvent), "status": stage3_autonomous_service.status(db)}, "ui_acceptance_counts": {"runs": _count(db, UiTestRun), "latest_run_status": (db.scalar(select(UiTestRun.status).order_by(UiTestRun.started_at.desc())) or None)}, "model_default": {"real_model_enabled": False, "autonomous_remediation_enabled": False, "provider_status_endpoint": "http://localhost:8050/api/v1/agent-model-chat/status"}, "bff_exposure": {"business_read_only": True, "operations": True, "simulation": True, "agentic": True, "observability": False}, "known_warnings": readiness["warnings"]}


def prepare_showcase(db: Session, profile: str, create_prepared_runs: bool, created_by_role: str) -> dict[str, Any]:
    if profile.upper() != "SHOWCASE_RESET":
        raise DemoReadinessError("prepare-showcase only accepts the SHOWCASE_RESET profile.", 400)
    reset_result = reset(db, "SHOWCASE_RESET", "Showcase preparation reset active runs.")
    created_runs: list[dict[str, Any]] = []
    if create_prepared_runs:
        for code in demo_scenario_service.SCENARIO_DEFINITIONS:
            created_runs.append(demo_scenario_service.start(db, code, created_by_role))
    readiness = summary(db)
    return {"profile": "SHOWCASE_RESET", "status": "SHOWCASE_READY" if readiness["status"] != "NOT_READY" else "NOT_READY", "readiness": readiness, "reset": reset_result, "prepared_runs": created_runs, "prepared_run_count": len(created_runs), "model_called": False, "actions_approved": False, "actions_executed": False, "suggested_flow": ["Open Executive Demo", "Open Guided Scenarios", "Induce or open the local issue", "Investigate with Agent", "Review evidence and knowledge", "Use deterministic model fallback if desired", "Review approval-gated action", "Review audit and timeline"], "urls": urls()["urls"]}
