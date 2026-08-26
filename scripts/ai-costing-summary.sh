#!/usr/bin/env bash
set -euo pipefail
curl -sS http://localhost:8050/api/v1/ai-costing/summary
printf '\n'
curl -sS http://localhost:8050/api/v1/ai-costing/models
printf '\n'
