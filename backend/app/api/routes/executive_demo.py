"""Read-only executive demo dashboard APIs."""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import executive_demo_service as service

router = APIRouter(prefix="/api/v1/executive-demo", tags=["executive-demo"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.summary(db)


@router.get("/value-metrics")
def value_metrics(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.value_metrics(db)


@router.get("/storyboard")
def storyboard(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.storyboard(db)


@router.get("/scenario-outcomes")
def scenario_outcomes(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return service.scenario_outcomes(db)


@router.get("/governance")
def governance(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.governance(db)


@router.get("/operating-model")
def operating_model(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.operating_model(db)


@router.get("/commercial-model")
def commercial_model(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.commercial_model(db)


@router.get("/deep-links")
def deep_links() -> dict[str, Any]:
    return service.deep_links()
