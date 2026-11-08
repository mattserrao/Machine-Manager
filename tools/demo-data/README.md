# MM LLM demo data

One fictional PM1 year (**Nov 1, 2025 – Oct 31, 2026**, demo "today" = Oct 31, 2026) for every MM LLM source.
All people and companies are fictional. Plan: *MM LLM - Demo Data Plan* in the Machine Manager Claude project.

| Path | What |
|---|---|
| `backbone.py` | Phase 1. Writes `demo-data/backbone/*.csv` and checks the storylines. `--check` runs in CI. |
| `structured.py` | Phase 2. Writes `demo-data/out/` (not committed; regenerate it): 365 BUS daily sheets (.xlsx), weekly JDE WO exports (changes in the last 7 days) plus a full export as of Oct 31, weekly Planner exports, and the RCFA log. `_truth/` holds ground truth for later phases. `--check` runs in CI. |
| `pi_envoy.py` | Phase 3. Mock Pi series (`demo-data/out/pi/`: hourly averages for 39 tags, 1-minute data around the storyline events, `points.json`) and the daily Envoy exception reports derived from them (`demo-data/out/envoy/`). Driven by the grade schedule, outages and `_truth/downtime.csv`. `--check` re-derives every Envoy report from the CSVs, checks stops/breaks against the truth table, and holds the storyline flag dates (S01 Sep 22, S02 Mar 24/25, S04 Oct 13, S05 two PV fan flags). |
| `mock_piwebapi.py` | A local mock of PI Web API over that data (`/dataservers`, `/points`, `/streams/{webId}/recorded·interpolated·summary·value`, `/streamsets/recorded`, PI relative times, UTC responses). `--selftest` round-trips it. Swapping to the real Pi later is a base-URL change plus mill network/VPN and credentials. |
| `storylines/*.yaml` | The planted stories the demo is built around. Each has a timeline (dates, the sources it shows up in, what happens), demo questions with expected answers, and `records:`: the exact WOs, BUS lines, actions, RCFAs and breaks it puts into the data. |
| `../../demo-data/backbone/` | Equipment register (My Machine position ids, fake JDE asset nos.), outages, grade schedule, DuPont crew schedule, roster, vendors, Pi tags |

Machine assumptions: 26/30/33# linerboard at ~2,450/2,250/2,050 fpm, with 4–5 grade changes a week. Normal outages run 14 h on the 6-week grid. The one-week annual outage (Oct 5–11) replaces the Sep 30 slot.

```
pip install pyyaml openpyxl numpy
python3 tools/demo-data/backbone.py           # regenerate
python3 tools/demo-data/backbone.py --check   # what CI runs
python3 tools/demo-data/structured.py         # phase 2 files -> demo-data/out/
python3 tools/demo-data/structured.py --check
python3 tools/demo-data/pi_envoy.py           # phase 3 (after structured.py)
python3 tools/demo-data/pi_envoy.py --check
python3 tools/demo-data/mock_piwebapi.py      # http://localhost:8811/piwebapi
```

Envoy convention: a report covers one calendar day (`Period`) and arrives the next morning (`Report Date`). Storyline dates for Envoy flags are the Period.

Next: phase 4 (vendor PDFs, RCFA write-ups, drawings), reading measured values (e.g. vibration route readings) from the Pi series.
