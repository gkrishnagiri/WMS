"""Small experience-specific facade summaries over existing services."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import get_db
from app.models.ai_config import AiGuardrailEvent, AiInvocationLog, AiProvider
from app.models.ams import AmsTicket
from app.models.batch import BatchJob, BatchRun
from app.models.copilot import CopilotSafeAction, CopilotSession
from app.models.monitoring import MonAlert, MonAlertRule, MonTriageCase
from app.models.observability import ObsDiagnosticCase, ObsTrace
from app.models.operations import OpsException
from app.models.synthetic_users import SyntheticJourney, SyntheticJourneyRun
from app.services import observability_stack_service, runtime_observability_service, warehouse_service

business_router = APIRouter(prefix="/api/v1/business", tags=["business-facade"])
operations_router = APIRouter(prefix="/api/v1/operations-console", tags=["operations-facade"])
simulation_router = APIRouter(prefix="/api/v1/simulation-lab", tags=["simulation-facade"])
observability_router = APIRouter(prefix="/api/v1/observability-control", tags=["observability-facade"])
agentic_router = APIRouter(prefix="/api/v1/agentic-console", tags=["agentic-facade"])

facade_router = APIRouter()
facade_router.include_router(business_router)
facade_router.include_router(operations_router)
facade_router.include_router(simulation_router)
facade_router.include_router(observability_router)
facade_router.include_router(agentic_router)


def _dependency_health(request: Request, experience: str) -> dict[str, object]:
    database_healthy = request.app.state.database.check_connection()
    # Redis health is asynchronous and the facade is intentionally lightweight;
    # the dedicated /health endpoint remains the authoritative dependency check.
    return {
        "status": "healthy" if database_healthy else "degraded",
        "experience": experience,
        "database": "healthy" if database_healthy else "unhealthy",
        "redis": "available via /health",
    }


@business_router.get("/summary")
def business_summary(db: Session = Depends(get_db)) -> dict[str, object]:
    return {"experience": "business", "warehouse": warehouse_service.get_summary(db).model_dump(mode="json")}


@business_router.get("/health")
def business_health(request: Request) -> dict[str, object]:
    return _dependency_health(request, "business")


@operations_router.get("/summary")
def operations_summary(db: Session = Depends(get_db)) -> dict[str, object]:
    active_ticket_statuses = ("NEW", "ACKNOWLEDGED", "IN_PROGRESS", "RESOLVED")
    active_exception_statuses = ("OPEN", "ACKNOWLEDGED", "LINKED_TO_TICKET")
    active_alert_statuses = ("OPEN", "ACKNOWLEDGED", "LINKED_TO_TICKET")
    active_triage_statuses = ("OPEN", "INVESTIGATING", "LINKED_TO_TICKET")
    return {
        "experience": "operations",
        "open_ams_tickets": db.scalar(select(func.count(AmsTicket.id)).where(AmsTicket.status.in_(active_ticket_statuses))) or 0,
        "open_exceptions": db.scalar(select(func.count(OpsException.id)).where(OpsException.status.in_(active_exception_statuses))) or 0,
        "active_alerts": db.scalar(select(func.count(MonAlert.id)).where(MonAlert.status.in_(active_alert_statuses))) or 0,
        "open_triage_cases": db.scalar(select(func.count(MonTriageCase.id)).where(MonTriageCase.status.in_(active_triage_statuses))) or 0,
        "failed_batch_runs": db.scalar(select(func.count(BatchRun.id)).where(BatchRun.status.in_(("FAILED", "TIMEOUT", "PARTIAL_SUCCESS")))) or 0,
        "open_diagnostic_cases": db.scalar(select(func.count(ObsDiagnosticCase.id)).where(ObsDiagnosticCase.status.in_(("OPEN", "UNDER_REVIEW", "DIAGNOSED", "LINKED_TO_TICKET")))) or 0,
    }


@operations_router.get("/health")
def operations_health(request: Request) -> dict[str, object]:
    return _dependency_health(request, "operations")


@simulation_router.get("/summary")
def simulation_summary(db: Session = Depends(get_db)) -> dict[str, object]:
    return {
        "experience": "simulation",
        "synthetic_users": db.scalar(select(func.count(SyntheticJourneyRun.synthetic_user_id.distinct()))) or 0,
        "journeys": db.scalar(select(func.count(SyntheticJourney.id))) or 0,
        "journey_runs": db.scalar(select(func.count(SyntheticJourneyRun.id))) or 0,
        "batch_jobs": db.scalar(select(func.count(BatchJob.id)).where(BatchJob.enabled.is_(True))) or 0,
        "batch_runs": db.scalar(select(func.count(BatchRun.id))) or 0,
        "monitoring_rules": db.scalar(select(func.count(MonAlertRule.id)).where(MonAlertRule.enabled.is_(True))) or 0,
    }


@simulation_router.get("/health")
def simulation_health(request: Request) -> dict[str, object]:
    return _dependency_health(request, "simulation")


@observability_router.get("/summary")
def observability_summary(request: Request, db: Session = Depends(get_db)) -> dict[str, object]:
    settings: Settings = request.app.state.settings
    return {
        "experience": "observability",
        "runtime": runtime_observability_service.runtime_summary(db, settings.runtime_observability_slow_request_ms).model_dump(mode="json"),
        "observability": {"traces": db.scalar(select(func.count(ObsTrace.id))) or 0, "diagnostic_cases": db.scalar(select(func.count(ObsDiagnosticCase.id))) or 0},
        "stack": observability_stack_service.summary(request).model_dump(mode="json"),
    }


@observability_router.get("/health")
def observability_health(request: Request) -> dict[str, object]:
    return _dependency_health(request, "observability")


@agentic_router.get("/summary")
def agentic_summary(db: Session = Depends(get_db)) -> dict[str, object]:
    return {
        "experience": "agentic",
        "copilot_sessions": db.scalar(select(func.count(CopilotSession.id))) or 0,
        "safe_actions": db.scalar(select(func.count(CopilotSafeAction.id)).where(CopilotSafeAction.enabled.is_(True))) or 0,
        "ai_providers": db.scalar(select(func.count(AiProvider.id))) or 0,
        "ai_invocations": db.scalar(select(func.count(AiInvocationLog.id))) or 0,
        "guardrail_events": db.scalar(select(func.count(AiGuardrailEvent.id))) or 0,
    }


@agentic_router.get("/health")
def agentic_health(request: Request) -> dict[str, object]:
    return _dependency_health(request, "agentic")
