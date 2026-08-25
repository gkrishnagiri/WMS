"""Add guided demo scenario orchestration tables."""

from alembic import op
import sqlalchemy as sa


revision = "0017_demo_scenario_orch"
down_revision = "0016_stage2_approval_gated"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "demo_scenarios",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("scenario_code", sa.String(80), unique=True, nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("business_value", sa.String(1000), nullable=False),
        sa.Column("default_experience", sa.String(40), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "demo_scenario_runs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("run_id", sa.String(100), unique=True, nullable=False),
        sa.Column("scenario_code", sa.String(80), sa.ForeignKey("demo_scenarios.scenario_code"), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("current_step_code", sa.String(100)),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("reset_at", sa.DateTime(timezone=True)),
        sa.Column("created_by_role", sa.String(80), nullable=False),
        sa.Column("summary", sa.String(2000), nullable=False),
        sa.Column("outcome_summary", sa.String(2000)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "demo_scenario_steps",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("run_id", sa.Uuid(), sa.ForeignKey("demo_scenario_runs.id"), nullable=False),
        sa.Column("step_code", sa.String(100), nullable=False),
        sa.Column("step_title", sa.String(180), nullable=False),
        sa.Column("step_description", sa.String(1000), nullable=False),
        sa.Column("presenter_instruction", sa.String(1000), nullable=False),
        sa.Column("expected_result", sa.String(1000), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("target_url", sa.String(500)),
        sa.Column("target_object_type", sa.String(80)),
        sa.Column("target_object_id", sa.Uuid()),
        sa.Column("instructions", sa.String(1500)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("run_id", "step_code", name="uq_demo_scenario_steps_code"),
    )
    op.create_table(
        "demo_scenario_artifacts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("run_id", sa.Uuid(), sa.ForeignKey("demo_scenario_runs.id"), nullable=False),
        sa.Column("artifact_type", sa.String(80), nullable=False),
        sa.Column("artifact_id", sa.Uuid(), nullable=False),
        sa.Column("artifact_display", sa.String(240), nullable=False),
        sa.Column("artifact_url", sa.String(500)),
        sa.Column("metadata_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("run_id", "artifact_type", "artifact_id", name="uq_demo_scenario_artifacts_link"),
    )
    op.create_table(
        "demo_scenario_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("run_id", sa.Uuid(), sa.ForeignKey("demo_scenario_runs.id"), nullable=False),
        sa.Column("event_type", sa.String(80), nullable=False),
        sa.Column("event_title", sa.String(240), nullable=False),
        sa.Column("event_description", sa.String(1500), nullable=False),
        sa.Column("event_timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("source_type", sa.String(80)),
        sa.Column("source_id", sa.Uuid()),
        sa.Column("metadata_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("demo_scenario_events")
    op.drop_table("demo_scenario_artifacts")
    op.drop_table("demo_scenario_steps")
    op.drop_table("demo_scenario_runs")
    op.drop_table("demo_scenarios")
