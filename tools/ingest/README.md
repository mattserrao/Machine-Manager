# MM LLM ingest

Turns mill files into the `llm.*` tables of one organization (see `supabase/llm.sql` and `supabase/SETUP.md`).

| File | What |
|---|---|
| `importers.py` | One importer per source: BUS sheets (.xlsx), JDE WO exports, Planner exports, RCFA log, Bonvoy CSVs, Pi series, documents (PDF text, OCR for scans, Word). Column names are in the `*_MAP` dicts, so real exports with other headers are a mapping change. The `Tagger` links every row to a PM1 position from the equipment register (exact match first; free text by name; equipment inherits its parent's position, so an HP shower belongs to its felt). Never reads the demo answer key. |
| `load.py` | Parses a folder and loads it: into Supabase through the `mm-llm-ingest` edge function (rows, original files, embeddings), or into a local Postgres for tests. Actions take the asset of the RCFA or WO they point to. |
| (reports) | Reports (Shift, Production, …) under `<source>/reports/` are ingested as `llm.reports` with their types from `tools/reports/registry.yaml`, then processed in the database (`mm_llm_process_reports`): downtime and daily production are extracted from them. See `tools/reports/README.md` |
| `verify_answers.py` | Runs every check in `demo-data/sim-mill/answers/answer_key.json` through the `mm_llm_*` tool functions as a signed-in viewer (RLS applies), or prints them as one SQL query for the live project. |

```
pip install "psycopg[binary]" openpyxl pypdf python-docx    # plus tesseract + poppler for scanned PDFs
python3 tools/ingest/load.py --source demo-data/sim-mill/out --backbone demo-data/sim-mill/backbone --dry-run
MM_INGEST_TOKEN=<token> python3 tools/ingest/load.py --source demo-data/sim-mill/out --backbone demo-data/sim-mill/backbone \
    --url https://<project>.supabase.co --key <publishable key> --files --embed
python3 tools/ingest/verify_answers.py --emit-sql --org "Sim Mill"
```

Tools the orchestrator calls (all read-only, RLS applies): `mm_llm_search_docs` (full text),
`mm_llm_search_docs_vec` (embeddings), `mm_llm_search_records` (BUS/WO/action/RCFA text), `mm_llm_position_history`,
`mm_llm_outage_scope`, `mm_llm_overdue_actions`, `mm_llm_bonvoy`, `mm_llm_pi_daily`, `mm_llm_pi_values`.
`mock_piwebapi.py` serves the generated Pi history with PI Web API's request and response shapes (`--selftest` checks it), so the Pi tool can later point at the real server by changing the base URL.

## Refreshing the saved answers

`ask_demo.py` runs the demo questions through the live `mm-llm-ask` function with an ingest token; the answers are
saved under each question id and shown to signed-in users on the MM LLM page. See `supabase/SETUP.md`.
