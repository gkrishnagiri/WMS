"""User-reported functional issue creation and lifecycle services."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app.models.ams import AmsTicket
from app.models.synthetic_users import SyntheticJourney, SyntheticJourneyRun, SyntheticUser
from app.models.user_reports import AmsUserReport
from app.schemas.user_reports import ReportTicketSummary, UserReportResponse
from app.services import ams_ticket_service

VALID_CHANNELS = ("SYNTHETIC_USER", "USER_PORTAL", "MANUAL", "PHONE", "EMAIL")
VALID_SEVERITIES = ("LOW", "MEDIUM", "HIGH", "CRITICAL")


class UserReportError(Exception):
    def __init__(self, message: str, status_code: int = 409) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _next_report_number(db: Session) -> str:
    from sqlalchemy import func

    prefix = f"USR-RPT-{_now():%Y%m%d}-"
    current = db.scalar(select(func.max(AmsUserReport.report_number)).where(AmsUserReport.report_number.like(f"{prefix}%")))
    sequence = 1
    if current:
        try:
            sequence = int(str(current).rsplit("-", 1)[1]) + 1
        except (IndexError, ValueError):
            sequence = 1
    return f"{prefix}{sequence:04d}"


def _response(db: Session, report: AmsUserReport) -> UserReportResponse:
    ticket = db.get(AmsTicket, report.ticket_id) if report.ticket_id else None
    run = db.get(SyntheticJourneyRun, report.journey_run_id) if report.journey_run_id else None
    journey = db.get(SyntheticJourney, run.journey_id) if run else None
    return UserReportResponse(
        id=report.id, report_number=report.report_number, reporter_user_id=report.reporter_user_id,
        reporter_name=report.reporter_name, reporter_email=report.reporter_email, reporter_persona=report.reporter_persona,
        report_channel=report.report_channel, source_module=report.source_module, affected_entity_type=report.affected_entity_type,
        affected_entity_id=report.affected_entity_id, title=report.title, description=report.description,
        business_impact=report.business_impact, severity=report.severity, status=report.status,
        journey_run_id=report.journey_run_id, journey_run_number=run.run_number if run else None,
        journey_code=journey.journey_code if journey else None, ticket_id=report.ticket_id,
        ticket=ReportTicketSummary(id=ticket.id, ticket_number=ticket.ticket_number, status=ticket.status, priority=ticket.priority) if ticket else None,
        submitted_at=report.submitted_at, acknowledged_at=report.acknowledged_at, resolved_at=report.resolved_at,
        created_at=report.created_at, updated_at=report.updated_at,
    )


def get_report(db: Session, report_id: UUID) -> UserReportResponse:
    report = db.get(AmsUserReport, report_id)
    if report is None:
        raise UserReportError("User report not found.", 404)
    return _response(db, report)


def list_reports(db: Session, status: str | None = None, severity: str | None = None) -> list[UserReportResponse]:
    open_first = case((AmsUserReport.status.in_(("SUBMITTED", "TICKET_CREATED", "ACKNOWLEDGED")), 0), else_=1)
    statement = select(AmsUserReport).order_by(open_first, AmsUserReport.submitted_at.desc(), AmsUserReport.report_number.desc())
    if status:
        statement = statement.where(AmsUserReport.status == status.upper())
    if severity:
        statement = statement.where(AmsUserReport.severity == severity.upper())
    return [_response(db, report) for report in db.scalars(statement).all()]


def create_report(db: Session, request: Any) -> UserReportResponse:
    channel = request.report_channel.upper()
    severity = request.severity.upper()
    if channel not in VALID_CHANNELS:
        raise UserReportError("Unsupported user report channel.", 400)
    if severity not in VALID_SEVERITIES:
        raise UserReportError("Unsupported user report severity.", 400)
    reporter = db.get(SyntheticUser, request.reporter_user_id) if request.reporter_user_id else None
    if request.reporter_user_id and reporter is None:
        raise UserReportError("Synthetic reporter user not found.", 404)
    run = db.get(SyntheticJourneyRun, request.journey_run_id) if request.journey_run_id else None
    if request.journey_run_id and run is None:
        raise UserReportError("Journey run not found.", 404)
    now = _now()
    report = AmsUserReport(
        report_number=_next_report_number(db), reporter_user_id=request.reporter_user_id,
        reporter_name=request.reporter_name.strip(), reporter_email=request.reporter_email.strip() if request.reporter_email else None,
        reporter_persona=request.reporter_persona.upper() if request.reporter_persona else (reporter.persona if reporter else None),
        report_channel=channel, source_module=request.source_module.upper(), affected_entity_type=request.affected_entity_type.upper(),
        affected_entity_id=request.affected_entity_id, title=request.title.strip(), description=request.description.strip(),
        business_impact=request.business_impact.strip(), severity=severity, status="SUBMITTED", journey_run_id=request.journey_run_id,
        submitted_at=now, created_at=now, updated_at=now,
    )
    db.add(report)
    db.flush()
    if request.create_ticket:
        ams_ticket_service.create_ticket_from_user_report(db, report.id)
    else:
        db.commit()
    return get_report(db, report.id)


def create_ticket(db: Session, report_id: UUID) -> UserReportResponse:
    try:
        ams_ticket_service.create_ticket_from_user_report(db, report_id)
    except ams_ticket_service.AmsError as error:
        raise UserReportError(error.message, error.status_code) from error
    return get_report(db, report_id)


def acknowledge_report(db: Session, report_id: UUID) -> UserReportResponse:
    report = db.get(AmsUserReport, report_id)
    if report is None:
        raise UserReportError("User report not found.", 404)
    if report.status not in ("SUBMITTED", "TICKET_CREATED"):
        raise UserReportError(f"User report cannot transition from {report.status} to ACKNOWLEDGED.")
    report.status = "ACKNOWLEDGED"
    report.acknowledged_at = _now()
    report.updated_at = _now()
    db.commit()
    return get_report(db, report.id)


def resolve_report(db: Session, report_id: UUID) -> UserReportResponse:
    report = db.get(AmsUserReport, report_id)
    if report is None:
        raise UserReportError("User report not found.", 404)
    if report.status not in ("SUBMITTED", "TICKET_CREATED", "ACKNOWLEDGED"):
        raise UserReportError(f"User report cannot transition from {report.status} to RESOLVED.")
    report.status = "RESOLVED"
    report.resolved_at = _now()
    report.updated_at = _now()
    db.commit()
    return get_report(db, report.id)

