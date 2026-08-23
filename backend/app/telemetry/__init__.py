"""Legacy application telemetry hooks.

Prompt 13's optional OpenTelemetry SDK setup lives in
``app.core.opentelemetry``; these hooks remain for the existing application
startup contract.
"""

from __future__ import annotations

import logging

from app.core.config import Settings

logger = logging.getLogger(__name__)


def initialize_telemetry(settings: Settings) -> None:
    """Keep the original telemetry startup hook stable."""
    logger.debug("Telemetry hooks initialized for %s", settings.app_name)


def shutdown_telemetry() -> None:
    """Keep the original telemetry shutdown hook stable."""
