"""Add deterministic batch jobs, runs, steps, and events."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_batch_jobs"
down_revision: Union[str, Sequence[str], None] = "0007_observability_diagnosis"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

uuid_type = postgresql.UUID(as_uuid=True)
timestamp_type = sa.DateTime(timezone=True)
json_type = postgresql.JSONB


def upgrade() -> None:
    op.create_table(
        "batch_jobs",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("job_code", sa.String(80), nullable=False), sa.Column("name", sa.String(180), nullable=False), sa.Column("description", sa.String(1000), nullable=False), sa.Column("job_type", sa.String(60), nullable=False), sa.Column("module", sa.String(80), nullable=False, server_default="WAREHOUSE_FULFILLMENT"), sa.Column("business_service", sa.String(160), nullable=False, server_default="Warehouse & Fulfillment Operations"), sa.Column("application_name", sa.String(160), nullable=False, server_default="Enterprise Operations Suite"), sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()), sa.Column("default_severity", sa.String(20), nullable=False, server_default="MEDIUM"), sa.Column("sla_minutes", sa.Integer, nullable=False, server_default="60"), sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.UniqueConstraint("job_code", name="uq_batch_jobs_code"),
    )
    op.create_table(
        "batch_job_steps",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("job_id", uuid_type, sa.ForeignKey("batch_jobs.id"), nullable=False), sa.Column("step_code", sa.String(100), nullable=False), sa.Column("step_name", sa.String(180), nullable=False), sa.Column("step_order", sa.Integer, nullable=False), sa.Column("step_type", sa.String(40), nullable=False), sa.Column("description", sa.String(500), nullable=False), sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.true()), sa.Column("expected_duration_ms", sa.Integer, nullable=False, server_default="1000"), sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.UniqueConstraint("job_id", "step_code", name="uq_batch_job_steps_code"), sa.UniqueConstraint("job_id", "step_order", name="uq_batch_job_steps_order"),
    )
    op.create_table(
        "batch_runs",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("run_number", sa.String(100), nullable=False), sa.Column("job_id", uuid_type, sa.ForeignKey("batch_jobs.id"), nullable=False), sa.Column("status", sa.String(30), nullable=False, server_default="PENDING"), sa.Column("trigger_type", sa.String(30), nullable=False, server_default="SIMULATION"), sa.Column("scenario_code", sa.String(100), nullable=False), sa.Column("started_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("completed_at", timestamp_type), sa.Column("duration_ms", sa.Integer), sa.Column("records_processed", sa.Integer, nullable=False, server_default="0"), sa.Column("records_succeeded", sa.Integer, nullable=False, server_default="0"), sa.Column("records_failed", sa.Integer, nullable=False, server_default="0"), sa.Column("failure_type", sa.String(60)), sa.Column("failure_message", sa.String(1500)), sa.Column("summary", sa.String(2000), nullable=False), sa.Column("linked_exception_id", uuid_type, sa.ForeignKey("ops_exceptions.id")), sa.Column("linked_ticket_id", uuid_type, sa.ForeignKey("ams_tickets.id")), sa.Column("linked_alert_id", uuid_type, sa.ForeignKey("mon_alerts.id")), sa.Column("linked_diagnostic_case_id", uuid_type, sa.ForeignKey("obs_diagnostic_cases.id")), sa.Column("created_by", sa.String(120), nullable=False, server_default="system"), sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.UniqueConstraint("run_number", name="uq_batch_runs_number"),
    )
    op.create_table(
        "batch_step_runs",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("batch_run_id", uuid_type, sa.ForeignKey("batch_runs.id"), nullable=False), sa.Column("job_step_id", uuid_type, sa.ForeignKey("batch_job_steps.id"), nullable=False), sa.Column("step_code", sa.String(100), nullable=False), sa.Column("step_name", sa.String(180), nullable=False), sa.Column("step_order", sa.Integer, nullable=False), sa.Column("status", sa.String(30), nullable=False, server_default="PENDING"), sa.Column("started_at", timestamp_type, nullable=False), sa.Column("completed_at", timestamp_type), sa.Column("duration_ms", sa.Integer), sa.Column("records_processed", sa.Integer, nullable=False, server_default="0"), sa.Column("records_succeeded", sa.Integer, nullable=False, server_default="0"), sa.Column("records_failed", sa.Integer, nullable=False, server_default="0"), sa.Column("failure_type", sa.String(60)), sa.Column("failure_message", sa.String(1500)), sa.Column("technical_context", json_type), sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
    )
    op.create_table(
        "batch_run_events",
        sa.Column("id", uuid_type, primary_key=True, nullable=False), sa.Column("batch_run_id", uuid_type, sa.ForeignKey("batch_runs.id"), nullable=False), sa.Column("event_type", sa.String(60), nullable=False), sa.Column("from_status", sa.String(30)), sa.Column("to_status", sa.String(30)), sa.Column("message", sa.String(1000), nullable=False), sa.Column("event_payload", json_type), sa.Column("created_by", sa.String(120), nullable=False, server_default="system"), sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_batch_runs_job_created", "batch_runs", ["job_id", "created_at"])
    op.create_index("ix_batch_step_runs_run_order", "batch_step_runs", ["batch_run_id", "step_order"])
    op.create_index("ix_batch_events_run_created", "batch_run_events", ["batch_run_id", "created_at"])


def downgrade() -> None:
    op.drop_index("ix_batch_events_run_created", table_name="batch_run_events")
    op.drop_index("ix_batch_step_runs_run_order", table_name="batch_step_runs")
    op.drop_index("ix_batch_runs_job_created", table_name="batch_runs")
    op.drop_table("batch_run_events")
    op.drop_table("batch_step_runs")
    op.drop_table("batch_runs")
    op.drop_table("batch_job_steps")
    op.drop_table("batch_jobs")
