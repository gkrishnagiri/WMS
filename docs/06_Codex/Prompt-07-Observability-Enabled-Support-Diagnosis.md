# Prompt 07 – Observability-Enabled Support Diagnosis

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

**Enterprise Operations Suite (EOS)**

Prompt 01 created the enterprise application foundation.

Prompt 02 created the Warehouse & Fulfillment domain foundation.

Prompt 03 created warehouse transaction workflows.

Prompt 04 created operational exceptions and the AMS ticket foundation.

Prompt 05 created synthetic users, synthetic journeys, and user-reported issues.

Prompt 06 created monitoring alert noise and manual triage without observability.

Your task now is to implement the next support scenario:

```text
Observability-Enabled Support Diagnosis
```

This prompt represents the scenario where monitoring alerts exist, but support engineers also have correlated observability evidence such as:

```text
request/workflow traces
span timelines
structured logs
metric samples
business transaction context
diagnostic evidence
```

This prompt must remain deterministic.

Do not implement GenAI, LLMs, agents, autonomous remediation, ServiceNow integration, or real external observability platform integration yet.

---

## Important Clarification

Do **not** modify Docker Compose, Prometheus, Grafana, OpenTelemetry Collector, or any observability infrastructure files.

For this prompt, implement an **application-level observability evidence model** inside EOS.

This means:

```text
EOS stores deterministic simulated traces, spans, logs, and metric samples in PostgreSQL.
EOS correlates these observability records with alerts, tickets, triage cases, orders, tasks, shipments, and workflow runs.
```

Real OpenTelemetry export, Tempo, Loki, Prometheus scraping, and Grafana dashboards remain deferred.

This prompt creates the data and UI foundation that will later allow real observability integration.

---

## Current Confirmed Baseline

The repository currently has:

- FastAPI backend
- React/Vite/MUI frontend
- PostgreSQL
- Redis
- Health and version endpoints
- Warehouse domain tables
- Warehouse seed data
- Warehouse read APIs
- Warehouse transaction workflows
- Inventory transaction ledger
- Order event history
- Operational exceptions
- AMS ticket foundation
- AMS ticket lifecycle
- Synthetic users
- Synthetic journeys
- User-reported issues
- Monitoring components
- Monitoring rules
- Monitoring alert noise simulations
- Monitoring triage cases
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

You may create a new Alembic migration.

You may update `.gitignore` only if needed to exclude local runtime artifacts.

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

- charting libraries
- workflow engines
- Celery
- Dramatiq
- Kafka
- Temporal
- LangGraph
- LLM SDKs
- agent frameworks
- ServiceNow connectors
- real Prometheus integration
- real OpenTelemetry export
- real Loki integration
- real Tempo integration

Use Material UI cards, tables, chips, timelines if already available, and layout components.

---

# Objective

Implement deterministic observability-enabled support diagnosis.

Prompt 06 showed this scenario:

```text
Many monitoring alerts
        ↓
No observability
        ↓
Manual triage with low confidence
```

Prompt 07 should now show:

```text
Monitoring alert or triage case
        ↓
Correlated trace/log/metric evidence
        ↓
Support engineer sees probable failure path
        ↓
Diagnostic case is created
        ↓
Evidence-backed support diagnosis is recorded
        ↓
AMS ticket can be linked or created
```

This prompt specifically addresses:

```text
C. Monitoring and observability are both enabled.
   Root cause investigation becomes easier because alerts can be correlated with traces, logs, metrics, and business context.
```

Do not claim AI-driven root cause analysis.

Use deterministic, rule-based diagnostic evidence.

---

# Architectural Intent

Prompt 06 created noisy alerts.

Prompt 07 adds observability context.

The intended contrast is:

## Without observability

```text
API latency alert
DB latency alert
workflow failure alert
frontend error alert
        ↓
support engineer manually guesses relationship
```

## With observability

```text
API latency alert
        ↓
trace id shows slow allocation request
        ↓
span shows database query delay
        ↓
logs show inventory lookup timeout
        ↓
metric samples show DB latency spike
        ↓
diagnostic evidence points to probable DB degradation
```

The system may present:

```text
probable cause
confidence
evidence
recommended next checks
```

But it must not claim autonomous certainty.

---

# Scope

Implement:

1. Observability trace model
2. Span timeline model
3. Structured log event model
4. Metric sample model
5. Diagnostic case model
6. Diagnostic evidence model
7. Deterministic observability simulations
8. Correlation between alerts, triage cases, tickets, and observability evidence
9. Support diagnosis APIs
10. Frontend observability pages
11. Backend tests
12. Documentation updates

Do not implement:

- real distributed tracing export
- real log ingestion
- real metric scraping
- real Grafana dashboards
- real Prometheus scraping
- AI/LLM root cause summaries
- autonomous remediation
- batch jobs
- ServiceNow integration

---

# Database Additions

Create a new Alembic migration.

Add the following tables:

```text
obs_traces
obs_spans
obs_log_events
obs_metric_samples
obs_diagnostic_cases
obs_diagnostic_evidence
```

Use UUID primary keys consistent with the existing project style.

Use timestamp conventions consistent with the existing project.

---

## Table: `obs_traces`

Purpose:

Represent an end-to-end request, workflow, or business transaction trace.

Fields:

```text
id
trace_id
trace_name
trace_type
status
source_module
root_entity_type
root_entity_id
root_reference
linked_alert_id
linked_triage_case_id
linked_ticket_id
started_at
ended_at
duration_ms
summary
created_at
updated_at
```

Rules:

- `trace_id` must be unique
- `linked_alert_id` nullable, references `mon_alerts.id`
- `linked_triage_case_id` nullable, references `mon_triage_cases.id`
- `linked_ticket_id` nullable, references `ams_tickets.id`
- `root_entity_type` examples:
  - ORDER
  - TASK
  - SHIPMENT
  - INVENTORY
  - API_REQUEST
  - SYNTHETIC_JOURNEY
- `root_entity_id` may be nullable
- `root_reference` should be human-readable if available

Suggested trace types:

```text
API_REQUEST
WAREHOUSE_WORKFLOW
SYNTHETIC_JOURNEY
SUPPORT_DIAGNOSIS
MONITORING_SCENARIO
```

Suggested statuses:

```text
SUCCESS
ERROR
DEGRADED
TIMEOUT
PARTIAL
```

---

## Table: `obs_spans`

Purpose:

Represent operations inside a trace.

Fields:

```text
id
trace_id
span_id
parent_span_id
span_name
service_name
component_code
operation_type
status
started_at
ended_at
duration_ms
error_type
error_message
attributes
created_at
updated_at
```

Rules:

- `trace_id` references `obs_traces.id`
- `span_id` should be unique within a trace
- `parent_span_id` nullable
- `attributes` should be JSON/JSONB if supported

Suggested operation types:

```text
HTTP_REQUEST
SERVICE_METHOD
DATABASE_QUERY
CACHE_OPERATION
WORKFLOW_STEP
EXTERNAL_CALL
VALIDATION
```

Suggested statuses:

```text
OK
ERROR
SLOW
TIMEOUT
SKIPPED
```

---

## Table: `obs_log_events`

Purpose:

Represent structured logs correlated with traces, spans, entities, alerts, and tickets.

Fields:

```text
id
log_number
trace_id
span_id
level
logger_name
message
event_type
source_module
component_code
entity_type
entity_id
linked_alert_id
linked_ticket_id
context
logged_at
created_at
```

Rules:

- `log_number` must be unique
- `trace_id` nullable, references `obs_traces.id`
- `span_id` nullable, references `obs_spans.id`
- `linked_alert_id` nullable, references `mon_alerts.id`
- `linked_ticket_id` nullable, references `ams_tickets.id`
- `context` should be JSON/JSONB if supported

Suggested levels:

```text
DEBUG
INFO
WARN
ERROR
CRITICAL
```

Suggested event types:

```text
REQUEST_STARTED
REQUEST_COMPLETED
WORKFLOW_STEP_STARTED
WORKFLOW_STEP_FAILED
DB_QUERY_SLOW
CACHE_FAILURE
VALIDATION_FAILED
EXTERNAL_CALL_FAILED
BUSINESS_RULE_BLOCKED
```

---

## Table: `obs_metric_samples`

Purpose:

Represent deterministic point-in-time metric samples related to a component, trace, alert, or scenario.

Fields:

```text
id
sample_number
metric_name
metric_value
metric_unit
component_code
severity
trace_id
linked_alert_id
recorded_at
attributes
created_at
```

Rules:

- `sample_number` must be unique
- `trace_id` nullable, references `obs_traces.id`
- `linked_alert_id` nullable, references `mon_alerts.id`
- `attributes` should be JSON/JSONB if supported

Suggested metric names:

```text
api_latency_ms
db_latency_ms
redis_connection_failures
workflow_failure_count
allocation_failure_count
shipment_exception_count
frontend_api_failure_count
```

Suggested units:

```text
ms
count
percent
boolean
```

---

## Table: `obs_diagnostic_cases`

Purpose:

Represent a support diagnosis case created from alerts, triage cases, tickets, or direct observability simulation.

This is not an AI diagnosis.

It is deterministic evidence-backed support analysis.

Fields:

```text
id
diagnostic_number
title
description
status
severity
source_type
source_id
linked_alert_id
linked_triage_case_id
linked_ticket_id
primary_trace_id
probable_cause
confidence_level
recommended_next_steps
diagnosis_summary
created_by
created_at
updated_at
resolved_at
```

Rules:

- `diagnostic_number` must be unique
- `linked_alert_id` nullable, references `mon_alerts.id`
- `linked_triage_case_id` nullable, references `mon_triage_cases.id`
- `linked_ticket_id` nullable, references `ams_tickets.id`
- `primary_trace_id` nullable, references `obs_traces.id`
- `probable_cause` must be deterministic and evidence-based
- `confidence_level` should not default to high unless evidence supports it

Suggested statuses:

```text
OPEN
UNDER_REVIEW
DIAGNOSED
LINKED_TO_TICKET
RESOLVED
CLOSED
```

Suggested source types:

```text
ALERT
TRIAGE_CASE
AMS_TICKET
SIMULATION
MANUAL
```

Suggested confidence levels:

```text
LOW
MEDIUM
HIGH
UNKNOWN
```

---

## Table: `obs_diagnostic_evidence`

Purpose:

Represent individual evidence records supporting a diagnostic case.

Fields:

```text
id
diagnostic_case_id
evidence_type
source_table
source_id
title
details
weight
created_at
```

Rules:

- `diagnostic_case_id` references `obs_diagnostic_cases.id`
- `weight` may be integer or decimal
- evidence should be clear enough for UI display

Suggested evidence types:

```text
TRACE
SPAN
LOG
METRIC
ALERT
TRIAGE_CASE
TICKET
BUSINESS_ENTITY
```

---

# Observability Service

Create service modules such as:

```text
backend/app/services/observability_service.py
backend/app/services/diagnostic_service.py
```

You may organize differently if consistent with existing project style.

The services should support:

```text
create_trace
create_span
create_log_event
create_metric_sample
create_diagnostic_case
add_diagnostic_evidence
correlate_alert_to_observability
correlate_triage_case_to_observability
correlate_ticket_to_observability
```

Do not duplicate database session handling.

Reuse existing patterns.

---

# Deterministic Observability Simulations

Use prefix:

```text
/api/v1/observability/simulations
```

Implement:

```text
POST /api/v1/observability/simulations/database-degradation
POST /api/v1/observability/simulations/redis-cache-failure
POST /api/v1/observability/simulations/allocation-failure
POST /api/v1/observability/simulations/shipment-integration-failure
POST /api/v1/observability/simulations/observability-demo-suite
```

Each simulation should generate:

```text
monitoring alert(s), if appropriate
trace
spans
log events
metric samples
diagnostic case
diagnostic evidence
optional AMS ticket linkage
```

Use existing monitoring and AMS services where safe.

---

## Simulation 1: Database Degradation

Endpoint:

```text
POST /api/v1/observability/simulations/database-degradation
```

Behavior:

Generate or reuse monitoring alerts similar to Prompt 06:

```text
EOS-POSTGRES db_latency_ms HIGH
EOS-BACKEND-API api_latency_ms HIGH
WF-INVENTORY-SERVICE allocation_failure_count HIGH
```

Create observability evidence:

Trace:

```text
Warehouse order allocation degraded by database latency
```

Spans:

```text
HTTP POST /api/v1/warehouse/orders/{id}/allocate
WarehouseWorkflowService.allocate_order
InventoryBalanceRepository.find_available_stock
PostgreSQL SELECT wf_inventory_balances
```

Logs:

```text
DB_QUERY_SLOW
WORKFLOW_STEP_FAILED
```

Metrics:

```text
db_latency_ms = 2450
api_latency_ms = 3200
allocation_failure_count = 3
```

Diagnostic case:

```text
Probable cause: Database latency affecting inventory allocation queries
Confidence: HIGH
Recommended next steps:
- Review PostgreSQL response time
- Check inventory balance query performance
- Check concurrent allocation load
```

Do not actually degrade PostgreSQL.

This is deterministic simulation data.

---

## Simulation 2: Redis Cache Failure

Endpoint:

```text
POST /api/v1/observability/simulations/redis-cache-failure
```

Behavior:

Generate alert evidence:

```text
EOS-REDIS redis_connection_failures HIGH
EOS-BACKEND-API api_error_rate MEDIUM
```

Create trace and spans showing:

```text
cache lookup failed
fallback path used
API response degraded
```

Diagnostic case:

```text
Probable cause: Redis cache instability causing degraded API response path
Confidence: MEDIUM
```

Do not actually stop Redis.

---

## Simulation 3: Allocation Failure

Endpoint:

```text
POST /api/v1/observability/simulations/allocation-failure
```

Behavior:

Create or reuse a warehouse allocation failure scenario.

This may use existing workflow services if safe.

Generate:

```text
business trace
validation span
inventory lookup span
structured logs
metric samples
diagnostic case
```

Diagnostic case should distinguish:

```text
Functional/business failure due to insufficient stock
```

from:

```text
technical system degradation
```

Probable cause example:

```text
Inventory availability below requested quantity; system correctly blocked allocation.
```

Confidence:

```text
HIGH
```

This scenario demonstrates observability helping avoid misclassifying a valid business rule failure as an application outage.

---

## Simulation 4: Shipment Integration Failure

Endpoint:

```text
POST /api/v1/observability/simulations/shipment-integration-failure
```

Behavior:

Generate monitoring alert:

```text
WF-SHIPMENT-SERVICE shipment_exception_count HIGH
```

Create trace:

```text
Ship order request failed during carrier label generation
```

Spans:

```text
ShipOrderWorkflow.ship_order
ShipmentService.create_shipment
CarrierLabelClient.generate_label
```

Logs:

```text
EXTERNAL_CALL_FAILED
WORKFLOW_STEP_FAILED
```

Metric samples:

```text
shipment_exception_count
api_latency_ms
```

Diagnostic case:

```text
Probable cause: Carrier label generation integration failure
Confidence: MEDIUM
```

Do not add real external carrier integration.

---

## Simulation 5: Observability Demo Suite

Endpoint:

```text
POST /api/v1/observability/simulations/observability-demo-suite
```

Behavior:

Run all enabled observability simulations in deterministic order.

Return:

```text
traces_created
diagnostic_cases_created
alerts_created_or_reused
tickets_created_or_linked
highest_severity
summary
```

Do not stop the suite if one simulation fails.

---

# Observability APIs

Create observability APIs.

Suggested files:

```text
backend/app/models/observability.py
backend/app/schemas/observability.py
backend/app/services/observability_service.py
backend/app/services/diagnostic_service.py
backend/app/api/routes/observability.py
```

Use prefix:

```text
/api/v1/observability
```

Add:

```text
GET  /api/v1/observability/summary
GET  /api/v1/observability/traces
GET  /api/v1/observability/traces/{trace_id}
GET  /api/v1/observability/log-events
GET  /api/v1/observability/metric-samples
GET  /api/v1/observability/diagnostic-cases
GET  /api/v1/observability/diagnostic-cases/{case_id}
POST /api/v1/observability/diagnostic-cases/{case_id}/link-ticket
POST /api/v1/observability/diagnostic-cases/{case_id}/resolve
POST /api/v1/observability/diagnostics/from-alert/{alert_id}
POST /api/v1/observability/diagnostics/from-triage-case/{case_id}
POST /api/v1/observability/diagnostics/from-ticket/{ticket_id}
POST /api/v1/observability/simulations/database-degradation
POST /api/v1/observability/simulations/redis-cache-failure
POST /api/v1/observability/simulations/allocation-failure
POST /api/v1/observability/simulations/shipment-integration-failure
POST /api/v1/observability/simulations/observability-demo-suite
```

---

## Observability Summary

Endpoint:

```text
GET /api/v1/observability/summary
```

Return:

```json
{
  "traces": 12,
  "error_traces": 4,
  "slow_spans": 8,
  "error_logs": 10,
  "metric_samples": 30,
  "open_diagnostic_cases": 3,
  "high_confidence_diagnoses": 2,
  "linked_tickets": 2
}
```

Use actual database queries.

---

## Trace List

Endpoint:

```text
GET /api/v1/observability/traces
```

Support optional filters:

```text
status
trace_type
source_module
linked_ticket_id
linked_alert_id
```

Default sort:

```text
newest first
```

---

## Trace Detail

Endpoint:

```text
GET /api/v1/observability/traces/{trace_id}
```

Return:

```text
trace header
spans
logs
metric samples
linked alert if any
linked triage case if any
linked ticket if any
```

The path parameter may be database UUID or trace_id string, whichever is easier and consistent.

---

## Log Events

Endpoint:

```text
GET /api/v1/observability/log-events
```

Support filters:

```text
level
event_type
trace_id
component_code
linked_ticket_id
```

Default sort:

```text
newest first
```

Limit default:

```text
200
```

---

## Metric Samples

Endpoint:

```text
GET /api/v1/observability/metric-samples
```

Support filters:

```text
metric_name
component_code
severity
trace_id
linked_alert_id
```

Default sort:

```text
newest first
```

Limit default:

```text
200
```

---

## Diagnostic Cases

Endpoint:

```text
GET /api/v1/observability/diagnostic-cases
```

Support filters:

```text
status
severity
confidence_level
source_type
linked_ticket_id
```

Default sort:

```text
open first, newest first
```

---

## Diagnostic Case Detail

Endpoint:

```text
GET /api/v1/observability/diagnostic-cases/{case_id}
```

Return:

```text
case header
probable cause
confidence
recommended next steps
diagnosis summary
linked trace
evidence records
linked alert
linked triage case
linked ticket
```

---

## Create Diagnosis from Alert

Endpoint:

```text
POST /api/v1/observability/diagnostics/from-alert/{alert_id}
```

Behavior:

- Inspect alert and related monitoring data.
- Create deterministic diagnostic case.
- If observability evidence already exists for the alert, link it.
- If not, create placeholder diagnostic case with low confidence.
- Do not hallucinate root cause.

---

## Create Diagnosis from Triage Case

Endpoint:

```text
POST /api/v1/observability/diagnostics/from-triage-case/{case_id}
```

Behavior:

- Inspect triage case and linked alerts.
- Create deterministic diagnostic case.
- Link any matching traces, logs, and metric samples.
- Confidence should depend on evidence strength.

---

## Create Diagnosis from Ticket

Endpoint:

```text
POST /api/v1/observability/diagnostics/from-ticket/{ticket_id}
```

Behavior:

- Inspect ticket source and linked alert/user report/exception if available.
- Create diagnostic case.
- Link matching observability records if available.

---

## Link Ticket to Diagnostic Case

Endpoint:

```text
POST /api/v1/observability/diagnostic-cases/{case_id}/link-ticket
```

Request:

```json
{
  "ticket_id": "optional-ticket-uuid"
}
```

Rules:

- If `ticket_id` supplied, link existing ticket.
- If omitted, create AMS incident from diagnostic case.
- Ticket source should be `OBSERVABILITY`.
- Ticket description should include probable cause, confidence, and evidence summary.
- Do not duplicate active ticket if already linked.

---

## Resolve Diagnostic Case

Endpoint:

```text
POST /api/v1/observability/diagnostic-cases/{case_id}/resolve
```

Request:

```json
{
  "resolution_notes": "Support engineer validated DB latency returned to normal."
}
```

Rules:

- allowed from `OPEN`, `UNDER_REVIEW`, `DIAGNOSED`, `LINKED_TO_TICKET`
- set status `RESOLVED`
- set `resolved_at`
- do not automatically close AMS ticket unless current AMS service supports it cleanly

---

# Diagnostic Confidence Rules

Use deterministic logic.

Example:

## High confidence

Use when:

```text
alert metric, span error/slow duration, log event, and metric sample all point to same component or cause
```

## Medium confidence

Use when:

```text
two evidence sources support the same probable cause
```

## Low confidence

Use when:

```text
only alert data exists or evidence is incomplete
```

## Unknown

Use when:

```text
diagnostic case cannot find enough evidence
```

Do not overstate diagnosis.

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
Observability
Traces
Diagnostics
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
Health
About
```

---

## Required Frontend Routes

Add:

```text
/observability
/observability/traces
/observability/traces/:traceId
/observability/logs
/observability/metrics
/observability/diagnostics
/observability/diagnostics/:caseId
/observability/simulations
```

Existing routes must continue working.

---

## Observability Overview Page

Route:

```text
/observability
```

Display summary cards from:

```text
GET /api/v1/observability/summary
```

Cards:

```text
traces
error traces
slow spans
error logs
metric samples
open diagnostic cases
high confidence diagnoses
linked tickets
```

Include explanatory text:

```text
This module demonstrates deterministic observability evidence for support diagnosis. It does not use AI or real external observability tools yet.
```

---

## Observability Simulations Page

Route:

```text
/observability/simulations
```

Display simulation cards:

```text
Database Degradation
Redis Cache Failure
Allocation Failure
Shipment Integration Failure
Observability Demo Suite
```

Each card should include:

- description
- button to run simulation
- result panel showing trace, diagnostic case, alert, and ticket links if available

---

## Traces Page

Route:

```text
/observability/traces
```

Display table:

```text
trace id
trace name
trace type
status
source module
root reference
duration
linked alert
linked ticket
started at
```

Use chips for status and trace type.

Trace ID should link to trace detail page.

---

## Trace Detail Page

Route:

```text
/observability/traces/:traceId
```

Display:

- trace header
- status
- duration
- linked business entity
- linked alert
- linked ticket
- span timeline/table
- related log events
- related metric samples

Span table columns:

```text
span name
service
component
operation type
status
duration
error message
```

Log table columns:

```text
time
level
event type
component
message
```

Metric table columns:

```text
time
metric
component
value
unit
severity
```

---

## Logs Page

Route:

```text
/observability/logs
```

Display table:

```text
log number
time
level
event type
component
entity
message
trace
ticket
```

Use chips for log level.

---

## Metrics Page

Route:

```text
/observability/metrics
```

Display table:

```text
sample number
time
metric name
component
value
unit
severity
trace
alert
```

Use chips for severity.

No charting library.

---

## Diagnostics Page

Route:

```text
/observability/diagnostics
```

Display table:

```text
diagnostic number
title
severity
status
confidence
probable cause
linked trace
linked ticket
created at
```

Actions:

```text
link/create ticket
resolve
```

Diagnostic number should link to detail page.

---

## Diagnostic Detail Page

Route:

```text
/observability/diagnostics/:caseId
```

Display:

- case header
- probable cause
- confidence level
- recommended next steps
- diagnosis summary
- linked trace
- linked alert
- linked triage case
- linked ticket
- evidence list/table

Evidence table:

```text
evidence type
title
details
weight
source
```

Actions:

```text
link/create ticket
resolve
```

---

# Frontend API Client

Create or extend typed API client.

Suggested file:

```text
frontend/src/services/observabilityApi.ts
```

Use `VITE_API_BASE_URL`.

Use TanStack Query for data loading.

Use mutations for simulations and actions.

Show loading and error states.

---

# AMS and Monitoring Integration Notes

You may need to extend existing AMS ticket schemas/service logic minimally to support:

```text
source = OBSERVABILITY
source_module = OBSERVABILITY
```

You may need to extend existing monitoring schemas minimally to allow links to observability data only if required.

Do this safely and minimally.

Do not break ticket creation from:

```text
operational exceptions
user reports
monitoring alerts
monitoring triage cases
manual ticket creation
```

Existing tests must continue to pass.

---

# Backend Tests

Add tests covering:

1. Existing health/version tests still pass
2. Existing warehouse read tests still pass
3. Existing warehouse workflow tests still pass
4. Existing operations/AMS tests still pass
5. Existing synthetic user tests still pass
6. Existing monitoring tests still pass
7. Observability simulation creates trace, spans, logs, metrics, and diagnostic case
8. Database degradation simulation creates high-confidence diagnostic case
9. Redis cache failure simulation creates medium-confidence diagnostic case
10. Allocation failure simulation identifies business-rule failure, not technical outage
11. Shipment integration failure simulation creates diagnostic evidence
12. Observability demo suite runs
13. Observability summary endpoint works
14. Trace list endpoint works
15. Trace detail endpoint includes spans/logs/metrics
16. Log event list endpoint works
17. Metric sample list endpoint works
18. Diagnostic case list endpoint works
19. Diagnostic case detail includes evidence
20. Create diagnosis from alert works
21. Create diagnosis from triage case works
22. Create diagnosis from ticket works
23. Link/create ticket from diagnostic case works
24. Duplicate ticket from diagnostic case is prevented
25. Resolve diagnostic case works
26. Invalid diagnostic transitions return `409`

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

- Prompt 07 observability-enabled diagnosis scenario summary
- simulated traces
- span timelines
- structured logs
- metric samples
- diagnostic cases
- diagnostic evidence
- observability simulations
- new APIs
- new frontend routes
- validation commands
- backend port `8050`
- frontend port `4001`
- explicit deferred items:
  - real OpenTelemetry export
  - Tempo
  - Loki
  - Prometheus scraping
  - Grafana dashboards
  - AI-native diagnosis
  - autonomous remediation
  - batch failures

Update `ARCHITECTURE.md` with:

- observability evidence module
- trace/log/metric model
- diagnostic case model
- evidence-backed support diagnosis flow
- comparison with Prompt 06 monitoring-only triage
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
pytest
```

Then validate live backend:

```bash
curl -sS http://localhost:8050/health | jq .
curl -sS http://localhost:8050/api/v1/observability/summary | jq .
curl -sS -X POST http://localhost:8050/api/v1/observability/simulations/database-degradation \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
curl -sS http://localhost:8050/api/v1/observability/traces | jq .
curl -sS http://localhost:8050/api/v1/observability/log-events | jq .
curl -sS http://localhost:8050/api/v1/observability/metric-samples | jq .
curl -sS http://localhost:8050/api/v1/observability/diagnostic-cases | jq .
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
http://localhost:4001/observability
http://localhost:4001/observability/simulations
http://localhost:4001/observability/traces
http://localhost:4001/observability/logs
http://localhost:4001/observability/metrics
http://localhost:4001/observability/diagnostics
```

Manual UI validation:

```text
Open Observability Simulations
Run Database Degradation simulation
Open Observability Overview
Confirm summary updates
Open Traces
Open generated trace detail
Confirm spans, logs, and metrics are visible
Open Diagnostics
Open generated diagnostic case
Confirm evidence is visible
Create/link AMS ticket from diagnostic case
Open AMS Tickets
Confirm observability-created ticket exists
Resolve diagnostic case
```

---

# Definition of Done

Prompt 07 is complete only when:

- migration exists
- `obs_traces` exists
- `obs_spans` exists
- `obs_log_events` exists
- `obs_metric_samples` exists
- `obs_diagnostic_cases` exists
- `obs_diagnostic_evidence` exists
- observability simulations work
- database degradation simulation works
- redis cache failure simulation works
- allocation failure simulation works
- shipment integration failure simulation works
- observability demo suite works
- trace list/detail APIs work
- log event API works
- metric sample API works
- diagnostic case APIs work
- diagnosis from alert works
- diagnosis from triage case works
- diagnosis from ticket works
- diagnostic evidence is visible through API
- ticket creation/linking from diagnostic case works
- duplicate ticket creation from diagnostic case is prevented
- diagnostic case resolution works
- existing warehouse APIs still work
- existing operations/AMS APIs still work
- existing synthetic user APIs still work
- existing monitoring APIs still work
- frontend observability overview page works
- frontend simulation page works
- frontend trace list/detail pages work
- frontend logs page works
- frontend metrics page works
- frontend diagnostics list/detail pages work
- backend tests pass
- frontend build passes
- backend remains on port `8050`
- frontend remains on port `4001`
- README updated
- ARCHITECTURE.md updated
- no infrastructure files modified

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Alembic migration name
4. Backend observability APIs added
5. Backend observability simulation APIs added
6. Frontend routes added
7. Backend validation results
8. Frontend validation results
9. Manual observability diagnosis validation result
10. Confirmation that infrastructure files were not modified
11. Any TODOs
12. Recommended Git commit message

Recommended commit message:

```text
feat: add observability-enabled support diagnosis
```

Do not proceed beyond this prompt.