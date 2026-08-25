"""Presenter-controlled guided demo scenario APIs."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import demo_scenario_service as service

router = APIRouter(prefix="/api/v1/demo-scenarios", tags=["demo-scenarios"])


class ScenarioStartRequest(BaseModel):
    created_by_role: str = Field(default="DEMO_PRESENTER", min_length=1, max_length=80)


class ScenarioResetRequest(BaseModel):
    reset_reason: str = Field(default="Presenter reset the guided demo.", max_length=1500)


def _error(error: service.DemoScenarioError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail=error.message)


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.summary(db)
    except service.DemoScenarioError as error:
        raise _error(error) from error


@router.get("/catalog")
def catalog(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        return service.list_catalog(db)
    except service.DemoScenarioError as error:
        raise _error(error) from error


@router.get("/runs")
def runs(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return service.list_runs(db)


@router.get("/runs/{run_id}")
def run_detail(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service._run_dict(db, service.get_run(db, run_id))
    except service.DemoScenarioError as error:
        raise _error(error) from error


@router.post("/{scenario_code}/start")
def start(scenario_code: str, request: ScenarioStartRequest = ScenarioStartRequest(), db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.start(db, scenario_code, request.created_by_role)
    except service.DemoScenarioError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/runs/{run_id}/advance")
def advance(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.advance(db, run_id)
    except service.DemoScenarioError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/runs/{run_id}/steps/{step_code}/complete")
def complete_step(run_id: str, step_code: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.complete_step(db, run_id, step_code)
    except service.DemoScenarioError as error:
        db.rollback()
        raise _error(error) from error


@router.post("/runs/{run_id}/reset")
def reset(run_id: str, request: ScenarioResetRequest = ScenarioResetRequest(), db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        return service.reset(db, run_id, request.reset_reason)
    except service.DemoScenarioError as error:
        db.rollback()
        raise _error(error) from error


@router.get("/runs/{run_id}/timeline")
def run_timeline(run_id: str, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        return service.timeline(db, run_id)
    except service.DemoScenarioError as error:
        raise _error(error) from error


@router.get("/runs/{run_id}/artifacts")
def run_artifacts(run_id: str, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    try:
        return service.artifacts(db, run_id)
    except service.DemoScenarioError as error:
        db.rollback()
        raise _error(error) from error


@router.get("/runs/{run_id}/next-action")
def run_next_action(run_id: str, db: Session = Depends(get_db)) -> dict[str, Any] | None:
    try:
        return service.next_action(db, run_id)
    except service.DemoScenarioError as error:
        raise _error(error) from error
