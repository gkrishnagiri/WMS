# Prompt 06 – Monitoring Alert Noise Without Observability

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

**Enterprise Operations Suite (EOS)**

Prompt 01 created the enterprise application foundation.

Prompt 02 created the Warehouse & Fulfillment domain foundation.

Prompt 03 created warehouse transaction workflows.

Prompt 04 created operational exceptions and the AMS ticket foundation.

Prompt 05 created synthetic users, synthetic journeys, user-reported issues, and ticket creation from user reports.

Your task now is to implement the next support scenario:

```text
Monitoring Alert Noise Without Observability
```

This prompt represents the scenario where a monitoring system exists, but there is **no deep observability, no traces, no log correlation, and no AI diagnosis**.

The support engineer sees many alerts from multiple components and must manually triage them.

Do not implement OpenTelemetry traces, log analysis, GenAI, LLMs, agents, batch jobs, or ServiceNow integration yet.

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
- Ticket creation from user reports
- Backend running on port `8050`
- Frontend running on port `4001`

Recent committed capabilities include:

```text
feat: add EOS enterprise foundation
feat: add warehouse fulfillment domain foundation
feat: add warehouse transaction workflows
feat: add operational exceptions and AMS ticket foundation
feat: add synthetic users and user-reported issues
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
- real OpenTelemetry instrumentation
- log aggregation features

This prompt should simulate a monitoring system at the application data/API level.

Do not modify the existing Prometheus, Grafana, or OpenTelemetry Collector configuration.

---

# Objective

Implement a deterministic monitoring-alert-noise module.

This prompt should allow EOS to demonstrate this scenario:

```text
Monitoring tool detects many component-level symptoms
        ↓
Multiple noisy alerts are generated
        ↓
Support engineer sees symptoms but lacks observability context
        ↓
Support engineer manually groups alerts into a triage case
        ↓
Support engineer creates an AMS ticket from the triage case
        ↓
Ticket lifecycle continues through the existing AMS ticket module
```

This prompt specifically addresses:

```text
B. Monitoring system enabled, but no observability in place.
   Many noisy alerts are generated from multiple components.
   A support engineer manually analyzes and resolves them.
```

This prompt does **not** address:

```text
C. Monitoring plus observability-enabled diagnosis
D. Batch issue
AI-native agentic remediation
```

Those will come in later prompts.

---

# Architectural Intent

Prompt 04 created operational exceptions and AMS tickets.

Prompt 05 created synthetic user/user-reported issue sources.

Prompt 06 creates another source of support work:

```text
Monitoring Alert
        ↓
Alert Noise
        ↓
Manual Triage Case
        ↓
AMS Ticket
```

In this prompt, monitoring alerts are **not** equivalent to root cause.

They are symptoms.

Because there is no observability yet, the system should not automatically identify root cause.

The support engineer should see clues such as:

```text
API latency high
database response time high
Redis connection failures
frontend API failures
warehouse allocation failures
shipment API timeout
```

But the system should not claim to know the real root cause.

---

# Scope

Implement:

1. Monitored component catalog
2. Monitoring alert rules
3. Monitoring alert records
4. Alert event history
5. Deterministic noisy alert simulations
6. Alert acknowledgement, suppression, and resolution
7. Manual triage case creation from alerts
8. AMS ticket creation from alert or triage case
9. Monitoring dashboard frontend pages
10. Backend tests
11. Documentation updates

Do not implement:

- actual Prometheus scraping
- actual Grafana integration
- OpenTelemetry traces
- distributed tracing
- log ingestion
- log correlation
- root cause automation
- AI summaries
- autonomous remediation
- ServiceNow integration
- batch jobs

---

# Database Additions

Create a new Alembic migration.

Add the following tables:

```text
mon_components
mon_alert_rules
mon_alerts
mon_alert_events
mon_triage_cases
mon_triage_case_alerts
```

Optional, only if simple and consistent:

```text
mon_simulation_runs
```

Use UUID primary keys consistent with the existing project style.

Use timestamp conventions consistent with the existing project.

---

## Table: `mon_components`

Purpose:

Represent application and infrastructure components that can emit monitoring alerts.

Fields:

```text
id
component_code
name
component_type
layer
environment
owner_team
business_service
application_name
status
description
created_at
updated_at
```

Rules:

- `component_code` must be unique
- `application_name` should default to `Enterprise Operations Suite`
- `business_service` should default to `Warehouse & Fulfillment Operations`
- `environment` should default to current app environment

Suggested component types:

```text
FRONTEND
API
DATABASE
CACHE
WORKFLOW
INTEGRATION
BUSINESS_PROCESS
```

Suggested layers:

```text
PRESENTATION
APPLICATION
DATA
CACHE
BUSINESS_WORKFLOW
EXTERNAL
```

Suggested components to seed:

```text
EOS-FRONTEND          EOS Frontend
EOS-BACKEND-API       EOS Backend API
EOS-POSTGRES          EOS PostgreSQL
EOS-REDIS             EOS Redis
WF-ORDER-WORKFLOW     Warehouse Order Workflow
WF-INVENTORY-SERVICE  Warehouse Inventory Service
WF-SHIPMENT-SERVICE   Warehouse Shipment Service
```

---

## Table: `mon_alert_rules`

Purpose:

Represent deterministic monitoring rules.

Fields:

```text
id
rule_code
name
description
component_id
metric_name
condition_operator
threshold_value
severity
enabled
dedupe_window_minutes
created_at
updated_at
```

Rules:

- `rule_code` must be unique
- `component_id` references `mon_components.id`
- `enabled` defaults to true

Suggested metric names:

```text
api_error_rate
api_latency_ms
db_latency_ms
redis_connection_failures
workflow_failure_count
allocation_failure_count
shipment_exception_count
frontend_api_failure_count
```

Suggested condition operators:

```text
GT
GTE
LT
LTE
EQ
```

Suggested severities:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Seed at least 8 rules.

---

## Table: `mon_alerts`

Purpose:

Represent monitoring alerts generated from component monitoring.

Fields:

```text
id
alert_number
rule_id
component_id
severity
status
signal_type
metric_name
observed_value
threshold_value
dedupe_key
title
description
first_seen_at
last_seen_at
occurrence_count
acknowledged_at
suppressed_at
resolved_at
linked_exception_id
linked_ticket_id
created_at
updated_at
```

Rules:

- `alert_number` must be unique
- `rule_id` references `mon_alert_rules.id`
- `component_id` references `mon_components.id`
- `linked_exception_id` nullable, references `ops_exceptions.id` if useful
- `linked_ticket_id` nullable, references `ams_tickets.id`
- `dedupe_key` should help avoid uncontrolled duplicates
- repeated alert with same dedupe key should increment `occurrence_count` and update `last_seen_at`

Suggested statuses:

```text
OPEN
ACKNOWLEDGED
SUPPRESSED
LINKED_TO_TICKET
RESOLVED
CLOSED
```

Suggested signal types:

```text
METRIC_THRESHOLD
AVAILABILITY
ERROR_RATE
LATENCY
BUSINESS_KPI
SYNTHETIC_CHECK
```

---

## Table: `mon_alert_events`

Purpose:

Maintain lifecycle/audit history for monitoring alerts.

Fields:

```text
id
alert_id
event_type
from_status
to_status
message
event_payload
created_by
created_at
```

Rules:

- `alert_id` references `mon_alerts.id`
- `event_payload` should be JSON/JSONB if supported
- `created_by` defaults to `system`

Suggested event types:

```text
ALERT_CREATED
ALERT_REPEATED
ALERT_ACKNOWLEDGED
ALERT_SUPPRESSED
ALERT_RESOLVED
ALERT_LINKED_TO_TICKET
ALERT_ADDED_TO_TRIAGE_CASE
```

---

## Table: `mon_triage_cases`

Purpose:

Represent a manual support triage grouping of related alerts.

This is not an AI root cause analysis.

It is a support engineer’s working case.

Fields:

```text
id
case_number
title
description
status
severity
suspected_impact
suspected_root_cause
confidence_level
analysis_notes
linked_ticket_id
created_by
created_at
updated_at
acknowledged_at
resolved_at
closed_at
```

Rules:

- `case_number` must be unique
- `linked_ticket_id` nullable, references `ams_tickets.id`
- `suspected_root_cause` should remain human-entered or deterministic placeholder text
- do not auto-generate root cause claims

Suggested statuses:

```text
OPEN
INVESTIGATING
LINKED_TO_TICKET
RESOLVED
CLOSED
```

Suggested confidence levels:

```text
LOW
MEDIUM
HIGH
UNKNOWN
```

---

## Table: `mon_triage_case_alerts`

Purpose:

Many-to-many relationship between triage cases and alerts.

Fields:

```text
id
triage_case_id
alert_id
created_at
```

Rules:

- `triage_case_id` references `mon_triage_cases.id`
- `alert_id` references `mon_alerts.id`
- unique constraint on `(triage_case_id, alert_id)`

---

## Optional Table: `mon_simulation_runs`

Only add this if straightforward.

Purpose:

Track monitoring simulation executions.

Fields:

```text
id
simulation_code
status
input_payload
result_payload
alerts_created
alerts_repeated
created_by
created_at
```

Suggested statuses:

```text
SUCCESS
FAILED
```

If this table adds too much complexity, skip it and document as deferred.

---

# Seed Data

Create an idempotent seed module:

```text
backend/app/db/seed_monitoring.py
```

Runnable as:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_monitoring
```

It should seed:

```text
7 monitored components
at least 8 alert rules
```

Running it multiple times must not create duplicates.

Update README validation commands to include this seed command.

Do not modify existing warehouse or synthetic user seed behavior.

---

# Monitoring Alert Service

Create a service such as:

```text
backend/app/services/monitoring_service.py
```

or similar.

Implement deterministic alert creation and deduplication.

## Alert Deduplication

When creating an alert, compute or accept a `dedupe_key`.

If an `OPEN` or `ACKNOWLEDGED` alert exists for the same dedupe key:

- do not create a duplicate alert
- increment `occurrence_count`
- update `last_seen_at`
- create `ALERT_REPEATED` event
- return the existing alert

If no active alert exists:

- create new alert
- `occurrence_count = 1`
- create `ALERT_CREATED` event

---

# Monitoring Simulations

Create deterministic monitoring simulations.

Use prefix:

```text
/api/v1/monitoring/simulations
```

Implement:

```text
POST /api/v1/monitoring/simulations/api-latency-cascade
POST /api/v1/monitoring/simulations/database-degradation
POST /api/v1/monitoring/simulations/redis-flapping
POST /api/v1/monitoring/simulations/frontend-error-burst
POST /api/v1/monitoring/simulations/warehouse-workflow-noise
POST /api/v1/monitoring/simulations/noisy-alert-storm
```

Each simulation should generate deterministic alert records.

Do not rely on real Prometheus metrics.

---

## Simulation 1: API Latency Cascade

Endpoint:

```text
POST /api/v1/monitoring/simulations/api-latency-cascade
```

Behavior:

Generate multiple related alerts:

```text
EOS-BACKEND-API api_latency_ms HIGH
EOS-BACKEND-API api_error_rate MEDIUM
EOS-FRONTEND frontend_api_failure_count MEDIUM
WF-ORDER-WORKFLOW workflow_failure_count MEDIUM
```

Purpose:

Show noisy symptoms across frontend, API, and workflow layers.

---

## Simulation 2: Database Degradation

Endpoint:

```text
POST /api/v1/monitoring/simulations/database-degradation
```

Behavior:

Generate alerts:

```text
EOS-POSTGRES db_latency_ms HIGH
EOS-BACKEND-API api_latency_ms HIGH
WF-INVENTORY-SERVICE allocation_failure_count HIGH
WF-ORDER-WORKFLOW workflow_failure_count MEDIUM
```

Purpose:

Show how a database issue can surface as multiple business/application alerts.

Do not claim root cause automatically.

---

## Simulation 3: Redis Flapping

Endpoint:

```text
POST /api/v1/monitoring/simulations/redis-flapping
```

Behavior:

Generate alerts:

```text
EOS-REDIS redis_connection_failures HIGH
EOS-BACKEND-API api_error_rate MEDIUM
WF-ORDER-WORKFLOW workflow_failure_count LOW
```

Purpose:

Show intermittent infrastructure noise.

---

## Simulation 4: Frontend Error Burst

Endpoint:

```text
POST /api/v1/monitoring/simulations/frontend-error-burst
```

Behavior:

Generate alerts:

```text
EOS-FRONTEND frontend_api_failure_count HIGH
EOS-BACKEND-API api_error_rate MEDIUM
```

Purpose:

Show user-facing noise without enough backend detail.

---

## Simulation 5: Warehouse Workflow Noise

Endpoint:

```text
POST /api/v1/monitoring/simulations/warehouse-workflow-noise
```

Behavior:

Generate alerts:

```text
WF-ORDER-WORKFLOW workflow_failure_count HIGH
WF-INVENTORY-SERVICE allocation_failure_count HIGH
WF-SHIPMENT-SERVICE shipment_exception_count MEDIUM
```

Purpose:

Show business-process monitoring noise.

---

## Simulation 6: Noisy Alert Storm

Endpoint:

```text
POST /api/v1/monitoring/simulations/noisy-alert-storm
```

Behavior:

Run several deterministic simulations in sequence.

Return:

```text
alerts_created
alerts_repeated
alerts_open
highest_severity
simulation_summary
```

Purpose:

Demo a noisy monitoring console.

---

# Monitoring APIs

Create monitoring APIs.

Suggested files:

```text
backend/app/models/monitoring.py
backend/app/schemas/monitoring.py
backend/app/services/monitoring_service.py
backend/app/api/routes/monitoring.py
backend/app/db/seed_monitoring.py
```

You may organize differently if consistent with existing project style.

Use prefix:

```text
/api/v1/monitoring
```

Add:

```text
GET  /api/v1/monitoring/summary
GET  /api/v1/monitoring/components
GET  /api/v1/monitoring/rules
GET  /api/v1/monitoring/alerts
GET  /api/v1/monitoring/alerts/{alert_id}
POST /api/v1/monitoring/alerts/{alert_id}/acknowledge
POST /api/v1/monitoring/alerts/{alert_id}/suppress
POST /api/v1/monitoring/alerts/{alert_id}/resolve
POST /api/v1/monitoring/alerts/{alert_id}/create-ticket
GET  /api/v1/monitoring/alerts/{alert_id}/events
GET  /api/v1/monitoring/triage-cases
POST /api/v1/monitoring/triage-cases
GET  /api/v1/monitoring/triage-cases/{case_id}
POST /api/v1/monitoring/triage-cases/{case_id}/add-alerts
POST /api/v1/monitoring/triage-cases/{case_id}/start-investigation
POST /api/v1/monitoring/triage-cases/{case_id}/resolve
POST /api/v1/monitoring/triage-cases/{case_id}/create-ticket
```

---

## Monitoring Summary

Endpoint:

```text
GET /api/v1/monitoring/summary
```

Return:

```json
{
  "open_alerts": 12,
  "critical_alerts": 1,
  "high_alerts": 4,
  "acknowledged_alerts": 2,
  "suppressed_alerts": 1,
  "open_triage_cases": 2,
  "alerts_linked_to_tickets": 3,
  "noisiest_component": "EOS-BACKEND-API"
}
```

Use actual database queries.

---

## Alert List Filters

Endpoint:

```text
GET /api/v1/monitoring/alerts
```

Support optional filters:

```text
status
severity
component_id
component_code
signal_type
metric_name
```

Default sort:

```text
open first, highest severity first, newest first
```

---

## Alert Lifecycle

### Acknowledge Alert

```text
POST /api/v1/monitoring/alerts/{alert_id}/acknowledge
```

Allowed from:

```text
OPEN
```

Result:

```text
ACKNOWLEDGED
```

Create event.

---

### Suppress Alert

```text
POST /api/v1/monitoring/alerts/{alert_id}/suppress
```

Allowed from:

```text
OPEN
ACKNOWLEDGED
```

Result:

```text
SUPPRESSED
```

Set `suppressed_at`.

Create event.

---

### Resolve Alert

```text
POST /api/v1/monitoring/alerts/{alert_id}/resolve
```

Allowed from:

```text
OPEN
ACKNOWLEDGED
SUPPRESSED
LINKED_TO_TICKET
```

Result:

```text
RESOLVED
```

Set `resolved_at`.

Create event.

---

## Create Ticket from Alert

Endpoint:

```text
POST /api/v1/monitoring/alerts/{alert_id}/create-ticket
```

Rules:

- If active ticket already exists for the alert, return existing ticket.
- Create AMS ticket type `INCIDENT`.
- Ticket source should be `MONITORING`.
- `source_module` should be `MONITORING`.
- `application_name` should be `Enterprise Operations Suite`.
- `business_service` should be `Warehouse & Fulfillment Operations`.
- Short description should include alert number and alert title.
- Description should include component, metric, observed value, threshold, severity, and lack of observability context.
- Map alert severity to ticket priority:
  - `CRITICAL` → `P1`
  - `HIGH` → `P2`
  - `MEDIUM` → `P3`
  - `LOW` → `P4`
- Update alert status to `LINKED_TO_TICKET`.
- Link `mon_alerts.linked_ticket_id`.

---

# Triage Case Behavior

## Create Triage Case

Endpoint:

```text
POST /api/v1/monitoring/triage-cases
```

Request:

```json
{
  "title": "Multiple warehouse API and database alerts",
  "description": "Support engineer is manually grouping noisy alerts for investigation.",
  "severity": "HIGH",
  "suspected_impact": "Order allocation and shipment workflows may be degraded.",
  "suspected_root_cause": "Unknown - no observability traces available",
  "confidence_level": "LOW",
  "alert_ids": ["optional-alert-id"]
}
```

Rules:

- Create triage case.
- Add selected alerts if provided.
- Do not require root cause.
- `suspected_root_cause` may be `"Unknown"`.

---

## Add Alerts to Triage Case

Endpoint:

```text
POST /api/v1/monitoring/triage-cases/{case_id}/add-alerts
```

Request:

```json
{
  "alert_ids": ["alert-id-1", "alert-id-2"]
}
```

Rules:

- Add alerts idempotently.
- Do not create duplicate links.

---

## Start Investigation

Endpoint:

```text
POST /api/v1/monitoring/triage-cases/{case_id}/start-investigation
```

Allowed from:

```text
OPEN
```

Result:

```text
INVESTIGATING
```

---

## Resolve Triage Case

Endpoint:

```text
POST /api/v1/monitoring/triage-cases/{case_id}/resolve
```

Request:

```json
{
  "analysis_notes": "Support engineer determined the symptom cleared after database response time normalized."
}
```

Rules:

- Set status `RESOLVED`.
- Set `resolved_at`.
- Do not automatically resolve linked AMS ticket unless the current AMS service supports it cleanly.

---

## Create Ticket from Triage Case

Endpoint:

```text
POST /api/v1/monitoring/triage-cases/{case_id}/create-ticket
```

Rules:

- If active ticket already exists for the triage case, return existing ticket.
- Create AMS incident.
- Ticket source should be `MONITORING`.
- Priority should follow triage case severity.
- Description should list included alert numbers and components.
- Update triage case status to `LINKED_TO_TICKET`.
- Link `mon_triage_cases.linked_ticket_id`.
- Optionally update included alerts to `LINKED_TO_TICKET` if safe and consistent.

---

# Error Handling

Use:

```text
400 Bad Request
```

for invalid inputs.

Use:

```text
404 Not Found
```

for missing records.

Use:

```text
409 Conflict
```

for invalid lifecycle transitions or duplicate active states.

Do not return generic internal errors for business rule violations.

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
Monitoring
Monitoring Simulations
Monitoring Triage
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
Health
About
```

---

## Required Frontend Routes

Add:

```text
/monitoring/alerts
/monitoring/simulations
/monitoring/triage
/monitoring/triage/:caseId
```

Existing routes must continue working.

---

## Monitoring Alerts Page

Route:

```text
/monitoring/alerts
```

Display:

- summary cards from `/api/v1/monitoring/summary`
- alert table

Alert table columns:

```text
alert number
severity
status
component
metric
observed value
threshold
occurrence count
first seen
last seen
linked ticket
```

Actions:

```text
acknowledge
suppress
resolve
create ticket
```

Use chips for severity and status.

---

## Monitoring Simulations Page

Route:

```text
/monitoring/simulations
```

Display simulation cards:

```text
API Latency Cascade
Database Degradation
Redis Flapping
Frontend Error Burst
Warehouse Workflow Noise
Noisy Alert Storm
```

Each card should show:

- description
- button to run simulation
- result panel showing alerts created/repeated

After a simulation runs, provide link to:

```text
/monitoring/alerts
```

---

## Monitoring Triage Page

Route:

```text
/monitoring/triage
```

Display:

- triage case list
- button to create new triage case
- simple create case form or dialog
- ability to select open alerts and create a triage case

Triage case table columns:

```text
case number
title
severity
status
alert count
linked ticket
created at
```

Actions:

```text
start investigation
resolve
create ticket
```

---

## Monitoring Triage Detail Page

Route:

```text
/monitoring/triage/:caseId
```

Display:

- triage case header
- suspected impact
- suspected root cause
- confidence level
- analysis notes
- linked alerts
- linked AMS ticket if any

Actions:

```text
start investigation
resolve
create ticket
```

---

# Frontend API Client

Create or extend typed API clients.

Suggested file:

```text
frontend/src/services/monitoringApi.ts
```

Use `VITE_API_BASE_URL`.

Use TanStack Query for data loading.

Use mutations for actions.

Show loading and error states.

---

# AMS Integration Notes

You may need to extend existing AMS ticket schemas or service logic to support:

```text
source = MONITORING
source_module = MONITORING
```

Do this minimally and safely.

Do not break existing ticket creation from:

```text
operational exceptions
user reports
manual ticket creation
```

Existing AMS tests must continue to pass.

---

# Backend Tests

Add tests covering:

1. Existing health/version tests still pass
2. Existing warehouse read tests still pass
3. Existing warehouse workflow tests still pass
4. Existing operations/AMS tests still pass
5. Existing synthetic user tests still pass
6. Monitoring seed is idempotent
7. List monitored components
8. List alert rules
9. Run API latency cascade simulation
10. Run database degradation simulation
11. Run noisy alert storm simulation
12. Alert deduplication increments occurrence count
13. List alerts
14. Acknowledge alert
15. Suppress alert
16. Resolve alert
17. Create ticket from alert
18. Prevent duplicate ticket from same alert
19. Create triage case from alerts
20. Add alerts to triage case idempotently
21. Start triage investigation
22. Create ticket from triage case
23. Resolve triage case
24. Monitoring summary endpoint works

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

- Prompt 06 monitoring-alert-noise scenario summary
- monitored components
- alert rules
- alert simulations
- alert lifecycle
- triage cases
- ticket creation from alerts and triage cases
- new APIs
- new frontend routes
- seed commands
- validation commands
- backend port `8050`
- frontend port `4001`
- deferred future scenario:
  - observability-enabled diagnosis with logs/metrics/traces
  - batch failures
  - AI-native support agents

Update `ARCHITECTURE.md` with:

- monitoring alert module
- alert noise simulation flow
- manual triage case module
- monitoring-to-AMS ticket flow
- explicit statement that root cause is not automated in this prompt
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
curl -sS http://localhost:8050/api/v1/monitoring/summary | jq .
curl -sS http://localhost:8050/api/v1/monitoring/components | jq .
curl -sS http://localhost:8050/api/v1/monitoring/rules | jq .
curl -sS -X POST http://localhost:8050/api/v1/monitoring/simulations/noisy-alert-storm \
  -H "Content-Type: application/json" \
  -d '{}' | jq .
curl -sS http://localhost:8050/api/v1/monitoring/alerts | jq .
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
http://localhost:4001/monitoring/alerts
http://localhost:4001/monitoring/simulations
http://localhost:4001/monitoring/triage
```

Manual UI validation:

```text
Open Monitoring Simulations
Run Noisy Alert Storm
Open Monitoring Alerts
Confirm multiple alerts exist
Acknowledge one alert
Suppress one alert
Create ticket from one alert
Open Monitoring Triage
Create triage case from multiple alerts
Start investigation
Create AMS ticket from triage case
Resolve triage case
Open AMS Tickets
Confirm monitoring-created ticket exists
```

---

# Definition of Done

Prompt 06 is complete only when:

- migration exists
- `mon_components` exists
- `mon_alert_rules` exists
- `mon_alerts` exists
- `mon_alert_events` exists
- `mon_triage_cases` exists
- `mon_triage_case_alerts` exists
- monitoring seed exists and is idempotent
- monitoring summary API works
- component API works
- alert rule API works
- alert list/detail APIs work
- alert simulations work
- noisy alert storm works
- alert deduplication works
- alert acknowledge/suppress/resolve works
- ticket creation from alert works
- duplicate ticket creation from alert is prevented
- triage case creation works
- alerts can be added to triage case
- ticket creation from triage case works
- triage lifecycle works
- existing AMS ticket lifecycle still works
- frontend monitoring alerts page works
- frontend monitoring simulations page works
- frontend monitoring triage page works
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
4. Backend monitoring APIs added
5. Backend simulation APIs added
6. Frontend routes added
7. Seed command and result
8. Backend validation results
9. Frontend validation results
10. Manual monitoring-noise and triage validation result
11. Confirmation that infrastructure files were not modified
12. Any TODOs
13. Recommended Git commit message

Recommended commit message:

```text
feat: add monitoring alert noise and triage foundation
```

Do not proceed beyond this prompt.