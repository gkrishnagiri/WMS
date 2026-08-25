"""Add Stage 2 approval-gated agent action state and audit tables."""

from alembic import op
import sqlalchemy as sa


revision = "0016_stage2_approval_gated"
down_revision = "0015_agent_contextual_handoff"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for name, column in (
        ("approved_by_role", sa.String(80)),
        ("approved_at", sa.DateTime(timezone=True)),
        ("rejected_by_role", sa.String(80)),
        ("rejected_at", sa.DateTime(timezone=True)),
        ("approval_comment", sa.String(2000)),
        ("execution_started_at", sa.DateTime(timezone=True)),
        ("execution_completed_at", sa.DateTime(timezone=True)),
        ("execution_error", sa.String(2000)),
        ("execution_result_json", sa.JSON()),
        ("execution_mode", sa.String(40)),
        ("safe_action_code", sa.String(80)),
        ("idempotency_key", sa.String(200)),
        ("action_payload_json", sa.JSON()),
    ):
        op.add_column("agent_action_proposals", sa.Column(name, column, nullable=True))
    op.create_unique_constraint("uq_agent_action_proposals_idempotency", "agent_action_proposals", ["idempotency_key"])
    op.execute("UPDATE agent_action_proposals SET execution_mode = 'STAGE_1_DISABLED' WHERE execution_mode IS NULL")

    op.create_table(
        "agent_action_executions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("execution_id", sa.String(100), unique=True, nullable=False),
        sa.Column("proposal_id", sa.Uuid(), sa.ForeignKey("agent_action_proposals.id"), nullable=False),
        sa.Column("case_id", sa.Uuid(), sa.ForeignKey("agent_cases.id"), nullable=False),
        sa.Column("run_id", sa.Uuid(), sa.ForeignKey("agent_orchestration_runs.id"), nullable=False),
        sa.Column("safe_action_code", sa.String(80), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("requested_by_role", sa.String(80), nullable=False),
        sa.Column("approved_by_role", sa.String(80)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("result_summary", sa.String(2000)),
        sa.Column("result_json", sa.JSON()),
        sa.Column("error_message", sa.String(2000)),
        sa.Column("idempotency_key", sa.String(200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("idempotency_key", name="uq_agent_action_execution_idempotency"),
    )
    op.create_table(
        "agent_action_audit_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("event_id", sa.String(100), unique=True, nullable=False),
        sa.Column("proposal_id", sa.Uuid(), sa.ForeignKey("agent_action_proposals.id"), nullable=False),
        sa.Column("case_id", sa.Uuid(), sa.ForeignKey("agent_cases.id"), nullable=False),
        sa.Column("run_id", sa.Uuid(), sa.ForeignKey("agent_orchestration_runs.id")),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("actor_role", sa.String(80), nullable=False),
        sa.Column("comment", sa.String(2000)),
        sa.Column("metadata_json", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("agent_action_audit_events")
    op.drop_table("agent_action_executions")
    op.drop_constraint("uq_agent_action_proposals_idempotency", "agent_action_proposals", type_="unique")
    for name in ("action_payload_json", "idempotency_key", "safe_action_code", "execution_mode", "execution_result_json", "execution_error", "execution_completed_at", "execution_started_at", "approval_comment", "rejected_at", "rejected_by_role", "approved_at", "approved_by_role"):
        op.drop_column("agent_action_proposals", name)
