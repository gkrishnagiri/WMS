"""SQLAlchemy engine, session factory, and connectivity management."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Generator

from fastapi import Request
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings
from app.core.opentelemetry import start_span


def current_git_commit() -> str:
    repository_root = Path(__file__).resolve().parents[3]
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository_root,
            capture_output=True,
            text=True,
            check=True,
            timeout=1,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


class DatabaseManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.engine: Engine | None = None
        self.session_factory: sessionmaker[Session] | None = None
        self.git_commit = current_git_commit()

    def initialize(self) -> None:
        self.engine = create_engine(
            self.settings.database_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 1},
        )
        self.session_factory = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def check_connection(self) -> bool:
        if self.engine is None:
            return False
        with start_span("PostgreSQL connectivity check", **{"db.system": "postgresql", "db.operation": "SELECT 1"}) as span:
            try:
                with self.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
                if span is not None:
                    span.set_attribute("eos.check.status", "healthy")
                return True
            except Exception as error:
                if span is not None:
                    span.record_exception(error)
                    span.set_attribute("eos.check.status", "unhealthy")
                return False

    def dispose(self) -> None:
        if self.engine is not None:
            self.engine.dispose()


def get_db(request: Request) -> Generator[Session, None, None]:
    factory = request.app.state.database.session_factory
    if factory is None:
        raise RuntimeError("Database session factory has not been initialized")
    db = factory()
    try:
        yield db
    finally:
        db.close()
