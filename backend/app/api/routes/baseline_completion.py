"""Read-only baseline completion, traceability, and handover APIs."""

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import baseline_completion_service as service

router = APIRouter(prefix="/api/v1/baseline-completion", tags=["baseline-completion"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.summary(db)


@router.get("/requirements")
def requirements() -> dict[str, Any]:
    return service.requirements()


@router.get("/walkthroughs")
def walkthroughs() -> dict[str, Any]:
    return service.walkthroughs()


@router.get("/demo-journeys")
def demo_journeys() -> dict[str, Any]:
    return service.demo_journeys()


@router.get("/reset-guide")
def reset_guide() -> dict[str, Any]:
    return service.reset_guide()


@router.get("/testing-guide")
def testing_guide() -> dict[str, Any]:
    return service.testing_guide()


@router.get("/model-guide")
def model_guide() -> dict[str, Any]:
    return service.model_guide()


@router.get("/stage-modes")
def stage_modes() -> dict[str, Any]:
    return service.stage_modes()


@router.get("/known-limitations")
def known_limitations() -> dict[str, Any]:
    return service.known_limitations()


@router.get("/signoff-checklist")
def signoff_checklist() -> dict[str, Any]:
    return service.signoff_checklist()


@router.get("/handover-pack")
def handover_pack(db: Session = Depends(get_db)) -> dict[str, Any]:
    return service.handover_pack(db)


@router.get("/handover-pack.md")
def handover_pack_markdown(db: Session = Depends(get_db)) -> Response:
    return Response(content=service.handover_markdown(db), media_type="text/markdown")
