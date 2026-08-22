"""Deterministic operational exception detection and simulation services."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.models.operations import OpsException
from app.models.warehouse import FulfillmentTask, InventoryBalance, InventoryTransaction, Item, Location, Order, Shipment, Warehouse
from app.schemas.operations import ExceptionResponse

ACTIVE_EXCEPTION_STATUSES = ("OPEN", "ACKNOWLEDGED", "LINKED_TO_TICKET")
ACTIVE_ORDER_STATUSES = ("ALLOCATED", "PICKING", "PACKING")


class OperationsError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_number(db: Session, model: Any, field: Any, prefix: str) -> str:
    current = db.scalar(select(func.max(field)).where(field.like(f"{prefix}%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            sequence = 1
    return f"{prefix}{sequence:04d}"


def _exception_prefix() -> str:
    return f"EXC-{_now():%Y%m%d}-"


def _active_exception(db: Session, exception_type: str, entity_type: str, entity_id: UUID | None) -> OpsException | None:
    return db.scalar(
        select(OpsException)
        .where(
            OpsException.exception_type == exception_type,
            OpsException.source_entity_type == entity_type,
            OpsException.source_entity_id == entity_id,
            OpsException.status.in_(ACTIVE_EXCEPTION_STATUSES),
        )
        .order_by(OpsException.last_detected_at.desc())
    )


def create_or_refresh_exception(
    db: Session,
    *,
    exception_type: str,
    severity: str,
    source_entity_type: str,
    source_entity_id: UUID | None,
    source_reference: str | None,
    title: str,
    description: str,
    detection_method: str,
    business_impact: str,
    technical_context: dict | None = None,
) -> OpsException:
    now = _now()
    exception = _active_exception(db, exception_type, source_entity_type, source_entity_id)
    if exception is None:
        exception = OpsException(
            exception_number=_next_number(db, OpsException, OpsException.exception_number, _exception_prefix()),
            exception_type=exception_type,
            severity=severity,
            status="OPEN",
            source_module="WAREHOUSE_FULFILLMENT",
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            source_reference=source_reference,
            title=title,
            description=description,
            detection_method=detection_method,
            business_impact=business_impact,
            technical_context=technical_context,
            first_detected_at=now,
            last_detected_at=now,
            created_at=now,
            updated_at=now,
        )
        db.add(exception)
    else:
        exception.severity = severity
        exception.source_reference = source_reference
        exception.title = title
        exception.description = description
        exception.detection_method = detection_method
        exception.business_impact = business_impact
        exception.technical_context = technical_context
        exception.last_detected_at = now
        exception.updated_at = now
    db.flush()
    return exception


def exception_to_response(db: Session, exception: OpsException) -> ExceptionResponse:
    from app.models.ams import AmsTicket

    ticket = db.scalar(
        select(AmsTicket)
        .where(AmsTicket.exception_id == exception.id, AmsTicket.status.not_in(("CLOSED", "CANCELLED")))
        .order_by(AmsTicket.created_at.desc())
    )
    return ExceptionResponse(
        id=exception.id,
        exception_number=exception.exception_number,
        exception_type=exception.exception_type,
        severity=exception.severity,
        status=exception.status,
        source_module=exception.source_module,
        source_entity_type=exception.source_entity_type,
        source_entity_id=exception.source_entity_id,
        source_reference=exception.source_reference,
        title=exception.title,
        description=exception.description,
        detection_method=exception.detection_method,
        business_impact=exception.business_impact,
        technical_context=exception.technical_context,
        first_detected_at=exception.first_detected_at,
        last_detected_at=exception.last_detected_at,
        resolved_at=exception.resolved_at,
        created_at=exception.created_at,
        updated_at=exception.updated_at,
        linked_ticket_id=ticket.id if ticket else None,
        linked_ticket_number=ticket.ticket_number if ticket else None,
    )


def list_exceptions(
    db: Session,
    status: str | None = None,
    severity: str | None = None,
    exception_type: str | None = None,
    source_module: str | None = None,
) -> list[ExceptionResponse]:
    open_first = case((OpsException.status.in_(ACTIVE_EXCEPTION_STATUSES), 0), else_=1)
    statement = select(OpsException).order_by(open_first, OpsException.last_detected_at.desc(), OpsException.exception_number.desc())
    if status:
        statement = statement.where(OpsException.status == status.upper())
    if severity:
        statement = statement.where(OpsException.severity == severity.upper())
    if exception_type:
        statement = statement.where(OpsException.exception_type == exception_type.upper())
    if source_module:
        statement = statement.where(OpsException.source_module == source_module.upper())
    return [exception_to_response(db, exception) for exception in db.scalars(statement).all()]


def get_exception(db: Session, exception_id: UUID) -> ExceptionResponse:
    exception = db.get(OpsException, exception_id)
    if exception is None:
        raise OperationsError("Operational exception not found.", 404)
    return exception_to_response(db, exception)


def acknowledge_exception(db: Session, exception_id: UUID) -> ExceptionResponse:
    exception = db.get(OpsException, exception_id)
    if exception is None:
        raise OperationsError("Operational exception not found.", 404)
    if exception.status != "OPEN":
        raise OperationsError("Only OPEN exceptions can be acknowledged.")
    exception.status = "ACKNOWLEDGED"
    exception.updated_at = _now()
    db.commit()
    return get_exception(db, exception.id)


def resolve_exception(db: Session, exception_id: UUID) -> ExceptionResponse:
    exception = db.get(OpsException, exception_id)
    if exception is None:
        raise OperationsError("Operational exception not found.", 404)
    if exception.status in {"RESOLVED", "SUPPRESSED"}:
        raise OperationsError("Exception is already closed for operations.")
    now = _now()
    exception.status = "RESOLVED"
    exception.resolved_at = now
    exception.updated_at = now
    db.commit()
    return get_exception(db, exception.id)


def detect_low_stock(db: Session, item_id: UUID | None = None, warehouse_id: UUID | None = None) -> list[ExceptionResponse]:
    statement = (
        select(InventoryBalance, Item, Warehouse, Location)
        .join(Item, Item.id == InventoryBalance.item_id)
        .join(Warehouse, Warehouse.id == InventoryBalance.warehouse_id)
        .join(Location, Location.id == InventoryBalance.location_id)
        .where(InventoryBalance.quantity_on_hand - InventoryBalance.quantity_allocated <= Item.reorder_point)
        .order_by(Warehouse.code, Location.code, Item.sku)
    )
    if item_id:
        statement = statement.where(InventoryBalance.item_id == item_id)
    if warehouse_id:
        statement = statement.where(InventoryBalance.warehouse_id == warehouse_id)
    exceptions = []
    for balance, item, warehouse, location in db.execute(statement).all():
        available = balance.quantity_on_hand - balance.quantity_allocated
        severity = "CRITICAL" if available <= 0 else "HIGH" if available < item.safety_stock else "MEDIUM"
        exceptions.append(
            create_or_refresh_exception(
                db,
                exception_type="LOW_STOCK",
                severity=severity,
                source_entity_type="INVENTORY_BALANCE",
                source_entity_id=balance.id,
                source_reference=f"{warehouse.code}/{location.code}/{item.sku}",
                title=f"Low stock: {item.sku} at {warehouse.code}",
                description=f"Available quantity for {item.name} is {available}, at or below the reorder point of {item.reorder_point}.",
                detection_method="RULE_BASED",
                business_impact=f"Replenishment may be required for {item.sku} before additional warehouse demand is accepted.",
                technical_context={"item_id": str(item.id), "warehouse_id": str(warehouse.id), "location_id": str(location.id), "available": available, "reorder_point": item.reorder_point},
            )
        )
    db.commit()
    return [exception_to_response(db, exception) for exception in exceptions]


def detect_order_stuck(db: Session, threshold_hours: float = 24) -> list[ExceptionResponse]:
    cutoff = _now() - timedelta(hours=threshold_hours)
    orders = db.scalars(
        select(Order).where(Order.status.in_(ACTIVE_ORDER_STATUSES), Order.updated_at <= cutoff).order_by(Order.updated_at)
    ).all()
    exceptions = []
    for order in orders:
        exceptions.append(
            create_or_refresh_exception(
                db,
                exception_type="ORDER_STUCK",
                severity="HIGH" if order.priority in {"HIGH", "URGENT"} else "MEDIUM",
                source_entity_type="ORDER",
                source_entity_id=order.id,
                source_reference=order.order_number,
                title=f"Order stuck in {order.status}: {order.order_number}",
                description=f"Order {order.order_number} has remained in {order.status} beyond the {threshold_hours:g}-hour detection threshold.",
                detection_method="RULE_BASED",
                business_impact="Customer fulfillment may miss the requested ship date.",
                technical_context={"order_id": str(order.id), "status": order.status, "threshold_hours": threshold_hours},
            )
        )
    db.commit()
    return [exception_to_response(db, exception) for exception in exceptions]


def _find_balance(db: Session, item_id: UUID | None, warehouse_id: UUID | None) -> tuple[InventoryBalance, Item, Warehouse, Location]:
    statement = (
        select(InventoryBalance, Item, Warehouse, Location)
        .join(Item, Item.id == InventoryBalance.item_id)
        .join(Warehouse, Warehouse.id == InventoryBalance.warehouse_id)
        .join(Location, Location.id == InventoryBalance.location_id)
        .order_by(Warehouse.code, Location.code, Item.sku)
    )
    if item_id:
        statement = statement.where(InventoryBalance.item_id == item_id)
    if warehouse_id:
        statement = statement.where(InventoryBalance.warehouse_id == warehouse_id)
    result = db.execute(statement).first()
    if result is None:
        raise OperationsError("No matching inventory balance was found.", 404)
    return result


def simulate_low_stock(db: Session, item_id: UUID | None, warehouse_id: UUID | None) -> ExceptionResponse:
    balance, item, warehouse, location = _find_balance(db, item_id, warehouse_id)
    target_available = max(0, item.reorder_point - 1)
    current_available = balance.quantity_on_hand - balance.quantity_allocated
    if current_available > target_available:
        balance.quantity_on_hand = balance.quantity_allocated + target_available
        db.add(
            InventoryTransaction(
                transaction_number=_next_number(db, InventoryTransaction, InventoryTransaction.transaction_number, f"SIM-{_now():%Y%m%d}-"),
                transaction_type="ADJUSTMENT",
                warehouse_id=warehouse.id,
                location_id=location.id,
                item_id=item.id,
                quantity_on_hand_delta=target_available - current_available,
                quantity_allocated_delta=0,
                quantity_on_hand_after=balance.quantity_on_hand,
                quantity_allocated_after=balance.quantity_allocated,
                quantity_available_after=target_available,
                reference_type="SIMULATION",
                reference_number=item.sku,
                reason_code="SIM_LOW_STOCK",
                notes="Deterministic low-stock failure simulation.",
                created_by="simulation",
                created_at=_now(),
            )
        )
    exception = create_or_refresh_exception(
        db,
        exception_type="LOW_STOCK",
        severity="CRITICAL" if target_available <= 0 else "HIGH" if target_available < item.safety_stock else "MEDIUM",
        source_entity_type="INVENTORY_BALANCE",
        source_entity_id=balance.id,
        source_reference=f"{warehouse.code}/{location.code}/{item.sku}",
        title=f"Low stock simulation: {item.sku}",
        description=f"Simulation reduced available quantity for {item.name} to {target_available}, at or below the reorder point of {item.reorder_point}.",
        detection_method="SIMULATED",
        business_impact=f"Simulated inventory pressure may prevent fulfillment for {item.sku}.",
        technical_context={"simulation": "low-stock", "item_id": str(item.id), "warehouse_id": str(warehouse.id), "location_id": str(location.id), "available": target_available},
    )
    db.flush()
    return exception_to_response(db, exception)


def simulate_task_blocked(db: Session, task_id: UUID | None, reason: str) -> ExceptionResponse:
    statement = select(FulfillmentTask).order_by(FulfillmentTask.task_number)
    if task_id:
        statement = statement.where(FulfillmentTask.id == task_id)
    else:
        statement = statement.where(FulfillmentTask.status.not_in(("COMPLETED", "CANCELLED", "BLOCKED")))
    task = db.scalar(statement)
    if task is None:
        raise OperationsError("No eligible fulfillment task was found.", 404)
    if task.status in {"COMPLETED", "CANCELLED"}:
        raise OperationsError("Completed or cancelled tasks cannot be blocked.")
    task.status = "BLOCKED"
    task.updated_at = _now()
    return create_or_refresh_exception(
        db,
        exception_type="TASK_BLOCKED",
        severity="HIGH",
        source_entity_type="TASK",
        source_entity_id=task.id,
        source_reference=task.task_number,
        title=f"Fulfillment task blocked: {task.task_number}",
        description=reason,
        detection_method="SIMULATED",
        business_impact="Warehouse work cannot progress until the blocked task is investigated.",
        technical_context={"task_id": str(task.id), "task_type": task.task_type, "reason": reason},
    )


def simulate_shipment_exception(db: Session, shipment_id: UUID | None, reason: str) -> ExceptionResponse:
    statement = select(Shipment).order_by(Shipment.shipment_number)
    if shipment_id:
        statement = statement.where(Shipment.id == shipment_id)
    else:
        statement = statement.where(Shipment.status != "SHIPPED")
    shipment = db.scalar(statement)
    if shipment is None:
        raise OperationsError("No eligible shipment was found.", 404)
    if shipment.status == "SHIPPED":
        raise OperationsError("A shipped shipment cannot be marked as an exception.")
    shipment.status = "EXCEPTION"
    shipment.updated_at = _now()
    return create_or_refresh_exception(
        db,
        exception_type="SHIPMENT_EXCEPTION",
        severity="HIGH",
        source_entity_type="SHIPMENT",
        source_entity_id=shipment.id,
        source_reference=shipment.shipment_number,
        title=f"Shipment exception: {shipment.shipment_number}",
        description=reason,
        detection_method="SIMULATED",
        business_impact="Outbound delivery may be delayed until the shipment issue is resolved.",
        technical_context={"shipment_id": str(shipment.id), "carrier": shipment.carrier, "reason": reason},
    )


def simulate_order_stuck(db: Session, order_id: UUID | None, requested_status: str) -> ExceptionResponse:
    status = requested_status.upper()
    if status not in ACTIVE_ORDER_STATUSES:
        raise OperationsError("Order stuck simulation status must be ALLOCATED, PICKING, or PACKING.", 400)
    statement = select(Order).order_by(Order.order_number)
    if order_id:
        statement = statement.where(Order.id == order_id)
    else:
        statement = statement.where(Order.status.in_(ACTIVE_ORDER_STATUSES))
    order = db.scalar(statement)
    if order is None:
        raise OperationsError("No eligible order was found.", 404)
    order.status = status
    order.updated_at = _now() - timedelta(hours=25)
    return create_or_refresh_exception(
        db,
        exception_type="ORDER_STUCK",
        severity="HIGH" if order.priority in {"HIGH", "URGENT"} else "MEDIUM",
        source_entity_type="ORDER",
        source_entity_id=order.id,
        source_reference=order.order_number,
        title=f"Order stuck simulation: {order.order_number}",
        description=f"Simulation left order {order.order_number} in {status} beyond the default detection threshold.",
        detection_method="SIMULATED",
        business_impact="Simulated fulfillment delay may affect the customer ship date.",
        technical_context={"simulation": "order-stuck", "order_id": str(order.id), "status": status, "threshold_hours": 24},
    )

