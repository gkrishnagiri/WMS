"""Read-only catalog, audit, and usage services for governed AI configuration."""

from __future__ import annotations

from datetime import datetime, time, timezone
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.ai_config import AiGuardrailEvent, AiInvocationLog, AiModelConfig, AiPromptTemplate, AiProvider, AiSafetyPolicy, AiSafetyPolicyRule, AiUsageDaily
from app.schemas.ai_config import AiConfigSummary, GuardrailEventResponse, InvocationResponse, ModelConfigResponse, PromptTemplateResponse, ProviderResponse, SafetyPolicyResponse, SafetyRuleResponse, UsageDailyResponse


class AiConfigError(Exception):
    def __init__(self, message: str, status_code: int = 404) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _provider_response(row: AiProvider) -> ProviderResponse:
    return ProviderResponse.model_validate(row, from_attributes=True)


def list_providers(db: Session) -> list[ProviderResponse]:
    return [_provider_response(row) for row in db.scalars(select(AiProvider).order_by(AiProvider.provider_code)).all()]


def list_models(db: Session) -> list[ModelConfigResponse]:
    rows = db.scalars(select(AiModelConfig).join(AiProvider).order_by(AiModelConfig.model_code)).all()
    return [ModelConfigResponse(id=row.id, model_code=row.model_code, provider_id=row.provider_id, provider_code=row.provider.provider_code, display_name=row.display_name, model_name=row.model_name, model_family=row.model_family, purpose=row.purpose, enabled=row.enabled, is_default=row.is_default, temperature=row.temperature, top_p=row.top_p, max_output_tokens=row.max_output_tokens, context_window_tokens=row.context_window_tokens, cost_per_1k_input_tokens=row.cost_per_1k_input_tokens, cost_per_1k_output_tokens=row.cost_per_1k_output_tokens, created_at=row.created_at, updated_at=row.updated_at) for row in rows]


def list_templates(db: Session) -> list[PromptTemplateResponse]:
    return [PromptTemplateResponse.model_validate(row, from_attributes=True) for row in db.scalars(select(AiPromptTemplate).order_by(AiPromptTemplate.template_code, AiPromptTemplate.template_version)).all()]


def list_policies(db: Session) -> list[SafetyPolicyResponse]:
    return [SafetyPolicyResponse.model_validate(row, from_attributes=True) for row in db.scalars(select(AiSafetyPolicy).order_by(AiSafetyPolicy.policy_code)).all()]


def list_rules(db: Session) -> list[SafetyRuleResponse]:
    rows = db.scalars(select(AiSafetyPolicyRule).join(AiSafetyPolicy).order_by(AiSafetyPolicyRule.rule_code)).all()
    return [SafetyRuleResponse(id=row.id, policy_id=row.policy_id, policy_code=row.policy.policy_code, rule_code=row.rule_code, name=row.name, description=row.description, rule_type=row.rule_type, severity=row.severity, enabled=row.enabled, match_pattern=row.match_pattern, action=row.action, created_at=row.created_at, updated_at=row.updated_at) for row in rows]


def _invocation_response(db: Session, row: AiInvocationLog) -> InvocationResponse:
    provider = db.get(AiProvider, row.provider_id) if row.provider_id else None
    model = db.get(AiModelConfig, row.model_config_id) if row.model_config_id else None
    template = db.get(AiPromptTemplate, row.template_id) if row.template_id else None
    policy = db.get(AiSafetyPolicy, row.policy_id) if row.policy_id else None
    events = db.scalars(select(AiGuardrailEvent).where(AiGuardrailEvent.invocation_id == row.id).order_by(AiGuardrailEvent.created_at, AiGuardrailEvent.id)).all()
    return InvocationResponse(id=row.id, invocation_number=row.invocation_number, provider_id=row.provider_id, provider_code=provider.provider_code if provider else None, model_config_id=row.model_config_id, model_code=model.model_code if model else None, template_id=row.template_id, template_code=template.template_code if template else None, policy_id=row.policy_id, policy_code=policy.policy_code if policy else None, request_source=row.request_source, request_source_id=row.request_source_id, task_type=row.task_type, status=row.status, input_summary=row.input_summary, prompt_rendered=row.prompt_rendered, response_text=row.response_text, response_json=row.response_json, safety_status=row.safety_status, blocked_reason=row.blocked_reason, latency_ms=row.latency_ms, input_tokens_estimated=row.input_tokens_estimated, output_tokens_estimated=row.output_tokens_estimated, total_tokens_estimated=row.total_tokens_estimated, cost_estimated=row.cost_estimated, created_by=row.created_by, created_at=row.created_at, updated_at=row.updated_at, guardrail_events=[GuardrailEventResponse.model_validate(event, from_attributes=True) for event in events])


def list_invocations(db: Session, status: str | None = None, task_type: str | None = None, provider_code: str | None = None, model_code: str | None = None, safety_status: str | None = None, request_source: str | None = None) -> list[InvocationResponse]:
    statement = select(AiInvocationLog).order_by(AiInvocationLog.created_at.desc()).limit(100)
    if status: statement = statement.where(AiInvocationLog.status == status.upper())
    if task_type: statement = statement.where(AiInvocationLog.task_type == task_type.upper())
    if safety_status: statement = statement.where(AiInvocationLog.safety_status == safety_status.upper())
    if request_source: statement = statement.where(AiInvocationLog.request_source == request_source)
    if provider_code: statement = statement.join(AiProvider, AiProvider.id == AiInvocationLog.provider_id).where(AiProvider.provider_code == provider_code)
    if model_code: statement = statement.join(AiModelConfig, AiModelConfig.id == AiInvocationLog.model_config_id).where(AiModelConfig.model_code == model_code)
    return [_invocation_response(db, row) for row in db.scalars(statement).all()]


def get_invocation(db: Session, invocation_id: UUID) -> InvocationResponse:
    row = db.get(AiInvocationLog, invocation_id)
    if row is None: raise AiConfigError("AI invocation not found.")
    return _invocation_response(db, row)


def list_usage(db: Session) -> list[UsageDailyResponse]:
    return [UsageDailyResponse.model_validate(row, from_attributes=True) for row in db.scalars(select(AiUsageDaily).order_by(AiUsageDaily.usage_date.desc(), AiUsageDaily.provider_code, AiUsageDaily.model_code, AiUsageDaily.task_type)).all()]


def list_guardrail_events(db: Session) -> list[GuardrailEventResponse]:
    return [GuardrailEventResponse.model_validate(row, from_attributes=True) for row in db.scalars(select(AiGuardrailEvent).order_by(AiGuardrailEvent.created_at.desc()).limit(200)).all()]


def get_summary(db: Session) -> AiConfigSummary:
    start = datetime.combine(datetime.now(timezone.utc).date(), time.min, tzinfo=timezone.utc)
    return AiConfigSummary(providers=db.scalar(select(func.count(AiProvider.id))) or 0, enabled_providers=db.scalar(select(func.count(AiProvider.id)).where(AiProvider.enabled.is_(True))) or 0, models=db.scalar(select(func.count(AiModelConfig.id))) or 0, enabled_models=db.scalar(select(func.count(AiModelConfig.id)).where(AiModelConfig.enabled.is_(True))) or 0, prompt_templates=db.scalar(select(func.count(AiPromptTemplate.id))) or 0, safety_policies=db.scalar(select(func.count(AiSafetyPolicy.id))) or 0, safety_rules=db.scalar(select(func.count(AiSafetyPolicyRule.id))) or 0, invocations_today=db.scalar(select(func.count(AiInvocationLog.id)).where(AiInvocationLog.created_at >= start)) or 0, blocked_invocations_today=db.scalar(select(func.count(AiInvocationLog.id)).where(AiInvocationLog.created_at >= start, AiInvocationLog.status == "BLOCKED")) or 0, estimated_tokens_today=db.scalar(select(func.coalesce(func.sum(AiInvocationLog.total_tokens_estimated), 0)).where(AiInvocationLog.created_at >= start)) or 0, estimated_cost_today=float(db.scalar(select(func.coalesce(func.sum(AiInvocationLog.cost_estimated), 0.0)).where(AiInvocationLog.created_at >= start)) or 0.0))
