"""Application-level deterministic observability evidence models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class ObsTrace(TimestampMixin, Base):
    __tablename__ = "obs_traces"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    trace_name: Mapped[str] = mapped_column(String(200), nullable=False)
    trace_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    source_module: Mapped[str] = mapped_column(String(80), nullable=False)
    root_entity_type: Mapped[Optional[str]] = mapped_column(String(40))
    root_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    root_reference: Mapped[Optional[str]] = mapped_column(String(160))
    linked_alert_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mon_alerts.id"))
    linked_triage_case_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mon_triage_cases.id"))
    linked_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(String(1000), nullable=False)

    spans: Mapped[list["ObsSpan"]] = relationship(back_populates="trace", cascade="all, delete-orphan")
    logs: Mapped[list["ObsLogEvent"]] = relationship(back_populates="trace")
    metrics: Mapped[list["ObsMetricSample"]] = relationship(back_populates="trace")


class ObsSpan(TimestampMixin, Base):
    __tablename__ = "obs_spans"
    __table_args__ = (UniqueConstraint("trace_id", "span_id", name="uq_obs_spans_trace_span"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trace_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("obs_traces.id"), nullable=False)
    span_id: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_span_id: Mapped[Optional[str]] = mapped_column(String(100))
    span_name: Mapped[str] = mapped_column(String(200), nullable=False)
    service_name: Mapped[str] = mapped_column(String(120), nullable=False)
    component_code: Mapped[Optional[str]] = mapped_column(String(80))
    operation_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    error_type: Mapped[Optional[str]] = mapped_column(String(120))
    error_message: Mapped[Optional[str]] = mapped_column(String(1000))
    attributes: Mapped[Optional[dict]] = mapped_column(JSON)

    trace: Mapped[ObsTrace] = relationship(back_populates="spans")


class ObsLogEvent(Base):
    __tablename__ = "obs_log_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    log_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    trace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("obs_traces.id"))
    span_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("obs_spans.id"))
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    logger_name: Mapped[str] = mapped_column(String(160), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    source_module: Mapped[str] = mapped_column(String(80), nullable=False)
    component_code: Mapped[Optional[str]] = mapped_column(String(80))
    entity_type: Mapped[Optional[str]] = mapped_column(String(40))
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    linked_alert_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mon_alerts.id"))
    linked_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id"))
    context: Mapped[Optional[dict]] = mapped_column(JSON)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    trace: Mapped[Optional[ObsTrace]] = relationship(back_populates="logs")


class ObsMetricSample(Base):
    __tablename__ = "obs_metric_samples"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(120), nullable=False)
    metric_value: Mapped[float] = mapped_column(nullable=False)
    metric_unit: Mapped[str] = mapped_column(String(30), nullable=False)
    component_code: Mapped[Optional[str]] = mapped_column(String(80))
    severity: Mapped[Optional[str]] = mapped_column(String(20))
    trace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("obs_traces.id"))
    linked_alert_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mon_alerts.id"))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    attributes: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    trace: Mapped[Optional[ObsTrace]] = relationship(back_populates="metrics")


class ObsDiagnosticCase(TimestampMixin, Base):
    __tablename__ = "obs_diagnostic_cases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diagnostic_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1500), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    linked_alert_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mon_alerts.id"))
    linked_triage_case_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("mon_triage_cases.id"))
    linked_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id"))
    primary_trace_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("obs_traces.id"))
    probable_cause: Mapped[str] = mapped_column(String(1000), nullable=False)
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    recommended_next_steps: Mapped[str] = mapped_column(String(1500), nullable=False)
    diagnosis_summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="support-engineer")
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    evidence: Mapped[list["ObsDiagnosticEvidence"]] = relationship(back_populates="diagnostic_case", cascade="all, delete-orphan")


class ObsDiagnosticEvidence(Base):
    __tablename__ = "obs_diagnostic_evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    diagnostic_case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("obs_diagnostic_cases.id"), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_table: Mapped[str] = mapped_column(String(80), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    details: Mapped[str] = mapped_column(String(1500), nullable=False)
    weight: Mapped[float] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    diagnostic_case: Mapped[ObsDiagnosticCase] = relationship(back_populates="evidence")
