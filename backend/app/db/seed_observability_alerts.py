"""Idempotent seed for the EOS observability alert rule catalog."""

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import DatabaseManager
from app.models.observability_alerts import ObsAlertRule

RULES = [
    ("EOS_BACKEND_UNAVAILABLE", "EOS backend unavailable", "The full platform backend health endpoint is unavailable.", "AVAILABILITY", "HTTP", None, "http://localhost:8050/health", "NE", 200, "CRITICAL", "full", True),
    ("EOS_BUSINESS_BFF_UNAVAILABLE", "Business BFF unavailable", "The business application API boundary is unavailable.", "AVAILABILITY", "HTTP", None, "http://localhost:8061/health", "NE", 200, "HIGH", "business", True),
    ("EOS_OPERATIONS_BFF_UNAVAILABLE", "Operations BFF unavailable", "The operations support API boundary is unavailable.", "AVAILABILITY", "HTTP", None, "http://localhost:8062/health", "NE", 200, "HIGH", "operations", True),
    ("EOS_SIMULATION_BFF_UNAVAILABLE", "Simulation BFF unavailable", "The simulation lab API boundary is unavailable.", "AVAILABILITY", "HTTP", None, "http://localhost:8063/health", "NE", 200, "MEDIUM", "simulation", False),
    ("EOS_OBSERVABILITY_BFF_UNAVAILABLE", "Observability BFF unavailable", "The observability control API boundary is unavailable.", "AVAILABILITY", "HTTP", None, "http://localhost:8064/health", "NE", 200, "HIGH", "observability", True),
    ("EOS_AGENTIC_BFF_UNAVAILABLE", "Agentic BFF unavailable", "The governed support API boundary is unavailable.", "AVAILABILITY", "HTTP", None, "http://localhost:8065/health", "NE", 200, "HIGH", "agentic", True),
    ("EOS_API_ERROR_RATE_HIGH", "EOS API error rate high", "Runtime API error count exceeded the configured threshold.", "METRIC", "EOS_RUNTIME", "api_error_count", None, "GT", 5, "HIGH", "operations", True),
    ("EOS_API_LATENCY_HIGH", "EOS API latency high", "Runtime API latency exceeded the configured threshold.", "METRIC", "EOS_RUNTIME", "api_latency_ms", None, "GT", 1000, "HIGH", "operations", True),
    ("EOS_BATCH_FAILURE_SPIKE", "Batch failure spike", "Recent batch failures exceeded the configured threshold.", "BATCH", "EOS_BATCH", "batch_failed_runs", None, "GT", 1, "HIGH", "operations", True),
    ("EOS_AMS_TICKET_BACKLOG_HIGH", "AMS ticket backlog high", "Open AMS ticket backlog exceeded the configured threshold.", "BUSINESS_SIGNAL", "EOS_AMS", "ams_open_tickets", None, "GT", 20, "MEDIUM", "operations", False),
]


def seed_rules(db) -> None:
    for code, name, description, signal_type, source_system, metric_name, query_text, operator, threshold, severity, target, auto_ticket in RULES:
        rule = db.scalar(select(ObsAlertRule).where(ObsAlertRule.rule_code == code))
        values = dict(name=name, description=description, signal_type=signal_type, source_system=source_system, metric_name=metric_name, query_text=query_text, condition_operator=operator, threshold_value=threshold, severity=severity, enabled=True, deduplication_key_template=f"{code}:{{source}}", cooldown_minutes=30, evaluation_window_minutes=15, target_experience=target, recommended_owner="AMS-WAREHOUSE-SUPPORT", create_ticket_by_default=auto_ticket)
        if rule is None:
            db.add(ObsAlertRule(rule_code=code, **values))
        else:
            for key, value in values.items():
                setattr(rule, key, value)


def seed() -> None:
    manager = DatabaseManager(get_settings())
    manager.initialize()
    assert manager.session_factory is not None
    with manager.session_factory() as db:
        seed_rules(db)
        db.commit()
    manager.dispose()
    print(f"Observability alert seed complete: rules={len(RULES)}")


if __name__ == "__main__":
    seed()
