"""Deterministic synthetic users, journey catalog, and run history models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class SyntheticUser(TimestampMixin, Base):
    __tablename__ = "synthetic_users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    persona: Mapped[str] = mapped_column(String(40), nullable=False)
    department: Mapped[str] = mapped_column(String(120), nullable=False)
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(200), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    journey_runs: Mapped[list["SyntheticJourneyRun"]] = relationship(back_populates="synthetic_user")
    reports: Mapped[list["AmsUserReport"]] = relationship(back_populates="reporter_user")


class SyntheticJourney(TimestampMixin, Base):
    __tablename__ = "synthetic_journeys"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journey_code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    persona: Mapped[str] = mapped_column(String(40), nullable=False)
    journey_type: Mapped[str] = mapped_column(String(40), nullable=False)
    expected_outcome: Mapped[str] = mapped_column(String(40), nullable=False)
    creates_user_report_on_failure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creates_ticket_on_failure: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    default_payload: Mapped[Optional[dict]] = mapped_column(JSON)

    runs: Mapped[list["SyntheticJourneyRun"]] = relationship(back_populates="journey")


class SyntheticJourneyRun(TimestampMixin, Base):
    __tablename__ = "synthetic_journey_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    journey_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("synthetic_journeys.id"), nullable=False)
    synthetic_user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("synthetic_users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PARTIAL")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[Optional[int]] = mapped_column()
    input_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    result_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    failure_type: Mapped[Optional[str]] = mapped_column(String(80))
    failure_message: Mapped[Optional[str]] = mapped_column(String(1000))
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_orders.id"))
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_fulfillment_tasks.id"))
    shipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_shipments.id"))
    user_report_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_user_reports.id", use_alter=True))
    ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id"))

    journey: Mapped[SyntheticJourney] = relationship(back_populates="runs")
    synthetic_user: Mapped[SyntheticUser] = relationship(back_populates="journey_runs")
    user_report: Mapped[Optional["AmsUserReport"]] = relationship(foreign_keys=[user_report_id])
