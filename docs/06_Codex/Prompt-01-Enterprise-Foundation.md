# Prompt 01 – Enterprise Foundation

## Role

You are the implementation engineer for the **AI-Native AMS Research Platform**.

Your task is to create the **Phase 1 Enterprise Application Foundation** for the demo application:

**Enterprise Operations Suite (EOS)**

You must implement only the foundational backend/frontend structure. Do not build business modules yet.

---

## Critical Instructions

This is an existing repository with a working Phase 0 infrastructure baseline.

You must not redesign the project.

You must not modify infrastructure files unless explicitly instructed.

You must not introduce alternative technologies.

You must not rename existing folders unless explicitly instructed.

You must preserve the current Docker and observability baseline.

---

## Existing Phase 0 Baseline

The following are already available and must remain undisturbed:

* PostgreSQL container
* Redis container
* OpenTelemetry Collector
* Prometheus
* Loki
* Grafana
* Existing `docker-compose.yml`
* Existing `observability/` configuration
* Existing `docs/` folder
* Existing Phase 0A architecture document

Do not modify the following paths:

```text
docker-compose.yml
observability/
docs/
data/
load-tests/
```

Exception: You may add documentation references to `README.md` and create `ARCHITECTURE.md`.

---

## Technology Stack

Use only the following technologies.

### Backend

* Python 3.12
* FastAPI
* Uvicorn
* Pydantic v2
* pydantic-settings
* SQLAlchemy 2.x
* Alembic
* psycopg
* redis-py
* pytest
* httpx

### Frontend

* React
* TypeScript
* Vite
* React Router
* TanStack Query
* Material UI

### Database

* PostgreSQL

### Cache / Queue Foundation

* Redis

### Observability

* Existing OpenTelemetry Collector
* Existing Prometheus
* Existing Loki
* Existing Grafana

Do not add Tempo in this prompt.

Tempo will be introduced later when real application traces exist.

---

## Application Name

The enterprise demo application is:

```text
Enterprise Operations Suite
```

Short name:

```text
EOS
```

Subtitle:

```text
AI-Native AMS Research Platform
```

The first business module, to be built in a later prompt, will be:

```text
Warehouse & Fulfillment Operations
```

Do not implement that module now.

---

## Repository Structure to Create

Create the following backend structure:

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── __init__.py
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── telemetry/
│   ├── utils/
│   ├── __init__.py
│   └── main.py
├── alembic/
├── tests/
├── requirements.txt
├── pyproject.toml
├── alembic.ini
├── .env.example
└── start_backend.sh
```

Create the following frontend structure:

```text
frontend/
├── src/
│   ├── assets/
│   ├── components/
│   ├── hooks/
│   ├── layouts/
│   ├── pages/
│   ├── router/
│   ├── services/
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── public/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── index.html
├── .env.example
└── start_frontend.sh
```

If any of these folders already exist, reuse them safely.

Do not delete unrelated folders.

---

## Backend Scope

Create a clean FastAPI application foundation.

### Required Backend Capabilities

Implement:

* Application startup
* Application shutdown
* Central configuration loading
* Structured logging
* Request ID middleware
* CORS middleware
* Central exception handling
* Database connection management
* Redis connection management
* Health endpoint
* Version endpoint
* Root endpoint
* Basic test coverage

Do not implement business APIs.

Do not create inventory/order/warehouse/shipping tables yet.

---

## Backend Configuration

Create configuration using `pydantic-settings`.

Support environment variables for:

```text
APP_NAME
APP_VERSION
APP_ENV
APP_HOST
APP_PORT
BACKEND_CORS_ORIGINS

DATABASE_HOST
DATABASE_PORT
DATABASE_NAME
DATABASE_USER
DATABASE_PASSWORD

REDIS_HOST
REDIS_PORT
REDIS_PASSWORD

LOG_LEVEL
REQUEST_ID_HEADER
```

For local development outside Docker, the default database host should be:

```text
localhost
```

The default PostgreSQL port should be:

```text
15432
```

This is important because the existing VM already has a host PostgreSQL service on port `5432`.

The default Redis host should be:

```text
localhost
```

The default Redis port should be:

```text
6379
```

---

## Backend Endpoints

### GET `/`

Return a basic API identity response:

```json
{
  "application": "Enterprise Operations Suite",
  "platform": "AI-Native AMS Research Platform",
  "status": "running"
}
```

### GET `/health`

Return HTTP 200 if the application process is alive.

Also check database and Redis connectivity.

Expected response shape:

```json
{
  "status": "healthy",
  "application": "Enterprise Operations Suite",
  "version": "0.1.0",
  "environment": "development",
  "checks": {
    "api": "healthy",
    "database": "healthy",
    "redis": "healthy"
  }
}
```

If database or Redis is unavailable, return HTTP 503 and show the failed component.

### GET `/version`

Return:

```json
{
  "application": "Enterprise Operations Suite",
  "platform": "AI-Native AMS Research Platform",
  "version": "0.1.0",
  "environment": "development",
  "python_version": "...",
  "git_commit": "...",
  "build_timestamp": "..."
}
```

If Git commit cannot be determined, return `"unknown"`.

---

## Backend Logging

Implement structured JSON-style logging where practical.

Every request should receive a request ID.

The request ID should be:

* accepted from an incoming header if present
* generated if missing
* returned in the response headers
* included in request logs

Use a simple implementation. Do not over-engineer.

---

## Backend Database

Create SQLAlchemy foundation:

* engine creation
* session factory
* dependency for request-scoped sessions
* declarative base
* connectivity check

Initialize Alembic.

Create an initial Alembic migration that does not create business tables yet. It can be an empty baseline migration.

---

## Backend Redis

Create a Redis connection manager:

* connect
* disconnect
* ping health check

Use async Redis client if appropriate for FastAPI.

---

## Backend Observability Hooks

Do not fully implement OpenTelemetry instrumentation yet.

Create a placeholder module:

```text
backend/app/telemetry/
```

It should contain clear TODOs and a safe initialization function that can be called from application startup without breaking anything.

Do not modify the existing Collector configuration.

Do not modify Prometheus, Loki, Grafana, or Docker Compose.

---

## Frontend Scope

Create the React foundation for EOS.

### Required Frontend Pages

Implement:

```text
/
```

Home / dashboard placeholder

```text
/health
```

Health status page

```text
/about
```

About page

---

## Frontend Layout

Create an enterprise-style application shell using Material UI.

It should include:

* top app bar
* sidebar navigation
* content area
* application title
* platform subtitle

Display:

```text
Enterprise Operations Suite
AI-Native AMS Research Platform
```

Use a clean enterprise visual design.

Do not build business workflows yet.

---

## Frontend Health Page

The frontend health page should call the backend `/health` endpoint.

Display:

* API status
* Database status
* Redis status
* Environment
* Application version

If the backend is unreachable, show a clear error message.

---

## Frontend About Page

Display:

* Application name
* Platform name
* Version
* Technology stack
* Current phase: Enterprise Foundation
* Future modules placeholder:

  * Warehouse & Fulfillment Operations
  * Inventory
  * Orders
  * Shipping
  * Batch Processing
  * Incident Simulation
  * Agentic AMS Platform

---

## Frontend Configuration

Create a frontend `.env.example`.

Support:

```text
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=Enterprise Operations Suite
VITE_PLATFORM_NAME=AI-Native AMS Research Platform
```

---

## Scripts

Create only these two scripts:

```text
backend/start_backend.sh
frontend/start_frontend.sh
```

Make them executable.

### `backend/start_backend.sh`

Should:

* create `.venv` if missing
* install dependencies
* start Uvicorn on port 8000

### `frontend/start_frontend.sh`

Should:

* install npm dependencies if needed
* start Vite dev server on port 3000 or 5173
* clearly print the frontend URL

Do not create or modify infrastructure scripts in the root `scripts/` folder.

---

## Tests

### Backend Tests

Create pytest tests for:

* `/`
* `/health`
* `/version`
* configuration loading

Tests should be runnable with:

```bash
cd backend
pytest
```

Where external PostgreSQL/Redis are required, tests should either:

* use the running local services, or
* clearly skip integration checks if services are unavailable

Do not make tests flaky.

### Frontend Tests

Create a minimal frontend validation setup.

At minimum:

* TypeScript build must pass
* Vite build must pass

A component test is optional in this prompt. Do not overcomplicate.

---

## Root Documentation

Update `README.md`.

Include:

* project overview
* current phase
* infrastructure status
* backend setup
* frontend setup
* environment variables
* validation commands
* repository structure
* how to run backend
* how to run frontend
* how to run tests

Create root-level:

```text
ARCHITECTURE.md
```

Keep it concise.

Include:

* current architecture
* current services
* backend modules
* frontend modules
* infrastructure baseline
* deferred items
* next phase

Do not duplicate the entire Phase 0A Word document.

---

## Files You Must Not Modify

Do not modify:

```text
docker-compose.yml
observability/
docs/
data/
load-tests/
```

Do not modify existing Git history.

Do not delete any existing folders.

---

## Implementation Order

Follow this order:

1. Inspect repository.
2. Create backend foundation.
3. Create backend tests.
4. Create frontend foundation.
5. Create frontend build setup.
6. Add startup scripts.
7. Update README.
8. Create ARCHITECTURE.md.
9. Run validation.
10. Provide final summary.

---

## Validation Commands to Run

At the end, run or provide results for:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Then:

```bash
cd frontend
npm install
npm run build
```

Then, if possible:

```bash
cd backend
./start_backend.sh
```

And verify:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/version
```

For frontend:

```bash
cd frontend
./start_frontend.sh
```

---

## Definition of Done

Prompt 01 is complete only when:

* backend folder exists
* frontend folder exists
* backend starts locally
* frontend starts locally
* `/` endpoint works
* `/health` endpoint works
* `/version` endpoint works
* database health check is implemented
* Redis health check is implemented
* backend tests exist
* backend tests pass or clearly document skipped integration checks
* frontend builds successfully
* README is updated
* ARCHITECTURE.md is created
* no infrastructure files are modified

---

## Final Response Required

When complete, provide:

1. Summary of created files
2. Summary of modified files
3. Confirmation that infrastructure files were not modified
4. Commands to run backend
5. Commands to run frontend
6. Validation commands and results
7. Any TODOs
8. Recommended Git commit message

Do not proceed beyond the scope of this prompt.
