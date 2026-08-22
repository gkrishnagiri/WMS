"""Schemas for the deterministic governed support copilot."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CopilotSafeActionResponse(BaseModel):
    id: UUID
    action_code: str
    name: str
    description: str
    target_module: str
    action_type: str
    risk_level: str
    requires_human_approval: bool
    enabled: bool
    created_at: datetime
    updated_at: datetime


class CopilotSessionCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="Support engineer copilot investigation.", max_length=1500)
    primary_entity_type: str = Field(default="MANUAL", max_length=40)
    primary_entity_id: UUID | None = None
    primary_ticket_id: UUID | None = None
    severity: str = Field(default="MEDIUM", max_length=20)
    created_by: str = Field(default="support-engineer", max_length=120)
    build_context: bool = False
    generate_recommendations: bool = False


class CopilotAnalyzeRequest(BaseModel):
    entity_type: str = Field(max_length=40)
    entity_id: UUID | None = None
    title: str = Field(default="Analyze support artifact", max_length=200)


class CopilotContextResponse(BaseModel):
    id: UUID
    session_id: UUID
    snapshot_number: str
    source_entity_type: str
    source_entity_id: UUID | None
    summary: str
    impact_summary: str
    technical_summary: str
    business_summary: str
    timeline_summary: str
    evidence_summary: str
    related_entities: dict | None
    raw_context: dict | None
    created_by: str
    created_at: datetime


class CopilotRecommendationResponse(BaseModel):
    id: UUID
    session_id: UUID
    snapshot_id: UUID | None
    recommendation_type: str
    title: str
    details: str
    priority: str
    confidence_level: str
    rationale: str
    source_evidence: dict | None
    status: str
    created_at: datetime
    updated_at: datetime
    accepted_at: datetime | None
    dismissed_at: datetime | None


class CopilotActionPlanResponse(BaseModel):
    id: UUID
    session_id: UUID
    snapshot_id: UUID | None
    plan_number: str
    title: str
    summary: str
    status: str
    steps: list
    risk_level: str
    requires_human_approval: bool
    created_at: datetime
    updated_at: datetime
    approved_at: datetime | None
    completed_at: datetime | None


class CopilotMessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    message_type: str
    title: str
    content: str
    status: str
    target_entity_type: str | None
    target_entity_id: UUID | None
    created_by: str
    created_at: datetime
    updated_at: datetime


class CopilotActionEventResponse(BaseModel):
    id: UUID
    session_id: UUID
    action_code: str
    event_type: str
    target_entity_type: str | None
    target_entity_id: UUID | None
    from_status: str | None
    to_status: str | None
    message: str
    event_payload: dict | None
    created_by: str
    created_at: datetime


class CopilotSessionResponse(BaseModel):
    id: UUID
    session_number: str
    title: str
    description: str
    status: str
    primary_entity_type: str
    primary_entity_id: UUID | None
    primary_ticket_id: UUID | None
    severity: str
    confidence_level: str
    created_by: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    latest_context_snapshot: CopilotContextResponse | None = None
    recommendations: list[CopilotRecommendationResponse] = Field(default_factory=list)
    latest_action_plan: CopilotActionPlanResponse | None = None
    messages: list[CopilotMessageResponse] = Field(default_factory=list)
    action_events: list[CopilotActionEventResponse] = Field(default_factory=list)
    primary_entity_summary: str | None = None


class CopilotSummary(BaseModel):
    open_sessions: int
    recommendations_proposed: int
    recommendations_accepted: int
    action_plans_ready: int
    draft_messages: int
    safe_actions_enabled: int


class CopilotAnalyzeResponse(BaseModel):
    session: CopilotSessionResponse

