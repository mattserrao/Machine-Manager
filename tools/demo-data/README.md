# MM LLM demo data

One fictional PM1 year (**Nov 1, 2025 – Oct 31, 2026**, demo "today" = Oct 31, 2026) for every MM LLM source.
All people and companies are fictional. Plan: *MM LLM - Demo Data Plan* in the Machine Manager Claude project.

| Path | What |
|---|---|
| `backbone.py` | Phase 1. Writes `demo-data/backbone/*.csv` and checks the storylines. `--check` runs in CI. |
| `structured.py` | Phase 2. Writes `demo-data/out/` (not committed; regenerate it): 365 BUS daily sheets (.xlsx), weekly JDE WO exports (changes in the last 7 days) plus a full export as of Oct 31, weekly Planner exports, and the RCFA log. `_truth/` holds ground truth for later phases. `--check` runs in CI. |
| `storylines/*.yaml` | The planted stories the demo is built around. Each has a timeline (dates, the sources it shows up in, what happens), demo questions with expected answers, and `records:`: the exact WOs, BUS lines, actions, RCFAs and breaks it puts into the data. |
| `../../demo-data/backbone/` | Equipment register (My Machine position ids, fake JDE asset nos.), outages, grade schedule, DuPont crew schedule, roster, vendors, Pi tags |

Machine assumptions: 26/30/33# linerboard at ~2,450/2,250/2,050 fpm, with 4–5 grade changes a week. Normal outages run 14 h on the 6-week grid. The one-week annual outage (Oct 5–11) replaces the Sep 30 slot.

```
pip install pyyaml openpyxl
python3 tools/demo-data/backbone.py           # regenerate
python3 tools/demo-data/backbone.py --check   # what CI runs
python3 tools/demo-data/structured.py         # phase 2 files -> demo-data/out/
python3 tools/demo-data/structured.py --check
```

Next: phase 3 (mock Pi series + Envoy, built on `_truth/downtime.csv`), then phase 4 (vendor PDFs, RCFA write-ups, drawings).
