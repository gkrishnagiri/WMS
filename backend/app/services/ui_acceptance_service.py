"""Manual browser-first UI acceptance catalog, runs, and evidence reports."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ui_acceptance import UiTestCase, UiTestRun, UiTestRunEvent, UiTestStep, UiTestStepResult, UiTestSuite


class UiAcceptanceError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


STEP_STATUSES = {"PASSED", "FAILED", "BLOCKED", "WARNING", "SKIPPED"}
RUN_STATUSES = {"NOT_STARTED", "IN_PROGRESS", "PASSED", "PASSED_WITH_WARNINGS", "FAILED", "ABORTED"}


def _step(code: str, url: str, click: str, expected: str, capture: str, mutating: bool = False, safety: str = "Read-only browser validation; capture evidence without changing EOS data.") -> dict[str, Any]:
    return {"step_code": code, "target_url": url, "what_to_click": click, "instruction": click, "expected_result": expected, "evidence_to_capture": capture, "is_mutating_step": mutating, "safety_note": safety}


def _case(code: str, title: str, description: str, url: str, steps: list[dict[str, Any]], preconditions: str = "EOS local demo stack is running and the required seed data is present.") -> dict[str, Any]:
    return {"case_code": code, "title": title, "description": description, "preconditions": preconditions, "expected_outcome": "All listed browser observations are visible and any mutation is explicit, local, and presenter-controlled.", "primary_url": url, "steps": steps}


UI_TEST_CATALOG: list[dict[str, Any]] = [
    {"suite_code": "EXECUTIVE_DEMO_VALIDATION", "title": "Executive Demo Validation", "description": "Validate executive dashboard, value storyboard, governance view, and commercial model narrative.", "experience": "business,full", "sort_order": 10, "cases": [_case("EXECUTIVE_DASHBOARD_READ_ONLY", "Executive dashboard read-only flow", "Validate the leadership-facing value storyboard without mutation controls.", "/executive-demo", [_step("OPEN_EXECUTIVE_DEMO", "/executive-demo", "Open the Executive Demo page.", "Executive summary and KPI cards are visible.", "Headline and KPI cards."), _step("VERIFY_STORYBOARD", "/executive-demo/storyboard", "Open the Storyboard view.", "Traditional challenge, AI-native model, proof points, and roadmap are visible.", "Storyboard sections."), _step("VERIFY_GOVERNANCE", "/executive-demo/governance", "Open Governance.", "Real model default off and autonomous remediation disabled are visible.", "Governance badges."), _step("VERIFY_COMMERCIAL_MODEL", "/executive-demo/value", "Open Value and review the commercial model section.", "Traditional-to-AI-native narrative and demo labels are visible.", "Commercial model rows."), _step("VERIFY_ASSUMPTION_DISCLAIMER", "/executive-demo", "Review the value estimate disclaimer.", "Demo estimate and illustrative assumptions are clearly labeled.", "Disclaimer text."), _step("VERIFY_NO_MUTATION_CONTROLS", "/executive-demo", "Look for reset, approval, execution, or API-key controls.", "No mutation, credential, or remediation controls are present.", "Read-only boundary.")])]},
    {"suite_code": "DEMO_READINESS_SHOWCASE_VALIDATION", "title": "Demo Readiness and Showcase Validation", "description": "Validate readiness score, smoke report, URL launcher, reset profiles, and showcase preparation.", "experience": "full,operations,simulation,agentic,business-read-only", "sort_order": 20, "cases": [_case("DEMO_READINESS_BROWSER_FLOW", "Readiness and showcase browser flow", "Validate the presenter preparation pages and Business boundary.", "/demo-readiness", [_step("OPEN_DEMO_READINESS", "/demo-readiness", "Open Demo Readiness.", "Readiness score, critical checks, and safety badges are visible.", "Score and check table."), _step("OPEN_SMOKE_REPORT", "/demo-readiness/smoke-report", "Open Smoke Report.", "Stack, seed, scenario, action, model, and BFF summaries are visible.", "Smoke report."), _step("OPEN_UI_TEST_GUIDE", "/demo-readiness/ui-test-guide", "Open UI Test Guide.", "Browser-first test sections and expected outcomes are visible.", "Guide section."), _step("OPEN_URL_LAUNCHER", "/demo-readiness/showcase", "Open Showcase Mode and review the URL launcher.", "Ordered presenter links are visible.", "Launcher list."), _step("PREPARE_SHOWCASE", "/demo-readiness/showcase", "In an allowed experience, click Prepare showcase.", "Local showcase preparation completes without model calls or action execution.", "Preparation response and readiness refresh.", True, "This is an explicit local reset/preparation step; it never approves or executes actions."), _step("VERIFY_BUSINESS_READ_ONLY", "/demo-readiness", "Open the Business UI readiness page.", "Readiness is visible and reset/preparation controls are hidden.", "Business read-only view.")])]},
    {"suite_code": "GUIDED_SCENARIO_VALIDATION", "title": "Guided Scenario Validation", "description": "Validate all four guided demo scenarios and presenter-controlled flows.", "experience": "full,operations,simulation,agentic", "sort_order": 30, "cases": [
        _case("STUCK_FULFILLMENT_ORDER_FLOW", "Stuck Fulfillment Order flow", "Validate issue induction through action audit for the stuck order storyline.", "/demo-scenarios", [_step("OPEN_SCENARIO_CATALOG", "/demo-scenarios", "Open Guided Demo Scenarios.", "Four scenario cards are visible.", "Scenario catalog."), _step("START_STUCK_ORDER", "/demo-scenarios", "Start Stuck Fulfillment Order.", "A local run opens with a guided checklist and initial artifacts.", "Run ID and artifacts.", True, "Explicitly starts a local synthetic scenario only."), _step("ADVANCE_STUCK_ORDER", "/demo-scenarios/runs/<RUN_ID>", "Advance to issue induction and open the generated ticket or exception.", "Local operations evidence is visible.", "Exception or ticket link."), _step("INVESTIGATE_STUCK_ORDER", "/agent-investigations/<CASE_ID>", "Click Investigate with Agent.", "Workspace shows evidence, knowledge, timeline, and action proposals.", "Investigation workspace."), _step("VERIFY_STUCK_ACTION_AUDIT", "/agent-actions/proposals", "Dry-run, approve, and explicitly execute one predefined safe action.", "Only the approved local action executes and audit/timeline update.", "Approval and execution audit.", True, "Requires explicit human approval and execution; no autonomous action is allowed.")]),
        _case("BATCH_FAILURE_RECOVERY_FLOW", "Batch Failure Recovery flow", "Validate failed batch evidence and checklist review.", "/demo-scenarios", [_step("START_BATCH_FAILURE", "/demo-scenarios", "Start Batch Failure Recovery.", "A local failed batch run and linked context are created.", "Batch run artifact.", True, "Explicitly starts a local deterministic batch scenario."), _step("OPEN_BATCH_FAILURE", "/batch/runs/<BATCH_RUN_ID>", "Open the failed batch run.", "Failed step and event history are visible.", "Batch failure evidence."), _step("OPEN_BATCH_ALERT", "/observability-alerts", "Open the linked local alert or diagnostic context.", "Alert evidence is linked and unresolved.", "Alert context."), _step("INVESTIGATE_BATCH", "/agent-investigations/<CASE_ID>", "Investigate with Agent.", "Batch evidence and runbook knowledge are visible.", "Knowledge and evidence."), _step("REVIEW_BATCH_CHECKLIST", "/agent-actions/proposals", "Review and approve a next-steps checklist proposal.", "Approval is recorded and no command is executed.", "Checklist proposal and audit.", True, "Approval-gated local draft only.")]),
        _case("USER_REPORTED_SHIPMENT_DELAY_FLOW", "User-Reported Shipment Delay flow", "Validate user report, linked ticket, investigation, and draft boundary.", "/demo-scenarios", [_step("START_SHIPMENT_DELAY", "/demo-scenarios", "Start User-Reported Shipment Delay.", "A synthetic report and local AMS ticket are linked.", "Report and ticket artifacts.", True, "Explicitly creates local synthetic report data."), _step("OPEN_USER_REPORT", "/user-reports/<REPORT_ID>", "Open the generated user report.", "Original report wording and business impact are visible.", "User report."), _step("OPEN_LINKED_TICKET", "/ams/tickets/<TICKET_ID>", "Open the linked AMS ticket.", "Local ticket context is visible.", "Ticket detail."), _step("INVESTIGATE_SHIPMENT", "/agent-investigations/<CASE_ID>", "Investigate with Agent.", "Evidence and read-only guidance are visible.", "Workspace evidence."), _step("VERIFY_CUSTOMER_DRAFT", "/agent-actions/proposals", "Review the customer-update draft.", "Draft exists locally and no customer communication is sent.", "Draft and no-send boundary.")]),
        _case("OBSERVABILITY_ALERT_NOISE_FLOW", "Observability Alert Noise flow", "Validate alert grouping, evidence, governance, and local acknowledgement proposal.", "/demo-scenarios", [_step("START_ALERT_NOISE", "/demo-scenarios", "Start Observability Alert Noise to Root Cause.", "Multiple local alerts and a triage artifact are available.", "Alert cluster and triage.", True, "Explicitly creates local synthetic alert data."), _step("OPEN_ALERT_TRIAGE", "/monitoring/triage-cases/<TRIAGE_ID>", "Open the alert/triage artifacts.", "Grouped alerts and triage context are visible.", "Triage case."), _step("INVESTIGATE_ALERT_NOISE", "/agent-investigations/<CASE_ID>", "Investigate with Agent.", "Grouped evidence and known-error/runbook context are visible.", "Evidence timeline."), _step("VERIFY_ACKNOWLEDGEMENT_PROPOSAL", "/agent-actions/proposals", "Review the local acknowledgement proposal.", "Proposal is clearly not a resolve/remediation action.", "Safe action proposal."), _step("VERIFY_ALERT_AUDIT", "/agent-actions/executions", "Review action audit after any explicit approved acknowledgement.", "Approval and local acknowledgement are traceable.", "Execution audit.", True, "Acknowledge only after explicit approval; do not resolve alerts.")]),
    ]},
    {"suite_code": "OPERATIONS_AGENT_HANDOFF_VALIDATION", "title": "Operations-to-Agent Handoff Validation", "description": "Validate Investigate with Agent from local operational source objects.", "experience": "operations,agentic,full", "sort_order": 40, "cases": [_case("SOURCE_OBJECT_HANDOFFS", "Operational source handoffs", "Review handoff controls from AMS, alerts, batches, reports, diagnostics, triage, and exceptions.", "/operations/exceptions", [_step("OPEN_OPERATIONS_SOURCE", "/operations/exceptions", "Open a local operations exception.", "The source object has contextual details and an Investigate with Agent path.", "Exception source."), _step("OPEN_AMS_SOURCE", "/ams/tickets", "Open a local AMS ticket.", "Ticket context and handoff control are visible.", "AMS handoff."), _step("OPEN_ALERT_SOURCE", "/observability-alerts", "Open a local observability alert event.", "Alert context can be reviewed without resolution controls.", "Alert handoff."), _step("OPEN_BATCH_SOURCE", "/batch/runs", "Open a local batch run.", "Batch failure context is available.", "Batch handoff."), _step("VERIFY_HANDOFF_WORKSPACE", "/agent-investigations", "Use an available Investigate with Agent link.", "A case/session/workspace is created using deterministic handoff.", "Workspace link."), _step("VERIFY_OTHER_SOURCE_BOUNDARIES", "/agent-investigations", "Review report, diagnostic, triage, and exception source context where available.", "Source metadata remains local and bounded.", "Source summary.")])]},
    {"suite_code": "AGENT_INVESTIGATION_WORKSPACE_VALIDATION", "title": "Agent Investigation Workspace Validation", "description": "Validate source context, evidence, knowledge, drafts, chat, actions, and scenario linkage.", "experience": "agentic,operations,full", "sort_order": 50, "cases": [_case("INVESTIGATION_WORKSPACE_DETAIL", "Investigation workspace detail", "Review all read-only investigation panels and scenario backlink.", "/agent-investigations", [_step("OPEN_INVESTIGATIONS", "/agent-investigations", "Open the investigations list.", "Agent cases and source summaries are visible.", "Investigation list."), _step("OPEN_WORKSPACE", "/agent-investigations/<CASE_ID>", "Open a case workspace.", "Case source context and current step are visible.", "Workspace header."), _step("VERIFY_EVIDENCE_TIMELINE", "/agent-investigations/<CASE_ID>", "Review evidence timeline and evidence items.", "Evidence events are ordered and linked to source objects.", "Timeline and evidence."), _step("VERIFY_KNOWLEDGE", "/agent-investigations/<CASE_ID>", "Review retrieved knowledge and known errors.", "Knowledge citations are visible.", "Knowledge citations."), _step("VERIFY_CHAT_AND_ACTIONS", "/agent-investigations/<CASE_ID>", "Review Stage 1 chat metadata and Stage 2 proposals.", "Model status/fallback and approval-gated actions are clearly separated.", "Chat and action panels."), _step("VERIFY_SCENARIO_BACKLINK", "/demo-scenarios/runs/<RUN_ID>", "Open the guided scenario backlink.", "Scenario, run, and step context link back to the presenter flow.", "Scenario backlink.")])]},
    {"suite_code": "MODEL_ASSISTED_STAGE1_CHAT_FALLBACK_VALIDATION", "title": "Model-Assisted Stage 1 Chat Fallback Validation", "description": "Validate disabled/default model status, preview, dry-run, deterministic ask, and safe fallback.", "experience": "agentic,operations,full", "sort_order": 60, "cases": [_case("MODEL_CHAT_FALLBACK_FLOW", "Governed model fallback flow", "Validate model-assisted controls without requiring credentials or a real call.", "/agent-investigations/<CASE_ID>", [_step("VERIFY_MODEL_OFF", "/agent-investigations/<CASE_ID>", "Open Model-Assisted Chat and leave the toggle off.", "Real model is off by default and Stage 1 read-only warning is visible.", "Model status badge."), _step("PREVIEW_MODEL_CONTEXT", "/agent-investigations/<CASE_ID>", "Click Preview Context.", "Bounded case, evidence, knowledge, and action context is displayed without a model call.", "Context preview."), _step("DRY_RUN_MODEL", "/agent-investigations/<CASE_ID>", "Click Dry Run.", "Prompt, safety, readiness, and guardrails validate without a model call.", "Dry-run result."), _step("ASK_DETERMINISTIC", "/agent-investigations/<CASE_ID>", "Ask a read-only question with real model disabled.", "Deterministic response is returned and actions executed remains zero.", "Generation mode."), _step("VERIFY_DISABLED_FALLBACK", "/agent-investigations/<CASE_ID>", "Request real model while the feature remains disabled.", "Safe deterministic fallback and reason are displayed.", "Fallback reason."), _step("VERIFY_NO_CREDENTIAL_EXPOSURE", "/ai-config/real-model", "Review the model status page.", "No API key input or secret value is displayed.", "Credential boundary.")])]},
    {"suite_code": "STAGE2_APPROVAL_GATED_ACTION_VALIDATION", "title": "Stage 2 Approval-Gated Action Validation", "description": "Validate safe proposals, dry-run, approval/rejection, execution audit, duplicate prevention, and timeline updates.", "experience": "agentic,operations,full", "sort_order": 70, "cases": [_case("APPROVAL_GATED_ACTION_FLOW", "Approval-gated local action flow", "Validate explicit human approval before a predefined local action.", "/agent-actions/proposals", [_step("OPEN_ACTION_PROPOSALS", "/agent-actions/proposals", "Open action proposals for a case.", "Only predefined safe catalog actions are listed.", "Proposal list."), _step("DRY_RUN_SAFE_ACTION", "/agent-actions/proposals", "Click Dry Run on a proposal.", "Expected local change and safety notes are shown without mutation.", "Dry-run output."), _step("REJECT_PROPOSAL", "/agent-actions/proposals", "Reject one proposal with a reason.", "Rejected proposal cannot execute.", "Rejection audit."), _step("APPROVE_PROPOSAL", "/agent-actions/proposals", "Approve another proposal with a role and comment.", "Proposal enters approved state and does not execute automatically.", "Approval audit.", True, "Explicit human approval only."), _step("EXECUTE_APPROVED", "/agent-actions/proposals", "Click Execute Approved Action and confirm the local-only warning.", "Only the approved local safe action executes.", "Execution result.", True, "No shell, SQL, external system, ServiceNow, or customer send capability exists."), _step("VERIFY_AUDIT_TIMELINE", "/agent-actions/executions", "Review execution history and linked investigation timeline.", "Approval, execution, result, and actor are recorded.", "Audit and timeline."), _step("VERIFY_DUPLICATE_GUARD", "/agent-actions/executions", "Attempt the same execution a second time.", "Duplicate is safely skipped or prevented.", "Duplicate result.")])]},
    {"suite_code": "GOVERNANCE_BOUNDARY_VALIDATION", "title": "Governance Boundary Validation", "description": "Validate experience boundaries, safe defaults, and absence of prohibited capabilities.", "experience": "business,operations,simulation,observability,agentic,full", "sort_order": 80, "cases": [_case("EXPERIENCE_AND_SAFETY_BOUNDARIES", "Experience and governance boundaries", "Validate that each experience exposes only its intended read or control surface.", "/executive-demo", [_step("VERIFY_BUSINESS_BOUNDARY", "http://localhost:4011/executive-demo", "Open Business UI and inspect navigation.", "Business view is leadership-oriented and read-only.", "Business navigation."), _step("VERIFY_OBSERVABILITY_BOUNDARY", "http://localhost:4014/observability", "Open Observability UI and try unrelated agent/readiness routes.", "Routes are unavailable or intentionally outside the experience.", "Boundary response."), _step("VERIFY_MODEL_DEFAULT", "/ai-config/real-model", "Open governed model status.", "Real model default is off and key presence is not exposed as a secret.", "Model status."), _step("VERIFY_NO_AUTONOMY", "/demo-readiness", "Review readiness safety badges.", "Autonomous remediation is disabled.", "Safety badges."), _step("VERIFY_NO_EXTERNALS", "/executive-demo/governance", "Review governance controls.", "No ServiceNow, customer-send, shell, or arbitrary SQL capability is presented.", "Prohibited capability list."), _step("VERIFY_AUDIT_BOUNDARY", "/agent-actions/executions", "Review available audit surfaces.", "Local approvals and executions are traceable.", "Audit surface.")])]},
]


def _now() -> datetime:
    return datetime.now(timezone.utc)


def seed_catalog(db: Session) -> int:
    created = 0
    for suite_data in UI_TEST_CATALOG:
        suite = db.scalar(select(UiTestSuite).where(UiTestSuite.suite_code == suite_data["suite_code"]))
        if suite is None:
            suite = UiTestSuite(suite_code=suite_data["suite_code"])
            db.add(suite)
            created += 1
        suite.title, suite.description, suite.experience = suite_data["title"], suite_data["description"], suite_data["experience"]
        suite.sort_order, suite.is_enabled = suite_data["sort_order"], True
        db.flush()
        for case_order, case_data in enumerate(suite_data["cases"], 1):
            case = db.scalar(select(UiTestCase).where(UiTestCase.case_code == case_data["case_code"]))
            if case is None:
                case = UiTestCase(case_code=case_data["case_code"])
                db.add(case)
                created += 1
            case.suite_code, case.title, case.description = suite.suite_code, case_data["title"], case_data["description"]
            case.preconditions, case.expected_outcome, case.primary_url = case_data["preconditions"], case_data["expected_outcome"], case_data["primary_url"]
            case.sort_order, case.is_enabled = case_order, True
            db.flush()
            for step_order, step_data in enumerate(case_data["steps"], 1):
                step = db.scalar(select(UiTestStep).where(UiTestStep.case_code == case.case_code, UiTestStep.step_code == step_data["step_code"]))
                if step is None:
                    step = UiTestStep(case_code=case.case_code, step_code=step_data["step_code"])
                    db.add(step)
                    created += 1
                for field in ("instruction", "target_url", "what_to_click", "expected_result", "evidence_to_capture", "is_mutating_step", "safety_note"):
                    setattr(step, field, step_data[field])
                step.step_order = step_order
    db.flush()
    return created


def _step_dict(step: UiTestStep, result: UiTestStepResult | None = None) -> dict[str, Any]:
    return {"id": step.id, "step_code": step.step_code, "case_code": step.case_code, "step_order": step.step_order, "instruction": step.instruction, "target_url": step.target_url, "what_to_click": step.what_to_click, "expected_result": step.expected_result, "evidence_to_capture": step.evidence_to_capture, "is_mutating_step": step.is_mutating_step, "safety_note": step.safety_note, "result": _result_dict(result) if result else None}


def _result_dict(result: UiTestStepResult) -> dict[str, Any]:
    return {"id": result.id, "suite_code": result.suite_code, "case_code": result.case_code, "step_code": result.step_code, "status": result.status, "observed_result": result.observed_result, "evidence_note": result.evidence_note, "screenshot_reference": result.screenshot_reference, "defect_note": result.defect_note, "tested_by_role": result.tested_by_role, "tested_at": result.tested_at}


def _case_dict(db: Session, case: UiTestCase, run: UiTestRun | None = None) -> dict[str, Any]:
    steps = db.scalars(select(UiTestStep).where(UiTestStep.case_code == case.case_code).order_by(UiTestStep.step_order)).all()
    results: dict[str, UiTestStepResult] = {}
    if run:
        results = {item.step_code: item for item in db.scalars(select(UiTestStepResult).where(UiTestStepResult.run_id == run.id, UiTestStepResult.case_code == case.case_code)).all()}
    return {"id": case.id, "case_code": case.case_code, "suite_code": case.suite_code, "title": case.title, "description": case.description, "preconditions": case.preconditions, "expected_outcome": case.expected_outcome, "primary_url": case.primary_url, "sort_order": case.sort_order, "is_enabled": case.is_enabled, "steps": [_step_dict(step, results.get(step.step_code)) for step in steps]}


def list_suites(db: Session) -> list[dict[str, Any]]:
    suites = db.scalars(select(UiTestSuite).order_by(UiTestSuite.sort_order, UiTestSuite.suite_code)).all()
    return [{"id": suite.id, "suite_code": suite.suite_code, "title": suite.title, "description": suite.description, "experience": suite.experience, "sort_order": suite.sort_order, "is_enabled": suite.is_enabled, "case_count": int(db.scalar(select(func.count(UiTestCase.id)).where(UiTestCase.suite_code == suite.suite_code)) or 0), "step_count": int(db.scalar(select(func.count(UiTestStep.id)).join(UiTestCase, UiTestStep.case_code == UiTestCase.case_code).where(UiTestCase.suite_code == suite.suite_code)) or 0)} for suite in suites]


def list_cases(db: Session, suite_code: str | None = None) -> list[dict[str, Any]]:
    query = select(UiTestCase).where(UiTestCase.is_enabled.is_(True)).order_by(UiTestCase.suite_code, UiTestCase.sort_order, UiTestCase.case_code)
    if suite_code:
        query = query.where(UiTestCase.suite_code == suite_code.upper())
    return [_case_dict(db, case) for case in db.scalars(query).all()]


def get_case(db: Session, case_code: str) -> dict[str, Any]:
    case = db.scalar(select(UiTestCase).where(UiTestCase.case_code == case_code.upper()))
    if case is None:
        raise UiAcceptanceError("UI acceptance case was not found.", 404)
    return _case_dict(db, case)


def _run_number(db: Session) -> str:
    current = db.scalar(select(func.max(UiTestRun.run_id)).where(UiTestRun.run_id.like("UI-RUN-%")))
    try:
        return f"UI-RUN-{int(str(current).rsplit('-', 1)[1]) + 1:04d}" if current else "UI-RUN-0001"
    except (ValueError, IndexError):
        return f"UI-RUN-{int(db.scalar(select(func.count(UiTestRun.id))) or 0) + 1:04d}"


def _event(db: Session, run: UiTestRun, event_type: str, title: str, description: str) -> None:
    db.add(UiTestRunEvent(run_id=run.id, event_type=event_type, event_title=title, event_description=description, metadata_json={"local_demo_only": True}))


def _selected_cases(db: Session, run: UiTestRun) -> list[UiTestCase]:
    codes = run.suite_codes or [item.suite_code for item in db.scalars(select(UiTestSuite).where(UiTestSuite.is_enabled.is_(True))).all()]
    return db.scalars(select(UiTestCase).where(UiTestCase.suite_code.in_(codes), UiTestCase.is_enabled.is_(True)).order_by(UiTestCase.suite_code, UiTestCase.sort_order)).all()


def _run_dict(db: Session, run: UiTestRun, include_details: bool = True) -> dict[str, Any]:
    cases = _selected_cases(db, run)
    results = {item.step_code: item for item in db.scalars(select(UiTestStepResult).where(UiTestStepResult.run_id == run.id)).all()}
    total = sum(len(db.scalars(select(UiTestStep.id).where(UiTestStep.case_code == case.case_code)).all()) for case in cases)
    tested = sum(1 for result in results.values() if result.status != "NOT_TESTED")
    return {"id": run.id, "run_id": run.run_id, "run_title": run.run_title, "status": run.status, "tester_role": run.tester_role, "suite_codes": run.suite_codes, "started_at": run.started_at, "completed_at": run.completed_at, "summary": run.summary, "progress": {"total_steps": total, "tested_steps": tested, "coverage_percent": round(tested * 100 / total, 1) if total else 0}, "suites": [{"suite_code": case.suite_code, "case_code": case.case_code} for case in cases], "cases": [_case_dict(db, case, run) for case in cases] if include_details else [], "events": [{"id": event.id, "event_type": event.event_type, "event_title": event.event_title, "event_description": event.event_description, "created_at": event.created_at} for event in db.scalars(select(UiTestRunEvent).where(UiTestRunEvent.run_id == run.id).order_by(UiTestRunEvent.created_at, UiTestRunEvent.id)).all()]}


def start_run(db: Session, run_title: str, tester_role: str, suite_codes: list[str] | None = None) -> dict[str, Any]:
    enabled = [item.suite_code for item in db.scalars(select(UiTestSuite).where(UiTestSuite.is_enabled.is_(True)).order_by(UiTestSuite.sort_order)).all()]
    selected = [code.upper() for code in (suite_codes or enabled)]
    if not selected:
        raise UiAcceptanceError("No enabled UI acceptance suites are seeded.", 409)
    missing = sorted(set(selected) - set(enabled))
    if missing:
        raise UiAcceptanceError(f"Unknown or disabled suite codes: {', '.join(missing)}", 400)
    run = UiTestRun(run_id=_run_number(db), run_title=run_title, tester_role=tester_role, status="IN_PROGRESS", suite_codes=selected)
    db.add(run)
    db.flush()
    _event(db, run, "RUN_STARTED", "UI acceptance run started", f"Manual browser-first run started for {len(selected)} suite(s).")
    db.commit()
    return _run_dict(db, run)


def get_run(db: Session, run_id: str) -> UiTestRun:
    run = db.scalar(select(UiTestRun).where(UiTestRun.run_id == run_id))
    if run is None:
        raise UiAcceptanceError("UI acceptance run was not found.", 404)
    return run


def list_runs(db: Session) -> list[dict[str, Any]]:
    return [_run_dict(db, run, include_details=False) for run in db.scalars(select(UiTestRun).order_by(UiTestRun.started_at.desc(), UiTestRun.id.desc())).all()]


def record_step_result(db: Session, run_id: str, suite_code: str, case_code: str, step_code: str, status: str, observed_result: str | None, evidence_note: str | None, screenshot_reference: str | None, defect_note: str | None, tested_by_role: str) -> dict[str, Any]:
    run = get_run(db, run_id)
    if run.status not in {"IN_PROGRESS", "NOT_STARTED"}:
        raise UiAcceptanceError("Step results can only be recorded for an active run.", 409)
    status = status.upper()
    if status not in STEP_STATUSES:
        raise UiAcceptanceError(f"Unsupported step result status: {status}", 400)
    step = db.scalar(select(UiTestStep).where(UiTestStep.step_code == step_code.upper(), UiTestStep.case_code == case_code.upper()))
    if step is None or step.case.suite_code != suite_code.upper() or suite_code.upper() not in (run.suite_codes or []):
        raise UiAcceptanceError("The suite, case, and step are not part of this test run.", 400)
    result = db.scalar(select(UiTestStepResult).where(UiTestStepResult.run_id == run.id, UiTestStepResult.suite_code == suite_code.upper(), UiTestStepResult.case_code == case_code.upper(), UiTestStepResult.step_code == step_code.upper()))
    if result is None:
        result = UiTestStepResult(run_id=run.id, suite_code=suite_code.upper(), case_code=case_code.upper(), step_code=step_code.upper(), tested_by_role=tested_by_role)
        db.add(result)
    result.status, result.observed_result, result.evidence_note = status, observed_result, evidence_note
    result.screenshot_reference, result.defect_note, result.tested_by_role, result.tested_at = screenshot_reference, defect_note, tested_by_role, _now()
    _event(db, run, "STEP_RESULT_RECORDED", f"Step {step_code.upper()} marked {status}", observed_result or "Manual browser result recorded.")
    db.commit()
    return _run_dict(db, run)


def complete_run(db: Session, run_id: str, summary: str | None) -> dict[str, Any]:
    run = get_run(db, run_id)
    if run.status in {"ABORTED", "PASSED", "PASSED_WITH_WARNINGS", "FAILED"}:
        raise UiAcceptanceError("This UI acceptance run is already closed.", 409)
    results = db.scalars(select(UiTestStepResult).where(UiTestStepResult.run_id == run.id)).all()
    statuses = [item.status for item in results]
    required_steps = sum(int(db.scalar(select(func.count(UiTestStep.id)).where(UiTestStep.case_code == case.case_code)) or 0) for case in _selected_cases(db, run))
    if "FAILED" in statuses or "BLOCKED" in statuses or len(results) < required_steps:
        run.status = "FAILED"
    elif "WARNING" in statuses or "SKIPPED" in statuses:
        run.status = "PASSED_WITH_WARNINGS"
    else:
        run.status = "PASSED"
    run.completed_at, run.summary = _now(), summary or "Manual UI acceptance run completed."
    _event(db, run, "RUN_COMPLETED", "UI acceptance run completed", run.summary)
    db.commit()
    return _run_dict(db, run)


def abort_run(db: Session, run_id: str, summary: str | None) -> dict[str, Any]:
    run = get_run(db, run_id)
    if run.status not in {"IN_PROGRESS", "NOT_STARTED"}:
        raise UiAcceptanceError("This UI acceptance run is already closed.", 409)
    run.status, run.completed_at, run.summary = "ABORTED", _now(), summary or "Manual UI acceptance run aborted."
    _event(db, run, "RUN_ABORTED", "UI acceptance run aborted", run.summary)
    db.commit()
    return _run_dict(db, run)


def report(db: Session, run_id: str) -> dict[str, Any]:
    run = get_run(db, run_id)
    cases = _selected_cases(db, run)
    results = db.scalars(select(UiTestStepResult).where(UiTestStepResult.run_id == run.id).order_by(UiTestStepResult.suite_code, UiTestStepResult.case_code, UiTestStepResult.step_code)).all()
    counts = {status: sum(1 for item in results if item.status == status) for status in ["PASSED", "FAILED", "BLOCKED", "WARNING", "SKIPPED"]}
    suite_summary: list[dict[str, Any]] = []
    for suite_code in run.suite_codes or []:
        suite_results = [item for item in results if item.suite_code == suite_code]
        suite_summary.append({"suite_code": suite_code, "case_count": sum(1 for item in cases if item.suite_code == suite_code), "tested_steps": len(suite_results), "passed_steps": sum(1 for item in suite_results if item.status == "PASSED"), "failed_steps": sum(1 for item in suite_results if item.status in {"FAILED", "BLOCKED"})})
    return {"run_id": run.run_id, "run_title": run.run_title, "tester_role": run.tester_role, "status": run.status, "started_at": run.started_at, "completed_at": run.completed_at, "summary": run.summary, "suite_summary": suite_summary, "status_counts": counts, "step_results": [_result_dict(item) for item in results], "coverage": coverage(db, run_id), "safety_confirmations": ["Manual browser-first testing only", "Real model calls are not required", "Actions are local and approval-gated", "No shell, SQL, ServiceNow, customer-send, or autonomous remediation capability is available"], "known_limitations": ["Screenshot files are referenced by text only; binary upload is not implemented.", "Results depend on the tester's browser observations."]}


def report_markdown(db: Session, run_id: str) -> str:
    data = report(db, run_id)
    lines = [f"# UI Acceptance Report: {data['run_id']}", "", f"- Title: {data['run_title']}", f"- Tester role: {data['tester_role']}", f"- Status: {data['status']}", f"- Started: {data['started_at']}", f"- Completed: {data['completed_at'] or 'In progress'}", "", "## Coverage", f"- Coverage: {data['coverage']['coverage_percent']}%", f"- Counts: {data['status_counts']}", "", "## Suite summary"]
    lines.extend(f"- {item['suite_code']}: {item['tested_steps']} tested, {item['passed_steps']} passed, {item['failed_steps']} failed/blocked" for item in data["suite_summary"])
    lines.extend(["", "## Evidence"])
    for item in data["step_results"]:
        lines.extend([f"### {item['suite_code']} / {item['case_code']} / {item['step_code']}", f"- Status: {item['status']}", f"- Observed: {item['observed_result'] or '—'}", f"- Evidence note: {item['evidence_note'] or '—'}", f"- Screenshot reference: {item['screenshot_reference'] or '—'}", f"- Defect: {item['defect_note'] or '—'}"])
    lines.extend(["", "## Safety confirmations", *[f"- {item}" for item in data["safety_confirmations"]], "", "## Limitations", *[f"- {item}" for item in data["known_limitations"]]])
    return "\n".join(lines) + "\n"


def coverage(db: Session, run_id: str | None = None) -> dict[str, Any]:
    total = int(db.scalar(select(func.count(UiTestStep.id)).join(UiTestCase, UiTestStep.case_code == UiTestCase.case_code).join(UiTestSuite, UiTestCase.suite_code == UiTestSuite.suite_code).where(UiTestSuite.is_enabled.is_(True))) or 0)
    query = select(UiTestStepResult)
    if run_id:
        run = get_run(db, run_id)
        query = query.where(UiTestStepResult.run_id == run.id)
    results = db.scalars(query).all()
    tested = sum(1 for item in results if item.status != "NOT_TESTED")
    return {"total_enabled_steps": total, "recorded_results": len(results), "tested_steps": tested, "passed_steps": sum(1 for item in results if item.status == "PASSED"), "failed_steps": sum(1 for item in results if item.status in {"FAILED", "BLOCKED"}), "warning_steps": sum(1 for item in results if item.status == "WARNING"), "coverage_percent": round(tested * 100 / total, 1) if total else 0, "classification": "Manual browser evidence; not automated E2E coverage.", "screenshot_upload_supported": False}


def summary(db: Session) -> dict[str, Any]:
    suites = list_suites(db)
    cases = int(db.scalar(select(func.count(UiTestCase.id)).where(UiTestCase.is_enabled.is_(True))) or 0)
    steps = int(db.scalar(select(func.count(UiTestStep.id)).join(UiTestCase, UiTestStep.case_code == UiTestCase.case_code).where(UiTestCase.is_enabled.is_(True))) or 0)
    runs = db.scalars(select(UiTestRun).order_by(UiTestRun.started_at.desc())).all()
    latest = runs[0] if runs else None
    return {"read_only_catalog": True, "enabled_suites": len([item for item in suites if item["is_enabled"]]), "total_suites": len(suites), "total_cases": cases, "total_steps": steps, "total_runs": len(runs), "latest_run_id": latest.run_id if latest else None, "latest_run_status": latest.status if latest else None, "latest_run": _run_dict(db, latest, include_details=False) if latest else None, "coverage": coverage(db), "safe_local_only": True, "browser_automation_enabled": False, "real_model_called_by_readiness": False, "external_services_required": False, "safety_note": "Manual browser-first acceptance records only; screenshot references are text fields and no binary upload is performed."}
