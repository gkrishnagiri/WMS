"""Approval-gated Stage 2 agent action APIs."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent_actions import ActionApprovalRequest, ActionDryRunRequest, ActionExecutionRequest, ActionRejectionRequest
from app.services import agent_action_service as service

router = APIRouter(prefix="/api/v1/agent-actions", tags=["agent-actions"])


def _error(error: Exception) -> HTTPException:
    return HTTPException(status_code=getattr(error, "status_code", 409), detail=getattr(error, "message", str(error)))


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.summary(db)


@router.get("/catalog")
def catalog() -> list[dict[str, Any]]:
    return service.catalog()


@router.get("/proposals")
def proposals(case_id: UUID | None = Query(default=None), status: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return service.list_proposals(db, case_id=case_id, status=status)


@router.get("/proposals/{proposal_id}")
def proposal(proposal_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.get_proposal(db, proposal_id)
    except service.AgentActionError as error:
        raise _error(error) from error


@router.post("/proposals/{proposal_id}/approve")
def approve(proposal_id: str, request: ActionApprovalRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.approve_proposal(db, proposal_id, request)
    except service.AgentActionError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/proposals/{proposal_id}/reject")
def reject(proposal_id: str, request: ActionRejectionRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.reject_proposal(db, proposal_id, request)
    except service.AgentActionError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/proposals/{proposal_id}/dry-run")
def dry_run(proposal_id: str, request: ActionDryRunRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.dry_run_proposal(db, proposal_id, request.requested_by_role)
    except service.AgentActionError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/proposals/{proposal_id}/execute")
def execute(proposal_id: str, request: ActionExecutionRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.execute_proposal(db, proposal_id, request)
    except service.AgentActionError as error:
        db.rollback()
        raise _error(error) from error


@router.get("/executions")
def executions(case_id: UUID | None = Query(default=None), status: str | None = Query(default=None), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return service.list_executions(db, case_id=case_id, status=status)


@router.get("/executions/{execution_id}")
def execution(execution_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.get_execution(db, execution_id)
    except service.AgentActionError as error:
        raise _error(error) from error
