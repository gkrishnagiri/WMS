"""Add OpenAI model pricing and usage snapshots."""

from alembic import op
import sqlalchemy as sa

revision = "0019_openai_model_cost_metering"
down_revision = "0018_ui_acceptance_testing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("ai_model_pricing",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("pricing_id", sa.String(140), unique=True, nullable=False),
        sa.Column("provider_code", sa.String(100), nullable=False), sa.Column("model_code", sa.String(120), nullable=False),
        sa.Column("external_model_name", sa.String(160), nullable=False), sa.Column("currency", sa.String(10), nullable=False, server_default="USD"),
        sa.Column("input_cost_per_million_tokens", sa.Float(), nullable=False, server_default="0"), sa.Column("completion_cost_per_million_tokens", sa.Float(), nullable=False, server_default="0"),
        sa.Column("cached_input_cost_per_million_tokens", sa.Float()), sa.Column("reasoning_cost_per_million_tokens", sa.Float()),
        sa.Column("pricing_source_note", sa.String(1000), nullable=False), sa.Column("pricing_effective_from", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_model_pricing_model_active", "ai_model_pricing", ["model_code", "is_active"])
    op.create_table("ai_model_usage_metering",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("usage_id", sa.String(140), unique=True, nullable=False),
        sa.Column("invocation_id", sa.Uuid(), sa.ForeignKey("ai_invocation_logs.id"), unique=True, nullable=False),
        sa.Column("provider_code", sa.String(100), nullable=False), sa.Column("model_code", sa.String(120), nullable=False), sa.Column("external_model_name", sa.String(160), nullable=False), sa.Column("task_type", sa.String(80), nullable=False), sa.Column("request_source", sa.String(100), nullable=False),
        sa.Column("session_id", sa.Uuid()), sa.Column("case_id", sa.Uuid()), sa.Column("input_tokens", sa.Integer()), sa.Column("completion_tokens", sa.Integer()), sa.Column("total_tokens", sa.Integer()), sa.Column("cached_input_tokens", sa.Integer()), sa.Column("reasoning_tokens", sa.Integer()),
        sa.Column("estimated_input_cost", sa.Float()), sa.Column("estimated_completion_cost", sa.Float()), sa.Column("estimated_cached_input_cost", sa.Float()), sa.Column("estimated_reasoning_cost", sa.Float()), sa.Column("estimated_total_cost", sa.Float()), sa.Column("currency", sa.String(10), nullable=False, server_default="USD"), sa.Column("pricing_id", sa.String(140)), sa.Column("pricing_snapshot_json", sa.JSON()), sa.Column("usage_source", sa.String(30), nullable=False, server_default="UNAVAILABLE"), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_model_usage_metering_model_created", "ai_model_usage_metering", ["model_code", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_ai_model_usage_metering_model_created", table_name="ai_model_usage_metering")
    op.drop_table("ai_model_usage_metering")
    op.drop_index("ix_ai_model_pricing_model_active", table_name="ai_model_pricing")
    op.drop_table("ai_model_pricing")
