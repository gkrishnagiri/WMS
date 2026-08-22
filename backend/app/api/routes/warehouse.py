"""Warehouse & Fulfillment API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.warehouse import (
    InventoryResponse,
    ItemResponse,
    OrderResponse,
    ShipmentResponse,
    TaskResponse,
    WarehouseDetail,
    WarehouseResponse,
    WarehouseSummary,
)
from app.schemas.warehouse_transactions import (
    InventoryTransactionResponse,
    OrderCreate,
    OrderDetail,
    OrderEventResponse,
    ShipOrderRequest,
)
from app.services import warehouse_service
from app.services import warehouse_workflow_service

router = APIRouter(prefix="/api/v1/warehouse", tags=["warehouse"])


def _workflow_error(error: warehouse_workflow_service.WorkflowError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("/summary", response_model=WarehouseSummary)
def summary(db: Session = Depends(get_db)) -> WarehouseSummary:
    return warehouse_service.get_summary(db)


@router.get("/warehouses", response_model=list[WarehouseResponse])
def warehouses(
    status_filter: str | None = Query(default=None, alias="status"), db: Session = Depends(get_db)
) -> list[WarehouseResponse]:
    return warehouse_service.list_warehouses(db, status_filter)


@router.get("/warehouses/{warehouse_id}", response_model=WarehouseDetail)
def warehouse_detail(warehouse_id: UUID, db: Session = Depends(get_db)) -> WarehouseDetail:
    result = warehouse_service.get_warehouse(db, warehouse_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found")
    return result


@router.get("/items", response_model=list[ItemResponse])
def items(
    active: bool | None = None,
    category: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
) -> list[ItemResponse]:
    return warehouse_service.list_items(db, active, category, search)


@router.get("/inventory", response_model=list[InventoryResponse])
def inventory(
    warehouse_id: UUID | None = None,
    sku: str | None = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db),
) -> list[InventoryResponse]:
    return warehouse_service.list_inventory(db, warehouse_id, sku, low_stock_only)


@router.get("/orders", response_model=list[OrderResponse])
def orders(
    status_filter: str | None = Query(default=None, alias="status"),
    priority: str | None = None,
    db: Session = Depends(get_db),
) -> list[OrderResponse]:
    return warehouse_service.list_orders(db, status_filter, priority)


@router.post("/orders", response_model=OrderDetail, status_code=status.HTTP_201_CREATED)
def create_order(request: OrderCreate, db: Session = Depends(get_db)) -> OrderDetail:
    try:
        return warehouse_workflow_service.create_order(db, request)
    except warehouse_workflow_service.WorkflowError as error:
        db.rollback()
        raise _workflow_error(error) from error


@router.get("/orders/{order_id}", response_model=OrderDetail)
def order_detail(order_id: UUID, db: Session = Depends(get_db)) -> OrderDetail:
    try:
        return warehouse_workflow_service.get_order_detail(db, order_id)
    except warehouse_workflow_service.WorkflowError as error:
        raise _workflow_error(error) from error


@router.post("/orders/{order_id}/allocate", response_model=OrderDetail)
def allocate_order(order_id: UUID, db: Session = Depends(get_db)) -> OrderDetail:
    try:
        return warehouse_workflow_service.allocate_order(db, order_id)
    except warehouse_workflow_service.WorkflowError as error:
        db.rollback()
        raise _workflow_error(error) from error


@router.post("/orders/{order_id}/release-tasks", response_model=OrderDetail)
def release_order_tasks(order_id: UUID, db: Session = Depends(get_db)) -> OrderDetail:
    try:
        return warehouse_workflow_service.release_tasks(db, order_id)
    except warehouse_workflow_service.WorkflowError as error:
        db.rollback()
        raise _workflow_error(error) from error


@router.post("/tasks/{task_id}/start", response_model=TaskResponse)
def start_task(task_id: UUID, db: Session = Depends(get_db)) -> TaskResponse:
    try:
        return warehouse_workflow_service.start_task(db, task_id)
    except warehouse_workflow_service.WorkflowError as error:
        db.rollback()
        raise _workflow_error(error) from error


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: UUID, db: Session = Depends(get_db)) -> TaskResponse:
    try:
        return warehouse_workflow_service.complete_task(db, task_id)
    except warehouse_workflow_service.WorkflowError as error:
        db.rollback()
        raise _workflow_error(error) from error


@router.post("/orders/{order_id}/ship", response_model=OrderDetail)
def ship_order(order_id: UUID, request: ShipOrderRequest, db: Session = Depends(get_db)) -> OrderDetail:
    try:
        return warehouse_workflow_service.ship_order(db, order_id, request)
    except warehouse_workflow_service.WorkflowError as error:
        db.rollback()
        raise _workflow_error(error) from error


@router.get("/inventory-transactions", response_model=list[InventoryTransactionResponse])
def inventory_transactions(
    item_id: UUID | None = None,
    warehouse_id: UUID | None = None,
    order_id: UUID | None = None,
    transaction_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[InventoryTransactionResponse]:
    return warehouse_workflow_service.list_inventory_transactions(
        db, item_id, warehouse_id, order_id, transaction_type, limit
    )


@router.get("/orders/{order_id}/events", response_model=list[OrderEventResponse])
def order_events(order_id: UUID, db: Session = Depends(get_db)) -> list[OrderEventResponse]:
    try:
        return warehouse_workflow_service.list_order_events(db, order_id)
    except warehouse_workflow_service.WorkflowError as error:
        raise _workflow_error(error) from error


@router.get("/tasks", response_model=list[TaskResponse])
def tasks(
    status_filter: str | None = Query(default=None, alias="status"),
    task_type: str | None = None,
    warehouse_id: UUID | None = None,
    db: Session = Depends(get_db),
) -> list[TaskResponse]:
    return warehouse_service.list_tasks(db, status_filter, task_type, warehouse_id)


@router.get("/shipments", response_model=list[ShipmentResponse])
def shipments(
    status_filter: str | None = Query(default=None, alias="status"),
    carrier: str | None = None,
    db: Session = Depends(get_db),
) -> list[ShipmentResponse]:
    return warehouse_service.list_shipments(db, status_filter, carrier)
