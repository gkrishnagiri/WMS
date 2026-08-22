"""Operational exception models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class OpsException(TimestampMixin, Base):
    __tablename__ = "ops_exceptions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exception_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    exception_type: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
    source_module: Mapped[str] = mapped_column(String(80), nullable=False, default="WAREHOUSE_FULFILLMENT")
    source_entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    source_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True), nullable=True)
    source_reference: Mapped[Optional[str]] = mapped_column(String(120))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    detection_method: Mapped[str] = mapped_column(String(30), nullable=False, default="RULE_BASED")
    business_impact: Mapped[str] = mapped_column(String(500), nullable=False)
    technical_context: Mapped[Optional[dict]] = mapped_column(JSON)
    first_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    tickets: Mapped[List["AmsTicket"]] = relationship(back_populates="exception")


from app.models.ams import AmsTicket  # noqa: E402  # imported for relationship typing/registration

