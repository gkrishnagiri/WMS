"""API contracts for Stage 2 approval-gated local agent actions."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ActionApprovalRequest(BaseModel):
    approved_by_role: str = Field(min_length=1, max_length=80)
    approval_comment: str | None = Field(default=None, max_length=2000)
    execute_after_approval: bool = False


class ActionRejectionRequest(BaseModel):
    rejected_by_role: str = Field(min_length=1, max_length=80)
    rejection_comment: str | None = Field(default=None, max_length=2000)


class ActionExecutionRequest(BaseModel):
    requested_by_role: str = Field(min_length=1, max_length=80)
    execution_comment: str | None = Field(default=None, max_length=2000)


class ActionDryRunRequest(BaseModel):
    requested_by_role: str = Field(default="SERVICE_ENGINEER", min_length=1, max_length=80)


class AgentActionProposalResponse(BaseModel):
    id: UUID
    proposal_id: str
    case_id: UUID
    run_id: UUID
    title: str
    description: str
    action_type: str
    safe_action_code: str | None
    risk_level: str
    status: str
    requires_approval: bool
    approval_status: str
    approved_by_role: str | None
    approved_at: datetime | None
    rejected_by_role: str | None
    rejected_at: datetime | None
    approval_comment: str | None
    execution_status: str
    execution_mode: str
    execution_started_at: datetime | None
    execution_completed_at: datetime | None
    execution_error: str | None
    execution_result_json: dict | None
    idempotency_key: str | None
    action_payload_json: dict | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentActionExecutionResponse(BaseModel):
    id: UUID
    execution_id: str
    proposal_id: UUID
    case_id: UUID
    run_id: UUID
    safe_action_code: str
    status: str
    requested_by_role: str
    approved_by_role: str | None
    started_at: datetime | None
    completed_at: datetime | None
    result_summary: str | None
    result_json: dict | None
    error_message: str | None
    idempotency_key: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
