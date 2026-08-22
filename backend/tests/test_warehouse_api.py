import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_warehouse_summary(warehouse_client: AsyncClient):
    response = await warehouse_client.get("/api/v1/warehouse/summary")
    assert response.status_code == 200
    assert response.json() == {
        "warehouses": 1,
        "locations": 1,
        "items": 1,
        "inventory_units_on_hand": 20,
        "open_orders": 1,
        "open_tasks": 1,
        "shipments_in_progress": 1,
        "low_stock_items": 0,
    }


@pytest.mark.anyio
async def test_warehouse_list(warehouse_client: AsyncClient):
    response = await warehouse_client.get("/api/v1/warehouse/warehouses?status=ACTIVE")
    assert response.status_code == 200
    assert response.json()[0]["code"] == "TEST-FC-01"
    assert response.json()[0]["location_count"] == 1


@pytest.mark.anyio
async def test_item_list_supports_search(warehouse_client: AsyncClient):
    response = await warehouse_client.get("/api/v1/warehouse/items?search=scanner")
    assert response.status_code == 200
    assert [item["sku"] for item in response.json()] == ["SKU-TEST-01"]


@pytest.mark.anyio
async def test_inventory_exposes_available_and_low_stock(warehouse_client: AsyncClient):
    response = await warehouse_client.get("/api/v1/warehouse/inventory?low_stock_only=true")
    assert response.status_code == 200
    assert response.json() == []

    response = await warehouse_client.get("/api/v1/warehouse/inventory")
    body = response.json()
    assert response.status_code == 200
    assert body[0]["quantity_available"] == 15
    assert body[0]["low_stock"] is False
