#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${BASE_URL:-http://127.0.0.1:8002}"
ADMIN_TOKEN="${ADMIN_TOKEN:-change-admin-token}"
ANALYZE_ENDPOINT="/api/v1/leads/analyze"
MODE="dict"

curl -fsS "$BASE_URL/health" >/dev/null

TS=$(date +%s)
CLIENT_JSON=$(curl -fsS -X POST "$BASE_URL/api/v1/admin/clients"   -H "X-Admin-Token: $ADMIN_TOKEN"   -H "Content-Type: application/json"   -d '{"name":"Smoke","email":"smoke-'"$TS"'@example.com","plan":"starter","initial_credits":5}')

API_KEY=$(CLIENT_JSON="$CLIENT_JSON" python - <<'PY2'
import json, os
print(json.loads(os.environ['CLIENT_JSON'])['api_key'])
PY2
)

ANALYZE_JSON=$(curl -fsS -X POST "$BASE_URL$ANALYZE_ENDPOINT"   -H "X-API-Key: $API_KEY"   -H "Content-Type: application/json"   --data @examples/sample_input.json)

ANALYZE_JSON="$ANALYZE_JSON" MODE="$MODE" python - <<'PY2'
import json, os
payload = json.loads(os.environ['ANALYZE_JSON'])
if os.environ['MODE'] == 'list':
    assert isinstance(payload, list) and payload
else:
    assert isinstance(payload, dict) and isinstance(payload.get('result'), dict)
print('smoke ok')
PY2
