# MM LLM demo data

One fictional PM1 year (**Nov 1, 2025 – Oct 31, 2026**, demo "today" = Oct 31, 2026) for every MM LLM source.
All people and companies are fictional. Plan: *MM LLM - Demo Data Plan* in the Machine Manager Claude project.

| Path | What |
|---|---|
| `backbone.py` | Phase 1. Writes `demo-data/backbone/*.csv` and checks the storylines. `--check` runs in CI. |
| `structured.py` | Phase 2. Writes `demo-data/out/` (not committed; regenerate it): 365 BUS daily sheets (.xlsx), weekly JDE WO exports (changes in the last 7 days) plus a full export as of Oct 31, weekly Planner exports, and the RCFA log. `_truth/` holds ground truth for later phases. `--check` runs in CI. |
| `pi_envoy.py` | Phase 3. Mock Pi series (`demo-data/out/pi/`: hourly averages for 39 tags, 1-minute data around the storyline events, `points.json`) and the daily Envoy exception reports derived from them (`demo-data/out/envoy/`). Driven by the grade schedule, outages and `_truth/downtime.csv`. `--check` re-derives every Envoy report from the CSVs, checks stops/breaks against the truth table, and holds the storyline flag dates (S01 Sep 22, S02 Mar 24/25, S04 Oct 13, S05 two PV fan flags). |
| `mock_piwebapi.py` | A local mock of PI Web API over that data (`/dataservers`, `/points`, `/streams/{webId}/recorded·interpolated·summary·value`, `/streamsets/recorded`, PI relative times, UTC responses). `--selftest` round-trips it. Swapping to the real Pi later is a base-URL change plus mill network/VPN and credentials. |
| `docs.py` | Phase 4. `demo-data/out/docs/`: 65 vendor reports (PDF: clothing surveys, trial reports, vibration routes, roll service, shower audits, refiner plate reports), 13 RCFA write-ups (.docx), 16 drawings (PDF, machine direction right to left) and 8 reference charts (PDF + typed CSV). Measured values come from the Pi series and the phase 2 exports. Three are scanned (no text layer, need OCR) and one has a rotated page. `_truth/documents.json` is the answer key: every field an extractor should find. `--check` extracts text from every document and finds each field (and OCRs the scanned ones when tesseract is installed). |
| `storylines/*.yaml` | The planted stories the demo is built around. Each has a timeline (dates, the sources it shows up in, what happens), demo questions with expected answers, and `records:`: the exact WOs, BUS lines, actions, RCFAs and breaks it puts into the data. |
| `../../demo-data/backbone/` | Equipment register (My Machine position ids, fake JDE asset nos.), outages, grade schedule, DuPont crew schedule, roster, vendors, Pi tags |

Machine assumptions: 26/30/33# linerboard at ~2,450/2,250/2,050 fpm, with 4–5 grade changes a week. Normal outages run 14 h on the 6-week grid. The one-week annual outage (Oct 5–11) replaces the Sep 30 slot.

```
pip install pyyaml openpyxl numpy reportlab pypdf python-docx pillow
python3 tools/demo-data/backbone.py           # regenerate
python3 tools/demo-data/backbone.py --check   # what CI runs
python3 tools/demo-data/structured.py         # phase 2 files -> demo-data/out/
python3 tools/demo-data/structured.py --check
python3 tools/demo-data/pi_envoy.py           # phase 3 (after structured.py)
python3 tools/demo-data/pi_envoy.py --check
python3 tools/demo-data/mock_piwebapi.py      # http://localhost:8811/piwebapi
python3 tools/demo-data/docs.py               # phase 4 (after pi_envoy.py)
python3 tools/demo-data/docs.py --check
```

Envoy convention: a report covers one calendar day (`Period`) and arrives the next morning (`Report Date`). Storyline dates for Envoy flags are the Period.

Next: phase 5 — load the Demo Mill organization in Supabase through the importers, and run the answer key.
