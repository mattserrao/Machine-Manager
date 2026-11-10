#!/bin/sh
# Run every test. Needs Node, Python with psycopg + playwright, and Postgres (PGDSN, default below).
set -e
cd "$(dirname "$0")/.."
: "${PGDSN:=host=localhost dbname=mm_test user=postgres password=pg}"
export PGDSN
python3 tools/stamp.py --check
node tests/unit/machine.test.js
node tests/unit/outage_export.test.js
node tests/unit/cloud_states.test.js
node tests/unit/mcp.test.mjs
node tests/unit/rag.test.mjs
node tests/sync/sync_sim.js
python3 tools/demo-data/backbone.py --check
python3 tools/sim-mill/run.py --check
python3 tools/sim-mill/validate_ref.py
python3 tools/demo-data/structured.py --check
python3 tools/demo-data/structured.py >/dev/null && python3 tools/demo-data/pi_bonvoy.py --check
python3 tools/demo-data/pi_bonvoy.py >/dev/null && python3 tools/demo-data/docs.py --check
psql "$PGDSN" -q -v ON_ERROR_STOP=1 -f tests/db/supabase-shim.sql -f supabase/schema.sql -f supabase/llm.sql >/dev/null
python3 tests/db/test_schema.py
python3 tests/db/test_llm.py
python3 tests/db/test_rag.py
python3 tools/demo-data/docs.py >/dev/null
python3 tools/demo-data/downtime_feed.py >/dev/null
TOKEN=$(psql "$PGDSN" -Atc "select public.mm_llm_new_ingest_token('Demo Mill', 1)")
python3 tools/ingest/load.py --source demo-data/out --backbone demo-data/backbone --dsn "$PGDSN" --token "$TOKEN" >/dev/null
python3 tools/ingest/verify_answers.py --dsn "$PGDSN" --org 'Demo Mill'
python3 tools/sim-mill/run.py >/dev/null
TOKEN=$(psql "$PGDSN" -Atc "select public.mm_llm_new_ingest_token('Sim Mill', 1)")
python3 tools/ingest/load.py --source demo-data/sim-mill/out --backbone demo-data/sim-mill/backbone --dsn "$PGDSN" --token "$TOKEN" >/dev/null
python3 tools/ingest/verify_answers.py --dsn "$PGDSN" --org 'Sim Mill'
python3 -m http.server 8799 >/dev/null 2>&1 & SERVER=$!
trap 'kill $SERVER' EXIT
sleep 1
python3 tests/browser/smoke.py http://localhost:8799/
python3 tests/browser/boards.py http://localhost:8799/
python3 tests/browser/signed_in.py http://localhost:8799/
python3 tests/browser/rag.py http://localhost:8799/
python3 tests/browser/theme.py http://localhost:8799/
python3 tests/browser/outages_demo.py http://localhost:8799/
python3 tests/browser/consumables_organizer.py http://localhost:8799/
python3 tests/browser/demo_sim_mill.py http://localhost:8799/
echo "All tests passed."
