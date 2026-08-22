# Prompt 03 – Warehouse Transaction Workflows

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

**Enterprise Operations Suite (EOS)**

Prompt 01 created the enterprise application foundation.

Prompt 02 created the initial read-focused **Warehouse & Fulfillment Operations** domain foundation.

Your task now is to implement controlled warehouse transaction workflows.

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
- Warehouse frontend pages
- Backend running on port `8050`
- Frontend running on port `4001`

Current known commits include:

```text
702c092 feat: add EOS enterprise foundation
```

Prompt 02 has also been committed and pushed.

Use the current repository structure and coding patterns.

Do not redesign Prompt 01 or Prompt 02 output.

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

You must preserve existing read APIs.

You must preserve existing frontend routes.

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

You may update `.gitignore` if needed to exclude local runtime artifacts.

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

Do not add a charting library in this prompt.

Do not add workflow engines.

Do not add Celery, Dramatiq, Kafka, Temporal, LangGraph, agents, AI, or ticket simulation in this prompt.

---

# Objective

Implement the first operational warehouse transaction path:

```text
Customer Order
    ↓
Allocation
    ↓
Fulfillment Task Release
    ↓
Pick Task Completion
    ↓
Pack Task Completion
    ↓
Shipment
    ↓
Inventory Reduction
    ↓
Inventory Transaction Ledger
```

This prompt should turn the warehouse module from a read-only demo into a controlled transactional business module.

---

# Scope

Implement:

1. Customer order creation
2. Inventory allocation
3. Fulfillment task release
4. Task start and completion
5. Shipment confirmation
6. Inventory transaction ledger
7. Order detail view
8. Frontend workflow actions
9. Backend workflow tests
10. Documentation updates

Do not implement:

- AI agents
- AMS incident simulation
- ticket generation
- automated anomaly detection
- batch jobs
- carrier API integration
- advanced wave planning
- replenishment optimization
- returns processing
- inventory adjustment approval workflows

Those come later.

---

# Database Additions

Create a new Alembic migration.

Add the following new tables:

```text
wf_allocations
wf_inventory_transactions
wf_order_events
```

Use the existing UUID and timestamp conventions from Prompt 02.

---

## Table: `wf_allocations`

Purpose:

Track which inventory balance/location was reserved for each order line.

Fields:

```text
id
order_id
order_line_id
warehouse_id
location_id
item_id
quantity_allocated
quantity_picked
quantity_packed
quantity_shipped
status
created_at
updated_at
```

Rules:

- `order_id` references `wf_orders.id`
- `order_line_id` references `wf_order_lines.id`
- `warehouse_id` references `wf_warehouses.id`
- `location_id` references `wf_locations.id`
- `item_id` references `wf_items.id`
- quantities must not be negative
- `quantity_picked`, `quantity_packed`, and `quantity_shipped` default to `0`
- one order line may have multiple allocations if needed, but Prompt 03 may implement single-location allocation first
- allocation seed should not be required

Suggested statuses:

```text
ALLOCATED
PICKED
PACKED
SHIPPED
CANCELLED
```

---

## Table: `wf_inventory_transactions`

Purpose:

Maintain an auditable inventory movement and reservation ledger.

Fields:

```text
id
transaction_number
transaction_type
warehouse_id
location_id
item_id
order_id
order_line_id
allocation_id
task_id
shipment_id
quantity_on_hand_delta
quantity_allocated_delta
quantity_on_hand_after
quantity_allocated_after
quantity_available_after
reference_type
reference_number
reason_code
notes
created_by
created_at
```

Rules:

- `transaction_number` must be unique
- `warehouse_id` references `wf_warehouses.id`
- `location_id` references `wf_locations.id`
- `item_id` references `wf_items.id`
- `order_id` nullable, references `wf_orders.id`
- `order_line_id` nullable, references `wf_order_lines.id`
- `allocation_id` nullable, references `wf_allocations.id`
- `task_id` nullable, references `wf_fulfillment_tasks.id`
- `shipment_id` nullable, references `wf_shipments.id`
- deltas may be positive, zero, or negative
- after-values must reflect the inventory balance after the transaction
- `created_by` defaults to `system`

Suggested transaction types:

```text
ALLOCATION_RESERVE
PICK_CONFIRM
PACK_CONFIRM
SHIPMENT_ISSUE
ALLOCATION_RELEASE
```

For Prompt 03, implement at minimum:

```text
ALLOCATION_RESERVE
PICK_CONFIRM
PACK_CONFIRM
SHIPMENT_ISSUE
```

---

## Table: `wf_order_events`

Purpose:

Maintain order workflow event history.

Fields:

```text
id
order_id
event_type
from_status
to_status
message
event_payload
created_by
created_at
```

Rules:

- `order_id` references `wf_orders.id`
- `event_payload` should be JSON/JSONB if supported
- `created_by` defaults to `system`

Suggested event types:

```text
ORDER_CREATED
ORDER_ALLOCATED
TASKS_RELEASED
TASK_STARTED
TASK_COMPLETED
ORDER_SHIPPED
VALIDATION_FAILED
```

---

# Existing Table Enhancements

Modify existing models/migrations only if required.

If existing columns already support the workflow, reuse them.

If additional fields are necessary, add them carefully.

Suggested optional additions:

### `wf_orders`

Add if missing:

```text
warehouse_id nullable
```

Rationale:

Prompt 03 workflows can allocate and ship from a selected warehouse.

If adding `warehouse_id`, it should reference `wf_warehouses.id`.

### `wf_shipments`

Add if missing:

```text
shipped_by
```

Keep optional.

Do not add unnecessary complexity.

---

# Workflow Rules

## Order Creation

Create a new customer order and order lines.

Endpoint:

```text
POST /api/v1/warehouse/orders
```

Request:

```json
{
  "customer_name": "Acme Retail Stores",
  "order_type": "STANDARD",
  "priority": "NORMAL",
  "requested_ship_date": "2026-08-25",
  "warehouse_id": "optional-warehouse-uuid",
  "lines": [
    {
      "item_id": "item-uuid",
      "quantity_ordered": 5
    }
  ]
}
```

Rules:

- generate order number if not supplied
- order number format should be deterministic and readable, for example `ORD-YYYYMMDD-0001`
- order status starts as `NEW`
- quantity allocated and quantity shipped start as `0`
- create an `ORDER_CREATED` event
- do not allocate inventory during order creation

Response should include created order with lines.

---

## Allocation

Allocate a `NEW` order.

Endpoint:

```text
POST /api/v1/warehouse/orders/{order_id}/allocate
```

Rules:

- only orders in `NEW` status can be allocated
- allocation must be atomic
- if any line cannot be fully allocated, the entire allocation should fail
- no partial allocation in Prompt 03
- find inventory balances where:

```text
quantity_on_hand - quantity_allocated >= quantity_ordered
```

- allocation should be deterministic:
  - prefer the order’s warehouse if specified
  - otherwise sort by warehouse code, location code
- create `wf_allocations`
- increment `wf_inventory_balances.quantity_allocated`
- update `wf_order_lines.quantity_allocated`
- set order status to `ALLOCATED`
- create one `ALLOCATION_RESERVE` inventory transaction per allocation
- create an `ORDER_ALLOCATED` event

If insufficient stock:

- return HTTP `409 Conflict`
- do not change inventory
- do not create allocations
- create no partial state

---

## Release Fulfillment Tasks

Release tasks for an allocated order.

Endpoint:

```text
POST /api/v1/warehouse/orders/{order_id}/release-tasks
```

Rules:

- only `ALLOCATED` orders can release tasks
- operation should be idempotent
- running it twice must not create duplicate tasks
- create one `PICK` task per order line/allocation
- create one `PACK` task per order
- task status starts as `OPEN`
- task priority should follow order priority
- set order status to `PICKING`
- create a `TASKS_RELEASED` order event

Task number format should be readable, for example:

```text
TASK-YYYYMMDD-0001
```

---

## Start Task

Endpoint:

```text
POST /api/v1/warehouse/tasks/{task_id}/start
```

Rules:

- only `OPEN` tasks can be started
- set task status to `IN_PROGRESS`
- create `TASK_STARTED` order event if task is linked to an order

---

## Complete Pick Task

Endpoint:

```text
POST /api/v1/warehouse/tasks/{task_id}/complete
```

For `PICK` tasks:

Rules:

- task must be `OPEN` or `IN_PROGRESS`
- set task status to `COMPLETED`
- update related allocation quantity picked
- set allocation status to `PICKED`
- create `PICK_CONFIRM` inventory transaction
  - `quantity_on_hand_delta = 0`
  - `quantity_allocated_delta = 0`
- if all pick tasks for the order are completed, keep or set order status to `PACKING`
- create `TASK_COMPLETED` order event

---

## Complete Pack Task

Same endpoint:

```text
POST /api/v1/warehouse/tasks/{task_id}/complete
```

For `PACK` tasks:

Rules:

- all related pick tasks for the order must be completed before pack completion
- task must be `OPEN` or `IN_PROGRESS`
- set task status to `COMPLETED`
- update related allocations quantity packed
- set allocation status to `PACKED`
- create `PACK_CONFIRM` inventory transaction
  - `quantity_on_hand_delta = 0`
  - `quantity_allocated_delta = 0`
- keep order status as `PACKING`
- create `TASK_COMPLETED` order event

If pick tasks are not completed:

- return HTTP `409 Conflict`

---

## Ship Order

Endpoint:

```text
POST /api/v1/warehouse/orders/{order_id}/ship
```

Request:

```json
{
  "carrier": "UPS",
  "tracking_number": "1Z999EOS0001",
  "shipped_by": "system"
}
```

Rules:

- order must be allocated and packed before shipment
- all required pick and pack tasks must be completed
- create shipment if needed
- set shipment status to `SHIPPED`
- set `shipped_at`
- for each allocation:
  - reduce `wf_inventory_balances.quantity_on_hand`
  - reduce `wf_inventory_balances.quantity_allocated`
  - update `wf_order_lines.quantity_shipped`
  - update `wf_allocations.quantity_shipped`
  - set allocation status to `SHIPPED`
  - create `SHIPMENT_ISSUE` inventory transaction
- set order status to `SHIPPED`
- create `ORDER_SHIPPED` order event

Inventory math:

```text
quantity_on_hand_delta = -quantity_shipped
quantity_allocated_delta = -quantity_shipped
```

After shipment:

```text
quantity_on_hand_after >= 0
quantity_allocated_after >= 0
```

If shipment would make inventory negative:

- return HTTP `409 Conflict`
- do not partially ship
- transaction must roll back

---

# Backend Implementation

Add or extend backend modules using the existing patterns.

Suggested files:

```text
backend/app/models/warehouse_transactions.py
backend/app/schemas/warehouse_transactions.py
backend/app/services/warehouse_workflow_service.py
backend/app/api/routes/warehouse_workflows.py
```

It is acceptable to place these in existing warehouse files if the project style favors fewer files, but keep the code organized.

Do not duplicate database session code.

Do not duplicate configuration code.

Use existing logging and request ID patterns.

---

# API Endpoints to Add

Add these endpoints under the existing warehouse API namespace:

```text
POST /api/v1/warehouse/orders
GET  /api/v1/warehouse/orders/{order_id}
POST /api/v1/warehouse/orders/{order_id}/allocate
POST /api/v1/warehouse/orders/{order_id}/release-tasks
POST /api/v1/warehouse/tasks/{task_id}/start
POST /api/v1/warehouse/tasks/{task_id}/complete
POST /api/v1/warehouse/orders/{order_id}/ship
GET  /api/v1/warehouse/inventory-transactions
GET  /api/v1/warehouse/orders/{order_id}/events
```

Keep existing Prompt 02 read endpoints working.

---

## Order Detail Response

`GET /api/v1/warehouse/orders/{order_id}` should include:

- order header
- order lines
- allocations
- tasks
- shipments
- recent events

Do not over-optimize.

---

## Inventory Transactions Endpoint

Endpoint:

```text
GET /api/v1/warehouse/inventory-transactions
```

Support optional filters:

```text
item_id
warehouse_id
order_id
transaction_type
```

Return newest first.

Limit default:

```text
100
```

---

# Error Handling

Use clear API error responses.

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

for invalid workflow state or insufficient stock.

Do not return generic internal errors for business rule violations.

Example:

```json
{
  "detail": "Order must be in ALLOCATED status before releasing tasks."
}
```

---

# Transaction Safety

Workflow operations must use database transactions.

Allocation and shipment must be atomic.

Do not leave partial allocations, partial inventory changes, or partial shipments.

If an operation fails, rollback the transaction.

---

# Frontend Implementation

Extend the existing EOS frontend.

Do not replace the application shell.

Do not change frontend port `4001`.

Do not change backend base URL away from `http://localhost:8050`.

---

## Navigation

Add or update sidebar entries:

```text
Dashboard
Warehouse
Inventory
Orders
Fulfillment Tasks
Shipments
Inventory Transactions
Health
About
```

---

## Required Frontend Routes

Existing routes must continue working:

```text
/
/health
/about
/warehouse
/warehouse/inventory
/warehouse/orders
/warehouse/tasks
/warehouse/shipments
```

Add:

```text
/warehouse/orders/new
/warehouse/orders/:orderId
/warehouse/inventory-transactions
```

---

## Orders Page Enhancements

Route:

```text
/warehouse/orders
```

Add:

- button: `Create Order`
- link from order number to order detail page
- status chips
- priority chips

---

## Create Order Page

Route:

```text
/warehouse/orders/new
```

Implement a simple form:

Fields:

```text
customer_name
order_type
priority
requested_ship_date
warehouse_id optional
lines
```

For lines:

- item dropdown
- quantity ordered

Support adding/removing lines.

On submit:

- call `POST /api/v1/warehouse/orders`
- navigate to order detail page

Keep validation simple.

---

## Order Detail Page

Route:

```text
/warehouse/orders/:orderId
```

Display:

- order header
- order lines
- allocations
- fulfillment tasks
- shipments
- order events

Add workflow action buttons based on status:

```text
Allocate
Release Tasks
Ship Order
```

Rules:

- show `Allocate` only for `NEW`
- show `Release Tasks` only for `ALLOCATED`
- show `Ship Order` when order is ready to ship

Use API errors to show clear messages.

---

## Fulfillment Tasks Page Enhancements

Route:

```text
/warehouse/tasks
```

Add action buttons:

```text
Start
Complete
```

Rules:

- `Start` visible for `OPEN`
- `Complete` visible for `OPEN` or `IN_PROGRESS`

After action, refresh task and order data.

---

## Inventory Transactions Page

Route:

```text
/warehouse/inventory-transactions
```

Display a table:

- transaction number
- transaction type
- warehouse
- location
- item
- on-hand delta
- allocated delta
- on-hand after
- allocated after
- available after
- reference
- created at

Use chips for transaction type.

---

# Frontend API Client

Extend typed API client.

Suggested files:

```text
frontend/src/services/warehouseApi.ts
```

Add typed methods for:

```text
createOrder
getOrderDetail
allocateOrder
releaseTasks
startTask
completeTask
shipOrder
getInventoryTransactions
getOrderEvents
```

Use TanStack Query for loading.

Use mutation hooks for actions where practical.

Show loading and error states.

---

# Seed Data Updates

Do not break existing seed behavior.

Seed should remain idempotent.

It is acceptable to keep seeded orders/tasks as demo data.

If adding workflow demo data, keep it deterministic and avoid duplicates.

Do not seed shipped transactions unless necessary.

The workflows should be testable by creating a new order through API/UI.

---

# Backend Tests

Add tests covering:

1. Existing health/version tests still pass
2. Existing warehouse read tests still pass
3. Create order
4. Allocate order successfully
5. Allocation fails cleanly when stock is insufficient
6. Release tasks idempotently
7. Start task
8. Complete pick task
9. Complete pack task
10. Ship order
11. Shipment reduces on-hand and allocated inventory
12. Inventory transactions are created
13. Invalid workflow transitions return `409`

Tests should be runnable with:

```bash
cd backend
source .venv/bin/activate
pytest
```

If live PostgreSQL is unavailable, integration tests may skip clearly.

When local infrastructure is running and seeded, tests should pass.

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

- Prompt 03 workflow summary
- new transaction workflow APIs
- new frontend routes
- backend port `8050`
- frontend port `4001`
- validation commands
- known deferred capabilities

Update `ARCHITECTURE.md` with:

- warehouse workflow service
- allocation table
- inventory transaction ledger
- order event history
- transaction flow
- deferred items

If `docs/06_Codex/` exists, do not modify prior prompt files unless necessary.

---

# Validation Commands

Run or provide results for:

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
python -m app.db.seed_warehouse
pytest
```

Then validate live backend:

```bash
curl -sS http://localhost:8050/health | jq .
curl -sS http://localhost:8050/api/v1/warehouse/summary | jq .
curl -sS http://localhost:8050/api/v1/warehouse/orders | jq .
curl -sS http://localhost:8050/api/v1/warehouse/inventory-transactions | jq .
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
http://localhost:4001/warehouse/orders
http://localhost:4001/warehouse/orders/new
http://localhost:4001/warehouse/tasks
http://localhost:4001/warehouse/inventory-transactions
```

Manually validate this UI flow:

```text
Create Order
Allocate
Release Tasks
Start Pick Task
Complete Pick Task
Start Pack Task
Complete Pack Task
Ship Order
View Inventory Transactions
```

---

# Definition of Done

Prompt 03 is complete only when:

- new migration exists
- `wf_allocations` exists
- `wf_inventory_transactions` exists
- `wf_order_events` exists
- create order API works
- allocate order API works
- release tasks API works
- start task API works
- complete task API works
- ship order API works
- inventory transaction ledger API works
- order events API works
- inventory updates correctly on allocation and shipment
- allocation and shipment are atomic
- invalid workflow transitions return clear `409` errors
- existing read APIs still work
- existing health/version endpoints still work
- frontend order creation page works
- frontend order detail page works
- frontend task action buttons work
- frontend inventory transactions page works
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
4. Backend workflow APIs added
5. Frontend routes added
6. Backend validation results
7. Frontend validation results
8. Manual workflow validation result
9. Confirmation that infrastructure files were not modified
10. Any TODOs
11. Recommended Git commit message

Recommended commit message:

```text
feat: add warehouse transaction workflows
```

Do not proceed beyond this prompt.