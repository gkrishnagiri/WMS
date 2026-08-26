"""Governed AI provider, prompt, safety, invocation, and usage models."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class AiProvider(TimestampMixin, Base):
    __tablename__ = "ai_providers"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    provider_type: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    base_url: Mapped[Optional[str]] = mapped_column(String(500))
    auth_type: Mapped[str] = mapped_column(String(40), nullable=False, default="NONE")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_mock: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    default_timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30)

    models: Mapped[list["AiModelConfig"]] = relationship(back_populates="provider")


class AiModelConfig(TimestampMixin, Base):
    __tablename__ = "ai_model_configs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    provider_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_providers.id"), nullable=False)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    model_name: Mapped[str] = mapped_column(String(160), nullable=False)
    model_family: Mapped[str] = mapped_column(String(80), nullable=False)
    purpose: Mapped[str] = mapped_column(String(60), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    catalog_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    top_p: Mapped[float] = mapped_column(Float, nullable=False, default=1)
    max_output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    context_window_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=8000)
    cost_per_1k_input_tokens: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    cost_per_1k_output_tokens: Mapped[float] = mapped_column(Float, nullable=False, default=0)

    provider: Mapped[AiProvider] = relationship(back_populates="models")


class AiPromptTemplate(TimestampMixin, Base):
    __tablename__ = "ai_prompt_templates"
    __table_args__ = (UniqueConstraint("template_code", "template_version", name="uq_ai_prompt_templates_version"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_code: Mapped[str] = mapped_column(String(120), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    task_type: Mapped[str] = mapped_column(String(60), nullable=False)
    template_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    system_template: Mapped[str] = mapped_column(String(3000), nullable=False)
    user_template: Mapped[str] = mapped_column(String(5000), nullable=False)
    input_schema: Mapped[Optional[dict]] = mapped_column(JSON)
    output_schema: Mapped[Optional[dict]] = mapped_column(JSON)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class AiSafetyPolicy(TimestampMixin, Base):
    __tablename__ = "ai_safety_policies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    policy_scope: Mapped[str] = mapped_column(String(60), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    blocking_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="BLOCK")

    rules: Mapped[list["AiSafetyPolicyRule"]] = relationship(back_populates="policy", cascade="all, delete-orphan")


class AiSafetyPolicyRule(TimestampMixin, Base):
    __tablename__ = "ai_safety_policy_rules"
    __table_args__ = (UniqueConstraint("policy_id", "rule_code", name="uq_ai_safety_rules_policy_code"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_safety_policies.id"), nullable=False)
    rule_code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="HIGH")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    match_pattern: Mapped[str] = mapped_column(String(200), nullable=False)
    action: Mapped[str] = mapped_column(String(20), nullable=False, default="BLOCK")

    policy: Mapped[AiSafetyPolicy] = relationship(back_populates="rules")


class AiInvocationLog(TimestampMixin, Base):
    __tablename__ = "ai_invocation_logs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invocation_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    provider_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ai_providers.id"))
    model_config_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ai_model_configs.id"))
    template_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ai_prompt_templates.id"))
    policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ai_safety_policies.id"))
    request_source: Mapped[str] = mapped_column(String(80), nullable=False)
    request_source_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    task_type: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    input_summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    prompt_rendered: Mapped[str] = mapped_column(String(10000), nullable=False)
    response_text: Mapped[Optional[str]] = mapped_column(String(10000))
    response_json: Mapped[Optional[dict]] = mapped_column(JSON)
    safety_status: Mapped[str] = mapped_column(String(20), nullable=False)
    blocked_reason: Mapped[Optional[str]] = mapped_column(String(1500))
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    input_tokens_estimated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens_estimated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens_estimated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_estimated: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="system")

    guardrail_events: Mapped[list["AiGuardrailEvent"]] = relationship(back_populates="invocation", cascade="all, delete-orphan")


class AiUsageDaily(TimestampMixin, Base):
    __tablename__ = "ai_usage_daily"
    __table_args__ = (UniqueConstraint("usage_date", "provider_code", "model_code", "task_type", name="uq_ai_usage_daily_key"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usage_date: Mapped[date] = mapped_column(Date, nullable=False)
    provider_code: Mapped[str] = mapped_column(String(100), nullable=False)
    model_code: Mapped[str] = mapped_column(String(120), nullable=False)
    task_type: Mapped[str] = mapped_column(String(60), nullable=False)
    invocation_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    blocked_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    input_tokens_estimated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    output_tokens_estimated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens_estimated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cost_estimated: Mapped[float] = mapped_column(Float, nullable=False, default=0)


class AiGuardrailEvent(Base):
    __tablename__ = "ai_guardrail_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invocation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_invocation_logs.id"), nullable=False)
    policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ai_safety_policies.id"))
    rule_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ai_safety_policy_rules.id"))
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    matched_text_summary: Mapped[Optional[str]] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    invocation: Mapped[AiInvocationLog] = relationship(back_populates="guardrail_events")
