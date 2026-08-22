"""Read-focused service operations for the Warehouse & Fulfillment domain."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.warehouse import (
    FulfillmentTask,
    InventoryBalance,
    Item,
    Location,
    Order,
    OrderLine,
    Shipment,
    Warehouse,
    Zone,
)
from app.schemas.warehouse import (
    InventoryResponse,
    ItemResponse,
    OrderResponse,
    ShipmentResponse,
    TaskResponse,
    WarehouseDetail,
    WarehouseResponse,
    WarehouseSummary,
    ZoneSummary,
)


def get_summary(db: Session) -> WarehouseSummary:
    total_on_hand = db.scalar(select(func.coalesce(func.sum(InventoryBalance.quantity_on_hand), 0))) or 0
    low_stock_items = db.scalar(
        select(func.count(func.distinct(InventoryBalance.item_id)))
        .join(Item, Item.id == InventoryBalance.item_id)
        .where(InventoryBalance.quantity_on_hand - InventoryBalance.quantity_allocated <= Item.reorder_point)
    ) or 0
    return WarehouseSummary(
        warehouses=db.scalar(select(func.count(Warehouse.id))) or 0,
        locations=db.scalar(select(func.count(Location.id))) or 0,
        items=db.scalar(select(func.count(Item.id)).where(Item.active.is_(True))) or 0,
        inventory_units_on_hand=total_on_hand,
        open_orders=db.scalar(select(func.count(Order.id)).where(Order.status.not_in(("SHIPPED", "CANCELLED")))) or 0,
        open_tasks=db.scalar(
            select(func.count(FulfillmentTask.id)).where(FulfillmentTask.status.not_in(("COMPLETED", "CANCELLED")))
        ) or 0,
        shipments_in_progress=db.scalar(
            select(func.count(Shipment.id)).where(Shipment.status.in_(("PLANNED", "READY")))
        ) or 0,
        low_stock_items=low_stock_items,
    )


def list_warehouses(db: Session, status: str | None = None) -> list[WarehouseResponse]:
    statement = select(Warehouse).options(selectinload(Warehouse.zones), selectinload(Warehouse.locations)).order_by(Warehouse.code)
    if status:
        statement = statement.where(Warehouse.status == status.upper())
    return [
        WarehouseResponse(
            id=warehouse.id,
            code=warehouse.code,
            name=warehouse.name,
            region=warehouse.region,
            city=warehouse.city,
            country=warehouse.country,
            status=warehouse.status,
            zone_count=len(warehouse.zones),
            location_count=len(warehouse.locations),
        )
        for warehouse in db.scalars(statement).all()
    ]


def get_warehouse(db: Session, warehouse_id: UUID) -> WarehouseDetail | None:
    statement = select(Warehouse).where(Warehouse.id == warehouse_id).options(
        selectinload(Warehouse.zones).selectinload(Zone.locations),
        selectinload(Warehouse.locations),
    )
    warehouse = db.scalar(statement)
    if warehouse is None:
        return None
    return WarehouseDetail(
        id=warehouse.id,
        code=warehouse.code,
        name=warehouse.name,
        region=warehouse.region,
        city=warehouse.city,
        country=warehouse.country,
        status=warehouse.status,
        zone_count=len(warehouse.zones),
        location_count=len(warehouse.locations),
        zones=[
            ZoneSummary(
                id=zone.id,
                code=zone.code,
                name=zone.name,
                zone_type=zone.zone_type,
                status=zone.status,
                location_count=len(zone.locations),
            )
            for zone in warehouse.zones
        ],
    )


def list_items(
    db: Session, active: bool | None = None, category: str | None = None, search: str | None = None
) -> list[ItemResponse]:
    statement = select(Item).order_by(Item.sku)
    if active is not None:
        statement = statement.where(Item.active.is_(active))
    if category:
        statement = statement.where(Item.category.ilike(category))
    if search:
        pattern = f"%{search}%"
        statement = statement.where(or_(Item.sku.ilike(pattern), Item.name.ilike(pattern)))
    return [ItemResponse.model_validate(item) for item in db.scalars(statement).all()]


def list_inventory(
    db: Session, warehouse_id: UUID | None = None, sku: str | None = None, low_stock_only: bool = False
) -> list[InventoryResponse]:
    statement = (
        select(InventoryBalance, Warehouse, Location, Item)
        .join(Warehouse, Warehouse.id == InventoryBalance.warehouse_id)
        .join(Location, Location.id == InventoryBalance.location_id)
        .join(Item, Item.id == InventoryBalance.item_id)
        .order_by(Warehouse.code, Location.code, Item.sku)
    )
    if warehouse_id:
        statement = statement.where(InventoryBalance.warehouse_id == warehouse_id)
    if sku:
        statement = statement.where(Item.sku.ilike(f"%{sku}%"))
    if low_stock_only:
        statement = statement.where(InventoryBalance.quantity_on_hand - InventoryBalance.quantity_allocated <= Item.reorder_point)
    return [
        InventoryResponse(
            id=balance.id,
            warehouse_id=warehouse.id,
            warehouse_code=warehouse.code,
            warehouse_name=warehouse.name,
            location_id=location.id,
            location_code=location.code,
            item_id=item.id,
            sku=item.sku,
            item_name=item.name,
            quantity_on_hand=balance.quantity_on_hand,
            quantity_allocated=balance.quantity_allocated,
            quantity_available=balance.quantity_on_hand - balance.quantity_allocated,
            low_stock=balance.quantity_on_hand - balance.quantity_allocated <= item.reorder_point,
        )
        for balance, warehouse, location, item in db.execute(statement).all()
    ]


def list_orders(db: Session, status: str | None = None, priority: str | None = None) -> list[OrderResponse]:
    # Group by order and use a regular aggregate for a stable one-row-per-order result.
    statement = (
        select(Order, func.count(OrderLine.id).label("line_count"))
        .outerjoin(OrderLine, OrderLine.order_id == Order.id)
        .group_by(Order.id)
        .order_by(Order.created_at.desc(), Order.order_number)
    )
    if status:
        statement = statement.where(Order.status == status.upper())
    if priority:
        statement = statement.where(Order.priority == priority.upper())
    return [
        OrderResponse(
            id=order.id,
            order_number=order.order_number,
            customer_name=order.customer_name,
            order_type=order.order_type,
            priority=order.priority,
            status=order.status,
            requested_ship_date=order.requested_ship_date,
            line_count=line_count,
        )
        for order, line_count in db.execute(statement).all()
    ]


def list_tasks(
    db: Session, status: str | None = None, task_type: str | None = None, warehouse_id: UUID | None = None
) -> list[TaskResponse]:
    statement = (
        select(FulfillmentTask, Order, Warehouse)
        .join(Order, Order.id == FulfillmentTask.order_id)
        .join(Warehouse, Warehouse.id == FulfillmentTask.warehouse_id)
        .order_by(FulfillmentTask.due_at, FulfillmentTask.task_number)
    )
    if status:
        statement = statement.where(FulfillmentTask.status == status.upper())
    if task_type:
        statement = statement.where(FulfillmentTask.task_type == task_type.upper())
    if warehouse_id:
        statement = statement.where(FulfillmentTask.warehouse_id == warehouse_id)
    return [
        TaskResponse(
            id=task.id,
            task_number=task.task_number,
            order_id=task.order_id,
            order_number=order.order_number,
            order_line_id=task.order_line_id,
            warehouse_id=task.warehouse_id,
            warehouse_code=warehouse.code,
            task_type=task.task_type,
            status=task.status,
            priority=task.priority,
            assigned_to=task.assigned_to,
            due_at=task.due_at,
        )
        for task, order, warehouse in db.execute(statement).all()
    ]


def list_shipments(db: Session, status: str | None = None, carrier: str | None = None) -> list[ShipmentResponse]:
    statement = (
        select(Shipment, Order, Warehouse)
        .join(Order, Order.id == Shipment.order_id)
        .join(Warehouse, Warehouse.id == Shipment.warehouse_id)
        .order_by(Shipment.created_at.desc(), Shipment.shipment_number)
    )
    if status:
        statement = statement.where(Shipment.status == status.upper())
    if carrier:
        statement = statement.where(Shipment.carrier.ilike(f"%{carrier}%"))
    return [
        ShipmentResponse(
            id=shipment.id,
            shipment_number=shipment.shipment_number,
            order_id=shipment.order_id,
            order_number=order.order_number,
            warehouse_id=shipment.warehouse_id,
            warehouse_code=warehouse.code,
            carrier=shipment.carrier,
            tracking_number=shipment.tracking_number,
            status=shipment.status,
            shipped_at=shipment.shipped_at,
            shipped_by=shipment.shipped_by,
        )
        for shipment, order, warehouse in db.execute(statement).all()
    ]
