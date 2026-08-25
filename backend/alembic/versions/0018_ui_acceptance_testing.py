"""Add manual UI acceptance testing catalog and evidence tables."""

from alembic import op
import sqlalchemy as sa


revision = "0018_ui_acceptance_testing"
down_revision = "0017_demo_scenario_orch"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("ui_test_suites",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("suite_code", sa.String(100), unique=True, nullable=False),
        sa.Column("title", sa.String(180), nullable=False), sa.Column("description", sa.String(1500), nullable=False),
        sa.Column("experience", sa.String(200), nullable=False), sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("ui_test_cases",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("case_code", sa.String(120), unique=True, nullable=False),
        sa.Column("suite_code", sa.String(100), sa.ForeignKey("ui_test_suites.suite_code"), nullable=False),
        sa.Column("title", sa.String(220), nullable=False), sa.Column("description", sa.String(1500), nullable=False),
        sa.Column("preconditions", sa.String(1500), nullable=False), sa.Column("expected_outcome", sa.String(1500), nullable=False),
        sa.Column("primary_url", sa.String(500), nullable=False), sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("ui_test_steps",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("step_code", sa.String(140), nullable=False),
        sa.Column("case_code", sa.String(120), sa.ForeignKey("ui_test_cases.case_code"), nullable=False), sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("instruction", sa.String(1500), nullable=False), sa.Column("target_url", sa.String(500), nullable=False), sa.Column("what_to_click", sa.String(1000), nullable=False),
        sa.Column("expected_result", sa.String(1500), nullable=False), sa.Column("evidence_to_capture", sa.String(1000), nullable=False), sa.Column("is_mutating_step", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("safety_note", sa.String(1000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("case_code", "step_code", name="uq_ui_test_steps_case_code"))
    op.create_table("ui_test_runs",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("run_id", sa.String(120), unique=True, nullable=False), sa.Column("run_title", sa.String(240), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("tester_role", sa.String(100), nullable=False), sa.Column("suite_codes", sa.JSON()), sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("completed_at", sa.DateTime(timezone=True)), sa.Column("summary", sa.String(4000)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("ui_test_step_results",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("run_id", sa.Uuid(), sa.ForeignKey("ui_test_runs.id"), nullable=False), sa.Column("suite_code", sa.String(100), nullable=False), sa.Column("case_code", sa.String(120), nullable=False), sa.Column("step_code", sa.String(140), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("observed_result", sa.String(4000)), sa.Column("evidence_note", sa.String(4000)), sa.Column("screenshot_reference", sa.String(1000)), sa.Column("defect_note", sa.String(4000)), sa.Column("tested_by_role", sa.String(100), nullable=False), sa.Column("tested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("run_id", "suite_code", "case_code", "step_code", name="uq_ui_test_result_step"))
    op.create_table("ui_test_run_events",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("run_id", sa.Uuid(), sa.ForeignKey("ui_test_runs.id"), nullable=False), sa.Column("event_type", sa.String(60), nullable=False), sa.Column("event_title", sa.String(240), nullable=False), sa.Column("event_description", sa.String(2000), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("metadata_json", sa.JSON()))


def downgrade() -> None:
    op.drop_table("ui_test_run_events")
    op.drop_table("ui_test_step_results")
    op.drop_table("ui_test_runs")
    op.drop_table("ui_test_steps")
    op.drop_table("ui_test_cases")
    op.drop_table("ui_test_suites")
