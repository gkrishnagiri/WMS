# Warehouse Fulfillment Management System

A synthetic enterprise Warehouse Fulfillment Management System used as a
production-like laboratory for Application Management Services incident
resolution and future agentic support experiments.

## Project Status

Environment bootstrap phase.

## Goals

- Simulate frontend business users
- Simulate backend transactional processing
- Simulate asynchronous workers and queues
- Simulate scheduled and data-processing batches
- Simulate downstream integrations
- Provide realistic application, infrastructure, and business telemetry
- Inject realistic technical, functional, data, and performance failures
- Generate incidents from monitoring alerts and synthetic users
- Provide a controlled environment for testing autonomous incident diagnosis
  and remediation

## Current Environment

The initial development environment runs on an Azure Ubuntu VM.

The application and supporting services will be containerized so the
environment can be reproduced consistently.

## Architecture

The initial target architecture will include:

- React frontend
- FastAPI backend
- PostgreSQL
- Redis
- Background workers
- Batch processing
- Mock downstream services
- OpenTelemetry
- Prometheus
- Loki
- Tempo
- Grafana
- Alertmanager
- Synthetic load testing
- Scenario and fault-injection engine
- Incident/ticket simulator

## Development Principle

The simulated production environment must expose realistic evidence through
tickets, logs, metrics, traces, application state, business data, and service
dependencies so that future support agents can investigate incidents rather
than rely on hard-coded solutions.