"""Optional local OpenTelemetry SDK setup for EOS runtime telemetry.

The SDK is deliberately opt-in.  EOS continues to use the Prompt 12 database
telemetry path when OTel is disabled or when a local Collector is unavailable.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import Settings

logger = logging.getLogger(__name__)
_tracer = None
_meter = None
_providers: list[Any] = []
_otel_log_handler = None


def _resource(settings: Settings):
    from opentelemetry.sdk.resources import Resource

    return Resource.create(
        {
            "service.name": settings.otel_service_name,
            "service.namespace": settings.otel_service_namespace,
            "service.version": settings.otel_service_version,
            "deployment.environment.name": settings.otel_environment,
        }
    )


def initialize_opentelemetry(application: Any, settings: Settings) -> None:
    """Initialize SDK providers without making app startup depend on OTel."""
    global _tracer, _meter
    application.state.otel_enabled = bool(settings.otel_enabled)
    application.state.otel_available = False
    application.state.otel_initialization_error = None
    if not settings.otel_enabled:
        return
    if _tracer is not None:
        application.state.otel_available = True
        return

    try:
        from opentelemetry import metrics, trace
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = _resource(settings)
        tracer_provider = TracerProvider(resource=resource)
        if settings.otel_traces_enabled:
            tracer_provider.add_span_processor(
                BatchSpanProcessor(
                    OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True),
                    max_queue_size=512,
                    schedule_delay_millis=2000,
                )
            )
        trace.set_tracer_provider(tracer_provider)
        _providers.append(tracer_provider)
        _tracer = trace.get_tracer(settings.otel_service_name, settings.otel_service_version)

        if settings.otel_metrics_enabled:
            metric_exporter = OTLPMetricExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
            meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[PeriodicExportingMetricReader(metric_exporter, export_interval_millis=5000)],
            )
            metrics.set_meter_provider(meter_provider)
            _providers.append(meter_provider)
            _meter = metrics.get_meter(settings.otel_service_name, settings.otel_service_version)

        if settings.otel_logs_enabled:
            _initialize_logging(resource, settings.otel_exporter_otlp_endpoint)
        application.state.otel_available = True
    except Exception as error:  # pragma: no cover - depends on optional runtime packages
        application.state.otel_initialization_error = str(error)
        logger.exception("OpenTelemetry initialization failed; EOS will continue without external export.")


def _initialize_logging(resource: Any, endpoint: str) -> None:
    global _otel_log_handler
    try:
        from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
        from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
        from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
    except ImportError:
        logger.warning("OTLP log export is unavailable in the installed OpenTelemetry packages.")
        return

    provider = LoggerProvider(resource=resource)
    provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint, insecure=True)))
    _otel_log_handler = LoggingHandler(level=logging.NOTSET, logger_provider=provider)
    logging.getLogger().addHandler(_otel_log_handler)
    _providers.append(provider)


def shutdown_opentelemetry() -> None:
    global _otel_log_handler
    if _otel_log_handler is not None:
        logging.getLogger().removeHandler(_otel_log_handler)
        _otel_log_handler = None
    for provider in reversed(_providers):
        try:
            provider.shutdown()
        except Exception:
            logger.exception("OpenTelemetry provider shutdown failed.")
    _providers.clear()


def is_enabled(application: Any) -> bool:
    return bool(getattr(application.state, "otel_enabled", False) and _tracer is not None)


def is_available() -> bool:
    return _tracer is not None


def current_ids() -> tuple[str | None, str | None]:
    try:
        from opentelemetry import trace

        context = trace.get_current_span().get_span_context()
        if not context or not context.is_valid:
            return None, None
        return f"{context.trace_id:032x}", f"{context.span_id:016x}"
    except Exception:
        return None, None


def start_span(name: str, **attributes: Any):
    if _tracer is None:
        from contextlib import nullcontext

        return nullcontext(None)
    return _tracer.start_as_current_span(name, attributes=attributes)


def record_request_metrics(*, method: str, path: str, status_code: int, duration_ms: int, environment: str) -> None:
    if _meter is None:
        return
    attrs = {"http_method": method, "http_route": path, "http_status_code": str(status_code), "environment": environment}
    try:
        _meter.create_counter("eos_api_request_count", unit="{request}").add(1, attrs)
        _meter.create_histogram("eos_api_latency_ms", unit="ms").record(duration_ms, attrs)
        if status_code >= 400:
            _meter.create_counter("eos_api_error_count", unit="{error}").add(1, attrs)
    except Exception:
        logger.exception("OpenTelemetry metric recording failed.")


def test_span() -> dict[str, str | None]:
    with start_span("eos.observability_stack.test_span", **{"test.type": "span", "component": "eos-backend"}):
        trace_id, span_id = current_ids()
    return {"trace_id": trace_id, "span_id": span_id}


def test_log() -> dict[str, str | None]:
    trace_id, span_id = current_ids()
    logging.getLogger("eos.otel.test").info(
        "EOS OpenTelemetry test log",
        extra={"test_type": "log", "trace_id": trace_id, "span_id": span_id},
    )
    return {"trace_id": trace_id, "span_id": span_id}


def test_metric() -> dict[str, str]:
    if _meter is None:
        return {"metric_name": "eos_test_metric", "status": "SKIPPED"}
    _meter.create_counter("eos_test_metric", unit="{test}").add(1, {"component": "eos-backend"})
    return {"metric_name": "eos_test_metric", "status": "RECORDED"}
