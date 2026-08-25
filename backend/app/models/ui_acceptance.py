"""Manual, browser-first UI acceptance testing records."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.warehouse import TimestampMixin


class UiTestSuite(TimestampMixin, Base):
    __tablename__ = "ui_test_suites"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suite_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(String(1500), nullable=False)
    experience: Mapped[str] = mapped_column(String(200), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_enabled: Mapped[bool] = mapped_column(nullable=False, default=True)

    cases: Mapped[list["UiTestCase"]] = relationship(back_populates="suite", cascade="all, delete-orphan")


class UiTestCase(TimestampMixin, Base):
    __tablename__ = "ui_test_cases"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_code: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    suite_code: Mapped[str] = mapped_column(ForeignKey("ui_test_suites.suite_code"), nullable=False)
    title: Mapped[str] = mapped_column(String(220), nullable=False)
    description: Mapped[str] = mapped_column(String(1500), nullable=False)
    preconditions: Mapped[str] = mapped_column(String(1500), nullable=False)
    expected_outcome: Mapped[str] = mapped_column(String(1500), nullable=False)
    primary_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_enabled: Mapped[bool] = mapped_column(nullable=False, default=True)

    suite: Mapped[UiTestSuite] = relationship(back_populates="cases")
    steps: Mapped[list["UiTestStep"]] = relationship(back_populates="case", cascade="all, delete-orphan")


class UiTestStep(TimestampMixin, Base):
    __tablename__ = "ui_test_steps"
    __table_args__ = (UniqueConstraint("case_code", "step_code", name="uq_ui_test_steps_case_code"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    step_code: Mapped[str] = mapped_column(String(140), nullable=False)
    case_code: Mapped[str] = mapped_column(ForeignKey("ui_test_cases.case_code"), nullable=False)
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    instruction: Mapped[str] = mapped_column(String(1500), nullable=False)
    target_url: Mapped[str] = mapped_column(String(500), nullable=False)
    what_to_click: Mapped[str] = mapped_column(String(1000), nullable=False)
    expected_result: Mapped[str] = mapped_column(String(1500), nullable=False)
    evidence_to_capture: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_mutating_step: Mapped[bool] = mapped_column(nullable=False, default=False)
    safety_note: Mapped[str] = mapped_column(String(1000), nullable=False)

    case: Mapped[UiTestCase] = relationship(back_populates="steps")


class UiTestRun(TimestampMixin, Base):
    __tablename__ = "ui_test_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    run_title: Mapped[str] = mapped_column(String(240), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="IN_PROGRESS")
    tester_role: Mapped[str] = mapped_column(String(100), nullable=False)
    suite_codes: Mapped[Optional[list]] = mapped_column(JSON)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    summary: Mapped[Optional[str]] = mapped_column(String(4000))

    step_results: Mapped[list["UiTestStepResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")
    events: Mapped[list["UiTestRunEvent"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class UiTestStepResult(TimestampMixin, Base):
    __tablename__ = "ui_test_step_results"
    __table_args__ = (UniqueConstraint("run_id", "suite_code", "case_code", "step_code", name="uq_ui_test_result_step"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ui_test_runs.id"), nullable=False)
    suite_code: Mapped[str] = mapped_column(String(100), nullable=False)
    case_code: Mapped[str] = mapped_column(String(120), nullable=False)
    step_code: Mapped[str] = mapped_column(String(140), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="NOT_TESTED")
    observed_result: Mapped[Optional[str]] = mapped_column(String(4000))
    evidence_note: Mapped[Optional[str]] = mapped_column(String(4000))
    screenshot_reference: Mapped[Optional[str]] = mapped_column(String(1000))
    defect_note: Mapped[Optional[str]] = mapped_column(String(4000))
    tested_by_role: Mapped[str] = mapped_column(String(100), nullable=False)
    tested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    run: Mapped[UiTestRun] = relationship(back_populates="step_results")


class UiTestRunEvent(Base):
    __tablename__ = "ui_test_run_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ui_test_runs.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(60), nullable=False)
    event_title: Mapped[str] = mapped_column(String(240), nullable=False)
    event_description: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON)

    run: Mapped[UiTestRun] = relationship(back_populates="events")
