"""Provider-neutral governed invocation gateway with a deterministic mock."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from math import ceil
from time import monotonic
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_config import AiGuardrailEvent, AiInvocationLog, AiModelConfig, AiPromptTemplate, AiProvider, AiSafetyPolicy, AiUsageDaily
from app.schemas.ai_config import InvocationResponse
from app.services import ai_config_service, ai_safety_service


class AiGatewayError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


TASK_TEMPLATE_DEFAULTS = {
    "GENERAL_TEST": "TPL-GENERAL-TEST",
    "COPILOT_CONTEXT_SUMMARY": "TPL-COPILOT-CONTEXT-SUMMARY",
    "COPILOT_RECOMMENDATION": "TPL-COPILOT-RECOMMENDATION",
    "WORK_NOTE_DRAFT": "TPL-WORK-NOTE-DRAFT",
    "CUSTOMER_UPDATE_DRAFT": "TPL-CUSTOMER-UPDATE-DRAFT",
    "INVESTIGATION_CHECKLIST": "TPL-INVESTIGATION-CHECKLIST",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_number(db: Session, field: Any, prefix: str) -> str:
    current = db.scalar(select(func.max(field)).where(field.like(f"{prefix}%")))
    sequence = 1
    if current:
        try: sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError): sequence = 1
    return f"{prefix}{sequence:04d}"


def _redact(text: str) -> str:
    text = re.sub(r"(?i)(api[_-]?key\s*[=:]\s*)[^\s,}]+", r"\1[REDACTED]", text)
    text = re.sub(r"(?i)(password\s*[=:]\s*)[^\s,}]+", r"\1[REDACTED]", text)
    text = re.sub(r"\bsk-[A-Za-z0-9_-]+", "sk-[REDACTED]", text)
    return text


def _render(template: AiPromptTemplate, payload: dict) -> str:
    body = json.dumps(payload, sort_keys=True, default=str)
    return _redact(f"SYSTEM:\n{template.system_template}\nUSER:\n{template.user_template}\nINPUT:\n{body}")


def _mock_response(task_type: str, payload: dict) -> tuple[str, dict]:
    task_type = task_type.upper()
    message = str(payload.get("message") or payload.get("text") or "the supplied support context")
    if task_type == "GENERAL_TEST":
        text = "Mock governed response generated successfully."
    elif task_type == "COPILOT_CONTEXT_SUMMARY":
        text = f"Mock governed context summary: {message}. Review source evidence before taking manual action."
    elif task_type == "WORK_NOTE_DRAFT":
        text = f"Support investigation update: Evidence was reviewed for {message}. Current hypothesis remains subject to human validation; next action is to review the governed investigation checklist."
    elif task_type == "CUSTOMER_UPDATE_DRAFT":
        text = f"We acknowledge the issue associated with {message}. Support is reviewing the available evidence and will provide an update after human validation."
    elif task_type == "INVESTIGATION_CHECKLIST":
        text = "- Review source status and business impact.\n- Validate related evidence.\n- Confirm the next manual support action."
    else:
        text = f"Mock governed response for {task_type}: {message}."
    return text, {"provider": "MOCK_GOVERNED", "task_type": task_type, "deterministic": True, "response": text}


def _usage(db: Session, provider: AiProvider, model: AiModelConfig, task_type: str, status: str, input_tokens: int, output_tokens: int, cost: float) -> None:
    today = _now().date()
    row = db.scalar(select(AiUsageDaily).where(AiUsageDaily.usage_date == today, AiUsageDaily.provider_code == provider.provider_code, AiUsageDaily.model_code == model.model_code, AiUsageDaily.task_type == task_type))
    if row is None:
        row = AiUsageDaily(usage_date=today, provider_code=provider.provider_code, model_code=model.model_code, task_type=task_type, invocation_count=0, blocked_count=0, input_tokens_estimated=0, output_tokens_estimated=0, total_tokens_estimated=0, cost_estimated=0)
        db.add(row)
    row.invocation_count += 1
    row.blocked_count += 1 if status == "BLOCKED" else 0
    row.input_tokens_estimated += input_tokens
    row.output_tokens_estimated += output_tokens
    row.total_tokens_estimated += input_tokens + output_tokens
    row.cost_estimated += cost
    row.updated_at = _now()


def invoke(db: Session, *, task_type: str, input_payload: dict, request_source: str, request_source_id: UUID | None = None, template_code: str | None = None, model_code: str | None = None, created_by: str = "system") -> InvocationResponse:
    task_type = task_type.upper()
    model = db.scalar(select(AiModelConfig).where(AiModelConfig.model_code == model_code)) if model_code else db.scalar(select(AiModelConfig).where(AiModelConfig.enabled.is_(True), AiModelConfig.is_default.is_(True)))
    if model is None and not model_code: model = db.scalar(select(AiModelConfig).where(AiModelConfig.enabled.is_(True)).order_by(AiModelConfig.model_code))
    if model is None: raise AiGatewayError("AI model configuration not found.", 404)
    provider = db.get(AiProvider, model.provider_id)
    if provider is None: raise AiGatewayError("AI provider configuration not found.", 404)
    if not model.enabled: raise AiGatewayError("Requested AI model is disabled.")
    if not provider.enabled: raise AiGatewayError("Requested AI provider is disabled.")
    if not provider.is_mock: raise AiGatewayError("Only the deterministic mock provider is executable in this phase.")
    template = db.scalar(select(AiPromptTemplate).where(AiPromptTemplate.template_code == (template_code or TASK_TEMPLATE_DEFAULTS.get(task_type, "TPL-GENERAL-TEST")), AiPromptTemplate.enabled.is_(True)).order_by(AiPromptTemplate.template_version.desc()))
    if template is None: raise AiGatewayError("Enabled prompt template not found.", 404)
    policy = db.scalar(select(AiSafetyPolicy).where(AiSafetyPolicy.enabled.is_(True)).order_by(AiSafetyPolicy.policy_code))
    rendered = _render(template, input_payload)
    evaluation = ai_safety_service.evaluate(db, f"{json.dumps(input_payload, sort_keys=True, default=str)}\n{rendered}", policy)
    now = _now(); started = monotonic()
    safe_prompt = _redact(rendered)
    input_tokens = max(1, ceil(len(safe_prompt) / 4))
    output_text = None; output_json = None; output_tokens = 0; status = "SUCCESS"; blocked_reason = None
    if evaluation.decision == "BLOCK":
        status = "BLOCKED"
        blocked_reason = "; ".join(rule.rule_code for rule in evaluation.matched_rules)
    else:
        output_text, output_json = _mock_response(task_type, input_payload)
        output_tokens = max(1, ceil(len(output_text) / 4))
    cost = (input_tokens / 1000) * model.cost_per_1k_input_tokens + (output_tokens / 1000) * model.cost_per_1k_output_tokens
    row = AiInvocationLog(invocation_number=_next_number(db, AiInvocationLog.invocation_number, f"AI-INV-{now:%Y%m%d}-"), provider_id=provider.id, model_config_id=model.id, template_id=template.id, policy_id=policy.id if policy else None, request_source=request_source, request_source_id=request_source_id, task_type=task_type, status=status, input_summary=_redact(json.dumps(input_payload, sort_keys=True, default=str))[:2000], prompt_rendered=safe_prompt[:10000], response_text=output_text, response_json=output_json, safety_status="BLOCKED" if status == "BLOCKED" else evaluation.safety_status, blocked_reason=blocked_reason, latency_ms=max(0, int((monotonic() - started) * 1000)), input_tokens_estimated=input_tokens, output_tokens_estimated=output_tokens, total_tokens_estimated=input_tokens + output_tokens, cost_estimated=cost, created_by=created_by, created_at=now, updated_at=now)
    db.add(row); db.flush()
    if evaluation.matched_rules:
        for rule in evaluation.matched_rules:
            db.add(AiGuardrailEvent(invocation_id=row.id, policy_id=policy.id if policy else None, rule_id=rule.id, event_type="RULE_BLOCKED" if status == "BLOCKED" else "RULE_WARNED", severity=rule.severity, message=f"Rule {rule.rule_code} {'blocked' if status == 'BLOCKED' else 'warned'} the governed invocation.", matched_text_summary="Configured safety pattern matched; raw text omitted.", created_at=_now()))
    elif policy:
        db.add(AiGuardrailEvent(invocation_id=row.id, policy_id=policy.id, rule_id=None, event_type="POLICY_PASSED", severity="INFO", message="Governed safety policy passed the invocation.", matched_text_summary=None, created_at=_now()))
    _usage(db, provider, model, task_type, status, input_tokens, output_tokens, cost)
    db.commit()
    return ai_config_service.get_invocation(db, row.id)
