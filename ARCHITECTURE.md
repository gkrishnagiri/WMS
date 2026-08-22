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
Alembic revisions `0002_warehouse_fulfillment` and
`0003_warehouse_workflows` creates the domain and transaction
tables.

## Frontend modules

The shared shell provides the top bar, sidebar, and content area. Warehouse
pages use typed API functions and TanStack Query for summary, inventory,
orders, fulfillment tasks, and shipment data. Material UI cards, tables, and
chips provide the operational views without a charting dependency.

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

## Warehouse transaction flow

Order creation creates a `NEW` order and an `ORDER_CREATED` event without
reserving inventory. Allocation locks eligible balances and either reserves
every line or rolls the whole operation back. Task release creates one pick
task per allocation and one pack task per order. Pick and pack completion
advance allocations and write zero-delta confirmation transactions. Shipment
confirmation locks each source balance, reduces on-hand and allocated
quantities together, marks allocations shipped, and writes `SHIPMENT_ISSUE`
ledger entries.

## Infrastructure baseline

The existing PostgreSQL, Redis, OpenTelemetry Collector, Prometheus, Loki,
and Grafana baseline remains in `docker-compose.yml` and `observability/`.
Those files are not part of the Phase 1 application changes.

## Deferred items

Application traces and Tempo, metrics instrumentation, background workers,
returns, replenishment, wave planning, inventory adjustment approval,
shipment rating, carrier integrations, batch processing, anomaly detection,
incident simulation, ticket generation, and agentic AMS behaviors are
deferred.

## Next phase

The next phase can extend the controlled workflow with additional warehouse
operations. Agents, AI behavior, ticket simulation, and incident management
remain out of scope for Prompt 03.
