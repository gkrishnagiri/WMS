#!/usr/bin/env bash
set -euo pipefail
MODEL_CODE="${1:-OPENAI_GPT_5_4_MINI}"
if [[ ! "$MODEL_CODE" =~ ^[A-Za-z0-9_.-]+$ ]]; then echo "Invalid model code" >&2; exit 2; fi
curl -sS -X POST http://localhost:8050/api/v1/ai-costing/smoke-test/dry-run -H 'Content-Type: application/json' -d "{\"model_code\":\"${MODEL_CODE}\",\"message_text\":\"Reply with one short sentence confirming the model is reachable.\",\"max_output_tokens\":100,\"allow_real_model\":false}" 
printf '\n'
