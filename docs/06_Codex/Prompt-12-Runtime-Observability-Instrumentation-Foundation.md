# Prompt 12 – Runtime Observability Instrumentation Foundation

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

**Enterprise Operations Suite (EOS)**

Prompt 01 created the enterprise application foundation.

Prompt 02 created the Warehouse & Fulfillment domain foundation.

Prompt 03 created warehouse transaction workflows.

Prompt 04 created operational exceptions and the AMS ticket foundation.

Prompt 05 created synthetic users and user-reported functional issues.

Prompt 06 created monitoring alert noise and manual triage without observability.

Prompt 07 created application-level observability evidence using simulated traces, spans, logs, metrics, and diagnostic cases.

Prompt 08 created batch jobs and batch failure scenarios.

Prompt 09 created the deterministic AI-native support engineer copilot foundation.

Prompt 10 created governed AI provider configuration and deterministic mock AI provider abstraction.

Prompt 11 connected the copilot to governed AI mock draft generation.

Your task now is to implement:

```text
Runtime Observability Instrumentation Foundation
```

This prompt moves EOS from only simulated observability evidence to **runtime application instrumentation**.

The system should now capture real runtime request telemetry from the FastAPI backend and store it in the existing observability tables.

---

## Important Clarification

This prompt does **not** introduce Tempo, Loki, Grafana dashboards, real OpenTelemetry export, or collector changes.

Do not modify:

```text
docker-compose.yml
observability/
Prometheus config
Grafana config
OpenTelemetry Collector config
```

The intended sequence is:

```text
Prompt 07 – Application-level simulated observability evidence
Prompt 12 – Runtime application instrumentation into EOS observability tables
Prompt 13 – Local observability stack expansion with external trace/log backends and dashboards
```

Prompt 12 should capture runtime telemetry inside EOS itself.

Prompt 13 can later export telemetry to external observability backends.

---

## Current Confirmed Baseline

The repository currently has:

- FastAPI backend
- React/Vite/MUI frontend
- PostgreSQL
- Redis
- Health and version endpoints
- Warehouse domain tables
- Warehouse transaction workflows
- Operational exceptions
- AMS tickets
- Synthetic users and user reports
- Monitoring alerts and triage
- Application-level observability evidence
- Diagnostic cases and evidence
- Batch jobs and batch failure support flows
- Copilot sessions and governed AI mock drafts
- AI config, mock provider, invocation logs, usage accounting, and guardrail events
- Backend running on port `8050`
- Frontend running on port `4001`

Recent committed capabilities include:

```text
feat: add EOS enterprise foundation
feat: add warehouse fulfillment domain foundation
feat: add warehouse transaction workflows
feat: add operational exceptions and AMS ticket foundation
feat: add synthetic users and user-reported issues
feat: add monitoring alert noise and triage foundation
feat: add observability-enabled support diagnosis
feat: add batch jobs and batch failure scenarios
feat: add ai-native support copilot foundation
feat: add governed ai provider configuration foundation
feat: add governed ai copilot draft integration
```

Use the current repository structure and coding patterns.

Do not redesign prior prompt output.

---

## Critical Instructions

You must not redesign the project.

You must not rename the application.

You must not change infrastructure.

You must not modify Docker Compose.

You must not modify observability configuration.

You must not introduce new major frameworks.

You must preserve backend port `8050`.

You must preserve frontend port `4001`.

You must preserve all existing APIs and frontend routes.

You must implement only the scope described in this prompt.

If something is unclear, leave a clear TODO comment instead of inventing architecture.

---

## Files and Paths You Must Not Modify

Do not modify:

```text
docker-compose.yml
observability/
data/
load-tests/
.git/
```

Do not modify local runtime files:

```text
backend/.env
backend/.venv/
frontend/.env
frontend/node_modules/
frontend/dist/
```

You may modify:

```text
backend/
frontend/
README.md
ARCHITECTURE.md
docs/06_Codex/
```

Prefer not to create a migration unless strictly needed.

Use the existing Prompt 07 observability tables where possible:

```text
obs_traces
obs_spans
obs_log_events
obs_metric_samples
obs_diagnostic_cases
obs_diagnostic_evidence
```

---

## Technology Constraints

Use only the technologies already selected.

### Backend

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic v2
- pydantic-settings
- psycopg
- redis-py
- pytest
- httpx

### Frontend

- React
- TypeScript
- Vite
- React Router
- TanStack Query
- Material UI

Do not add:

- OpenTelemetry SDK packages
- Tempo
- Loki
- Grafana dashboards
- new Docker services
- LangGraph
- LiteLLM
- OpenAI SDK
- Anthropic SDK
- vector databases
- embedding libraries
- RAG frameworks
- agent frameworks
- Celery
- Kafka
- Temporal
- ServiceNow connectors
- charting libraries

This prompt should use lightweight in-application instrumentation and persist telemetry into PostgreSQL.

---

# Objective

Implement runtime observability instrumentation for EOS.

EOS should now capture actual runtime evidence for backend API requests:

```text
HTTP request arrives
        ↓
Correlation/request ID is assigned
        ↓
Runtime trace is created
        ↓
Request span is recorded
        ↓
Structured log events are captured
        ↓
Metric samples are recorded
        ↓
Response carries correlation headers
        ↓
Support engineer can inspect runtime telemetry in the UI
```

The purpose is to show a realistic transition from:

```text
simulated observability evidence
```

to:

```text
actual application runtime observability evidence
```

without yet integrating an external observability backend.

---

# Architectural Intent

Prompt 07 created observability tables and simulated evidence.

Prompt 12 should start writing real runtime data to those tables.

The observability model should support:

```text
API request traces
request spans
runtime logs
latency metrics
error metrics
database probe spans
Redis probe spans
copilot / AI invocation request traces
batch simulation request traces
```

The runtime telemetry should help answer questions such as:

```text
Which API calls are slow?
Which requests failed?
Which route generated this error?
What is the correlation ID?
What logs and metrics were captured for this request?
What happened during a backend health probe?
```

Do not claim full distributed tracing yet.

Do not claim external observability platform integration yet.

---

# Scope

Implement:

1. Request and correlation ID handling
2. FastAPI runtime observability middleware
3. Runtime trace/span/log/metric creation
4. Runtime telemetry service
5. Runtime observability probe endpoint
6. Runtime observability read APIs
7. Frontend runtime observability pages
8. Frontend request correlation header support where practical
9. Backend tests
10. Documentation updates

Do not implement:

- real OpenTelemetry SDK/export
- Tempo
- Loki
- Grafana dashboards
- Prometheus scraping changes
- collector changes
- distributed tracing across multiple services
- browser-side telemetry collection
- AI diagnosis changes
- autonomous remediation
- ServiceNow integration

---

# Schema Guidance

Prefer no new migration.

Use the existing tables:

```text
obs_traces
obs_spans
obs_log_events
obs_metric_samples
```

Suggested mapping:

## Runtime request trace

Use `obs_traces`:

```text
trace_id              generated runtime trace id or incoming correlation id
trace_name            HTTP METHOD + route/path
trace_type            API_REQUEST
status                SUCCESS / ERROR / DEGRADED
source_module         RUNTIME_OBSERVABILITY
root_entity_type      API_REQUEST
root_entity_id        nullable
root_reference        METHOD path
started_at
ended_at
duration_ms
summary
```

## Runtime request span

Use `obs_spans`:

```text
span_id               generated span id
span_name             HTTP request
service_name          eos-backend
component_code        EOS-BACKEND-API
operation_type        HTTP_REQUEST
status                OK / ERROR / SLOW
duration_ms
error_type
error_message
attributes
```

Store useful request metadata in `attributes`, such as:

```json
{
  "method": "GET",
  "path": "/api/v1/batch/summary",
  "status_code": 200,
  "request_id": "...",
  "correlation_id": "...",
  "client_host": "127.0.0.1"
}
```

## Runtime logs

Use `obs_log_events`:

```text
level                 INFO / WARN / ERROR
event_type            REQUEST_STARTED / REQUEST_COMPLETED / REQUEST_FAILED
source_module         RUNTIME_OBSERVABILITY
component_code        EOS-BACKEND-API
message
trace_id
span_id
context
logged_at
```

## Runtime metric samples

Use `obs_metric_samples`:

```text
metric_name           api_latency_ms / api_request_count / api_error_count
metric_value
metric_unit           ms / count
component_code        EOS-BACKEND-API
severity              LOW / MEDIUM / HIGH / CRITICAL where applicable
trace_id
recorded_at
attributes
```

If the current model field names differ slightly, adapt to existing code style.

---

# Runtime Configuration

Add settings only if consistent with the existing configuration style.

Suggested settings:

```text
runtime_observability_enabled = true
runtime_observability_capture_requests = true
runtime_observability_capture_health = false
runtime_observability_slow_request_ms = 1000
runtime_observability_max_body_capture_chars = 0
```

Important:

- Do not capture request bodies by default.
- Do not capture secrets.
- Do not capture Authorization headers.
- Do not capture cookies.
- Do not capture environment variables.

Update `.env.example` if the project uses it.

Do not modify local `.env`.

---

# Backend Implementation

Suggested files:

```text
backend/app/core/correlation.py
backend/app/middleware/runtime_observability.py
backend/app/services/runtime_observability_service.py
backend/app/api/routes/runtime_observability.py
```

You may organize differently if consistent with existing project style.

Register the middleware in the backend application startup path.

Register the route under:

```text
/api/v1/runtime-observability
```

---

## Correlation ID Handling

For every non-excluded request:

1. Read incoming headers:

```text
X-Request-ID
X-Correlation-ID
traceparent
```

2. If missing, generate deterministic UUID-like identifiers.

3. Store on request state:

```text
request.state.request_id
request.state.correlation_id
request.state.runtime_trace_id
```

4. Add response headers:

```text
X-Request-ID
X-Correlation-ID
X-EOS-Runtime-Trace-ID
```

If `traceparent` exists, store it in span attributes, but do not implement full W3C tracing.

---

## Middleware Behavior

For each captured backend request:

1. Start timer.
2. Create runtime trace/span metadata.
3. Continue request.
4. On success:
   - record trace status `SUCCESS` or `DEGRADED` if slow.
   - record span status `OK` or `SLOW`.
   - record request started/completed logs.
   - record latency metric.
   - record request count metric.
5. On exception:
   - record trace status `ERROR`.
   - record span status `ERROR`.
   - record failed log.
   - record error count metric.
   - re-raise the exception.
6. Telemetry recording must not break the original request.
   - If telemetry insert fails, log to standard logging and continue.

Excluded paths:

```text
/docs
/redoc
/openapi.json
/favicon.ico
/static
```

Health endpoint may be excluded by default unless configuration says otherwise.

---

# Runtime Observability Service

Implement service functions such as:

```text
record_http_request_trace
record_runtime_log
record_runtime_metric
record_probe_trace
list_runtime_traces
get_runtime_trace_detail
runtime_summary
```

The service should use existing observability models.

Avoid duplicating code from Prompt 07 unless necessary.

If a generic observability service already exists, reuse it.

---

# Probe Endpoint

Add a runtime probe to create deterministic real backend telemetry.

Endpoint:

```text
POST /api/v1/runtime-observability/probes/backend-health
```

Behavior:

- create a trace named `Runtime backend health probe`
- create spans:
  - `Backend probe request`
  - `PostgreSQL connectivity check`
  - `Redis connectivity check`
- create logs:
  - probe started
  - database check result
  - Redis check result
  - probe completed
- create metrics:
  - `runtime_probe_duration_ms`
  - `db_probe_latency_ms`
  - `redis_probe_latency_ms`
- return probe status and trace id

The probe should not change business data.

If Redis or database check fails, the probe should return a clear degraded/error result and still record telemetry where possible.

---

# Runtime Observability APIs

Use prefix:

```text
/api/v1/runtime-observability
```

Add:

```text
GET  /api/v1/runtime-observability/summary
GET  /api/v1/runtime-observability/traces
GET  /api/v1/runtime-observability/traces/{trace_id}
GET  /api/v1/runtime-observability/logs
GET  /api/v1/runtime-observability/metrics
POST /api/v1/runtime-observability/probes/backend-health
```

---

## Runtime Summary

Endpoint:

```text
GET /api/v1/runtime-observability/summary
```

Return actual database-derived values:

```json
{
  "runtime_traces": 25,
  "successful_requests": 20,
  "degraded_requests": 3,
  "error_requests": 2,
  "average_latency_ms": 145.2,
  "max_latency_ms": 1220,
  "slow_request_threshold_ms": 1000,
  "runtime_logs": 80,
  "runtime_metric_samples": 75,
  "last_runtime_trace_at": "2026-08-23T06:50:00Z"
}
```

---

## Runtime Trace List

Endpoint:

```text
GET /api/v1/runtime-observability/traces
```

Support filters:

```text
status
method
path
correlation_id
request_id
```

Default:

```text
newest first
limit 100
```

Return:

```text
trace id
trace name
status
root reference
duration
started at
ended at
summary
```

---

## Runtime Trace Detail

Endpoint:

```text
GET /api/v1/runtime-observability/traces/{trace_id}
```

Return:

```text
trace header
spans
logs
metrics
correlation/request metadata
```

Path parameter may accept database UUID or trace_id string, whichever is consistent with existing observability code.

---

## Runtime Logs

Endpoint:

```text
GET /api/v1/runtime-observability/logs
```

Support filters:

```text
level
event_type
trace_id
correlation_id
```

Default:

```text
newest first
limit 200
```

---

## Runtime Metrics

Endpoint:

```text
GET /api/v1/runtime-observability/metrics
```

Support filters:

```text
metric_name
trace_id
component_code
severity
```

Default:

```text
newest first
limit 200
```

---

# Integration with Existing Observability APIs

Existing Prompt 07 observability APIs must continue to work.

Do not replace:

```text
/api/v1/observability/*
```

Runtime telemetry can appear in existing trace/log/metric lists, but Prompt 12 should also provide the dedicated runtime-observability APIs for easier demo validation.

---

# Frontend Implementation

Extend the existing EOS frontend.

Do not replace the application shell.

Do not change frontend port `4001`.

Do not change backend base URL away from `http://localhost:8050`.

---

## Navigation

Add sidebar entries:

```text
Runtime Observability
Runtime Traces
```

Keep existing entries:

```text
Dashboard
Warehouse
Inventory
Orders
Fulfillment Tasks
Shipments
Inventory Transactions
Operations
AMS Tickets
Synthetic Journeys
Journey Runs
User Reports
Monitoring
Monitoring Simulations
Monitoring Triage
Observability
Traces
Diagnostics
Batch Jobs
Batch Runs
Batch Simulations
Copilot
Copilot Sessions
AI Config
AI Invocations
AI Safety
Health
About
```

---

## Required Frontend Routes

Add:

```text
/observability/runtime
/observability/runtime/traces
/observability/runtime/traces/:traceId
```

Existing routes must continue working.

---

## Runtime Observability Overview Page

Route:

```text
/observability/runtime
```

Display:

- summary cards from `/api/v1/runtime-observability/summary`
- probe button: `Run Backend Health Probe`
- recent runtime traces table
- explanation:

```text
Runtime observability captures live EOS backend request traces, spans, logs, and metrics into the EOS observability tables. External observability backends are not enabled yet.
```

Cards:

```text
runtime traces
successful requests
degraded requests
error requests
average latency
max latency
runtime logs
runtime metric samples
```

---

## Runtime Traces Page

Route:

```text
/observability/runtime/traces
```

Display table:

```text
trace id
trace name
status
route/root reference
duration
started at
ended at
summary
```

Trace ID should link to detail page.

Use chips for status.

---

## Runtime Trace Detail Page

Route:

```text
/observability/runtime/traces/:traceId
```

Display:

- trace header
- correlation ID
- request ID
- duration
- status
- spans
- logs
- metric samples

Span table:

```text
span name
operation type
status
duration
error message
```

Log table:

```text
time
level
event type
message
```

Metric table:

```text
time
metric
value
unit
severity
```

---

# Frontend Request Correlation Support

Where practical, update the frontend API client layer to send:

```text
X-Request-ID
X-Correlation-ID
```

for API requests.

Rules:

- generate a new request ID per request
- keep a browser-session correlation ID in memory or local storage if simple
- do not include user secrets
- do not break existing API clients

If API clients are fragmented and this is too invasive, implement the backend header generation only and document frontend-wide header unification as deferred.

---

# Frontend API Client

Create or extend typed API client:

```text
frontend/src/services/runtimeObservabilityApi.ts
```

Add methods for:

```text
getRuntimeSummary
getRuntimeTraces
getRuntimeTraceDetail
getRuntimeLogs
getRuntimeMetrics
runBackendHealthProbe
```

Use `VITE_API_BASE_URL`.

Use TanStack Query for data loading.

Use mutations for probe execution.

Show loading and error states.

---

# Backend Tests

Add tests covering:

1. Existing health/version tests still pass
2. Existing warehouse tests still pass
3. Existing workflow tests still pass
4. Existing operations/AMS tests still pass
5. Existing synthetic user tests still pass
6. Existing monitoring tests still pass
7. Existing observability tests still pass
8. Existing batch tests still pass
9. Existing copilot tests still pass
10. Existing AI config tests still pass
11. Runtime middleware adds correlation headers
12. Runtime middleware records trace for captured API request
13. Runtime middleware records span for captured API request
14. Runtime middleware records logs for captured API request
15. Runtime middleware records metric samples for captured API request
16. Runtime summary endpoint works
17. Runtime trace list endpoint works
18. Runtime trace detail includes spans/logs/metrics
19. Runtime logs endpoint works
20. Runtime metrics endpoint works
21. Backend health probe creates trace/spans/logs/metrics
22. Excluded paths do not create excessive telemetry
23. Telemetry recording failure does not break request if feasible to test
24. No OpenTelemetry SDK dependency is required
25. No infrastructure files are modified

Tests should be runnable with:

```bash
cd backend
source .venv/bin/activate
pytest
```

When local PostgreSQL and Redis are running and database is migrated/seeded, tests should pass.

If integration prerequisites are missing, tests may skip clearly, but do not hide real application errors.

---

# Frontend Validation

Ensure:

```bash
cd frontend
npm run build
```

passes.

Do not add unnecessary frontend test complexity in this prompt.

---

# Documentation Updates

Update `README.md` with:

- Prompt 12 runtime observability instrumentation summary
- distinction from Prompt 07 simulated observability
- request/correlation ID behavior
- runtime traces
- runtime spans
- runtime logs
- runtime metrics
- runtime backend health probe
- new APIs
- new frontend routes
- validation commands
- backend port `8050`
- frontend port `4001`
- explicit deferred items:
  - OpenTelemetry SDK/export
  - Tempo
  - Loki
  - Grafana dashboards
  - collector trace/log pipeline
  - distributed tracing across services
  - browser telemetry
  - external observability SaaS integration

Update `ARCHITECTURE.md` with:

- runtime observability middleware
- in-application telemetry persistence into `obs_*` tables
- correlation/request ID handling
- runtime probe flow
- relationship to Prompt 07 simulated observability
- relationship to future Prompt 13 external observability stack
- current deferred items

If `docs/06_Codex/` exists, do not modify prior prompt files unless necessary.

---

# Validation Commands

Run or provide results for:

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed_warehouse
python -m app.db.seed_synthetic_users
python -m app.db.seed_monitoring
python -m app.db.seed_batch
python -m app.db.seed_copilot
python -m app.db.seed_ai_config
pytest
```

Then validate live backend:

```bash
curl -sS http://localhost:8050/health | jq .
curl -sS http://localhost:8050/api/v1/runtime-observability/summary | jq .
curl -sS http://localhost:8050/api/v1/runtime-observability/traces | jq .
curl -sS http://localhost:8050/api/v1/runtime-observability/logs | jq .
curl -sS http://localhost:8050/api/v1/runtime-observability/metrics | jq .
```

Run runtime probe:

```bash
curl -sS -X POST http://localhost:8050/api/v1/runtime-observability/probes/backend-health \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
```

Generate runtime request traces by calling existing APIs:

```bash
curl -sS http://localhost:8050/api/v1/batch/summary | jq .
curl -sS http://localhost:8050/api/v1/copilot/summary | jq .
curl -sS http://localhost:8050/api/v1/ai-config/summary | jq .
```

Confirm runtime telemetry was recorded:

```bash
curl -sS http://localhost:8050/api/v1/runtime-observability/summary | jq .
curl -sS http://localhost:8050/api/v1/runtime-observability/traces | jq .
```

Then validate frontend:

```bash
cd frontend
npm install
npm run build
./start_frontend.sh
```

Confirm UI pages are available at:

```text
http://localhost:4001/observability/runtime
http://localhost:4001/observability/runtime/traces
```

Manual UI validation:

```text
Open Runtime Observability overview
Run Backend Health Probe
Confirm summary updates
Open Runtime Traces
Open latest runtime trace detail
Confirm spans are visible
Confirm logs are visible
Confirm metric samples are visible
Call Batch Summary or AI Config Summary from UI
Return to Runtime Observability
Confirm new runtime traces appear
Confirm response headers include X-Request-ID, X-Correlation-ID, and X-EOS-Runtime-Trace-ID where practical
```

---

# Definition of Done

Prompt 12 is complete only when:

- runtime observability middleware exists
- request ID and correlation ID handling works
- response headers include request/correlation IDs
- captured API requests create `obs_traces`
- captured API requests create `obs_spans`
- captured API requests create `obs_log_events`
- captured API requests create `obs_metric_samples`
- runtime summary API works
- runtime trace list API works
- runtime trace detail API works
- runtime logs API works
- runtime metrics API works
- backend health probe works
- backend health probe creates trace/spans/logs/metrics
- existing Prompt 07 observability APIs still work
- existing warehouse APIs still work
- existing operations/AMS APIs still work
- existing synthetic user APIs still work
- existing monitoring APIs still work
- existing batch APIs still work
- existing copilot APIs still work
- existing AI config APIs still work
- frontend runtime observability overview works
- frontend runtime traces page works
- frontend runtime trace detail page works
- backend tests pass
- frontend build passes
- backend remains on port `8050`
- frontend remains on port `4001`
- README updated
- ARCHITECTURE.md updated
- no infrastructure files modified
- no OpenTelemetry SDK dependency introduced
- no external observability backend introduced

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Alembic migration name, or confirmation no migration was needed
4. Backend runtime observability APIs added
5. Middleware behavior summary
6. Frontend routes added
7. Backend validation results
8. Frontend validation results
9. Runtime probe validation result
10. Runtime request telemetry validation result
11. Confirmation that infrastructure files were not modified
12. Confirmation that no OpenTelemetry SDK or external observability backend was introduced
13. Any TODOs
14. Recommended Git commit message

Recommended commit message:

```text
feat: add runtime observability instrumentation foundation
```

Do not proceed beyond this prompt.