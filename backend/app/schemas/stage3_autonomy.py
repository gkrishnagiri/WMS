"""API contracts for the local Stage 3 autonomous sandbox."""

from pydantic import BaseModel, Field


class SandboxRunCreateRequest(BaseModel):
    case_id: str | None = None
    scenario_run_id: str | None = None
    profile_code: str = Field(default="DRY_RUN_ONLY", min_length=1, max_length=80)
    created_by_role: str = Field(default="DEMO_PRESENTER", min_length=1, max_length=80)
    use_real_model: bool = False
    provider_code: str | None = "OPENAI_RESPONSES"
    model_code: str | None = None
    max_steps: int = Field(default=3, ge=1, le=100)
    max_estimated_cost: float = Field(default=0.25, ge=0)
    acknowledge_sandbox_only: bool = False


class SandboxDryRunRequest(BaseModel):
    requested_by_role: str = Field(default="DEMO_PRESENTER", min_length=1, max_length=80)


class SandboxStartRequest(BaseModel):
    requested_by_role: str = Field(default="DEMO_PRESENTER", min_length=1, max_length=80)
    acknowledge_autonomous_sandbox: bool = False
    acknowledge_no_external_systems: bool = False
    acknowledge_cost: bool = False


class SandboxControlRequest(BaseModel):
    requested_by_role: str = Field(default="DEMO_PRESENTER", min_length=1, max_length=80)
    reason: str = Field(default="Presenter control action.", max_length=2000)


class SandboxKillSwitchRequest(SandboxControlRequest):
    enabled: bool
