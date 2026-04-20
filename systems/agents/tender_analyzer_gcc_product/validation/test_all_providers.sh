#!/bin/bash
set +e
SERVER_PID=""
TOTAL_PASSED=0
TOTAL_FAILED=0
TOTAL_SKIPPED=0

cleanup() {
  if [ -n "$SERVER_PID" ]; then
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" 2>/dev/null || true
    SERVER_PID=""
  fi
}
trap cleanup EXIT INT TERM

wait_for_health() {
  for i in {1..20}; do
    sleep 1
    curl -sf http://localhost:8000/health >/dev/null 2>&1 && return 0
  done
  return 1
}

test_provider() {
  local provider="$1"
  local model="$2"
  local env_name="$3"
  if [ "$provider" != "local" ] && [ -z "${!env_name}" ]; then
    echo "SKIP $provider"
    TOTAL_SKIPPED=$((TOTAL_SKIPPED+1))
    return
  fi
  export LLM_PROVIDER="$provider"
  export LLM_MODEL="$model"
  python3 -m src.main >/tmp/tender_product_$provider.log 2>&1 &
  SERVER_PID=$!
  if ! wait_for_health; then
    echo "FAIL $provider"
    TOTAL_FAILED=$((TOTAL_FAILED+1))
    cleanup
    return
  fi
  python3 validation/test_provider.py
  if [ $? -eq 0 ]; then
    TOTAL_PASSED=$((TOTAL_PASSED+1))
  else
    TOTAL_FAILED=$((TOTAL_FAILED+1))
  fi
  cleanup
}

[ -f .env ] && set -a && source .env && set +a
test_provider openai gpt-4o-mini OPENAI_API_KEY
test_provider anthropic claude-3-5-sonnet-20241022 ANTHROPIC_API_KEY
test_provider gemini gemini-1.5-flash GEMINI_API_KEY
test_provider local local-model DUMMY
echo "Passed: $TOTAL_PASSED"
echo "Failed: $TOTAL_FAILED"
echo "Skipped: $TOTAL_SKIPPED"
[ "$TOTAL_FAILED" -gt 0 ] && exit 1 || exit 0
