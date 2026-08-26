"""Central application configuration."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


LOCAL_FRONTEND_CORS_ORIGINS = (
    "http://localhost:4001",
    "http://127.0.0.1:4001",
    "http://localhost:4011",
    "http://127.0.0.1:4011",
    "http://localhost:4012",
    "http://127.0.0.1:4012",
    "http://localhost:4013",
    "http://127.0.0.1:4013",
    "http://localhost:4014",
    "http://127.0.0.1:4014",
    "http://localhost:4015",
    "http://127.0.0.1:4015",
)


class Settings(BaseSettings):
    """Environment-backed settings for the EOS API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Enterprise Operations Suite"
    platform_name: str = "AI-Native AMS Research Platform"
    app_version: str = "0.1.0"
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    app_host: str = "0.0.0.0"
    app_port: int = 8050
    backend_cors_origins: str = ",".join(LOCAL_FRONTEND_CORS_ORIGINS)

    database_host: str = "localhost"
    database_port: int = 15432
    database_name: str = "wms"
    database_user: str = "wms"
    database_password: str = "change-me"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str | None = None

    log_level: str = "INFO"
    request_id_header: str = "X-Request-ID"
    runtime_observability_enabled: bool = True
    runtime_observability_capture_requests: bool = True
    runtime_observability_capture_health: bool = False
    runtime_observability_slow_request_ms: int = 1000
    runtime_observability_body_capture_chars: int = 0
    otel_enabled: bool = False
    otel_service_name: str = "eos-backend"
    otel_service_namespace: str = "enterprise-operations-suite"
    otel_service_version: str = "0.1.0"
    otel_environment: str = "development"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_exporter_otlp_protocol: str = "grpc"
    otel_traces_enabled: bool = True
    otel_logs_enabled: bool = True
    otel_metrics_enabled: bool = True
    otel_sample_ratio: float = 1.0
    otel_collector_health_url: str = "http://localhost:13133"
    otel_prometheus_url: str = "http://localhost:9090"
    otel_grafana_url: str = "http://localhost:3001"
    otel_tempo_url: str = "http://localhost:3200"
    otel_loki_url: str = "http://localhost:3100"

    # Real-model support is deliberately opt-in. The API key is read from the
    # environment only and is never persisted or returned by an API endpoint.
    real_model_enabled: bool = False
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_org_id: str | None = None
    openai_project_id: str | None = None
    openai_default_model: str = "gpt-5.4-mini"
    openai_request_timeout_seconds: int = 30
    openai_max_output_tokens: int = 1200
    openai_reasoning_effort: str = "low"
    openai_store_responses: bool = False
    real_model_allowed_task_types: str = "AGENT_STAGE_1_CHAT,AGENT_INVESTIGATION_QA,AGENT_EVIDENCE_SUMMARY,MODEL_SMOKE_TEST"
    real_model_max_input_chars: int = 24000
    real_model_max_context_items: int = 40
    real_model_max_daily_invocations: int = 100
    real_model_max_daily_estimated_cost: float = 10.0
    real_model_max_single_call_estimated_cost: float = 1.0
    real_model_max_input_tokens: int = 32000
    real_model_max_output_tokens: int = 1200
    real_model_stage1_only: bool = True

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.database_port}/{self.database_name}"
        )

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/0"
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def cors_origins(self) -> list[str]:
        configured_origins = [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]
        return list(dict.fromkeys([*configured_origins, *LOCAL_FRONTEND_CORS_ORIGINS]))


@lru_cache
def get_settings() -> Settings:
    return Settings()
