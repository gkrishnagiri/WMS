"""AMS ticket APIs and deterministic lifecycle transitions."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ams import AmsSummary, TicketCreate, TicketEventResponse, TicketResolveRequest, TicketResponse
from app.services import ams_ticket_service

router = APIRouter(prefix="/api/v1/ams", tags=["ams"])


def _error(error: ams_ticket_service.AmsError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("/summary", response_model=AmsSummary)
def summary(db: Session = Depends(get_db)) -> AmsSummary:
    return ams_ticket_service.get_summary(db)


@router.get("/tickets", response_model=list[TicketResponse])
def tickets(
    status_filter: str | None = Query(default=None, alias="status"),
    severity: str | None = None,
    priority: str | None = None,
    db: Session = Depends(get_db),
) -> list[TicketResponse]:
    return ams_ticket_service.list_tickets(db, status_filter, severity, priority)


@router.post("/tickets", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(request: TicketCreate, db: Session = Depends(get_db)) -> TicketResponse:
    try:
        return ams_ticket_service.create_manual_ticket(db, request)
    except ams_ticket_service.AmsError as error:
        db.rollback()
        raise _error(error) from error


@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def ticket_detail(ticket_id: UUID, db: Session = Depends(get_db)) -> TicketResponse:
    try:
        return ams_ticket_service.get_ticket(db, ticket_id)
    except ams_ticket_service.AmsError as error:
        raise _error(error) from error


@router.post("/tickets/from-exception/{exception_id}", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_from_exception(exception_id: UUID, db: Session = Depends(get_db)) -> TicketResponse:
    try:
        return ams_ticket_service.create_ticket_from_exception(db, exception_id)
    except ams_ticket_service.AmsError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/tickets/{ticket_id}/acknowledge", response_model=TicketResponse)
def acknowledge(ticket_id: UUID, db: Session = Depends(get_db)) -> TicketResponse:
    try:
        return ams_ticket_service.acknowledge_ticket(db, ticket_id)
    except ams_ticket_service.AmsError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/tickets/{ticket_id}/start-work", response_model=TicketResponse)
def start_work(ticket_id: UUID, db: Session = Depends(get_db)) -> TicketResponse:
    try:
        return ams_ticket_service.start_work(db, ticket_id)
    except ams_ticket_service.AmsError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/tickets/{ticket_id}/resolve", response_model=TicketResponse)
def resolve(ticket_id: UUID, request: TicketResolveRequest, db: Session = Depends(get_db)) -> TicketResponse:
    try:
        return ams_ticket_service.resolve_ticket(db, ticket_id, request.resolution_code, request.resolution_notes)
    except ams_ticket_service.AmsError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/tickets/{ticket_id}/close", response_model=TicketResponse)
def close(ticket_id: UUID, db: Session = Depends(get_db)) -> TicketResponse:
    try:
        return ams_ticket_service.close_ticket(db, ticket_id)
    except ams_ticket_service.AmsError as error:
        db.rollback()
        raise _error(error) from error


@router.get("/tickets/{ticket_id}/events", response_model=list[TicketEventResponse])
def events(ticket_id: UUID, db: Session = Depends(get_db)) -> list[TicketEventResponse]:
    try:
        return ams_ticket_service.list_events(db, ticket_id)
    except ams_ticket_service.AmsError as error:
        raise _error(error) from error

