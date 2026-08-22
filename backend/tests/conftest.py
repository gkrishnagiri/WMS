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
