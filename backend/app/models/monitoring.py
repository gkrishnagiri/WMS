"""Deterministic monitoring components, alerts, and manual triage cases."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class MonComponent(TimestampMixin, Base):
    __tablename__ = "mon_components"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    component_code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    component_type: Mapped[str] = mapped_column(String(40), nullable=False)
    layer: Mapped[str] = mapped_column(String(40), nullable=False)
    environment: Mapped[str] = mapped_column(String(40), nullable=False, default="development")
    owner_team: Mapped[str] = mapped_column(String(120), nullable=False)
    business_service: Mapped[str] = mapped_column(String(160), nullable=False, default="Warehouse & Fulfillment Operations")
    application_name: Mapped[str] = mapped_column(String(160), nullable=False, default="Enterprise Operations Suite")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    description: Mapped[str] = mapped_column(String(500), nullable=False)

    rules: Mapped[list["MonAlertRule"]] = relationship(back_populates="component")
    alerts: Mapped[list["MonAlert"]] = relationship(back_populates="component")


class MonAlertRule(TimestampMixin, Base):
    __tablename__ = "mon_alert_rules"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    component_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mon_components.id"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(80), nullable=False)
    condition_operator: Mapped[str] = mapped_column(String(10), nullable=False)
    threshold_value: Mapped[float] = mapped_column(nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    dedupe_window_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=15)

    component: Mapped[MonComponent] = relationship(back_populates="rules")
    alerts: Mapped[list["MonAlert"]] = relationship(back_populates="rule")


class MonAlert(TimestampMixin, Base):
    __tablename__ = "mon_alerts"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    rule_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mon_alert_rules.id"), nullable=False)
    component_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mon_components.id"), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
    signal_type: Mapped[str] = mapped_column(String(40), nullable=False, default="METRIC_THRESHOLD")
    metric_name: Mapped[str] = mapped_column(String(80), nullable=False)
    observed_value: Mapped[float] = mapped_column(nullable=False)
    threshold_value: Mapped[float] = mapped_column(nullable=False)
    dedupe_key: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    suppressed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    linked_exception_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ops_exceptions.id"))
    linked_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id"))

    rule: Mapped[MonAlertRule] = relationship(back_populates="alerts")
    component: Mapped[MonComponent] = relationship(back_populates="alerts")
    events: Mapped[list["MonAlertEvent"]] = relationship(back_populates="alert", cascade="all, delete-orphan")


class MonAlertEvent(Base):
    __tablename__ = "mon_alert_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mon_alerts.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    from_status: Mapped[Optional[str]] = mapped_column(String(30))
    to_status: Mapped[Optional[str]] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    event_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    alert: Mapped[MonAlert] = relationship(back_populates="events")


class MonTriageCase(TimestampMixin, Base):
    __tablename__ = "mon_triage_cases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1500), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    suspected_impact: Mapped[str] = mapped_column(String(1000), nullable=False)
    suspected_root_cause: Mapped[Optional[str]] = mapped_column(String(1000))
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    analysis_notes: Mapped[Optional[str]] = mapped_column(String(2000))
    linked_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id"))
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="support-engineer")
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    alert_links: Mapped[list["MonTriageCaseAlert"]] = relationship(back_populates="triage_case", cascade="all, delete-orphan")


class MonTriageCaseAlert(Base):
    __tablename__ = "mon_triage_case_alerts"
    __table_args__ = (UniqueConstraint("triage_case_id", "alert_id", name="uq_mon_triage_case_alert"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    triage_case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mon_triage_cases.id"), nullable=False)
    alert_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("mon_alerts.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    triage_case: Mapped[MonTriageCase] = relationship(back_populates="alert_links")
    alert: Mapped[MonAlert] = relationship()

