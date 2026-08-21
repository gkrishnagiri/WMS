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
contain the first business domain. Alembic revision
0002_warehouse_fulfillment creates the domain tables.

## Frontend modules

The shared shell provides the top bar, sidebar, and content area. Warehouse
pages use typed API functions and TanStack Query for summary, inventory,
orders, fulfillment tasks, and shipment data. Material UI cards, tables, and
chips provide the operational views without a charting dependency.

## Warehouse domain

The warehouse domain uses the following PostgreSQL tables, all prefixed with
wf_: wf_warehouses, wf_zones, wf_locations, wf_items,
wf_inventory_balances, wf_orders, wf_order_lines, wf_fulfillment_tasks, and
wf_shipments.

The read-focused API is mounted at /api/v1/warehouse and exposes summary,
warehouse, item, inventory, order, fulfillment task, and shipment views.
Inventory availability is calculated as on-hand minus allocated quantity;
low stock is calculated against the item's reorder point.

## Infrastructure baseline

The existing PostgreSQL, Redis, OpenTelemetry Collector, Prometheus, Loki,
and Grafana baseline remains in `docker-compose.yml` and `observability/`.
Those files are not part of the Phase 1 application changes.

## Deferred items

Application traces and Tempo, metrics instrumentation, background workers,
allocation, picking confirmation, inventory adjustment approval, shipment
rating, carrier integrations, batch processing, incident simulation, and
agentic AMS behaviors are deferred.

## Next phase

Extend the read-focused warehouse foundation with carefully scoped business
transactions and workflows in a later prompt. Agents, AI behavior, ticket
simulation, and incident management remain out of scope for this phase.
