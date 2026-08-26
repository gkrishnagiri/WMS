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
from app.core.config import Settings, get_settings
from app.schemas.ai_config import InvocationResponse, RealModelInvocationResponse, RealModelRequest, RealModelStatus
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
    "AGENT_STAGE_1_GUIDANCE": "TPL-AGENT-STAGE-1-GUIDANCE",
    "AGENT_KNOWLEDGE_SUMMARY": "TPL-AGENT-KNOWLEDGE-SUMMARY",
    "AGENT_EVIDENCE_SUMMARY": "TPL-AGENT-EVIDENCE-SUMMARY",
    "AGENT_STAGE_1_CHAT": "TPL-AGENT-STAGE-1-CHAT",
    "AGENT_INVESTIGATION_QA": "TPL-AGENT-INVESTIGATION-QA",
    "AGENT_KNOWLEDGE_GROUNDED_ANSWER": "TPL-AGENT-KNOWLEDGE-GROUNDED-ANSWER",
    "MODEL_SMOKE_TEST": "TPL-MODEL-SMOKE-TEST",
    "CUSTOMER_FACING_ISSUE_GUIDANCE": "TPL-CUSTOMER-FACING-ISSUE-GUIDANCE",
    "SERVICE_ENGINEER_INVESTIGATION_GUIDANCE": "TPL-SERVICE-ENGINEER-INVESTIGATION-GUIDANCE",
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


def _real_model_code(settings: Settings) -> str:
    """Translate the configured external model name to the catalog code."""
    return settings.openai_default_model or "OPENAI_GPT_5_4_MINI"


def _resolve_real_configuration(db: Session, request: RealModelRequest) -> tuple[AiProvider | None, AiModelConfig | None, AiPromptTemplate | None, AiSafetyPolicy | None]:
    provider = db.scalar(select(AiProvider).where(AiProvider.provider_code == request.provider_code))
    model = db.scalar(select(AiModelConfig).where(AiModelConfig.model_code == request.model_code))
    if model is None:
        model = db.scalar(select(AiModelConfig).where(AiModelConfig.model_name == request.model_code))
    template = db.scalar(
        select(AiPromptTemplate).where(
            AiPromptTemplate.template_code == (request.metadata.get("template_code") or TASK_TEMPLATE_DEFAULTS.get(request.task_type.upper(), "TPL-AGENT-STAGE-1-GUIDANCE")),
            AiPromptTemplate.enabled.is_(True),
        ).order_by(AiPromptTemplate.template_version.desc())
    )
    policy = db.scalar(select(AiSafetyPolicy).where(AiSafetyPolicy.enabled.is_(True)).order_by(AiSafetyPolicy.policy_code))
    return provider, model, template, policy


def real_model_status(db: Session, *, provider_code: str = "OPENAI_RESPONSES", model_code: str | None = None, settings: Settings | None = None) -> RealModelStatus:
    settings = settings or get_settings()
    selected_model_code = model_code or _real_model_code(settings)
    provider = db.scalar(select(AiProvider).where(AiProvider.provider_code == provider_code))
    model = db.scalar(select(AiModelConfig).where(AiModelConfig.model_code == selected_model_code))
    if model is None:
        model = db.scalar(select(AiModelConfig).where(AiModelConfig.model_name == selected_model_code))
    if model is not None:
        selected_model_code = model.model_code
    provider_configured = provider is not None
    model_configured = model is not None and (provider is None or model.provider_id == provider.id)
    provider_enabled = bool(provider and provider.enabled)
    model_enabled = bool(model and model.enabled)
    api_key_present = bool((settings.openai_api_key or "").strip())
    reasons: list[str] = []
    if not settings.real_model_enabled: reasons.append("REAL_MODEL_ENABLED is false")
    if not provider_configured: reasons.append("provider configuration is missing")
    elif not provider_enabled: reasons.append("provider is disabled")
    if not model_configured: reasons.append("model configuration is missing or belongs to another provider")
    elif not model_enabled: reasons.append("model is disabled")
    if not api_key_present: reasons.append("OPENAI_API_KEY is not present")
    safe = not reasons and not provider.is_mock and provider.provider_type == "REAL_MODEL"
    if not safe and provider_configured and provider.is_mock: reasons.append("selected provider is the deterministic mock provider")
    return RealModelStatus(real_model_enabled=settings.real_model_enabled, provider_code=provider_code, model_code=selected_model_code, default_model=settings.openai_default_model, provider_configured=provider_configured, model_configured=model_configured, api_key_present=api_key_present, provider_enabled=provider_enabled, model_enabled=model_enabled, safe_to_invoke=safe, reason="Ready for an explicit governed invocation." if safe else "; ".join(dict.fromkeys(reasons)))


class OpenAIResponsesProvider:
    """Small lazy OpenAI Responses adapter kept behind the governed gateway."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def invoke(self, *, model_name: str, system_instruction: str, input_text: str, max_output_tokens: int, reasoning_effort: str, temperature: float | None) -> tuple[str, dict[str, int], str | None]:
        return _openai_call(self.settings, model_name=model_name, system_instruction=system_instruction, input_text=input_text, max_output_tokens=max_output_tokens, reasoning_effort=reasoning_effort, temperature=temperature)


def _openai_call(settings: Settings, *, model_name: str, system_instruction: str, input_text: str, max_output_tokens: int, reasoning_effort: str, temperature: float | None) -> tuple[str, dict[str, int], str | None]:
    """Call the optional SDK lazily so mock/default startup needs no SDK or key."""
    from openai import OpenAI

    kwargs: dict[str, Any] = {"api_key": settings.openai_api_key, "timeout": settings.openai_request_timeout_seconds}
    if settings.openai_base_url: kwargs["base_url"] = settings.openai_base_url
    if settings.openai_org_id: kwargs["organization"] = settings.openai_org_id
    if settings.openai_project_id: kwargs["project"] = settings.openai_project_id
    client = OpenAI(**kwargs)
    request_kwargs: dict[str, Any] = {"model": model_name, "instructions": system_instruction, "input": input_text, "max_output_tokens": max_output_tokens, "reasoning": {"effort": reasoning_effort}, "store": settings.openai_store_responses}
    if temperature is not None: request_kwargs["temperature"] = temperature
    response = client.responses.create(**request_kwargs)
    output = getattr(response, "output_text", None) or ""
    usage_obj = getattr(response, "usage", None)
    usage: dict[str, int] = {}
    for key in ("input_tokens", "output_tokens", "total_tokens", "cached_input_tokens", "reasoning_tokens"):
        value = getattr(usage_obj, key, None) if usage_obj is not None else None
        if value is not None: usage[key] = int(value)
    if "output_tokens" in usage: usage["completion_tokens"] = usage["output_tokens"]
    return str(output), usage, getattr(response, "id", None)


def _post_safety_failure(text: str) -> str | None:
    lowered = text.lower()
    unsafe_markers = ("i executed", "action was executed", "i closed the ticket", "i deleted", "send me your api key", "provide your password", "run rm -rf")
    return "Unsafe or disallowed response content detected." if any(marker in lowered for marker in unsafe_markers) else None


def _real_fallback() -> str:
    return "The governed real-model response was not used. Safe deterministic Stage 1 guidance remains available; no external action was executed."


def _real_audit(db: Session, *, request: RealModelRequest, provider: AiProvider | None, model: AiModelConfig | None, template: AiPromptTemplate | None, policy: AiSafetyPolicy | None, prompt: str, status: str, generation_mode: str, safety_status: str, output_text: str | None, blocked_reason: str | None, fallback_used: bool, usage: dict[str, int], external_request_id: str | None, error_message: str | None, matched_rules: list[AiSafetyPolicyRule] | None = None) -> RealModelInvocationResponse:
    now = _now()
    input_tokens = int(usage.get("input_tokens") or max(1, ceil(len(prompt) / 4)))
    output_tokens = int(usage.get("output_tokens") or (max(1, ceil(len(output_text) / 4)) if output_text else 0))
    cost = ((input_tokens / 1000) * (model.cost_per_1k_input_tokens if model else 0)) + ((output_tokens / 1000) * (model.cost_per_1k_output_tokens if model else 0))
    normalized_usage = {"input_tokens": input_tokens, "completion_tokens": output_tokens, "output_tokens": output_tokens, "total_tokens": int(usage.get("total_tokens") or input_tokens + output_tokens)}
    for key in ("cached_input_tokens", "reasoning_tokens"):
        if usage.get(key) is not None: normalized_usage[key] = int(usage[key])
    metadata = {"generation_mode": generation_mode, "fallback_used": fallback_used, "external_request_id": external_request_id, "usage": normalized_usage}
    row = AiInvocationLog(invocation_number=_next_number(db, AiInvocationLog.invocation_number, f"AI-INV-{now:%Y%m%d}-"), provider_id=provider.id if provider else None, model_config_id=model.id if model else None, template_id=template.id if template else None, policy_id=policy.id if policy else None, request_source=request.request_source, request_source_id=request.request_source_id, task_type=request.task_type.upper(), status=status, input_summary=_redact(request.input_text)[:2000], prompt_rendered=_redact(prompt)[:10000], response_text=output_text, response_json=metadata, safety_status=safety_status, blocked_reason=blocked_reason, latency_ms=0, input_tokens_estimated=input_tokens, output_tokens_estimated=output_tokens, total_tokens_estimated=input_tokens + output_tokens, cost_estimated=cost, created_by=request.created_by, created_at=now, updated_at=now)
    db.add(row); db.flush()
    for rule in matched_rules or []:
        db.add(AiGuardrailEvent(invocation_id=row.id, policy_id=policy.id if policy else None, rule_id=rule.id, event_type="RULE_BLOCKED", severity=rule.severity, message=f"Rule {rule.rule_code} blocked the governed real-model request or response.", matched_text_summary="Configured safety pattern matched; raw text omitted.", created_at=_now()))
    if blocked_reason and not matched_rules and generation_mode == "REAL_MODEL_BLOCKED":
        db.add(AiGuardrailEvent(invocation_id=row.id, policy_id=policy.id if policy else None, rule_id=None, event_type="OUTPUT_BLOCKED", severity="HIGH", message=blocked_reason, matched_text_summary="Unsafe response marker detected; raw text omitted.", created_at=_now()))
    metering = None
    if provider and model:
        _usage(db, provider, model, request.task_type.upper(), "BLOCKED" if status in ("BLOCKED", "FAILED") and safety_status == "BLOCKED" else status, input_tokens, output_tokens, cost)
        from app.services import ai_model_cost_service
        metering = ai_model_cost_service.record_usage_for_invocation(db, row, provider=provider, model=model, usage=usage)
    db.commit()
    events = db.scalars(select(AiGuardrailEvent).where(AiGuardrailEvent.invocation_id == row.id).order_by(AiGuardrailEvent.created_at, AiGuardrailEvent.id)).all()
    return RealModelInvocationResponse(invocation_id=row.id, invocation_number=row.invocation_number, provider_code=request.provider_code, model_code=request.model_code, generation_mode=generation_mode, status=status, safety_status=safety_status, output_text=output_text, fallback_used=fallback_used, external_request_id=external_request_id, latency_ms=0, usage=metadata["usage"], guardrail_events=[ai_config_service._invocation_response(db, row).guardrail_events[i] for i in range(len(events))], error_message=error_message, estimated_cost=metering.estimated_total_cost if metering else None, pricing_status=("CONFIGURED" if metering and metering.pricing_snapshot_json else "MISSING_PRICING"), usage_source=metering.usage_source if metering else None, notes=["API keys are read from environment only and are never stored or logged."])


def invoke_real_model(db: Session, request: RealModelRequest, settings: Settings | None = None) -> RealModelInvocationResponse:
    settings = settings or get_settings()
    provider, model, template, policy = _resolve_real_configuration(db, request)
    prompt_payload = {"input_text": request.input_text, "context_items": request.context_items, "metadata": request.metadata}
    prompt = _render(template, prompt_payload) if template else _redact(request.input_text)
    evaluation = ai_safety_service.evaluate(db, f"{request.input_text}\n{prompt}", policy)
    if evaluation.decision == "BLOCK":
        return _real_audit(db, request=request, provider=provider, model=model, template=template, policy=policy, prompt=prompt, status="BLOCKED", generation_mode="REAL_MODEL_BLOCKED", safety_status="BLOCKED", output_text=None, blocked_reason="; ".join(rule.rule_code for rule in evaluation.matched_rules), fallback_used=True, usage={}, external_request_id=None, error_message="Safety policy blocked the request before provider invocation.", matched_rules=evaluation.matched_rules)
    status = real_model_status(db, provider_code=request.provider_code, model_code=request.model_code, settings=settings)
    if request.dry_run:
        return _real_audit(db, request=request, provider=provider, model=model, template=template, policy=policy, prompt=prompt, status="DRY_RUN", generation_mode="REAL_MODEL_DRY_RUN", safety_status=evaluation.safety_status, output_text="Dry run passed prompt and safety validation; no external provider was called.", blocked_reason=None, fallback_used=False, usage={}, external_request_id=None, error_message=None)
    from app.services import ai_model_cost_service
    guardrail_reasons = ai_model_cost_service.real_call_guardrail(db, model.model_code if model else request.model_code, prompt, request.max_output_tokens or (model.max_output_tokens if model else settings.openai_max_output_tokens), settings)
    allowed_tasks = {part.strip().upper() for part in settings.real_model_allowed_task_types.split(",") if part.strip()}
    if request.task_type.upper() not in allowed_tasks:
        guardrail_reasons.append(f"Task type {request.task_type.upper()} is not allowed for real-model invocation")
    if not request.allow_real_model or not status.safe_to_invoke or guardrail_reasons:
        reason = "Explicit real-model invocation was not allowed." if not request.allow_real_model else status.reason
        if guardrail_reasons: reason = "; ".join(guardrail_reasons)
        return _real_audit(db, request=request, provider=provider, model=model, template=template, policy=policy, prompt=prompt, status="DISABLED", generation_mode="REAL_MODEL_DISABLED", safety_status=evaluation.safety_status, output_text=_real_fallback(), blocked_reason=reason, fallback_used=True, usage={}, external_request_id=None, error_message=reason)
    started = monotonic()
    try:
        output, usage, external_id = OpenAIResponsesProvider(settings).invoke(model_name=model.model_name, system_instruction=request.system_instruction or template.system_template, input_text=prompt, max_output_tokens=request.max_output_tokens or model.max_output_tokens or settings.openai_max_output_tokens, reasoning_effort=request.reasoning_effort or settings.openai_reasoning_effort, temperature=request.temperature if request.temperature is not None else model.temperature)
        output_block_reason = _post_safety_failure(output)
        if output_block_reason:
            result = _real_audit(db, request=request, provider=provider, model=model, template=template, policy=policy, prompt=prompt, status="BLOCKED", generation_mode="REAL_MODEL_BLOCKED", safety_status="BLOCKED", output_text=_real_fallback(), blocked_reason=output_block_reason, fallback_used=True, usage=usage, external_request_id=external_id, error_message=output_block_reason)
        else:
            result = _real_audit(db, request=request, provider=provider, model=model, template=template, policy=policy, prompt=prompt, status="SUCCESS", generation_mode="REAL_MODEL_OPENAI_RESPONSES", safety_status=evaluation.safety_status, output_text=output, blocked_reason=None, fallback_used=False, usage=usage, external_request_id=external_id, error_message=None)
        result.latency_ms = max(0, int((monotonic() - started) * 1000))
        return result
    except Exception as error:
        message = "Governed real-model provider failed; deterministic fallback is available."
        result = _real_audit(db, request=request, provider=provider, model=model, template=template, policy=policy, prompt=prompt, status="FAILED", generation_mode="REAL_MODEL_FAILED", safety_status=evaluation.safety_status, output_text=_real_fallback(), blocked_reason=None, fallback_used=True, usage={}, external_request_id=None, error_message=message)
        result.latency_ms = max(0, int((monotonic() - started) * 1000))
        return result
