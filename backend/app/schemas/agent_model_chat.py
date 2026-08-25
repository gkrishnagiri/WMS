from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentModelChatRequest(BaseModel):
    message_text: str = Field(min_length=1, max_length=24000)
    use_real_model: bool = False
    provider_code: str | None = Field(default=None, max_length=100)
    model_code: str | None = Field(default=None, max_length=120)
    task_type: str = Field(default="AGENT_STAGE_1_CHAT", max_length=60)
    dry_run: bool = False


class AgentModelContextRequest(BaseModel):
    message_text: str = Field(min_length=1, max_length=24000)
    task_type: str = Field(default="AGENT_STAGE_1_CHAT", max_length=60)


class AgentModelStatusResponse(BaseModel):
    real_model_enabled: bool
    provider_code: str
    model_code: str
    default_model: str
    provider_configured: bool
    model_configured: bool
    api_key_present: bool
    provider_enabled: bool
    model_enabled: bool
    safe_to_invoke: bool
    reason: str
    allowed_task_types: list[str]
    max_context_items: int
    max_input_chars: int
    daily_usage: dict[str, Any]
    stage_mode: str


class AgentModelContextResponse(BaseModel):
    session_id: str
    task_type: str
    context_package: dict[str, Any]
    validation_issues: list[str] = Field(default_factory=list)
    model_call_made: bool = False


class AgentModelAskResponse(BaseModel):
    session_id: str
    answer: str
    generation_mode: str
    safety_status: str
    fallback_used: bool
    invocation_id: str | None
    invocation_number: str | None
    metadata: dict[str, Any]
    actions_executed: int = 0
