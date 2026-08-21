# Prompt 02 – Warehouse & Fulfillment Domain Foundation

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

The enterprise demo application is:

**Enterprise Operations Suite (EOS)**

Prompt 01 has already created the enterprise application foundation.

Your task now is to implement the first business domain foundation:

**Warehouse & Fulfillment Operations**

This prompt must create the initial warehouse domain model, database schema, seed data, backend APIs, and frontend pages.

Do not implement agents, AI, ticket simulation, incident management, or advanced workflows yet.

---

## Current Confirmed Baseline

The repository currently has:

- Backend FastAPI foundation
- Frontend React/Vite/MUI foundation
- PostgreSQL connectivity
- Redis connectivity
- `/`, `/health`, `/version` backend endpoints
- Frontend running on port `4001`
- Backend running on port `8050`
- Commit already pushed:

```text
702c092 feat: add EOS enterprise foundation
```

Use the current repository structure and coding patterns.

Do not redesign Prompt 01 output.

---

## Critical Instructions

You must not redesign the project.

You must not rename the application.

You must not change infrastructure.

You must not modify Docker Compose.

You must not modify observability configuration.

You must not introduce new major frameworks.

You must preserve the existing backend and frontend foundation.

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

Use Material UI cards, tables, chips, and layout components.

---

# Objective

Implement the initial **Warehouse & Fulfillment Operations** domain foundation.

This includes:

1. Database schema
2. SQLAlchemy models
3. Pydantic schemas
4. Service layer
5. API routes
6. Deterministic seed data
7. Frontend navigation
8. Frontend pages
9. Tests
10. README and architecture updates

This is a domain foundation, not a full WMS.

Do not implement complex transactions such as allocation, picking confirmation, shipment rating, inventory adjustment approval, or carrier integration.

Those come later.

---

# Domain Scope

Implement the following domain concepts.

## Warehouse

A physical warehouse or fulfillment center.

Examples:

- Dallas Fulfillment Center
- Chicago Regional DC

## Zone

A logical area within a warehouse.

Examples:

- Receiving
- Storage
- Picking
- Packing
- Shipping
- Returns

## Location

A bin, rack, aisle, dock, or staging area inside a zone.

Examples:

- DAL-PICK-A01-B01
- CHI-STOR-B02-L03

## Item

A sellable or stocked product.

Examples:

- SKU-1001 Barcode Scanner
- SKU-2001 Wireless Headset

## Inventory Balance

Current item balance by warehouse/location.

Tracks:

- quantity on hand
- quantity allocated
- quantity available

Quantity available can be calculated as:

```text
quantity_on_hand - quantity_allocated
```

## Customer Order

A customer demand record.

This is not a full order management implementation yet.

## Order Line

A line item on a customer order.

## Fulfillment Task

A task representing warehouse work.

Examples:

- Pick
- Pack
- Ship
- Replenish
- Cycle Count

## Shipment

A basic outbound shipment record.

---

# Database Schema

Create an Alembic migration for the warehouse domain.

Use UUID primary keys where consistent with the existing project style. If the existing project has no UUID convention, use UUIDs.

Create these tables:

```text
wf_warehouses
wf_zones
wf_locations
wf_items
wf_inventory_balances
wf_orders
wf_order_lines
wf_fulfillment_tasks
wf_shipments
```

Use the `wf_` prefix for all Warehouse & Fulfillment tables.

---

## Table Requirements

### `wf_warehouses`

Fields:

```text
id
code
name
region
city
country
status
created_at
updated_at
```

Rules:

- `code` must be unique
- `status` should support active/inactive

---

### `wf_zones`

Fields:

```text
id
warehouse_id
code
name
zone_type
status
created_at
updated_at
```

Rules:

- `warehouse_id` references `wf_warehouses.id`
- unique constraint on `(warehouse_id, code)`

Suggested zone types:

```text
RECEIVING
STORAGE
PICKING
PACKING
SHIPPING
RETURNS
```

---

### `wf_locations`

Fields:

```text
id
warehouse_id
zone_id
code
aisle
bay
level
bin
location_type
capacity_units
status
created_at
updated_at
```

Rules:

- `warehouse_id` references `wf_warehouses.id`
- `zone_id` references `wf_zones.id`
- unique constraint on `(warehouse_id, code)`

---

### `wf_items`

Fields:

```text
id
sku
name
category
unit_of_measure
reorder_point
safety_stock
active
created_at
updated_at
```

Rules:

- `sku` must be unique
- `active` defaults to true

---

### `wf_inventory_balances`

Fields:

```text
id
warehouse_id
location_id
item_id
quantity_on_hand
quantity_allocated
created_at
updated_at
```

Rules:

- `warehouse_id` references `wf_warehouses.id`
- `location_id` references `wf_locations.id`
- `item_id` references `wf_items.id`
- unique constraint on `(location_id, item_id)`
- quantity fields must not be negative

The API response should expose:

```text
quantity_available = quantity_on_hand - quantity_allocated
```

---

### `wf_orders`

Fields:

```text
id
order_number
customer_name
order_type
priority
status
requested_ship_date
created_at
updated_at
```

Rules:

- `order_number` must be unique

Suggested statuses:

```text
NEW
ALLOCATED
PICKING
PACKING
SHIPPED
CANCELLED
```

Suggested priorities:

```text
LOW
NORMAL
HIGH
URGENT
```

---

### `wf_order_lines`

Fields:

```text
id
order_id
item_id
line_number
quantity_ordered
quantity_allocated
quantity_shipped
created_at
updated_at
```

Rules:

- `order_id` references `wf_orders.id`
- `item_id` references `wf_items.id`
- unique constraint on `(order_id, line_number)`
- quantity fields must not be negative

---

### `wf_fulfillment_tasks`

Fields:

```text
id
task_number
order_id
order_line_id
warehouse_id
task_type
status
priority
assigned_to
due_at
created_at
updated_at
```

Rules:

- `task_number` must be unique
- `order_id` references `wf_orders.id`
- `order_line_id` references `wf_order_lines.id`, nullable
- `warehouse_id` references `wf_warehouses.id`

Suggested task types:

```text
PICK
PACK
SHIP
REPLENISH
CYCLE_COUNT
```

Suggested statuses:

```text
OPEN
IN_PROGRESS
BLOCKED
COMPLETED
CANCELLED
```

---

### `wf_shipments`

Fields:

```text
id
shipment_number
order_id
warehouse_id
carrier
tracking_number
status
shipped_at
created_at
updated_at
```

Rules:

- `shipment_number` must be unique
- `order_id` references `wf_orders.id`
- `warehouse_id` references `wf_warehouses.id`

Suggested statuses:

```text
PLANNED
READY
SHIPPED
DELIVERED
EXCEPTION
```

---

# Backend Implementation

Create backend modules under the existing structure.

Suggested structure:

```text
backend/app/models/warehouse.py
backend/app/schemas/warehouse.py
backend/app/services/warehouse_service.py
backend/app/api/routes/warehouse.py
backend/app/db/seed_warehouse.py
```

Reuse existing configuration, database, logging, and API router patterns from Prompt 01.

Do not duplicate infrastructure code.

---

## API Prefix

Use:

```text
/api/v1/warehouse
```

Register the router in the existing FastAPI application.

---

## Required API Endpoints

Implement read-focused endpoints.

### `GET /api/v1/warehouse/summary`

Return dashboard summary:

```json
{
  "warehouses": 2,
  "locations": 12,
  "items": 8,
  "inventory_units_on_hand": 1250,
  "open_orders": 4,
  "open_tasks": 6,
  "shipments_in_progress": 2,
  "low_stock_items": 3
}
```

Use actual database queries.

---

### `GET /api/v1/warehouse/warehouses`

Return list of warehouses.

Support optional query parameter:

```text
status
```

---

### `GET /api/v1/warehouse/warehouses/{warehouse_id}`

Return warehouse detail including zones and location count.

---

### `GET /api/v1/warehouse/items`

Return list of items.

Support optional query parameters:

```text
active
category
search
```

Search should match SKU or item name.

---

### `GET /api/v1/warehouse/inventory`

Return inventory balances enriched with:

- warehouse code/name
- location code
- item SKU/name
- quantity on hand
- quantity allocated
- quantity available
- low stock flag

Support optional query parameters:

```text
warehouse_id
sku
low_stock_only
```

Low stock means:

```text
quantity_available <= item.reorder_point
```

---

### `GET /api/v1/warehouse/orders`

Return customer orders with summary line counts.

Support optional query parameters:

```text
status
priority
```

---

### `GET /api/v1/warehouse/tasks`

Return fulfillment tasks.

Support optional query parameters:

```text
status
task_type
warehouse_id
```

---

### `GET /api/v1/warehouse/shipments`

Return shipments.

Support optional query parameters:

```text
status
carrier
```

---

# Seed Data

Create deterministic seed data.

The seed should be idempotent.

Running it multiple times must not create duplicates.

Create a script or module runnable as:

```bash
cd backend
source .venv/bin/activate
python -m app.db.seed_warehouse
```

Seed at least:

```text
2 warehouses
6 zones
12 locations
8 items
16 inventory balances
5 orders
10 order lines
8 fulfillment tasks
4 shipments
```

Use realistic demo data.

Example warehouses:

```text
DAL-FC-01 Dallas Fulfillment Center
CHI-RDC-01 Chicago Regional Distribution Center
```

Example item categories:

```text
Electronics
Accessories
Packaging
Maintenance
```

Keep seed values deterministic and enterprise-demo friendly.

---

# Frontend Implementation

Extend the existing EOS frontend.

Do not replace the application shell.

Do not change the frontend port away from `4001`.

Use the existing Material UI style and routing.

---

## Navigation

Add sidebar navigation entries:

```text
Dashboard
Warehouse
Inventory
Orders
Fulfillment Tasks
Shipments
Health
About
```

Do not remove existing Health or About pages.

---

## Required Frontend Routes

Create:

```text
/warehouse
/warehouse/inventory
/warehouse/orders
/warehouse/tasks
/warehouse/shipments
```

Existing routes should continue working:

```text
/
/health
/about
```

---

## Warehouse Overview Page

Route:

```text
/warehouse
```

Display:

- page title: Warehouse & Fulfillment Operations
- summary cards from `/api/v1/warehouse/summary`
- warehouse list
- low-stock count
- open orders count
- open tasks count
- shipments in progress count

Use Material UI cards and tables.

No charting library.

---

## Inventory Page

Route:

```text
/warehouse/inventory
```

Display inventory table with:

- warehouse
- location
- SKU
- item name
- on hand
- allocated
- available
- low stock indicator

Add simple filters if practical:

- search by SKU/name
- low stock only

---

## Orders Page

Route:

```text
/warehouse/orders
```

Display orders table with:

- order number
- customer
- status
- priority
- requested ship date
- line count

---

## Fulfillment Tasks Page

Route:

```text
/warehouse/tasks
```

Display tasks table with:

- task number
- task type
- status
- priority
- warehouse
- assigned to
- due date

Use chips for status and priority.

---

## Shipments Page

Route:

```text
/warehouse/shipments
```

Display shipments table with:

- shipment number
- order number
- warehouse
- carrier
- tracking number
- status
- shipped date

---

# Frontend API Client

Create or extend a typed API client.

Suggested file:

```text
frontend/src/services/warehouseApi.ts
```

Use `VITE_API_BASE_URL`.

Use TanStack Query for data loading.

Show clear loading and error states.

Do not hardcode backend data in the frontend except as fallback labels.

---

# Tests

## Backend Tests

Add tests for:

```text
GET /api/v1/warehouse/summary
GET /api/v1/warehouse/warehouses
GET /api/v1/warehouse/items
GET /api/v1/warehouse/inventory
```

Tests should not be flaky.

If live PostgreSQL is unavailable, integration tests may skip clearly.

But when local infrastructure is running, tests should pass.

Existing Prompt 01 tests must continue passing.

Command:

```bash
cd backend
source .venv/bin/activate
pytest
```

---

## Frontend Validation

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

- Warehouse & Fulfillment Operations module
- new API endpoints
- seed data command
- frontend route list
- validation commands

Update `ARCHITECTURE.md` with:

- new warehouse domain module
- new database tables
- new API routes
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
pytest
```

Then:

```bash
curl -sS http://localhost:8050/api/v1/warehouse/summary | jq .
curl -sS http://localhost:8050/api/v1/warehouse/warehouses | jq .
curl -sS http://localhost:8050/api/v1/warehouse/inventory | jq .
```

Then:

```bash
cd frontend
npm install
npm run build
```

Then start frontend if needed:

```bash
cd frontend
./start_frontend.sh
```

Confirm UI pages are available at:

```text
http://localhost:4001/warehouse
http://localhost:4001/warehouse/inventory
http://localhost:4001/warehouse/orders
http://localhost:4001/warehouse/tasks
http://localhost:4001/warehouse/shipments
```

---

# Definition of Done

Prompt 02 is complete only when:

- Alembic migration exists
- Warehouse tables exist
- SQLAlchemy models exist
- Pydantic schemas exist
- Service layer exists
- Warehouse router exists
- Seed script exists and is idempotent
- Seed data loads successfully
- `/api/v1/warehouse/summary` works
- `/api/v1/warehouse/warehouses` works
- `/api/v1/warehouse/items` works
- `/api/v1/warehouse/inventory` works
- `/api/v1/warehouse/orders` works
- `/api/v1/warehouse/tasks` works
- `/api/v1/warehouse/shipments` works
- Frontend routes exist
- Frontend build passes
- Existing health/version endpoints still work
- Existing tests still pass
- README updated
- ARCHITECTURE.md updated
- No infrastructure files modified

---

# Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Alembic migration name
4. Seed command and result
5. Backend validation results
6. Frontend validation results
7. Confirmation that infrastructure files were not modified
8. Any TODOs
9. Recommended Git commit message

Recommended commit message:

```text
feat: add warehouse fulfillment domain foundation
```

Do not proceed beyond this prompt.