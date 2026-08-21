"""Add Warehouse & Fulfillment domain tables.

Revision ID: 0002_warehouse_fulfillment
Revises: 0001_empty_baseline
Create Date: 2026-08-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0002_warehouse_fulfillment"
down_revision: Union[str, Sequence[str], None] = "0001_empty_baseline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

uuid_type = postgresql.UUID(as_uuid=True)
timestamp_type = sa.DateTime(timezone=True)


def _timestamps() -> dict[str, object]:
    return {"created_at": timestamp_type, "updated_at": timestamp_type}


def upgrade() -> None:
    op.create_table(
        "wf_warehouses",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("region", sa.String(length=80), nullable=False),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("country", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("code", name="uq_wf_warehouses_code"),
    )
    op.create_table(
        "wf_zones",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("warehouse_id", uuid_type, sa.ForeignKey("wf_warehouses.id"), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("zone_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("warehouse_id", "code", name="uq_wf_zones_warehouse_code"),
    )
    op.create_table(
        "wf_locations",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("warehouse_id", uuid_type, sa.ForeignKey("wf_warehouses.id"), nullable=False),
        sa.Column("zone_id", uuid_type, sa.ForeignKey("wf_zones.id"), nullable=False),
        sa.Column("code", sa.String(length=60), nullable=False),
        sa.Column("aisle", sa.String(length=20)),
        sa.Column("bay", sa.String(length=20)),
        sa.Column("level", sa.String(length=20)),
        sa.Column("bin", sa.String(length=20)),
        sa.Column("location_type", sa.String(length=30), nullable=False),
        sa.Column("capacity_units", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("warehouse_id", "code", name="uq_wf_locations_warehouse_code"),
    )
    op.create_table(
        "wf_items",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("sku", sa.String(length=60), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("unit_of_measure", sa.String(length=20), nullable=False, server_default="EA"),
        sa.Column("reorder_point", sa.Integer, nullable=False, server_default="0"),
        sa.Column("safety_stock", sa.Integer, nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("sku", name="uq_wf_items_sku"),
    )
    op.create_table(
        "wf_inventory_balances",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("warehouse_id", uuid_type, sa.ForeignKey("wf_warehouses.id"), nullable=False),
        sa.Column("location_id", uuid_type, sa.ForeignKey("wf_locations.id"), nullable=False),
        sa.Column("item_id", uuid_type, sa.ForeignKey("wf_items.id"), nullable=False),
        sa.Column("quantity_on_hand", sa.Integer, nullable=False, server_default="0"),
        sa.Column("quantity_allocated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("location_id", "item_id", name="uq_wf_inventory_location_item"),
        sa.CheckConstraint("quantity_on_hand >= 0", name="ck_wf_inventory_on_hand_nonnegative"),
        sa.CheckConstraint("quantity_allocated >= 0", name="ck_wf_inventory_allocated_nonnegative"),
    )
    op.create_table(
        "wf_orders",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("order_number", sa.String(length=60), nullable=False),
        sa.Column("customer_name", sa.String(length=160), nullable=False),
        sa.Column("order_type", sa.String(length=30), nullable=False, server_default="STANDARD"),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="NORMAL"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="NEW"),
        sa.Column("requested_ship_date", sa.Date),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("order_number", name="uq_wf_orders_order_number"),
    )
    op.create_table(
        "wf_order_lines",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("order_id", uuid_type, sa.ForeignKey("wf_orders.id"), nullable=False),
        sa.Column("item_id", uuid_type, sa.ForeignKey("wf_items.id"), nullable=False),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("quantity_ordered", sa.Integer, nullable=False, server_default="0"),
        sa.Column("quantity_allocated", sa.Integer, nullable=False, server_default="0"),
        sa.Column("quantity_shipped", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("order_id", "line_number", name="uq_wf_order_lines_order_line"),
        sa.CheckConstraint("quantity_ordered >= 0", name="ck_wf_order_lines_ordered_nonnegative"),
        sa.CheckConstraint("quantity_allocated >= 0", name="ck_wf_order_lines_allocated_nonnegative"),
        sa.CheckConstraint("quantity_shipped >= 0", name="ck_wf_order_lines_shipped_nonnegative"),
    )
    op.create_table(
        "wf_fulfillment_tasks",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("task_number", sa.String(length=60), nullable=False),
        sa.Column("order_id", uuid_type, sa.ForeignKey("wf_orders.id"), nullable=False),
        sa.Column("order_line_id", uuid_type, sa.ForeignKey("wf_order_lines.id")),
        sa.Column("warehouse_id", uuid_type, sa.ForeignKey("wf_warehouses.id"), nullable=False),
        sa.Column("task_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="OPEN"),
        sa.Column("priority", sa.String(length=20), nullable=False, server_default="NORMAL"),
        sa.Column("assigned_to", sa.String(length=120)),
        sa.Column("due_at", timestamp_type),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("task_number", name="uq_wf_tasks_task_number"),
    )
    op.create_table(
        "wf_shipments",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("shipment_number", sa.String(length=60), nullable=False),
        sa.Column("order_id", uuid_type, sa.ForeignKey("wf_orders.id"), nullable=False),
        sa.Column("warehouse_id", uuid_type, sa.ForeignKey("wf_warehouses.id"), nullable=False),
        sa.Column("carrier", sa.String(length=60), nullable=False),
        sa.Column("tracking_number", sa.String(length=120)),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="PLANNED"),
        sa.Column("shipped_at", timestamp_type),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("shipment_number", name="uq_wf_shipments_shipment_number"),
    )


def downgrade() -> None:
    op.drop_table("wf_shipments")
    op.drop_table("wf_fulfillment_tasks")
    op.drop_table("wf_order_lines")
    op.drop_table("wf_orders")
    op.drop_table("wf_inventory_balances")
    op.drop_table("wf_items")
    op.drop_table("wf_locations")
    op.drop_table("wf_zones")
    op.drop_table("wf_warehouses")
