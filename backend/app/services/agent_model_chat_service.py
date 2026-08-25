"""Governed, read-only Stage 1 model chat orchestration.

This module is intentionally a thin policy boundary around the existing AI
provider gateway. It packages only bounded EOS records and never exposes tools
or an execution capability to the model.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, time, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.models.ai_config import AiInvocationLog, AiModelConfig, AiProvider, AiUsageDaily
from app.models.agent_chat import AgentChatSession
from app.schemas.ai_config import RealModelRequest
from app.services import ai_config_service, ai_provider_gateway, agent_investigation_service

STAGE_1 = "STAGE_1_READ_ONLY"
DEFAULT_PROVIDER = "OPENAI_RESPONSES"
ALLOWED_TASK_DEFAULTS = ("AGENT_STAGE_1_CHAT", "AGENT_INVESTIGATION_QA", "AGENT_EVIDENCE_SUMMARY")

SYSTEM_INSTRUCTION = (
    "You are an enterprise AMS support agent operating in Stage 1 read-only mode. "
    "Use only the provided context. Do not claim to have executed actions. Do not instruct anyone to run shell commands. "
    "Do not request passwords, tokens, API keys, or secrets. Do not send customer communications. Do not post to ServiceNow. "
    "Do not resolve or close production objects. You may recommend human-reviewed next steps. "
    "If evidence is insufficient, say what evidence is missing. Cite the context items used. Keep the answer concise and structured."
)

_PRECHECK_PATTERNS: tuple[tuple[str, str], ...] = (
    ("SHELL_EXECUTION_REQUEST", r"\b(shell|bash|zsh|powershell|run\s+command|execute\s+command|rm\s+-rf|curl\s+https?)\b"),
    ("ARBITRARY_SQL_REQUEST", r"\b(select|insert|delete|drop|alter|truncate)\b.{0,40}\b(sql|database|table|production)\b"),
    ("SECRET_REQUEST", r"\b(api[_ -]?key|password|secret|token|credential)\b.{0,40}\b(reveal|share|provide|show|send|give)\b"),
    ("PROMPT_INJECTION", r"(ignore\s+(all\s+)?previous|reveal\s+(the\s+)?system\s+prompt|hidden\s+instructions|bypass\s+(the\s+)?rules)"),
    ("EXTERNAL_ACTION_REQUEST", r"(servicenow|send\s+(an?\s+)?(email|message|customer\s+update)|post\s+externally|call\s+external\s+api)"),
    ("AUTONOMOUS_REMEDIATION_REQUEST", r"(auto(?:nomous|matically)?\s+(remediat|resolve|close)|bypass\s+approval|without\s+human\s+approval)"),
)
_POSTCHECK_PATTERNS: tuple[tuple[str, str], ...] = (
    ("CLAIMED_EXECUTION", r"(i\s+(have\s+)?executed|action\s+(was|has\s+been)\s+executed|i\s+restarted|i\s+deleted|i\s+closed\s+the\s+ticket)"),
    ("UNSAFE_COMMAND_INSTRUCTION", r"(^|\n)\s*(sudo\s+|rm\s+-rf|curl\s+https?|bash\s+-c|kubectl\s+(delete|exec))"),
    ("ARBITRARY_SQL_OUTPUT", r"\b(drop\s+table|delete\s+from|truncate\s+table|update\s+\w+\s+set)\b"),
    ("SECRET_REQUEST_OUTPUT", r"(send\s+me\s+your\s+(api\s+key|password|token)|provide\s+your\s+credentials)"),
    ("EXTERNAL_SEND_CLAIM", r"(posted\s+to\s+servicenow|sent\s+(the\s+)?customer|emailed\s+the\s+customer|resolved\s+the\s+production\s+alert)"),
    ("APPROVAL_BYPASS_OUTPUT", r"(bypass\s+approval|no\s+approval\s+is\s+needed|autonomous\s+remediation)"),
)


@dataclass
class ModelChatResult:
    answer: str
    generation_mode: str
    safety_status: str
    fallback_used: bool
    invocation_id: UUID | None
    invocation_number: str | None
    metadata: dict[str, Any]


def _settings(settings: Settings | None = None) -> Settings:
    return settings or get_settings()


def resolve_session_id(db: Session, value: str | UUID) -> UUID:
    """Accept both the database UUID used by the UI and AGENT-CHAT-NNNN."""
    if isinstance(value, UUID):
        session = db.get(AgentChatSession, value)
    else:
        try:
            session = db.get(AgentChatSession, UUID(value))
        except ValueError:
            session = db.scalar(select(AgentChatSession).where(AgentChatSession.session_id == value))
    if session is None:
        raise ValueError("Agent chat session not found.")
    return session.id


def _json_value(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    return value


def _item(item_id: str, item_type: str, title: str, summary: str, *, source_id: Any = None, source_url: str | None = None, timestamp: Any = None, confidence: float | None = None) -> dict[str, Any]:
    return {"context_item_id": item_id, "context_item_type": item_type, "title": str(title)[:200], "summary": str(summary)[:1500], "source_id": str(source_id) if source_id else None, "source_url": source_url, "timestamp": _json_value(timestamp), "confidence": confidence}


def build_context(db: Session, session_id: UUID, message_text: str, settings: Settings | None = None) -> dict[str, Any]:
    """Build a bounded, secret-free context package without invoking a model."""
    settings = _settings(settings)
    session = db.get(AgentChatSession, session_id)
    if session is None:
        raise ValueError("Agent chat session not found.")
    workspace = agent_investigation_service.get_workspace(db, session.case_id)
    case = workspace["case"]
    items: list[dict[str, Any]] = []
    items.append(_item(f"case:{case['case_id']}", "CASE", case["title"], case["description"], source_id=case["id"], timestamp=case["updated_at"], confidence=1.0))
    source = workspace.get("source") or {}
    if source.get("type") or source.get("display"):
        items.append(_item(f"source:{source.get('id') or source.get('type')}", "SOURCE_OBJECT", source.get("display") or source.get("type"), source.get("summary") or "Linked investigation source.", source_id=source.get("id"), source_url=source.get("url"), confidence=1.0))
    for key, value in (workspace.get("linked_objects") or {}).items():
        if value:
            display = value.get("ticket_number") or value.get("event_id") or value.get("run_number") or value.get("report_number") or value.get("case_number") or value.get("exception_number") or key
            summary = " | ".join(f"{field}: {value[field]}" for field in ("status", "severity", "priority", "short_description", "condition_summary", "failure_message", "probable_cause", "suspected_root_cause", "business_impact") if value.get(field))
            items.append(_item(f"linked:{key}:{value.get('id')}", {"ams_ticket": "AMS_TICKET", "observability_alert": "ALERT", "batch_run": "BATCH_RUN", "user_report": "USER_REPORT", "diagnostic_case": "DIAGNOSTIC_CASE", "monitoring_triage": "MONITORING_TRIAGE", "operations_exception": "OPERATIONS_EXCEPTION"}.get(key, "SOURCE_OBJECT"), display, summary or str(value.get("description") or "Linked support object."), source_id=value.get("id"), source_url=value.get("source_url"), confidence=0.95))
    for evidence in (workspace.get("evidence") or []):
        items.append(_item(f"evidence:{evidence.get('evidence_id')}", "EVIDENCE", evidence.get("title"), evidence.get("summary"), source_id=evidence.get("source_id"), source_url=evidence.get("source_url"), timestamp=evidence.get("created_at"), confidence=evidence.get("relevance_score")))
    for knowledge in (workspace.get("knowledge") or []):
        items.append(_item(f"knowledge:{knowledge.get('id')}", "KNOWLEDGE_CHUNK", knowledge.get("title"), knowledge.get("summary"), source_id=knowledge.get("id"), source_url=knowledge.get("source_url"), confidence=knowledge.get("score")))
    for known in (workspace.get("known_errors") or []):
        items.append(_item(f"known-error:{known.get('id')}", "KNOWN_ERROR", known.get("error_code") or known.get("title"), known.get("summary") or known.get("likely_cause"), source_id=known.get("id"), confidence=0.9))
    for proposal in (workspace.get("action_proposals") or []):
        items.append(_item(f"proposal:{proposal.get('proposal_id')}", "ACTION_PROPOSAL", proposal.get("title"), f"{proposal.get('description')} Approval: {proposal.get('approval_status')}. Execution: {proposal.get('execution_status')}.", source_id=proposal.get("id"), confidence=1.0))
    for execution in (workspace.get("executions") or []):
        items.append(_item(f"execution:{execution.get('execution_id')}", "ACTION_EXECUTION", execution.get("safe_action_code"), f"Status: {execution.get('status')}. Result: {execution.get('result_summary') or execution.get('error_message') or 'No result summary.'}", source_id=execution.get("id"), timestamp=execution.get("completed_at"), confidence=1.0))
    for message in (workspace.get("messages") or [])[-8:]:
        items.append(_item(f"chat:{message.get('message_id')}", "CHAT_HISTORY", message.get("sender_type"), message.get("message_text"), source_id=message.get("id"), timestamp=message.get("created_at"), confidence=1.0))
    items = items[: max(1, settings.real_model_max_context_items)]
    package = {"case_id": case["case_id"], "stage_mode": STAGE_1, "question": message_text[: settings.real_model_max_input_chars], "context_items": items, "safety_state": {"stage_1_read_only": True, "actions_executed": workspace.get("counts", {}).get("actions_executed", 0), "autonomous_remediation_enabled": False}, "bounded": True}
    return _json_value(package)


def _find_match(text: str, patterns: tuple[tuple[str, str], ...]) -> str | None:
    lowered = text.lower()
    for code, pattern in patterns:
        if re.search(pattern, lowered, re.DOTALL):
            return code
    return None


def safety_precheck(text: str) -> str | None:
    return _find_match(text, _PRECHECK_PATTERNS)


def safety_postcheck(text: str) -> str | None:
    return _find_match(text, _POSTCHECK_PATTERNS)


def _allowed_tasks(settings: Settings) -> list[str]:
    configured = [item.strip().upper() for item in settings.real_model_allowed_task_types.split(",") if item.strip()]
    return configured or list(ALLOWED_TASK_DEFAULTS)


def resolve_model_code(db: Session, model_code: str | None, settings: Settings) -> str:
    requested = (model_code or "").strip()
    if requested and db.scalar(select(AiModelConfig).where(AiModelConfig.model_code == requested)):
        return requested
    if requested and db.scalar(select(AiModelConfig).where(AiModelConfig.model_name == requested)):
        return db.scalar(select(AiModelConfig).where(AiModelConfig.model_name == requested)).model_code
    if settings.openai_default_model:
        row = db.scalar(select(AiModelConfig).where(AiModelConfig.model_code == settings.openai_default_model)) or db.scalar(select(AiModelConfig).where(AiModelConfig.model_name == settings.openai_default_model))
        if row:
            return row.model_code
    row = db.scalar(select(AiModelConfig).join(AiProvider).where(AiProvider.provider_code == DEFAULT_PROVIDER).order_by(AiModelConfig.is_default.desc(), AiModelConfig.model_code))
    return row.model_code if row else (requested or "OPENAI_GPT_5_4_MINI")


def status(db: Session, settings: Settings | None = None) -> dict[str, Any]:
    settings = _settings(settings)
    model_code = resolve_model_code(db, None, settings)
    gateway_status = ai_provider_gateway.real_model_status(db, provider_code=DEFAULT_PROVIDER, model_code=model_code, settings=settings)
    today = datetime.now(timezone.utc).date()
    invocations = int(db.scalar(select(func.count(AiInvocationLog.id)).where(AiInvocationLog.created_at >= datetime.combine(today, time.min, tzinfo=timezone.utc), AiInvocationLog.request_source.in_(("AGENT_CHAT", "AGENT_MODEL_CHAT")))) or 0)
    cost = float(db.scalar(select(func.coalesce(func.sum(AiInvocationLog.cost_estimated), 0.0)).where(AiInvocationLog.created_at >= datetime.combine(today, time.min, tzinfo=timezone.utc), AiInvocationLog.request_source.in_(("AGENT_CHAT", "AGENT_MODEL_CHAT")))) or 0.0)
    reason = gateway_status.reason
    safe = gateway_status.safe_to_invoke and bool(settings.real_model_enabled)
    if not settings.real_model_enabled:
        reason = "REAL_MODEL_ENABLED is false"
    return {"real_model_enabled": settings.real_model_enabled, "provider_code": gateway_status.provider_code, "model_code": gateway_status.model_code, "default_model": gateway_status.default_model, "provider_configured": gateway_status.provider_configured, "model_configured": gateway_status.model_configured, "api_key_present": gateway_status.api_key_present, "provider_enabled": gateway_status.provider_enabled, "model_enabled": gateway_status.model_enabled, "safe_to_invoke": safe, "reason": reason, "allowed_task_types": _allowed_tasks(settings), "max_context_items": settings.real_model_max_context_items, "max_input_chars": settings.real_model_max_input_chars, "daily_usage": {"invocations": invocations, "estimated_cost": cost, "max_invocations": settings.real_model_max_daily_invocations, "max_estimated_cost": settings.real_model_max_daily_estimated_cost, "cost_tracking_status": "UNKNOWN_PRICING" if cost == 0 else "ESTIMATED"}, "stage_mode": STAGE_1}


def validate(db: Session, session_id: UUID, message_text: str, *, task_type: str, use_real_model: bool, context: dict[str, Any] | None = None, settings: Settings | None = None) -> list[str]:
    settings = _settings(settings)
    issues: list[str] = []
    normalized_task = task_type.upper()
    if normalized_task not in _allowed_tasks(settings): issues.append(f"Task type {normalized_task} is not allowed.")
    if len(message_text) > settings.real_model_max_input_chars: issues.append("Input exceeds the configured character guardrail.")
    package = context or build_context(db, session_id, message_text, settings)
    if len(package.get("context_items", [])) > settings.real_model_max_context_items: issues.append("Context exceeds the configured item guardrail.")
    if safety_precheck(message_text): issues.append("Input safety pre-check blocked the request.")
    if settings.real_model_stage1_only and package.get("stage_mode") != STAGE_1: issues.append("Only Stage 1 read-only cases are eligible.")
    if use_real_model:
        usage = status(db, settings)["daily_usage"]
        if usage["invocations"] >= settings.real_model_max_daily_invocations: issues.append("Daily real-model invocation limit reached.")
        if usage["estimated_cost"] >= settings.real_model_max_daily_estimated_cost: issues.append("Daily estimated cost limit reached.")
    return issues


def _parse_output(text: str, context: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    metadata: dict[str, Any] = {"evidence_used": [], "knowledge_used": [], "recommended_next_steps": [], "human_review_required": True, "actions_executed": 0, "stage_mode": STAGE_1, "limitations": ["Read-only guidance; human review is required."]}
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            answer = str(parsed.get("answer") or parsed.get("response") or text)
            metadata.update({key: parsed[key] for key in metadata if key in parsed})
            return answer, metadata
    except (TypeError, json.JSONDecodeError):
        pass
    return text, metadata


def answer(db: Session, session_id: UUID, message_text: str, *, task_type: str = "AGENT_STAGE_1_CHAT", provider_code: str | None = None, model_code: str | None = None, use_real_model: bool = False, dry_run: bool = False, fallback_text: str, created_by: str = "SERVICE_ENGINEER", settings: Settings | None = None) -> ModelChatResult:
    settings = _settings(settings)
    context = build_context(db, session_id, message_text, settings)
    issues = validate(db, session_id, message_text, task_type=task_type, use_real_model=use_real_model, context=context, settings=settings)
    common = {"context_package": context, "evidence_used": [item for item in context["context_items"] if item["context_item_type"] in ("EVIDENCE", "AMS_TICKET", "ALERT", "BATCH_RUN", "USER_REPORT", "DIAGNOSTIC_CASE")], "knowledge_used": [item for item in context["context_items"] if item["context_item_type"] in ("KNOWLEDGE_CHUNK", "KNOWN_ERROR")], "human_review_required": True, "actions_executed": 0, "stage_mode": STAGE_1}
    if not use_real_model:
        return ModelChatResult(fallback_text, "DETERMINISTIC_AGENT", "SAFE", False, None, None, {**common, "fallback_reason": "Real model was not requested."})
    if issues:
        # Persist an audit record through the gateway, explicitly forbidding
        # provider execution. This keeps blocked attempts observable without
        # allowing a pre-check failure to reach the external adapter.
        audit_request = RealModelRequest(provider_code=provider_code or DEFAULT_PROVIDER, model_code=resolve_model_code(db, model_code, settings), task_type=task_type.upper(), request_source="AGENT_MODEL_CHAT", request_source_id=session_id, input_text=message_text, system_instruction=SYSTEM_INSTRUCTION, context_items=context["context_items"], allow_real_model=False, metadata={"template_code": "TPL-AGENT-STAGE-1-CHAT", "guardrail_precheck": True}, created_by=created_by)
        audit = ai_provider_gateway.invoke_real_model(db, audit_request, settings)
        return ModelChatResult(fallback_text, "FALLBACK_DETERMINISTIC", "BLOCKED" if any("safety" in issue.lower() for issue in issues) else "NOT_INVOKED", True, audit.invocation_id, audit.invocation_number, {**common, "fallback_reason": "; ".join(issues), "guardrail_blocked": True})
    selected_model = resolve_model_code(db, model_code, settings)
    request = RealModelRequest(provider_code=provider_code or DEFAULT_PROVIDER, model_code=selected_model, task_type=task_type.upper(), request_source="AGENT_MODEL_CHAT", request_source_id=session_id, input_text=message_text, system_instruction=SYSTEM_INSTRUCTION, context_items=context["context_items"], allow_real_model=True, dry_run=dry_run, metadata={"template_code": "TPL-AGENT-STAGE-1-CHAT", "context_package": context, "case_stage_mode": STAGE_1}, created_by=created_by)
    result = ai_provider_gateway.invoke_real_model(db, request, settings)
    output = result.output_text or fallback_text
    parsed_answer, parsed_metadata = _parse_output(output, context)
    unsafe = safety_postcheck(output) or safety_postcheck(parsed_answer)
    if unsafe:
        return ModelChatResult(fallback_text, "FALLBACK_DETERMINISTIC", "BLOCKED", True, result.invocation_id, result.invocation_number, {**common, **parsed_metadata, "fallback_reason": f"Output safety post-check blocked {unsafe}.", "unsafe_output_blocked": True})
    generation_mode = result.generation_mode if result.status == "SUCCESS" and not dry_run else ("REAL_MODEL_DRY_RUN" if dry_run else "FALLBACK_DETERMINISTIC")
    return ModelChatResult(parsed_answer if result.status == "SUCCESS" and not dry_run else fallback_text, generation_mode, result.safety_status, bool(result.fallback_used or dry_run), result.invocation_id, result.invocation_number, {**common, **parsed_metadata, "fallback_reason": result.error_message if result.fallback_used else None, "provider_code": result.provider_code, "model_code": result.model_code, "real_model_status": result.status, "usage": result.usage, "limitations": ["Stage 1 read-only; no actions were executed."]})


def invocation_list(db: Session) -> list[Any]:
    return ai_config_service.list_invocations(db, request_source="AGENT_MODEL_CHAT")


def invocation_detail(db: Session, invocation_id: UUID) -> Any:
    return ai_config_service.get_invocation(db, invocation_id)
