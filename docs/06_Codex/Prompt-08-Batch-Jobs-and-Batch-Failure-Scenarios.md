# Prompt 08 – Batch Jobs and Batch Failure Scenarios

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

Prompt 07 created observability-enabled support diagnosis using deterministic traces, spans, logs, metrics, and diagnostic cases.

Your task now is to implement the next support scenario:

```text
Batch Jobs and Batch Failure Scenarios
```

This prompt represents failures that occur in scheduled or operational batch processes, such as nightly inventory reconciliation, shipment status synchronization, order release batches, and delayed/stuck batch jobs.

Do not implement GenAI, LLMs, agents, autonomous remediation, ServiceNow integration, real schedulers, Celery, Kafka, or external batch orchestration yet.

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
- Application-level observability evidence
- Diagnostic cases and diagnostic evidence
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

- real schedulers
- cron integration
- Celery
- Dramatiq
- Kafka
- Temporal
- Airflow
- workflow engines
- browser automation frameworks
- charting libraries
- LangGraph
- LLM SDKs
- agent frameworks
- ServiceNow connectors
- real external integrations

Batch processing in this prompt is deterministic and manually triggered through APIs/UI.

---

# Objective

Implement a deterministic batch job and batch failure foundation.

This prompt should allow EOS to demonstrate this support scenario:

```text
A scheduled/operational batch process runs
        ↓
Batch steps execute
        ↓
One or more steps succeed, fail, timeout, or partially complete
        ↓
Batch run status is recorded
        ↓
Batch failure creates operational exception and/or AMS ticket
        ↓
Monitoring alerts and observability evidence can be linked where appropriate
        ↓
Support engineer investigates and manages the failure
```

This prompt specifically addresses:

```text
D. Batch issue
```

It should also connect naturally to the existing support layers:

```text
Batch failure
    ↓
Operational exception
    ↓
Monitoring alert
    ↓
Observability diagnostic evidence
    ↓
AMS ticket
```

However, keep all integrations deterministic and simple.

---

# Architectural Intent

Prompts 04–07 created supportability capabilities for interactive workflows.

Prompt 08 adds a new class of support scenarios: batch operations.

Batch jobs should be modeled as first-class operational processes.

Examples:

```text
Nightly inventory reconciliation
Order release batch
Shipment status synchronization
Low stock notification batch
Inventory snapshot batch
```

Batch jobs are important for AMS because many production incidents occur outside direct user interaction.

In this prompt:

- batch jobs are not real scheduled background processes
- batch jobs are manually started through API/UI
- batch runs and step runs are persisted
- deterministic failure simulations are supported
- support artifacts can be generated from failures

---

# Scope

Implement:

1. Batch job catalog
2. Batch job steps
3. Batch run history
4. Batch step run history
5. Batch run events
6. Deterministic batch execution simulations
7. Batch failure scenarios
8. Batch-to-exception integration
9. Batch-to-AMS-ticket integration
10. Optional batch-to-monitoring/observability integration where simple
11. Batch frontend pages
12. Backend tests
13. Documentation updates

Do not implement:

- real scheduling
- real async workers
- real cron
- real queue workers
- real external integrations
- real file ingestion
- AI diagnosis
- autonomous remediation
- ServiceNow integration
- production-grade retry orchestration

---

# Database Additions

Create a new Alembic migration.

Add the following tables:

```text
batch_jobs
batch_job_steps
batch_runs
batch_step_runs
batch_run_events
```

Optional only if simple and useful:

```text
batch_failure_patterns
```

Use UUID primary keys consistent with the existing project style.

Use timestamp conventions consistent with the existing project.

---

## Table: `batch_jobs`

Purpose:

Define deterministic batch jobs available in EOS.

Fields:

```text
id
job_code
name
description
job_type
module
business_service
application_name
enabled
default_severity
sla_minutes
created_at
updated_at
```

Rules:

- `job_code` must be unique
- `module` should usually be `WAREHOUSE_FULFILLMENT`
- `business_service` should default to `Warehouse & Fulfillment Operations`
- `application_name` should default to `Enterprise Operations Suite`
- `enabled` defaults to true

Suggested job types:

```text
INVENTORY_RECONCILIATION
ORDER_RELEASE
SHIPMENT_SYNC
LOW_STOCK_NOTIFICATION
INVENTORY_SNAPSHOT
```

Seed jobs:

```text
BATCH-INV-RECON     Nightly Inventory Reconciliation
BATCH-ORDER-RELEASE Wave Order Release
BATCH-SHIP-SYNC     Shipment Status Synchronization
BATCH-LOW-STOCK     Low Stock Notification Batch
BATCH-INV-SNAPSHOT  Inventory Snapshot Batch
```

---

## Table: `batch_job_steps`

Purpose:

Define ordered steps inside a batch job.

Fields:

```text
id
job_id
step_code
step_name
step_order
step_type
description
enabled
expected_duration_ms
created_at
updated_at
```

Rules:

- `job_id` references `batch_jobs.id`
- unique constraint on `(job_id, step_code)`
- unique constraint on `(job_id, step_order)`
- `enabled` defaults to true

Suggested step types:

```text
EXTRACT
VALIDATE
TRANSFORM
PROCESS
RECONCILE
NOTIFY
EXPORT
```

Example steps for inventory reconciliation:

```text
EXTRACT_INVENTORY_BALANCES
VALIDATE_BALANCES
RECONCILE_ON_HAND
GENERATE_VARIANCE_REPORT
PUBLISH_RESULTS
```

---

## Table: `batch_runs`

Purpose:

Record each execution of a batch job.

Fields:

```text
id
run_number
job_id
status
trigger_type
scenario_code
started_at
completed_at
duration_ms
records_processed
records_succeeded
records_failed
failure_type
failure_message
summary
linked_exception_id
linked_ticket_id
linked_alert_id
linked_diagnostic_case_id
created_by
created_at
updated_at
```

Rules:

- `run_number` must be unique
- `job_id` references `batch_jobs.id`
- linked fields are nullable
- `scenario_code` captures deterministic scenario used for the run

Suggested statuses:

```text
PENDING
RUNNING
SUCCESS
FAILED
PARTIAL_SUCCESS
TIMEOUT
CANCELLED
```

Suggested trigger types:

```text
MANUAL
SIMULATION
SCHEDULED_SIMULATION
SYSTEM
```

Suggested failure types:

```text
DATA_VALIDATION_ERROR
TIMEOUT
EXTERNAL_SYSTEM_ERROR
BUSINESS_RULE_FAILURE
DATABASE_LATENCY
PARTIAL_RECORD_FAILURE
UNKNOWN
```

Run number format:

```text
BATCH-RUN-YYYYMMDD-0001
```

---

## Table: `batch_step_runs`

Purpose:

Record execution result of each batch step.

Fields:

```text
id
batch_run_id
job_step_id
step_code
step_name
step_order
status
started_at
completed_at
duration_ms
records_processed
records_succeeded
records_failed
failure_type
failure_message
technical_context
created_at
updated_at
```

Rules:

- `batch_run_id` references `batch_runs.id`
- `job_step_id` references `batch_job_steps.id`
- `technical_context` should be JSON/JSONB if supported

Suggested statuses:

```text
PENDING
RUNNING
SUCCESS
FAILED
SKIPPED
TIMEOUT
PARTIAL_SUCCESS
```

---

## Table: `batch_run_events`

Purpose:

Maintain lifecycle and audit events for batch runs.

Fields:

```text
id
batch_run_id
event_type
from_status
to_status
message
event_payload
created_by
created_at
```

Rules:

- `batch_run_id` references `batch_runs.id`
- `event_payload` should be JSON/JSONB if supported
- `created_by` defaults to `system`

Suggested event types:

```text
BATCH_RUN_CREATED
BATCH_RUN_STARTED
BATCH_STEP_STARTED
BATCH_STEP_COMPLETED
BATCH_STEP_FAILED
BATCH_RUN_COMPLETED
BATCH_RUN_FAILED
BATCH_RUN_PARTIAL_SUCCESS
BATCH_EXCEPTION_CREATED
BATCH_TICKET_CREATED
BATCH_ALERT_CREATED
BATCH_DIAGNOSTIC_CREATED
```

---

## Optional Table: `batch_failure_patterns`

Only add this if straightforward.

Purpose:

Represent reusable deterministic failure patterns.

Fields:

```text
id
pattern_code
name
description
job_code
failure_type
severity
default_payload
enabled
created_at
updated_at
```

If this table adds too much complexity, skip it and document as deferred.

---

# Seed Data

Create an idempotent seed module:

```text
backend/app/db/seed_batch.py
```

Runnable as:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_batch
```

It should seed:

```text
5 batch jobs
at least 20 batch job steps
```

Running it multiple times must not create duplicates.

Update README validation commands to include this seed command.

Do not modify existing seed behavior for warehouse, synthetic users, monitoring, operations, AMS, or observability.

---

# Batch Execution Service

Create services such as:

```text
backend/app/services/batch_service.py
backend/app/services/batch_simulation_service.py
```

or equivalent.

The services should support:

```text
list batch jobs
get batch job detail
start deterministic batch run
create batch step runs
record batch events
simulate success
simulate failure
link batch run to exception
link batch run to AMS ticket
link batch run to monitoring alert if useful
link batch run to diagnostic case if useful
```

Do not duplicate database session handling.

Reuse existing support services where safe.

---

# Batch Execution Behavior

Batch runs are synchronous deterministic simulations in this prompt.

A run should:

1. create `batch_runs` row with status `RUNNING`
2. create `BATCH_RUN_STARTED` event
3. execute configured job steps in order
4. create `batch_step_runs`
5. record step success/failure
6. set final run status
7. create support artifacts if requested
8. return complete run summary

Do not use background tasks or async workers unless the existing app already has a very simple safe pattern.

---

# Batch Simulation Scenarios

Use prefix:

```text
/api/v1/batch/simulations
```

Implement:

```text
POST /api/v1/batch/simulations/inventory-reconciliation-success
POST /api/v1/batch/simulations/inventory-reconciliation-failure
POST /api/v1/batch/simulations/order-release-validation-failure
POST /api/v1/batch/simulations/shipment-sync-timeout
POST /api/v1/batch/simulations/low-stock-notification-partial-failure
POST /api/v1/batch/simulations/batch-failure-suite
```

Each simulation should create a batch run and step runs.

Failure simulations should be able to create exception and ticket.

---

## Simulation 1: Inventory Reconciliation Success

Endpoint:

```text
POST /api/v1/batch/simulations/inventory-reconciliation-success
```

Behavior:

- use job `BATCH-INV-RECON`
- all steps succeed
- final status `SUCCESS`
- records processed should be deterministic, for example 250
- no exception
- no AMS ticket unless explicitly requested, but default should be no ticket

Purpose:

Show normal batch behavior.

---

## Simulation 2: Inventory Reconciliation Failure

Endpoint:

```text
POST /api/v1/batch/simulations/inventory-reconciliation-failure
```

Request:

```json
{
  "create_exception": true,
  "create_ticket": true,
  "create_observability": true
}
```

Behavior:

- use job `BATCH-INV-RECON`
- extraction step succeeds
- validation step succeeds
- reconciliation step fails
- final status `FAILED`
- failure type `DATA_VALIDATION_ERROR`
- failure message example:

```text
Inventory reconciliation detected negative available quantity for one or more balances.
```

Support artifacts:

- create operational exception type `WORKFLOW_VALIDATION_FAILURE` or suitable existing type
- create AMS ticket if requested
- create monitoring alert if simple and useful
- create observability diagnostic case if `create_observability = true` and existing observability service can be reused safely

Purpose:

Show a batch failure that creates a support incident.

---

## Simulation 3: Order Release Validation Failure

Endpoint:

```text
POST /api/v1/batch/simulations/order-release-validation-failure
```

Behavior:

- use job `BATCH-ORDER-RELEASE`
- order selection step succeeds
- validation step fails
- final status `FAILED`
- failure type `BUSINESS_RULE_FAILURE`
- failure message example:

```text
Order release batch found orders that cannot be released because allocation prerequisites are incomplete.
```

Support artifacts:

- exception optional
- ticket optional
- diagnostic optional

Purpose:

Show business-rule batch failure, not infrastructure failure.

---

## Simulation 4: Shipment Sync Timeout

Endpoint:

```text
POST /api/v1/batch/simulations/shipment-sync-timeout
```

Behavior:

- use job `BATCH-SHIP-SYNC`
- extraction step succeeds
- external sync step times out
- final status `TIMEOUT`
- failure type `EXTERNAL_SYSTEM_ERROR`
- failure message example:

```text
Shipment status synchronization timed out while waiting for carrier status response.
```

Support artifacts:

- operational exception type `SHIPMENT_EXCEPTION` if consistent
- AMS ticket optional
- monitoring alert optional
- observability diagnostic optional

Purpose:

Show external dependency failure in batch process.

---

## Simulation 5: Low Stock Notification Partial Failure

Endpoint:

```text
POST /api/v1/batch/simulations/low-stock-notification-partial-failure
```

Behavior:

- use job `BATCH-LOW-STOCK`
- low-stock scan succeeds
- notification generation partially succeeds
- publish/notify step partially fails
- final status `PARTIAL_SUCCESS`
- failure type `PARTIAL_RECORD_FAILURE`
- deterministic record counts, for example:
  - processed 40
  - succeeded 32
  - failed 8

Support artifacts:

- exception optional
- AMS ticket optional

Purpose:

Show partial batch success and support impact.

---

## Simulation 6: Batch Failure Suite

Endpoint:

```text
POST /api/v1/batch/simulations/batch-failure-suite
```

Behavior:

- run deterministic set of batch scenarios
- include at least one success and at least two failures
- do not stop suite if one scenario fails
- return:

```text
runs_created
successful_runs
failed_runs
partial_runs
tickets_created
exceptions_created
diagnostics_created
summary
```

---

# Batch APIs

Create batch APIs.

Suggested files:

```text
backend/app/models/batch.py
backend/app/schemas/batch.py
backend/app/services/batch_service.py
backend/app/api/routes/batch.py
backend/app/db/seed_batch.py
```

You may organize differently if consistent with existing project style.

Use prefix:

```text
/api/v1/batch
```

Add:

```text
GET  /api/v1/batch/summary
GET  /api/v1/batch/jobs
GET  /api/v1/batch/jobs/{job_id}
GET  /api/v1/batch/runs
GET  /api/v1/batch/runs/{run_id}
GET  /api/v1/batch/runs/{run_id}/events
POST /api/v1/batch/runs/{run_id}/create-ticket
POST /api/v1/batch/runs/{run_id}/create-exception
POST /api/v1/batch/runs/{run_id}/create-diagnostic
POST /api/v1/batch/simulations/inventory-reconciliation-success
POST /api/v1/batch/simulations/inventory-reconciliation-failure
POST /api/v1/batch/simulations/order-release-validation-failure
POST /api/v1/batch/simulations/shipment-sync-timeout
POST /api/v1/batch/simulations/low-stock-notification-partial-failure
POST /api/v1/batch/simulations/batch-failure-suite
```

---

## Batch Summary

Endpoint:

```text
GET /api/v1/batch/summary
```

Return:

```json
{
  "batch_jobs": 5,
  "runs_total": 12,
  "runs_success": 4,
  "runs_failed": 5,
  "runs_partial": 2,
  "runs_timeout": 1,
  "open_batch_tickets": 3,
  "open_batch_exceptions": 2,
  "last_run_status": "FAILED"
}
```

Use actual database queries.

---

## Batch Job List

Endpoint:

```text
GET /api/v1/batch/jobs
```

Support optional filters:

```text
enabled
job_type
```

Return jobs with step count.

---

## Batch Job Detail

Endpoint:

```text
GET /api/v1/batch/jobs/{job_id}
```

Return:

```text
job header
configured steps
recent runs
```

Path parameter may be UUID or job_code if easier and consistent.

---

## Batch Run List

Endpoint:

```text
GET /api/v1/batch/runs
```

Support optional filters:

```text
job_code
status
failure_type
linked_ticket
```

Default sort:

```text
newest first
```

Limit default:

```text
100
```

---

## Batch Run Detail

Endpoint:

```text
GET /api/v1/batch/runs/{run_id}
```

Return:

```text
run header
job details
step runs
events
linked exception
linked ticket
linked alert
linked diagnostic case
```

Path parameter may be UUID or run_number if easier and consistent.

---

## Create Ticket from Batch Run

Endpoint:

```text
POST /api/v1/batch/runs/{run_id}/create-ticket
```

Rules:

- if an active ticket already exists for the batch run, return it
- create AMS ticket type `INCIDENT`
- ticket source should be `BATCH`
- source module should be `BATCH_OPERATIONS`
- business service should be `Warehouse & Fulfillment Operations`
- application name should be `Enterprise Operations Suite`
- priority should map from severity/failure type:
  - severe failed/timeout run → `P2`
  - partial success → `P3`
  - lower impact → `P4`
- description should include job, run number, failed step, failure type, failure message, records processed/succeeded/failed
- link `batch_runs.linked_ticket_id`
- create batch event `BATCH_TICKET_CREATED`

---

## Create Exception from Batch Run

Endpoint:

```text
POST /api/v1/batch/runs/{run_id}/create-exception
```

Rules:

- if linked exception already exists, return it
- create operational exception
- exception source module should be `BATCH_OPERATIONS`
- source entity type should be `BATCH_RUN`
- source entity id should be the batch run id
- severity should be based on batch status and failure type
- title should include job name and run number
- link `batch_runs.linked_exception_id`
- create batch event `BATCH_EXCEPTION_CREATED`

---

## Create Diagnostic from Batch Run

Endpoint:

```text
POST /api/v1/batch/runs/{run_id}/create-diagnostic
```

Rules:

- if existing linked diagnostic exists, return it
- create deterministic observability diagnostic case if observability service supports it safely
- create evidence records from:
  - batch run
  - failed step runs
  - batch events
  - linked monitoring alert if any
  - linked ticket if any
- probable cause should be deterministic and not AI-generated
- confidence should reflect evidence:
  - HIGH if failed step and failure type are clear
  - MEDIUM if only run failure is known
  - LOW otherwise
- link `batch_runs.linked_diagnostic_case_id`
- create batch event `BATCH_DIAGNOSTIC_CREATED`

If observability service integration is too complex, create a TODO and skip this endpoint only if necessary. Prefer implementing it if existing diagnostic service is reusable.

---

# Integration with Existing Support Modules

Use existing services where safe.

## Operational Exceptions

Batch failures should be able to create exceptions.

Suggested exception mapping:

```text
DATA_VALIDATION_ERROR      -> WORKFLOW_VALIDATION_FAILURE
BUSINESS_RULE_FAILURE      -> WORKFLOW_VALIDATION_FAILURE
EXTERNAL_SYSTEM_ERROR      -> SYSTEM_INTEGRATION_FAILURE
TIMEOUT                    -> SYSTEM_INTEGRATION_FAILURE
DATABASE_LATENCY           -> SYSTEM_INTEGRATION_FAILURE
PARTIAL_RECORD_FAILURE     -> WORKFLOW_VALIDATION_FAILURE
```

## AMS Tickets

Batch failures should be able to create AMS tickets.

Suggested ticket source:

```text
BATCH
```

Suggested source module:

```text
BATCH_OPERATIONS
```

## Monitoring

Where simple, batch failure simulations may create monitoring alerts using existing monitoring service.

Do not overcomplicate.

## Observability

Where simple, batch failure simulations may create diagnostic cases and evidence using existing observability services.

Do not overcomplicate.

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
Batch Jobs
Batch Runs
Batch Simulations
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
Health
About
```

---

## Required Frontend Routes

Add:

```text
/batch/jobs
/batch/jobs/:jobId
/batch/runs
/batch/runs/:runId
/batch/simulations
```

Existing routes must continue working.

---

## Batch Jobs Page

Route:

```text
/batch/jobs
```

Display:

- summary cards from `/api/v1/batch/summary`
- batch job table

Job table columns:

```text
job code
name
job type
enabled
SLA minutes
step count
recent status
```

Job code should link to job detail page.

---

## Batch Job Detail Page

Route:

```text
/batch/jobs/:jobId
```

Display:

- job header
- configured steps
- recent runs

Step table:

```text
step order
step code
step name
step type
expected duration
enabled
```

Recent run table:

```text
run number
status
duration
records processed
failed records
started at
```

---

## Batch Runs Page

Route:

```text
/batch/runs
```

Display:

- batch run table

Columns:

```text
run number
job
status
scenario
duration
records processed
records failed
failure type
linked exception
linked ticket
linked diagnostic
started at
```

Use chips for status and failure type.

Run number should link to run detail page.

---

## Batch Run Detail Page

Route:

```text
/batch/runs/:runId
```

Display:

- run header
- job information
- status
- failure message
- records processed/succeeded/failed
- linked exception
- linked ticket
- linked alert
- linked diagnostic case
- step runs
- event timeline

Actions:

```text
Create Exception
Create Ticket
Create Diagnostic
```

Only show actions where relevant and safe.

---

## Batch Simulations Page

Route:

```text
/batch/simulations
```

Display simulation cards:

```text
Inventory Reconciliation Success
Inventory Reconciliation Failure
Order Release Validation Failure
Shipment Sync Timeout
Low Stock Notification Partial Failure
Batch Failure Suite
```

Each card should include:

- description
- button to run simulation
- toggles where supported:
  - create exception
  - create ticket
  - create observability
- result panel showing:
  - run number
  - status
  - exception link if created
  - ticket link if created
  - diagnostic link if created

---

# Frontend API Client

Create or extend typed API client.

Suggested file:

```text
frontend/src/services/batchApi.ts
```

Use `VITE_API_BASE_URL`.

Use TanStack Query for data loading.

Use mutations for simulations and actions.

Show loading and error states.

---

# Backend Tests

Add tests covering:

1. Existing health/version tests still pass
2. Existing warehouse read tests still pass
3. Existing warehouse workflow tests still pass
4. Existing operations/AMS tests still pass
5. Existing synthetic user tests still pass
6. Existing monitoring tests still pass
7. Existing observability tests still pass
8. Batch seed is idempotent
9. List batch jobs
10. Get batch job detail
11. Run inventory reconciliation success
12. Run inventory reconciliation failure
13. Failure run creates step failure
14. Failure run creates exception when requested
15. Failure run creates AMS ticket when requested
16. Duplicate ticket from same batch run is prevented
17. Order release validation failure works
18. Shipment sync timeout works
19. Low stock partial failure works
20. Batch failure suite runs
21. Batch run list endpoint works
22. Batch run detail includes steps and events
23. Create exception from run endpoint works
24. Create ticket from run endpoint works
25. Create diagnostic from run endpoint works, if implemented
26. Batch summary endpoint works

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

- Prompt 08 batch issue scenario summary
- batch job catalog
- batch run history
- batch step runs
- batch failure simulations
- batch-to-exception flow
- batch-to-ticket flow
- batch-to-diagnostic flow if implemented
- new APIs
- new frontend routes
- seed commands
- validation commands
- backend port `8050`
- frontend port `4001`
- deferred future items:
  - real scheduling
  - async workers
  - batch retry orchestration
  - external file transfer
  - AI-native support agents

Update `ARCHITECTURE.md` with:

- batch operations module
- batch job/run/step model
- batch failure support flow
- integration with operational exceptions
- integration with AMS tickets
- integration with observability diagnostics if implemented
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
pytest
```

Then validate live backend:

```bash
curl -sS http://localhost:8050/health | jq .
curl -sS http://localhost:8050/api/v1/batch/summary | jq .
curl -sS http://localhost:8050/api/v1/batch/jobs | jq .
curl -sS http://localhost:8050/api/v1/batch/runs | jq .
curl -sS -X POST http://localhost:8050/api/v1/batch/simulations/inventory-reconciliation-failure \
  -H "Content-Type: application/json" \
  -d '{"create_exception": true, "create_ticket": true, "create_observability": true}' | jq .
curl -sS http://localhost:8050/api/v1/batch/runs | jq .
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
http://localhost:4001/batch/jobs
http://localhost:4001/batch/runs
http://localhost:4001/batch/simulations
```

Manual UI validation:

```text
Open Batch Simulations
Run Inventory Reconciliation Success
Confirm successful batch run exists
Run Inventory Reconciliation Failure with exception/ticket/observability enabled
Open Batch Runs
Open failed batch run detail
Confirm failed step and event timeline are visible
Confirm linked exception exists if created
Confirm linked AMS ticket exists if created
Confirm linked diagnostic exists if created
Open AMS Tickets
Confirm batch-created ticket exists
Open Operations Exceptions
Confirm batch-created exception exists
Open Observability Diagnostics if diagnostic was created
Confirm batch diagnostic evidence is visible
```

---

# Definition of Done

Prompt 08 is complete only when:

- migration exists
- `batch_jobs` exists
- `batch_job_steps` exists
- `batch_runs` exists
- `batch_step_runs` exists
- `batch_run_events` exists
- batch seed exists and is idempotent
- batch summary API works
- batch job list/detail APIs work
- batch run list/detail APIs work
- batch run events API works
- inventory reconciliation success simulation works
- inventory reconciliation failure simulation works
- order release validation failure simulation works
- shipment sync timeout simulation works
- low stock partial failure simulation works
- batch failure suite works
- batch failure can create operational exception
- batch failure can create AMS ticket
- duplicate ticket from same batch run is prevented
- batch diagnostic creation works if implemented
- existing warehouse APIs still work
- existing operations/AMS APIs still work
- existing synthetic user APIs still work
- existing monitoring APIs still work
- existing observability APIs still work
- frontend batch jobs page works
- frontend batch job detail page works
- frontend batch runs page works
- frontend batch run detail page works
- frontend batch simulations page works
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
4. Backend batch APIs added
5. Backend batch simulation APIs added
6. Frontend routes added
7. Seed command and result
8. Backend validation results
9. Frontend validation results
10. Manual batch failure validation result
11. Confirmation that infrastructure files were not modified
12. Any TODOs
13. Recommended Git commit message

Recommended commit message:

```text
feat: add batch jobs and batch failure scenarios
```

Do not proceed beyond this prompt.