"""Deterministic backend-driven synthetic user journey execution."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ams import AmsTicket
from app.models.synthetic_users import SyntheticJourney, SyntheticJourneyRun, SyntheticUser
from app.models.user_reports import AmsUserReport
from app.models.warehouse import FulfillmentTask, InventoryBalance, Item, Location, Order, Shipment, Warehouse
from app.schemas.synthetic_users import JourneyRunResponse, RunJourneyRequest, RunSuiteResponse
from app.schemas.user_reports import UserReportCreate
from app.schemas.warehouse_transactions import OrderCreate, OrderLineCreate, ShipOrderRequest
from app.services import user_report_service, warehouse_workflow_service


class SyntheticUserError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_run_number(db: Session) -> str:
    prefix = f"SYN-RUN-{_now():%Y%m%d}-"
    current = db.scalar(select(func.max(SyntheticJourneyRun.run_number)).where(SyntheticJourneyRun.run_number.like(f"{prefix}%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            sequence = 1
    return f"{prefix}{sequence:04d}"


def list_users(db: Session) -> list[SyntheticUser]:
    return db.scalars(select(SyntheticUser).order_by(SyntheticUser.user_code)).all()


def list_journeys(db: Session) -> list[SyntheticJourney]:
    return db.scalars(select(SyntheticJourney).order_by(SyntheticJourney.journey_code)).all()


def get_journey(db: Session, journey_code: str) -> SyntheticJourney:
    journey = db.scalar(select(SyntheticJourney).where(SyntheticJourney.journey_code == journey_code.upper()))
    if journey is None:
        raise SyntheticUserError("Synthetic journey not found.", 404)
    return journey


def _find_user(db: Session, journey: SyntheticJourney, user_id: UUID | None) -> SyntheticUser:
    if user_id:
        user = db.get(SyntheticUser, user_id)
        if user is None:
            raise SyntheticUserError("Synthetic user not found.", 404)
        if not user.active:
            raise SyntheticUserError("Inactive synthetic users cannot run journeys.", 409)
        return user
    user = db.scalar(select(SyntheticUser).where(SyntheticUser.active.is_(True), SyntheticUser.persona == journey.persona).order_by(SyntheticUser.user_code))
    if user is None:
        raise SyntheticUserError(f"No active synthetic user is available for persona {journey.persona}.", 409)
    return user


def _run_response(db: Session, run: SyntheticJourneyRun) -> JourneyRunResponse:
    journey = db.get(SyntheticJourney, run.journey_id)
    user = db.get(SyntheticUser, run.synthetic_user_id)
    report = db.get(AmsUserReport, run.user_report_id) if run.user_report_id else None
    ticket = db.get(AmsTicket, run.ticket_id) if run.ticket_id else None
    if journey is None or user is None:
        raise SyntheticUserError("Journey run references missing catalog data.", 500)
    return JourneyRunResponse(
        id=run.id, run_number=run.run_number, journey_id=run.journey_id, journey_code=journey.journey_code,
        journey_name=journey.name, synthetic_user_id=run.synthetic_user_id, synthetic_user_name=user.display_name,
        status=run.status, started_at=run.started_at, completed_at=run.completed_at, duration_ms=run.duration_ms,
        input_payload=run.input_payload, result_payload=run.result_payload, failure_type=run.failure_type,
        failure_message=run.failure_message, order_id=run.order_id, task_id=run.task_id, shipment_id=run.shipment_id,
        user_report_id=run.user_report_id, user_report_number=report.report_number if report else None,
        ticket_id=run.ticket_id, ticket_number=ticket.ticket_number if ticket else None,
        created_at=run.created_at, updated_at=run.updated_at,
    )


def list_runs(db: Session, journey_code: str | None = None, status: str | None = None, synthetic_user_id: UUID | None = None, limit: int = 100) -> list[JourneyRunResponse]:
    statement = select(SyntheticJourneyRun).join(SyntheticJourney).order_by(SyntheticJourneyRun.started_at.desc(), SyntheticJourneyRun.run_number.desc()).limit(limit)
    if journey_code:
        statement = statement.where(SyntheticJourney.journey_code == journey_code.upper())
    if status:
        statement = statement.where(SyntheticJourneyRun.status == status.upper())
    if synthetic_user_id:
        statement = statement.where(SyntheticJourneyRun.synthetic_user_id == synthetic_user_id)
    return [_run_response(db, run) for run in db.scalars(statement).all()]


def get_run(db: Session, run_id: UUID) -> JourneyRunResponse:
    run = db.get(SyntheticJourneyRun, run_id)
    if run is None:
        raise SyntheticUserError("Synthetic journey run not found.", 404)
    return _run_response(db, run)


def _select_order_item(db: Session) -> tuple[InventoryBalance, Item, Warehouse, Location]:
    result = db.execute(
        select(InventoryBalance, Item, Warehouse, Location)
        .join(Item, Item.id == InventoryBalance.item_id)
        .join(Warehouse, Warehouse.id == InventoryBalance.warehouse_id)
        .join(Location, Location.id == InventoryBalance.location_id)
        .where(InventoryBalance.quantity_on_hand - InventoryBalance.quantity_allocated >= 1, Warehouse.status == "ACTIVE", Location.status == "ACTIVE", Item.active.is_(True))
        .order_by(Warehouse.code, Location.code, Item.sku)
    ).first()
    if result is None:
        raise SyntheticUserError("No available inventory exists for a synthetic order.", 409)
    return result


def _create_small_order(db: Session, customer: str, quantity: int = 1) -> Any:
    _balance, item, warehouse, _location = _select_order_item(db)
    return warehouse_workflow_service.create_order(
        db,
        OrderCreate(customer_name=customer, order_type="STANDARD", priority="NORMAL", warehouse_id=warehouse.id, lines=[OrderLineCreate(item_id=item.id, quantity_ordered=quantity)]),
    )


def _create_failure_report(db: Session, run: SyntheticJourneyRun, user: SyntheticUser, title: str, description: str, business_impact: str, severity: str, create_ticket: bool, entity_type: str = "ORDER", entity_id: UUID | None = None) -> None:
    report = user_report_service.create_report(
        db,
        UserReportCreate(
            reporter_user_id=user.id, reporter_name=user.display_name, reporter_email=user.email, reporter_persona=user.persona,
            report_channel="SYNTHETIC_USER", source_module="WAREHOUSE_FULFILLMENT", affected_entity_type=entity_type,
            affected_entity_id=entity_id, title=title, description=description, business_impact=business_impact,
            severity=severity, journey_run_id=run.id, create_ticket=create_ticket,
        ),
    )
    run.user_report_id = report.id
    run.ticket_id = report.ticket_id


def _finish(db: Session, run: SyntheticJourneyRun, started: datetime, status: str, result: dict, failure_type: str | None = None, failure_message: str | None = None) -> JourneyRunResponse:
    completed = _now()
    run.status = status
    run.completed_at = completed
    run.duration_ms = max(0, int((completed - started).total_seconds() * 1000))
    run.result_payload = result
    run.failure_type = failure_type
    run.failure_message = failure_message
    run.updated_at = completed
    db.commit()
    return _run_response(db, run)


def run_journey(db: Session, journey_code: str, request: RunJourneyRequest) -> JourneyRunResponse:
    journey = get_journey(db, journey_code)
    if not journey.enabled:
        raise SyntheticUserError("Synthetic journey is disabled.", 409)
    user = _find_user(db, journey, request.synthetic_user_id)
    started = _now()
    input_payload = {**(journey.default_payload or {}), **request.input_payload, "create_ticket": request.create_ticket}
    run = SyntheticJourneyRun(run_number=_next_run_number(db), journey_id=journey.id, synthetic_user_id=user.id, status="PARTIAL", started_at=started, input_payload=input_payload, created_at=started, updated_at=started)
    db.add(run)
    db.commit()
    try:
        if journey.journey_code == "JRN-ORDER-FULFILL-SUCCESS":
            order = _create_small_order(db, f"{user.display_name} Success Customer")
            run = db.get(SyntheticJourneyRun, run.id)
            run.order_id = order.id
            allocated = warehouse_workflow_service.allocate_order(db, order.id)
            released = warehouse_workflow_service.release_tasks(db, order.id)
            pick = next(task for task in released.tasks if task.task_type == "PICK")
            pack = next(task for task in released.tasks if task.task_type == "PACK")
            warehouse_workflow_service.start_task(db, pick.id)
            warehouse_workflow_service.complete_task(db, pick.id)
            warehouse_workflow_service.start_task(db, pack.id)
            warehouse_workflow_service.complete_task(db, pack.id)
            shipped = warehouse_workflow_service.ship_order(db, order.id, ShipOrderRequest(carrier="UPS", shipped_by="synthetic-user"))
            run = db.get(SyntheticJourneyRun, run.id)
            run.order_id = shipped.id
            run.shipment_id = shipped.shipments[0].id if shipped.shipments else None
            return _finish(db, run, started, "SUCCESS", {"message": "Synthetic fulfillment completed successfully.", "order_id": str(shipped.id), "shipment_id": str(run.shipment_id) if run.shipment_id else None})

        if journey.journey_code == "JRN-ALLOCATE-INSUFFICIENT-STOCK":
            order = _create_small_order(db, f"{user.display_name} Insufficient Stock Customer", int(input_payload.get("quantity", 999999)))
            run = db.get(SyntheticJourneyRun, run.id)
            run.order_id = order.id
            try:
                warehouse_workflow_service.allocate_order(db, order.id)
            except warehouse_workflow_service.WorkflowError as error:
                db.rollback()
                run = db.get(SyntheticJourneyRun, run.id)
                _create_failure_report(db, run, user, "User unable to allocate customer order due to insufficient stock", error.message, "Customer order allocation is blocked and fulfillment is delayed.", "HIGH", request.create_ticket, "ORDER", run.order_id)
                return _finish(db, run, started, "FAILED", {"order_id": str(run.order_id)}, "INSUFFICIENT_STOCK", error.message)
            raise SyntheticUserError("Insufficient-stock journey unexpectedly allocated.", 409)

        if journey.journey_code == "JRN-PACK-BEFORE-PICK":
            order = _create_small_order(db, f"{user.display_name} Pack Validation Customer")
            run = db.get(SyntheticJourneyRun, run.id)
            run.order_id = order.id
            warehouse_workflow_service.allocate_order(db, order.id)
            released = warehouse_workflow_service.release_tasks(db, order.id)
            pack = next(task for task in released.tasks if task.task_type == "PACK")
            try:
                warehouse_workflow_service.complete_task(db, pack.id)
            except warehouse_workflow_service.WorkflowError as error:
                db.rollback()
                run = db.get(SyntheticJourneyRun, run.id)
                _create_failure_report(db, run, user, "User attempted pack step before picking was completed", error.message, "The warehouse workflow cannot advance until picking is completed.", "MEDIUM", request.create_ticket, "ORDER", run.order_id)
                return _finish(db, run, started, "FAILED", {"order_id": str(run.order_id), "task_id": str(pack.id)}, "PACK_BEFORE_PICK", error.message)
            raise SyntheticUserError("Pack-before-pick journey unexpectedly completed.", 409)

        if journey.journey_code == "JRN-SHIP-BEFORE-PACK":
            order = _create_small_order(db, f"{user.display_name} Ship Validation Customer")
            run = db.get(SyntheticJourneyRun, run.id)
            run.order_id = order.id
            warehouse_workflow_service.allocate_order(db, order.id)
            released = warehouse_workflow_service.release_tasks(db, order.id)
            if input_payload.get("complete_pick"):
                pick = next(task for task in released.tasks if task.task_type == "PICK")
                warehouse_workflow_service.complete_task(db, pick.id)
            try:
                warehouse_workflow_service.ship_order(db, order.id, ShipOrderRequest(carrier="UPS", shipped_by="synthetic-user"))
            except warehouse_workflow_service.WorkflowError as error:
                db.rollback()
                run = db.get(SyntheticJourneyRun, run.id)
                _create_failure_report(db, run, user, "User unable to ship order because pack step is incomplete", error.message, "Customer shipment is delayed because warehouse packing is incomplete.", "HIGH", request.create_ticket, "ORDER", run.order_id)
                return _finish(db, run, started, "FAILED", {"order_id": str(run.order_id)}, "SHIP_BEFORE_PACK", error.message)
            raise SyntheticUserError("Ship-before-pack journey unexpectedly shipped.", 409)

        if journey.journey_code == "JRN-MANUAL-FUNCTIONAL-ISSUE":
            _create_failure_report(db, run, user, "Order dashboard shows confusing fulfillment status for business user", "The synthetic business user reports that the order dashboard does not clearly explain the current fulfillment status.", "The business user may be unable to confidently determine whether an order requires action.", "MEDIUM", request.create_ticket, "SCREEN")
            return _finish(db, run, started, "SUCCESS", {"message": "Manual functional issue report submitted."})

        raise SyntheticUserError("Synthetic journey implementation is not available.", 409)
    except warehouse_workflow_service.WorkflowError as error:
        db.rollback()
        run = db.get(SyntheticJourneyRun, run.id)
        return _finish(db, run, started, "FAILED", {}, "WORKFLOW_FAILURE", error.message)


def run_suite(db: Session, create_ticket: bool) -> RunSuiteResponse:
    journeys = db.scalars(select(SyntheticJourney).where(SyntheticJourney.enabled.is_(True)).order_by(SyntheticJourney.journey_code)).all()
    runs: list[JourneyRunResponse] = []
    for journey in journeys:
        try:
            runs.append(run_journey(db, journey.journey_code, RunJourneyRequest(create_ticket=create_ticket)))
        except SyntheticUserError as error:
            # Catalog or environment problems are recorded as a failed run when
            # a journey could not reach its execution path.
            user = _find_user(db, journey, None)
            now = _now()
            run = SyntheticJourneyRun(run_number=_next_run_number(db), journey_id=journey.id, synthetic_user_id=user.id, status="FAILED", started_at=now, completed_at=now, duration_ms=0, input_payload={"create_ticket": create_ticket}, result_payload={}, failure_type="JOURNEY_EXECUTION", failure_message=error.message, created_at=now, updated_at=now)
            db.add(run)
            db.commit()
            runs.append(_run_response(db, run))
    return RunSuiteResponse(total=len(runs), succeeded=sum(run.status == "SUCCESS" for run in runs), failed=sum(run.status == "FAILED" for run in runs), runs=runs)
