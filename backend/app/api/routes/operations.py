"""Operational exception and deterministic failure simulation APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ams import TicketResponse
from app.schemas.operations import (
    DetectOrderStuckRequest,
    ExceptionResponse,
    LowStockSimulationRequest,
    OrderStuckSimulationRequest,
    ShipmentExceptionSimulationRequest,
    SimulationResult,
    TaskBlockedSimulationRequest,
)
from app.services import ams_ticket_service, operations_exception_service

router = APIRouter(prefix="/api/v1/operations", tags=["operations"])


def _error(error: operations_exception_service.OperationsError | ams_ticket_service.AmsError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


def _simulation_result(db: Session, simulation_type: str, exception: ExceptionResponse, create_ticket: bool) -> SimulationResult:
    ticket: TicketResponse | None = None
    if create_ticket:
        ticket = ams_ticket_service.create_ticket_from_exception(db, exception.id)
    else:
        db.commit()
    return SimulationResult(
        simulation_type=simulation_type,
        exception=operations_exception_service.get_exception(db, exception.id),
        ticket=ticket,
    )


@router.get("/exceptions", response_model=list[ExceptionResponse])
def exceptions(
    status_filter: str | None = Query(default=None, alias="status"),
    severity: str | None = None,
    exception_type: str | None = None,
    source_module: str | None = None,
    db: Session = Depends(get_db),
) -> list[ExceptionResponse]:
    return operations_exception_service.list_exceptions(db, status_filter, severity, exception_type, source_module)


@router.get("/exceptions/{exception_id}", response_model=ExceptionResponse)
def exception_detail(exception_id: UUID, db: Session = Depends(get_db)) -> ExceptionResponse:
    try:
        return operations_exception_service.get_exception(db, exception_id)
    except operations_exception_service.OperationsError as error:
        raise _error(error) from error


@router.post("/exceptions/{exception_id}/acknowledge", response_model=ExceptionResponse)
def acknowledge_exception(exception_id: UUID, db: Session = Depends(get_db)) -> ExceptionResponse:
    try:
        return operations_exception_service.acknowledge_exception(db, exception_id)
    except operations_exception_service.OperationsError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/exceptions/{exception_id}/resolve", response_model=ExceptionResponse)
def resolve_exception(exception_id: UUID, db: Session = Depends(get_db)) -> ExceptionResponse:
    try:
        return operations_exception_service.resolve_exception(db, exception_id)
    except operations_exception_service.OperationsError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/detect/low-stock", response_model=list[ExceptionResponse])
def detect_low_stock(item_id: UUID | None = None, warehouse_id: UUID | None = None, db: Session = Depends(get_db)) -> list[ExceptionResponse]:
    return operations_exception_service.detect_low_stock(db, item_id, warehouse_id)


@router.post("/detect/order-stuck", response_model=list[ExceptionResponse])
def detect_order_stuck(request: DetectOrderStuckRequest | None = None, db: Session = Depends(get_db)) -> list[ExceptionResponse]:
    return operations_exception_service.detect_order_stuck(db, request.threshold_hours if request else 24)


@router.post("/simulations/low-stock", response_model=SimulationResult)
def simulate_low_stock(request: LowStockSimulationRequest, db: Session = Depends(get_db)) -> SimulationResult:
    try:
        exception = operations_exception_service.simulate_low_stock(db, request.item_id, request.warehouse_id)
        return _simulation_result(db, "LOW_STOCK", exception, request.create_ticket)
    except (operations_exception_service.OperationsError, ams_ticket_service.AmsError) as error:
        db.rollback()
        raise _error(error) from error


@router.post("/simulations/task-blocked", response_model=SimulationResult)
def simulate_task_blocked(request: TaskBlockedSimulationRequest, db: Session = Depends(get_db)) -> SimulationResult:
    try:
        exception = operations_exception_service.simulate_task_blocked(db, request.task_id, request.reason)
        return _simulation_result(db, "TASK_BLOCKED", exception, request.create_ticket)
    except (operations_exception_service.OperationsError, ams_ticket_service.AmsError) as error:
        db.rollback()
        raise _error(error) from error


@router.post("/simulations/shipment-exception", response_model=SimulationResult)
def simulate_shipment_exception(request: ShipmentExceptionSimulationRequest, db: Session = Depends(get_db)) -> SimulationResult:
    try:
        exception = operations_exception_service.simulate_shipment_exception(db, request.shipment_id, request.reason)
        return _simulation_result(db, "SHIPMENT_EXCEPTION", exception, request.create_ticket)
    except (operations_exception_service.OperationsError, ams_ticket_service.AmsError) as error:
        db.rollback()
        raise _error(error) from error


@router.post("/simulations/order-stuck", response_model=SimulationResult)
def simulate_order_stuck(request: OrderStuckSimulationRequest, db: Session = Depends(get_db)) -> SimulationResult:
    try:
        exception = operations_exception_service.simulate_order_stuck(db, request.order_id, request.status)
        return _simulation_result(db, "ORDER_STUCK", exception, request.create_ticket)
    except (operations_exception_service.OperationsError, ams_ticket_service.AmsError) as error:
        db.rollback()
        raise _error(error) from error

