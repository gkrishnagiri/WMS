"""API schemas for governed AI configuration and mock invocations."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProviderResponse(BaseModel):
    id: UUID
    provider_code: str
    name: str
    provider_type: str
    description: str
    base_url: str | None
    auth_type: str
    enabled: bool
    is_mock: bool
    default_timeout_seconds: int
    created_at: datetime
    updated_at: datetime


class ModelConfigResponse(BaseModel):
    id: UUID
    model_code: str
    provider_id: UUID
    provider_code: str
    display_name: str
    model_name: str
    model_family: str
    purpose: str
    enabled: bool
    is_default: bool
    temperature: float
    top_p: float
    max_output_tokens: int
    context_window_tokens: int
    cost_per_1k_input_tokens: float
    cost_per_1k_output_tokens: float
    created_at: datetime
    updated_at: datetime


class PromptTemplateResponse(BaseModel):
    id: UUID
    template_code: str
    name: str
    description: str
    task_type: str
    template_version: int
    system_template: str
    user_template: str
    input_schema: dict | None
    output_schema: dict | None
    enabled: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime


class SafetyPolicyResponse(BaseModel):
    id: UUID
    policy_code: str
    name: str
    description: str
    policy_scope: str
    enabled: bool
    blocking_mode: str
    created_at: datetime
    updated_at: datetime


class SafetyRuleResponse(BaseModel):
    id: UUID
    policy_id: UUID
    policy_code: str
    rule_code: str
    name: str
    description: str
    rule_type: str
    severity: str
    enabled: bool
    match_pattern: str
    action: str
    created_at: datetime
    updated_at: datetime


class GuardrailEventResponse(BaseModel):
    id: UUID
    invocation_id: UUID
    policy_id: UUID | None
    rule_id: UUID | None
    event_type: str
    severity: str
    message: str
    matched_text_summary: str | None
    created_at: datetime


class UsageDailyResponse(BaseModel):
    id: UUID
    usage_date: date
    provider_code: str
    model_code: str
    task_type: str
    invocation_count: int
    blocked_count: int
    input_tokens_estimated: int
    output_tokens_estimated: int
    total_tokens_estimated: int
    cost_estimated: float
    created_at: datetime
    updated_at: datetime


class InvocationResponse(BaseModel):
    id: UUID
    invocation_number: str
    provider_id: UUID | None
    provider_code: str | None
    model_config_id: UUID | None
    model_code: str | None
    template_id: UUID | None
    template_code: str | None
    policy_id: UUID | None
    policy_code: str | None
    request_source: str
    request_source_id: UUID | None
    task_type: str
    status: str
    input_summary: str
    prompt_rendered: str
    response_text: str | None
    response_json: dict | None
    safety_status: str
    blocked_reason: str | None
    latency_ms: int
    input_tokens_estimated: int
    output_tokens_estimated: int
    total_tokens_estimated: int
    cost_estimated: float
    created_by: str
    created_at: datetime
    updated_at: datetime
    guardrail_events: list[GuardrailEventResponse] = Field(default_factory=list)


class AiConfigSummary(BaseModel):
    providers: int
    enabled_providers: int
    models: int
    enabled_models: int
    prompt_templates: int
    safety_policies: int
    safety_rules: int
    invocations_today: int
    blocked_invocations_today: int
    estimated_tokens_today: int
    estimated_cost_today: float


class TestInvocationRequest(BaseModel):
    task_type: str = Field(default="GENERAL_TEST", max_length=60)
    input_payload: dict = Field(default_factory=dict)
    template_code: str | None = Field(default=None, max_length=120)
    model_code: str | None = Field(default=None, max_length=120)
    request_source: str = Field(default="ADMIN_TEST", max_length=80)
    request_source_id: UUID | None = None
    created_by: str = Field(default="admin", max_length=120)


class SafetyCheckRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)


class SafetyMatchResponse(BaseModel):
    rule_code: str
    name: str
    action: str
    severity: str
    message: str


class SafetyCheckResponse(BaseModel):
    decision: str
    safety_status: str
    matched_rules: list[SafetyMatchResponse] = Field(default_factory=list)
    message: str

