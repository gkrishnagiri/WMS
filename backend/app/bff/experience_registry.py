"""Local experience and BFF registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExperienceDefinition:
    code: str
    name: str
    description: str
    frontend_url: str
    backend_url: str
    allowed_origins: tuple[str, ...]
    otel_service_name: str


def _origins(port: int) -> tuple[str, ...]:
    return (f"http://localhost:{port}", f"http://127.0.0.1:{port}")


EXPERIENCE_DEFINITIONS: dict[str, ExperienceDefinition] = {
    "full": ExperienceDefinition("full", "Enterprise Operations Suite", "Full integrated EOS demo experience.", "http://localhost:4001", "http://localhost:8050", _origins(4001), "eos-full-backend"),
    "business": ExperienceDefinition("business", "EOS Business Application", "Business-facing warehouse and fulfillment application.", "http://localhost:4011", "http://localhost:8061", _origins(4011), "eos-business-bff"),
    "operations": ExperienceDefinition("operations", "EOS Operations Console", "AMS and support operations console.", "http://localhost:4012", "http://localhost:8062", _origins(4012), "eos-operations-bff"),
    "simulation": ExperienceDefinition("simulation", "EOS Simulation Lab", "Synthetic users and controlled fault-injection lab.", "http://localhost:4013", "http://localhost:8063", _origins(4013), "eos-simulation-bff"),
    "observability": ExperienceDefinition("observability", "EOS Observability Control Plane", "Runtime telemetry and local observability stack control plane.", "http://localhost:4014", "http://localhost:8064", _origins(4014), "eos-observability-bff"),
    "agentic": ExperienceDefinition("agentic", "EOS Agentic Support Console", "Copilot and governed AI support console.", "http://localhost:4015", "http://localhost:8065", _origins(4015), "eos-agentic-bff"),
}


def get_experience(code: str) -> ExperienceDefinition:
    return EXPERIENCE_DEFINITIONS[code]
