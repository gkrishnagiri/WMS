"""Request and response schemas for deterministic agent chat."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AgentCaseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    case_type: str | None = None
    priority: str = "P3"
    source: str = "CHAT"
    created_by_role: str = "SERVICE_ENGINEER"
    linked_ams_ticket_id: UUID | None = None
    linked_user_report_id: UUID | None = None
    linked_alert_event_id: UUID | None = None
    linked_batch_run_id: UUID | None = None
    linked_diagnostic_case_id: UUID | None = None
    linked_order_id: UUID | None = None
    linked_shipment_id: UUID | None = None
    linked_inventory_item_id: UUID | None = None


class AgentHandoffRequest(BaseModel):
    initial_message: str = Field(default="Investigate this issue and summarize likely next steps.", min_length=1, max_length=6000)
    reuse_existing: bool = True
    use_real_model: bool = False
    provider_code: str | None = Field(default=None, max_length=100)
    model_code: str | None = Field(default=None, max_length=120)
    dry_run: bool = False


class AgentSessionCreate(BaseModel):
    case_id: UUID | None = None
    audience: str = "SERVICE_ENGINEER"
    title: str = Field(default="Agent support session", max_length=200)
    started_by_role: str = "SERVICE_ENGINEER"
    experience: str = "agentic"


class AgentMessageCreate(BaseModel):
    message_text: str = Field(min_length=1, max_length=6000)
    sender_type: str = "SERVICE_ENGINEER"
    sender_role: str | None = None
    use_real_model: bool = False
    provider_code: str | None = Field(default=None, max_length=100)
    model_code: str | None = Field(default=None, max_length=120)
    dry_run: bool = False


class AgentIntakeRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    initial_message: str = Field(min_length=1, max_length=6000)
    priority: str = "P3"
    created_by_role: str | None = None
    linked_ams_ticket_id: UUID | None = None
    linked_user_report_id: UUID | None = None
    linked_alert_event_id: UUID | None = None
    linked_batch_run_id: UUID | None = None
    linked_diagnostic_case_id: UUID | None = None


class AgentCaseResponse(BaseModel):
    id: UUID
    case_id: str
    case_type: str
    title: str
    description: str
    status: str
    priority: str
    source: str
    stage_mode: str
    created_by_role: str
    linked_ams_ticket_id: UUID | None
    linked_user_report_id: UUID | None
    linked_alert_event_id: UUID | None
    linked_batch_run_id: UUID | None
    linked_diagnostic_case_id: UUID | None
    linked_order_id: UUID | None
    linked_shipment_id: UUID | None
    linked_inventory_item_id: UUID | None
    source_object_type: str | None
    source_object_id: UUID | None
    source_object_display: str | None
    source_object_url: str | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None

    model_config = {"from_attributes": True}


class AgentHandoffResponse(BaseModel):
    case_id: str
    case_record_id: UUID
    session_id: str
    session_record_id: UUID
    source_object_type: str
    source_object_id: UUID
    source_object_display: str
    source_object_url: str | None
    created_new_case: bool
    created_new_session: bool
    reused_existing_case: bool
    stage_mode: str
    generation_mode: str
    actions_executed: int
    agent_chat_url: str
    message: str
    session: dict


class AgentChatMessageResponse(BaseModel):
    id: UUID
    message_id: str
    session_id: UUID
    sender_type: str
    sender_role: str
    message_text: str
    message_format: str
    generation_mode: str
    safety_status: str
    created_at: datetime
    metadata_json: dict | None

    model_config = {"from_attributes": True}


class AgentEvidenceResponse(BaseModel):
    id: UUID
    evidence_id: str
    case_id: UUID
    run_id: UUID
    evidence_type: str
    source_type: str
    source_id: UUID | None
    title: str
    summary: str
    payload_json: dict | None
    source_url: str | None
    relevance_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentRunResponse(BaseModel):
    id: UUID
    run_id: str
    case_id: UUID
    session_id: UUID
    trigger_message_id: UUID
    status: str
    stage_mode: str
    orchestrator_mode: str
    started_at: datetime
    completed_at: datetime | None
    summary: str
    error_message: str | None
    tools_planned: dict | None
    tools_used: dict | None
    actions_proposed: int
    actions_executed: int

    model_config = {"from_attributes": True}


class AgentActionProposalResponse(BaseModel):
    id: UUID
    proposal_id: str
    case_id: UUID
    run_id: UUID
    title: str
    description: str
    action_type: str
    risk_level: str
    status: str
    requires_approval: bool
    approval_status: str
    execution_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentChatSessionResponse(BaseModel):
    id: UUID
    session_id: str
    case_id: UUID
    audience: str
    title: str
    status: str
    started_by_role: str
    experience: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    case: AgentCaseResponse | None = None
    messages: list[AgentChatMessageResponse] = Field(default_factory=list)
    evidence: list[AgentEvidenceResponse] = Field(default_factory=list)
    orchestration_runs: list[AgentRunResponse] = Field(default_factory=list)
    action_proposals: list[AgentActionProposalResponse] = Field(default_factory=list)
