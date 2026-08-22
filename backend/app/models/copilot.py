"""Governed deterministic support copilot models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class CopilotSession(TimestampMixin, Base):
    __tablename__ = "copilot_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1500), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
    primary_entity_type: Mapped[str] = mapped_column(String(40), nullable=False, default="MANUAL")
    primary_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    primary_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id"))
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="support-engineer")
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    snapshots: Mapped[list["CopilotContextSnapshot"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    recommendations: Mapped[list["CopilotRecommendation"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    action_plans: Mapped[list["CopilotActionPlan"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    messages: Mapped[list["CopilotMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    action_events: Mapped[list["CopilotActionEvent"]] = relationship(back_populates="session", cascade="all, delete-orphan")


class CopilotContextSnapshot(Base):
    __tablename__ = "copilot_context_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("copilot_sessions.id"), nullable=False)
    snapshot_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    source_entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    source_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    impact_summary: Mapped[str] = mapped_column(String(1500), nullable=False)
    technical_summary: Mapped[str] = mapped_column(String(2500), nullable=False)
    business_summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    timeline_summary: Mapped[str] = mapped_column(String(3000), nullable=False)
    evidence_summary: Mapped[str] = mapped_column(String(3000), nullable=False)
    related_entities: Mapped[Optional[dict]] = mapped_column(JSON)
    raw_context: Mapped[Optional[dict]] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="support-engineer")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    session: Mapped[CopilotSession] = relationship(back_populates="snapshots")
    recommendations: Mapped[list["CopilotRecommendation"]] = relationship(back_populates="snapshot")
    action_plans: Mapped[list["CopilotActionPlan"]] = relationship(back_populates="snapshot")


class CopilotRecommendation(TimestampMixin, Base):
    __tablename__ = "copilot_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("copilot_sessions.id"), nullable=False)
    snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("copilot_context_snapshots.id"))
    recommendation_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    details: Mapped[str] = mapped_column(String(1500), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    confidence_level: Mapped[str] = mapped_column(String(20), nullable=False, default="UNKNOWN")
    rationale: Mapped[str] = mapped_column(String(1500), nullable=False)
    source_evidence: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PROPOSED")
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    session: Mapped[CopilotSession] = relationship(back_populates="recommendations")
    snapshot: Mapped[Optional[CopilotContextSnapshot]] = relationship(back_populates="recommendations")


class CopilotActionPlan(TimestampMixin, Base):
    __tablename__ = "copilot_action_plans"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("copilot_sessions.id"), nullable=False)
    snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("copilot_context_snapshots.id"))
    plan_number: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="DRAFT")
    steps: Mapped[list] = mapped_column(JSON, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    session: Mapped[CopilotSession] = relationship(back_populates="action_plans")
    snapshot: Mapped[Optional[CopilotContextSnapshot]] = relationship(back_populates="action_plans")


class CopilotMessage(TimestampMixin, Base):
    __tablename__ = "copilot_messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("copilot_sessions.id"), nullable=False)
    message_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(String(5000), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")
    target_entity_type: Mapped[Optional[str]] = mapped_column(String(40))
    target_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="support-engineer")

    session: Mapped[CopilotSession] = relationship(back_populates="messages")


class CopilotSafeAction(TimestampMixin, Base):
    __tablename__ = "copilot_safe_actions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action_code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    target_module: Mapped[str] = mapped_column(String(80), nullable=False)
    action_type: Mapped[str] = mapped_column(String(40), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False, default="LOW")
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class CopilotActionEvent(Base):
    __tablename__ = "copilot_action_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("copilot_sessions.id"), nullable=False)
    action_code: Mapped[str] = mapped_column(String(80), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_entity_type: Mapped[Optional[str]] = mapped_column(String(40))
    target_entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    from_status: Mapped[Optional[str]] = mapped_column(String(30))
    to_status: Mapped[Optional[str]] = mapped_column(String(30))
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    event_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    session: Mapped[CopilotSession] = relationship(back_populates="action_events")
