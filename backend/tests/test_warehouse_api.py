from datetime import date

import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.warehouse import FulfillmentTask, InventoryBalance, Item, Location, Order, OrderLine, Shipment, Warehouse, Zone


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

    warehouse = Warehouse(
        code="TEST-FC-01",
        name="Test Fulfillment Center",
        region="Test Region",
        city="Test City",
        country="USA",
    )
    zone = Zone(warehouse=warehouse, code="PICK", name="Picking", zone_type="PICKING")
    location = Location(warehouse=warehouse, zone=zone, code="TEST-PICK-01", location_type="BIN", capacity_units=100)
    item = Item(sku="SKU-TEST-01", name="Test Scanner", category="Electronics", reorder_point=10, safety_stock=5)
    session.add_all([warehouse, zone, location, item])
    session.flush()
    balance = InventoryBalance(
        warehouse_id=warehouse.id,
        location_id=location.id,
        item_id=item.id,
        quantity_on_hand=20,
        quantity_allocated=5,
    )
    order = Order(
        order_number="ORD-TEST-01",
        customer_name="Test Customer",
        order_type="STANDARD",
        priority="HIGH",
        status="NEW",
        requested_ship_date=date(2026, 8, 25),
    )
    session.add(order)
    session.flush()
    line = OrderLine(order_id=order.id, item_id=item.id, line_number=1, quantity_ordered=2)
    session.add(line)
    session.flush()
    task = FulfillmentTask(
        task_number="TASK-TEST-01",
        order=order,
        order_line_id=line.id,
        warehouse_id=warehouse.id,
        task_type="PICK",
        status="OPEN",
        priority="HIGH",
    )
    shipment = Shipment(
        shipment_number="SHP-TEST-01",
        order=order,
        warehouse_id=warehouse.id,
        carrier="UPS",
        status="PLANNED",
    )
    session.add_all([balance, task, shipment])
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
