# Enterprise Operations Suite (EOS)

Enterprise Operations Suite is the demo application for the AI-Native AMS
Research Platform. Phase 1 established the reusable backend and frontend
foundation. Prompt 04 added the deterministic supportability layer around the
warehouse module, and Prompt 05 adds synthetic users and user-reported issue
flows.

## Current phase

Prompt 05 — Synthetic Users and User-Reported Functional Issues.

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

After applying the Alembic migrations, load deterministic demo data with:

    cd backend
    source .venv/bin/activate
    alembic upgrade head
    python -m app.db.seed_warehouse
    python -m app.db.seed_synthetic_users

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

The existing /, /health, and /about routes remain available.

## Validation

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed_warehouse
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

Deferred capabilities include monitoring alert noise, observability-enabled
diagnosis, batch failures, returns, replenishment, wave planning, carrier
integrations, background jobs, adjustment approvals, external ITSM
connectors, notifications, ticket analytics, anomaly detection, root-cause
inference, LLM summaries, agents, and autonomous remediation.
