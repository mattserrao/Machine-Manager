# MM LLM ingest

Turns mill files into the `llm.*` tables of one organization (see `supabase/llm.sql` and `supabase/SETUP.md`).

| File | What |
|---|---|
| `importers.py` | One importer per source: BUS sheets (.xlsx), JDE WO exports, Planner exports, RCFA log, Envoy CSVs, Pi series, documents (PDF text, OCR for scans, Word). Column names are in the `*_MAP` dicts, so real exports with other headers are a mapping change. The `Tagger` links every row to a PM1 position from the equipment register (exact match first; free text by name; equipment inherits its parent's position, so an HP shower belongs to its felt). Never reads the demo answer key. |
| `load.py` | Parses a folder and loads it: into Supabase through the `mm-llm-ingest` edge function (rows, original files, embeddings), or into a local Postgres for tests. Actions take the asset of the RCFA or WO they point to. |
| `verify_answers.py` | Runs every check in `demo-data/answers/answer_key.json` through the `mm_llm_*` tool functions as a signed-in viewer (RLS applies), or prints them as one SQL query for the live project. |

```
pip install "psycopg[binary]" openpyxl pypdf python-docx    # plus tesseract + poppler for scanned PDFs
python3 tools/ingest/load.py --source demo-data/out --backbone demo-data/backbone --dry-run
MM_INGEST_TOKEN=<token> python3 tools/ingest/load.py --source demo-data/out --backbone demo-data/backbone \
    --url https://<project>.supabase.co --key <publishable key> --files --embed
python3 tools/ingest/verify_answers.py --emit-sql --org "Demo Mill"
```

Tools the orchestrator calls (all read-only, RLS applies): `mm_llm_search_docs` (full text),
`mm_llm_search_docs_vec` (embeddings), `mm_llm_search_records` (BUS/WO/action/RCFA text), `mm_llm_position_history`,
`mm_llm_outage_scope`, `mm_llm_overdue_actions`, `mm_llm_envoy`, `mm_llm_pi_daily`, `mm_llm_pi_values`.
The full Pi history is also served by the mock PI Web API (`tools/demo-data/mock_piwebapi.py`).
