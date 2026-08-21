# Enterprise Operations Suite (EOS)

Enterprise Operations Suite is the demo application for the AI-Native AMS
Research Platform. Phase 1 established the reusable backend and frontend
foundation, and Prompt 02 adds the first business domain foundation.

## Current phase

Prompt 02 — Warehouse & Fulfillment Operations.

The application includes a FastAPI API, React/MUI application shell, request
IDs, structured logging, configuration, PostgreSQL and Redis connectivity
checks, and the Warehouse & Fulfillment domain model. The domain is
read-focused: allocation, picking confirmation, inventory adjustments,
shipment rating, carrier integrations, agents, incidents, and advanced
workflows remain deferred.

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

After applying the Alembic migrations, load deterministic demo data with:

    cd backend
    source .venv/bin/activate
    alembic upgrade head
    python -m app.db.seed_warehouse

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
- /warehouse/tasks
- /warehouse/shipments

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
