"""Add deterministic observability evidence and diagnostic cases."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_observability_diagnosis"
down_revision: Union[str, Sequence[str], None] = "0006_monitoring_alert_noise"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

uuid_type = postgresql.UUID(as_uuid=True)
timestamp_type = sa.DateTime(timezone=True)
json_type = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "obs_traces",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("trace_id", sa.String(100), nullable=False),
        sa.Column("trace_name", sa.String(200), nullable=False), sa.Column("trace_type", sa.String(40), nullable=False),
        sa.Column("status", sa.String(30), nullable=False), sa.Column("source_module", sa.String(80), nullable=False),
        sa.Column("root_entity_type", sa.String(40)), sa.Column("root_entity_id", uuid_type), sa.Column("root_reference", sa.String(160)),
        sa.Column("linked_alert_id", uuid_type, sa.ForeignKey("mon_alerts.id")), sa.Column("linked_triage_case_id", uuid_type, sa.ForeignKey("mon_triage_cases.id")), sa.Column("linked_ticket_id", uuid_type, sa.ForeignKey("ams_tickets.id")),
        sa.Column("started_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("ended_at", timestamp_type), sa.Column("duration_ms", sa.Integer), sa.Column("summary", sa.String(1000), nullable=False),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.UniqueConstraint("trace_id", name="uq_obs_traces_trace_id"),
    )
    op.create_table(
        "obs_spans",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("trace_id", uuid_type, sa.ForeignKey("obs_traces.id"), nullable=False), sa.Column("span_id", sa.String(100), nullable=False), sa.Column("parent_span_id", sa.String(100)),
        sa.Column("span_name", sa.String(200), nullable=False), sa.Column("service_name", sa.String(120), nullable=False), sa.Column("component_code", sa.String(80)), sa.Column("operation_type", sa.String(40), nullable=False), sa.Column("status", sa.String(30), nullable=False),
        sa.Column("started_at", timestamp_type, nullable=False), sa.Column("ended_at", timestamp_type), sa.Column("duration_ms", sa.Integer), sa.Column("error_type", sa.String(120)), sa.Column("error_message", sa.String(1000)), sa.Column("attributes", json_type),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.UniqueConstraint("trace_id", "span_id", name="uq_obs_spans_trace_span"),
    )
    op.create_table(
        "obs_log_events",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("log_number", sa.String(100), nullable=False), sa.Column("trace_id", uuid_type, sa.ForeignKey("obs_traces.id")), sa.Column("span_id", uuid_type, sa.ForeignKey("obs_spans.id")),
        sa.Column("level", sa.String(20), nullable=False), sa.Column("logger_name", sa.String(160), nullable=False), sa.Column("message", sa.String(1000), nullable=False), sa.Column("event_type", sa.String(80), nullable=False), sa.Column("source_module", sa.String(80), nullable=False), sa.Column("component_code", sa.String(80)), sa.Column("entity_type", sa.String(40)), sa.Column("entity_id", uuid_type), sa.Column("linked_alert_id", uuid_type, sa.ForeignKey("mon_alerts.id")), sa.Column("linked_ticket_id", uuid_type, sa.ForeignKey("ams_tickets.id")), sa.Column("context", json_type), sa.Column("logged_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.UniqueConstraint("log_number", name="uq_obs_log_events_number"),
    )
    op.create_table(
        "obs_metric_samples",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("sample_number", sa.String(100), nullable=False), sa.Column("metric_name", sa.String(120), nullable=False), sa.Column("metric_value", sa.Float, nullable=False), sa.Column("metric_unit", sa.String(30), nullable=False), sa.Column("component_code", sa.String(80)), sa.Column("severity", sa.String(20)), sa.Column("trace_id", uuid_type, sa.ForeignKey("obs_traces.id")), sa.Column("linked_alert_id", uuid_type, sa.ForeignKey("mon_alerts.id")), sa.Column("recorded_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("attributes", json_type), sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.UniqueConstraint("sample_number", name="uq_obs_metric_samples_number"),
    )
    op.create_table(
        "obs_diagnostic_cases",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("diagnostic_number", sa.String(100), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("description", sa.String(1500), nullable=False), sa.Column("status", sa.String(30), nullable=False, server_default="OPEN"), sa.Column("severity", sa.String(20), nullable=False, server_default="MEDIUM"), sa.Column("source_type", sa.String(30), nullable=False), sa.Column("source_id", uuid_type), sa.Column("linked_alert_id", uuid_type, sa.ForeignKey("mon_alerts.id")), sa.Column("linked_triage_case_id", uuid_type, sa.ForeignKey("mon_triage_cases.id")), sa.Column("linked_ticket_id", uuid_type, sa.ForeignKey("ams_tickets.id")), sa.Column("primary_trace_id", uuid_type, sa.ForeignKey("obs_traces.id")), sa.Column("probable_cause", sa.String(1000), nullable=False), sa.Column("confidence_level", sa.String(20), nullable=False, server_default="UNKNOWN"), sa.Column("recommended_next_steps", sa.String(1500), nullable=False), sa.Column("diagnosis_summary", sa.String(2000), nullable=False), sa.Column("created_by", sa.String(120), nullable=False, server_default="support-engineer"), sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("resolved_at", timestamp_type), sa.UniqueConstraint("diagnostic_number", name="uq_obs_diagnostic_cases_number"),
    )
    op.create_table(
        "obs_diagnostic_evidence",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("diagnostic_case_id", uuid_type, sa.ForeignKey("obs_diagnostic_cases.id"), nullable=False), sa.Column("evidence_type", sa.String(30), nullable=False), sa.Column("source_table", sa.String(80), nullable=False), sa.Column("source_id", uuid_type, nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("details", sa.String(1500), nullable=False), sa.Column("weight", sa.Float, nullable=False, server_default="1"), sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_obs_spans_trace_started", "obs_spans", ["trace_id", "started_at"])
    op.create_index("ix_obs_logs_trace_logged", "obs_log_events", ["trace_id", "logged_at"])
    op.create_index("ix_obs_metrics_trace_recorded", "obs_metric_samples", ["trace_id", "recorded_at"])


def downgrade() -> None:
    op.drop_index("ix_obs_metrics_trace_recorded", table_name="obs_metric_samples")
    op.drop_index("ix_obs_logs_trace_logged", table_name="obs_log_events")
    op.drop_index("ix_obs_spans_trace_started", table_name="obs_spans")
    op.drop_table("obs_diagnostic_evidence")
    op.drop_table("obs_diagnostic_cases")
    op.drop_table("obs_metric_samples")
    op.drop_table("obs_log_events")
    op.drop_table("obs_spans")
    op.drop_table("obs_traces")
