"""Request and response schemas for operational exceptions and simulations."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ExceptionResponse(BaseModel):
    id: UUID
    exception_number: str
    exception_type: str
    severity: str
    status: str
    source_module: str
    source_entity_type: str
    source_entity_id: UUID | None
    source_reference: str | None
    title: str
    description: str
    detection_method: str
    business_impact: str
    technical_context: dict | None
    first_detected_at: datetime
    last_detected_at: datetime
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime
    linked_ticket_id: UUID | None = None
    linked_ticket_number: str | None = None


class LowStockSimulationRequest(BaseModel):
    item_id: UUID | None = None
    warehouse_id: UUID | None = None
    create_ticket: bool = True


class TaskBlockedSimulationRequest(BaseModel):
    task_id: UUID | None = None
    reason: str = Field(default="Operational task is blocked.", min_length=1, max_length=500)
    create_ticket: bool = True


class ShipmentExceptionSimulationRequest(BaseModel):
    shipment_id: UUID | None = None
    reason: str = Field(default="Shipment requires operational investigation.", min_length=1, max_length=500)
    create_ticket: bool = True


class OrderStuckSimulationRequest(BaseModel):
    order_id: UUID | None = None
    status: str = "PICKING"
    create_ticket: bool = True


class SimulationResult(BaseModel):
    simulation_type: str
    exception: ExceptionResponse
    ticket: "TicketResponse | None" = None


class DetectOrderStuckRequest(BaseModel):
    threshold_hours: float = Field(default=24, gt=0, le=24 * 365)


from app.schemas.ams import TicketResponse  # noqa: E402

SimulationResult.model_rebuild()

