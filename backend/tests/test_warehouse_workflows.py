import pytest
from httpx import AsyncClient


async def _workflow_context(client: AsyncClient) -> tuple[str, str]:
    warehouse = (await client.get("/api/v1/warehouse/warehouses")).json()[0]
    item = (await client.get("/api/v1/warehouse/items")).json()[0]
    return warehouse["id"], item["id"]


@pytest.mark.anyio
async def test_create_allocate_release_and_ship_workflow(warehouse_client: AsyncClient):
    warehouse_id, item_id = await _workflow_context(warehouse_client)
    inventory_before = (await warehouse_client.get(f"/api/v1/warehouse/inventory?warehouse_id={warehouse_id}")).json()[0]
    created = await warehouse_client.post(
        "/api/v1/warehouse/orders",
        json={
            "customer_name": "Workflow Customer",
            "order_type": "STANDARD",
            "priority": "NORMAL",
            "requested_ship_date": "2026-08-25",
            "warehouse_id": warehouse_id,
            "lines": [{"item_id": item_id, "quantity_ordered": 2}],
        },
    )
    assert created.status_code == 201
    order = created.json()
    assert order["status"] == "NEW"
    assert order["events"][0]["event_type"] == "ORDER_CREATED"

    allocated = await warehouse_client.post(f"/api/v1/warehouse/orders/{order['id']}/allocate")
    assert allocated.status_code == 200
    assert allocated.json()["status"] == "ALLOCATED"
    assert len(allocated.json()["allocations"]) == 1

    released = await warehouse_client.post(f"/api/v1/warehouse/orders/{order['id']}/release-tasks")
    assert released.status_code == 200
    assert released.json()["status"] == "PICKING"
    assert len(released.json()["tasks"]) == 2

    released_again = await warehouse_client.post(f"/api/v1/warehouse/orders/{order['id']}/release-tasks")
    assert released_again.status_code == 200
    assert len(released_again.json()["tasks"]) == 2

    pick_task = next(task for task in released.json()["tasks"] if task["task_type"] == "PICK")
    pack_task = next(task for task in released.json()["tasks"] if task["task_type"] == "PACK")
    assert (await warehouse_client.post(f"/api/v1/warehouse/tasks/{pick_task['id']}/start")).status_code == 200
    completed_pick = await warehouse_client.post(f"/api/v1/warehouse/tasks/{pick_task['id']}/complete")
    assert completed_pick.status_code == 200
    assert completed_pick.json()["status"] == "COMPLETED"

    assert (await warehouse_client.post(f"/api/v1/warehouse/tasks/{pack_task['id']}/start")).status_code == 200
    completed_pack = await warehouse_client.post(f"/api/v1/warehouse/tasks/{pack_task['id']}/complete")
    assert completed_pack.status_code == 200

    shipped = await warehouse_client.post(
        f"/api/v1/warehouse/orders/{order['id']}/ship",
        json={"carrier": "UPS", "tracking_number": "1Z999EOS0001", "shipped_by": "test"},
    )
    assert shipped.status_code == 200
    assert shipped.json()["status"] == "SHIPPED"
    assert shipped.json()["shipments"][0]["status"] == "SHIPPED"
    assert [event["event_type"] for event in shipped.json()["events"]][:2] == ["ORDER_SHIPPED", "TASK_COMPLETED"]

    transactions = (
        await warehouse_client.get(f"/api/v1/warehouse/inventory-transactions?order_id={order['id']}")
    ).json()
    assert {transaction["transaction_type"] for transaction in transactions} == {
        "ALLOCATION_RESERVE",
        "PICK_CONFIRM",
        "PACK_CONFIRM",
        "SHIPMENT_ISSUE",
    }
    shipment_issue = next(transaction for transaction in transactions if transaction["transaction_type"] == "SHIPMENT_ISSUE")
    assert shipment_issue["quantity_on_hand_delta"] == -2
    assert shipment_issue["quantity_allocated_delta"] == -2
    inventory_after = (await warehouse_client.get(f"/api/v1/warehouse/inventory?warehouse_id={warehouse_id}")).json()[0]
    assert inventory_after["quantity_on_hand"] == inventory_before["quantity_on_hand"] - 2
    assert inventory_after["quantity_allocated"] == inventory_before["quantity_allocated"]


@pytest.mark.anyio
async def test_insufficient_allocation_has_no_partial_state(warehouse_client: AsyncClient):
    warehouse_id, item_id = await _workflow_context(warehouse_client)
    created = await warehouse_client.post(
        "/api/v1/warehouse/orders",
        json={"customer_name": "Insufficient Customer", "warehouse_id": warehouse_id, "lines": [{"item_id": item_id, "quantity_ordered": 999}]},
    )
    order = created.json()
    response = await warehouse_client.post(f"/api/v1/warehouse/orders/{order['id']}/allocate")
    assert response.status_code == 409
    assert "Insufficient available inventory" in response.json()["detail"]
    detail = (await warehouse_client.get(f"/api/v1/warehouse/orders/{order['id']}")).json()
    assert detail["status"] == "NEW"
    assert detail["allocations"] == []
    assert (await warehouse_client.get(f"/api/v1/warehouse/inventory-transactions?order_id={order['id']}")).json() == []


@pytest.mark.anyio
async def test_invalid_workflow_transitions_return_conflict(warehouse_client: AsyncClient):
    warehouse_id, item_id = await _workflow_context(warehouse_client)
    created = await warehouse_client.post(
        "/api/v1/warehouse/orders",
        json={"customer_name": "Invalid Transition Customer", "warehouse_id": warehouse_id, "lines": [{"item_id": item_id, "quantity_ordered": 1}]},
    )
    order_id = created.json()["id"]
    assert (await warehouse_client.post(f"/api/v1/warehouse/orders/{order_id}/release-tasks")).status_code == 409
    assert (await warehouse_client.post(f"/api/v1/warehouse/orders/{order_id}/allocate")).status_code == 200
    assert (await warehouse_client.post(f"/api/v1/warehouse/orders/{order_id}/allocate")).status_code == 409
