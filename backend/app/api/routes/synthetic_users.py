"""Synthetic user catalog and deterministic journey APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.synthetic_users import JourneyRunResponse, RunJourneyRequest, RunSuiteRequest, RunSuiteResponse, SyntheticJourneyResponse, SyntheticUserResponse
from app.services import ams_ticket_service, synthetic_user_service, user_report_service

router = APIRouter(prefix="/api/v1/synthetic-users", tags=["synthetic-users"])


def _error(error: synthetic_user_service.SyntheticUserError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("/users", response_model=list[SyntheticUserResponse])
def users(db: Session = Depends(get_db)) -> list[SyntheticUserResponse]:
    return [SyntheticUserResponse.model_validate(user, from_attributes=True) for user in synthetic_user_service.list_users(db)]


@router.get("/journeys", response_model=list[SyntheticJourneyResponse])
def journeys(db: Session = Depends(get_db)) -> list[SyntheticJourneyResponse]:
    return [SyntheticJourneyResponse.model_validate(journey, from_attributes=True) for journey in synthetic_user_service.list_journeys(db)]


@router.get("/journeys/{journey_code}", response_model=SyntheticJourneyResponse)
def journey_detail(journey_code: str, db: Session = Depends(get_db)) -> SyntheticJourneyResponse:
    try:
        return SyntheticJourneyResponse.model_validate(synthetic_user_service.get_journey(db, journey_code), from_attributes=True)
    except synthetic_user_service.SyntheticUserError as error:
        raise _error(error) from error


@router.post("/journeys/{journey_code}/run", response_model=JourneyRunResponse)
def run_journey(journey_code: str, request: RunJourneyRequest, db: Session = Depends(get_db)) -> JourneyRunResponse:
    try:
        return synthetic_user_service.run_journey(db, journey_code, request)
    except (synthetic_user_service.SyntheticUserError, user_report_service.UserReportError, ams_ticket_service.AmsError) as error:
        db.rollback()
        raise HTTPException(status_code=error.status_code, detail=error.message) from error


@router.post("/run-suite", response_model=RunSuiteResponse)
def run_suite(request: RunSuiteRequest, db: Session = Depends(get_db)) -> RunSuiteResponse:
    try:
        return synthetic_user_service.run_suite(db, request.create_ticket)
    except (synthetic_user_service.SyntheticUserError, user_report_service.UserReportError, ams_ticket_service.AmsError) as error:
        db.rollback()
        raise HTTPException(status_code=error.status_code, detail=error.message) from error


@router.get("/runs", response_model=list[JourneyRunResponse])
def runs(
    journey_code: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    synthetic_user_id: UUID | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[JourneyRunResponse]:
    return synthetic_user_service.list_runs(db, journey_code, status_filter, synthetic_user_id, limit)


@router.get("/runs/{run_id}", response_model=JourneyRunResponse)
def run_detail(run_id: UUID, db: Session = Depends(get_db)) -> JourneyRunResponse:
    try:
        return synthetic_user_service.get_run(db, run_id)
    except synthetic_user_service.SyntheticUserError as error:
        raise _error(error) from error
