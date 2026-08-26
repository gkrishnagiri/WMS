"""Read-only Baseline 1.0 completion and handover content for EOS."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.demo_scenario import DemoScenario


BASELINE_NAME = "AI-Native AMS Research Platform – EOS Baseline Demo"
BASELINE_VERSION = "Baseline 1.0"
DISCLAIMER = "This is a local EOS demo handover package. It describes implemented demo behavior and does not claim production readiness or production ROI."
SAFETY_BOUNDARY = "Read-only completion surfaces do not start scenarios, reset data, call models, approve actions, execute actions, or call external systems."


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _count_scenarios(db: Session) -> int:
    try:
        return int(db.scalar(select(func.count(DemoScenario.id))) or 0)
    except Exception:
        return 0


def summary(db: Session) -> dict[str, Any]:
    scenario_count = _count_scenarios(db)
    warnings = [] if scenario_count >= 4 else ["The four required scenario catalog rows are not all present; run the idempotent demo scenario seed."]
    return {
        "baseline_name": BASELINE_NAME,
        "baseline_version": BASELINE_VERSION,
        "completion_status": "BASELINE_READY" if not warnings else "BASELINE_READY_WITH_WARNINGS",
        "completed_prompt_range": "Prompts 13-30",
        "capability_count": 12,
        "scenario_count": scenario_count,
        "stage_modes_supported": ["STAGE_1_READ_ONLY", "STAGE_2_APPROVAL_GATED", "STAGE_3_AUTONOMOUS_SANDBOX"],
        "real_model_default_enabled": False,
        "stage3_autonomous_execution_default_enabled": False,
        "service_now_enabled": False,
        "authentication_enabled": False,
        "recommended_start_url": "http://localhost:4001/executive-demo",
        "recommended_demo_flow": [
            "Open the executive value storyboard.",
            "Prepare or open a guided demo scenario.",
            "Investigate the generated issue with the agent.",
            "Review evidence, knowledge, and the Stage 2 approval gate.",
            "Optionally preview the Stage 3 local sandbox without executing it.",
            "Return to readiness and the evidence/report surfaces.",
        ],
        "warnings": warnings,
        "read_only": True,
        "safety_boundary": SAFETY_BOUNDARY,
        "generated_at": _now(),
    }


def _req(requirement_id: str, category: str, requirement: str, status: str, prompts: list[str], ui: list[str], api: list[str], evidence: str, tests: str, notes: str = "") -> dict[str, Any]:
    return {"requirement_id": requirement_id, "category": category, "requirement": requirement, "status": status, "implemented_by_prompts": prompts, "primary_ui_routes": ui, "primary_api_routes": api, "evidence_source": evidence, "test_coverage": tests, "notes": notes}


def requirements() -> dict[str, Any]:
    rows = [
        _req("BUS-001", "Synthetic Business Application", "Warehouse and fulfillment application exists", "COVERED", ["13"], ["/warehouse", "/warehouse/orders"], ["/api/v1/warehouse"], "Warehouse pages and seeded data", "Warehouse API/page tests"),
        _req("BUS-002", "Synthetic Business Application", "Orders, inventory, locations, tasks, and shipments exist", "COVERED", ["13-17"], ["/warehouse/orders", "/warehouse/inventory", "/warehouse/tasks", "/warehouse/shipments"], ["/api/v1/warehouse"], "Warehouse model and seed records", "Warehouse workflow tests"),
        _req("BUS-003", "Synthetic Business Application", "Business and operations UI can view operational state", "COVERED", ["13-18"], ["/warehouse", "/operations/exceptions"], ["/api/v1/operations", "/api/v1/warehouse"], "Experience routing and navigation", "Experience boundary tests"),
        _req("ITSM-001", "ITSM and AMS Foundation", "AMS tickets and ticket events exist", "COVERED", ["14-18"], ["/ams/tickets"], ["/api/v1/ams/tickets"], "AMS ticket pages and models", "AMS route tests"),
        _req("ITSM-002", "ITSM and AMS Foundation", "Operational exceptions exist", "COVERED", ["15-18"], ["/operations/exceptions"], ["/api/v1/operations/exceptions"], "Operations exception records", "Operations tests"),
        _req("ITSM-003", "ITSM and AMS Foundation", "User-reported issues exist", "COVERED", ["16-18"], ["/ams/user-reports"], ["/api/v1/ams/user-reports"], "Synthetic user report flow", "User report tests"),
        _req("ITSM-004", "ITSM and AMS Foundation", "Agent handoff can originate from operational objects", "COVERED", ["21"], ["/agent-investigations"], ["/api/v1/agent-chat/intake"], "Contextual handoff links", "Handoff tests"),
        _req("OBS-001", "Monitoring and Observability", "Monitoring components and alerts exist", "COVERED", ["15-17"], ["/monitoring/alerts"], ["/api/v1/monitoring"], "Local monitoring catalog", "Monitoring tests"),
        _req("OBS-002", "Monitoring and Observability", "Observability evidence and runtime observability exist", "COVERED", ["17-22"], ["/observability", "/observability/runtime"], ["/api/v1/observability", "/api/v1/runtime-observability"], "Local telemetry and evidence pages", "Observability tests", "Uses the local observability stack for demo purposes."),
        _req("OBS-003", "Monitoring and Observability", "Alert-to-AMS integration exists", "COVERED", ["18-21"], ["/observability-alerts"], ["/api/v1/observability-alerts"], "Alert event and handoff records", "Alert handoff tests"),
        _req("BATCH-001", "Batch Operations", "Batch jobs, runs, and failures exist", "COVERED", ["17"], ["/batch/jobs", "/batch/runs"], ["/api/v1/batch/runs"], "Batch models and seeded jobs", "Batch tests"),
        _req("BATCH-002", "Batch Operations", "Batch failure scenario exists", "COVERED", ["25"], ["/demo-scenarios"], ["/api/v1/demo-scenarios"], "BATCH_FAILURE_RECOVERY catalog", "Scenario tests"),
        _req("BATCH-003", "Batch Operations", "Batch evidence can be used by the agent", "COVERED", ["19-22"], ["/agent-investigations"], ["/api/v1/agent-investigations"], "Evidence timeline context", "Investigation tests"),
        _req("SCEN-001", "Synthetic Users and Scenario Generation", "Synthetic users and journeys exist", "COVERED", ["16-18"], ["/synthetic-users/journeys"], ["/api/v1/synthetic-users"], "Synthetic user seed", "Synthetic user tests"),
        _req("SCEN-002", "Synthetic Users and Scenario Generation", "User issue reports exist", "COVERED", ["16-18"], ["/ams/user-reports"], ["/api/v1/ams/user-reports"], "User report intake", "User report tests"),
        _req("SCEN-003", "Synthetic Users and Scenario Generation", "Four guided demo scenarios, runs, artifacts, and timeline exist", "COVERED", ["25"], ["/demo-scenarios"], ["/api/v1/demo-scenarios"], "Scenario catalog and run pages", "Demo scenario tests"),
        _req("AG1-001", "Agentic Stage 1 – Assisted Investigation", "Agent cases, chat, evidence timeline, knowledge, known errors, drafts, and guidance exist", "COVERED", ["18-22"], ["/agent-chat", "/agent-investigations"], ["/api/v1/agent-chat", "/api/v1/agent-investigations", "/api/v1/agent-knowledge"], "Agent workspace and timeline", "Agent investigation tests"),
        _req("AG1-002", "Agentic Stage 1 – Assisted Investigation", "Governed real-model assisted chat can be enabled, while deterministic/mock remains default", "COVERED", ["20", "24"], ["/agent-investigations", "/ai-config/real-model"], ["/api/v1/agent-model-chat"], "Model status and fallback metadata", "Model chat tests", "Optional real-model feature; not required for baseline demo."),
        _req("AG2-001", "Agentic Stage 2 – Human Approval-Gated Actions", "Safe local action catalog and proposals exist", "COVERED", ["23"], ["/agent-actions/proposals", "/agent-investigations"], ["/api/v1/agent-actions"], "Action catalog and proposal panel", "Action service tests"),
        _req("AG2-002", "Agentic Stage 2 – Human Approval-Gated Actions", "Dry run, explicit approval, execution audit, and duplicate prevention exist", "COVERED", ["23"], ["/agent-actions/executions"], ["/api/v1/agent-actions"], "Action audit and timeline", "Approval/execution tests"),
        _req("AG3-001", "Agentic Stage 3 – Autonomous Sandbox", "Autonomous sandbox profiles and dry-run-first behavior exist", "COVERED", ["30"], ["/stage3-autonomy", "/stage3-autonomy/profiles"], ["/api/v1/stage3-autonomy"], "Sandbox status and profile catalog", "Stage 3 tests"),
        _req("AG3-002", "Agentic Stage 3 – Autonomous Sandbox", "Execution is disabled by default, bounded, safe-action-only, and supports human handback", "COVERED", ["30"], ["/stage3-autonomy/runs"], ["/api/v1/stage3-autonomy"], "Kill switch and guardrail state", "Stage 3 policy tests"),
        _req("AG3-003", "Agentic Stage 3 – Autonomous Sandbox", "Cost and token tracking integrates with the sandbox", "COVERED", ["29-30"], ["/ai-costing/usage", "/stage3-autonomy"], ["/api/v1/ai-costing", "/api/v1/stage3-autonomy"], "Usage and run audit fields", "Costing/Stage 3 tests"),
        _req("MODEL-001", "Real Model Governance and Costing", "OpenAI model catalog and model configurations can be managed", "COVERED", ["20", "29", "additional model management change"], ["/ai-costing/models", "/ai-config/real-model"], ["/api/v1/ai-costing/models", "/api/v1/ai-config"], "Governed catalog UI", "AI costing tests"),
        _req("MODEL-002", "Real Model Governance and Costing", "Real calls are disabled by default and API keys are not stored", "COVERED", ["20", "24", "29"], ["/ai-costing", "/ai-costing/smoke-test"], ["/api/v1/agent-model-chat/status", "/api/v1/ai-costing/guardrails"], "Status response and environment governance", "Default-disabled tests"),
        _req("MODEL-003", "Real Model Governance and Costing", "Editable pricing assumptions, token metering, estimated cost, and opt-in smoke dry-run exist", "COVERED", ["29"], ["/ai-costing/models", "/ai-costing/usage", "/ai-costing/smoke-test"], ["/api/v1/ai-costing"], "Costing dashboard", "Metering and smoke tests", "Cost is estimated from local assumptions, not an invoice."),
        _req("EXP-001", "Experience Segregation", "Full, Business, Operations, Simulation, Observability, and Agentic UIs exist", "COVERED", ["13-18"], ["/", "/executive-demo", "/demo-readiness"], ["/health"], "Experience registry and six ports", "BFF tests"),
        _req("EXP-002", "Experience Segregation", "BFF route boundaries and Business read-only boundaries exist", "COVERED", ["13-31"], ["/baseline-completion"], ["/api/v1/baseline-completion"], "BFF route matrix", "BFF exposure tests"),
        _req("EXEC-001", "Executive and Commercial Story", "Executive dashboard, value metrics, storyboard, governance, and commercial model view exist", "COVERED", ["26"], ["/executive-demo"], ["/api/v1/executive-demo"], "Executive dashboard", "Executive demo tests"),
        _req("EXEC-002", "Executive and Commercial Story", "Demo-estimated effort impact is clearly labeled", "COVERED", ["26"], ["/executive-demo/value"], ["/api/v1/executive-demo/value-metrics"], "Visible estimate disclaimer", "Value metric tests"),
        _req("DEMO-001", "Demo Operations and Testing", "Readiness, showcase preparation, reset profiles, URL launcher, and smoke report exist", "COVERED", ["27"], ["/demo-readiness"], ["/api/v1/demo-readiness"], "Readiness dashboard", "Readiness tests"),
        _req("DEMO-002", "Demo Operations and Testing", "Manual UI acceptance testing, evidence capture, and Markdown report exist", "COVERED", ["28"], ["/ui-acceptance"], ["/api/v1/ui-acceptance"], "UI acceptance run/report pages", "UI acceptance tests"),
        _req("DEMO-003", "Demo Operations and Testing", "Baseline traceability and handover pack exist", "COVERED", ["31"], ["/baseline-completion"], ["/api/v1/baseline-completion"], "This completion module", "Baseline completion tests"),
    ]
    out_of_scope = [
        _req("OOS-001", "Explicitly Out of Scope for Baseline", "Production ServiceNow integration", "OUT_OF_SCOPE", ["31"], [], [], "Limitations register", "Read-only boundary tests", "Future connector phase."),
        _req("OOS-002", "Explicitly Out of Scope for Baseline", "Production authentication and authorization", "OUT_OF_SCOPE", ["31"], [], [], "Limitations register", "Boundary documentation", "Future enterprise identity phase."),
        _req("OOS-003", "Explicitly Out of Scope for Baseline", "Production autonomous remediation", "OUT_OF_SCOPE", ["30", "31"], [], [], "Stage 3 warning and limitations", "Default-disabled tests", "Stage 3 is local sandbox only."),
        _req("OOS-004", "Explicitly Out of Scope for Baseline", "External customer communication sending", "OUT_OF_SCOPE", ["31"], [], [], "Safety boundary documentation", "Safety tests", "Drafts are local only."),
        _req("OOS-005", "Explicitly Out of Scope for Baseline", "Browser automation", "OUT_OF_SCOPE", ["28", "31"], ["/ui-acceptance"], ["/api/v1/ui-acceptance"], "UI acceptance catalog", "No browser automation required", "Manual browser-first testing only."),
        _req("OOS-006", "Explicitly Out of Scope for Baseline", "Production ROI calculator", "OUT_OF_SCOPE", ["26", "31"], ["/executive-demo/value"], ["/api/v1/executive-demo/value-metrics"], "Estimate disclaimer", "Value metric tests", "Demo estimates are not production measurements."),
        _req("OOS-007", "Explicitly Out of Scope for Baseline", "Real observability source integration beyond the local stack", "OUT_OF_SCOPE", ["31"], ["/observability"], [], "Limitations register", "Local stack tests", "Future production connector phase."),
    ]
    rows.extend(out_of_scope)
    return {"requirements": rows, "summary": {"total": len(rows), "covered": sum(row["status"] == "COVERED" for row in rows), "partially_covered": 0, "out_of_scope": len(out_of_scope), "future_phase": 0}, "read_only": True}


def _steps(*items: tuple[str, str, str, str, str]) -> list[dict[str, Any]]:
    return [{"step_number": index, "instruction": item[0], "page_url": item[1], "what_to_click": item[2], "expected_result": item[3], "evidence_to_capture": item[4]} for index, item in enumerate(items, 1)]


def walkthroughs() -> dict[str, Any]:
    return {"walkthroughs": [
        {"walkthrough_id": "EXECUTIVE_BUSINESS", "title": "Executive Business Walkthrough", "audience": "Executives, client stakeholders, commercial stakeholders", "estimated_duration_minutes": 8, "start_experience": "business", "start_url": "http://localhost:4011/executive-demo", "preconditions": ["Local stack is ready", "Use the Business UI for read-only storytelling"], "steps": _steps(("Open the executive dashboard.", "http://localhost:4011/executive-demo", "Review KPI cards", "Value chain and scenario KPIs are visible.", "Capture the dashboard and estimate disclaimer."), ("Open storyboard and governance sections.", "http://localhost:4011/executive-demo/storyboard", "Open storyboard, governance, and commercial model links", "Traditional versus AI-native narrative and controls are visible.", "Capture governance badges."), ("Open baseline completion traceability.", "http://localhost:4011/baseline-completion", "Open Baseline Completion", "Coverage and limitations are available read-only.", "Capture the baseline status.")), "expected_outcomes": ["Business value is explained without mutation controls", "Assumptions are labeled as demo estimates"], "evidence_to_capture": ["KPI screenshot", "governance screenshot", "traceability route"], "reset_instructions": "No reset is needed; all views are read-only."},
        {"walkthrough_id": "READINESS_RESET", "title": "Demo Readiness and Reset Walkthrough", "audience": "Demo presenter, tester", "estimated_duration_minutes": 6, "start_experience": "full", "start_url": "http://localhost:4001/demo-readiness", "preconditions": ["Local EOS stack is running"], "steps": _steps(("Open readiness dashboard.", "http://localhost:4001/demo-readiness", "Review readiness score", "Checks and warnings are visible.", "Capture score."), ("Open smoke report and URL launcher.", "http://localhost:4001/demo-readiness/smoke-report", "Open Smoke Report and UI Test Guide", "Read-only reports and presenter links load.", "Capture report."), ("Prepare showcase or soft reset when appropriate.", "http://localhost:4001/demo-readiness/showcase", "Use Prepare Showcase or Soft Reset", "Only explicit local demo records are changed; seed and audit history remain.", "Capture operation response.")), "expected_outcomes": ["Presenter can prepare a repeatable demo", "Reset boundaries are understood"], "evidence_to_capture": ["readiness report", "showcase response"], "reset_instructions": "Use SOFT_RESET for replay; LOCAL_DEV_GENERATED_DATA_RESET requires its confirmation string."},
        {"walkthrough_id": "STUCK_FULFILLMENT_ORDER", "title": "Stuck Fulfillment Order End-to-End Walkthrough", "audience": "Operations leaders, AMS leaders, technical stakeholders", "estimated_duration_minutes": 15, "start_experience": "simulation", "start_url": "http://localhost:4013/demo-scenarios", "preconditions": ["Showcase is prepared", "Stage 2 action proposals are available after investigation"], "steps": _steps(("Start the Stuck Fulfillment Order scenario.", "http://localhost:4013/demo-scenarios", "Start scenario and advance to issue induction", "Local order exception and support artifacts appear.", "Capture scenario run ID."), ("Open the generated operational artifact and ticket.", "http://localhost:4012/operations/exceptions", "Open artifact links", "Source context is linked.", "Capture exception/ticket."), ("Investigate with Agent.", "http://localhost:4015/agent-investigations", "Click Investigate with Agent", "Workspace opens with evidence and knowledge.", "Capture investigation workspace."), ("Review Stage 2 and dry-run a safe action.", "http://localhost:4015/agent-investigations", "Review proposals, Dry Run, Approve, Execute Approved Action", "Only the explicitly approved local action executes and is audited.", "Capture proposal and execution audit."), ("Optionally open Stage 3 dry-run.", "http://localhost:4015/stage3-autonomy", "Open Stage 3 console and run Dry Run", "A plan is shown; execution remains disabled by default.", "Capture sandbox warning and plan.")), "expected_outcomes": ["Issue-to-investigation flow is visible", "Human approval and sandbox boundaries are explicit"], "evidence_to_capture": ["scenario artifacts", "evidence timeline", "action audit", "Stage 3 dry-run"], "reset_instructions": "Soft reset the scenario run after the walkthrough; retain audit history."},
        {"walkthrough_id": "BATCH_FAILURE_RECOVERY", "title": "Batch Failure Recovery Walkthrough", "audience": "Operations and AMS stakeholders", "estimated_duration_minutes": 12, "start_experience": "simulation", "start_url": "http://localhost:4013/demo-scenarios", "preconditions": ["Showcase is prepared"], "steps": _steps(("Start Batch Failure Recovery.", "http://localhost:4013/demo-scenarios", "Start and advance the scenario", "A failed batch, alert, and support context are linked.", "Capture batch run and alert links."), ("Investigate with Agent.", "http://localhost:4015/agent-investigations", "Open the linked investigation", "Batch evidence and runbook knowledge are visible.", "Capture evidence timeline."), ("Review checklist and Stage 2 action.", "http://localhost:4015/agent-investigations", "Review next-step checklist and approval gate", "A local draft/checklist requires explicit review.", "Capture proposal status."), ("Open optional Stage 3 dry-run.", "http://localhost:4015/stage3-autonomy", "Open sandbox console", "No action runs automatically.", "Capture dry-run plan.")), "expected_outcomes": ["Batch risk becomes contextual agent evidence", "Approval remains human controlled"], "evidence_to_capture": ["batch failure", "runbook knowledge", "audit"], "reset_instructions": "Use the readiness soft reset after replay."},
        {"walkthrough_id": "USER_REPORTED_SHIPMENT_DELAY", "title": "User-Reported Shipment Delay Walkthrough", "audience": "Business users and AMS stakeholders", "estimated_duration_minutes": 10, "start_experience": "operations", "start_url": "http://localhost:4012/demo-scenarios", "preconditions": ["Showcase is prepared"], "steps": _steps(("Start the shipment-delay scenario.", "http://localhost:4012/demo-scenarios", "Start scenario and open user report", "A synthetic user report and linked ticket appear.", "Capture report and ticket links."), ("Investigate with Agent.", "http://localhost:4015/agent-investigations", "Open linked investigation", "Source context and customer-update draft are visible.", "Capture draft status."), ("Confirm communication boundary.", "http://localhost:4011/executive-demo", "Review Business UI and governance", "No external customer communication is sent.", "Capture read-only boundary.")), "expected_outcomes": ["User impact is contextualized", "Customer update remains a local draft"], "evidence_to_capture": ["user report", "draft", "Business UI"], "reset_instructions": "No external communication occurs; reset the local scenario run if replaying."},
        {"walkthrough_id": "OBSERVABILITY_ALERT_NOISE_ROOT_CAUSE", "title": "Observability Alert Noise Walkthrough", "audience": "Observability and operations stakeholders", "estimated_duration_minutes": 11, "start_experience": "operations", "start_url": "http://localhost:4012/demo-scenarios", "preconditions": ["Local alert catalog is seeded"], "steps": _steps(("Start the alert-noise scenario.", "http://localhost:4012/demo-scenarios", "Start and advance scenario", "Alert, triage, and diagnostic artifacts are grouped.", "Capture alert event."), ("Investigate the grouped evidence.", "http://localhost:4015/agent-investigations", "Open linked investigation", "Evidence timeline and known error/runbook context appear.", "Capture grouped evidence."), ("Review acknowledgement proposal.", "http://localhost:4015/agent-investigations", "Review Stage 2 proposal and governance", "A local acknowledgement requires human approval and does not resolve production alerts.", "Capture proposal safety note.")), "expected_outcomes": ["Alert noise is converted into an investigation", "Acknowledgement is local and governed"], "evidence_to_capture": ["alert grouping", "triage", "governance"], "reset_instructions": "Retain alert/audit history; reset only generated scenario run state."},
        {"walkthrough_id": "MODEL_COSTING", "title": "Model Costing and Smoke-Test Walkthrough", "audience": "Agentic architects and platform owners", "estimated_duration_minutes": 8, "start_experience": "agentic", "start_url": "http://localhost:4015/ai-costing", "preconditions": ["No API key is needed for this walkthrough", "Real model remains disabled by default"], "steps": _steps(("Open AI Costing dashboard and model catalog.", "http://localhost:4015/ai-costing", "Review model status and pricing assumptions", "OpenAI catalog, enabled state, and local pricing fields are visible.", "Capture pricing note."), ("Review usage and guardrails.", "http://localhost:4015/ai-costing/usage", "Open Usage Metering", "Token/cost fields and guardrails are visible.", "Capture usage dashboard."), ("Run smoke-test dry-run.", "http://localhost:4015/ai-costing/smoke-test", "Click Dry Run", "Readiness and estimated cost are returned without a model call.", "Capture dry-run response."), ("Confirm real smoke test is opt-in.", "http://localhost:4015/ai-costing/smoke-test", "Review disabled run control", "No credit-consuming call is required.", "Capture default-off state.")), "expected_outcomes": ["Cost assumptions are transparent", "No real call occurs by default"], "evidence_to_capture": ["model status", "pricing", "dry-run"], "reset_instructions": "No reset is needed; pricing changes are explicit configuration changes."},
        {"walkthrough_id": "UI_ACCEPTANCE_EVIDENCE", "title": "UI Acceptance Evidence Walkthrough", "audience": "Manual tester and demo presenter", "estimated_duration_minutes": 10, "start_experience": "agentic", "start_url": "http://localhost:4015/ui-acceptance", "preconditions": ["UI acceptance catalog is seeded"], "steps": _steps(("Open the UI acceptance dashboard.", "http://localhost:4015/ui-acceptance", "Review suites and coverage", "Deterministic suites and cases are visible.", "Capture coverage."), ("Start a test run and open a step.", "http://localhost:4015/ui-acceptance/runs", "Start run and open current step", "Instruction, target URL, safety note, and expected result appear.", "Capture current step."), ("Record browser evidence.", "http://localhost:4015/ui-acceptance/runs/:runId", "Enter observed result, evidence note, screenshot reference, and save", "Step result is persisted without uploading binary screenshots.", "Capture local screenshot reference."), ("Complete and open Markdown report.", "http://localhost:4015/ui-acceptance/runs/:runId/report", "Complete run and open report", "Evidence, defects, and coverage are exportable as Markdown.", "Capture report.")), "expected_outcomes": ["Manual browser validation is repeatable", "Evidence references are retained"], "evidence_to_capture": ["step result", "screenshot reference", "Markdown report"], "reset_instructions": "Test runs are records; abort or complete them as appropriate without altering demo data."},
    ], "read_only": True}


def demo_journeys() -> dict[str, Any]:
    journeys = [
        ("BUSINESS_VALUE", "Business Value Journey", "Explain the move from ticket handling to outcome-oriented support.", ["Executive", "Commercial stakeholder"], "/executive-demo", ["Executive dashboard", "Storyboard", "Governance"], "EOS turns operational signals into governed, explainable support outcomes.", "Do not present demo estimates as production savings.", ["KPI summary", "value chain", "governance narrative"]),
        ("OPERATIONS_ISSUE", "Operations Issue Journey", "Show a signal becoming a contextual issue.", ["Operations lead", "AMS engineer"], "/demo-scenarios", ["Scenario run", "Exception/ticket", "Alert or batch"], "The presenter can replay the same local issue consistently.", "Do not claim production state was changed.", ["scenario artifacts", "source links"]),
        ("INVESTIGATION", "Agentic Investigation Journey", "Show evidence and knowledge assembled around a case.", ["Support engineer", "Agentic operator"], "/agent-investigations", ["Handoff", "Workspace", "Evidence timeline", "Knowledge"], "The agent reduces context switching while keeping the reasoning visible.", "Do not claim the agent executed an action in Stage 1.", ["evidence timeline", "knowledge citations"]),
        ("APPROVAL", "Human Approval Journey", "Show a narrow safe local action under human control.", ["Service engineer", "Risk reviewer"], "/agent-actions/proposals", ["Proposal", "Dry run", "Approval", "Audit"], "The system executes only the approved predefined local action.", "Do not claim external remediation or customer communication.", ["approval record", "execution audit"]),
        ("SANDBOX", "Autonomous Sandbox Journey", "Demonstrate bounded autonomy potential without production access.", ["Architect", "Platform owner"], "/stage3-autonomy", ["Profile", "Dry-run plan", "Kill switch", "Handback"], "Stage 3 is a local sandbox with small bounded runs and a kill switch.", "Do not call it production autonomy.", ["sandbox plan", "guardrail events"]),
        ("GOVERNANCE", "Governance and Cost Journey", "Make model and action risk visible.", ["Risk stakeholder", "AI platform owner"], "/ai-costing", ["Model status", "Pricing", "Usage", "Fallback"], "Governance is observable before any optional model spend.", "Do not run a smoke test without intentional credit acknowledgement.", ["status", "pricing snapshot", "usage audit"]),
        ("TESTING", "Testing and Evidence Journey", "Create a repeatable browser-first handover record.", ["Tester", "Demo presenter"], "/ui-acceptance", ["Catalog", "Test run", "Evidence fields", "Markdown report"], "Every important claim can be paired with a route and evidence note.", "Do not imply browser automation is included.", ["step results", "handover report"]),
    ]
    return {"journeys": [{"journey_id": item[0], "title": item[1], "goal": item[2], "personas": item[3], "ui_entry_point": item[4], "major_screens": item[5], "what_to_say": item[6], "what_to_avoid_claiming": item[7], "evidence_produced": item[8]} for item in journeys], "read_only": True}


def reset_guide() -> dict[str, Any]:
    return {"title": "Safe reset and replay guide", "read_only": True, "profiles": [{"profile": "SOFT_RESET", "when_to_use": "Replay scenarios while retaining all history.", "ui_path": "/demo-readiness/showcase", "script": "scripts/reset-demo-readiness.sh --profile SOFT_RESET", "preserves": ["seed data", "scenario events", "action audit", "model invocation audit", "AMS and operational history"]}, {"profile": "SHOWCASE_RESET", "when_to_use": "Prepare a deterministic showcase state and verify the four scenario catalog rows.", "ui_path": "/demo-readiness/showcase", "script": "scripts/prepare-showcase.sh", "preserves": ["seed/reference data", "audit history", "database schema"]}, {"profile": "LOCAL_DEV_GENERATED_DATA_RESET", "when_to_use": "Archive generated local demo run state during development.", "ui_path": "/demo-readiness/showcase", "script": "scripts/reset-demo-readiness.sh --profile LOCAL_DEV_GENERATED_DATA_RESET --confirmation RESET_LOCAL_DEMO_GENERATED_DATA", "confirmation": "RESET_LOCAL_DEMO_GENERATED_DATA", "preserves": ["seed data", "audit history", "database schema"]}], "rules": ["Never drop the database or schema.", "Reset marks/archives local generated records; it does not delete shared seed data.", "Audit history is retained by default.", "After Stage 2/3 demos, reset only generated scenario/run state before replaying."]}


def testing_guide() -> dict[str, Any]:
    return {"title": "Browser-first testing operating guide", "read_only": True, "workflow": ["Start and validate the local stack.", "Open the readiness and showcase pages.", "Use the guided scenario links instead of backend commands where possible.", "Capture observed results and screenshot filenames in UI acceptance runs.", "Complete the run and review the Markdown report.", "Use the baseline traceability matrix for handover."], "boundaries": ["Manual browser testing only; no browser automation is included.", "Real model calls are not required.", "Only explicit scenario/reset/approval actions mutate local demo records."], "primary_route": "/ui-acceptance"}


def model_guide() -> dict[str, Any]:
    return {"title": "Real model and cost guide", "read_only": True, "default_state": "Real model calls are off by default.", "model_catalog": "Use AI Costing > Models to add, edit, enable, or remove governed OpenAI model configurations; API keys remain environment-only and are never displayed or stored.", "pricing": "Pricing fields are local editable assumptions. Update input/output per-million-token values and source note before relying on estimates.", "dry_run": "Use the smoke-test Dry Run to validate readiness, pricing, limits, and expected maximum cost without calling a model.", "real_smoke_test": "Run a real smoke test only intentionally, with REAL_MODEL_ENABLED=true, a present API key, enabled provider/model, pricing, low output limits, and explicit cost acknowledgement.", "tracking": ["input_tokens", "completion_tokens", "total_tokens", "estimated_total_cost", "invocation ID", "pricing snapshot"], "credit_safety": ["No API key is required for startup, tests, seeds, or the normal demo.", "Do not run the real smoke test repeatedly.", "Estimated cost is based on local pricing assumptions, not an OpenAI invoice."], "routes": ["/ai-costing", "/ai-costing/models", "/ai-costing/usage", "/ai-costing/smoke-test"]}


def stage_modes() -> dict[str, Any]:
    return {"stage_modes": [
        {"mode": "STAGE_1_READ_ONLY", "purpose": "Gather evidence, retrieve knowledge, explain likely cause, and recommend next steps.", "default_state": "Enabled with deterministic/mock behavior.", "can_happen": ["Contextual investigation", "Knowledge-grounded guidance", "Optional governed model-assisted answer"], "cannot_happen": ["Action execution", "External sends", "ServiceNow updates", "Autonomous remediation"], "ui_pages": ["/agent-investigations", "/agent-chat", "/ai-costing"], "apis": ["/api/v1/agent-chat", "/api/v1/agent-model-chat"], "safety_controls": ["Input/output checks", "Fallback", "Invocation audit", "Stage 1 label"]},
        {"mode": "STAGE_2_APPROVAL_GATED", "purpose": "Propose and execute narrowly scoped local safe actions after human review.", "default_state": "Catalog/proposals available; execution requires explicit approval.", "can_happen": ["Dry run", "Approve/reject", "Local drafts, notes, checklists, status, links, acknowledgements"], "cannot_happen": ["Unapproved execution", "Shell/SQL", "External systems", "Customer send"], "ui_pages": ["/agent-investigations", "/agent-actions/proposals"], "apis": ["/api/v1/agent-actions"], "safety_controls": ["Safe catalog", "Approval gate", "Idempotency", "Execution audit"]},
        {"mode": "STAGE_3_AUTONOMOUS_SANDBOX", "purpose": "Demonstrate bounded local autonomy potential in a disposable demo-safe sandbox.", "default_state": "Execution disabled by default; dry-run-first.", "can_happen": ["Bounded deterministic plan", "Safe local action execution only when explicitly enabled", "Kill switch and human handback"], "cannot_happen": ["Production remediation", "Background polling", "Shell/SQL", "External systems", "Unbounded loop"], "ui_pages": ["/stage3-autonomy", "/stage3-autonomy/runs"], "apis": ["/api/v1/stage3-autonomy"], "safety_controls": ["Feature flag", "Kill switch", "Max steps/duration/cost", "Dry-run requirement", "Per-step audit"]},
    ], "read_only": True}


def known_limitations() -> dict[str, Any]:
    descriptions = [
        ("LIM-001", "Integrations", "No production ServiceNow integration.", "External ticket synchronization is not demonstrated.", "CURRENT_LIMITATION", "Add a ServiceNow sandbox connector in a future phase."),
        ("LIM-002", "Security", "No authentication or authorization.", "The local demo is not an enterprise access-control implementation.", "CURRENT_LIMITATION", "Add enterprise identity and role-based access."),
        ("LIM-003", "Autonomy", "No production autonomous remediation.", "Stage 3 is local sandbox only and disabled by default.", "CURRENT_LIMITATION", "Harden a controlled autonomy lab before any production consideration."),
        ("LIM-004", "Communications", "No external customer communication.", "Customer updates remain local drafts.", "CURRENT_LIMITATION", "Add governed communication integration only with explicit approvals."),
        ("LIM-005", "Testing", "No browser automation.", "UI acceptance is manual browser-first testing.", "CURRENT_LIMITATION", "Add Playwright E2E in a separate phase."),
        ("LIM-006", "Reporting", "No PDF evidence export.", "Reports are JSON/Markdown.", "CURRENT_LIMITATION", "Add a document export if needed."),
        ("LIM-007", "Observability", "No real production observability integration beyond the local stack.", "Signals are synthetic/local.", "CURRENT_LIMITATION", "Add production connector adapters."),
        ("LIM-008", "Value", "No production ROI calculator.", "Effort impact uses clearly labeled demo assumptions.", "CURRENT_LIMITATION", "Add governed commercial analytics from measured data."),
        ("LIM-009", "Model", "Real-model smoke testing is opt-in and not required.", "Normal startup and validation need no API key or credits.", "CURRENT_LIMITATION", "Run controlled real-model validation only when intentionally funded."),
        ("LIM-010", "Sandbox", "Stage 3 is deterministic by default.", "No real model or autonomous execution is enabled by default.", "CURRENT_LIMITATION", "Expand only within a separately governed sandbox."),
    ]
    return {"limitations": [{"limitation_id": item[0], "area": item[1], "description": item[2], "impact": item[3], "status": item[4], "future_phase_recommendation": item[5]} for item in descriptions], "read_only": True}


def signoff_checklist() -> dict[str, Any]:
    areas = [
        ("Infrastructure", "Local stack and six experiences are reachable.", "/demo-readiness", "Run readiness and stack validation."),
        ("Synthetic business app", "Warehouse operational views and seed data are present.", "/warehouse", "Open warehouse pages."),
        ("AMS/ITSM", "Tickets, exceptions, reports, and handoffs are available.", "/ams/tickets", "Replay a source-object flow."),
        ("Monitoring and observability", "Local alerts, evidence, and telemetry views are available.", "/observability", "Review local observability controls."),
        ("Batch", "Batch runs and failure scenario are available.", "/batch/runs", "Run batch walkthrough."),
        ("Synthetic users", "Users and issue reports are seeded.", "/synthetic-users/journeys", "Review synthetic data."),
        ("Guided scenarios", "Four scenarios can be started and replayed.", "/demo-scenarios", "Start each scenario catalog entry."),
        ("Agent Stage 1", "Investigation, evidence, knowledge, and fallback chat are available.", "/agent-investigations", "Open workspace and ask deterministic question."),
        ("Agent Stage 2", "Safe proposals require approval and are audited.", "/agent-actions/proposals", "Dry-run, approve, execute, and review audit."),
        ("Agent Stage 3", "Local sandbox is bounded, dry-run-first, and disabled by default.", "/stage3-autonomy", "Review status and dry-run without execution."),
        ("Model governance", "Real model is off by default and key is environment-only.", "/ai-config/real-model", "Review status without entering a key."),
        ("AI costing", "Pricing, usage, guardrails, and smoke dry-run are available.", "/ai-costing", "Review assumptions and dry-run."),
        ("Executive dashboard", "Value storyboard and governance narrative are visible.", "/executive-demo", "Review executive walkthrough."),
        ("Demo readiness", "Readiness, showcase, reset, and smoke reports are available.", "/demo-readiness", "Review score and reports."),
        ("UI acceptance", "Manual catalog, evidence fields, and Markdown report are available.", "/ui-acceptance", "Record one browser result."),
        ("Experience segregation", "Business remains read-only and Observability excludes agent surfaces.", "/baseline-completion/requirements", "Check route boundaries."),
        ("Documentation", "README, architecture, walkthrough, and handover content are available.", "/baseline-completion/handover", "Read the generated pack."),
        ("Safety boundaries", "No external execution, ServiceNow, auth, or default autonomy is claimed.", "/baseline-completion/limitations", "Review limitations and stage modes."),
    ]
    items = [{"item": item[1], "status": "READY_WITH_LIMITATION" if item[0] in {"Model governance", "AI costing", "Agent Stage 3", "Monitoring and observability"} else "READY", "evidence_url_or_route": item[2], "validation_method": item[3], "notes": DISCLAIMER if item[0] in {"AI costing", "Executive dashboard"} else ""} for item in areas]
    return {"sections": [{"area": area, "items": [item]} for (area, *_), item in zip(areas, items)], "overall_status": "BASELINE_READY", "read_only": True}


def handover_pack(db: Session) -> dict[str, Any]:
    return {"title": f"{BASELINE_NAME} – Handover Pack", "summary": summary(db), "start_stack": ["./scripts/start-demo-stack.sh", "./scripts/status-demo-stack.sh", "./scripts/validate-demo-stack.sh"], "recommended_ui_opening_sequence": ["http://localhost:4001/executive-demo", "http://localhost:4001/demo-readiness", "http://localhost:4013/demo-scenarios", "http://localhost:4015/agent-investigations", "http://localhost:4015/ui-acceptance", "http://localhost:4001/baseline-completion"], "walkthroughs": walkthroughs()["walkthroughs"], "demo_journeys": demo_journeys()["journeys"], "requirements": requirements(), "reset_guide": reset_guide(), "testing_guide": testing_guide(), "model_guide": model_guide(), "stage_modes": stage_modes(), "known_limitations": known_limitations(), "signoff_checklist": signoff_checklist(), "recommended_next_phases": ["Phase 2 – Real-model controlled validation", "Phase 3 – Browser automation / Playwright E2E", "Phase 4 – ServiceNow sandbox integration", "Phase 5 – Enterprise authentication and role-based access", "Phase 6 – Production observability connectors", "Phase 7 – Controlled autonomous remediation lab", "Phase 8 – Commercial analytics and contract simulation"], "read_only": True, "safety_boundary": SAFETY_BOUNDARY}


def handover_markdown(db: Session) -> str:
    pack = handover_pack(db)
    req = pack["requirements"]["summary"]
    lines = [f"# {pack['title']}", "", DISCLAIMER, "", "## Baseline summary", f"- Status: **{pack['summary']['completion_status']}**", f"- Version: {pack['summary']['baseline_version']}", f"- Completed capability range: {pack['summary']['completed_prompt_range']}", f"- Real model default: **off**", f"- Stage 3 execution default: **off**", f"- ServiceNow: **not configured**", f"- Authentication: **not enabled**", "", "## Start the stack", "```bash", *pack["start_stack"], "```", "", "## Recommended UI opening sequence", *[f"- {url}" for url in pack["recommended_ui_opening_sequence"]], "", "## Walkthrough pack"]
    for item in pack["walkthroughs"]:
        lines.extend([f"### {item['title']} ({item['estimated_duration_minutes']} minutes)", f"Start: {item['start_url']}", f"Audience: {item['audience']}", f"- {item['steps'][0]['instruction']}"])
    lines.extend(["", "## Requirements traceability", f"- Total: {req['total']}", f"- Covered: {req['covered']}", f"- Out of scope: {req['out_of_scope']}", "See the JSON endpoint for route-level evidence and notes.", "", "## Stage modes"])
    for mode in pack["stage_modes"]["stage_modes"]:
        lines.extend([f"### {mode['mode']}", mode["purpose"], f"- Default: {mode['default_state']}", f"- Cannot: {', '.join(mode['cannot_happen'])}"])
    lines.extend(["", "## Reset and replay", *[f"- **{item['profile']}**: {item['when_to_use']} UI `{item['ui_path']}`; script `{item['script']}`" for item in pack["reset_guide"]["profiles"]], "", "## Real model and costing", pack["model_guide"]["default_state"], pack["model_guide"]["credit_safety"][2], "", "## Known limitations"])
    lines.extend([f"- {item['description']} — {item['future_phase_recommendation']}" for item in pack["known_limitations"]["limitations"]])
    lines.extend(["", "## Final sign-off", *[f"- [{item['status']}] {item['item']} — `{item['evidence_url_or_route']}`" for section in pack["signoff_checklist"]["sections"] for item in section["items"]], "", "## Recommended next phases", *[f"- {phase}" for phase in pack["recommended_next_phases"]], "", "## Safety boundary", SAFETY_BOUNDARY])
    return "\n".join(lines) + "\n"
