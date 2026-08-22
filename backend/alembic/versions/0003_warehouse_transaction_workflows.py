"""Add controlled warehouse transaction workflow tables.

Revision ID: 0003_warehouse_workflows
Revises: 0002_warehouse_fulfillment
Create Date: 2026-08-21
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0003_warehouse_workflows"
down_revision: Union[str, Sequence[str], None] = "0002_warehouse_fulfillment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

uuid_type = postgresql.UUID(as_uuid=True)
timestamp_type = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.add_column("wf_orders", sa.Column("warehouse_id", uuid_type, sa.ForeignKey("wf_warehouses.id"), nullable=True))
    op.add_column("wf_shipments", sa.Column("shipped_by", sa.String(length=120), nullable=True))

    op.create_table(
        "wf_allocations",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("order_id", uuid_type, sa.ForeignKey("wf_orders.id"), nullable=False),
        sa.Column("order_line_id", uuid_type, sa.ForeignKey("wf_order_lines.id"), nullable=False),
        sa.Column("warehouse_id", uuid_type, sa.ForeignKey("wf_warehouses.id"), nullable=False),
        sa.Column("location_id", uuid_type, sa.ForeignKey("wf_locations.id"), nullable=False),
        sa.Column("item_id", uuid_type, sa.ForeignKey("wf_items.id"), nullable=False),
        sa.Column("quantity_allocated", sa.Integer, nullable=False),
        sa.Column("quantity_picked", sa.Integer, nullable=False, server_default="0"),
        sa.Column("quantity_packed", sa.Integer, nullable=False, server_default="0"),
        sa.Column("quantity_shipped", sa.Integer, nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ALLOCATED"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("quantity_allocated >= 0", name="ck_wf_allocations_allocated_nonnegative"),
        sa.CheckConstraint("quantity_picked >= 0", name="ck_wf_allocations_picked_nonnegative"),
        sa.CheckConstraint("quantity_packed >= 0", name="ck_wf_allocations_packed_nonnegative"),
        sa.CheckConstraint("quantity_shipped >= 0", name="ck_wf_allocations_shipped_nonnegative"),
    )
    op.create_table(
        "wf_inventory_transactions",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("transaction_number", sa.String(length=60), nullable=False),
        sa.Column("transaction_type", sa.String(length=30), nullable=False),
        sa.Column("warehouse_id", uuid_type, sa.ForeignKey("wf_warehouses.id"), nullable=False),
        sa.Column("location_id", uuid_type, sa.ForeignKey("wf_locations.id"), nullable=False),
        sa.Column("item_id", uuid_type, sa.ForeignKey("wf_items.id"), nullable=False),
        sa.Column("order_id", uuid_type, sa.ForeignKey("wf_orders.id")),
        sa.Column("order_line_id", uuid_type, sa.ForeignKey("wf_order_lines.id")),
        sa.Column("allocation_id", uuid_type, sa.ForeignKey("wf_allocations.id")),
        sa.Column("task_id", uuid_type, sa.ForeignKey("wf_fulfillment_tasks.id")),
        sa.Column("shipment_id", uuid_type, sa.ForeignKey("wf_shipments.id")),
        sa.Column("quantity_on_hand_delta", sa.Integer, nullable=False, server_default="0"),
        sa.Column("quantity_allocated_delta", sa.Integer, nullable=False, server_default="0"),
        sa.Column("quantity_on_hand_after", sa.Integer, nullable=False),
        sa.Column("quantity_allocated_after", sa.Integer, nullable=False),
        sa.Column("quantity_available_after", sa.Integer, nullable=False),
        sa.Column("reference_type", sa.String(length=40)),
        sa.Column("reference_number", sa.String(length=80)),
        sa.Column("reason_code", sa.String(length=40)),
        sa.Column("notes", sa.String(length=500)),
        sa.Column("created_by", sa.String(length=120), nullable=False, server_default="system"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("transaction_number", name="uq_wf_inventory_transactions_number"),
    )
    op.create_table(
        "wf_order_events",
        sa.Column("id", uuid_type, primary_key=True, nullable=False),
        sa.Column("order_id", uuid_type, sa.ForeignKey("wf_orders.id"), nullable=False),
        sa.Column("event_type", sa.String(length=40), nullable=False),
        sa.Column("from_status", sa.String(length=20)),
        sa.Column("to_status", sa.String(length=20)),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("event_payload", postgresql.JSONB),
        sa.Column("created_by", sa.String(length=120), nullable=False, server_default="system"),
        sa.Column("created_at", timestamp_type, nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("wf_order_events")
    op.drop_table("wf_inventory_transactions")
    op.drop_table("wf_allocations")
    op.drop_column("wf_shipments", "shipped_by")
    op.drop_column("wf_orders", "warehouse_id")
