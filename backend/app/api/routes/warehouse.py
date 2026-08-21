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
from app.services import warehouse_service

router = APIRouter(prefix="/api/v1/warehouse", tags=["warehouse"])


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
