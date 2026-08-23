"""Add governed AI linkage to copilot messages."""

from alembic import op
import sqlalchemy as sa


revision = "0011_copilot_governed_ai_drafts"
down_revision = "0010_governed_ai_config"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("copilot_messages", sa.Column("ai_invocation_id", sa.Uuid(), nullable=True))
    op.add_column("copilot_messages", sa.Column("generation_mode", sa.String(length=30), nullable=True))
    op.create_foreign_key(
        "fk_copilot_messages_ai_invocation",
        "copilot_messages",
        "ai_invocation_logs",
        ["ai_invocation_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_copilot_messages_ai_invocation", "copilot_messages", type_="foreignkey")
    op.drop_column("copilot_messages", "generation_mode")
    op.drop_column("copilot_messages", "ai_invocation_id")
