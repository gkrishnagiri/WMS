"""Transactional services for the controlled warehouse order workflow."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.warehouse import (
    Allocation,
    FulfillmentTask,
    InventoryBalance,
    InventoryTransaction,
    Item,
    Location,
    Order,
    OrderEvent,
    OrderLine,
    Shipment,
    Warehouse,
)
from app.schemas.warehouse import ShipmentResponse, TaskResponse
from app.schemas.warehouse_transactions import (
    AllocationResponse,
    InventoryTransactionResponse,
    OrderCreate,
    OrderDetail,
    OrderEventResponse,
    OrderLineDetail,
    ShipOrderRequest,
)


class WorkflowError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _next_number(db: Session, model: Any, field: Any, prefix: str) -> str:
    current = db.scalar(select(func.max(field)).where(field.like(f"{prefix}%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            sequence = 1
    return f"{prefix}{sequence:04d}"


def _today_prefix(kind: str) -> str:
    return f"{kind}-{datetime.now(timezone.utc):%Y%m%d}-"


def _event(
    db: Session,
    order: Order,
    event_type: str,
    message: str,
    from_status: str | None = None,
    to_status: str | None = None,
    payload: dict | None = None,
) -> None:
    db.add(
        OrderEvent(
            order_id=order.id,
            event_type=event_type,
            from_status=from_status,
            to_status=to_status,
            message=message,
            event_payload=payload,
            created_by="system",
            created_at=datetime.now(timezone.utc),
        )
    )


def _get_order(db: Session, order_id: UUID, lock: bool = False) -> Order:
    statement = select(Order).where(Order.id == order_id)
    if lock:
        statement = statement.with_for_update()
    order = db.scalar(statement)
    if order is None:
        raise WorkflowError("Order not found.", 404)
    return order


def create_order(db: Session, request: OrderCreate) -> OrderDetail:
    if request.warehouse_id is not None:
        warehouse = db.get(Warehouse, request.warehouse_id)
        if warehouse is None:
            raise WorkflowError("Warehouse not found.", 404)
        if warehouse.status != "ACTIVE":
            raise WorkflowError("Orders can only be created for an active warehouse.", 400)

    item_ids = [line.item_id for line in request.lines]
    items = {item.id: item for item in db.scalars(select(Item).where(Item.id.in_(item_ids))).all()}
    missing_item = next((item_id for item_id in item_ids if item_id not in items), None)
    if missing_item is not None:
        raise WorkflowError(f"Item {missing_item} not found.", 404)

    order_number = request.order_number or _next_number(db, Order, Order.order_number, _today_prefix("ORD"))
    if db.scalar(select(Order.id).where(Order.order_number == order_number)) is not None:
        raise WorkflowError("Order number already exists.", 409)
    order = Order(
        order_number=order_number,
        customer_name=request.customer_name.strip(),
        order_type=request.order_type.upper(),
        priority=request.priority.upper(),
        status="NEW",
        requested_ship_date=request.requested_ship_date,
        warehouse_id=request.warehouse_id,
    )
    db.add(order)
    db.flush()
    for line_number, line_request in enumerate(request.lines, start=1):
        db.add(
            OrderLine(
                order_id=order.id,
                item_id=line_request.item_id,
                line_number=line_number,
                quantity_ordered=line_request.quantity_ordered,
                quantity_allocated=0,
                quantity_shipped=0,
            )
        )
    _event(db, order, "ORDER_CREATED", "Customer order created.", to_status="NEW")
    db.commit()
    return get_order_detail(db, order.id)


def allocate_order(db: Session, order_id: UUID) -> OrderDetail:
    order = _get_order(db, order_id, lock=True)
    if order.status != "NEW":
        raise WorkflowError("Only orders in NEW status can be allocated.")
    lines = db.scalars(select(OrderLine).where(OrderLine.order_id == order.id).order_by(OrderLine.line_number)).all()
    if not lines:
        raise WorkflowError("Order must contain at least one line.", 400)

    allocated_rows: list[tuple[OrderLine, InventoryBalance, int]] = []
    for line in lines:
        statement = (
            select(InventoryBalance, Warehouse, Location)
            .join(Warehouse, Warehouse.id == InventoryBalance.warehouse_id)
            .join(Location, Location.id == InventoryBalance.location_id)
            .where(
                InventoryBalance.item_id == line.item_id,
                InventoryBalance.quantity_on_hand - InventoryBalance.quantity_allocated >= line.quantity_ordered,
                Warehouse.status == "ACTIVE",
                Location.status == "ACTIVE",
            )
            .order_by(Warehouse.code, Location.code)
            .with_for_update()
        )
        if order.warehouse_id is not None:
            statement = statement.where(InventoryBalance.warehouse_id == order.warehouse_id)
        candidate = db.execute(statement).first()
        if candidate is None:
            raise WorkflowError(f"Insufficient available inventory for item {line.item_id}.")
        balance, _warehouse, _location = candidate
        quantity = line.quantity_ordered
        balance.quantity_allocated += quantity
        line.quantity_allocated = quantity
        db.flush()
        allocation = Allocation(
            order_id=order.id,
            order_line_id=line.id,
            warehouse_id=balance.warehouse_id,
            location_id=balance.location_id,
            item_id=line.item_id,
            quantity_allocated=quantity,
            status="ALLOCATED",
        )
        db.add(allocation)
        db.flush()
        db.add(
            InventoryTransaction(
                transaction_number=_next_number(
                    db, InventoryTransaction, InventoryTransaction.transaction_number, _today_prefix("INV")
                ),
                transaction_type="ALLOCATION_RESERVE",
                warehouse_id=balance.warehouse_id,
                location_id=balance.location_id,
                item_id=line.item_id,
                order_id=order.id,
                order_line_id=line.id,
                allocation_id=allocation.id,
                quantity_on_hand_delta=0,
                quantity_allocated_delta=quantity,
                quantity_on_hand_after=balance.quantity_on_hand,
                quantity_allocated_after=balance.quantity_allocated,
                quantity_available_after=balance.quantity_on_hand - balance.quantity_allocated,
                reference_type="ORDER",
                reference_number=order.order_number,
                reason_code="ORDER_ALLOCATION",
                notes="Inventory reserved for customer order.",
            )
        )
        db.flush()
        allocated_rows.append((line, balance, quantity))

    order.status = "ALLOCATED"
    _event(db, order, "ORDER_ALLOCATED", "Inventory allocated for all order lines.", from_status="NEW", to_status="ALLOCATED")
    db.commit()
    return get_order_detail(db, order.id)


def release_tasks(db: Session, order_id: UUID) -> OrderDetail:
    order = _get_order(db, order_id, lock=True)
    existing_tasks = db.scalars(select(FulfillmentTask).where(FulfillmentTask.order_id == order.id)).all()
    if order.status == "PICKING" and existing_tasks:
        return get_order_detail(db, order.id)
    if order.status != "ALLOCATED":
        raise WorkflowError("Order must be in ALLOCATED status before releasing tasks.")

    allocations = db.scalars(select(Allocation).where(Allocation.order_id == order.id).order_by(Allocation.created_at, Allocation.id)).all()
    if not allocations:
        raise WorkflowError("Order has no allocations to release.")
    for allocation in allocations:
        db.add(
            FulfillmentTask(
                task_number=_next_number(db, FulfillmentTask, FulfillmentTask.task_number, _today_prefix("TASK")),
                order_id=order.id,
                order_line_id=allocation.order_line_id,
                warehouse_id=allocation.warehouse_id,
                task_type="PICK",
                status="OPEN",
                priority=order.priority,
            )
        )
        db.flush()
    db.add(
        FulfillmentTask(
            task_number=_next_number(db, FulfillmentTask, FulfillmentTask.task_number, _today_prefix("TASK")),
            order_id=order.id,
            order_line_id=None,
            warehouse_id=allocations[0].warehouse_id,
            task_type="PACK",
            status="OPEN",
            priority=order.priority,
        )
    )
    old_status = order.status
    order.status = "PICKING"
    _event(db, order, "TASKS_RELEASED", "Picking and packing tasks released.", from_status=old_status, to_status="PICKING")
    db.commit()
    return get_order_detail(db, order.id)


def start_task(db: Session, task_id: UUID) -> TaskResponse:
    task = db.scalar(select(FulfillmentTask).where(FulfillmentTask.id == task_id).with_for_update())
    if task is None:
        raise WorkflowError("Fulfillment task not found.", 404)
    if task.status != "OPEN":
        raise WorkflowError("Only OPEN tasks can be started.")
    order = _get_order(db, task.order_id, lock=True)
    task.status = "IN_PROGRESS"
    _event(db, order, "TASK_STARTED", f"Task {task.task_number} started.", payload={"task_id": str(task.id)})
    db.commit()
    return _task_response(db, task.id)


def complete_task(db: Session, task_id: UUID) -> TaskResponse:
    task = db.scalar(select(FulfillmentTask).where(FulfillmentTask.id == task_id).with_for_update())
    if task is None:
        raise WorkflowError("Fulfillment task not found.", 404)
    if task.status not in {"OPEN", "IN_PROGRESS"}:
        raise WorkflowError("Only OPEN or IN_PROGRESS tasks can be completed.")
    order = _get_order(db, task.order_id, lock=True)
    old_order_status = order.status

    if task.task_type == "PICK":
        allocation = db.scalar(select(Allocation).where(Allocation.order_line_id == task.order_line_id, Allocation.order_id == order.id).with_for_update())
        if allocation is None:
            raise WorkflowError("Pick task is not linked to an allocation.", 409)
        allocation.quantity_picked = allocation.quantity_allocated
        allocation.status = "PICKED"
        balance = db.scalar(
            select(InventoryBalance).where(
                InventoryBalance.location_id == allocation.location_id, InventoryBalance.item_id == allocation.item_id
            )
        )
        if balance is None:
            raise WorkflowError("Inventory balance for pick task was not found.", 404)
        db.add(
            InventoryTransaction(
                transaction_number=_next_number(
                    db, InventoryTransaction, InventoryTransaction.transaction_number, _today_prefix("INV")
                ),
                transaction_type="PICK_CONFIRM",
                warehouse_id=allocation.warehouse_id,
                location_id=allocation.location_id,
                item_id=allocation.item_id,
                order_id=order.id,
                order_line_id=allocation.order_line_id,
                allocation_id=allocation.id,
                task_id=task.id,
                quantity_on_hand_delta=0,
                quantity_allocated_delta=0,
                quantity_on_hand_after=balance.quantity_on_hand,
                quantity_allocated_after=balance.quantity_allocated,
                quantity_available_after=balance.quantity_on_hand - balance.quantity_allocated,
                reference_type="TASK",
                reference_number=task.task_number,
                reason_code="PICK_CONFIRM",
                notes="Pick task completed.",
            )
        )
        db.flush()
        task.status = "COMPLETED"
        remaining = db.scalar(
            select(func.count(FulfillmentTask.id)).where(
                FulfillmentTask.order_id == order.id,
                FulfillmentTask.task_type == "PICK",
                FulfillmentTask.id != task.id,
                FulfillmentTask.status != "COMPLETED",
            )
        )
        if not remaining:
            order.status = "PACKING"
    elif task.task_type == "PACK":
        incomplete_picks = db.scalar(
            select(func.count(FulfillmentTask.id)).where(
                FulfillmentTask.order_id == order.id,
                FulfillmentTask.task_type == "PICK",
                FulfillmentTask.status != "COMPLETED",
            )
        )
        if incomplete_picks:
            raise WorkflowError("All pick tasks must be completed before the pack task.")
        allocations = db.scalars(select(Allocation).where(Allocation.order_id == order.id).with_for_update()).all()
        for allocation in allocations:
            allocation.quantity_packed = allocation.quantity_allocated
            allocation.status = "PACKED"
            balance = db.scalar(
                select(InventoryBalance).where(
                    InventoryBalance.location_id == allocation.location_id, InventoryBalance.item_id == allocation.item_id
                )
            )
            if balance is None:
                raise WorkflowError("Inventory balance for pack task was not found.", 404)
            db.add(
                InventoryTransaction(
                    transaction_number=_next_number(
                        db, InventoryTransaction, InventoryTransaction.transaction_number, _today_prefix("INV")
                    ),
                    transaction_type="PACK_CONFIRM",
                    warehouse_id=allocation.warehouse_id,
                    location_id=allocation.location_id,
                    item_id=allocation.item_id,
                    order_id=order.id,
                    order_line_id=allocation.order_line_id,
                    allocation_id=allocation.id,
                    task_id=task.id,
                    quantity_on_hand_delta=0,
                    quantity_allocated_delta=0,
                    quantity_on_hand_after=balance.quantity_on_hand,
                    quantity_allocated_after=balance.quantity_allocated,
                    quantity_available_after=balance.quantity_on_hand - balance.quantity_allocated,
                    reference_type="TASK",
                    reference_number=task.task_number,
                    reason_code="PACK_CONFIRM",
                    notes="Pack task completed.",
                )
            )
            db.flush()
        task.status = "COMPLETED"
    else:
        raise WorkflowError("Only PICK and PACK task completion is supported.")

    _event(
        db,
        order,
        "TASK_COMPLETED",
        f"Task {task.task_number} completed.",
        from_status=old_order_status,
        to_status=order.status,
        payload={"task_id": str(task.id), "task_type": task.task_type},
    )
    db.commit()
    return _task_response(db, task.id)


def ship_order(db: Session, order_id: UUID, request: ShipOrderRequest) -> OrderDetail:
    order = _get_order(db, order_id, lock=True)
    if order.status == "SHIPPED":
        raise WorkflowError("Order has already been shipped.")
    tasks = db.scalars(select(FulfillmentTask).where(FulfillmentTask.order_id == order.id)).all()
    if not tasks or any(task.task_type not in {"PICK", "PACK"} or task.status != "COMPLETED" for task in tasks):
        raise WorkflowError("All required pick and pack tasks must be completed before shipment.")
    allocations = db.scalars(select(Allocation).where(Allocation.order_id == order.id).with_for_update()).all()
    if not allocations or any(allocation.quantity_packed < allocation.quantity_allocated for allocation in allocations):
        raise WorkflowError("Order must be fully packed before shipment.")

    shipment = db.scalar(select(Shipment).where(Shipment.order_id == order.id).order_by(Shipment.created_at.desc()).with_for_update())
    if shipment is None:
        shipment = Shipment(
            shipment_number=_next_number(db, Shipment, Shipment.shipment_number, _today_prefix("SHP")),
            order_id=order.id,
            warehouse_id=allocations[0].warehouse_id,
            carrier=request.carrier.strip(),
            tracking_number=request.tracking_number,
            status="SHIPPED",
            shipped_by=request.shipped_by.strip(),
            shipped_at=datetime.now(timezone.utc),
        )
        db.add(shipment)
        db.flush()
    else:
        if shipment.status == "SHIPPED":
            raise WorkflowError("Order has already been shipped.")
        shipment.carrier = request.carrier.strip()
        shipment.tracking_number = request.tracking_number
        shipment.shipped_by = request.shipped_by.strip()
        shipment.status = "SHIPPED"
        shipment.shipped_at = datetime.now(timezone.utc)

    for allocation in allocations:
        balance = db.scalar(
            select(InventoryBalance)
            .where(InventoryBalance.location_id == allocation.location_id, InventoryBalance.item_id == allocation.item_id)
            .with_for_update()
        )
        if balance is None:
            raise WorkflowError("Inventory balance for shipment was not found.", 404)
        quantity = allocation.quantity_shipped = allocation.quantity_allocated
        if balance.quantity_on_hand < quantity or balance.quantity_allocated < quantity:
            raise WorkflowError("Shipment would make inventory negative.")
        balance.quantity_on_hand -= quantity
        balance.quantity_allocated -= quantity
        allocation.status = "SHIPPED"
        line = db.get(OrderLine, allocation.order_line_id)
        if line is None:
            raise WorkflowError("Order line for shipment was not found.", 404)
        line.quantity_shipped += quantity
        db.add(
            InventoryTransaction(
                transaction_number=_next_number(
                    db, InventoryTransaction, InventoryTransaction.transaction_number, _today_prefix("INV")
                ),
                transaction_type="SHIPMENT_ISSUE",
                warehouse_id=allocation.warehouse_id,
                location_id=allocation.location_id,
                item_id=allocation.item_id,
                order_id=order.id,
                order_line_id=allocation.order_line_id,
                allocation_id=allocation.id,
                shipment_id=shipment.id,
                quantity_on_hand_delta=-quantity,
                quantity_allocated_delta=-quantity,
                quantity_on_hand_after=balance.quantity_on_hand,
                quantity_allocated_after=balance.quantity_allocated,
                quantity_available_after=balance.quantity_on_hand - balance.quantity_allocated,
                reference_type="SHIPMENT",
                reference_number=shipment.shipment_number,
                reason_code="SHIPMENT_ISSUE",
                notes="Inventory issued for confirmed shipment.",
            )
        )
        db.flush()
    old_status = order.status
    order.status = "SHIPPED"
    _event(db, order, "ORDER_SHIPPED", "Order shipment confirmed.", from_status=old_status, to_status="SHIPPED", payload={"shipment_id": str(shipment.id)})
    db.commit()
    return get_order_detail(db, order.id)


def _task_response(db: Session, task_id: UUID) -> TaskResponse:
    result = db.execute(
        select(FulfillmentTask, Order, Warehouse)
        .join(Order, Order.id == FulfillmentTask.order_id)
        .join(Warehouse, Warehouse.id == FulfillmentTask.warehouse_id)
        .where(FulfillmentTask.id == task_id)
    ).first()
    if result is None:
        raise WorkflowError("Fulfillment task not found.", 404)
    task, order, warehouse = result
    return TaskResponse(
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


def get_order_detail(db: Session, order_id: UUID) -> OrderDetail:
    order = db.scalar(select(Order).where(Order.id == order_id))
    if order is None:
        raise WorkflowError("Order not found.", 404)
    line_rows = db.execute(
        select(OrderLine, Item).join(Item, Item.id == OrderLine.item_id).where(OrderLine.order_id == order.id).order_by(OrderLine.line_number)
    ).all()
    lines = [
        OrderLineDetail(
            id=line.id,
            line_number=line.line_number,
            item_id=line.item_id,
            sku=item.sku,
            item_name=item.name,
            quantity_ordered=line.quantity_ordered,
            quantity_allocated=line.quantity_allocated,
            quantity_shipped=line.quantity_shipped,
        )
        for line, item in line_rows
    ]
    allocation_rows = db.execute(
        select(Allocation, Warehouse, Location, Item)
        .join(Warehouse, Warehouse.id == Allocation.warehouse_id)
        .join(Location, Location.id == Allocation.location_id)
        .join(Item, Item.id == Allocation.item_id)
        .where(Allocation.order_id == order.id)
        .order_by(Allocation.created_at, Allocation.id)
    ).all()
    allocations = [
        AllocationResponse(
            id=allocation.id,
            order_id=allocation.order_id,
            order_line_id=allocation.order_line_id,
            warehouse_id=allocation.warehouse_id,
            warehouse_code=warehouse.code,
            location_id=allocation.location_id,
            location_code=location.code,
            item_id=allocation.item_id,
            sku=item.sku,
            quantity_allocated=allocation.quantity_allocated,
            quantity_picked=allocation.quantity_picked,
            quantity_packed=allocation.quantity_packed,
            quantity_shipped=allocation.quantity_shipped,
            status=allocation.status,
        )
        for allocation, warehouse, location, item in allocation_rows
    ]
    task_rows = db.execute(
        select(FulfillmentTask, Warehouse)
        .join(Warehouse, Warehouse.id == FulfillmentTask.warehouse_id)
        .where(FulfillmentTask.order_id == order.id)
        .order_by(FulfillmentTask.created_at, FulfillmentTask.task_number)
    ).all()
    tasks = [
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
        for task, warehouse in task_rows
    ]
    shipment_rows = db.execute(
        select(Shipment, Warehouse)
        .join(Warehouse, Warehouse.id == Shipment.warehouse_id)
        .where(Shipment.order_id == order.id)
        .order_by(Shipment.created_at.desc(), Shipment.shipment_number)
    ).all()
    shipments = [
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
        for shipment, warehouse in shipment_rows
    ]
    events = [OrderEventResponse.model_validate(event) for event in db.scalars(select(OrderEvent).where(OrderEvent.order_id == order.id).order_by(OrderEvent.created_at.desc(), OrderEvent.id)).all()]
    return OrderDetail(
        id=order.id,
        order_number=order.order_number,
        customer_name=order.customer_name,
        order_type=order.order_type,
        priority=order.priority,
        status=order.status,
        requested_ship_date=order.requested_ship_date,
        warehouse_id=order.warehouse_id,
        lines=lines,
        allocations=allocations,
        tasks=tasks,
        shipments=shipments,
        events=events,
    )


def list_order_events(db: Session, order_id: UUID) -> list[OrderEventResponse]:
    _get_order(db, order_id)
    return [OrderEventResponse.model_validate(event) for event in db.scalars(select(OrderEvent).where(OrderEvent.order_id == order_id).order_by(OrderEvent.created_at.desc(), OrderEvent.id)).all()]


def list_inventory_transactions(
    db: Session,
    item_id: UUID | None = None,
    warehouse_id: UUID | None = None,
    order_id: UUID | None = None,
    transaction_type: str | None = None,
    limit: int = 100,
) -> list[InventoryTransactionResponse]:
    statement = (
        select(InventoryTransaction, Warehouse, Location, Item)
        .join(Warehouse, Warehouse.id == InventoryTransaction.warehouse_id)
        .join(Location, Location.id == InventoryTransaction.location_id)
        .join(Item, Item.id == InventoryTransaction.item_id)
        .order_by(InventoryTransaction.created_at.desc(), InventoryTransaction.transaction_number.desc())
        .limit(limit)
    )
    if item_id:
        statement = statement.where(InventoryTransaction.item_id == item_id)
    if warehouse_id:
        statement = statement.where(InventoryTransaction.warehouse_id == warehouse_id)
    if order_id:
        statement = statement.where(InventoryTransaction.order_id == order_id)
    if transaction_type:
        statement = statement.where(InventoryTransaction.transaction_type == transaction_type.upper())
    return [
        InventoryTransactionResponse(
            id=transaction.id,
            transaction_number=transaction.transaction_number,
            transaction_type=transaction.transaction_type,
            warehouse_id=transaction.warehouse_id,
            warehouse_code=warehouse.code,
            location_id=transaction.location_id,
            location_code=location.code,
            item_id=transaction.item_id,
            sku=item.sku,
            order_id=transaction.order_id,
            order_line_id=transaction.order_line_id,
            allocation_id=transaction.allocation_id,
            task_id=transaction.task_id,
            shipment_id=transaction.shipment_id,
            quantity_on_hand_delta=transaction.quantity_on_hand_delta,
            quantity_allocated_delta=transaction.quantity_allocated_delta,
            quantity_on_hand_after=transaction.quantity_on_hand_after,
            quantity_allocated_after=transaction.quantity_allocated_after,
            quantity_available_after=transaction.quantity_available_after,
            reference_type=transaction.reference_type,
            reference_number=transaction.reference_number,
            reason_code=transaction.reason_code,
            notes=transaction.notes,
            created_by=transaction.created_by,
            created_at=transaction.created_at,
        )
        for transaction, warehouse, location, item in db.execute(statement).all()
    ]
