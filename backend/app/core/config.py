"""Central application configuration."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    backend_cors_origins: str = "http://localhost:4001,http://127.0.0.1:4001"

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
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
