from types import SimpleNamespace

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine

from app.db.base import Base
from app.db import seed_synthetic_users


@pytest.mark.anyio
async def test_synthetic_catalog_lists_users_and_journeys(warehouse_client: AsyncClient):
    users = await warehouse_client.get("/api/v1/synthetic-users/users")
    journeys = await warehouse_client.get("/api/v1/synthetic-users/journeys")
    assert users.status_code == 200
    assert len(users.json()) == 6
    assert journeys.status_code == 200
    assert [journey["journey_code"] for journey in journeys.json()] == [
        "JRN-ALLOCATE-INSUFFICIENT-STOCK",
        "JRN-MANUAL-FUNCTIONAL-ISSUE",
        "JRN-ORDER-FULFILL-SUCCESS",
        "JRN-PACK-BEFORE-PICK",
        "JRN-SHIP-BEFORE-PACK",
    ]


@pytest.mark.anyio
async def test_successful_fulfillment_journey_has_no_report_or_ticket(warehouse_client: AsyncClient):
    response = await warehouse_client.post("/api/v1/synthetic-users/journeys/JRN-ORDER-FULFILL-SUCCESS/run", json={"create_ticket": True})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "SUCCESS"
    assert body["order_id"]
    assert body["shipment_id"]
    assert body["user_report_id"] is None
    assert body["ticket_id"] is None


@pytest.mark.anyio
async def test_failed_journeys_create_user_reports_and_optional_ticket(warehouse_client: AsyncClient):
    insufficient = await warehouse_client.post(
        "/api/v1/synthetic-users/journeys/JRN-ALLOCATE-INSUFFICIENT-STOCK/run", json={"create_ticket": True}
    )
    assert insufficient.status_code == 200
    first = insufficient.json()
    assert first["status"] == "FAILED"
    assert first["failure_type"] == "INSUFFICIENT_STOCK"
    assert first["user_report_id"]
    assert first["ticket_id"]

    pack = await warehouse_client.post("/api/v1/synthetic-users/journeys/JRN-PACK-BEFORE-PICK/run", json={"create_ticket": False})
    ship = await warehouse_client.post("/api/v1/synthetic-users/journeys/JRN-SHIP-BEFORE-PACK/run", json={"create_ticket": False})
    assert pack.json()["status"] == "FAILED"
    assert pack.json()["failure_type"] == "PACK_BEFORE_PICK"
    assert ship.json()["status"] == "FAILED"
    assert ship.json()["failure_type"] == "SHIP_BEFORE_PACK"
    assert pack.json()["user_report_id"] and pack.json()["ticket_id"] is None
    assert ship.json()["user_report_id"] and ship.json()["ticket_id"] is None


@pytest.mark.anyio
async def test_manual_issue_and_report_lifecycle_prevents_duplicate_ticket(warehouse_client: AsyncClient):
    manual = await warehouse_client.post("/api/v1/synthetic-users/journeys/JRN-MANUAL-FUNCTIONAL-ISSUE/run", json={"create_ticket": False})
    report_id = manual.json()["user_report_id"]
    assert manual.json()["status"] == "SUCCESS"
    report = await warehouse_client.get(f"/api/v1/ams/user-reports/{report_id}")
    assert report.json()["status"] == "SUBMITTED"
    first_ticket = await warehouse_client.post(f"/api/v1/ams/user-reports/{report_id}/create-ticket")
    duplicate_ticket = await warehouse_client.post(f"/api/v1/ams/user-reports/{report_id}/create-ticket")
    assert first_ticket.status_code == 200
    assert duplicate_ticket.status_code == 200
    assert first_ticket.json()["ticket"]["id"] == duplicate_ticket.json()["ticket"]["id"]
    acknowledged = await warehouse_client.post(f"/api/v1/ams/user-reports/{report_id}/acknowledge")
    resolved = await warehouse_client.post(f"/api/v1/ams/user-reports/{report_id}/resolve")
    assert acknowledged.json()["status"] == "ACKNOWLEDGED"
    assert resolved.json()["status"] == "RESOLVED"
    assert resolved.json()["ticket"]["status"] == "NEW"


@pytest.mark.anyio
async def test_run_suite_and_run_list(warehouse_client: AsyncClient):
    suite = await warehouse_client.post("/api/v1/synthetic-users/run-suite", json={"create_ticket": False})
    assert suite.status_code == 200
    assert suite.json()["total"] == 5
    assert suite.json()["succeeded"] == 2
    assert suite.json()["failed"] == 3
    runs = await warehouse_client.get("/api/v1/synthetic-users/runs?status=FAILED")
    assert runs.status_code == 200
    assert len(runs.json()) == 3
    assert all(run["failure_message"] for run in runs.json())


@pytest.mark.anyio
async def test_manual_user_report_and_filters(warehouse_client: AsyncClient):
    created = await warehouse_client.post(
        "/api/v1/ams/user-reports",
        json={
            "reporter_name": "Ben Business User",
            "reporter_email": "ben@example.com",
            "reporter_persona": "BUSINESS_USER",
            "report_channel": "USER_PORTAL",
            "affected_entity_type": "SCREEN",
            "title": "Unable to understand order status",
            "description": "The dashboard status is unclear.",
            "business_impact": "Customer response is delayed.",
            "severity": "HIGH",
            "create_ticket": True,
        },
    )
    assert created.status_code == 201
    assert created.json()["status"] == "TICKET_CREATED"
    assert created.json()["ticket"]["priority"] == "P2"
    listed = await warehouse_client.get("/api/v1/ams/user-reports?severity=HIGH&status=TICKET_CREATED")
    assert listed.status_code == 200
    assert listed.json()[0]["report_number"].startswith("USR-RPT-")


def test_synthetic_seed_is_idempotent(tmp_path):
    database_path = tmp_path / "synthetic-seed.db"
    engine = create_engine(f"sqlite+pysqlite:///{database_path}")
    Base.metadata.create_all(engine)
    original = seed_synthetic_users.get_settings
    seed_synthetic_users.get_settings = lambda: SimpleNamespace(database_url=f"sqlite+pysqlite:///{database_path}")
    try:
        assert seed_synthetic_users.seed() == {"synthetic_users": 6, "synthetic_journeys": 5}
        assert seed_synthetic_users.seed() == {"synthetic_users": 6, "synthetic_journeys": 5}
    finally:
        seed_synthetic_users.get_settings = original
        engine.dispose()

