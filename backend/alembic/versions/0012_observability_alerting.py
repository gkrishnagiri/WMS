"""Add observability alert rules and alert-to-AMS linkage."""

from alembic import op
import sqlalchemy as sa

revision = "0012_observability_alerting"
down_revision = "0011_copilot_governed_ai_drafts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("obs_alert_rules",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("rule_code", sa.String(100), nullable=False, unique=True),
        sa.Column("name", sa.String(200), nullable=False), sa.Column("description", sa.String(1000), nullable=False),
        sa.Column("signal_type", sa.String(40), nullable=False), sa.Column("source_system", sa.String(80), nullable=False),
        sa.Column("metric_name", sa.String(120)), sa.Column("query_text", sa.String(500)), sa.Column("condition_operator", sa.String(10), nullable=False),
        sa.Column("threshold_value", sa.Float()), sa.Column("severity", sa.String(20), nullable=False), sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("deduplication_key_template", sa.String(250), nullable=False), sa.Column("cooldown_minutes", sa.Integer(), nullable=False),
        sa.Column("evaluation_window_minutes", sa.Integer(), nullable=False), sa.Column("target_experience", sa.String(40), nullable=False),
        sa.Column("recommended_owner", sa.String(120), nullable=False), sa.Column("create_ticket_by_default", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("obs_alert_evaluation_runs",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("run_id", sa.String(100), nullable=False, unique=True), sa.Column("trigger_source", sa.String(40), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("started_at", sa.DateTime(timezone=True), nullable=False), sa.Column("completed_at", sa.DateTime(timezone=True)), sa.Column("rules_evaluated", sa.Integer(), nullable=False), sa.Column("events_created", sa.Integer(), nullable=False), sa.Column("events_suppressed", sa.Integer(), nullable=False), sa.Column("tickets_created", sa.Integer(), nullable=False), sa.Column("error_message", sa.String(1000)))
    op.create_table("obs_alert_events",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("event_id", sa.String(100), nullable=False, unique=True), sa.Column("rule_id", sa.Uuid(), sa.ForeignKey("obs_alert_rules.id"), nullable=False), sa.Column("rule_code", sa.String(100), nullable=False), sa.Column("title", sa.String(250), nullable=False), sa.Column("description", sa.String(1500), nullable=False), sa.Column("severity", sa.String(20), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("deduplication_key", sa.String(250), nullable=False), sa.Column("source_signal", sa.String(120), nullable=False), sa.Column("source_url", sa.String(500)), sa.Column("observed_value", sa.Float()), sa.Column("threshold_value", sa.Float()), sa.Column("condition_summary", sa.String(500), nullable=False), sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False), sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False), sa.Column("occurrence_count", sa.Integer(), nullable=False), sa.Column("suppressed_count", sa.Integer(), nullable=False), sa.Column("ticket_creation_status", sa.String(30), nullable=False), sa.Column("created_ticket_id", sa.Uuid(), sa.ForeignKey("ams_tickets.id")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("obs_alert_event_evidence",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("event_id", sa.Uuid(), sa.ForeignKey("obs_alert_events.id"), nullable=False), sa.Column("evidence_type", sa.String(40), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("summary", sa.String(1000), nullable=False), sa.Column("payload_json", sa.JSON()), sa.Column("source_url", sa.String(500)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("obs_alert_ticket_links",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("event_id", sa.Uuid(), sa.ForeignKey("obs_alert_events.id"), nullable=False), sa.Column("ams_ticket_id", sa.Uuid(), sa.ForeignKey("ams_tickets.id"), nullable=False), sa.Column("link_type", sa.String(30), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("created_by", sa.String(120), nullable=False))


def downgrade() -> None:
    op.drop_table("obs_alert_ticket_links")
    op.drop_table("obs_alert_event_evidence")
    op.drop_table("obs_alert_events")
    op.drop_table("obs_alert_evaluation_runs")
    op.drop_table("obs_alert_rules")
