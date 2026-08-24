"""Persistent case-intake and deterministic agent chat models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class AgentCase(TimestampMixin, Base):
    __tablename__ = "agent_cases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    case_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="P3")
    source: Mapped[str] = mapped_column(String(40), nullable=False, default="CHAT")
    stage_mode: Mapped[str] = mapped_column(String(40), nullable=False, default="STAGE_1_READ_ONLY")
    created_by_role: Mapped[str] = mapped_column(String(50), nullable=False)
    linked_ams_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_tickets.id"))
    linked_user_report_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ams_user_reports.id"))
    linked_alert_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("obs_alert_events.id"))
    linked_batch_run_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("batch_runs.id"))
    linked_diagnostic_case_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("obs_diagnostic_cases.id"))
    linked_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_orders.id"))
    linked_shipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_shipments.id"))
    linked_inventory_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_items.id"))
    source_object_type: Mapped[Optional[str]] = mapped_column(String(50))
    source_object_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    source_object_display: Mapped[Optional[str]] = mapped_column(String(200))
    source_object_url: Mapped[Optional[str]] = mapped_column(String(500))
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    sessions: Mapped[list["AgentChatSession"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    evidence: Mapped[list["AgentEvidenceItem"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    runs: Mapped[list["AgentOrchestrationRun"]] = relationship(back_populates="case", cascade="all, delete-orphan")
    proposals: Mapped[list["AgentActionProposal"]] = relationship(back_populates="case", cascade="all, delete-orphan")


class AgentChatSession(Base):
    __tablename__ = "agent_chat_sessions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_cases.id"), nullable=False)
    audience: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    started_by_role: Mapped[str] = mapped_column(String(50), nullable=False)
    experience: Mapped[str] = mapped_column(String(30), nullable=False, default="agentic")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    case: Mapped[AgentCase] = relationship(back_populates="sessions")
    messages: Mapped[list["AgentChatMessage"]] = relationship(back_populates="session", cascade="all, delete-orphan")
    runs: Mapped[list["AgentOrchestrationRun"]] = relationship(back_populates="session")


class AgentChatMessage(Base):
    __tablename__ = "agent_chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_chat_sessions.id"), nullable=False)
    sender_type: Mapped[str] = mapped_column(String(30), nullable=False)
    sender_role: Mapped[str] = mapped_column(String(50), nullable=False)
    message_text: Mapped[str] = mapped_column(String(6000), nullable=False)
    message_format: Mapped[str] = mapped_column(String(30), nullable=False, default="PLAIN_TEXT")
    generation_mode: Mapped[str] = mapped_column(String(40), nullable=False)
    safety_status: Mapped[str] = mapped_column(String(30), nullable=False, default="NOT_APPLICABLE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)

    session: Mapped[AgentChatSession] = relationship(back_populates="messages")


class AgentOrchestrationRun(Base):
    __tablename__ = "agent_orchestration_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_cases.id"), nullable=False)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_chat_sessions.id"), nullable=False)
    trigger_message_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_chat_messages.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    stage_mode: Mapped[str] = mapped_column(String(40), nullable=False)
    orchestrator_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="DETERMINISTIC_STAGE_1")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    summary: Mapped[str] = mapped_column(String(3000), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000))
    tools_planned: Mapped[Optional[dict]] = mapped_column(JSON)
    tools_used: Mapped[Optional[dict]] = mapped_column(JSON)
    actions_proposed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    actions_executed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    case: Mapped[AgentCase] = relationship(back_populates="runs")
    session: Mapped[AgentChatSession] = relationship(back_populates="runs")
    evidence: Mapped[list["AgentEvidenceItem"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class AgentEvidenceItem(Base):
    __tablename__ = "agent_evidence_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_cases.id"), nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_orchestration_runs.id"), nullable=False)
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid(as_uuid=True))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(String(1500), nullable=False)
    payload_json: Mapped[Optional[dict]] = mapped_column(JSON)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    relevance_score: Mapped[float] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    case: Mapped[AgentCase] = relationship(back_populates="evidence")
    run: Mapped[AgentOrchestrationRun] = relationship(back_populates="evidence")


class AgentActionProposal(Base):
    __tablename__ = "agent_action_proposals"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    proposal_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_cases.id"), nullable=False)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agent_orchestration_runs.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    action_type: Mapped[str] = mapped_column(String(60), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="PROPOSED")
    requires_approval: Mapped[bool] = mapped_column(nullable=False, default=True)
    approval_status: Mapped[str] = mapped_column(String(30), nullable=False, default="PENDING")
    execution_status: Mapped[str] = mapped_column(String(40), nullable=False, default="DISABLED_IN_STAGE_1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    case: Mapped[AgentCase] = relationship(back_populates="proposals")
