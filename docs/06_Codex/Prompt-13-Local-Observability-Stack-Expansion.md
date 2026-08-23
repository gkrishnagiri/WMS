# Prompt 13 – Local Observability Stack Expansion

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

**Enterprise Operations Suite (EOS)**

Prompt 12 created runtime observability instrumentation inside EOS and persisted runtime telemetry into the existing `obs_*` PostgreSQL observability tables.

Your task now is to implement:

```text
Local Observability Stack Expansion
```

This prompt introduces the local external observability stack for the first time:

```text
OpenTelemetry export
Tempo traces
Loki logs
Prometheus metrics
Grafana data sources and dashboards
```

This prompt may modify Docker Compose and observability configuration.

Do not implement AI agents, autonomous remediation, ServiceNow integration, external observability SaaS, or production-grade distributed tracing yet.

---

## Current Confirmed Baseline

The repository currently has:

- FastAPI backend
- React/Vite/MUI frontend
- PostgreSQL
- Redis
- OpenTelemetry Collector container
- Prometheus container
- Grafana container
- Runtime observability middleware
- Runtime traces/logs/metrics persisted to PostgreSQL `obs_*` tables
- Backend running on port `8050`
- Frontend running on port `4001`
- Prometheus on port `9090`
- Grafana on port `3001`
- OpenTelemetry Collector receiving OTLP on ports `4317` and `4318`

Recent committed capabilities include:

```text
feat: add governed ai copilot draft integration
feat: add runtime observability instrumentation foundation
```

The current stable infrastructure stack does **not** include Tempo or Loki yet.

This prompt now intentionally adds them.

---

## Critical Instructions

You must not redesign the project.

You must not rename the application.

You must preserve backend port `8050`.

You must preserve frontend port `4001`.

You must preserve PostgreSQL host port `15432`.

You must preserve Redis host port `6379`.

You must preserve Prometheus host port `9090`.

You must preserve Grafana host port `3001`.

You must preserve OpenTelemetry Collector host ports `4317` and `4318`.

You may modify:

```text
docker-compose.yml
observability/
backend/
frontend/
README.md
ARCHITECTURE.md
docs/06_Codex/
scripts/
```

Do not modify local runtime files:

```text
backend/.env
backend/.venv/
frontend/.env
frontend/node_modules/
frontend/dist/
```

Do not add ServiceNow integration.

Do not add external AI/LLM integration.

Do not add cloud observability integration.

Do not use sudo or install system-level services.

Everything must run through the existing project-local Docker Compose stack and Python/Node project dependencies.

---

# Objective

Expand EOS from internal runtime observability storage to a local observability stack:

```text
EOS backend
    ↓ OTLP traces/logs/metrics
OpenTelemetry Collector
    ↓ traces
Tempo
    ↓ logs
Loki
    ↓ metrics
Prometheus
    ↓ dashboards
Grafana
```

Prompt 12 must remain intact.

The system should support both:

```text
EOS internal observability tables
External local observability stack
```

Do not replace the Prompt 12 PostgreSQL runtime observability model.

Prompt 13 adds external export and visualization.

---

# Scope

Implement:

1. Tempo service
2. Loki service
3. OpenTelemetry Collector traces/logs/metrics pipelines
4. Grafana data sources for Prometheus, Loki, and Tempo
5. Grafana dashboard provisioning
6. Backend OpenTelemetry SDK instrumentation
7. Backend OTLP trace export
8. Backend OTLP log export if feasible
9. Backend OTLP metric export
10. Runtime correlation between EOS request IDs and OpenTelemetry trace IDs
11. Observability stack health APIs
12. Frontend observability stack pages
13. Tests and validation commands
14. Documentation updates

Do not implement:

- external observability SaaS
- cloud tracing
- ServiceNow
- AI diagnosis changes
- autonomous remediation
- production-grade sampling controls
- Kubernetes
- distributed multi-service tracing beyond EOS backend
- browser RUM telemetry

---

# Infrastructure Changes Now Allowed

Unlike Prompts 04–12, this prompt **may modify**:

```text
docker-compose.yml
observability/
```

Add only the minimum needed services/configuration.

Do not remove existing services.

Do not break the existing PostgreSQL, Redis, Prometheus, Grafana, or OpenTelemetry Collector stack.

---

# Docker Compose Requirements

Update `docker-compose.yml` to include:

```text
tempo
loki
```

Keep existing services:

```text
postgres
redis
otel-collector
prometheus
grafana
```

## Tempo

Add Tempo for local trace storage.

Expose Tempo HTTP/API port:

```text
3200:3200
```

Do not publish Tempo OTLP ports on the host if they conflict with the OpenTelemetry Collector.

The collector should export traces to Tempo over the Docker network.

Suggested internal endpoint:

```text
tempo:4317
```

## Loki

Add Loki for local log storage.

Expose Loki port:

```text
3100:3100
```

Suggested endpoint:

```text
http://loki:3100
```

## Grafana

Grafana should depend on:

```text
prometheus
tempo
loki
```

Keep Grafana host port:

```text
3001:3000
```

---

# Observability Configuration Files

Create or update files under:

```text
observability/
```

Suggested structure:

```text
observability/
  otel-collector-config.yaml
  prometheus.yml
  tempo/
    tempo.yaml
  loki/
    loki-config.yaml
  grafana/
    provisioning/
      datasources/
        datasources.yml
      dashboards/
        dashboards.yml
    dashboards/
      eos-runtime-observability.json
      eos-ams-support-overview.json
```

Use the current repository’s existing structure if different.

Do not create duplicate conflicting config paths.

---

# OpenTelemetry Collector Configuration

Update the collector config to support:

```text
traces
logs
metrics
```

Existing metrics pipeline must continue to work.

The collector should receive OTLP from EOS backend on:

```text
4317 gRPC
4318 HTTP
```

## Pipelines

Required pipelines:

```text
traces
logs
metrics
```

## Exporters

Required exporters:

```text
prometheus exporter for metrics
otlp exporter to Tempo for traces
Loki-compatible exporter for logs
debug exporter for local troubleshooting
```

If the selected collector image supports the Loki exporter directly, use it.

If Loki exporter syntax is not supported by the collector version, use a Loki-supported OTLP HTTP endpoint if available for the selected Loki configuration.

The implementation must validate the collector starts cleanly.

Do not leave a config that makes the collector crash.

---

# Prometheus Configuration

Update Prometheus only as needed.

It should continue scraping:

```text
otel-collector prometheus exporter
```

If the backend exposes an additional metrics endpoint, scrape it only if implemented safely.

Do not break existing Prometheus readiness.

---

# Grafana Provisioning

Provision data sources:

```text
Prometheus
Loki
Tempo
```

Prometheus URL inside Docker:

```text
http://prometheus:9090
```

Loki URL inside Docker:

```text
http://loki:3100
```

Tempo URL inside Docker:

```text
http://tempo:3200
```

Create dashboards that are useful for demos.

## Dashboard 1: EOS Runtime Observability

Panels should include where feasible:

```text
API request count
API latency
API error count
Recent runtime logs
Trace search/link panel
Collector pipeline status
```

## Dashboard 2: EOS AMS Support Overview

Panels should include where feasible:

```text
Support-related API traffic
Batch simulation API calls
Copilot API calls
AI config API calls
Error logs
Recent traces
```

Dashboards may use simple Prometheus/Loki/Tempo queries.

Do not over-engineer dashboards.

They must import cleanly into Grafana.

---

# Backend OpenTelemetry Instrumentation

Add Python OpenTelemetry dependencies to `backend/requirements.txt`.

Use only official OpenTelemetry Python packages.

Suggested categories:

```text
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp
opentelemetry-instrumentation-fastapi
opentelemetry-instrumentation-sqlalchemy
opentelemetry-instrumentation-redis
opentelemetry-instrumentation-logging
```

Use exact pinned versions if the project style requires pinned dependencies.

Do not add unrelated observability frameworks.

---

## Backend Configuration

Add settings using the existing configuration style.

Suggested settings:

```text
otel_enabled
otel_service_name
otel_service_namespace
otel_service_version
otel_environment
otel_exporter_otlp_endpoint
otel_exporter_otlp_protocol
otel_traces_enabled
otel_logs_enabled
otel_metrics_enabled
otel_sample_ratio
```

Suggested defaults:

```text
otel_enabled = false
otel_service_name = eos-backend
otel_service_namespace = enterprise-operations-suite
otel_environment = development
otel_exporter_otlp_endpoint = http://localhost:4317
otel_exporter_otlp_protocol = grpc
otel_traces_enabled = true
otel_logs_enabled = true
otel_metrics_enabled = true
otel_sample_ratio = 1.0
```

Important:

- Do not modify local `backend/.env`.
- Update `.env.example`.
- Backend must still run when `otel_enabled=false`.
- Backend must still run if collector is unavailable.
- Tests should not require the collector.

---

## Backend Instrumentation Module

Create a module such as:

```text
backend/app/core/opentelemetry.py
```

or:

```text
backend/app/observability/otel.py
```

It should initialize:

```text
TracerProvider
MeterProvider
LoggerProvider if feasible
OTLP exporters
FastAPI instrumentation
SQLAlchemy instrumentation
Redis instrumentation
logging correlation
```

Register instrumentation in the backend app startup path.

The instrumentation must be idempotent and safe under reload.

Avoid duplicate instrumentation warnings where possible.

---

## Request Correlation

Prompt 12 already adds:

```text
X-Request-ID
X-Correlation-ID
X-EOS-Runtime-Trace-ID
```

Prompt 13 should add OpenTelemetry correlation where feasible.

Add response header if practical:

```text
X-EOS-OTEL-Trace-ID
```

This should reflect the active OpenTelemetry trace ID if available.

Add request/correlation IDs as span attributes:

```text
eos.request_id
eos.correlation_id
http.route
http.method
```

Do not remove Prompt 12 headers.

---

# Metrics

Add OpenTelemetry metrics where feasible.

At minimum, record from the runtime observability middleware or a lightweight metrics helper:

```text
eos_api_request_count
eos_api_error_count
eos_api_latency_ms
```

Attributes:

```text
method
path or route
status_code
environment
```

Avoid high-cardinality values such as raw query strings.

Metrics should be exported through the collector to Prometheus.

Prompt 12 internal `obs_metric_samples` must continue to work.

---

# Logs

Where feasible, export backend logs through OTLP to the collector and Loki.

Logs should include:

```text
service.name
environment
trace_id
span_id
request_id
correlation_id
level
message
```

If full OTLP log export is difficult, implement a minimal structured logging bridge and document the limitation clearly.

Do not log secrets.

Do not log Authorization headers.

Do not log cookies.

Do not log request bodies by default.

---

# Traces

FastAPI requests should create traces visible in Tempo.

SQLAlchemy and Redis operations should create child spans where supported.

Add a test endpoint to generate a controlled trace.

---

# Observability Stack Backend APIs

Create routes under:

```text
/api/v1/observability-stack
```

Add:

```text
GET  /api/v1/observability-stack/summary
GET  /api/v1/observability-stack/health
GET  /api/v1/observability-stack/config
POST /api/v1/observability-stack/test-span
POST /api/v1/observability-stack/test-log
POST /api/v1/observability-stack/test-metric
POST /api/v1/observability-stack/test-all
```

## Summary

Return:

```json
{
  "otel_enabled": true,
  "service_name": "eos-backend",
  "collector_endpoint": "http://localhost:4317",
  "traces_enabled": true,
  "logs_enabled": true,
  "metrics_enabled": true,
  "tempo_url": "http://localhost:3200",
  "loki_url": "http://localhost:3100",
  "prometheus_url": "http://localhost:9090",
  "grafana_url": "http://localhost:3001"
}
```

## Health

Check reachable local endpoints where feasible:

```text
OpenTelemetry Collector health/readiness if configured
Prometheus readiness
Grafana health
Tempo readiness
Loki readiness
```

If some checks are not possible from backend, return `unknown` rather than failing the endpoint.

Do not make this endpoint dependent on external internet.

## Config

Return sanitized OpenTelemetry config.

Do not expose secrets.

## Test Span

Create a custom span:

```text
eos.observability_stack.test_span
```

Add attributes:

```text
test.type = span
component = eos-backend
```

Return active trace ID and span ID if available.

## Test Log

Emit a structured test log.

Return confirmation.

## Test Metric

Record a test counter or histogram sample.

Return confirmation.

## Test All

Run span, log, and metric test actions.

Return all generated metadata.

---

# Frontend Implementation

Extend the existing EOS frontend.

Do not change frontend port `4001`.

Add navigation entries:

```text
Observability Stack
Grafana Dashboards
```

Add frontend routes:

```text
/observability/stack
/observability/stack/health
/observability/stack/test
/observability/dashboards
```

## Observability Stack Overview

Route:

```text
/observability/stack
```

Show:

```text
OTel enabled
collector endpoint
traces/logs/metrics enabled
Tempo link
Loki link
Prometheus link
Grafana link
```

Explain:

```text
Prompt 13 adds local external observability backends. Prompt 12 internal PostgreSQL runtime observability remains active.
```

## Stack Health Page

Route:

```text
/observability/stack/health
```

Show health cards for:

```text
OpenTelemetry Collector
Prometheus
Grafana
Tempo
Loki
```

## Stack Test Page

Route:

```text
/observability/stack/test
```

Buttons:

```text
Generate Test Span
Generate Test Log
Generate Test Metric
Generate All
```

Display response metadata:

```text
trace id
span id
status
message
```

## Dashboards Page

Route:

```text
/observability/dashboards
```

Show links:

```text
Grafana Home
EOS Runtime Observability Dashboard
EOS AMS Support Overview Dashboard
Prometheus
Tempo
Loki
```

If direct dashboard URLs are not stable, link to Grafana home and explain the provisioned dashboard names.

---

# Startup Scripts

Update existing scripts only if needed:

```text
scripts/start.sh
scripts/stop.sh
```

They should continue to start/stop the full local stack.

Do not require sudo.

Do not require manually starting Tempo/Loki outside Docker Compose.

---

# Backend Tests

Add tests covering:

1. Existing tests still pass
2. Backend can start with `otel_enabled=false`
3. OpenTelemetry configuration endpoint returns sanitized config
4. Observability stack summary endpoint works
5. Observability stack health endpoint works with unavailable services returning `unknown` or `unhealthy`, not crashing
6. Test span endpoint works
7. Test log endpoint works
8. Test metric endpoint works
9. Test all endpoint works
10. Prompt 12 runtime observability headers still exist
11. Prompt 12 runtime trace persistence still works
12. No external internet dependency is required
13. No external AI/LLM dependency is introduced

Tests must not require Tempo/Loki/Collector to be running.

Use mocks or tolerate unavailable local services for health tests.

---

# Frontend Validation

Ensure:

```bash
cd frontend
npm run build
```

passes.

---

# Infrastructure Validation

Run:

```bash
cd ~/giri/AIProjects/WMS
docker compose config
./scripts/start.sh
docker compose ps
```

Validate services:

```bash
curl -sS http://localhost:9090/-/ready
curl -sS http://localhost:3001/api/health
curl -sS http://localhost:3200/ready
curl -sS http://localhost:3100/ready
```

If the OpenTelemetry Collector exposes a health endpoint, validate it too.

---

# Backend Live Validation

Start backend with OpenTelemetry enabled without editing local `.env`:

```bash
cd backend
source .venv/bin/activate

OTEL_ENABLED=true \
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 \
./start_backend.sh
```

If the settings prefix differs in the codebase, use the actual names implemented.

Validate:

```bash
curl -sS http://localhost:8050/health | jq .
curl -sS http://localhost:8050/api/v1/observability-stack/summary | jq .
curl -sS http://localhost:8050/api/v1/observability-stack/health | jq .
curl -sS -X POST http://localhost:8050/api/v1/observability-stack/test-all \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
curl -sS http://localhost:8050/api/v1/batch/summary | jq .
curl -sS http://localhost:8050/api/v1/runtime-observability/summary | jq .
```

---

# Grafana Validation

Open:

```text
http://localhost:3001
```

Confirm data sources exist:

```text
Prometheus
Loki
Tempo
```

Confirm dashboards exist:

```text
EOS Runtime Observability
EOS AMS Support Overview
```

Generate traffic:

```bash
curl -sS http://localhost:8050/api/v1/batch/summary | jq .
curl -sS http://localhost:8050/api/v1/copilot/summary | jq .
curl -sS http://localhost:8050/api/v1/ai-config/summary | jq .
curl -sS -X POST http://localhost:8050/api/v1/observability-stack/test-all \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
```

Then confirm in Grafana/Tempo/Loki/Prometheus where feasible:

```text
Tempo has EOS traces
Loki has EOS logs
Prometheus has EOS/collector metrics
Grafana dashboards load without import errors
```

If a specific panel is empty due to no traffic yet, document that and confirm the data source connection works.

---

# Documentation Updates

Update `README.md` with:

- Prompt 13 local observability stack summary
- Tempo
- Loki
- Prometheus
- Grafana
- OpenTelemetry Collector pipeline
- Backend OpenTelemetry enablement
- Relationship to Prompt 12 internal runtime observability
- How to start the stack
- How to start backend with OTel enabled
- Validation commands
- Troubleshooting tips

Update `ARCHITECTURE.md` with:

- Local observability stack architecture
- OTLP telemetry flow
- Collector pipelines
- Tempo/Loki/Prometheus/Grafana roles
- Backend instrumentation model
- Current limitations and deferred items

Explicitly document deferred items:

```text
production sampling policy
remote observability SaaS
browser RUM
multi-service distributed tracing
alert rules from Prometheus
Grafana alerting
ServiceNow integration
AI-driven remediation
```

---

# Definition of Done

Prompt 13 is complete only when:

- Docker Compose includes Tempo
- Docker Compose includes Loki
- Existing services still start
- OpenTelemetry Collector starts cleanly
- Collector has traces/logs/metrics pipelines
- Prometheus still works
- Grafana still works
- Grafana has Prometheus data source
- Grafana has Loki data source
- Grafana has Tempo data source
- Grafana dashboards are provisioned
- Backend has OpenTelemetry configuration
- Backend runs with OTel disabled
- Backend runs with OTel enabled
- Backend emits traces to collector
- Backend emits metrics to collector
- Backend emits logs to collector/Loki if implemented
- Test span endpoint works
- Test log endpoint works
- Test metric endpoint works
- Observability stack summary API works
- Observability stack health API works
- Prompt 12 internal runtime observability still works
- Existing warehouse APIs still work
- Existing operations/AMS APIs still work
- Existing synthetic user APIs still work
- Existing monitoring APIs still work
- Existing observability APIs still work
- Existing batch APIs still work
- Existing copilot APIs still work
- Existing AI config APIs still work
- Backend tests pass
- Frontend build passes
- Backend remains on port `8050`
- Frontend remains on port `4001`
- README updated
- ARCHITECTURE.md updated
- No external observability SaaS introduced
- No external LLM/agent framework introduced

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Docker Compose services added
4. OpenTelemetry Collector pipeline summary
5. Grafana data sources added
6. Grafana dashboards added
7. Backend OpenTelemetry instrumentation summary
8. Backend APIs added
9. Frontend routes added
10. Backend validation results
11. Frontend validation results
12. Docker Compose validation results
13. Tempo validation result
14. Loki validation result
15. Prometheus validation result
16. Grafana validation result
17. Runtime trace/log/metric export validation result
18. Confirmation Prompt 12 internal observability still works
19. Confirmation no external SaaS, LLM SDK, or agent framework was introduced
20. Any TODOs or limitations
21. Recommended Git commit message

Recommended commit message:

```text
feat: add local observability stack expansion
```

Do not proceed beyond this prompt.