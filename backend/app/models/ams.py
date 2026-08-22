"""Deterministic AMS ticket and lifecycle event models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class AmsTicket(TimestampMixin, Base):
    __tablename__ = "ams_tickets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    ticket_type: Mapped[str] = mapped_column(String(30), nullable=False, default="INCIDENT")
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="P3")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="NEW")
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="MANUAL")
    source_module: Mapped[str] = mapped_column(String(80), nullable=False, default="WAREHOUSE_FULFILLMENT")
    exception_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ops_exceptions.id"), nullable=True)
    user_report_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_user_reports.id", use_alter=True), nullable=True)
    affected_entity_type: Mapped[Optional[str]] = mapped_column(String(40))
    affected_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    short_description: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    assignment_group: Mapped[str] = mapped_column(String(120), nullable=False, default="AMS-WAREHOUSE-SUPPORT")
    assigned_to: Mapped[Optional[str]] = mapped_column(String(120))
    business_service: Mapped[str] = mapped_column(String(160), nullable=False, default="Warehouse & Fulfillment Operations")
    application_name: Mapped[str] = mapped_column(String(160), nullable=False, default="Enterprise Operations Suite")
    environment: Mapped[str] = mapped_column(String(40), nullable=False, default="development")
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolution_code: Mapped[Optional[str]] = mapped_column(String(80))
    resolution_notes: Mapped[Optional[str]] = mapped_column(String(2000))

    exception: Mapped[Optional["OpsException"]] = relationship(back_populates="tickets")
    events: Mapped[list["AmsTicketEvent"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")


class AmsTicketEvent(Base):
    __tablename__ = "ams_ticket_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ams_tickets.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    from_status: Mapped[Optional[str]] = mapped_column(String(30))
    to_status: Mapped[Optional[str]] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    event_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    ticket: Mapped[AmsTicket] = relationship(back_populates="events")
