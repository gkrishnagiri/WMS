"""Pydantic response schemas for Warehouse & Fulfillment APIs."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class WarehouseSummary(BaseModel):
    warehouses: int
    locations: int
    items: int
    inventory_units_on_hand: int
    open_orders: int
    open_tasks: int
    shipments_in_progress: int
    low_stock_items: int


class ZoneSummary(ORMModel):
    id: UUID
    code: str
    name: str
    zone_type: str
    status: str
    location_count: int = 0


class WarehouseResponse(ORMModel):
    id: UUID
    code: str
    name: str
    region: str
    city: str
    country: str
    status: str
    zone_count: int = 0
    location_count: int = 0


class WarehouseDetail(WarehouseResponse):
    zones: list[ZoneSummary] = Field(default_factory=list)


class ItemResponse(ORMModel):
    id: UUID
    sku: str
    name: str
    category: str
    unit_of_measure: str
    reorder_point: int
    safety_stock: int
    active: bool


class InventoryResponse(BaseModel):
    id: UUID
    warehouse_id: UUID
    warehouse_code: str
    warehouse_name: str
    location_id: UUID
    location_code: str
    item_id: UUID
    sku: str
    item_name: str
    quantity_on_hand: int
    quantity_allocated: int
    quantity_available: int
    low_stock: bool


class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    customer_name: str
    order_type: str
    priority: str
    status: str
    requested_ship_date: date | None
    line_count: int


class TaskResponse(BaseModel):
    id: UUID
    task_number: str
    order_id: UUID
    order_number: str
    order_line_id: UUID | None
    warehouse_id: UUID
    warehouse_code: str
    task_type: str
    status: str
    priority: str
    assigned_to: str | None
    due_at: datetime | None


class ShipmentResponse(BaseModel):
    id: UUID
    shipment_number: str
    order_id: UUID
    order_number: str
    warehouse_id: UUID
    warehouse_code: str
    carrier: str
    tracking_number: str | None
    status: str
    shipped_at: datetime | None
    shipped_by: str | None = None
