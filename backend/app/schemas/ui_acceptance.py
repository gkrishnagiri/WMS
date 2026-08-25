"""Request schemas for manual UI acceptance records."""

from pydantic import BaseModel, Field


class StartUiTestRunRequest(BaseModel):
    run_title: str = Field(default="Manual EOS UI Acceptance Run", min_length=1, max_length=240)
    tester_role: str = Field(default="DEMO_TESTER", min_length=1, max_length=100)
    suite_codes: list[str] = Field(default_factory=list)


class StepResultRequest(BaseModel):
    suite_code: str = Field(min_length=1, max_length=100)
    case_code: str = Field(min_length=1, max_length=120)
    step_code: str = Field(min_length=1, max_length=140)
    status: str = Field(min_length=1, max_length=30)
    observed_result: str | None = Field(default=None, max_length=4000)
    evidence_note: str | None = Field(default=None, max_length=4000)
    screenshot_reference: str | None = Field(default=None, max_length=1000)
    defect_note: str | None = Field(default=None, max_length=4000)
    tested_by_role: str = Field(default="DEMO_TESTER", min_length=1, max_length=100)


class RunSummaryRequest(BaseModel):
    summary: str | None = Field(default=None, max_length=4000)
