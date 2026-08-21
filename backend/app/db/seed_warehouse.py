"""Idempotent demo seed for the Warehouse & Fulfillment domain."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import TypeVar

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models.warehouse import FulfillmentTask, InventoryBalance, Item, Location, Order, OrderLine, Shipment, Warehouse, Zone

T = TypeVar("T")


def _find_or_create(session: Session, model: type[T], lookup: dict[str, object], values: dict[str, object]) -> T:
    instance = session.scalar(select(model).filter_by(**lookup))
    if instance is None:
        instance = model(**{**values, **lookup})  # type: ignore[call-arg]
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
    now = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)

    with factory() as session:
        warehouses: dict[str, Warehouse] = {}
        for data in (
            {
                "code": "DAL-FC-01",
                "name": "Dallas Fulfillment Center",
                "region": "South Central",
                "city": "Dallas",
                "country": "USA",
            },
            {
                "code": "CHI-RDC-01",
                "name": "Chicago Regional Distribution Center",
                "region": "Midwest",
                "city": "Chicago",
                "country": "USA",
            },
        ):
            warehouses[data["code"]] = _find_or_create(session, Warehouse, {"code": data["code"]}, data)

        zones: dict[tuple[str, str], Zone] = {}
        zone_specs = (
            ("DAL-FC-01", "REC", "Receiving", "RECEIVING"),
            ("DAL-FC-01", "PICK", "Picking", "PICKING"),
            ("DAL-FC-01", "SHIP", "Shipping", "SHIPPING"),
            ("CHI-RDC-01", "REC", "Receiving", "RECEIVING"),
            ("CHI-RDC-01", "STOR", "Storage", "STORAGE"),
            ("CHI-RDC-01", "PACK", "Packing", "PACKING"),
        )
        for warehouse_code, code, name, zone_type in zone_specs:
            warehouse = warehouses[warehouse_code]
            zones[(warehouse_code, code)] = _find_or_create(
                session,
                Zone,
                {"warehouse_id": warehouse.id, "code": code},
                {"name": name, "zone_type": zone_type, "status": "ACTIVE"},
            )

        locations: dict[str, Location] = {}
        location_specs = (
            ("DAL-FC-01", "REC", "DAL-REC-D01", "DOCK", 500),
            ("DAL-FC-01", "REC", "DAL-REC-D02", "DOCK", 500),
            ("DAL-FC-01", "PICK", "DAL-PICK-A01-B01", "BIN", 120),
            ("DAL-FC-01", "PICK", "DAL-PICK-A01-B02", "BIN", 120),
            ("DAL-FC-01", "PICK", "DAL-PICK-A02-B01", "BIN", 120),
            ("DAL-FC-01", "SHIP", "DAL-SHIP-S01", "STAGING", 400),
            ("CHI-RDC-01", "REC", "CHI-REC-D01", "DOCK", 450),
            ("CHI-RDC-01", "REC", "CHI-REC-D02", "DOCK", 450),
            ("CHI-RDC-01", "STOR", "CHI-STOR-B02-L03", "RACK", 300),
            ("CHI-RDC-01", "STOR", "CHI-STOR-B02-L04", "RACK", 300),
            ("CHI-RDC-01", "PACK", "CHI-PACK-P01", "STAGING", 250),
            ("CHI-RDC-01", "PACK", "CHI-PACK-P02", "STAGING", 250),
        )
        for warehouse_code, zone_code, code, location_type, capacity_units in location_specs:
            warehouse = warehouses[warehouse_code]
            zone = zones[(warehouse_code, zone_code)]
            locations[code] = _find_or_create(
                session,
                Location,
                {"warehouse_id": warehouse.id, "code": code},
                {
                    "zone_id": zone.id,
                    "location_type": location_type,
                    "capacity_units": capacity_units,
                    "status": "ACTIVE",
                },
            )

        items: dict[str, Item] = {}
        item_specs = (
            ("SKU-1001", "Industrial Barcode Scanner", "Electronics", 40, 20),
            ("SKU-1002", "Wireless Handheld Terminal", "Electronics", 30, 15),
            ("SKU-2001", "Wireless Headset", "Accessories", 35, 18),
            ("SKU-2002", "USB-C Charging Dock", "Accessories", 25, 12),
            ("SKU-3001", "Shipping Carton - Medium", "Packaging", 80, 40),
            ("SKU-3002", "Thermal Label Roll", "Packaging", 60, 30),
            ("SKU-4001", "Conveyor Drive Belt", "Maintenance", 10, 5),
            ("SKU-4002", "Safety Cutter", "Maintenance", 25, 12),
        )
        for sku, name, category, reorder_point, safety_stock in item_specs:
            items[sku] = _find_or_create(
                session,
                Item,
                {"sku": sku},
                {
                    "name": name,
                    "category": category,
                    "unit_of_measure": "EA",
                    "reorder_point": reorder_point,
                    "safety_stock": safety_stock,
                    "active": True,
                },
            )

        inventory_specs = (
            ("DAL-FC-01", "DAL-PICK-A01-B01", "SKU-1001", 120, 24),
            ("DAL-FC-01", "DAL-PICK-A01-B02", "SKU-1002", 100, 20),
            ("DAL-FC-01", "DAL-PICK-A02-B01", "SKU-2001", 70, 10),
            ("DAL-FC-01", "DAL-SHIP-S01", "SKU-3001", 150, 30),
            ("DAL-FC-01", "DAL-REC-D01", "SKU-3002", 80, 12),
            ("DAL-FC-01", "DAL-REC-D02", "SKU-4001", 12, 5),
            ("DAL-FC-01", "DAL-PICK-A02-B01", "SKU-4002", 30, 8),
            ("DAL-FC-01", "DAL-PICK-A01-B01", "SKU-2002", 40, 15),
            ("CHI-RDC-01", "CHI-STOR-B02-L03", "SKU-1001", 150, 18),
            ("CHI-RDC-01", "CHI-STOR-B02-L04", "SKU-1002", 120, 12),
            ("CHI-RDC-01", "CHI-PACK-P01", "SKU-2001", 80, 8),
            ("CHI-RDC-01", "CHI-PACK-P02", "SKU-2002", 65, 10),
            ("CHI-RDC-01", "CHI-REC-D01", "SKU-3001", 110, 15),
            ("CHI-RDC-01", "CHI-REC-D02", "SKU-3002", 70, 8),
            ("CHI-RDC-01", "CHI-STOR-B02-L03", "SKU-4001", 5, 2),
            ("CHI-RDC-01", "CHI-STOR-B02-L04", "SKU-4002", 48, 6),
        )
        for warehouse_code, location_code, sku, on_hand, allocated in inventory_specs:
            _find_or_create(
                session,
                InventoryBalance,
                {"location_id": locations[location_code].id, "item_id": items[sku].id},
                {
                    "warehouse_id": warehouses[warehouse_code].id,
                    "quantity_on_hand": on_hand,
                    "quantity_allocated": allocated,
                },
            )

        orders: dict[str, Order] = {}
        order_specs = (
            ("ORD-2026-0001", "Northstar Retail Group", "HIGH", "ALLOCATED", 2),
            ("ORD-2026-0002", "Lone Star Office Supply", "NORMAL", "PICKING", 2),
            ("ORD-2026-0003", "Midwest Medical Services", "URGENT", "PACKING", 2),
            ("ORD-2026-0004", "Great Lakes Field Services", "NORMAL", "NEW", 2),
            ("ORD-2026-0005", "Prairie Tech Partners", "LOW", "SHIPPED", 2),
        )
        for number, customer, priority, order_status, _line_count in order_specs:
            orders[number] = _find_or_create(
                session,
                Order,
                {"order_number": number},
                {
                    "customer_name": customer,
                    "order_type": "STANDARD",
                    "priority": priority,
                    "status": order_status,
                    "requested_ship_date": date(2026, 8, 22),
                },
            )

        line_specs = (
            ("ORD-2026-0001", 1, "SKU-1001", 4, 4, 0),
            ("ORD-2026-0001", 2, "SKU-2001", 6, 6, 0),
            ("ORD-2026-0002", 1, "SKU-1002", 3, 3, 0),
            ("ORD-2026-0002", 2, "SKU-3002", 5, 5, 0),
            ("ORD-2026-0003", 1, "SKU-2002", 2, 2, 0),
            ("ORD-2026-0003", 2, "SKU-3001", 10, 10, 0),
            ("ORD-2026-0004", 1, "SKU-4002", 4, 0, 0),
            ("ORD-2026-0004", 2, "SKU-1001", 1, 0, 0),
            ("ORD-2026-0005", 1, "SKU-4001", 2, 2, 2),
            ("ORD-2026-0005", 2, "SKU-2002", 3, 3, 3),
        )
        lines: dict[tuple[str, int], OrderLine] = {}
        for order_number, line_number, sku, ordered, allocated, shipped in line_specs:
            lines[(order_number, line_number)] = _find_or_create(
                session,
                OrderLine,
                {"order_id": orders[order_number].id, "line_number": line_number},
                {
                    "item_id": items[sku].id,
                    "quantity_ordered": ordered,
                    "quantity_allocated": allocated,
                    "quantity_shipped": shipped,
                },
            )

        task_specs = (
            ("TASK-2026-0001", "ORD-2026-0001", 1, "DAL-FC-01", "PICK", "OPEN", "HIGH", "Jordan Lee", 1),
            ("TASK-2026-0002", "ORD-2026-0001", 2, "DAL-FC-01", "PICK", "IN_PROGRESS", "HIGH", "Morgan Patel", 1),
            ("TASK-2026-0003", "ORD-2026-0002", 1, "DAL-FC-01", "PICK", "OPEN", "NORMAL", None, 2),
            ("TASK-2026-0004", "ORD-2026-0002", 2, "DAL-FC-01", "PACK", "OPEN", "NORMAL", "Casey Nguyen", 2),
            ("TASK-2026-0005", "ORD-2026-0003", 1, "CHI-RDC-01", "PACK", "IN_PROGRESS", "URGENT", "Taylor Brooks", 1),
            ("TASK-2026-0006", "ORD-2026-0003", 2, "CHI-RDC-01", "SHIP", "CANCELLED", "URGENT", None, 1),
            ("TASK-2026-0007", "ORD-2026-0004", 1, "CHI-RDC-01", "PICK", "BLOCKED", "NORMAL", "Riley Chen", 3),
            ("TASK-2026-0008", "ORD-2026-0005", None, "CHI-RDC-01", "SHIP", "COMPLETED", "LOW", "Alex Garcia", 0),
        )
        for task_number, order_number, line_number, warehouse_code, task_type, task_status, priority, assigned_to, due_days in task_specs:
            _find_or_create(
                session,
                FulfillmentTask,
                {"task_number": task_number},
                {
                    "order_id": orders[order_number].id,
                    "order_line_id": lines[(order_number, line_number)].id if line_number else None,
                    "warehouse_id": warehouses[warehouse_code].id,
                    "task_type": task_type,
                    "status": task_status,
                    "priority": priority,
                    "assigned_to": assigned_to,
                    "due_at": now + timedelta(days=due_days),
                },
            )

        shipment_specs = (
            ("SHP-2026-0001", "ORD-2026-0001", "DAL-FC-01", "UPS", "1Z999AA10123456784", "READY", None),
            ("SHP-2026-0002", "ORD-2026-0002", "DAL-FC-01", "FedEx", "771234567890", "PLANNED", None),
            ("SHP-2026-0003", "ORD-2026-0003", "CHI-RDC-01", "DHL", "DHLUS123456789", "EXCEPTION", None),
            ("SHP-2026-0004", "ORD-2026-0005", "CHI-RDC-01", "UPS", "1Z999AA10123456785", "SHIPPED", now - timedelta(days=1)),
        )
        for shipment_number, order_number, warehouse_code, carrier, tracking, shipment_status, shipped_at in shipment_specs:
            _find_or_create(
                session,
                Shipment,
                {"shipment_number": shipment_number},
                {
                    "order_id": orders[order_number].id,
                    "warehouse_id": warehouses[warehouse_code].id,
                    "carrier": carrier,
                    "tracking_number": tracking,
                    "status": shipment_status,
                    "shipped_at": shipped_at,
                },
            )

        session.commit()
        result = {
            "warehouses": len(warehouses),
            "zones": len(zones),
            "locations": len(locations),
            "items": len(items),
            "inventory_balances": len(inventory_specs),
            "orders": len(orders),
            "order_lines": len(line_specs),
            "fulfillment_tasks": len(task_specs),
            "shipments": len(shipment_specs),
        }
    engine.dispose()
    return result


if __name__ == "__main__":
    counts = seed()
    print("Warehouse seed complete: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
