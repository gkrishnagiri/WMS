"""Safe observability extension points.

OpenTelemetry instrumentation is intentionally deferred until application
traces are introduced in a later phase. The hooks here keep startup/shutdown
integration stable without requiring an OpenTelemetry SDK dependency today.
"""

from __future__ import annotations

import logging

from app.core.config import Settings

logger = logging.getLogger(__name__)


def initialize_telemetry(settings: Settings) -> None:
    """Prepare future telemetry integrations without changing infrastructure."""
    # TODO: add application metrics/tracing exporters in the observability phase.
    logger.debug("Telemetry hooks initialized for %s", settings.app_name)


def shutdown_telemetry() -> None:
    """Placeholder for future telemetry provider shutdown."""
    # TODO: flush and close telemetry providers when instrumentation is added.
