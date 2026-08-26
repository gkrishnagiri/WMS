from datetime import date
from pydantic import BaseModel, Field, field_validator


class PricingUpdateRequest(BaseModel):
    currency: str = Field(default="USD", min_length=3, max_length=10)
    input_cost_per_million_tokens: float = Field(ge=0)
    completion_cost_per_million_tokens: float = Field(ge=0)
    cached_input_cost_per_million_tokens: float | None = Field(default=None, ge=0)
    reasoning_cost_per_million_tokens: float | None = Field(default=None, ge=0)
    pricing_source_note: str = Field(default="Local EOS pricing assumption; verify before real use.", max_length=1000)
    pricing_effective_from: date


class ModelCreateRequest(BaseModel):
    model_code: str = Field(min_length=1, max_length=120)
    external_model_name: str = Field(min_length=1, max_length=160)
    display_name: str | None = Field(default=None, max_length=160)
    enabled: bool = False
    input_cost_per_million_tokens: float = Field(default=0, ge=0)
    completion_cost_per_million_tokens: float = Field(default=0, ge=0)
    cached_input_cost_per_million_tokens: float | None = Field(default=None, ge=0)
    reasoning_cost_per_million_tokens: float | None = Field(default=None, ge=0)
    pricing_source_note: str = Field(default="User-editable local pricing assumption; verify before real use.", max_length=1000)
    pricing_effective_from: date = Field(default_factory=date.today)

    @field_validator("model_code")
    @classmethod
    def normalize_model_code(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized.replace("_", "").replace("-", "").replace(".", "").isalnum():
            raise ValueError("model_code may contain only letters, numbers, underscore, hyphen, and period")
        return normalized

    @field_validator("external_model_name")
    @classmethod
    def normalize_external_name(cls, value: str) -> str:
        return value.strip()


class SmokeTestRequest(BaseModel):
    model_code: str = Field(min_length=1, max_length=120)
    message_text: str = Field(min_length=1, max_length=24000)
    max_output_tokens: int = Field(default=100, ge=1, le=300)
    allow_real_model: bool = False
    acknowledge_cost: bool = False
    allow_missing_pricing: bool = False
