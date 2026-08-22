"""Add governed deterministic support copilot foundation."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_copilot_foundation"
down_revision: Union[str, Sequence[str], None] = "0008_batch_jobs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

uuid_type = postgresql.UUID(as_uuid=True)
timestamp_type = sa.DateTime(timezone=True)
json_type = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "copilot_sessions",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("session_number", sa.String(80), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.String(1500), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="OPEN"),
        sa.Column("primary_entity_type", sa.String(40), nullable=False, server_default="MANUAL"),
        sa.Column("primary_entity_id", uuid_type),
        sa.Column("primary_ticket_id", uuid_type, sa.ForeignKey("ams_tickets.id")),
        sa.Column("severity", sa.String(20), nullable=False, server_default="MEDIUM"),
        sa.Column("confidence_level", sa.String(20), nullable=False, server_default="UNKNOWN"),
        sa.Column("created_by", sa.String(120), nullable=False, server_default="support-engineer"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("closed_at", timestamp_type),
        sa.UniqueConstraint("session_number", name="uq_copilot_sessions_number"),
    )
    op.create_table(
        "copilot_context_snapshots",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("session_id", uuid_type, sa.ForeignKey("copilot_sessions.id"), nullable=False),
        sa.Column("snapshot_number", sa.String(80), nullable=False),
        sa.Column("source_entity_type", sa.String(40), nullable=False),
        sa.Column("source_entity_id", uuid_type),
        sa.Column("summary", sa.String(2000), nullable=False),
        sa.Column("impact_summary", sa.String(1500), nullable=False),
        sa.Column("technical_summary", sa.String(2500), nullable=False),
        sa.Column("business_summary", sa.String(2000), nullable=False),
        sa.Column("timeline_summary", sa.String(3000), nullable=False),
        sa.Column("evidence_summary", sa.String(3000), nullable=False),
        sa.Column("related_entities", json_type),
        sa.Column("raw_context", json_type),
        sa.Column("created_by", sa.String(120), nullable=False, server_default="support-engineer"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("snapshot_number", name="uq_copilot_snapshots_number"),
    )
    op.create_table(
        "copilot_recommendations",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("session_id", uuid_type, sa.ForeignKey("copilot_sessions.id"), nullable=False),
        sa.Column("snapshot_id", uuid_type, sa.ForeignKey("copilot_context_snapshots.id")),
        sa.Column("recommendation_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("details", sa.String(1500), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False, server_default="MEDIUM"),
        sa.Column("confidence_level", sa.String(20), nullable=False, server_default="UNKNOWN"),
        sa.Column("rationale", sa.String(1500), nullable=False),
        sa.Column("source_evidence", json_type),
        sa.Column("status", sa.String(20), nullable=False, server_default="PROPOSED"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("accepted_at", timestamp_type),
        sa.Column("dismissed_at", timestamp_type),
    )
    op.create_table(
        "copilot_action_plans",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("session_id", uuid_type, sa.ForeignKey("copilot_sessions.id"), nullable=False),
        sa.Column("snapshot_id", uuid_type, sa.ForeignKey("copilot_context_snapshots.id")),
        sa.Column("plan_number", sa.String(80), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("summary", sa.String(2000), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="DRAFT"),
        sa.Column("steps", json_type, nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="MEDIUM"),
        sa.Column("requires_human_approval", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("approved_at", timestamp_type),
        sa.Column("completed_at", timestamp_type),
        sa.UniqueConstraint("plan_number", name="uq_copilot_plans_number"),
    )
    op.create_table(
        "copilot_messages",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("session_id", uuid_type, sa.ForeignKey("copilot_sessions.id"), nullable=False),
        sa.Column("message_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.String(5000), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="DRAFT"),
        sa.Column("target_entity_type", sa.String(40)),
        sa.Column("target_entity_id", uuid_type),
        sa.Column("created_by", sa.String(120), nullable=False, server_default="support-engineer"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
    )
    op.create_table(
        "copilot_safe_actions",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("action_code", sa.String(80), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("target_module", sa.String(80), nullable=False),
        sa.Column("action_type", sa.String(40), nullable=False),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="LOW"),
        sa.Column("requires_human_approval", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("action_code", name="uq_copilot_safe_actions_code"),
    )
    op.create_table(
        "copilot_action_events",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("session_id", uuid_type, sa.ForeignKey("copilot_sessions.id"), nullable=False),
        sa.Column("action_code", sa.String(80), nullable=False),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("target_entity_type", sa.String(40)),
        sa.Column("target_entity_id", uuid_type),
        sa.Column("from_status", sa.String(30)),
        sa.Column("to_status", sa.String(30)),
        sa.Column("message", sa.String(1000), nullable=False),
        sa.Column("event_payload", json_type),
        sa.Column("created_by", sa.String(120), nullable=False, server_default="system"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_copilot_context_session_created", "copilot_context_snapshots", ["session_id", "created_at"])
    op.create_index("ix_copilot_recommendations_session_status", "copilot_recommendations", ["session_id", "status"])
    op.create_index("ix_copilot_messages_session_created", "copilot_messages", ["session_id", "created_at"])
    op.create_index("ix_copilot_events_session_created", "copilot_action_events", ["session_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_copilot_events_session_created", table_name="copilot_action_events")
    op.drop_index("ix_copilot_messages_session_created", table_name="copilot_messages")
    op.drop_index("ix_copilot_recommendations_session_status", table_name="copilot_recommendations")
    op.drop_index("ix_copilot_context_session_created", table_name="copilot_context_snapshots")
    op.drop_table("copilot_action_events")
    op.drop_table("copilot_safe_actions")
    op.drop_table("copilot_messages")
    op.drop_table("copilot_action_plans")
    op.drop_table("copilot_recommendations")
    op.drop_table("copilot_context_snapshots")
    op.drop_table("copilot_sessions")
