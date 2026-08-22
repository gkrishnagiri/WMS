"""Request and response schemas for warehouse transaction workflows."""

from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.warehouse import ShipmentResponse, TaskResponse


class OrderLineCreate(BaseModel):
    item_id: UUID
    quantity_ordered: int = Field(gt=0)


class OrderCreate(BaseModel):
    order_number: str | None = Field(default=None, min_length=1, max_length=60)
    customer_name: str = Field(min_length=1, max_length=160)
    order_type: str = Field(default="STANDARD", max_length=30)
    priority: str = Field(default="NORMAL", max_length=20)
    requested_ship_date: date | None = None
    warehouse_id: UUID | None = None
    lines: list[OrderLineCreate] = Field(min_length=1)


class ShipOrderRequest(BaseModel):
    carrier: str = Field(min_length=1, max_length=60)
    tracking_number: str | None = Field(default=None, max_length=120)
    shipped_by: str = Field(default="system", min_length=1, max_length=120)


class OrderLineDetail(BaseModel):
    id: UUID
    line_number: int
    item_id: UUID
    sku: str
    item_name: str
    quantity_ordered: int
    quantity_allocated: int
    quantity_shipped: int


class AllocationResponse(BaseModel):
    id: UUID
    order_id: UUID
    order_line_id: UUID
    warehouse_id: UUID
    warehouse_code: str
    location_id: UUID
    location_code: str
    item_id: UUID
    sku: str
    quantity_allocated: int
    quantity_picked: int
    quantity_packed: int
    quantity_shipped: int
    status: str


class OrderEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_id: UUID
    event_type: str
    from_status: str | None
    to_status: str | None
    message: str
    event_payload: dict | None
    created_by: str
    created_at: datetime


class OrderDetail(BaseModel):
    id: UUID
    order_number: str
    customer_name: str
    order_type: str
    priority: str
    status: str
    requested_ship_date: date | None
    warehouse_id: UUID | None
    lines: list[OrderLineDetail]
    allocations: list[AllocationResponse]
    tasks: list[TaskResponse]
    shipments: list[ShipmentResponse]
    events: list[OrderEventResponse]


class InventoryTransactionResponse(BaseModel):
    id: UUID
    transaction_number: str
    transaction_type: str
    warehouse_id: UUID
    warehouse_code: str
    location_id: UUID
    location_code: str
    item_id: UUID
    sku: str
    order_id: UUID | None
    order_line_id: UUID | None
    allocation_id: UUID | None
    task_id: UUID | None
    shipment_id: UUID | None
    quantity_on_hand_delta: int
    quantity_allocated_delta: int
    quantity_on_hand_after: int
    quantity_allocated_after: int
    quantity_available_after: int
    reference_type: str | None
    reference_number: str | None
    reason_code: str | None
    notes: str | None
    created_by: str
    created_at: datetime
