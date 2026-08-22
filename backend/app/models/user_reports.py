"""User-reported functional issue model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class AmsUserReport(TimestampMixin, Base):
    __tablename__ = "ams_user_reports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    reporter_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("synthetic_users.id"))
    reporter_name: Mapped[str] = mapped_column(String(160), nullable=False)
    reporter_email: Mapped[Optional[str]] = mapped_column(String(200))
    reporter_persona: Mapped[Optional[str]] = mapped_column(String(40))
    report_channel: Mapped[str] = mapped_column(String(30), nullable=False, default="MANUAL")
    source_module: Mapped[str] = mapped_column(String(80), nullable=False, default="WAREHOUSE_FULFILLMENT")
    affected_entity_type: Mapped[str] = mapped_column(String(40), nullable=False, default="UNKNOWN")
    affected_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    business_impact: Mapped[str] = mapped_column(String(1000), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="SUBMITTED")
    journey_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("synthetic_journey_runs.id", use_alter=True))
    ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id", use_alter=True))
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    reporter_user: Mapped[Optional["SyntheticUser"]] = relationship(back_populates="reports")
    journey_run: Mapped[Optional["SyntheticJourneyRun"]] = relationship(foreign_keys=[journey_run_id])
