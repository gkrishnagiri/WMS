"""OpenAI pricing snapshots and per-invocation usage metering."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class AiModelPricing(Base):
    __tablename__ = "ai_model_pricing"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pricing_id: Mapped[str] = mapped_column(String(140), unique=True, nullable=False)
    provider_code: Mapped[str] = mapped_column(String(100), nullable=False, default="OPENAI_RESPONSES")
    model_code: Mapped[str] = mapped_column(String(120), nullable=False)
    external_model_name: Mapped[str] = mapped_column(String(160), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    input_cost_per_million_tokens: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    completion_cost_per_million_tokens: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    cached_input_cost_per_million_tokens: Mapped[Optional[float]] = mapped_column(Float)
    reasoning_cost_per_million_tokens: Mapped[Optional[float]] = mapped_column(Float)
    pricing_source_note: Mapped[str] = mapped_column(String(1000), nullable=False)
    pricing_effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class AiModelUsageMetering(Base):
    __tablename__ = "ai_model_usage_metering"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usage_id: Mapped[str] = mapped_column(String(140), unique=True, nullable=False)
    invocation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ai_invocation_logs.id"), unique=True, nullable=False)
    provider_code: Mapped[str] = mapped_column(String(100), nullable=False)
    model_code: Mapped[str] = mapped_column(String(120), nullable=False)
    external_model_name: Mapped[str] = mapped_column(String(160), nullable=False)
    task_type: Mapped[str] = mapped_column(String(80), nullable=False)
    request_source: Mapped[str] = mapped_column(String(100), nullable=False)
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    case_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    cached_input_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    reasoning_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_input_cost: Mapped[Optional[float]] = mapped_column(Float)
    estimated_completion_cost: Mapped[Optional[float]] = mapped_column(Float)
    estimated_cached_input_cost: Mapped[Optional[float]] = mapped_column(Float)
    estimated_reasoning_cost: Mapped[Optional[float]] = mapped_column(Float)
    estimated_total_cost: Mapped[Optional[float]] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    pricing_id: Mapped[Optional[str]] = mapped_column(String(140))
    pricing_snapshot_json: Mapped[Optional[dict]] = mapped_column(JSON)
    usage_source: Mapped[str] = mapped_column(String(30), nullable=False, default="UNAVAILABLE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
