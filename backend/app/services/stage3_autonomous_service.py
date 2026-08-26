"""Bounded, synchronous, local-only Stage 3 autonomy sandbox."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.agent_chat import AgentActionProposal, AgentCase, AgentChatSession
from app.models.stage3_autonomy import Stage3AutonomousEvent, Stage3AutonomousRun, Stage3AutonomousStep, Stage3AutonomyControl
from app.services import agent_action_service

STAGE_MODE = "STAGE_3_AUTONOMOUS_SANDBOX"
SAFETY = "Local EOS sandbox only. No external systems, shell commands, arbitrary SQL, ServiceNow, customer communication, or production remediation."

PROFILE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "DRY_RUN_ONLY": {"title": "Dry run only", "description": "Build an autonomous plan without executing actions.", "allowed_actions": [], "execution_enabled": False},
    "LOCAL_DRAFT_AUTONOMY": {"title": "Local draft autonomy", "description": "Execute only local drafts, internal notes, checklists, and local case status updates.", "allowed_actions": ["CREATE_AMS_WORK_NOTE_DRAFT", "CREATE_CUSTOMER_UPDATE_DRAFT", "CREATE_NEXT_STEPS_CHECKLIST", "ADD_INTERNAL_CASE_NOTE", "UPDATE_AGENT_CASE_STATUS", "CREATE_FOLLOW_UP_TASK_DRAFT", "MARK_AGENT_PROPOSAL_REVIEWED", "LINK_EVIDENCE_TO_CASE"], "execution_enabled": True},
    "LOCAL_ACKNOWLEDGEMENT_AUTONOMY": {"title": "Local acknowledgement autonomy", "description": "Acknowledge local EOS alerts or exceptions and link evidence; never resolve them.", "allowed_actions": ["ACKNOWLEDGE_OBSERVABILITY_ALERT", "ACKNOWLEDGE_MONITORING_ALERT", "ACKNOWLEDGE_OPERATIONS_EXCEPTION", "LINK_EVIDENCE_TO_CASE", "ADD_INTERNAL_CASE_NOTE"], "execution_enabled": True},
    "HUMAN_HANDOFF_ON_UNCERTAINTY": {"title": "Human handoff on uncertainty", "description": "Use safe local actions only while handing back whenever policy or evidence is uncertain.", "allowed_actions": ["CREATE_AMS_WORK_NOTE_DRAFT", "CREATE_NEXT_STEPS_CHECKLIST", "ADD_INTERNAL_CASE_NOTE", "LINK_EVIDENCE_TO_CASE"], "execution_enabled": True, "handoff_on_uncertainty": True},
}
PROFILE_ALIASES = {"LOCAL_DRAUTONOMY": "LOCAL_DRAFT_AUTONOMY", "LOCAL_DRAFT_AUTONOMY": "LOCAL_DRAFT_AUTONOMY"}


class Stage3AutonomyError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next(db: Session, model: Any, field: Any, prefix: str) -> str:
    current = db.scalar(select(func.max(field)).where(field.like(f"{prefix}%")))
    try:
        number = int(str(current).rsplit("-", 1)[1]) + 1 if current else 1
    except (ValueError, IndexError):
        number = 1
    return f"{prefix}{number:04d}"


def _profile(code: str) -> tuple[str, dict[str, Any]]:
    canonical = PROFILE_ALIASES.get(code.upper(), code.upper())
    if canonical not in PROFILE_DEFINITIONS:
        raise Stage3AutonomyError("Unknown Stage 3 sandbox profile.", 400)
    return canonical, PROFILE_DEFINITIONS[canonical]


def _control(db: Session) -> Stage3AutonomyControl | None:
    return db.scalar(select(Stage3AutonomyControl).where(Stage3AutonomyControl.control_key == "GLOBAL"))


def _kill_switch(db: Session, settings: Settings) -> bool:
    control = _control(db)
    return bool(settings.autonomous_sandbox_kill_switch or (control and control.kill_switch_enabled))


def _event(db: Session, run: Stage3AutonomousRun, event_type: str, title: str, description: str, severity: str = "INFO", step: Stage3AutonomousStep | None = None, metadata: dict[str, Any] | None = None) -> None:
    db.add(Stage3AutonomousEvent(event_id=_next(db, Stage3AutonomousEvent, Stage3AutonomousEvent.event_id, "ST3-EVENT-"), run_id=run.id, step_id=step.id if step else None, event_type=event_type, event_title=title, event_description=description[:2000], severity=severity, metadata_json=metadata))
    # Event identifiers are human-readable sequences. Flush immediately so a
    # burst of audit events in one transaction cannot reuse the same number.
    db.flush()


def status(db: Session, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    kill = _kill_switch(db, settings)
    return {"mode": STAGE_MODE, "sandbox_enabled": bool(settings.autonomous_sandbox_enabled), "kill_switch_enabled": kill, "real_model_allowed": bool(settings.autonomous_sandbox_allow_real_model), "real_model_default_enabled": False, "require_dry_run_first": bool(settings.autonomous_sandbox_require_dry_run_first), "max_steps": settings.autonomous_sandbox_max_steps, "max_duration_seconds": settings.autonomous_sandbox_max_duration_seconds, "max_estimated_cost": settings.autonomous_sandbox_max_estimated_cost, "safe_to_execute": bool(settings.autonomous_sandbox_enabled) and not kill, "production_autonomous_remediation": False, "safety_notes": SAFETY, "reason": "Sandbox execution is disabled by default." if not settings.autonomous_sandbox_enabled else ("Kill switch is active." if kill else "Explicitly requested local sandbox execution may be evaluated.")}


def profiles(db: Session | None = None, settings: Settings | None = None) -> list[dict[str, Any]]:
    settings = settings or get_settings()
    items = [{"profile_code": code, **definition, "enabled_for_execution": bool(definition["execution_enabled"] and settings.autonomous_sandbox_enabled), "safety_notes": SAFETY} for code, definition in PROFILE_DEFINITIONS.items()]
    # Accept and display the original Prompt 30 spelling used by some demo
    # scripts while keeping LOCAL_DRAFT_AUTONOMY as the canonical code.
    draft = next(item for item in items if item["profile_code"] == "LOCAL_DRAFT_AUTONOMY")
    items.insert(2, {**draft, "profile_code": "LOCAL_DRAUTONOMY", "alias_for": "LOCAL_DRAFT_AUTONOMY"})
    return items


def _case(db: Session, case_id: str | None) -> AgentCase | None:
    if not case_id:
        return None
    try:
        parsed = UUID(case_id)
        row = db.get(AgentCase, parsed)
    except ValueError:
        row = db.scalar(select(AgentCase).where(AgentCase.case_id == case_id))
    if row is None:
        raise Stage3AutonomyError("Agent case not found.", 404)
    return row


def _run_dict(db: Session, run: Stage3AutonomousRun, children: bool = True) -> dict[str, Any]:
    steps = db.scalars(select(Stage3AutonomousStep).where(Stage3AutonomousStep.run_id == run.id).order_by(Stage3AutonomousStep.step_number)).all() if children else []
    events = db.scalars(select(Stage3AutonomousEvent).where(Stage3AutonomousEvent.run_id == run.id).order_by(Stage3AutonomousEvent.created_at, Stage3AutonomousEvent.id)).all() if children else []
    return {"id": run.id, "run_id": run.run_id, "case_id": run.case_id, "scenario_run_id": run.scenario_run_id, "session_id": run.session_id, "source_object_type": run.source_object_type, "source_object_id": run.source_object_id, "status": run.status, "mode": run.mode, "profile_code": run.profile_code, "dry_run_required": run.dry_run_required, "dry_run_completed": run.dry_run_completed, "real_model_requested": run.real_model_requested, "real_model_used": run.real_model_used, "provider_code": run.provider_code, "model_code": run.model_code, "max_steps": run.max_steps, "steps_completed": run.steps_completed, "max_duration_seconds": run.max_duration_seconds, "max_estimated_cost": run.max_estimated_cost, "estimated_total_cost": run.estimated_total_cost, "total_input_tokens": run.total_input_tokens, "total_completion_tokens": run.total_completion_tokens, "total_tokens": run.total_tokens, "started_at": run.started_at, "completed_at": run.completed_at, "stopped_at": run.stopped_at, "stop_reason": run.stop_reason, "created_by_role": run.created_by_role, "created_at": run.created_at, "updated_at": run.updated_at, "steps": [{"id": x.id, "step_id": x.step_id, "step_number": x.step_number, "status": x.status, "decision_type": x.decision_type, "decision_summary": x.decision_summary, "selected_action_code": x.selected_action_code, "proposal_id": x.proposal_id, "execution_id": x.execution_id, "guardrail_status": x.guardrail_status, "guardrail_reason": x.guardrail_reason, "input_tokens": x.input_tokens, "completion_tokens": x.completion_tokens, "total_tokens": x.total_tokens, "estimated_cost": x.estimated_cost, "started_at": x.started_at, "completed_at": x.completed_at, "error_message": x.error_message} for x in steps], "events": [{"id": x.id, "event_id": x.event_id, "event_type": x.event_type, "event_title": x.event_title, "event_description": x.event_description, "severity": x.severity, "metadata_json": x.metadata_json, "created_at": x.created_at} for x in events]}


def create_run(db: Session, request: Any, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    if not request.acknowledge_sandbox_only:
        raise Stage3AutonomyError("acknowledge_sandbox_only must be true for a Stage 3 run.", 400)
    profile_code, _ = _profile(request.profile_code)
    if request.max_steps > settings.autonomous_sandbox_max_steps:
        raise Stage3AutonomyError(f"max_steps cannot exceed {settings.autonomous_sandbox_max_steps}.", 400)
    if request.max_estimated_cost > settings.autonomous_sandbox_max_estimated_cost:
        raise Stage3AutonomyError(f"max_estimated_cost cannot exceed {settings.autonomous_sandbox_max_estimated_cost}.", 400)
    case = _case(db, request.case_id)
    session = db.scalar(select(AgentChatSession).where(AgentChatSession.case_id == case.id, AgentChatSession.status == "ACTIVE").order_by(AgentChatSession.updated_at.desc()).limit(1)) if case else None
    now = _now()
    run = Stage3AutonomousRun(run_id=_next(db, Stage3AutonomousRun, Stage3AutonomousRun.run_id, "ST3-RUN-"), case_id=case.id if case else None, scenario_run_id=UUID(request.scenario_run_id) if request.scenario_run_id else None, session_id=session.id if session else None, source_object_type=case.source_object_type if case else None, source_object_id=str(case.source_object_id) if case and case.source_object_id else None, status="CREATED", mode=STAGE_MODE, profile_code=profile_code, dry_run_required=settings.autonomous_sandbox_require_dry_run_first, real_model_requested=bool(request.use_real_model), provider_code=request.provider_code, model_code=request.model_code, max_steps=request.max_steps, max_duration_seconds=settings.autonomous_sandbox_max_duration_seconds, max_estimated_cost=request.max_estimated_cost, created_by_role=request.created_by_role, created_at=now, updated_at=now)
    db.add(run)
    db.flush()
    _event(db, run, "RUN_CREATED", "Stage 3 sandbox run created", "An explicit bounded local sandbox run was created; no action was executed.", metadata={"profile_code": profile_code, "safety_notes": SAFETY})
    db.commit()
    return _run_dict(db, db.get(Stage3AutonomousRun, run.id))


def _candidates(db: Session, run: Stage3AutonomousRun, definition: dict[str, Any]) -> list[AgentActionProposal]:
    if not run.case_id:
        return []
    proposals = db.scalars(select(AgentActionProposal).where(AgentActionProposal.case_id == run.case_id).order_by(AgentActionProposal.created_at, AgentActionProposal.id)).all()
    allowed = set(definition["allowed_actions"])
    return [proposal for proposal in proposals if (proposal.safe_action_code or proposal.action_type) in allowed and (proposal.safe_action_code or proposal.action_type) != "REVIEW_EVIDENCE"]


def dry_run(db: Session, run_id: str, requested_by_role: str, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    run = get_run(db, run_id)
    _, definition = _profile(run.profile_code)
    _event(db, run, "DRY_RUN_STARTED", "Stage 3 dry run started", "The sandbox is planning local safe actions without executing them.")
    existing = db.scalars(select(Stage3AutonomousStep).where(Stage3AutonomousStep.run_id == run.id)).all()
    if not existing:
        for number, proposal in enumerate(_candidates(db, run, definition)[:run.max_steps], start=1):
            db.add(Stage3AutonomousStep(step_id=_next(db, Stage3AutonomousStep, Stage3AutonomousStep.step_id, "ST3-STEP-"), run_id=run.id, step_number=number, status="SKIPPED_DRY_RUN", decision_type="DETERMINISTIC_SAFE_ACTION", decision_summary=f"Would evaluate {proposal.title} within the {run.profile_code} profile.", selected_action_code=proposal.safe_action_code or proposal.action_type, proposal_id=proposal.id, guardrail_status="PLANNED", guardrail_reason="No execution occurs during dry-run."))
            db.flush()
    run.dry_run_completed, run.status, run.updated_at = True, "DRY_RUN_COMPLETED", _now()
    _event(db, run, "DRY_RUN_COMPLETED", "Stage 3 dry run completed", "Planned actions are local and safe-catalog constrained; no execution occurred.", metadata={"requested_by_role": requested_by_role, "planned_step_count": len(existing) or len(_candidates(db, run, definition)[:run.max_steps]), "execution_performed": False, "safety_notes": SAFETY})
    db.commit()
    return {"run": _run_dict(db, db.get(Stage3AutonomousRun, run.id)), "planned_actions": [{"step_number": step.step_number, "action_code": step.selected_action_code, "proposal_id": step.proposal_id, "would_execute": False, "policy_check": "SAFE_CATALOG_AND_PROFILE"} for step in db.scalars(select(Stage3AutonomousStep).where(Stage3AutonomousStep.run_id == run.id).order_by(Stage3AutonomousStep.step_number)).all()], "guardrails": {"sandbox_enabled": settings.autonomous_sandbox_enabled, "kill_switch_enabled": _kill_switch(db, settings), "max_steps": run.max_steps, "max_duration_seconds": run.max_duration_seconds, "max_estimated_cost": run.max_estimated_cost}, "human_handback_conditions": ["kill switch", "policy mismatch", "budget or duration limit", "no safe proposal", "uncertain context"], "what_will_not_be_done": SAFETY}


def _run_row(db: Session, run_id: str) -> Stage3AutonomousRun:
    row = db.scalar(select(Stage3AutonomousRun).where(Stage3AutonomousRun.run_id == run_id))
    if row is None:
        raise Stage3AutonomyError("Stage 3 sandbox run not found.", 404)
    return row


get_run = _run_row


def start(db: Session, run_id: str, request: Any, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    run = get_run(db, run_id)
    if not request.acknowledge_autonomous_sandbox or not request.acknowledge_no_external_systems or not request.acknowledge_cost:
        raise Stage3AutonomyError("All autonomous sandbox, no-external-system, and cost acknowledgements are required.", 400)
    if _kill_switch(db, settings):
        run.status, run.stop_reason, run.updated_at = "KILLED_BY_SWITCH", "Global Stage 3 kill switch is active.", _now()
        _event(db, run, "KILL_SWITCH_TRIGGERED", "Sandbox start blocked by kill switch", run.stop_reason, "HIGH")
        db.commit()
        return _run_dict(db, db.get(Stage3AutonomousRun, run.id))
    if not settings.autonomous_sandbox_enabled:
        run.status, run.stop_reason, run.updated_at = "BLOCKED_BY_POLICY", "AUTONOMOUS_SANDBOX_ENABLED is false; no autonomous execution occurred.", _now()
        _event(db, run, "GUARDRAIL_BLOCKED", "Sandbox execution disabled", run.stop_reason, "WARN")
        db.commit()
        return _run_dict(db, db.get(Stage3AutonomousRun, run.id))
    if run.dry_run_required and not run.dry_run_completed:
        raise Stage3AutonomyError("Dry-run must be completed before execution.", 409)
    _, definition = _profile(run.profile_code)
    if not definition["execution_enabled"]:
        run.status, run.stop_reason = "BLOCKED_BY_POLICY", "The selected profile is dry-run only."
        _event(db, run, "GUARDRAIL_BLOCKED", "Dry-run-only profile blocked execution", run.stop_reason, "WARN")
        db.commit()
        return _run_dict(db, db.get(Stage3AutonomousRun, run.id))
    run.status, run.started_at, run.updated_at = "RUNNING", _now(), _now()
    _event(db, run, "AUTONOMY_STARTED", "Bounded sandbox execution started", "Only explicitly permitted safe local catalog actions will be evaluated.")
    db.flush()
    planned = db.scalars(select(Stage3AutonomousStep).where(Stage3AutonomousStep.run_id == run.id, Stage3AutonomousStep.status == "SKIPPED_DRY_RUN").order_by(Stage3AutonomousStep.step_number)).all()
    if not planned:
        run.status, run.stop_reason, run.completed_at = "NEEDS_HUMAN_REVIEW", "No safe local proposal is available for this case.", _now()
        _event(db, run, "HUMAN_HANDOFF", "Human review required", run.stop_reason, "WARN")
        run.updated_at = _now()
        db.commit()
        return _run_dict(db, db.get(Stage3AutonomousRun, run.id))
    for planned_step in planned[:run.max_steps]:
        if run.started_at and (_now() - run.started_at).total_seconds() > run.max_duration_seconds:
            run.status, run.stop_reason, run.completed_at = "NEEDS_HUMAN_REVIEW", "Maximum sandbox duration exceeded.", _now()
            _event(db, run, "GUARDRAIL_BLOCKED", "Sandbox duration limit reached", run.stop_reason, "WARN", planned_step)
            break
        if _kill_switch(db, settings):
            run.status, run.stop_reason = "KILLED_BY_SWITCH", "Kill switch activated during bounded execution."
            _event(db, run, "KILL_SWITCH_TRIGGERED", "Sandbox stopped by kill switch", run.stop_reason, "HIGH", planned_step)
            break
        # The dry-run row becomes the execution row. Reusing it preserves one
        # auditable step number and avoids duplicate step records.
        step = planned_step
        step.status, step.guardrail_status, step.guardrail_reason = "RUNNING", "PASSED", "Enabled sandbox, profile, catalog, dry-run, and kill-switch checks passed."
        step.started_at, step.updated_at = _now(), _now()
        db.flush()
        _event(db, run, "GUARDRAIL_PASSED", "Sandbox guardrails passed", "Action is in the configured safe catalog and allowed by the selected profile.", step=step)
        try:
            case = db.get(AgentCase, run.case_id) if run.case_id else None
            result = agent_action_service.execute_sandbox_action(db, case, step.selected_action_code, request.requested_by_role, f"stage3:{run.run_id}:{step.selected_action_code}") if case else None
            if result is None or result.get("execution") is None:
                raise agent_action_service.AgentActionError("No linked agent case is available for sandbox execution.", 409)
            execution = result["execution"]
            step.execution_id = UUID(str(execution["id"])) if execution.get("id") else None
            step.proposal_id = UUID(str(result["proposal"]["id"])) if result.get("proposal") else step.proposal_id
            step.status = "SUCCEEDED" if execution.get("status") == "SUCCEEDED" else "FAILED"
            step.completed_at, step.updated_at = _now(), _now()
            run.steps_completed += 1
            _event(db, run, "ACTION_EXECUTION_SUCCEEDED" if step.status == "SUCCEEDED" else "ACTION_EXECUTION_FAILED", "Sandbox action completed" if step.status == "SUCCEEDED" else "Sandbox action failed", execution.get("result_summary") or execution.get("error_message") or "Action handler returned no summary.", "INFO" if step.status == "SUCCEEDED" else "WARN", step)
        except agent_action_service.AgentActionError as error:
            step.status, step.error_message, step.guardrail_status, step.guardrail_reason, step.completed_at = "NEEDS_HUMAN_REVIEW", error.message, "BLOCKED", error.message, _now()
            run.status, run.stop_reason = "NEEDS_HUMAN_REVIEW", error.message
            _event(db, run, "HUMAN_HANDOFF", "Human review required", error.message, "WARN", step)
            break
    else:
        run.status = "COMPLETED"
        run.completed_at = _now()
        _event(db, run, "RUN_COMPLETED", "Sandbox run completed", "The bounded local sandbox completed without external or prohibited execution.")
    if run.status == "RUNNING":
        run.status, run.completed_at = "COMPLETED", _now()
        _event(db, run, "RUN_COMPLETED", "Sandbox run completed", "The bounded step limit was reached.")
    run.updated_at = _now()
    db.commit()
    return _run_dict(db, db.get(Stage3AutonomousRun, run.id))


def pause(db: Session, run_id: str, reason: str) -> dict[str, Any]:
    run = get_run(db, run_id)
    run.status, run.stop_reason, run.updated_at = "PAUSED", reason, _now()
    _event(db, run, "RUN_STOPPED", "Sandbox paused", reason)
    db.commit()
    return _run_dict(db, db.get(Stage3AutonomousRun, run.id))


def stop(db: Session, run_id: str, reason: str) -> dict[str, Any]:
    run = get_run(db, run_id)
    run.status, run.stop_reason, run.stopped_at, run.updated_at = "STOPPED", reason, _now(), _now()
    _event(db, run, "RUN_STOPPED", "Sandbox stopped", reason)
    db.commit()
    return _run_dict(db, db.get(Stage3AutonomousRun, run.id))


def kill_switch(db: Session, enabled: bool, requested_by_role: str, reason: str) -> dict[str, Any]:
    row = _control(db)
    if row is None:
        row = Stage3AutonomyControl(control_key="GLOBAL")
        db.add(row)
    row.kill_switch_enabled, row.requested_by_role, row.reason, row.updated_at = enabled, requested_by_role, reason, _now()
    db.commit()
    return {"kill_switch_enabled": enabled, "requested_by_role": requested_by_role, "reason": reason, "safety_notes": SAFETY}


def list_runs(db: Session, case_id: str | None = None) -> list[dict[str, Any]]:
    statement = select(Stage3AutonomousRun).order_by(Stage3AutonomousRun.created_at.desc()).limit(100)
    if case_id:
        case = _case(db, case_id)
        statement = statement.where(Stage3AutonomousRun.case_id == case.id) if case else statement.where(False)
    return [_run_dict(db, row, False) for row in db.scalars(statement).all()]


def summary(db: Session, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    rows = db.scalars(select(Stage3AutonomousRun)).all()
    counts = {status_code: sum(1 for row in rows if row.status == status_code) for status_code in ("CREATED", "DRY_RUN_COMPLETED", "RUNNING", "COMPLETED", "STOPPED", "NEEDS_HUMAN_REVIEW", "BLOCKED_BY_POLICY", "KILLED_BY_SWITCH")}
    return {"mode": STAGE_MODE, "sandbox_enabled": settings.autonomous_sandbox_enabled, "kill_switch_enabled": _kill_switch(db, settings), "run_count": len(rows), "completed_runs": counts["COMPLETED"], "blocked_runs": counts["BLOCKED_BY_POLICY"] + counts["KILLED_BY_SWITCH"], "needs_human_review": counts["NEEDS_HUMAN_REVIEW"], "total_estimated_cost": sum(row.estimated_total_cost or 0 for row in rows), "total_tokens": sum(row.total_tokens or 0 for row in rows), "status_counts": counts, "production_autonomous_remediation": False, "real_model_default_enabled": False, "safety_notes": SAFETY}
