"""Governed, database-backed observability alerting models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class ObsAlertRule(TimestampMixin, Base):
    __tablename__ = "obs_alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(40), nullable=False)
    source_system: Mapped[str] = mapped_column(String(80), nullable=False)
    metric_name: Mapped[Optional[str]] = mapped_column(String(120))
    query_text: Mapped[Optional[str]] = mapped_column(String(500))
    condition_operator: Mapped[str] = mapped_column(String(10), nullable=False, default="GT")
    threshold_value: Mapped[Optional[float]] = mapped_column()
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    enabled: Mapped[bool] = mapped_column(nullable=False, default=True)
    deduplication_key_template: Mapped[str] = mapped_column(String(250), nullable=False)
    cooldown_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    evaluation_window_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    target_experience: Mapped[str] = mapped_column(String(40), nullable=False, default="operations")
    recommended_owner: Mapped[str] = mapped_column(String(120), nullable=False, default="AMS-WAREHOUSE-SUPPORT")
    create_ticket_by_default: Mapped[bool] = mapped_column(nullable=False, default=False)


class ObsAlertEvaluationRun(Base):
    __tablename__ = "obs_alert_evaluation_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    trigger_source: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rules_evaluated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    events_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    events_suppressed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tickets_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000))


class ObsAlertEvent(TimestampMixin, Base):
    __tablename__ = "obs_alert_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    rule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("obs_alert_rules.id"), nullable=False)
    rule_code: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(String(1500), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
    deduplication_key: Mapped[str] = mapped_column(String(250), nullable=False)
    source_signal: Mapped[str] = mapped_column(String(120), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    observed_value: Mapped[Optional[float]] = mapped_column()
    threshold_value: Mapped[Optional[float]] = mapped_column()
    condition_summary: Mapped[str] = mapped_column(String(500), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    suppressed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ticket_creation_status: Mapped[str] = mapped_column(String(30), nullable=False, default="NOT_REQUIRED")
    created_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id"))

    rule: Mapped[ObsAlertRule] = relationship()
    evidence: Mapped[list["ObsAlertEventEvidence"]] = relationship(back_populates="event", cascade="all, delete-orphan")


class ObsAlertEventEvidence(Base):
    __tablename__ = "obs_alert_event_evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("obs_alert_events.id"), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(40), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(String(1000), nullable=False)
    payload_json: Mapped[Optional[dict]] = mapped_column(JSON)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    event: Mapped[ObsAlertEvent] = relationship(back_populates="evidence")


class ObsAlertTicketLink(Base):
    __tablename__ = "obs_alert_ticket_links"
    __table_args__ = (UniqueConstraint("event_id", "ams_ticket_id", name="uq_obs_alert_ticket_link"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("obs_alert_events.id"), nullable=False)
    ams_ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ams_tickets.id"), nullable=False)
    link_type: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="system")
