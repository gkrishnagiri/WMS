"""Local, bounded Stage 3 autonomous sandbox audit models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Stage3AutonomousRun(Base):
    __tablename__ = "stage3_autonomous_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    case_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_cases.id"))
    scenario_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("demo_scenario_runs.id"))
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_chat_sessions.id"))
    source_object_type: Mapped[Optional[str]] = mapped_column(String(80))
    source_object_id: Mapped[Optional[str]] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="CREATED")
    mode: Mapped[str] = mapped_column(String(50), nullable=False, default="STAGE_3_AUTONOMOUS_SANDBOX")
    profile_code: Mapped[str] = mapped_column(String(80), nullable=False)
    dry_run_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    dry_run_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    real_model_requested: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    real_model_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    provider_code: Mapped[Optional[str]] = mapped_column(String(80))
    model_code: Mapped[Optional[str]] = mapped_column(String(120))
    max_steps: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    steps_completed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=120)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    stopped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    stop_reason: Mapped[Optional[str]] = mapped_column(String(2000))
    max_estimated_cost: Mapped[float] = mapped_column(nullable=False, default=1.0)
    estimated_total_cost: Mapped[float] = mapped_column(nullable=False, default=0)
    total_input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by_role: Mapped[str] = mapped_column(String(80), nullable=False, default="DEMO_PRESENTER")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    steps: Mapped[list["Stage3AutonomousStep"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    events: Mapped[list["Stage3AutonomousEvent"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class Stage3AutonomousStep(Base):
    __tablename__ = "stage3_autonomous_steps"
    __table_args__ = (UniqueConstraint("run_id", "step_number", name="uq_stage3_steps_run_number"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    step_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stage3_autonomous_runs.id"), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="PLANNED")
    decision_type: Mapped[Optional[str]] = mapped_column(String(80))
    decision_summary: Mapped[Optional[str]] = mapped_column(String(2000))
    selected_action_code: Mapped[Optional[str]] = mapped_column(String(100))
    proposal_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_action_proposals.id"))
    execution_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("agent_action_executions.id"))
    guardrail_status: Mapped[Optional[str]] = mapped_column(String(40))
    guardrail_reason: Mapped[Optional[str]] = mapped_column(String(2000))
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost: Mapped[float] = mapped_column(nullable=False, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    run: Mapped[Stage3AutonomousRun] = relationship(back_populates="steps")


class Stage3AutonomousEvent(Base):
    __tablename__ = "stage3_autonomous_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stage3_autonomous_runs.id"), nullable=False)
    step_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("stage3_autonomous_steps.id"))
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    event_title: Mapped[str] = mapped_column(String(240), nullable=False)
    event_description: Mapped[str] = mapped_column(String(2000), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="INFO")
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    run: Mapped[Stage3AutonomousRun] = relationship(back_populates="events")


class Stage3AutonomyControl(Base):
    __tablename__ = "stage3_autonomy_controls"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    control_key: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    kill_switch_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requested_by_role: Mapped[Optional[str]] = mapped_column(String(80))
    reason: Mapped[Optional[str]] = mapped_column(String(2000))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
