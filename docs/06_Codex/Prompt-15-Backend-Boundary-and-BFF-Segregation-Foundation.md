# Prompt 15 – Backend Boundary and BFF Segregation Foundation

Prompt 15 adds local FastAPI backend-for-frontend boundaries for the Prompt 14
experiences while retaining one repository, one PostgreSQL database, and the
full backend API.

## Runtime mapping

| Experience | Frontend | Backend/BFF |
| --- | --- | --- |
| Full | 4001 | 8050 |
| Business | 4011 | 8061 |
| Operations | 4012 | 8062 |
| Simulation Lab | 4013 | 8063 |
| Observability Control | 4014 | 8064 |
| Agentic Support | 4015 | 8065 |

The BFFs are created by `backend/app/bff/app_factory.py` and use the shared
models, services, database lifecycle, middleware, CORS behavior, and
OpenTelemetry settings. Route groups are filtered by experience. Platform
metadata and lightweight facade summaries provide stable experience-specific
entrypoints without duplicating business logic.

This phase does not add authentication, authorization, ServiceNow, external
LLM calls, autonomous agents, new containers, new migrations, or independent
deployable services. It creates local process/runtime boundaries only. The
full backend and full frontend remain available for regression and fallback.
