# EOS Foundation Architecture

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

`app/core` contains configuration, JSON-style logging, request IDs, and
exception handlers. `app/db` contains the declarative base and session
management. `app/services` contains the Redis manager. `app/telemetry` is a
safe placeholder for later instrumentation. Alembic currently contains an
empty baseline migration; no business tables exist.

## Frontend modules

The shared shell provides the top bar, sidebar, and content area. The current
pages are the dashboard placeholder, dependency health view, and About page.
Business navigation and workflows are intentionally not implemented.

## Infrastructure baseline

The existing PostgreSQL, Redis, OpenTelemetry Collector, Prometheus, Loki,
and Grafana baseline remains in `docker-compose.yml` and `observability/`.
Those files are not part of the Phase 1 application changes.

## Deferred items

Application traces and Tempo, metrics instrumentation, background workers,
business models, warehouse workflows, inventory, orders, shipping, batch
processing, incident simulation, and agentic AMS behaviors are deferred.

## Next phase

Build the Warehouse & Fulfillment Operations module on top of this foundation,
including its domain models, APIs, UI workflows, and test coverage.
