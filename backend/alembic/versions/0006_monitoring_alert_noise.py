"""Add deterministic monitoring alerts and manual triage cases.

Revision ID: 0006_monitoring_alert_noise
Revises: 0005_synthetic_users_reports
Create Date: 2026-08-22
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0006_monitoring_alert_noise"
down_revision: Union[str, Sequence[str], None] = "0005_synthetic_users_reports"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

uuid_type = postgresql.UUID(as_uuid=True)
timestamp_type = sa.DateTime(timezone=True)
json_type = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "mon_components",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("component_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("component_type", sa.String(length=40), nullable=False),
        sa.Column("layer", sa.String(length=40), nullable=False),
        sa.Column("environment", sa.String(length=40), nullable=False, server_default="development"),
        sa.Column("owner_team", sa.String(length=120), nullable=False),
        sa.Column("business_service", sa.String(length=160), nullable=False, server_default="Warehouse & Fulfillment Operations"),
        sa.Column("application_name", sa.String(length=160), nullable=False, server_default="Enterprise Operations Suite"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("component_code", name="uq_mon_components_code"),
    )
    op.create_table(
        "mon_alert_rules",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("rule_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("component_id", uuid_type, sa.ForeignKey("mon_components.id"), nullable=False),
        sa.Column("metric_name", sa.String(length=80), nullable=False),
        sa.Column("condition_operator", sa.String(length=10), nullable=False),
        sa.Column("threshold_value", sa.Float, nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("dedupe_window_minutes", sa.Integer, nullable=False, server_default="15"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("rule_code", name="uq_mon_alert_rules_code"),
    )
    op.create_table(
        "mon_alerts",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("alert_number", sa.String(length=80), nullable=False),
        sa.Column("rule_id", uuid_type, sa.ForeignKey("mon_alert_rules.id"), nullable=False),
        sa.Column("component_id", uuid_type, sa.ForeignKey("mon_components.id"), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("signal_type", sa.String(length=40), nullable=False, server_default="METRIC_THRESHOLD"),
        sa.Column("metric_name", sa.String(length=80), nullable=False),
        sa.Column("observed_value", sa.Float, nullable=False),
        sa.Column("threshold_value", sa.Float, nullable=False),
        sa.Column("dedupe_key", sa.String(length=200), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False),
        sa.Column("first_seen_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("last_seen_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("occurrence_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("acknowledged_at", timestamp_type),
        sa.Column("suppressed_at", timestamp_type),
        sa.Column("resolved_at", timestamp_type),
        sa.Column("linked_exception_id", uuid_type, sa.ForeignKey("ops_exceptions.id")),
        sa.Column("linked_ticket_id", uuid_type, sa.ForeignKey("ams_tickets.id")),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("alert_number", name="uq_mon_alerts_number"),
    )
    op.create_index("ix_mon_alerts_dedupe_status", "mon_alerts", ["dedupe_key", "status"])
    op.create_table(
        "mon_alert_events",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("alert_id", uuid_type, sa.ForeignKey("mon_alerts.id"), nullable=False),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("from_status", sa.String(length=30)),
        sa.Column("to_status", sa.String(length=30)),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("event_payload", json_type),
        sa.Column("created_by", sa.String(length=120), nullable=False, server_default="system"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_mon_alert_events_alert_created", "mon_alert_events", ["alert_id", "created_at"])
    op.create_table(
        "mon_triage_cases",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("case_number", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=1500), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("suspected_impact", sa.String(length=1000), nullable=False),
        sa.Column("suspected_root_cause", sa.String(length=1000)),
        sa.Column("confidence_level", sa.String(length=20), nullable=False, server_default="UNKNOWN"),
        sa.Column("analysis_notes", sa.String(length=2000)),
        sa.Column("linked_ticket_id", uuid_type, sa.ForeignKey("ams_tickets.id")),
        sa.Column("created_by", sa.String(length=120), nullable=False, server_default="support-engineer"),
        sa.Column("acknowledged_at", timestamp_type),
        sa.Column("resolved_at", timestamp_type),
        sa.Column("closed_at", timestamp_type),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("case_number", name="uq_mon_triage_cases_number"),
    )
    op.create_table(
        "mon_triage_case_alerts",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("triage_case_id", uuid_type, sa.ForeignKey("mon_triage_cases.id"), nullable=False),
        sa.Column("alert_id", uuid_type, sa.ForeignKey("mon_alerts.id"), nullable=False),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("triage_case_id", "alert_id", name="uq_mon_triage_case_alert"),
    )


def downgrade() -> None:
    op.drop_table("mon_triage_case_alerts")
    op.drop_table("mon_triage_cases")
    op.drop_index("ix_mon_alert_events_alert_created", table_name="mon_alert_events")
    op.drop_table("mon_alert_events")
    op.drop_index("ix_mon_alerts_dedupe_status", table_name="mon_alerts")
    op.drop_table("mon_alerts")
    op.drop_table("mon_alert_rules")
    op.drop_table("mon_components")

