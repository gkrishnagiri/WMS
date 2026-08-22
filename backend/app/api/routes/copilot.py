"""Governed deterministic support copilot APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.copilot import CopilotAnalyzeRequest, CopilotContextResponse, CopilotActionPlanResponse, CopilotMessageResponse, CopilotRecommendationResponse, CopilotSafeActionResponse, CopilotSessionCreate, CopilotSessionResponse, CopilotSummary
from app.services import copilot_service

router = APIRouter(prefix="/api/v1/copilot", tags=["copilot"])


def _error(error: copilot_service.CopilotError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("/summary", response_model=CopilotSummary)
def summary(db: Session = Depends(get_db)) -> CopilotSummary:
    return copilot_service.get_summary(db)


@router.get("/safe-actions", response_model=list[CopilotSafeActionResponse])
def safe_actions(db: Session = Depends(get_db)) -> list[CopilotSafeActionResponse]:
    return copilot_service.list_safe_actions(db)


@router.get("/sessions", response_model=list[CopilotSessionResponse])
def sessions(db: Session = Depends(get_db)) -> list[CopilotSessionResponse]:
    return copilot_service.list_sessions(db)


@router.post("/sessions", response_model=CopilotSessionResponse, status_code=201)
def create_session(request: CopilotSessionCreate, db: Session = Depends(get_db)) -> CopilotSessionResponse:
    try:
        return copilot_service.create_session(db, request)
    except copilot_service.CopilotError as error:
        raise _error(error) from error


@router.get("/sessions/{session_id}", response_model=CopilotSessionResponse)
def session_detail(session_id: UUID, db: Session = Depends(get_db)) -> CopilotSessionResponse:
    try:
        return copilot_service.get_session(db, session_id)
    except copilot_service.CopilotError as error:
        raise _error(error) from error


@router.post("/sessions/{session_id}/build-context", response_model=CopilotContextResponse)
def build_context(session_id: UUID, db: Session = Depends(get_db)) -> CopilotContextResponse:
    try:
        return copilot_service.build_context(db, session_id)
    except copilot_service.CopilotError as error:
        raise _error(error) from error


@router.post("/sessions/{session_id}/generate-recommendations", response_model=list[CopilotRecommendationResponse])
def generate_recommendations(session_id: UUID, db: Session = Depends(get_db)) -> list[CopilotRecommendationResponse]:
    try:
        return copilot_service.generate_recommendations(db, session_id)
    except copilot_service.CopilotError as error:
        raise _error(error) from error


@router.post("/sessions/{session_id}/generate-action-plan", response_model=CopilotActionPlanResponse)
def generate_action_plan(session_id: UUID, db: Session = Depends(get_db)) -> CopilotActionPlanResponse:
    try:
        return copilot_service.generate_action_plan(db, session_id)
    except copilot_service.CopilotError as error:
        raise _error(error) from error


def _message(session_id: UUID, kind: str, db: Session) -> CopilotMessageResponse:
    try:
        return copilot_service.generate_message(db, session_id, kind)
    except copilot_service.CopilotError as error:
        raise _error(error) from error


@router.post("/sessions/{session_id}/generate-work-note", response_model=CopilotMessageResponse)
def generate_work_note(session_id: UUID, db: Session = Depends(get_db)) -> CopilotMessageResponse:
    return _message(session_id, "WORK_NOTE_DRAFT", db)


@router.post("/sessions/{session_id}/generate-customer-update", response_model=CopilotMessageResponse)
def generate_customer_update(session_id: UUID, db: Session = Depends(get_db)) -> CopilotMessageResponse:
    return _message(session_id, "CUSTOMER_UPDATE_DRAFT", db)


@router.post("/sessions/{session_id}/generate-investigation-checklist", response_model=CopilotMessageResponse)
def generate_investigation_checklist(session_id: UUID, db: Session = Depends(get_db)) -> CopilotMessageResponse:
    return _message(session_id, "INVESTIGATION_CHECKLIST", db)


@router.post("/recommendations/{recommendation_id}/accept", response_model=CopilotRecommendationResponse)
def accept_recommendation(recommendation_id: UUID, db: Session = Depends(get_db)) -> CopilotRecommendationResponse:
    try:
        return copilot_service.accept_recommendation(db, recommendation_id)
    except copilot_service.CopilotError as error:
        raise _error(error) from error


@router.post("/recommendations/{recommendation_id}/dismiss", response_model=CopilotRecommendationResponse)
def dismiss_recommendation(recommendation_id: UUID, db: Session = Depends(get_db)) -> CopilotRecommendationResponse:
    try:
        return copilot_service.dismiss_recommendation(db, recommendation_id)
    except copilot_service.CopilotError as error:
        raise _error(error) from error


@router.post("/sessions/{session_id}/close", response_model=CopilotSessionResponse)
def close_session(session_id: UUID, db: Session = Depends(get_db)) -> CopilotSessionResponse:
    try:
        return copilot_service.close_session(db, session_id)
    except copilot_service.CopilotError as error:
        raise _error(error) from error


@router.post("/analyze", response_model=CopilotSessionResponse)
def analyze(request: CopilotAnalyzeRequest, db: Session = Depends(get_db)) -> CopilotSessionResponse:
    try:
        return copilot_service.analyze(db, request)
    except copilot_service.CopilotError as error:
        raise _error(error) from error
