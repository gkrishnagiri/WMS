"""Guided, local-only EOS demo scenario orchestration models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class DemoScenario(TimestampMixin, Base):
    __tablename__ = "demo_scenarios"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    business_value: Mapped[str] = mapped_column(String(1000), nullable=False)
    default_experience: Mapped[str] = mapped_column(String(40), nullable=False, default="agentic")
    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    runs: Mapped[list["DemoScenarioRun"]] = relationship(back_populates="scenario")


class DemoScenarioRun(TimestampMixin, Base):
    __tablename__ = "demo_scenario_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    scenario_code: Mapped[str] = mapped_column(ForeignKey("demo_scenarios.scenario_code"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="IN_PROGRESS")
    current_step_code: Mapped[Optional[str]] = mapped_column(String(100))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reset_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_by_role: Mapped[str] = mapped_column(String(80), nullable=False, default="DEMO_PRESENTER")
    summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    outcome_summary: Mapped[Optional[str]] = mapped_column(String(2000))

    scenario: Mapped[DemoScenario] = relationship(back_populates="runs")
    steps: Mapped[list["DemoScenarioStep"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    artifacts: Mapped[list["DemoScenarioArtifact"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    events: Mapped[list["DemoScenarioEvent"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class DemoScenarioStep(TimestampMixin, Base):
    __tablename__ = "demo_scenario_steps"
    __table_args__ = (UniqueConstraint("run_id", "step_code", name="uq_demo_scenario_steps_code"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("demo_scenario_runs.id"), nullable=False)
    step_code: Mapped[str] = mapped_column(String(100), nullable=False)
    step_title: Mapped[str] = mapped_column(String(180), nullable=False)
    step_description: Mapped[str] = mapped_column(String(1000), nullable=False)
    presenter_instruction: Mapped[str] = mapped_column(String(1000), nullable=False)
    expected_result: Mapped[str] = mapped_column(String(1000), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False, default="INFO")
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    target_url: Mapped[Optional[str]] = mapped_column(String(500))
    target_object_type: Mapped[Optional[str]] = mapped_column(String(80))
    target_object_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    instructions: Mapped[Optional[str]] = mapped_column(String(1500))

    run: Mapped[DemoScenarioRun] = relationship(back_populates="steps")


class DemoScenarioArtifact(TimestampMixin, Base):
    __tablename__ = "demo_scenario_artifacts"
    __table_args__ = (UniqueConstraint("run_id", "artifact_type", "artifact_id", name="uq_demo_scenario_artifacts_link"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("demo_scenario_runs.id"), nullable=False)
    artifact_type: Mapped[str] = mapped_column(String(80), nullable=False)
    artifact_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    artifact_display: Mapped[str] = mapped_column(String(240), nullable=False)
    artifact_url: Mapped[Optional[str]] = mapped_column(String(500))
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)

    run: Mapped[DemoScenarioRun] = relationship(back_populates="artifacts")


class DemoScenarioEvent(Base):
    __tablename__ = "demo_scenario_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("demo_scenario_runs.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    event_title: Mapped[str] = mapped_column(String(240), nullable=False)
    event_description: Mapped[str] = mapped_column(String(1500), nullable=False)
    event_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    source_type: Mapped[Optional[str]] = mapped_column(String(80))
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    run: Mapped[DemoScenarioRun] = relationship(back_populates="events")
