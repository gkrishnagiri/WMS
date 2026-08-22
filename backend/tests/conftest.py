from collections.abc import AsyncIterator
from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.core.config import Settings
from app.models.warehouse import FulfillmentTask, InventoryBalance, Item, Location, Order, OrderLine, Shipment, Warehouse, Zone
from app.models.synthetic_users import SyntheticJourney, SyntheticUser
from app.models.monitoring import MonAlertRule, MonComponent
from app.models.batch import BatchJob, BatchJobStep
from app.models.copilot import CopilotSafeAction
from app.db.seed_copilot import SAFE_ACTIONS
from app.models.ai_config import AiModelConfig, AiPromptTemplate, AiProvider, AiSafetyPolicy, AiSafetyPolicyRule
from app.db.seed_ai_config import PROVIDERS, RULES, TEMPLATES


class _UnavailableDatabase:
    git_commit = "test-commit"

    def check_connection(self) -> bool:
        return False


class _UnavailableRedis:
    async def ping(self) -> bool:
        return False


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    # Endpoint tests do not require external services. Their unavailable
    # dependency doubles make the 503 health path deterministic; running the
    # real service checks is an integration concern for a live environment.
    app.state.settings = Settings()
    app.state.database = _UnavailableDatabase()
    app.state.redis = _UnavailableRedis()
    app.state.build_timestamp = "test-build"
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as test_client:
        yield test_client


@pytest.fixture
async def warehouse_client(client: AsyncClient):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = factory()

    warehouse = Warehouse(code="TEST-FC-01", name="Test Fulfillment Center", region="Test Region", city="Test City", country="USA")
    zone = Zone(warehouse=warehouse, code="PICK", name="Picking", zone_type="PICKING")
    location = Location(warehouse=warehouse, zone=zone, code="TEST-PICK-01", location_type="BIN", capacity_units=100)
    item = Item(sku="SKU-TEST-01", name="Test Scanner", category="Electronics", reorder_point=10, safety_stock=5)
    session.add_all([warehouse, zone, location, item])
    session.flush()
    session.add(InventoryBalance(warehouse_id=warehouse.id, location_id=location.id, item_id=item.id, quantity_on_hand=20, quantity_allocated=5))
    order = Order(order_number="ORD-TEST-01", customer_name="Test Customer", order_type="STANDARD", priority="HIGH", status="NEW", requested_ship_date=date(2026, 8, 25))
    session.add(order)
    session.flush()
    line = OrderLine(order_id=order.id, item_id=item.id, line_number=1, quantity_ordered=2)
    session.add(line)
    session.flush()
    session.add(
        FulfillmentTask(task_number="TASK-TEST-01", order=order, order_line_id=line.id, warehouse_id=warehouse.id, task_type="PICK", status="OPEN", priority="HIGH")
    )
    session.add(Shipment(shipment_number="SHP-TEST-01", order=order, warehouse_id=warehouse.id, carrier="UPS", status="PLANNED"))
    session.add_all([
        SyntheticUser(user_code="USR-ORDER-MGR-01", display_name="Olivia Order Manager", persona="ORDER_MANAGER", department="Customer Operations", role="Order Manager", email="olivia.order.manager@example.com"),
        SyntheticUser(user_code="USR-WH-SUP-01", display_name="Sam Warehouse Supervisor", persona="WAREHOUSE_SUPERVISOR", department="Warehouse Operations", role="Warehouse Supervisor", email="sam.warehouse.supervisor@example.com"),
        SyntheticUser(user_code="USR-PICKER-01", display_name="Priya Picker", persona="PICKER", department="Warehouse Operations", role="Picker", email="priya.picker@example.com"),
        SyntheticUser(user_code="USR-PACKER-01", display_name="Peter Packer", persona="PACKER", department="Warehouse Operations", role="Packer", email="peter.packer@example.com"),
        SyntheticUser(user_code="USR-SHIP-01", display_name="Sofia Shipping Coordinator", persona="SHIPPING_COORDINATOR", department="Logistics", role="Shipping Coordinator", email="sofia.shipping@example.com"),
        SyntheticUser(user_code="USR-BIZ-USER-01", display_name="Ben Business User", persona="BUSINESS_USER", department="Commercial Operations", role="Business User", email="ben.business.user@example.com"),
    ])
    session.add_all([
        SyntheticJourney(journey_code="JRN-ORDER-FULFILL-SUCCESS", name="Successful Fulfillment", description="Create, allocate, pick, pack, and ship a small customer order.", persona="ORDER_MANAGER", journey_type="SUCCESS_PATH", expected_outcome="SUCCESS", creates_user_report_on_failure=False, creates_ticket_on_failure=False, enabled=True, default_payload={}),
        SyntheticJourney(journey_code="JRN-ALLOCATE-INSUFFICIENT-STOCK", name="Insufficient Stock Allocation Failure", description="Attempt to allocate an order that exceeds available inventory.", persona="ORDER_MANAGER", journey_type="FUNCTIONAL_FAILURE", expected_outcome="FAILED", creates_user_report_on_failure=True, creates_ticket_on_failure=True, enabled=True, default_payload={"quantity": 999999}),
        SyntheticJourney(journey_code="JRN-PACK-BEFORE-PICK", name="Pack Before Pick Functional Failure", description="Attempt to complete packing before the pick task is complete.", persona="PACKER", journey_type="VALIDATION_FAILURE", expected_outcome="FAILED", creates_user_report_on_failure=True, creates_ticket_on_failure=True, enabled=True, default_payload={}),
        SyntheticJourney(journey_code="JRN-SHIP-BEFORE-PACK", name="Ship Before Pack Functional Failure", description="Attempt to ship an order while packing is incomplete.", persona="SHIPPING_COORDINATOR", journey_type="VALIDATION_FAILURE", expected_outcome="FAILED", creates_user_report_on_failure=True, creates_ticket_on_failure=True, enabled=True, default_payload={"complete_pick": False}),
        SyntheticJourney(journey_code="JRN-MANUAL-FUNCTIONAL-ISSUE", name="Manual Functional Issue", description="Submit a business-user issue that is not automatically detected.", persona="BUSINESS_USER", journey_type="USER_REPORTED_ISSUE", expected_outcome="SUCCESS", creates_user_report_on_failure=True, creates_ticket_on_failure=True, enabled=True, default_payload={}),
    ])
    monitoring_components = [
        ("EOS-FRONTEND", "EOS Frontend", "FRONTEND", "PRESENTATION"),
        ("EOS-BACKEND-API", "EOS Backend API", "API", "APPLICATION"),
        ("EOS-POSTGRES", "EOS PostgreSQL", "DATABASE", "DATA"),
        ("EOS-REDIS", "EOS Redis", "CACHE", "CACHE"),
        ("WF-ORDER-WORKFLOW", "Warehouse Order Workflow", "WORKFLOW", "BUSINESS_WORKFLOW"),
        ("WF-INVENTORY-SERVICE", "Warehouse Inventory Service", "BUSINESS_PROCESS", "BUSINESS_WORKFLOW"),
        ("WF-SHIPMENT-SERVICE", "Warehouse Shipment Service", "BUSINESS_PROCESS", "BUSINESS_WORKFLOW"),
    ]
    component_rows = {}
    for code, name, component_type, layer in monitoring_components:
        component_rows[code] = MonComponent(component_code=code, name=name, component_type=component_type, layer=layer, environment="test", owner_team="Test Support", business_service="Warehouse & Fulfillment Operations", application_name="Enterprise Operations Suite", status="ACTIVE", description=name)
        session.add(component_rows[code])
    session.flush()
    monitoring_rules = [
        ("MON-API-LATENCY", "EOS-BACKEND-API", "api_latency_ms", "HIGH"), ("MON-API-ERROR", "EOS-BACKEND-API", "api_error_rate", "MEDIUM"),
        ("MON-FRONTEND-API", "EOS-FRONTEND", "frontend_api_failure_count", "HIGH"), ("MON-WORKFLOW-FAILURE", "WF-ORDER-WORKFLOW", "workflow_failure_count", "MEDIUM"),
        ("MON-DB-LATENCY", "EOS-POSTGRES", "db_latency_ms", "HIGH"), ("MON-INV-ALLOC", "WF-INVENTORY-SERVICE", "allocation_failure_count", "HIGH"),
        ("MON-REDIS-FLAP", "EOS-REDIS", "redis_connection_failures", "HIGH"), ("MON-SHIPMENT-EXC", "WF-SHIPMENT-SERVICE", "shipment_exception_count", "MEDIUM"),
        ("MON-WORKFLOW-HIGH", "WF-ORDER-WORKFLOW", "workflow_failure_count", "HIGH"), ("MON-WORKFLOW-LOW", "WF-ORDER-WORKFLOW", "workflow_failure_count", "LOW"),
    ]
    session.add_all([MonAlertRule(rule_code=code, name=code, description=code, component_id=component_rows[component].id, metric_name=metric, condition_operator="GT", threshold_value=1, severity=severity, enabled=True, dedupe_window_minutes=15) for code, component, metric, severity in monitoring_rules])
    batch_definitions = [
        ("BATCH-INV-RECON", "Nightly Inventory Reconciliation", "INVENTORY_RECONCILIATION", ["EXTRACT_INVENTORY_BALANCES", "VALIDATE_BALANCES", "RECONCILE_ON_HAND", "GENERATE_VARIANCE_REPORT", "PUBLISH_RESULTS"]),
        ("BATCH-ORDER-RELEASE", "Wave Order Release", "ORDER_RELEASE", ["SELECT_RELEASE_CANDIDATES", "VALIDATE_RELEASE_PREREQUISITES", "RELEASE_ORDERS", "PUBLISH_RELEASE_SUMMARY"]),
        ("BATCH-SHIP-SYNC", "Shipment Status Synchronization", "SHIPMENT_SYNC", ["EXTRACT_OPEN_SHIPMENTS", "SYNC_CARRIER_STATUS", "VALIDATE_STATUS_CHANGES", "PUBLISH_SHIPMENT_RESULTS"]),
        ("BATCH-LOW-STOCK", "Low Stock Notification Batch", "LOW_STOCK_NOTIFICATION", ["SCAN_LOW_STOCK", "BUILD_NOTIFICATION_PAYLOADS", "PUBLISH_NOTIFICATIONS", "RECORD_NOTIFICATION_RESULTS"]),
        ("BATCH-INV-SNAPSHOT", "Inventory Snapshot Batch", "INVENTORY_SNAPSHOT", ["EXTRACT_BALANCE_DATA", "VALIDATE_SNAPSHOT_DATA", "WRITE_SNAPSHOT", "PUBLISH_SNAPSHOT"]),
    ]
    for job_code, job_name, job_type, step_codes in batch_definitions:
        job = BatchJob(job_code=job_code, name=job_name, description=job_name, job_type=job_type, module="WAREHOUSE_FULFILLMENT", business_service="Warehouse & Fulfillment Operations", application_name="Enterprise Operations Suite", enabled=True, default_severity="MEDIUM", sla_minutes=60)
        session.add(job)
        session.flush()
        session.add_all([BatchJobStep(job_id=job.id, step_code=step_code, step_name=step_code.replace("_", " "), step_order=index, step_type="PROCESS", description=step_code, enabled=True, expected_duration_ms=1000) for index, step_code in enumerate(step_codes, 1)])
    session.add_all([CopilotSafeAction(action_code=code, name=name, description=description, target_module=module, action_type=action_type, risk_level=risk, requires_human_approval=True, enabled=True) for code, name, description, module, action_type, risk in SAFE_ACTIONS])
    provider_rows = {}
    for code, name, provider_type, description, base_url, auth_type, enabled, is_mock in PROVIDERS:
        provider_rows[code] = AiProvider(provider_code=code, name=name, provider_type=provider_type, description=description, base_url=base_url, auth_type=auth_type, enabled=enabled, is_mock=is_mock, default_timeout_seconds=30)
        session.add(provider_rows[code])
    session.flush()
    session.add(AiModelConfig(model_code="MOCK-SUPPORT-COPILOT-001", provider_id=provider_rows["MOCK_GOVERNED"].id, display_name="Mock Support Copilot", model_name="mock-governed-v1", model_family="DETERMINISTIC", purpose="GENERAL_TEST", enabled=True, is_default=True, temperature=0, top_p=1, max_output_tokens=1000, context_window_tokens=8000, cost_per_1k_input_tokens=0, cost_per_1k_output_tokens=0))
    session.add(AiModelConfig(model_code="DISABLED-EXTERNAL-001", provider_id=provider_rows["OPENAI_DISABLED_PLACEHOLDER"].id, display_name="Disabled External Placeholder", model_name="disabled-external", model_family="PLACEHOLDER", purpose="GENERAL_TEST", enabled=False, is_default=False, temperature=0, top_p=1, max_output_tokens=1000, context_window_tokens=8000, cost_per_1k_input_tokens=0, cost_per_1k_output_tokens=0))
    session.add_all([AiPromptTemplate(template_code=code, name=name, description=description, task_type=task_type, template_version=1, system_template=system_template, user_template=user_template, input_schema=input_schema, output_schema=output_schema, enabled=True, is_default=code == "TPL-GENERAL-TEST") for code, name, description, task_type, system_template, user_template, input_schema, output_schema in TEMPLATES])
    policy = AiSafetyPolicy(policy_code="POL-COPILOT-GOVERNANCE", name="Copilot Governance", description="Test safety policy.", policy_scope="GENERAL_INVOCATION", enabled=True, blocking_mode="BLOCK")
    session.add(policy)
    session.flush()
    session.add_all([AiSafetyPolicyRule(policy_id=policy.id, rule_code=code, name=name, description=description, rule_type=rule_type, severity=severity, enabled=True, match_pattern=pattern, action=action) for code, name, description, rule_type, severity, pattern, action in RULES])
    session.commit()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield client
    finally:
        app.dependency_overrides.pop(get_db, None)
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()
