# Enterprise Operations Suite (EOS)

Enterprise Operations Suite is the demo application for the AI-Native AMS
Research Platform. Phase 1 established the reusable backend and frontend
foundation. Prompts 04 through 06 added deterministic supportability sources,
and Prompt 07 added application-level observability evidence for support
diagnosis. Prompt 08 adds deterministic batch operations and failure support
flows. Prompt 09 adds a governed deterministic support engineer copilot.

## Current phase

Prompt 09 — AI-Native Support Engineer Copilot Foundation.

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
Prompt 09 adds copilot sessions, context snapshots, deterministic
recommendations, human-approved action plans, safe-action catalog data, and
reviewable work-note, customer-update, and investigation-checklist drafts.

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
python -m app.db.seed_batch
python -m app.db.seed_copilot
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

## Prompt 09 governed support copilot

The `copilot_sessions`, `copilot_context_snapshots`,
`copilot_recommendations`, `copilot_action_plans`, `copilot_messages`,
`copilot_safe_actions`, and `copilot_action_events` tables provide a governed
support workbench across existing EOS artifacts:

```text
Ticket/exception/alert/triage/diagnostic/batch/user report
    → deterministic context snapshot
    → recommendations and human-review action plan
    → work-note, customer-update, or checklist draft
```

The context builder aggregates currently available ticket, exception, user
report, monitoring, observability, and batch data without secrets or external
calls. Recommendation generation is rules-based and repeatable. Accepting or
dismissing a recommendation records an audit event only; it does not resolve a
ticket, close an alert, rerun a batch, change warehouse data, or perform any
other underlying action.

Seed the safe-action catalog idempotently with:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_copilot
```

Copilot APIs include summary, safe actions, session list/create/detail,
context building, recommendation generation and review, action-plan
generation, deterministic draft generation, session closure, and the
convenience `POST /api/v1/copilot/analyze` flow.

Copilot frontend routes:

- `/copilot`
- `/copilot/sessions`
- `/copilot/sessions/:sessionId`
- `/copilot/analyze`

## Prompt 09 validation

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed_warehouse
python -m app.db.seed_synthetic_users
python -m app.db.seed_monitoring
python -m app.db.seed_batch
python -m app.db.seed_copilot
pytest

cd ../frontend
npm run build
```

The backend remains on port `8050` and the frontend remains on port `4001`.
External LLMs, OpenAI/Anthropic SDKs, LangGraph, LiteLLM, RAG, embeddings,
vector stores, autonomous remediation, notification sending, and ServiceNow
integration are explicitly deferred.

## Prompt 10 governed AI configuration

The governed AI configuration layer adds provider and model catalogs, versioned
prompt templates, safety policies/rules, invocation audit logs, daily usage
aggregates, and guardrail events. The only executable provider is the local,
deterministic `MOCK_GOVERNED` provider with model
`MOCK-SUPPORT-COPILOT-001`; no external network or model SDK is used.

The request flow is:

```text
Task request → provider/model/template selection → safety evaluation
             → deterministic mock response → invocation audit + usage aggregate
```

The seed is idempotent:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_ai_config
```

It creates one enabled mock provider, disabled non-mock placeholders, one
enabled mock model, six prompt templates, one governance policy, and seven
deterministic safety rules. Rules block obvious API-key/password material,
destructive ticket/data requests, and external-message requests; warnings are
recorded without blocking the mock invocation.

AI configuration APIs are available under `/api/v1/ai-config` for summaries,
providers, models, prompt templates, safety policies/rules, test invocations,
invocation audit records, usage aggregates, guardrail events, and safety-only
checks. The frontend routes are:

- `/ai-config`
- `/ai-config/providers`
- `/ai-config/prompts`
- `/ai-config/safety`
- `/ai-config/invocations`
- `/ai-config/usage`
- `/ai-config/test`

## Prompt 10 validation

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

cd ../frontend
npm run build
```

The backend remains on port `8050` and the frontend remains on port `4001`.
Real external LLM calls, OpenAI/Azure/Anthropic SDKs, LangGraph, LiteLLM,
RAG, embeddings/vector stores, autonomous remediation, tool execution,
production secret storage, and ServiceNow integration are deferred.

## Prompt 11 governed AI copilot draft integration

Copilot sessions can now optionally use the Prompt 10 governed provider
gateway for four draft types:

```text
Context summary → Work note draft → Customer update draft → Investigation checklist
```

The existing deterministic Prompt 09 generation remains available in parallel.
Governed drafts send only the summarized context snapshot, use the enabled
`MOCK-SUPPORT-COPILOT-001` model, evaluate safety rules first, and persist the
AI invocation number, safety status, token estimate, and generation mode on the
copilot message. Blocked requests create an audited `GOVERNED_AI_BLOCKED`
message and never produce a provider response.

New copilot endpoints are:

- `POST /api/v1/copilot/sessions/{session_id}/generate-governed-context-summary`
- `POST /api/v1/copilot/sessions/{session_id}/generate-governed-work-note`
- `POST /api/v1/copilot/sessions/{session_id}/generate-governed-customer-update`
- `POST /api/v1/copilot/sessions/{session_id}/generate-governed-investigation-checklist`
- `GET /api/v1/copilot/sessions/{session_id}/ai-invocations`

The copilot session detail page now provides governed draft controls and an AI
invocation audit table. Generated content is always a reviewable draft; it is
not applied to tickets, alerts, diagnostics, warehouse data, or external
communications.

## Prompt 11 validation

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

cd ../frontend
npm run build
```

The backend remains on port `8050` and the frontend remains on port `4001`.
Real external LLM calls, streaming, LangGraph, LiteLLM, RAG,
embeddings/vector stores, autonomous remediation, external notifications,
ServiceNow integration, runtime observability instrumentation, and local
observability-stack expansion remain deferred.

## Prompt 12 runtime observability instrumentation

Runtime observability now captures actual EOS backend request telemetry into the
existing Prompt 07 PostgreSQL observability tables. This is distinct from the
deterministic scenario evidence: captured API requests create runtime traces,
HTTP spans, structured request logs, latency/request/error metric samples, and
correlation metadata.

The runtime flow is:

```text
HTTP request → request/correlation/runtime trace IDs → API execution
            → obs_traces + obs_spans + obs_log_events + obs_metric_samples
            → response correlation headers
```

Incoming `X-Request-ID`, `X-Correlation-ID`, and `traceparent` values are read
when present. Missing IDs are generated, stored on request state, and returned
as `X-Request-ID`, `X-Correlation-ID`, and `X-EOS-Runtime-Trace-ID`. Request
bodies, authorization headers, cookies, credentials, and environment values
are not captured. Documentation, OpenAPI, static, favicon, and health paths
are excluded by default from persistence.

The backend health probe at
`POST /api/v1/runtime-observability/probes/backend-health` performs actual
PostgreSQL and Redis connectivity checks without changing business data. It
persists a probe trace with backend, PostgreSQL, and Redis spans, structured
probe logs, and probe latency metrics.

Runtime APIs are available under `/api/v1/runtime-observability`:

- `GET /summary`
- `GET /traces`
- `GET /traces/{trace_id}`
- `GET /logs`
- `GET /metrics`
- `POST /probes/backend-health`

Runtime frontend routes are:

- `/observability/runtime`
- `/observability/runtime/traces`
- `/observability/runtime/traces/:traceId`

The backend remains on port `8050` and the frontend remains on port `4001`.

## Prompt 12 validation

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

cd ../frontend
npm run build
```

OpenTelemetry SDK/export, Tempo, Loki, Grafana dashboards, collector
trace/log pipelines, distributed tracing across services, browser telemetry,
Prometheus scraping changes, external observability SaaS integration, and AI
diagnosis changes remain deferred to later phases.

## Prompt 13 local observability stack expansion

Prompt 13 adds a local external observability stack alongside the Prompt 12
PostgreSQL runtime telemetry. EOS exports OpenTelemetry traces, logs, and
metrics to the Collector, which routes them to Tempo, Loki, and Prometheus;
Grafana provisions those data sources and two demo dashboards. Tempo and Loki
use local Docker volumes and are not external SaaS services.

The backend uses the official OpenTelemetry Python API/SDK and OTLP exporters.
Instrumentation is opt-in with `OTEL_ENABLED=true`, remains safe when the
Collector is unavailable, and adds `X-EOS-OTEL-Trace-ID` while preserving all
Prompt 12 request/correlation headers. A lightweight application middleware
creates request spans and metrics; structured application logs are bridged to
OTLP when the installed SDK supports it. No request bodies, credentials,
authorization headers, or cookies are exported.

Start the local stack with:

```bash
docker compose config
docker compose up -d
docker compose ps
```

Start the backend with local export enabled without editing `backend/.env`:

```bash
cd backend
source .venv/bin/activate
OTEL_ENABLED=true OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317 ./start_backend.sh
```

Stack APIs are available under `/api/v1/observability-stack`:

- `GET /summary`, `GET /health`, and `GET /config`
- `POST /test-span`, `POST /test-log`, `POST /test-metric`, and `POST /test-all`

Runtime stack frontend routes are:

- `/observability/stack`
- `/observability/stack/health`
- `/observability/stack/test`
- `/observability/dashboards`

The local service ports remain: backend `8050`, frontend `4001`, PostgreSQL
`15432`, Redis `6379`, Prometheus `9090`, Grafana `3001`, Collector OTLP
`4317`/`4318`, Tempo `3200`, and Loki `3100`.

## Prompt 13 validation

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

cd ../frontend
npm run build
```

Production sampling policy, remote SaaS export, browser RUM, multi-service
distributed tracing, Prometheus alert rules, Grafana alerting, ServiceNow,
AI-driven remediation, and cloud integrations remain deferred.

## Prompt 14 experience segregation

Prompt 14 adds frontend experience segregation without splitting the shared
FastAPI backend. The same React/Vite codebase is launched with
`VITE_EOS_EXPERIENCE`, so the integrated full demo remains available while
specialized browser windows expose focused navigation and landing pages:

| Experience | URL | Purpose |
| --- | --- | --- |
| Full | `http://localhost:4001` | Integrated EOS demo UI |
| Business | `http://localhost:4011` | Warehouse and fulfillment application |
| Operations | `http://localhost:4012` | AMS and support operations console |
| Simulation | `http://localhost:4013` | Synthetic users and fault-injection lab |
| Observability | `http://localhost:4014` | Runtime telemetry and local stack control plane |
| Agentic | `http://localhost:4015` | Copilot and governed AI support console |

Experience navigation is centralized in `frontend/src/config/navigation.ts`
and mode metadata is in `frontend/src/config/experience.ts`. Direct access to
a route owned by another experience shows a friendly experience-boundary page;
this is demo navigation segregation, not authentication or authorization.

Start a mode with the provided scripts:

```bash
cd frontend
./start_full_frontend.sh          # 4001
./start_business_frontend.sh      # 4011
./start_operations_frontend.sh    # 4012
./start_simulation_frontend.sh    # 4013
./start_observability_frontend.sh # 4014
./start_agentic_frontend.sh       # 4015
```

Each script sets `VITE_EOS_EXPERIENCE`, the appropriate frontend port, and the
corresponding local API boundary. The full mode uses `http://localhost:8050`;
specialized modes use the Prompt 15 BFFs on `8061` through `8065`.

Experience-specific route groups are:

- Business: `/warehouse`, `/warehouse/inventory`, `/warehouse/orders`,
  `/warehouse/tasks`, `/warehouse/shipments`, `/warehouse/inventory-transactions`,
  `/health`, and `/about`
- Operations: `/operations/exceptions`, `/ams/tickets`, `/ams/user-reports`,
  `/monitoring/alerts`, `/monitoring/triage`, `/batch/runs`,
  `/observability/diagnostics`, and `/copilot/sessions`
- Simulation: `/synthetic-users/*`, `/batch/jobs`, `/batch/runs`,
  `/batch/simulations`, `/monitoring/simulations`,
  `/observability/simulations`, and `/observability/stack/test`
- Observability: `/observability/*`, including runtime views, stack health,
  tests, dashboards, traces, logs, metrics, and diagnostics
- Agentic: `/copilot/*`, `/ai-config/*`, and the future `/agentic` placeholder

Prompt 14 deliberately did not split backend services. Prompt 15 adds local
FastAPI BFF runtime boundaries without creating independent containers or
repositories. Future Azure
deployment may use Azure Monitor/Application Insights/Log Analytics (with
Managed Grafana if desired), or the open-source Grafana/Prometheus/Tempo/Loki/
OpenTelemetry stack. Open-source components may avoid license fees, but Azure
compute, storage, networking, and managed services still have infrastructure
costs. No final production choice is made here.

## Prompt 14 validation

```bash
cd frontend
npm install
npm run build
```

The mode scripts can then be opened at ports `4001`, `4011`, `4012`, `4013`,
`4014`, and `4015`. Existing backend APIs, the full UI, and the Prompt 13
observability stack remain unchanged. Backend boundary/BFF segregation,
authentication, authorization, and production deployment topology are
deferred.

## Prompt 15 backend boundary and BFF segregation

Prompt 15 preserves the full platform backend at `http://localhost:8050` and
adds five FastAPI entrypoints in the same backend codebase:

| Experience | BFF URL | Frontend URL |
| --- | --- | --- |
| Business | `http://localhost:8061` | `http://localhost:4011` |
| Operations | `http://localhost:8062` | `http://localhost:4012` |
| Simulation Lab | `http://localhost:8063` | `http://localhost:4013` |
| Observability Control | `http://localhost:8064` | `http://localhost:4014` |
| Agentic Support | `http://localhost:8065` | `http://localhost:4015` |

The BFFs use `backend/app/bff/app_factory.py` and a shared experience
registry. They reuse existing models, database sessions, middleware, and
routers but expose only the route groups relevant to each experience. Every
BFF provides `/health` and `/api/v1/platform/experiences`,
`/api/v1/platform/current-experience`, and `/api/v1/platform/topology`.
Facade summaries are available at `/api/v1/business/summary`,
`/api/v1/operations-console/summary`, `/api/v1/simulation-lab/summary`,
`/api/v1/observability-control/summary`, and
`/api/v1/agentic-console/summary`.

Start the full backend or a BFF with the executable scripts in `backend/`:

```bash
./start_full_backend.sh       # 8050
./start_business_bff.sh       # 8061
./start_operations_bff.sh     # 8062
./start_simulation_bff.sh     # 8063
./start_observability_bff.sh  # 8064
./start_agentic_bff.sh        # 8065
```

The full backend retains all routes. BFFs are local API boundaries, not
security controls: authentication and authorization are intentionally absent.
The database and codebase remain shared, and no Docker Compose changes or
additional containers are required. With `OTEL_ENABLED=true`, BFF scripts use
distinct service names (`eos-business-bff`, `eos-operations-bff`,
`eos-simulation-bff`, `eos-observability-bff`, and `eos-agentic-bff`).

Prompt 15 validation includes the existing seed/test/build commands plus live
health, platform metadata, facade, disallowed-route, and CORS preflight checks
for each frontend/BFF pair. ServiceNow placement for the Operations Console,
agent orchestration placement, physical deployment separation, and production
network policy remain future work.

## Prompt 16 demo stack orchestration and control panel

Prompt 16 adds PID-owned local orchestration for the Docker infrastructure,
full backend, five BFFs, and six frontend experiences. The scripts are safe to
run from any directory and keep runtime metadata and logs outside the
repository:

```text
/tmp/eos-demo/*.pid
/tmp/eos-demo/logs/*.log
```

Use these commands from the project root:

```bash
./scripts/start-demo-stack.sh
./scripts/status-demo-stack.sh
./scripts/validate-demo-stack.sh
./scripts/stop-demo-stack.sh
```

`stop-demo-stack.sh` stops only processes with matching PID records created by
the orchestration scripts. It leaves Docker infrastructure running by
default; use `./scripts/stop-demo-stack.sh --with-infra` to also run
`docker compose down`. Infrastructure-only controls are available through
`start-infra.sh` and `stop-infra.sh` (`--volumes` is opt-in). Existing healthy
processes on expected ports are reused, while occupied ports are reported as
conflicts rather than being killed.

The full UI includes a read-only control panel at
`http://localhost:4001/demo-control`. It displays experience topology,
backend/frontend URLs, infrastructure and observability links, readiness
checks, and terminal command snippets. The page never starts or stops OS
processes and does not execute shell commands. Its APIs are:

- `GET /api/v1/demo-control/summary`
- `GET /api/v1/demo-control/components`
- `GET /api/v1/demo-control/urls`
- `GET /api/v1/demo-control/readiness`

The full demo stack retains the existing ports: UI `4001`, BFF/frontend pairs
`8061/4011` through `8065/4015`, PostgreSQL `15432`, Redis `6379`, Prometheus
`9090`, Grafana `3001`, Tempo `3200`, Loki `3100`, and Collector ports
`4317`/`4318`/`13133`. Prompt 13 observability, Prompt 14 frontend
segregation, and Prompt 15 BFF boundaries remain unchanged.

## Prompt 17 observability alert rules and AMS integration

Prompt 17 adds a deterministic alerting layer with alert rules, evaluation
runs, alert events, evidence, and AMS ticket links. Ten idempotently seeded
rules cover backend/BFF health, API errors/latency, batch failure spikes, and
AMS backlog. Seed with:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_observability_alerts
```

Manual evaluation uses short health probes and internal EOS runtime, batch,
and AMS data. Cooldown deduplication updates occurrence/suppression counts
for repeated signals. Engineers can acknowledge, resolve, or explicitly
create one AMS incident carrying `OBSERVABILITY_ALERT` and captured evidence.
No remediation is performed, and tests do not require external observability
services.

Alert APIs are available on the full backend and Operations/Observability
BFFs under `/api/v1/observability-alerts`. Full, Operations, and Observability
UIs expose alert overview, rules, evaluation runs, events, evidence,
lifecycle, and ticket-link pages. Business intentionally returns 404 for this
support surface. Demo-control readiness includes an Observability Alerting
check.

This phase has no uncontrolled scheduler, Prometheus/Grafana alert-rule
provisioning, ServiceNow integration, external LLM, authentication, or
autonomous remediation.

## Prompt 18 agent chat and case intake

Prompt 18 adds a persisted agentic support intake foundation. Users and
service engineers can open cases and chat sessions, submit messages, and
receive deterministic Stage 1 guidance assembled from existing EOS support
artifacts. The orchestrator stores evidence items and orchestration runs and
may record review proposals, but proposals are always approval-required and
`DISABLED_IN_STAGE_1`.

Agent chat is available at:

```text
/agent-chat
/agent-chat/user
/agent-chat/engineer
/agent-chat/cases
/agent-chat/cases/:caseId
/agent-chat/sessions
/agent-chat/sessions/:sessionId
```

The APIs use `/api/v1/agent-chat`. The full backend exposes all endpoints;
Business exposes user-facing intake and session routes, Operations exposes
the investigation surface, and the Agentic BFF exposes the complete agent
chat API. The Simulation BFF intentionally returns 404 for this support
surface. Demo-control readiness includes Agent Chat, Agentic Case Intake,
and the Stage 1 Orchestrator.

The response format includes Understanding, Relevant Evidence, Likely Cause,
Recommended Next Steps, and What I Cannot Do Yet. It explicitly remains
read-only: there is no real LLM call, RAG/vector database, shell command,
ticket closure, alert resolution, notification, or remediation execution.
The future agent design can combine governed real-model selection, RAG over
static runbooks, live read-only tools, and approval-gated action tools.

Validate Prompt 18 with:

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
python -m app.db.seed_observability_alerts
pytest
```

The Agentic UI is `http://localhost:4015/agent-chat`, the Business user
assistant is `http://localhost:4011/agent-chat/user`, the Operations engineer
chat is `http://localhost:4012/agent-chat/engineer`, and the full UI remains
at `http://localhost:4001`. All use the existing backend/BFF ports and no
additional infrastructure.

## Prompt 19 knowledge and RAG foundation

Prompt 19 adds curated EOS support knowledge for the deterministic Stage 1
agent. The knowledge catalog contains five sources, ten runbooks/SOPs and
guides, thirty searchable chunks, and six known-error records. Seed it
idempotently with:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_agent_knowledge
```

Knowledge is searched through transparent keyword scoring across titles,
tags, domains, summaries, chunks, symptoms, and known-error records. Each
search creates a retrieval query and result audit record. Agent orchestration
uses the same retrieval path and stores top article chunks/known errors as
case evidence; responses now include a `Relevant Knowledge` section.

Knowledge APIs use `/api/v1/agent-knowledge`:

- `GET /summary`, `/sources`, `/articles`, `/known-errors`
- `GET /articles/{article_id}`, `/known-errors/{known_error_id}`
- `POST /search`
- `GET /retrieval-queries` and `/retrieval-queries/{query_id}`

The full backend, Operations BFF, and Agentic BFF expose the knowledge API;
Business exposes only summary/search for user help, while Simulation and
Observability intentionally return 404. Knowledge pages are available in the
full, Operations, and Agentic UIs at `/agent-knowledge`, `/search`,
`/articles`, `/known-errors`, and `/retrieval-queries` (with detail routes).

This is a RAG foundation only: retrieval is deterministic keyword matching,
with no external LLM, embedding model, vector database, LangChain/LlamaIndex,
or remediation execution. Future work can add hybrid vector retrieval,
reranking, citations, document ingestion, and governed real-model generation.

## Prompt 20 governed real-model provider foundation

Prompt 20 adds an optional OpenAI-compatible Responses API adapter behind the
existing governed AI gateway. The default remains `MOCK_GOVERNED` and
deterministic Stage 1 guidance. A real call requires the feature flag, an
enabled catalog provider and model, `allow_real_model=true`, a configured
`OPENAI_API_KEY`, and a passed safety pre-check. The key is read from the
process environment only; it is never stored in PostgreSQL or written to
logs. Real provider failures and blocked outputs are audited and return a safe
fallback where appropriate.

Configuration is documented in `backend/.env.example`:

```text
REAL_MODEL_ENABLED=false
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_DEFAULT_MODEL=gpt-5.4-mini
OPENAI_REQUEST_TIMEOUT_SECONDS=30
OPENAI_MAX_OUTPUT_TOKENS=1200
OPENAI_REASONING_EFFORT=low
OPENAI_STORE_RESPONSES=false
```

Seed the disabled real provider/model catalog entry with:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_ai_config
```

The governed APIs are:

```text
GET  /api/v1/ai-config/real-model/status
POST /api/v1/ai-config/real-model/dry-run
POST /api/v1/ai-config/real-model/test
GET  /api/v1/ai-config/real-model/providers
GET  /api/v1/ai-config/real-model/models
```

Dry-run validates prompt and safety configuration without making an external
call. The test endpoint remains controlled and normally returns a disabled
safe fallback. Agent chat remains deterministic unless a service engineer
explicitly requests the governed real-model path; even then, the case is
`STAGE_1_READ_ONLY`, actions executed remain zero, and failed/disabled calls
fall back safely. The real-model status page is available at
`/ai-config/real-model` in the Full and Agentic UIs, with no API-key entry
field.

Prompt 20 does not add autonomous remediation, external model calls by
default, RAG/vector storage, authentication, ServiceNow, or an agent
framework. Optional manual real-model validation must be performed only with
an intentionally supplied environment key and must never commit that key.

## Prompt 21 contextual agent investigation handoff

Prompt 21 adds contextual `Investigate with Agent` handoffs from AMS tickets,
observability alerts, batch runs, user reports, diagnostic cases, monitoring
triage cases, and operations exceptions. A handoff creates or reuses an open
agent case and active chat session, stores source metadata, gathers source
evidence, runs deterministic knowledge retrieval, and opens Stage 1 guidance.
Repeated handoffs for the same source reuse the active investigation.

Endpoints are under `/api/v1/agent-chat/intake`: `from-ams-ticket`,
`from-observability-alert`, `from-batch-run`, `from-user-report`,
`from-diagnostic-case`, `from-monitoring-triage`, and
`from-operations-exception`. Operations and Agentic BFFs expose operational
handoffs; Business exposes user-report handoff; Simulation does not expose
agent handoffs. No external model call, remediation, or ServiceNow integration
is present.

## Prompt 22 agent investigation workspace

Prompt 22 adds a unified read-only workspace at `/agent-investigations` and
`/agent-investigations/:caseId` for Full, Operations, and Agentic experiences.
It consolidates contextual source metadata, linked records, chat, evidence,
knowledge, known errors, orchestration runs, disabled action proposals, and a
chronological evidence timeline. The workspace is available through the Full
backend, Operations BFF, and Agentic BFF.

The workspace computes four deterministic drafts: investigation summary, AMS
work note, customer update, and human next-steps checklist. Drafts are not
posted or sent anywhere and always require human review. The Stage 2 action
foundation can execute only explicitly approved local safe handlers; real
model use remains off by default and no external LLM,
ServiceNow, or remediation execution is introduced.

Validate with:

```bash
curl -sS http://localhost:8050/api/v1/agent-investigations/summary | jq .
curl -sS http://localhost:8050/api/v1/agent-investigations/cases | jq .
curl -sS -X POST http://localhost:8050/api/v1/agent-investigations/cases/<CASE_ID>/generate-drafts -H 'Content-Type: application/json' -d '{}' | jq .
```

## Prompt 23 Stage 2 approval-gated agent actions

Prompt 23 adds a deterministic foundation for narrowly scoped, local-only
actions. The flow is always proposal -> explicit human approval or rejection
-> explicit execute call -> audit result.

The catalog includes local draft creation (`CREATE_AMS_WORK_NOTE_DRAFT`,
`CREATE_CUSTOMER_UPDATE_DRAFT`, `CREATE_NEXT_STEPS_CHECKLIST`), internal case
notes, local agent case status changes, evidence linking, proposal review,
follow-up task drafts, and local acknowledgement of observability, monitoring,
or operations exceptions. Drafts are never posted or sent externally, and
alerts/exceptions are acknowledged but never resolved or closed.

The action APIs are available on the Full backend, Operations BFF, and Agentic
BFF under `/api/v1/agent-actions`. The investigation workspace exposes the
catalog, proposal state, Dry Run, Approve, Reject, Execute Approved Action, and
execution history controls. Every approval, rejection, dry run, and execution
transition is recorded in the local audit trail and relevant system chat.

```bash
CASE_ID=<agent-case-record-id>
curl -sS "http://localhost:8050/api/v1/agent-actions/proposals?case_id=${CASE_ID}" | jq .
PROPOSAL_ID=<proposal-id>
curl -sS -X POST "http://localhost:8050/api/v1/agent-actions/proposals/${PROPOSAL_ID}/dry-run" -H 'Content-Type: application/json' -d '{"requested_by_role":"SERVICE_ENGINEER"}' | jq .
curl -sS -X POST "http://localhost:8050/api/v1/agent-actions/proposals/${PROPOSAL_ID}/approve" -H 'Content-Type: application/json' -d '{"approved_by_role":"SERVICE_ENGINEER","approval_comment":"Evidence reviewed.","execute_after_approval":false}' | jq .
curl -sS -X POST "http://localhost:8050/api/v1/agent-actions/proposals/${PROPOSAL_ID}/execute" -H 'Content-Type: application/json' -d '{"requested_by_role":"SERVICE_ENGINEER"}' | jq .
curl -sS "http://localhost:8050/api/v1/agent-actions/executions?case_id=${CASE_ID}" | jq .
```

Prompt 23 does not introduce autonomous remediation, shell commands,
arbitrary SQL or user code execution, external API calls, ServiceNow updates,
customer communication sends, authentication, or real-model-required
execution. Deterministic/mock behavior remains the default and no OpenAI key
is required. Duplicate execution attempts are safely prevented by a proposal
idempotency key and execution audit record.

## Prompt 24: governed Stage 1 real-model chat

Prompt 24 adds optional, governed model assistance for Stage 1 investigation
chat. Deterministic/mock behavior remains the default. A real call requires the
feature flag, an enabled catalog provider/model, an environment API key, an
explicit request, an allowed task, safety checks, and daily context/cost
guardrails. The key is never entered in or returned by the UI.

```bash
curl -sS http://localhost:8050/api/v1/agent-model-chat/status | jq .
curl -sS -X POST http://localhost:8050/api/v1/agent-model-chat/sessions/<SESSION_ID>/preview-context -H 'Content-Type: application/json' -d '{"message_text":"What is the likely cause?"}' | jq .
curl -sS -X POST http://localhost:8050/api/v1/agent-model-chat/sessions/<SESSION_ID>/dry-run -H 'Content-Type: application/json' -d '{"message_text":"What should I check next?","use_real_model":true}' | jq .
curl -sS -X POST http://localhost:8050/api/v1/agent-model-chat/sessions/<SESSION_ID>/ask -H 'Content-Type: application/json' -d '{"message_text":"What should I check next?","use_real_model":false}' | jq .
curl -sS http://localhost:8050/api/v1/agent-model-chat/invocations | jq .
```

Preview and dry-run never call a model. An unavailable, disabled, unsafe, or
over-limit request returns safe deterministic fallback guidance. Model answers
are read-only, grounded in bounded case/evidence/knowledge context, audited,
and marked with evidence/knowledge metadata. Prompt 24 does not execute
actions, send customer communications, post to ServiceNow, run shell or SQL,
or introduce autonomous remediation. An optional single smoke test may be run
only when a user intentionally supplies a key in the shell; keys must never be
committed.
