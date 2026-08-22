"""Idempotent seed for the Prompt 06 monitoring catalog."""

from __future__ import annotations

from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import DatabaseManager
from app.models.monitoring import MonAlertRule, MonComponent


COMPONENTS = [
    ("EOS-FRONTEND", "EOS Frontend", "FRONTEND", "PRESENTATION", "EOS Web Experience"),
    ("EOS-BACKEND-API", "EOS Backend API", "API", "APPLICATION", "EOS Platform Engineering"),
    ("EOS-POSTGRES", "EOS PostgreSQL", "DATABASE", "DATA", "Database Operations"),
    ("EOS-REDIS", "EOS Redis", "CACHE", "CACHE", "Platform Operations"),
    ("WF-ORDER-WORKFLOW", "Warehouse Order Workflow", "WORKFLOW", "BUSINESS_WORKFLOW", "Warehouse Application Support"),
    ("WF-INVENTORY-SERVICE", "Warehouse Inventory Service", "BUSINESS_PROCESS", "BUSINESS_WORKFLOW", "Warehouse Application Support"),
    ("WF-SHIPMENT-SERVICE", "Warehouse Shipment Service", "BUSINESS_PROCESS", "BUSINESS_WORKFLOW", "Warehouse Application Support"),
]

RULES = [
    ("MON-API-LATENCY", "API latency threshold", "Backend API response latency is above the deterministic threshold.", "EOS-BACKEND-API", "api_latency_ms", "GT", 500, "HIGH"),
    ("MON-API-ERROR", "API error rate threshold", "Backend API error rate is above the deterministic threshold.", "EOS-BACKEND-API", "api_error_rate", "GT", 3, "MEDIUM"),
    ("MON-FRONTEND-API", "Frontend API failure threshold", "Frontend API requests are failing above the deterministic threshold.", "EOS-FRONTEND", "frontend_api_failure_count", "GTE", 10, "HIGH"),
    ("MON-WORKFLOW-FAILURE", "Workflow failure threshold", "Warehouse workflow failures are above the deterministic threshold.", "WF-ORDER-WORKFLOW", "workflow_failure_count", "GT", 3, "MEDIUM"),
    ("MON-DB-LATENCY", "Database latency threshold", "PostgreSQL response time is above the deterministic threshold.", "EOS-POSTGRES", "db_latency_ms", "GT", 300, "HIGH"),
    ("MON-INV-ALLOC", "Allocation failure threshold", "Inventory allocation failures are above the deterministic threshold.", "WF-INVENTORY-SERVICE", "allocation_failure_count", "GT", 2, "HIGH"),
    ("MON-REDIS-FLAP", "Redis connection failure threshold", "Redis connection failures are above the deterministic threshold.", "EOS-REDIS", "redis_connection_failures", "GT", 2, "HIGH"),
    ("MON-SHIPMENT-EXC", "Shipment exception threshold", "Shipment exceptions are above the deterministic threshold.", "WF-SHIPMENT-SERVICE", "shipment_exception_count", "GT", 2, "MEDIUM"),
    ("MON-WORKFLOW-HIGH", "High workflow failure threshold", "A high-severity warehouse workflow failure symptom is present.", "WF-ORDER-WORKFLOW", "workflow_failure_count", "GT", 10, "HIGH"),
    ("MON-WORKFLOW-LOW", "Low workflow failure threshold", "A low-severity intermittent workflow failure symptom is present.", "WF-ORDER-WORKFLOW", "workflow_failure_count", "GT", 1, "LOW"),
]


def seed() -> None:
    manager = DatabaseManager(get_settings())
    manager.initialize()
    assert manager.session_factory is not None
    with manager.session_factory() as db:
        components: dict[str, MonComponent] = {}
        for code, name, component_type, layer, owner in COMPONENTS:
            row = db.scalar(select(MonComponent).where(MonComponent.component_code == code))
            if row is None:
                row = MonComponent(component_code=code, name=name, component_type=component_type, layer=layer, environment=get_settings().app_env, owner_team=owner, business_service="Warehouse & Fulfillment Operations", application_name="Enterprise Operations Suite", status="ACTIVE", description=f"Deterministic monitoring catalog component for {name}.")
                db.add(row)
            components[code] = row
        db.flush()
        for code, name, description, component_code, metric, operator, threshold, severity in RULES:
            row = db.scalar(select(MonAlertRule).where(MonAlertRule.rule_code == code))
            if row is None:
                db.add(MonAlertRule(rule_code=code, name=name, description=description, component_id=components[component_code].id, metric_name=metric, condition_operator=operator, threshold_value=threshold, severity=severity, enabled=True, dedupe_window_minutes=15))
            else:
                row.component_id = components[component_code].id
                row.metric_name, row.condition_operator, row.threshold_value, row.severity = metric, operator, threshold, severity
        db.commit()
    manager.dispose()
    print(f"Monitoring seed complete: mon_components={len(COMPONENTS)}, mon_alert_rules={len(RULES)}")


if __name__ == "__main__":
    seed()
