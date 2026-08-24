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
