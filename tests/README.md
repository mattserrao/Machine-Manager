# Tests

| Folder | What | Needs |
|---|---|---|
| `db/` | `supabase/schema.sql` against plain Postgres (with `supabase-shim.sql` standing in for Supabase): access rules, version checks, one bad change never blocking a batch, races, deadlocks | Postgres, `psycopg` |
| `unit/` | `mm-machine.js`, `mm-demo.js`, `mm-records.js` | Node |
| `sync/` | `mm-cloud.js` sync with several simulated browsers: conflicts, offline, retries, catch-up, paging | Node |
| `browser/` | Every page loads cleanly; the board tools used end to end; signed in against a fake Supabase (`fake-supabase.js`); stored-XSS check | Python, Playwright |
| `browser/visual.py` + `compare.py` | Screenshots of the board tools in fixed states, to compare before and after a change (not run in CI) | Python, Playwright, Pillow |

They all run on every pull request (`.github/workflows/tests.yml`). To run them locally:

```sh
tools/test.sh            # everything; needs Postgres on localhost (PGDSN) and Playwright
```

Before/after screenshots of a refactor:

```sh
python3 tests/browser/visual.py http://localhost:8000/ /tmp/before   # on the old version
python3 tests/browser/visual.py http://localhost:8000/ /tmp/after    # on the new one
python3 tests/browser/compare.py /tmp/before /tmp/after
```
