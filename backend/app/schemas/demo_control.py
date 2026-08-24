"""Schemas for the read-only local demo control plane."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class DemoReadinessItem(BaseModel):
    name: str
    kind: str
    url: str
    expected_status: int | str
    actual_status: int | str | None = None
    healthy: bool
    message: str


class DemoReadinessResponse(BaseModel):
    overall_status: str
    checked_at: datetime
    items: list[DemoReadinessItem]
