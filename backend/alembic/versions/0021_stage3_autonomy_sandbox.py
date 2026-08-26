"""Add the bounded local Stage 3 autonomy sandbox audit tables."""

from alembic import op
import sqlalchemy as sa

revision = "0021_stage3_autonomy_sandbox"
down_revision = "0020_dynamic_model_catalog"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stage3_autonomous_runs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("run_id", sa.String(120), nullable=False),
        sa.Column("case_id", sa.Uuid(), nullable=True),
        sa.Column("scenario_run_id", sa.Uuid(), nullable=True),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column("source_object_type", sa.String(80)), sa.Column("source_object_id", sa.String(120)),
        sa.Column("status", sa.String(40), nullable=False), sa.Column("mode", sa.String(50), nullable=False),
        sa.Column("profile_code", sa.String(80), nullable=False), sa.Column("dry_run_required", sa.Boolean(), nullable=False),
        sa.Column("dry_run_completed", sa.Boolean(), nullable=False), sa.Column("real_model_requested", sa.Boolean(), nullable=False),
        sa.Column("real_model_used", sa.Boolean(), nullable=False), sa.Column("provider_code", sa.String(80)), sa.Column("model_code", sa.String(120)),
        sa.Column("max_steps", sa.Integer(), nullable=False), sa.Column("steps_completed", sa.Integer(), nullable=False),
        sa.Column("max_duration_seconds", sa.Integer(), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)), sa.Column("stopped_at", sa.DateTime(timezone=True)), sa.Column("stop_reason", sa.String(2000)),
        sa.Column("max_estimated_cost", sa.Float(), nullable=False), sa.Column("estimated_total_cost", sa.Float(), nullable=False),
        sa.Column("total_input_tokens", sa.Integer(), nullable=False), sa.Column("total_completion_tokens", sa.Integer(), nullable=False), sa.Column("total_tokens", sa.Integer(), nullable=False),
        sa.Column("created_by_role", sa.String(80), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["agent_cases.id"]), sa.ForeignKeyConstraint(["scenario_run_id"], ["demo_scenario_runs.id"]), sa.ForeignKeyConstraint(["session_id"], ["agent_chat_sessions.id"]),
        sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("run_id"),
    )
    op.create_index("ix_stage3_runs_status", "stage3_autonomous_runs", ["status"])
    op.create_table(
        "stage3_autonomous_steps",
        sa.Column("id", sa.Uuid(), nullable=False), sa.Column("step_id", sa.String(120), nullable=False), sa.Column("run_id", sa.Uuid(), nullable=False), sa.Column("step_number", sa.Integer(), nullable=False), sa.Column("status", sa.String(40), nullable=False),
        sa.Column("decision_type", sa.String(80)), sa.Column("decision_summary", sa.String(2000)), sa.Column("selected_action_code", sa.String(100)), sa.Column("proposal_id", sa.Uuid()), sa.Column("execution_id", sa.Uuid()), sa.Column("guardrail_status", sa.String(40)), sa.Column("guardrail_reason", sa.String(2000)),
        sa.Column("input_tokens", sa.Integer(), nullable=False), sa.Column("completion_tokens", sa.Integer(), nullable=False), sa.Column("total_tokens", sa.Integer(), nullable=False), sa.Column("estimated_cost", sa.Float(), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True)), sa.Column("completed_at", sa.DateTime(timezone=True)), sa.Column("error_message", sa.String(2000)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["stage3_autonomous_runs.id"]), sa.ForeignKeyConstraint(["proposal_id"], ["agent_action_proposals.id"]), sa.ForeignKeyConstraint(["execution_id"], ["agent_action_executions.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("step_id"), sa.UniqueConstraint("run_id", "step_number", name="uq_stage3_steps_run_number"),
    )
    op.create_table(
        "stage3_autonomous_events",
        sa.Column("id", sa.Uuid(), nullable=False), sa.Column("event_id", sa.String(120), nullable=False), sa.Column("run_id", sa.Uuid(), nullable=False), sa.Column("step_id", sa.Uuid()), sa.Column("event_type", sa.String(80), nullable=False), sa.Column("event_title", sa.String(240), nullable=False), sa.Column("event_description", sa.String(2000), nullable=False), sa.Column("severity", sa.String(20), nullable=False), sa.Column("metadata_json", sa.JSON()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["stage3_autonomous_runs.id"]), sa.ForeignKeyConstraint(["step_id"], ["stage3_autonomous_steps.id"]), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("event_id"),
    )
    op.create_table(
        "stage3_autonomy_controls",
        sa.Column("id", sa.Uuid(), nullable=False), sa.Column("control_key", sa.String(80), nullable=False), sa.Column("kill_switch_enabled", sa.Boolean(), nullable=False), sa.Column("requested_by_role", sa.String(80)), sa.Column("reason", sa.String(2000)), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("control_key"),
    )


def downgrade() -> None:
    op.drop_table("stage3_autonomy_controls")
    op.drop_table("stage3_autonomous_events")
    op.drop_table("stage3_autonomous_steps")
    op.drop_index("ix_stage3_runs_status", table_name="stage3_autonomous_runs")
    op.drop_table("stage3_autonomous_runs")
