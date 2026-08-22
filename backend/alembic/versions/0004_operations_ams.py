"""Add operational exceptions and AMS ticket foundation tables.

Revision ID: 0004_operations_ams
Revises: 0003_warehouse_workflows
Create Date: 2026-08-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0004_operations_ams"
down_revision: Union[str, Sequence[str], None] = "0003_warehouse_workflows"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

uuid_type = postgresql.UUID(as_uuid=True)
timestamp_type = sa.DateTime(timezone=True)
json_type = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "ops_exceptions",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("exception_number", sa.String(length=60), nullable=False),
        sa.Column("exception_type", sa.String(length=50), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("source_module", sa.String(length=80), nullable=False, server_default="WAREHOUSE_FULFILLMENT"),
        sa.Column("source_entity_type", sa.String(length=40), nullable=False),
        sa.Column("source_entity_id", uuid_type, nullable=True),
        sa.Column("source_reference", sa.String(length=120)),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.Column("detection_method", sa.String(length=30), nullable=False, server_default="RULE_BASED"),
        sa.Column("business_impact", sa.String(length=500), nullable=False),
        sa.Column("technical_context", json_type),
        sa.Column("first_detected_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("last_detected_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("resolved_at", timestamp_type),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("exception_number", name="uq_ops_exceptions_number"),
    )
    op.create_index(
        "ix_ops_exceptions_active_source",
        "ops_exceptions",
        ["exception_type", "source_entity_type", "source_entity_id", "status"],
    )

    op.create_table(
        "ams_tickets",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("ticket_number", sa.String(length=60), nullable=False),
        sa.Column("ticket_type", sa.String(length=30), nullable=False, server_default="INCIDENT"),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("priority", sa.String(length=10), nullable=False, server_default="P3"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="NEW"),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="MANUAL"),
        sa.Column("source_module", sa.String(length=80), nullable=False, server_default="WAREHOUSE_FULFILLMENT"),
        sa.Column("exception_id", uuid_type, sa.ForeignKey("ops_exceptions.id"), nullable=True),
        sa.Column("affected_entity_type", sa.String(length=40)),
        sa.Column("affected_entity_id", uuid_type, nullable=True),
        sa.Column("short_description", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=False),
        sa.Column("assignment_group", sa.String(length=120), nullable=False, server_default="AMS-WAREHOUSE-SUPPORT"),
        sa.Column("assigned_to", sa.String(length=120)),
        sa.Column("business_service", sa.String(length=160), nullable=False, server_default="Warehouse & Fulfillment Operations"),
        sa.Column("application_name", sa.String(length=160), nullable=False, server_default="Enterprise Operations Suite"),
        sa.Column("environment", sa.String(length=40), nullable=False, server_default="development"),
        sa.Column("opened_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("acknowledged_at", timestamp_type),
        sa.Column("resolved_at", timestamp_type),
        sa.Column("closed_at", timestamp_type),
        sa.Column("resolution_code", sa.String(length=80)),
        sa.Column("resolution_notes", sa.String(length=2000)),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("ticket_number", name="uq_ams_tickets_number"),
    )
    op.create_index("ix_ams_tickets_exception_status", "ams_tickets", ["exception_id", "status"])

    op.create_table(
        "ams_ticket_events",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("ticket_id", uuid_type, sa.ForeignKey("ams_tickets.id"), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("from_status", sa.String(length=30)),
        sa.Column("to_status", sa.String(length=30)),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("event_payload", json_type),
        sa.Column("created_by", sa.String(length=120), nullable=False, server_default="system"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ams_ticket_events_ticket_created", "ams_ticket_events", ["ticket_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_ams_ticket_events_ticket_created", table_name="ams_ticket_events")
    op.drop_table("ams_ticket_events")
    op.drop_index("ix_ams_tickets_exception_status", table_name="ams_tickets")
    op.drop_table("ams_tickets")
    op.drop_index("ix_ops_exceptions_active_source", table_name="ops_exceptions")
    op.drop_table("ops_exceptions")

