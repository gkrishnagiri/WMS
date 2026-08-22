"""User-reported functional issue APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user_reports import UserReportCreate, UserReportResponse
from app.services import ams_ticket_service, user_report_service

router = APIRouter(prefix="/api/v1/ams/user-reports", tags=["ams-user-reports"])


def _error(error: user_report_service.UserReportError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("", response_model=list[UserReportResponse])
def reports(
    status_filter: str | None = Query(default=None, alias="status"),
    severity: str | None = None,
    db: Session = Depends(get_db),
) -> list[UserReportResponse]:
    return user_report_service.list_reports(db, status_filter, severity)


@router.post("", response_model=UserReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(request: UserReportCreate, db: Session = Depends(get_db)) -> UserReportResponse:
    try:
        return user_report_service.create_report(db, request)
    except (user_report_service.UserReportError, ams_ticket_service.AmsError) as error:
        db.rollback()
        if isinstance(error, ams_ticket_service.AmsError):
            raise HTTPException(status_code=error.status_code, detail=error.message) from error
        raise _error(error) from error


@router.get("/{report_id}", response_model=UserReportResponse)
def report_detail(report_id: UUID, db: Session = Depends(get_db)) -> UserReportResponse:
    try:
        return user_report_service.get_report(db, report_id)
    except user_report_service.UserReportError as error:
        raise _error(error) from error


@router.post("/{report_id}/create-ticket", response_model=UserReportResponse)
def create_ticket(report_id: UUID, db: Session = Depends(get_db)) -> UserReportResponse:
    try:
        return user_report_service.create_ticket(db, report_id)
    except user_report_service.UserReportError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/{report_id}/acknowledge", response_model=UserReportResponse)
def acknowledge(report_id: UUID, db: Session = Depends(get_db)) -> UserReportResponse:
    try:
        return user_report_service.acknowledge_report(db, report_id)
    except user_report_service.UserReportError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/{report_id}/resolve", response_model=UserReportResponse)
def resolve(report_id: UUID, db: Session = Depends(get_db)) -> UserReportResponse:
    try:
        return user_report_service.resolve_report(db, report_id)
    except user_report_service.UserReportError as error:
        db.rollback()
        raise _error(error) from error
