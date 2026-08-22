"""Deterministic batch job definitions, executions, and audit history."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class BatchJob(TimestampMixin, Base):
    __tablename__ = "batch_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    job_type: Mapped[str] = mapped_column(String(60), nullable=False)
    module: Mapped[str] = mapped_column(String(80), nullable=False, default="WAREHOUSE_FULFILLMENT")
    business_service: Mapped[str] = mapped_column(String(160), nullable=False, default="Warehouse & Fulfillment Operations")
    application_name: Mapped[str] = mapped_column(String(160), nullable=False, default="Enterprise Operations Suite")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    default_severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    sla_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=60)

    steps: Mapped[list["BatchJobStep"]] = relationship(back_populates="job", cascade="all, delete-orphan")
    runs: Mapped[list["BatchRun"]] = relationship(back_populates="job")


class BatchJobStep(TimestampMixin, Base):
    __tablename__ = "batch_job_steps"
    __table_args__ = (
        UniqueConstraint("job_id", "step_code", name="uq_batch_job_steps_code"),
        UniqueConstraint("job_id", "step_order", name="uq_batch_job_steps_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("batch_jobs.id"), nullable=False)
    step_code: Mapped[str] = mapped_column(String(100), nullable=False)
    step_name: Mapped[str] = mapped_column(String(180), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    expected_duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)

    job: Mapped[BatchJob] = relationship(back_populates="steps")
    runs: Mapped[list["BatchStepRun"]] = relationship(back_populates="job_step")


class BatchRun(TimestampMixin, Base):
    __tablename__ = "batch_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("batch_jobs.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    trigger_type: Mapped[str] = mapped_column(String(30), nullable=False, default="SIMULATION")
    scenario_code: Mapped[str] = mapped_column(String(100), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    records_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_succeeded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_type: Mapped[Optional[str]] = mapped_column(String(60))
    failure_message: Mapped[Optional[str]] = mapped_column(String(1500))
    summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    linked_exception_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ops_exceptions.id"))
    linked_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id"))
    linked_alert_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mon_alerts.id"))
    linked_diagnostic_case_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("obs_diagnostic_cases.id"))
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="system")

    job: Mapped[BatchJob] = relationship(back_populates="runs")
    step_runs: Mapped[list["BatchStepRun"]] = relationship(back_populates="batch_run", cascade="all, delete-orphan")
    events: Mapped[list["BatchRunEvent"]] = relationship(back_populates="batch_run", cascade="all, delete-orphan")


class BatchStepRun(Base):
    __tablename__ = "batch_step_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("batch_runs.id"), nullable=False)
    job_step_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("batch_job_steps.id"), nullable=False)
    step_code: Mapped[str] = mapped_column(String(100), nullable=False)
    step_name: Mapped[str] = mapped_column(String(180), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    records_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_succeeded: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_failed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failure_type: Mapped[Optional[str]] = mapped_column(String(60))
    failure_message: Mapped[Optional[str]] = mapped_column(String(1500))
    technical_context: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    batch_run: Mapped[BatchRun] = relationship(back_populates="step_runs")
    job_step: Mapped[BatchJobStep] = relationship(back_populates="runs")


class BatchRunEvent(Base):
    __tablename__ = "batch_run_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("batch_runs.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    from_status: Mapped[Optional[str]] = mapped_column(String(30))
    to_status: Mapped[Optional[str]] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    event_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    batch_run: Mapped[BatchRun] = relationship(back_populates="events")
