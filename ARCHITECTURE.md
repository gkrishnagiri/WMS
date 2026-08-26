# EOS Architecture

## Current architecture

EOS is a local enterprise demo composed of a React frontend and a FastAPI
backend. The frontend uses React Router for navigation and TanStack Query for
API state. The backend exposes platform identity and health endpoints, with
configuration managed by `pydantic-settings`.

## Current services

- `frontend/`: Vite, TypeScript, Material UI application shell
- `backend/`: FastAPI API, request middleware, exception handling, and tests
- PostgreSQL: SQLAlchemy engine/session foundation and connectivity check
- Redis: async client manager and connectivity check

## Backend modules

app/core contains configuration, JSON-style logging, request IDs, and
exception handlers. app/db contains the declarative base, session
management, and the idempotent Warehouse & Fulfillment demo seed. The
app/models/warehouse.py, app/schemas/warehouse.py,
app/services/warehouse_service.py, and app/api/routes/warehouse.py modules
contain the read APIs. The transaction workflow is organized in
`app/schemas/warehouse_transactions.py` and
`app/services/warehouse_workflow_service.py` under the same route namespace.
Alembic revisions `0002_warehouse_fulfillment`, `0003_warehouse_workflows`,
`0004_operations_ams`, and `0005_synthetic_users_reports` create the domain,
transaction, exception, AMS, synthetic user, journey, run, and user-report
tables.
Revision `0006_monitoring_alert_noise` adds monitored components, alert rules,
alerts, alert events, manual triage cases, and triage-case alert links.
Revision `0007_observability_diagnosis` adds traces, spans, structured logs,
metric samples, diagnostic cases, and diagnostic evidence.
Revision `0008_batch_jobs` adds batch jobs, ordered job steps, run history,
step runs, and batch run events.
Revision `0009_copilot_foundation` adds governed copilot sessions, context
snapshots, recommendations, action plans, message drafts, safe actions, and
copilot action events.

The operations module is organized in `app/models/operations.py`,
`app/schemas/operations.py`, `app/services/operations_exception_service.py`,
and `app/api/routes/operations.py`. It records business/application symptoms
and applies deterministic low-stock and order-stuck rules. Demo simulations
can also mark tasks blocked, mark shipments exceptional, reduce a balance to
low stock, or make an active order stale.

The AMS module is organized in `app/models/ams.py`, `app/schemas/ams.py`,
`app/services/ams_ticket_service.py`, and `app/api/routes/ams.py`. Tickets may
be created manually or from an exception. Every ticket has lifecycle events,
and the supported lifecycle is `NEW` → `ACKNOWLEDGED` or `IN_PROGRESS` →
`RESOLVED` → `CLOSED`. A linked exception is marked `LINKED_TO_TICKET` on
creation and `RESOLVED` when its ticket is resolved.

The synthetic-user module is organized in `app/models/synthetic_users.py`,
`app/schemas/synthetic_users.py`, `app/services/synthetic_user_service.py`,
`app/db/seed_synthetic_users.py`, and
`app/api/routes/synthetic_users.py`. It maintains deterministic personas and
journey definitions and executes warehouse workflows by calling existing
service-layer functions directly. Runs persist status, timing, entity IDs,
failure details, and linked report/ticket IDs.

The user-report module is organized in `app/models/user_reports.py`,
`app/schemas/user_reports.py`, `app/services/user_report_service.py`, and
`app/api/routes/user_reports.py`. Reports represent a human-reported
functional experience independently from operational exceptions. They can be
submitted manually or by a synthetic journey, then linked idempotently to an
AMS incident through the existing ticket-event/lifecycle foundation.

The monitoring module is organized in `app/models/monitoring.py`,
`app/schemas/monitoring.py`, `app/services/monitoring_service.py`,
`app/api/routes/monitoring.py`, and `app/db/seed_monitoring.py`. It provides a
deterministic component/rule catalog and six simulations that create
deduplicated alert symptoms. Repeated signals update occurrence counts and
last-seen timestamps while recording alert events.

The triage module uses `mon_triage_cases` and `mon_triage_case_alerts` as a
manual support-engineer working set. Alerts may be acknowledged, suppressed,
resolved, or linked to an AMS incident. A triage case may group multiple
alerts and then create one monitoring-origin AMS incident. This is manual
symptom grouping: root cause is not inferred or automated in Prompt 06, and
no observability context is attached.

## Frontend modules

The shared shell provides the top bar, sidebar, and content area. Warehouse
pages use typed API functions and TanStack Query for summary, inventory,
orders, fulfillment tasks, and shipment data. Supportability pages use the
same approach for exception lists, deterministic simulations, AMS summaries,
ticket lists, ticket detail, and event timelines. Material UI cards, tables,
and chips provide the operational views without a charting dependency.
Synthetic journey cards, run history, user-report list/create/detail pages,
and report-to-ticket links extend the same shell without browser automation.
Monitoring alert, simulation, and triage pages extend the shell with the same
typed API and TanStack Query pattern.

The observability evidence module is organized in
`app/models/observability.py`, `app/schemas/observability.py`,
`app/services/observability_service.py`, and
`app/api/routes/observability.py`. It stores application-level simulated
traces, span timelines, structured logs, and metric samples in PostgreSQL.
These records can reference monitoring alerts, manual triage cases, business
entities, and AMS tickets without exporting to an external observability
platform.

The batch operations module is organized in `app/models/batch.py`,
`app/schemas/batch.py`, `app/services/batch_service.py`,
`app/api/routes/batch.py`, and `app/db/seed_batch.py`. It models five
deterministic batch jobs and twenty-one ordered steps. Batch simulations run
synchronously, persist every step and lifecycle event, and finish as
`SUCCESS`, `FAILED`, `TIMEOUT`, or `PARTIAL_SUCCESS`.

Batch support flow:

```text
Batch run failure → BATCH_OPERATIONS exception → BATCH AMS ticket
                  → Optional observability diagnostic evidence
```

Batch tickets use source `BATCH` and source module `BATCH_OPERATIONS`; active
duplicate tickets for the same run are prevented. Batch diagnostic cases use
the existing deterministic observability service and add evidence for the
run, failed steps, and failure events. The batch module does not schedule
work or provide retries, queue workers, file transfer, or autonomous
remediation.

The support copilot module is organized in `app/models/copilot.py`,
`app/schemas/copilot.py`, `app/services/copilot_service.py`,
`app/api/routes/copilot.py`, and `app/db/seed_copilot.py`. It is a deterministic
context and recommendation layer over existing support artifacts. A session
can target an AMS ticket, operational exception, user report, monitoring
alert or triage case, observability diagnostic, batch run, or a manual
investigation. Context snapshots persist sanitized summaries and related
entity references; recommendations and action plans retain their evidence and
human-approval requirements.

Copilot support flow:

```text
Existing support artifact → Context snapshot → Rules-based recommendations
                           → Human-review action plan → Draft support messages
```

The copilot records recommendation acceptance/dismissal and draft creation in
`copilot_action_events`. These are audit records, not an execution engine.
The copilot does not automatically acknowledge, resolve, suppress, close, or
rerun anything, and it does not change warehouse business data. The analyze
endpoint is a deterministic convenience flow that creates a session,
snapshot, recommendations, action plan, and investigation checklist.

The governed AI configuration module is organized in
`app/models/ai_config.py`, `app/schemas/ai_config.py`,
`app/services/ai_config_service.py`, `app/services/ai_safety_service.py`,
`app/services/ai_provider_gateway.py`, `app/api/routes/ai_config.py`, and
`app/db/seed_ai_config.py`. It separates provider/model selection, prompt
template registry, safety policy evaluation, invocation auditing, usage
accounting, and guardrail events from copilot business logic.

The only executable provider is the deterministic `MOCK_GOVERNED` provider:

```text
AI request → enabled model/provider → prompt template → safety rules
          → mock response or governed block → audit log + daily usage
```

Safety blocks are logged without invoking the provider. Warnings are logged and
the deterministic mock may proceed. Rendered prompts are sanitized for the
local demo and no API keys or production credentials are stored. Disabled
non-mock providers cannot be invoked. Prompt 09's deterministic copilot
continues to operate independently; it is not replaced by an external model.

Prompt 11 adds `app/services/copilot_ai_service.py` and governed endpoints to
bridge copilot snapshots to the provider gateway. The service selects one of
four task/template pairs, sends a bounded summary payload, stores the returned
invocation ID and `GOVERNED_AI_MOCK` generation mode on a copilot message, and
records the invocation under `COPILOT_SESSION` for audit and usage accounting.

```text
Copilot context snapshot → safety policy → mock provider
                          → AI invocation audit + usage
                          → reviewable copilot draft
```

Blocked safety requests produce an audited blocked message without a normal
draft response. Deterministic Prompt 09 drafts remain available. Neither path
updates ticket, alert, diagnostic, batch, or warehouse state automatically;
governed content is only a human-reviewable artifact.

## Runtime observability instrumentation

Prompt 12 adds `app/core/correlation.py`,
`app/middleware/runtime_observability.py`,
`app/services/runtime_observability_service.py`,
`app/schemas/runtime_observability.py`, and
`app/api/routes/runtime_observability.py`. The middleware assigns or preserves
request and correlation IDs, generates a runtime trace ID, and returns all
three identifiers in response headers. It records the completed request into
the existing `obs_traces`, `obs_spans`, `obs_log_events`, and
`obs_metric_samples` tables without capturing request bodies or secrets.

Runtime request flow:

```text
Request IDs → FastAPI middleware → HTTP trace/span → request logs + metrics
            → PostgreSQL observability tables → runtime read APIs/UI
```

Slow requests are marked `DEGRADED`/`SLOW` using the configured threshold;
errors are marked `ERROR` and receive error logs/metrics. Telemetry failures
are isolated and logged so they cannot fail the original request. The runtime
health probe creates a separate deterministic trace containing PostgreSQL and
Redis connectivity spans and probe metrics.

This complements Prompt 07 simulated evidence: Prompt 07 creates controlled
business scenarios and diagnosis evidence, while Prompt 12 records real EOS
backend request execution metadata. The dedicated runtime APIs and UI expose
that data without replacing `/api/v1/observability/*`.

## Warehouse domain

The warehouse domain uses PostgreSQL tables prefixed with `wf_`: warehouses,
zones, locations, items, inventory balances, orders, order lines, fulfillment
tasks, shipments, allocations, inventory transactions, and order events.
`wf_allocations` records the source balance/location reserved for an order
line. `wf_inventory_transactions` records reservation, pick, pack, and
shipment movements with after-values. `wf_order_events` records order status
history and workflow messages.

The API is mounted at `/api/v1/warehouse` and exposes the existing read views
plus transactional order, allocation, task, shipment, event, and ledger APIs.
Inventory availability is calculated as on-hand minus allocated quantity;
low stock is calculated against the item's reorder point.

## Observability-enabled diagnosis flow

Prompt 06 presents monitoring symptoms without context. Prompt 07 extends the
same alert and triage flow with deterministic evidence:

```text
Alert or triage case → Trace → Spans + logs + metrics → Diagnostic case → AMS ticket
```

The database-degradation scenario correlates a slow PostgreSQL span, API and
workflow spans, structured error logs, and metric samples into a high-
confidence diagnosis. Redis and shipment scenarios use medium confidence.
Insufficient-stock allocation is recorded as a high-confidence business-rule
rejection rather than a technical outage. Diagnostic evidence is rule-based
and human-reviewable; the system does not claim AI certainty or infer a root
cause beyond the supplied deterministic evidence.

The observability demo suite runs database, Redis, allocation, and shipment
scenarios in a fixed order. Diagnostic cases can also be created from an
alert, triage case, or AMS ticket when matching evidence is absent; incomplete
cases retain low or unknown confidence.

## Warehouse transaction flow

Order creation creates a `NEW` order and an `ORDER_CREATED` event without
reserving inventory. Allocation locks eligible balances and either reserves
every line or rolls the whole operation back. Task release creates one pick
task per allocation and one pack task per order. Pick and pack completion
advance allocations and write zero-delta confirmation transactions. Shipment
confirmation locks each source balance, reduces on-hand and allocated
quantities together, marks allocations shipped, and writes `SHIPMENT_ISSUE`
ledger entries.

## Exception-to-ticket flow

An exception is the business symptom and an AMS ticket is the support record.
The operations service creates or refreshes one active exception for a source
entity/type. The AMS service maps severity to priority (`CRITICAL`/`HIGH`/
`MEDIUM`/`LOW` to `P1`/`P2`/`P3`/`P4`) and prevents a second active ticket for
the same exception. Ticket lifecycle changes are written to
`ams_ticket_events`; resolving a linked ticket resolves the exception.

## Synthetic journey flow

Journey execution creates a `synthetic_journey_runs` record and calls the
existing warehouse workflow service for the controlled success and validation
scenarios. A failed functional journey records `failure_type` and
`failure_message`, then creates an `ams_user_reports` record for the selected
persona. Ticket creation is controlled by the request flag; user reports and
their tickets are linked in both directions and duplicate ticket creation is
prevented.

## Infrastructure baseline

The local stack in `docker-compose.yml` includes PostgreSQL, Redis, the
OpenTelemetry Collector, Prometheus, Grafana, Tempo, and Loki. Host ports are
preserved: PostgreSQL `15432`, Redis `6379`, Prometheus `9090`, Grafana
`3001`, Collector OTLP `4317`/`4318`, Tempo `3200`, and Loki `3100`.

## Local observability stack

Prompt 13 adds official OpenTelemetry Python SDK setup in
`app/core/opentelemetry.py` and a lightweight runtime middleware in
`app/middleware/opentelemetry_runtime.py`. It is opt-in via `OTEL_ENABLED` and
does not replace Prompt 12's runtime request persistence. With export enabled,
EOS creates request spans, API counters/histograms, and structured log records
with `service.name`, runtime trace ID, request ID, and correlation ID context.
The middleware preserves Prompt 12 headers and adds
`X-EOS-OTEL-Trace-ID` when an active OTel span exists.

The OTLP flow is:

```text
EOS FastAPI → OTLP Collector → traces: Tempo
                         ├── logs: Loki
                         └── metrics: Prometheus exporter → Prometheus → Grafana
```

The Collector keeps its existing Prometheus exporter and adds traces, logs,
and metrics pipelines with debug exporters for local troubleshooting. Grafana
provisions Prometheus, Loki, and Tempo data sources plus `EOS Runtime
Observability` and `EOS AMS Support Overview` dashboards. The
`/api/v1/observability-stack` APIs expose sanitized configuration, local
service health, and deterministic span/log/metric test signals.

This is deliberately a local single-backend integration. Prompt 07 simulated
business observability evidence and Prompt 12 internal runtime telemetry stay
available through their original PostgreSQL APIs. Tempo, Loki, and Prometheus
are external local stores for exported telemetry, not replacements for the
`obs_*` tables.

## Experience segregation

Prompt 14 keeps one React/Vite codebase and one shared FastAPI backend while
separating the browser experience model. `VITE_EOS_EXPERIENCE` selects one of
`full`, `business`, `operations`, `simulation`, `observability`, or `agentic`.
The centralized registry in `frontend/src/config/experience.ts` owns display
metadata, route ownership, specialized landing content, and local stack links;
`frontend/src/config/navigation.ts` owns the filtered sidebar registry.

The shell applies light route-boundary handling: a route outside the current
experience displays a friendly explanation and a link to the owning browser
port. This is not a security boundary. The full integrated UI remains on
`4001`, while specialized modes use `4011` through `4015`:

```text
Business Application        :4011 → warehouse and fulfillment pages
Operations Console          :4012 → exceptions, tickets, alerts, triage, support
Simulation Lab              :4013 → synthetic, batch, monitoring, and test controls
Observability Control Plane :4014 → runtime evidence and local stack controls
Agentic Support Console     :4015 → copilot and governed AI configuration
```

Each mode reuses the existing page components and API clients. The mode
startup wrappers set the experience code, frontend port, and API boundary:
the full mode uses `8050`, while business, operations, simulation,
observability, and agentic use `8061` through `8065`. Prompt 14's frontend
segregation is therefore preserved while Prompt 15 supplies the corresponding
local backend boundaries. The observability control plane links to Grafana as
the primary UI and exposes only EOS helper views.

This is intentionally frontend-first. Prompt 15 is the next boundary where
separate backend/BFF ownership can be introduced without changing the current
shared API contract.

## Demo stack orchestration and control panel

Prompt 16 adds local operational orchestration around the existing shared
runtime. `scripts/start-demo-stack.sh` starts infrastructure, then the full
backend and five BFFs, then the six frontend modes. `status-demo-stack.sh`
reports Docker, process, HTTP, and observability endpoint status;
`validate-demo-stack.sh` performs the complete smoke check; and
`stop-demo-stack.sh` stops application processes before optionally stopping
Docker with `--with-infra`.

The scripts resolve the repository root from their own location and store
process records and logs under `/tmp/eos-demo`. Each PID record contains the
process ID and Linux process start time. Shutdown verifies both the recorded
start time and an expected command marker before sending `TERM`, so stale
records and unrelated processes are not broadly killed. Healthy unmanaged
processes are reused by startup and are not claimed or stopped by the scripts.

The full backend exposes a read-only `/api/v1/demo-control` API for summary,
component, URL, and readiness data. It performs short, bounded HTTP/TCP checks
for the local stack and never invokes shell commands or reads arbitrary local
files. The full frontend's `/demo-control` page presents this information,
links to every experience and observability service, and terminal command
snippets. It has no start/stop controls and cannot manage OS processes.

This remains local-demo orchestration. A future phase may use containerized or
environment-level orchestration, but Prompt 16 does not add new services,
authentication, ServiceNow, external LLMs, or autonomous remediation.

## Backend boundary and BFF segregation

Prompt 15 adds five FastAPI BFF entrypoints without splitting the repository,
database, or physical deployment units. `app/bff/experience_registry.py`
defines the local topology and frontend origins. `app/bff/app_factory.py`
builds each application with the shared lifecycle, request/correlation
middleware, CORS, runtime telemetry middleware, exception handling, platform
metadata, and only the selected router groups.

```text
8050 full backend          → all existing EOS APIs
8061 business BFF          → business facade + warehouse APIs
8062 operations BFF        → exceptions, AMS, monitoring, triage, support reads
8063 simulation BFF        → synthetic, batch, monitoring/observability simulations
8064 observability BFF    → runtime, evidence, stack, and diagnostics APIs
8065 agentic BFF          → copilot and governed AI configuration APIs
```

All BFFs expose `/health` with experience metadata and the shared platform
metadata routes. Experience-specific facade summaries provide a stable place
for future BFF evolution while currently delegating to existing service logic.
The full backend remains backward-compatible and continues to expose every
prior route. Each specialized BFF uses only its matching frontend origins for
CORS; this is boundary configuration, not authentication or authorization.

The BFFs share the existing PostgreSQL and Redis resources and are started as
separate local Uvicorn processes using `backend/start_*_bff.sh`. No new Docker
services, migrations, or independent deployable units are introduced. Prompt
15 is intentionally a runtime boundary foundation; a future physical split
can place the Operations BFF beside ServiceNow integration and the Agentic BFF
beside agent orchestration without changing the current business application
boundary.

## Observability alert rules and AMS integration

Prompt 17 introduces `obs_alert_rules`, evaluation runs, alert events,
evidence, and ticket links. A manual deterministic evaluator uses local health
checks plus internal runtime, batch, and AMS signals. Repeated active signals
with the same key inside the rule cooldown are suppressed and counted rather
than creating duplicate events or tickets.

Alert lifecycle actions are explicit. AMS incidents are created only by the
event action endpoint or a rule configured with `create_ticket_by_default`; a
created ticket records `OBSERVABILITY_ALERT` / `OBSERVABILITY_ALERTING`, the
condition, and evidence. No ticket is resolved and no production remediation
is executed. The alert API is exposed by the full backend and Operations and
Observability BFFs, and is intentionally absent from Business.

This layer is separate from the earlier synthetic monitoring alert-noise
model and does not provision Prometheus/Grafana rules or run a background
scheduler. Future work includes external alert managers, production
evaluation scheduling, and governed agentic handoff.

## Agent chat and case intake

Prompt 18 adds an agentic support data plane under `/api/v1/agent-chat`.
`agent_cases` represent the issue boundary, `agent_chat_sessions` and
`agent_chat_messages` preserve the conversation, `agent_orchestration_runs`
audit each deterministic cycle, and `agent_evidence_items` preserve the
support context gathered from linked and recent EOS artifacts. The
`agent_action_proposals` table prepares for future approval-gated actions but
does not execute anything in this phase.

The `agent_orchestrator_service` is a transparent Stage 1 implementation. It
classifies messages with simple linked-context and keyword rules, retrieves a
bounded subset of AMS tickets, user reports, observability alerts and
evidence, failed batches, diagnostics, and recent open support signals, then
returns a structured response with Understanding, Relevant Evidence, Likely
Cause, Recommended Next Steps, and What I Cannot Do Yet.

Every case is `STAGE_1_READ_ONLY`; orchestration runs use
`DETERMINISTIC_STAGE_1`, and any proposal is approval-required with execution
status `DISABLED_IN_STAGE_1`. The implementation does not call a model,
perform RAG/vector search, run shell commands, mutate business data, close a
ticket, resolve an alert, or execute remediation. Business, Operations, and
Agentic BFFs expose the appropriate chat surfaces while Simulation does not.

The maturity path is intentionally explicit:

```text
Stage 1: read-only deterministic guidance (Prompt 18)
Stage 2: approval-gated model/tool proposals and audited execution
Stage 3: constrained autonomous remediation in an approved sandbox
```

Future orchestration can add governed real-model selection, RAG over runbooks,
SOPs, KB articles and historical tickets, live read-only tools for current
state, and separately governed action tools. Those layers remain deferred.

## Knowledge and deterministic RAG foundation

Prompt 19 adds a curated knowledge plane for agent support. Knowledge sources
own articles; articles are split into small deterministic chunks with normalized
text, estimated word counts, and keyword lists. Known-error records capture
repeatable symptoms, causes, workarounds, and links to related articles.

`agent_retrieval_queries` and `agent_retrieval_results` provide an audit trail
for every search, including searches initiated by an agent case. Retrieval is
keyword/scored and bounded by `top_k`; title, tag, domain, summary, phrase,
chunk, symptom, and known-error matches contribute transparent scores. There
are no embeddings or vector-store dependencies.

During Stage 1 orchestration, the agent combines operational evidence with
knowledge results, persists `KNOWLEDGE_CHUNK` and `KNOWN_ERROR` evidence, and
includes a Relevant Knowledge section in its read-only response. This keeps
retrieval separate from generation and preserves the existing deterministic
agent contract.

The future hybrid design is:

```text
curated/static knowledge -> keyword + vector retrieval -> optional reranking
live EOS state           -> read-only tools
case context             -> governed model prompt with citations
approved actions         -> separate human-approved action tools
```

Prompt 19 implements only the catalog, chunking, deterministic retrieval, and
audit foundation. It does not call a real model, create embeddings, use a
vector database, ingest ServiceNow knowledge, or execute remediation.

## Governed real-model provider foundation

Prompt 20 extends the AI configuration plane with an optional
`OPENAI_RESPONSES` provider adapter. It reuses the provider, model, prompt,
safety, invocation, guardrail, and usage tables already present, so no new
schema migration is needed. The provider and `OPENAI_GPT_5_4_MINI` catalog
model are seeded disabled; the deterministic `MOCK_GOVERNED` provider remains
the only default executable path.

The gateway resolves a catalog provider/model/template, evaluates the input
against the governed safety policy, and only then considers an external call.
The real path additionally requires `REAL_MODEL_ENABLED=true`, explicit
`allow_real_model=true`, enabled catalog records, and a non-empty
`OPENAI_API_KEY`. The key is environment-only and is never persisted,
returned, or logged. The OpenAI SDK is imported lazily so disabled startup,
tests, seeds, and the demo stack do not require a key or network access.

Every dry-run, disabled, blocked, failed, or successful attempt is represented
by an existing AI invocation audit row. Mode, fallback, external request ID,
and usage metadata are stored only in the sanitized invocation JSON; token and
cost accounting continues through `ai_usage_daily`. Response output is
checked for unsafe claims such as executed actions or secret requests. A
blocked response is replaced with a safe fallback and a guardrail event.

Agent chat remains deterministic by default. An explicit Agentic/Full chat
request can select the governed real path, but the orchestrator still uses
curated operational/knowledge context, remains `STAGE_1_READ_ONLY`, keeps
`actions_executed=0`, and falls back to deterministic guidance whenever the
provider is disabled, unavailable, or blocked. No model receives tools or can
change EOS data.

Prompt 20 adds status, dry-run, and controlled test routes below
`/api/v1/ai-config/real-model`. Full and Agentic BFFs expose the complete
surface; Operations exposes status and dry-run; Business, Simulation, and
Observability do not expose real-model administration. The UI exposes status
and test controls without an API-key input. This is a provider integration
foundation, not an enablement of unrestricted model use.

The future path is:

```text
curated case/evidence/knowledge context -> governed prompt template
                                       -> safety pre-check
                                       -> optional real provider adapter
                                       -> safety post-check
                                       -> invocation/usage audit
                                       -> human-reviewed Stage 1 response
```

Real model selection, external credentials, production cost limits, model
availability, prompt/version governance, and eventual RAG/tool/action layers
remain separately governed. Prompt 20 does not add vector RAG, ServiceNow,
authentication, autonomous remediation, or external calls by default.

## Contextual agent investigation handoff

Prompt 21 adds a handoff boundary from operational source objects into Agent
Chat and Case Intake. A source-specific intake resolves the source record,
writes generic source metadata on `agent_cases`, links existing IDs where
available, creates or reuses an active session, and invokes deterministic Stage
1 orchestration. The orchestrator gathers source evidence and deterministic
knowledge before appending guidance.

Supported sources are AMS tickets, observability alert events, batch runs, user
reports, diagnostic cases, monitoring triage cases, and operations exceptions.
An active case is reused for the same source object. Operations and Agentic
BFFs expose operational handoffs, Business exposes user-report handoff, and
Simulation remains isolated. This is a demo/API boundary, not authorization;
Prompt 21 does not enable real models, execute actions, integrate ServiceNow,
or change infrastructure.

## Agent investigation workspace

Prompt 22 provides a computed workspace over an `agent_case`. It joins the
contextual handoff source, linked AMS/alert/batch/diagnostic records, chat
messages, orchestration runs, evidence, deterministic retrieval results, and
disabled action proposals. A timeline builder turns those records into
chronological case, source, conversation, orchestration, evidence, knowledge,
and proposal events.

The workspace also produces deterministic investigation summary, AMS work-note,
customer-update, and next-steps drafts. These are display/copy artifacts only;
they are not persisted to external systems, sent to customers, or applied to
tickets. The Stage 2 banner remains authoritative: only explicitly approved
local safe actions can execute, remediation remains disabled, and real-model
use is not enabled by default. Full, Operations, and Agentic BFFs expose the workspace while the
Business, Simulation, and Observability BFFs do not.

## Stage 2 approval-gated action architecture

Prompt 23 separates agent guidance from action execution. The deterministic
orchestrator creates safe catalog proposals but cannot execute them. An
explicit engineer approval changes a proposal to `APPROVED`; only a separate
explicit execute request can run a registered handler. Rejection is terminal.

```text
case context -> deterministic proposal
                    |
                    v              v
             human approve    human reject
                    |
                    v
           explicit execute request
                    |
        registered local safe handler
                    |
             execution + audit
                    |
          timeline and system chat
```

`agent_action_proposals` stores approval identity/timestamps, the safe action
code, execution state, result, and an idempotency key. The
`agent_action_executions` table records each execution attempt and result.
`agent_action_audit_events` records approval, rejection, dry-run, execution
start, success, and failure events used by the investigation timeline.

Handlers are allowlisted and narrowly scoped: local draft generation, an
internal local case note, allowed local agent-case statuses, evidence
reference confirmation, and local acknowledgement of linked alerts or
operations exceptions. Acknowledgement never resolves an alert or closes an
exception. Draft handlers never send data. The execution service rejects
unapproved, rejected, unknown, and previously attempted proposals before a
handler is called.

Operations BFF and Agentic BFF expose the complete `/api/v1/agent-actions`
surface. Business, Simulation, and Observability BFFs do not expose it. The
Full backend exposes it for the integrated demo. Demo readiness checks the
summary endpoint without approving or executing anything.

This is the explicit boundary before a future Stage 3: any autonomous
remediation, broader tool permissions, external system integration, real
customer sends, shell/SQL/code execution, or model-driven execution requires
a separately governed design and is not enabled by Prompt 23.

## Deferred items

Application traces and Tempo, metrics instrumentation, background workers,
returns, replenishment, wave planning, inventory adjustment approval,
shipment rating, carrier integrations, real scheduling, async batch workers,
batch retry orchestration, external file transfer, external ITSM connectors,
notifications, ticket analytics, anomaly detection, root-cause
inference, real OpenTelemetry SDK/export, Tempo, Loki, Prometheus scraping,
Grafana dashboards, collector trace/log pipelines, distributed tracing,
browser telemetry, external observability SaaS integration, LLM summaries,
model-backed agent orchestration, AI-native diagnosis, governed external LLM execution,
and autonomous remediation are deferred. Synthetic journey runs, monitoring
alerts, simulated observability evidence, and runtime request telemetry are
stored for audit. Prompt 13 now provides local external export, but production
sampling, remote observability SaaS, browser RUM, distributed multi-service
tracing, Prometheus alert rules, Grafana alerting, ServiceNow integration, and
AI-driven remediation remain deferred.

## Next phase

The next phase can extend the controlled workflow with additional warehouse
operations and supportability data. Real external LLM/provider SDK
integration, streaming, LangGraph/LiteLLM, RAG, embeddings/vector storage,
tool execution, local observability-stack expansion, distributed tracing,
browser telemetry, AI classification, ticket analytics, agentic behavior, and
autonomous resolution remain out of scope for Prompt 13.

## Prompt 24: governed Stage 1 model chat

The Stage 1 model path is deliberately separate from the Prompt 23 action
executor:

```text
chat question -> bounded context package -> prompt/safety/limit checks
             -> existing provider gateway -> output safety check
             -> assistant metadata + invocation audit
             -> deterministic fallback when blocked or unavailable
```

`agent_model_chat_service` curates case, linked operational records, evidence,
knowledge/known errors, recent chat, and local action status into a bounded
context package. It excludes keys, secrets, environment values, and tools.
Governed prompt templates describe Stage 1 read-only behavior and require
grounded citations. The existing lazy provider gateway remains the only path
to an OpenAI Responses call; it reads keys from the environment and records
invocation, usage, and guardrail audit data.

The service enforces explicit task allowlisting, input/context limits, daily
invocation and estimated-cost limits, pre-call safety checks, and post-call
checks for execution claims, commands, SQL, secrets, external sends, and
approval bypass. Preview and dry-run are non-mutating. Ask with
`use_real_model=false`, disabled readiness, missing credentials, provider
failure, or a failed check stays deterministic and reports the fallback reason.
Assistant metadata retains generation mode, invocation ID, usage/status,
evidence used, knowledge used, and the Stage 1 boundary; actions executed
remains zero.

Prompt 23 local actions still require separate human approval and explicit
execution. Prompt 24 never invokes those handlers. A future Stage 3 design
would need a new authorization, tool, and external-system governance boundary;
it is not implied by model chat activation. Streaming, voice, browser use,
vector databases, ServiceNow, customer sends, and autonomous remediation remain
future work.

## Prompt 25 demo scenario orchestration

The guided demo layer coordinates a presenter-friendly storyline without
becoming an automation or remediation engine:

```text
scenario catalog -> presenter starts run -> safe local issue induction
                  -> guided step + deep links -> agent investigation
                  -> evidence/knowledge/action review -> human action workflow
                  -> scenario artifacts, timeline, and outcome summary
```

`demo_scenarios` stores the seeded catalog. `demo_scenario_runs` owns a
presenter-controlled run, while `demo_scenario_steps` stores ordered
instructions, talking points, target links, and completion state.
`demo_scenario_artifacts` links generated local records such as orders,
exceptions, tickets, batch runs, alerts, agent cases, sessions, proposals,
and executions without copying their business data. `demo_scenario_events`
provides a scenario-specific timeline. Reset marks a run as `RESET` and adds
an event; it intentionally does not delete shared operational or action audit
history.

The service uses existing deterministic operations, AMS, batch, monitoring,
user-report, agent handoff, investigation, and action services. Start creates
minimum local context and the first active step. Advance or explicit step
completion activates the next step; it never approves or executes an action
and never invokes the real model. Agent handoff occurs only when the presenter
advances to that guided step, with `use_real_model=false`. The investigation
workspace exposes scenario name/run/step and links back to the guided run.

Scenario APIs are exposed on the Full backend, Operations BFF, Simulation BFF,
and Agentic BFF. Business has only catalog/summary read endpoints and
Observability has no scenario surface. Demo readiness reads the catalog and
summary only; readiness never starts a scenario. Prompt 25 adds guided demo
orchestration only. It does not enable real model calls by default, execute
shell commands or arbitrary SQL, call external systems, post to ServiceNow,
send customer communications, add authentication, or introduce autonomous
remediation.

## Prompt 26 executive demo value storyboard

The executive layer is a read-only projection over the existing guided
scenario, agent investigation, knowledge, action, and AI audit records:

```text
scenario runs + investigations + evidence/knowledge + actions + AI audit
                              -> executive aggregation service
                              -> KPI summary + value metrics + storyboard
                              -> leadership UI and experience-aware deep links
```

`executive_demo_service` computes scenario-derived counts dynamically. It
reports the issue-to-investigation chain, evidence and retrieval activity,
approval-gated action state, model readiness, guardrail/audit coverage, and
scenario proof points. Its effort-impact panel uses explicit illustrative
assumptions for manual triage, evidence collection, drafting, assisted review,
and approval review. The API returns the assumptions and a disclaimer so the
figures cannot be mistaken for production productivity or ROI.

The storyboard presents the traditional AMS challenge, AI-native operating
model, four guided scenario proof points, governance by design, commercial
model implications, and a roadmap to production. The commercial view is
narrative only; there is no billing, pricing, contract, or financial engine.
The value chain links signals, contextual handoff, evidence/knowledge,
Stage 1 guidance, approval-gated actions, and audit/learning to existing EOS
experiences.

Business, Operations, and Agentic BFFs expose the read-only executive APIs;
the Simulation BFF also exposes them as a read-only demo view, while the
Observability BFF does not. Readiness checks only the summary endpoint and
cannot start scenarios, invoke a model, or execute an action. Prompt 26 does
not enable real model calls by default, add autonomous remediation, execute
shell/SQL/code, integrate ServiceNow, send customer communications, add
authentication, or claim production savings.

## Prompt 27 demo readiness and one-command showcase mode

The readiness layer is a local, presenter-oriented projection over existing
EOS seed, scenario, investigation, action, and model-governance records:

```text
seed/database checks + route checks + safety defaults
                         -> readiness summary/checks
                         -> showcase preparation + URL launcher + UI guide
                         -> repeatable presenter flow
```

`demo_readiness_service` keeps reporting read-only. Its `SOFT_RESET` profile
marks active guided runs reset and preserves scenario events, operational
records, action audit, model invocation audit, and investigations. Its
`SHOWCASE_RESET` profile also idempotently ensures the four scenario catalog
rows. `LOCAL_DEV_GENERATED_DATA_RESET` requires the exact local confirmation
string and uses the same archive-by-status approach; it does not drop schema,
delete seed data, or wipe audit history. Prepared runs are created only by an
explicit `prepare-showcase` request and are still presenter-controlled; the
service never approves or executes actions and never calls a model.

The API provides readiness checks, grouped presenter URLs, a human-executable
UI test guide, and a smoke report. Demo Control includes readiness, showcase,
reset-profile, UI-guide, and smoke-report capabilities without invoking reset,
scenario, model, or action operations. Demo scripts call only the local
readiness API; they do not contain database or external-system operations.

Full, Operations, Simulation, and Agentic expose the complete readiness surface.
Business receives only read-only GET endpoints, and Observability receives no
readiness routes. The frontend mirrors this boundary by hiding mutation
controls in Business and presenting score, safety badges, URL launcher,
showcase controls, UI guide, and smoke report in the approved experiences.
Prompt 27 is showcase hardening only: real model use stays disabled by default,
autonomous remediation and external integrations remain out of scope, and no
production reset or authentication boundary is implied.

## Prompt 28 UI acceptance testing and evidence capture

The UI acceptance layer is a manual evidence ledger over the browser routes
already provided by EOS:

```text
seeded suite/case/step catalog -> tester starts run
                                  -> browser observation
                                  -> step result + evidence reference
                                  -> coverage + JSON/Markdown report
```

`ui_test_suites`, `ui_test_cases`, and `ui_test_steps` define deterministic
browser guidance. `ui_test_runs` stores the tester and lifecycle, while
`ui_test_step_results` stores status, observed result, evidence note,
screenshot reference, and defect note. `ui_test_run_events` provides a small
run audit trail. The service validates that submitted steps belong to the
selected suites, upserts results idempotently, calculates coverage, and derives
overall completion status. Markdown is rendered from stored text; screenshot
binary upload and PDF generation are intentionally not included.

The catalog covers executive value, demo readiness/showcase, all four guided
scenarios, operations-to-agent handoffs, investigation evidence, governed
Stage 1 fallback, Stage 2 approval-gated actions, and experience/governance
boundaries. Mutating steps are explicitly labeled with local safety notes so a
tester knows when a scenario start, showcase preparation, approval, or action
execution is expected. The acceptance service itself never invokes a model or
executes operational actions.

Full, Operations, Simulation, and Agentic expose the complete acceptance API.
Business exposes only catalog, run, coverage, and report GET routes; mutation
routes are absent. Observability exposes no acceptance surface. Demo readiness
checks catalog/run/report availability without starting a test run. Prompt 28
adds manual browser-first testing only: no browser automation, external test
SaaS, real-model requirement, autonomous remediation, shell/SQL execution,
ServiceNow integration, customer sends, or authentication.

## Prompt 29: OpenAI costing and smoke-test boundary

The optional OpenAI path remains behind `ai_provider_gateway`. The
`ai_model_pricing` table stores editable, effective-dated local pricing
assumptions; each real-provider invocation is normalized into
`ai_model_usage_metering` with provider-reported or estimated input,
completion, and total tokens plus a pricing snapshot. Historical costs do not
change when future pricing is edited.

The costing service checks the feature flag, provider/model governance,
environment key presence, task allow-list, safety, input/output limits, daily
invocation/cost limits, and single-call estimated cost. Dry-runs never invoke a
provider. A smoke run crosses the provider boundary only after an explicit
request and cost acknowledgement; blocked attempts use the governed gateway
with `allow_real_model=false` where possible so the attempt remains auditable.
OpenAI usage fields are normalized to EOS terminology.

Agentic and Full expose costing, pricing, usage, and one-shot smoke controls;
Operations receives read-only costing plus smoke controls; Business receives
read-only catalog/summary views; Simulation and Observability receive none.
No API key is returned or accepted by the UI. Stage 1 chat is catalog-backed
but deterministic fallback remains the default. Prompt 29 adds no autonomous
remediation, shell/SQL/code execution, external business-system calls,
ServiceNow integration, customer communication, authentication, or billing.
Estimated costs are local demo assumptions, not production measurements or
invoices.

### Dynamic model catalog amendment

The governed OpenAI costing catalog is not limited to seeded examples.
`AiModelConfig.catalog_active` separates catalog membership from governance
`enabled`. Agentic and Full experiences can add a model with initial local
pricing through the costing API/UI. Delete archives the configuration and
deactivates active pricing without deleting referenced invocation, usage, or
historical pricing records. Archived models are omitted from normal selection
and are available only through an explicit inactive-catalog query.
