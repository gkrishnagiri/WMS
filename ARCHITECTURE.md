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

The existing PostgreSQL, Redis, OpenTelemetry Collector, Prometheus, Loki,
and Grafana baseline remains in `docker-compose.yml` and `observability/`.
Those files are not part of the Phase 1 application changes.

## Deferred items

Application traces and Tempo, metrics instrumentation, background workers,
returns, replenishment, wave planning, inventory adjustment approval,
shipment rating, carrier integrations, batch processing, external ITSM
connectors, notifications, ticket analytics, anomaly detection, root-cause
inference, real OpenTelemetry export, Tempo, Loki, Prometheus scraping,
Grafana dashboards, batch failures, LLM summaries, agent orchestration, AI-
native diagnosis, and autonomous remediation are deferred. Synthetic journey
runs, monitoring alerts, and simulated observability evidence are stored for
audit, but no browser automation, external observability export, batch
execution, or autonomous diagnosis is performed by this module.

## Next phase

The next phase can extend the controlled workflow with additional warehouse
operations and supportability data. Real observability integrations, batch
failures, AI classification, ticket analytics, agentic behavior, and
autonomous resolution remain out of scope for Prompt 07.
