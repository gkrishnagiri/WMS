# Enterprise Operations Suite (EOS)

Enterprise Operations Suite is the demo application for the AI-Native AMS
Research Platform. Phase 1 established the reusable backend and frontend
foundation. Prompts 04 through 06 added deterministic supportability sources,
and Prompt 07 added application-level observability evidence for support
diagnosis. Prompt 08 adds deterministic batch operations and failure support
flows.

## Current phase

Prompt 08 — Batch Jobs and Batch Failure Scenarios.

The application includes a FastAPI API, React/MUI application shell, request
IDs, structured logging, configuration, PostgreSQL and Redis connectivity
checks, and the Warehouse & Fulfillment domain model. Prompt 03 adds the
controlled path from customer order through allocation, pick and pack task
completion, shipment confirmation, inventory reduction, and an auditable
inventory transaction ledger. Allocation and shipment operations are atomic.
Prompt 04 adds operational exception detection, deterministic failure
simulations, AMS ticket creation, ticket events, and a controlled ticket
lifecycle.
Prompt 05 adds six deterministic synthetic users, five cataloged journeys,
auditable journey runs, user-reported functional issues, and ticket creation
from user reports.
Prompt 06 adds a deterministic monitored-component catalog, alert rules,
deduplicated noisy alerts, manual triage cases, and monitoring-origin AMS
tickets. It deliberately provides symptoms without traces, logs, or automated
root-cause diagnosis.
Prompt 07 adds simulated traces, spans, structured logs, metric samples, and
evidence-backed diagnostic cases without external observability export.
Prompt 08 adds five batch job definitions, ordered steps, synchronous run
history, failure scenarios, and deterministic links to exceptions, AMS tickets,
and diagnostic cases.

## Infrastructure status

The existing Phase 0 baseline remains the source of truth and is unchanged:

- PostgreSQL on host port `15432`
- Redis on host port `6379`
- OpenTelemetry Collector, Prometheus, Loki, and Grafana
- Existing `docker-compose.yml`, `observability/`, `docs/`, `data/`, and
  `load-tests/`

Tempo and application tracing are deferred.

## Repository structure

```text
backend/       FastAPI application, SQLAlchemy, Alembic, and pytest tests
frontend/      React, TypeScript, Vite, React Router, TanStack Query, MUI
observability/ Phase 0 observability configuration (unchanged)
docs/          Phase 0 and project documentation (unchanged)
```

## Backend setup

```bash
cd backend
cp .env.example .env       # optional; defaults are local-development safe
./start_backend.sh
```

The API is available at http://localhost:8050. Useful endpoints are /,
/health, /version, and the Warehouse & Fulfillment API under
/api/v1/warehouse. The health endpoint returns HTTP 503 when
PostgreSQL or Redis is unavailable.

Warehouse API endpoints:

- GET /api/v1/warehouse/summary
- GET /api/v1/warehouse/warehouses
- GET /api/v1/warehouse/warehouses/{warehouse_id}
- GET /api/v1/warehouse/items
- GET /api/v1/warehouse/inventory
- GET /api/v1/warehouse/orders
- GET /api/v1/warehouse/tasks
- GET /api/v1/warehouse/shipments
- POST /api/v1/warehouse/orders
- GET /api/v1/warehouse/orders/{order_id}
- POST /api/v1/warehouse/orders/{order_id}/allocate
- POST /api/v1/warehouse/orders/{order_id}/release-tasks
- POST /api/v1/warehouse/tasks/{task_id}/start
- POST /api/v1/warehouse/tasks/{task_id}/complete
- POST /api/v1/warehouse/orders/{order_id}/ship
- GET /api/v1/warehouse/orders/{order_id}/events
- GET /api/v1/warehouse/inventory-transactions

Operations and exception APIs:

- GET /api/v1/operations/exceptions
- GET /api/v1/operations/exceptions/{exception_id}
- POST /api/v1/operations/exceptions/{exception_id}/acknowledge
- POST /api/v1/operations/exceptions/{exception_id}/resolve
- POST /api/v1/operations/detect/low-stock
- POST /api/v1/operations/detect/order-stuck
- POST /api/v1/operations/simulations/low-stock
- POST /api/v1/operations/simulations/task-blocked
- POST /api/v1/operations/simulations/shipment-exception
- POST /api/v1/operations/simulations/order-stuck

AMS APIs:

- GET /api/v1/ams/summary
- GET /api/v1/ams/tickets
- POST /api/v1/ams/tickets
- GET /api/v1/ams/tickets/{ticket_id}
- POST /api/v1/ams/tickets/from-exception/{exception_id}
- POST /api/v1/ams/tickets/{ticket_id}/acknowledge
- POST /api/v1/ams/tickets/{ticket_id}/start-work
- POST /api/v1/ams/tickets/{ticket_id}/resolve
- POST /api/v1/ams/tickets/{ticket_id}/close
- GET /api/v1/ams/tickets/{ticket_id}/events

Synthetic user and journey APIs:

- GET /api/v1/synthetic-users/users
- GET /api/v1/synthetic-users/journeys
- GET /api/v1/synthetic-users/journeys/{journey_code}
- POST /api/v1/synthetic-users/journeys/{journey_code}/run
- POST /api/v1/synthetic-users/run-suite
- GET /api/v1/synthetic-users/runs
- GET /api/v1/synthetic-users/runs/{run_id}

User report APIs:

- GET /api/v1/ams/user-reports
- POST /api/v1/ams/user-reports
- GET /api/v1/ams/user-reports/{report_id}
- POST /api/v1/ams/user-reports/{report_id}/create-ticket
- POST /api/v1/ams/user-reports/{report_id}/acknowledge
- POST /api/v1/ams/user-reports/{report_id}/resolve

Monitoring APIs:

- GET /api/v1/monitoring/summary
- GET /api/v1/monitoring/components
- GET /api/v1/monitoring/rules
- GET /api/v1/monitoring/alerts
- GET /api/v1/monitoring/alerts/{alert_id}
- POST /api/v1/monitoring/alerts/{alert_id}/acknowledge
- POST /api/v1/monitoring/alerts/{alert_id}/suppress
- POST /api/v1/monitoring/alerts/{alert_id}/resolve
- POST /api/v1/monitoring/alerts/{alert_id}/create-ticket
- GET /api/v1/monitoring/alerts/{alert_id}/events
- GET/POST /api/v1/monitoring/triage-cases
- GET /api/v1/monitoring/triage-cases/{case_id}
- POST /api/v1/monitoring/triage-cases/{case_id}/add-alerts
- POST /api/v1/monitoring/triage-cases/{case_id}/start-investigation
- POST /api/v1/monitoring/triage-cases/{case_id}/resolve
- POST /api/v1/monitoring/triage-cases/{case_id}/create-ticket
- POST /api/v1/monitoring/simulations/api-latency-cascade
- POST /api/v1/monitoring/simulations/database-degradation
- POST /api/v1/monitoring/simulations/redis-flapping
- POST /api/v1/monitoring/simulations/frontend-error-burst
- POST /api/v1/monitoring/simulations/warehouse-workflow-noise
- POST /api/v1/monitoring/simulations/noisy-alert-storm

After applying the Alembic migrations, load deterministic demo data with:

    cd backend
    source .venv/bin/activate
    alembic upgrade head
    python -m app.db.seed_warehouse
    python -m app.db.seed_synthetic_users
    python -m app.db.seed_monitoring

Supported backend variables are documented in `backend/.env.example`,
including `APP_*`, `BACKEND_CORS_ORIGINS`, `DATABASE_*`, `REDIS_*`,
`LOG_LEVEL`, and `REQUEST_ID_HEADER`.

## Frontend setup

```bash
cd frontend
cp .env.example .env       # optional
./start_frontend.sh
```

The frontend is served at http://localhost:4001. Its API URL and branding
variables are documented in `frontend/.env.example`.

Warehouse frontend routes:

- /warehouse
- /warehouse/inventory
- /warehouse/orders
- /warehouse/orders/new
- /warehouse/orders/:orderId
- /warehouse/tasks
- /warehouse/shipments
- /warehouse/inventory-transactions
- /operations/exceptions
- /operations/simulations
- /ams/tickets
- /ams/tickets/:ticketId
- /synthetic-users/journeys
- /synthetic-users/runs
- /ams/user-reports
- /ams/user-reports/new
- /ams/user-reports/:reportId
- /monitoring/alerts
- /monitoring/simulations
- /monitoring/triage
- /monitoring/triage/:caseId

The existing /, /health, and /about routes remain available.

## Validation

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed_warehouse
python -m app.db.seed_synthetic_users
python -m app.db.seed_monitoring
pytest

cd ../frontend
npm install
npm run build
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the current foundation boundaries
and deferred work.

## Prompt 03 workflow

```text
Customer Order → Allocation → Fulfillment Task Release → Pick → Pack
→ Shipment → Inventory Reduction → Inventory Transaction Ledger
```

The workflow tables are `wf_allocations`, `wf_inventory_transactions`, and
`wf_order_events`. The frontend provides order creation, order detail actions,
task start/complete actions, and the transaction ledger at port `4001`; the
backend remains on port `8050`.

## Prompt 04 supportability layer

The `ops_exceptions`, `ams_tickets`, and `ams_ticket_events` tables support:

```text
Warehouse degradation or simulation → Operational exception → AMS incident →
Acknowledge → Start work → Resolve → Close
```

Low-stock and order-stuck rules can be run through detection endpoints. The
simulation page can deterministically reduce inventory, block a fulfillment
task, mark a shipment as an exception, or place an order into a stale active
status. Active exception/ticket creation is idempotent for the same source.
The backend remains on port `8050` and the frontend remains on port `4001`.

## Prompt 05 user-driven failure layer

The `synthetic_users`, `synthetic_journeys`, `synthetic_journey_runs`, and
`ams_user_reports` tables support this deterministic flow:

```text
Synthetic user journey → Success or functional failure → User report →
AMS incident → Existing AMS lifecycle
```

The successful fulfillment, insufficient-stock, pack-before-pick,
ship-before-pack, and manual functional issue journeys are backend-driven;
they do not use browser automation or monitoring. Failed journeys can create
user reports and optionally link an idempotent AMS ticket. The seed command
is safe to run repeatedly and creates six users and five journeys.

## Prompt 05 validation

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed_warehouse
python -m app.db.seed_synthetic_users
pytest

cd ../frontend
npm run build
```

Deferred capabilities include real scheduling, async workers, batch retry
orchestration, external file transfer, returns, replenishment, wave planning,
carrier integrations, background jobs, adjustment approvals, external ITSM
connectors, notifications, ticket analytics, anomaly detection, root-cause
inference, LLM summaries, agents, and autonomous remediation.

## Prompt 06 monitoring alert-noise layer

The `mon_components`, `mon_alert_rules`, `mon_alerts`, `mon_alert_events`,
`mon_triage_cases`, and `mon_triage_case_alerts` tables support:

```text
Monitoring symptom → Repeated/noisy alerts → Manual triage case → AMS incident
```

The six monitoring simulations are application-level demo APIs, not
Prometheus scraping. They cover API latency cascades, database degradation,
Redis flapping, frontend error bursts, warehouse workflow noise, and a
combined alert storm. Alert lifecycle actions include acknowledgement,
suppression, resolution, and ticket creation. Triage cases preserve
human-entered analysis notes and do not infer a root cause.

## Prompt 06 validation

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed_warehouse
python -m app.db.seed_synthetic_users
python -m app.db.seed_monitoring
pytest

cd ../frontend
npm run build
```

The backend remains on port `8050` and the frontend remains on port `4001`.
Real OpenTelemetry export, Tempo, Loki, Prometheus scraping, Grafana
dashboards, real scheduling, async workers, and AI-native support agents
remain deferred.

## Prompt 07 observability-enabled diagnosis

The `obs_traces`, `obs_spans`, `obs_log_events`, `obs_metric_samples`,
`obs_diagnostic_cases`, and `obs_diagnostic_evidence` tables support:

```text
Monitoring symptom → Trace/span/log/metric evidence → Diagnostic case → AMS ticket
```

The database-degradation, Redis cache failure, allocation failure, shipment
integration failure, and combined demo-suite simulations generate deterministic
evidence. Diagnostic confidence is rule-based: high confidence requires
multiple matching evidence sources, while incomplete evidence remains low or
unknown. Allocation diagnosis explicitly distinguishes insufficient inventory
as a business-rule rejection from a technical outage.

Observability APIs include summary, trace list/detail, log events, metric
samples, diagnostic case list/detail, diagnosis creation from alerts/triage
cases/tickets, diagnostic ticket linking, and diagnostic resolution.

Simulation APIs:

- POST /api/v1/observability/simulations/database-degradation
- POST /api/v1/observability/simulations/redis-cache-failure
- POST /api/v1/observability/simulations/allocation-failure
- POST /api/v1/observability/simulations/shipment-integration-failure
- POST /api/v1/observability/simulations/observability-demo-suite

Frontend routes include `/observability`, `/observability/simulations`,
`/observability/traces`, `/observability/traces/:traceId`,
`/observability/logs`, `/observability/metrics`,
`/observability/diagnostics`, and `/observability/diagnostics/:caseId`.

## Prompt 07 validation

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed_warehouse
python -m app.db.seed_synthetic_users
python -m app.db.seed_monitoring
pytest

cd ../frontend
npm run build
```

The backend remains on port `8050` and the frontend remains on port `4001`.
Real OpenTelemetry export, Tempo, Loki, Prometheus scraping, Grafana
dashboards, AI-native diagnosis, autonomous remediation, and real scheduling
are deferred.

## Prompt 08 batch operations and failure scenarios

The `batch_jobs`, `batch_job_steps`, `batch_runs`, `batch_step_runs`, and
`batch_run_events` tables support manually triggered deterministic batch
processing:

```text
Batch job → Ordered step runs → Success/failure/timeout/partial result
          → Operational exception → BATCH AMS ticket → Optional diagnostic case
```

The batch catalog contains inventory reconciliation, order release, shipment
status synchronization, low-stock notification, and inventory snapshot jobs.
The simulations cover normal reconciliation, reconciliation validation
failure, order-release business-rule failure, shipment synchronization
timeout, low-stock notification partial failure, and a combined failure suite.
Runs are synchronous API/UI simulations; no scheduler, worker, queue, or
external file transfer is introduced.

Batch APIs include job and run summaries, job/run detail, run events, support
artifact creation, and the six `/api/v1/batch/simulations/*` endpoints.
Batch-origin tickets use source `BATCH` and source module
`BATCH_OPERATIONS`. When requested, failures also create deterministic
`BATCH_OPERATIONS` exceptions and reusable observability diagnostic evidence.

Batch frontend routes:

- `/batch/jobs`
- `/batch/jobs/:jobId`
- `/batch/runs`
- `/batch/runs/:runId`
- `/batch/simulations`

## Prompt 08 validation

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed_warehouse
python -m app.db.seed_synthetic_users
python -m app.db.seed_monitoring
python -m app.db.seed_batch
pytest

cd ../frontend
npm run build
```

The backend remains on port `8050` and the frontend remains on port `4001`.
Real scheduling, async batch workers, retry orchestration, external file
transfer, and AI-native support agents remain deferred.
