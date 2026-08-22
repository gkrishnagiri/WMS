import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_low_stock_detection_and_simulation_creates_one_linked_ticket(warehouse_client: AsyncClient):
    detected = await warehouse_client.post("/api/v1/operations/detect/low-stock")
    assert detected.status_code == 200
    assert detected.json() == []

    simulated = await warehouse_client.post("/api/v1/operations/simulations/low-stock", json={"create_ticket": True})
    assert simulated.status_code == 200
    body = simulated.json()
    assert body["exception"]["exception_type"] == "LOW_STOCK"
    assert body["exception"]["status"] == "LINKED_TO_TICKET"
    assert body["ticket"]["ticket_number"].startswith("AMS-INC-")
    assert body["ticket"]["priority"] in {"P1", "P2", "P3", "P4"}

    repeated = await warehouse_client.post("/api/v1/operations/simulations/low-stock", json={"create_ticket": True})
    assert repeated.status_code == 200
    assert repeated.json()["exception"]["id"] == body["exception"]["id"]
    assert (await warehouse_client.get("/api/v1/ams/tickets")).json().__len__() == 1


@pytest.mark.anyio
async def test_task_shipment_and_order_simulations_record_exceptions(warehouse_client: AsyncClient):
    task = (await warehouse_client.get("/api/v1/warehouse/tasks?status=OPEN")).json()[0]
    task_result = await warehouse_client.post(
        "/api/v1/operations/simulations/task-blocked",
        json={"task_id": task["id"], "reason": "Picker device unavailable", "create_ticket": False},
    )
    assert task_result.status_code == 200
    assert task_result.json()["exception"]["exception_type"] == "TASK_BLOCKED"
    assert (await warehouse_client.get(f"/api/v1/warehouse/tasks?status=BLOCKED")).json()[0]["id"] == task["id"]

    shipment = (await warehouse_client.get("/api/v1/warehouse/shipments?status=PLANNED")).json()[0]
    shipment_result = await warehouse_client.post(
        "/api/v1/operations/simulations/shipment-exception",
        json={"shipment_id": shipment["id"], "reason": "Carrier label generation failed", "create_ticket": False},
    )
    assert shipment_result.status_code == 200
    assert shipment_result.json()["exception"]["exception_type"] == "SHIPMENT_EXCEPTION"

    order = (await warehouse_client.get("/api/v1/warehouse/orders?status=NEW")).json()[0]
    order_result = await warehouse_client.post(
        "/api/v1/operations/simulations/order-stuck",
        json={"order_id": order["id"], "status": "PICKING", "create_ticket": False},
    )
    assert order_result.status_code == 200
    assert order_result.json()["exception"]["exception_type"] == "ORDER_STUCK"
    assert (await warehouse_client.post("/api/v1/operations/detect/order-stuck", json={"threshold_hours": 24})).status_code == 200


@pytest.mark.anyio
async def test_ticket_creation_lifecycle_and_exception_linkage(warehouse_client: AsyncClient):
    exception = (
        await warehouse_client.post(
            "/api/v1/operations/simulations/task-blocked", json={"create_ticket": False, "reason": "Blocked for support test"}
        )
    ).json()["exception"]
    created = await warehouse_client.post(f"/api/v1/ams/tickets/from-exception/{exception['id']}")
    assert created.status_code == 201
    ticket = created.json()
    duplicate = await warehouse_client.post(f"/api/v1/ams/tickets/from-exception/{exception['id']}")
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == ticket["id"]

    acknowledged = await warehouse_client.post(f"/api/v1/ams/tickets/{ticket['id']}/acknowledge")
    assert acknowledged.status_code == 200
    assert acknowledged.json()["status"] == "ACKNOWLEDGED"
    started = await warehouse_client.post(f"/api/v1/ams/tickets/{ticket['id']}/start-work")
    assert started.json()["status"] == "IN_PROGRESS"
    resolved = await warehouse_client.post(
        f"/api/v1/ams/tickets/{ticket['id']}/resolve",
        json={"resolution_code": "WORKAROUND_APPLIED", "resolution_notes": "Reset simulated blocked workflow state."},
    )
    assert resolved.json()["status"] == "RESOLVED"
    assert resolved.json()["exception"]["status"] == "RESOLVED"
    closed = await warehouse_client.post(f"/api/v1/ams/tickets/{ticket['id']}/close")
    assert closed.json()["status"] == "CLOSED"
    assert len((await warehouse_client.get(f"/api/v1/ams/tickets/{ticket['id']}/events")).json()) == 5


@pytest.mark.anyio
async def test_invalid_ticket_transition_and_summary(warehouse_client: AsyncClient):
    created = await warehouse_client.post(
        "/api/v1/ams/tickets",
        json={"short_description": "Manual support ticket", "description": "Manual demo scenario"},
    )
    assert created.status_code == 201
    ticket_id = created.json()["id"]
    assert (await warehouse_client.post(f"/api/v1/ams/tickets/{ticket_id}/close")).status_code == 409
    summary = await warehouse_client.get("/api/v1/ams/summary")
    assert summary.status_code == 200
    assert summary.json()["open_tickets"] == 1


@pytest.mark.anyio
async def test_exception_list_filters_and_actions(warehouse_client: AsyncClient):
    exception = (
        await warehouse_client.post(
            "/api/v1/operations/simulations/low-stock", json={"create_ticket": False}
        )
    ).json()["exception"]
    listed = await warehouse_client.get("/api/v1/operations/exceptions?exception_type=LOW_STOCK&status=OPEN")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == exception["id"]
    acknowledged = await warehouse_client.post(f"/api/v1/operations/exceptions/{exception['id']}/acknowledge")
    assert acknowledged.json()["status"] == "ACKNOWLEDGED"
    resolved = await warehouse_client.post(f"/api/v1/operations/exceptions/{exception['id']}/resolve")
    assert resolved.json()["status"] == "RESOLVED"
