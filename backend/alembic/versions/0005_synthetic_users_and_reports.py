"""Add synthetic users, journey runs, and user-reported issues.

Revision ID: 0005_synthetic_users_reports
Revises: 0004_operations_ams
Create Date: 2026-08-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0005_synthetic_users_reports"
down_revision: Union[str, Sequence[str], None] = "0004_operations_ams"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

uuid_type = postgresql.UUID(as_uuid=True)
timestamp_type = sa.DateTime(timezone=True)
json_type = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "synthetic_users",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("user_code", sa.String(length=60), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("persona", sa.String(length=40), nullable=False),
        sa.Column("department", sa.String(length=120), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=200)),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("user_code", name="uq_synthetic_users_code"),
        sa.UniqueConstraint("email", name="uq_synthetic_users_email"),
    )

    op.create_table(
        "synthetic_journeys",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("journey_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.Column("persona", sa.String(length=40), nullable=False),
        sa.Column("journey_type", sa.String(length=40), nullable=False),
        sa.Column("expected_outcome", sa.String(length=40), nullable=False),
        sa.Column("creates_user_report_on_failure", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("creates_ticket_on_failure", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("default_payload", json_type),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("journey_code", name="uq_synthetic_journeys_code"),
    )

    op.create_table(
        "synthetic_journey_runs",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("run_number", sa.String(length=80), nullable=False),
        sa.Column("journey_id", uuid_type, sa.ForeignKey("synthetic_journeys.id"), nullable=False),
        sa.Column("synthetic_user_id", uuid_type, sa.ForeignKey("synthetic_users.id"), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PARTIAL"),
        sa.Column("started_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", timestamp_type),
        sa.Column("duration_ms", sa.Integer),
        sa.Column("input_payload", json_type),
        sa.Column("result_payload", json_type),
        sa.Column("failure_type", sa.String(length=80)),
        sa.Column("failure_message", sa.String(length=1000)),
        sa.Column("order_id", uuid_type, sa.ForeignKey("wf_orders.id")),
        sa.Column("task_id", uuid_type, sa.ForeignKey("wf_fulfillment_tasks.id")),
        sa.Column("shipment_id", uuid_type, sa.ForeignKey("wf_shipments.id")),
        sa.Column("user_report_id", uuid_type),
        sa.Column("ticket_id", uuid_type, sa.ForeignKey("ams_tickets.id")),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("run_number", name="uq_synthetic_journey_runs_number"),
    )

    op.create_table(
        "ams_user_reports",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("report_number", sa.String(length=80), nullable=False),
        sa.Column("reporter_user_id", uuid_type, sa.ForeignKey("synthetic_users.id")),
        sa.Column("reporter_name", sa.String(length=160), nullable=False),
        sa.Column("reporter_email", sa.String(length=200)),
        sa.Column("reporter_persona", sa.String(length=40)),
        sa.Column("report_channel", sa.String(length=30), nullable=False, server_default="MANUAL"),
        sa.Column("source_module", sa.String(length=80), nullable=False, server_default="WAREHOUSE_FULFILLMENT"),
        sa.Column("affected_entity_type", sa.String(length=40), nullable=False, server_default="UNKNOWN"),
        sa.Column("affected_entity_id", uuid_type),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=False),
        sa.Column("business_impact", sa.String(length=1000), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="SUBMITTED"),
        sa.Column("journey_run_id", uuid_type, sa.ForeignKey("synthetic_journey_runs.id")),
        sa.Column("ticket_id", uuid_type, sa.ForeignKey("ams_tickets.id")),
        sa.Column("submitted_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("acknowledged_at", timestamp_type),
        sa.Column("resolved_at", timestamp_type),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("report_number", name="uq_ams_user_reports_number"),
    )
    op.create_foreign_key("fk_synthetic_runs_user_report", "synthetic_journey_runs", "ams_user_reports", ["user_report_id"], ["id"])
    op.add_column("ams_tickets", sa.Column("user_report_id", uuid_type, nullable=True))
    op.create_foreign_key("fk_ams_tickets_user_report", "ams_tickets", "ams_user_reports", ["user_report_id"], ["id"])
    op.create_index("ix_synthetic_runs_journey_status", "synthetic_journey_runs", ["journey_id", "status"])
    op.create_index("ix_ams_user_reports_status", "ams_user_reports", ["status", "severity"])
    op.create_index("ix_ams_user_reports_ticket", "ams_user_reports", ["ticket_id"])


def downgrade() -> None:
    op.drop_index("ix_ams_user_reports_ticket", table_name="ams_user_reports")
    op.drop_index("ix_ams_user_reports_status", table_name="ams_user_reports")
    op.drop_index("ix_synthetic_runs_journey_status", table_name="synthetic_journey_runs")
    op.drop_constraint("fk_ams_tickets_user_report", "ams_tickets", type_="foreignkey")
    op.drop_column("ams_tickets", "user_report_id")
    op.drop_constraint("fk_synthetic_runs_user_report", "synthetic_journey_runs", type_="foreignkey")
    op.drop_table("ams_user_reports")
    op.drop_table("synthetic_journey_runs")
    op.drop_table("synthetic_journeys")
    op.drop_table("synthetic_users")

