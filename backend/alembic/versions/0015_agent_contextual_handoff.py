"""Add generic source references for contextual agent investigations."""

from alembic import op
import sqlalchemy as sa

revision = "0015_agent_contextual_handoff"
down_revision = "0014_agent_knowledge_rag"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("agent_cases", sa.Column("source_object_type", sa.String(50), nullable=True))
    op.add_column("agent_cases", sa.Column("source_object_id", sa.Uuid(), nullable=True))
    op.add_column("agent_cases", sa.Column("source_object_display", sa.String(200), nullable=True))
    op.add_column("agent_cases", sa.Column("source_object_url", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("agent_cases", "source_object_url")
    op.drop_column("agent_cases", "source_object_display")
    op.drop_column("agent_cases", "source_object_id")
    op.drop_column("agent_cases", "source_object_type")
