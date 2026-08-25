"""Request schemas for the local EOS demo readiness surface."""

from pydantic import BaseModel, Field


class DemoResetRequest(BaseModel):
    profile: str = Field(default="SOFT_RESET", max_length=60)
    reset_reason: str = Field(default="Presenter reset the local EOS demo.", max_length=1500)
    confirmation: str | None = Field(default=None, max_length=100)


class PrepareShowcaseRequest(BaseModel):
    profile: str = Field(default="SHOWCASE_RESET", max_length=60)
    create_prepared_runs: bool = False
    created_by_role: str = Field(default="DEMO_PRESENTER", max_length=80)
