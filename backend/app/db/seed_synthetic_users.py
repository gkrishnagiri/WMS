"""Idempotent seed for synthetic users and deterministic journey catalog."""

from __future__ import annotations

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models.synthetic_users import SyntheticJourney, SyntheticUser


def _find_or_create(session: Session, model: type, lookup: dict[str, object], values: dict[str, object]):
    instance = session.scalar(select(model).filter_by(**lookup))
    if instance is None:
        instance = model(**{**values, **lookup})
        session.add(instance)
        session.flush()
    else:
        for key, value in values.items():
            setattr(instance, key, value)
    return instance


def seed() -> dict[str, int]:
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    users = (
        ("USR-ORDER-MGR-01", "Olivia Order Manager", "ORDER_MANAGER", "Customer Operations", "Order Manager", "olivia.order.manager@example.com"),
        ("USR-WH-SUP-01", "Sam Warehouse Supervisor", "WAREHOUSE_SUPERVISOR", "Warehouse Operations", "Warehouse Supervisor", "sam.warehouse.supervisor@example.com"),
        ("USR-PICKER-01", "Priya Picker", "PICKER", "Warehouse Operations", "Picker", "priya.picker@example.com"),
        ("USR-PACKER-01", "Peter Packer", "PACKER", "Warehouse Operations", "Packer", "peter.packer@example.com"),
        ("USR-SHIP-01", "Sofia Shipping Coordinator", "SHIPPING_COORDINATOR", "Logistics", "Shipping Coordinator", "sofia.shipping@example.com"),
        ("USR-BIZ-USER-01", "Ben Business User", "BUSINESS_USER", "Commercial Operations", "Business User", "ben.business.user@example.com"),
    )
    journeys = (
        ("JRN-ORDER-FULFILL-SUCCESS", "Successful Fulfillment", "Create, allocate, pick, pack, and ship a small customer order.", "ORDER_MANAGER", "SUCCESS_PATH", "SUCCESS", False, False, {}),
        ("JRN-ALLOCATE-INSUFFICIENT-STOCK", "Insufficient Stock Allocation Failure", "Attempt to allocate an order that exceeds available inventory.", "ORDER_MANAGER", "FUNCTIONAL_FAILURE", "FAILED", True, True, {"quantity": 999999}),
        ("JRN-PACK-BEFORE-PICK", "Pack Before Pick Functional Failure", "Attempt to complete packing before the pick task is complete.", "PACKER", "VALIDATION_FAILURE", "FAILED", True, True, {}),
        ("JRN-SHIP-BEFORE-PACK", "Ship Before Pack Functional Failure", "Attempt to ship an order while packing is incomplete.", "SHIPPING_COORDINATOR", "VALIDATION_FAILURE", "FAILED", True, True, {"complete_pick": False}),
        ("JRN-MANUAL-FUNCTIONAL-ISSUE", "Manual Functional Issue", "Submit a business-user issue that is not automatically detected.", "BUSINESS_USER", "USER_REPORTED_ISSUE", "SUCCESS", True, True, {}),
    )
    with factory() as session:
        for code, display_name, persona, department, role, email in users:
            _find_or_create(session, SyntheticUser, {"user_code": code}, {"display_name": display_name, "persona": persona, "department": department, "role": role, "email": email, "active": True})
        for code, name, description, persona, journey_type, expected, report_on_failure, ticket_on_failure, payload in journeys:
            _find_or_create(session, SyntheticJourney, {"journey_code": code}, {"name": name, "description": description, "persona": persona, "journey_type": journey_type, "expected_outcome": expected, "creates_user_report_on_failure": report_on_failure, "creates_ticket_on_failure": ticket_on_failure, "enabled": True, "default_payload": payload})
        session.commit()
    engine.dispose()
    return {"synthetic_users": len(users), "synthetic_journeys": len(journeys)}


if __name__ == "__main__":
    counts = seed()
    print("Synthetic user seed complete: " + ", ".join(f"{key}={value}" for key, value in counts.items()))

