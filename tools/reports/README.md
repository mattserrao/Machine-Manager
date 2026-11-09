# Reports: one procedure from report to table

Every report Machine Manager reads goes through the same lifecycle, whoever writes it. Today the writer is the Sim Mill
generator; at a mill it would be a shift supervisor's form, the MES or an emailed export.

```
  where it's written                       the database (supabase/llm.sql, step 09)
  generated ─▶ submitted ──(ingest)──▶ ingested ─▶ extracted ─▶ indexed
       └──────────┴───────────────────────────┴──────────┴──▶ failed (+ error) ──▶ retry
```

| File | What |
|---|---|
| `registry.yaml` | The report types: cadence (shift or mill day), id pattern, required body fields, the tables each feeds (`extract`) and its search kind. Loaded into `llm.report_types` with every load, so the database checks the same fields |
| `lifecycle.py` | The envelope (report id, type, period, crew, author, body, text, status, history), the allowed state changes, validation, outbox paths, and the periods a type has |
| `daemon.py` | One idempotent reconcile loop: for each type and each period that has ended, generate the missing reports, validate, submit to the outbox. `push` ingests the outbox and processes it. Running it twice changes nothing |

**Types today:** `shift` (Shift Report, every 12 h, feeds `llm.downtime`) and `production` (Production Report:
Quality / Uptime / Tonnage / OME, every mill day, feeds `llm.production_daily`).

**In the database:** `llm.reports` holds each report as written (full-text searchable), `llm.report_events` logs every
status change, and `public.mm_llm_process_reports(token)` checks the required fields, runs the type's extractors
(`private.llm_extract_<table>`) and indexes it. Each extracted row keeps `report_id`, so a page can open the report a
number came from (`mm_llm_report`). A report that fails is marked `failed` with the error; fix it and ingest it again.

**Adding a report type:** add it to `registry.yaml`, write its producer (anything with `generate(type, mill_day, shift)`),
and, only if it feeds a table, an extractor in SQL plus its name in the `case` of `mm_llm_process_reports`.

```
python3 tools/sim-mill/run.py                              # Sim Mill: generates the year's reports into out/reports/
python3 tools/reports/daemon.py status --outbox demo-data/sim-mill/out/reports
python3 tools/reports/daemon.py push --outbox demo-data/sim-mill/out/reports --dsn "host=... dbname=..." --token <token>
```

A live job (later) runs the same loop every shift with `through` = now and pushes what's new.
