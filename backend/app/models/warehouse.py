"""SQLAlchemy models for the Warehouse & Fulfillment domain."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Warehouse(TimestampMixin, Base):
    __tablename__ = "wf_warehouses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    region: Mapped[str] = mapped_column(String(80), nullable=False)
    city: Mapped[str] = mapped_column(String(80), nullable=False)
    country: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")

    zones: Mapped[List["Zone"]] = relationship(back_populates="warehouse", cascade="all, delete-orphan")
    locations: Mapped[List["Location"]] = relationship(back_populates="warehouse")


class Zone(TimestampMixin, Base):
    __tablename__ = "wf_zones"
    __table_args__ = (UniqueConstraint("warehouse_id", "code", name="uq_wf_zones_warehouse_code"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_warehouses.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    zone_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")

    warehouse: Mapped[Warehouse] = relationship(back_populates="zones")
    locations: Mapped[List["Location"]] = relationship(back_populates="zone", cascade="all, delete-orphan")


class Location(TimestampMixin, Base):
    __tablename__ = "wf_locations"
    __table_args__ = (UniqueConstraint("warehouse_id", "code", name="uq_wf_locations_warehouse_code"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_warehouses.id"), nullable=False)
    zone_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_zones.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(60), nullable=False)
    aisle: Mapped[Optional[str]] = mapped_column(String(20))
    bay: Mapped[Optional[str]] = mapped_column(String(20))
    level: Mapped[Optional[str]] = mapped_column(String(20))
    bin: Mapped[Optional[str]] = mapped_column(String(20))
    location_type: Mapped[str] = mapped_column(String(30), nullable=False)
    capacity_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")

    warehouse: Mapped[Warehouse] = relationship(back_populates="locations")
    zone: Mapped[Zone] = relationship(back_populates="locations")


class Item(TimestampMixin, Base):
    __tablename__ = "wf_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(20), nullable=False, default="EA")
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    safety_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class InventoryBalance(TimestampMixin, Base):
    __tablename__ = "wf_inventory_balances"
    __table_args__ = (
        UniqueConstraint("location_id", "item_id", name="uq_wf_inventory_location_item"),
        CheckConstraint("quantity_on_hand >= 0", name="ck_wf_inventory_on_hand_nonnegative"),
        CheckConstraint("quantity_allocated >= 0", name="ck_wf_inventory_allocated_nonnegative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_warehouses.id"), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_locations.id"), nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_items.id"), nullable=False)
    quantity_on_hand: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_allocated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Order(TimestampMixin, Base):
    __tablename__ = "wf_orders"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(160), nullable=False)
    order_type: Mapped[str] = mapped_column(String(30), nullable=False, default="STANDARD")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="NORMAL")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="NEW")
    requested_ship_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_warehouses.id"), nullable=True)

    lines: Mapped[List["OrderLine"]] = relationship(back_populates="order", cascade="all, delete-orphan")
    tasks: Mapped[List["FulfillmentTask"]] = relationship(back_populates="order")
    shipments: Mapped[List["Shipment"]] = relationship(back_populates="order")
    warehouse: Mapped[Optional[Warehouse]] = relationship()


class OrderLine(TimestampMixin, Base):
    __tablename__ = "wf_order_lines"
    __table_args__ = (
        UniqueConstraint("order_id", "line_number", name="uq_wf_order_lines_order_line"),
        CheckConstraint("quantity_ordered >= 0", name="ck_wf_order_lines_ordered_nonnegative"),
        CheckConstraint("quantity_allocated >= 0", name="ck_wf_order_lines_allocated_nonnegative"),
        CheckConstraint("quantity_shipped >= 0", name="ck_wf_order_lines_shipped_nonnegative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_orders.id"), nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_items.id"), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_ordered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_allocated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_shipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    order: Mapped[Order] = relationship(back_populates="lines")
    allocations: Mapped[List["Allocation"]] = relationship(back_populates="order_line")


class FulfillmentTask(TimestampMixin, Base):
    __tablename__ = "wf_fulfillment_tasks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_orders.id"), nullable=False)
    order_line_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_order_lines.id"), nullable=True)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_warehouses.id"), nullable=False)
    task_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="OPEN")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="NORMAL")
    assigned_to: Mapped[Optional[str]] = mapped_column(String(120))
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    order: Mapped[Order] = relationship(back_populates="tasks")


class Shipment(TimestampMixin, Base):
    __tablename__ = "wf_shipments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    shipment_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_orders.id"), nullable=False)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_warehouses.id"), nullable=False)
    carrier: Mapped[str] = mapped_column(String(60), nullable=False)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="PLANNED")
    shipped_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    shipped_by: Mapped[Optional[str]] = mapped_column(String(120))

    order: Mapped[Order] = relationship(back_populates="shipments")


class Allocation(TimestampMixin, Base):
    __tablename__ = "wf_allocations"
    __table_args__ = (
        CheckConstraint("quantity_allocated >= 0", name="ck_wf_allocations_allocated_nonnegative"),
        CheckConstraint("quantity_picked >= 0", name="ck_wf_allocations_picked_nonnegative"),
        CheckConstraint("quantity_packed >= 0", name="ck_wf_allocations_packed_nonnegative"),
        CheckConstraint("quantity_shipped >= 0", name="ck_wf_allocations_shipped_nonnegative"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_orders.id"), nullable=False)
    order_line_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_order_lines.id"), nullable=False)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_warehouses.id"), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_locations.id"), nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_items.id"), nullable=False)
    quantity_allocated: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_picked: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_packed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_shipped: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ALLOCATED")

    order: Mapped[Order] = relationship()
    order_line: Mapped[OrderLine] = relationship(back_populates="allocations")
    warehouse: Mapped[Warehouse] = relationship()
    location: Mapped[Location] = relationship()
    item: Mapped[Item] = relationship()


class InventoryTransaction(Base):
    __tablename__ = "wf_inventory_transactions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_number: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(30), nullable=False)
    warehouse_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_warehouses.id"), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_locations.id"), nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_items.id"), nullable=False)
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_orders.id"))
    order_line_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_order_lines.id"))
    allocation_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_allocations.id"))
    task_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_fulfillment_tasks.id"))
    shipment_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("wf_shipments.id"))
    quantity_on_hand_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_allocated_delta: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    quantity_on_hand_after: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_allocated_after: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_available_after: Mapped[int] = mapped_column(Integer, nullable=False)
    reference_type: Mapped[Optional[str]] = mapped_column(String(40))
    reference_number: Mapped[Optional[str]] = mapped_column(String(80))
    reason_code: Mapped[Optional[str]] = mapped_column(String(40))
    notes: Mapped[Optional[str]] = mapped_column(String(500))
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class OrderEvent(Base):
    __tablename__ = "wf_order_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wf_orders.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    from_status: Mapped[Optional[str]] = mapped_column(String(20))
    to_status: Mapped[Optional[str]] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    event_payload: Mapped[Optional[dict]] = mapped_column(JSON)
    created_by: Mapped[str] = mapped_column(String(120), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
