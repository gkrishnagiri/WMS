"""Allow the governed OpenAI costing catalog to be extended or archived."""

from alembic import op
import sqlalchemy as sa

revision = "0020_dynamic_model_catalog"
down_revision = "0019_openai_model_cost_metering"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ai_model_configs", sa.Column("catalog_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_ai_model_configs_catalog_active", "ai_model_configs", ["catalog_active"])


def downgrade() -> None:
    op.drop_index("ix_ai_model_configs_catalog_active", table_name="ai_model_configs")
    op.drop_column("ai_model_configs", "catalog_active")
