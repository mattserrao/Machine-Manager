#!/bin/sh
# Run every test. Needs Node, Python with psycopg + playwright, and Postgres (PGDSN, default below).
set -e
cd "$(dirname "$0")/.."
: "${PGDSN:=host=localhost dbname=mm_test user=postgres password=pg}"
export PGDSN
python3 tools/stamp.py --check
node tests/unit/machine.test.js
node tests/sync/sync_sim.js
python3 tools/demo-data/backbone.py --check
python3 tools/demo-data/structured.py --check
psql "$PGDSN" -q -v ON_ERROR_STOP=1 -f tests/db/supabase-shim.sql -f supabase/schema.sql >/dev/null
python3 tests/db/test_schema.py
python3 -m http.server 8799 >/dev/null 2>&1 & SERVER=$!
trap 'kill $SERVER' EXIT
sleep 1
python3 tests/browser/smoke.py http://localhost:8799/
python3 tests/browser/boards.py http://localhost:8799/
python3 tests/browser/signed_in.py http://localhost:8799/
python3 tests/browser/theme.py http://localhost:8799/
python3 tests/browser/outages_demo.py http://localhost:8799/
python3 tests/browser/consumables_organizer.py http://localhost:8799/
echo "All tests passed."
