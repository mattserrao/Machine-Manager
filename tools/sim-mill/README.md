# Sim Mill: a data-generating model of The Paper Mill's mill

The public demo organization, **Sim Mill**, built from a model rather than a script. It is the only demo: signed-out
visitors and the demo account (`demodemo@gmail.com`, a viewer with live questions) see it in every tool; Demo Mill is
kept but no longer published. The model is a Python port of
the simulation in [the-paper-mill](https://github.com/mattserrao/the-paper-mill), stripped of its 3D view and game
systems on the `sim-headless` branch there. It runs one realistic year of the game's own recycled-board
mill and writes every Machine Manager source. The year is written for Nov 1 2025 – Oct 31 2026 (the base year) and
**rolls forward** in whole 6-week outage cycles so the demo stays current (see *The roll* below). Plan: *Sim Mill - Plan* in the Machine Manager Claude project.

| Path | What |
|---|---|
| `config/mill.yaml` | Machine (fourdrinier, 2 refiners, 2 press nips, 4 uno-run dryer sections of 5 cans with 5 felt rolls each), grades 24/28/31/34 Super, calendar (20 h outages every 6 weeks), realism rates, vendors, roster, clothing / plate / roll life, consumables |
| `config/plants.yaml` | The five planted faults F1–F5. Everything else is emergent |
| `reference/` | From the-paper-mill `sim-headless`: the upset catalogue, critical assets, reliability constants and grades (`catalog.json`), the reference year's per-grade tag statistics and event summary |
| `simmill/model.py` | Grade campaigns, position life, every stop (outages, upsets at a year's MTBF, sheet breaks, bearing faults found on the route or failing, motors, drives, the planted faults), RCFA rule |
| `simmill/process.py` | Hourly Pi values for 47 tags, 1-minute windows around F1–F5, and the Envoy rule (same as Demo Mill's) |
| `simmill/records.py` | JDE work orders, Planner actions, BUS issues, RCFAs and their actions |
| `simmill/docs.py` | Vendor reports (clothing surveys, felt analysis, vibration routes, shower audits, plate reports, roll service, steam surveys), RCFA write-ups, drawings, reference charts |
| `simmill/emit.py` | Writers, in Demo Mill's layouts, plus three new feeds: downtime events, daily production, position runs |
| `simmill/mm_records.py` | My Machine (machine + 35 positions with run history and condition notes), the task-package library, Outage Planning (the last three outages done with their packages, the next one being planned, the one after started, all from one change plan) and Consumables records |
| `packages.js` | Sim Mill's task-package library (forming fabric, press felt, dryer felt, felt roll, refiner plates, stock prep cleaners), laid out by the Task Library's own code |
| `roll.py` | The scheduled roll: regenerate for the current cycle, check, reload Sim Mill (rows, records, files, embeddings) and re-ask the demo questions |
| `run.py` | Generate (`demo-data/sim-mill/backbone/`, committed; `demo-data/sim-mill/out/`, not committed). `--check` holds the targets and the planted faults |
| `validate_ref.py` | Holds the port to the reference model: per-grade running medians of 15 tags, break rate, unplanned stops, outages |

```
pip install pyyaml openpyxl numpy reportlab pypdf python-docx
python3 tools/sim-mill/run.py --check        # ~10 s: generate to a temp folder and check
python3 tools/sim-mill/validate_ref.py       # port vs the-paper-mill reference year
python3 tools/sim-mill/run.py                # write demo-data/sim-mill/out/
```

**The roll.** `run.py --cycles k` moves every date by k × 42 days (outage grid, weekdays and the planted faults keep
their places; the Keel route stays on the base year's second Wednesdays); `--auto` picks the cycles that have passed.
Dates written in the code go through `B()` / `BT()` and `tx()` in `simmill/base.py`; the answer key is written as
`answers/answer_key.base.json` and rendered to `answers/answer_key.json` (month facts like "the worst month for breaks"
are read from the generated data, since calendar months don't move with the roll). A scheduled task runs
`roll.py` weekly; it does work only when a new cycle has started. Position histories also get two or three runs before
the modelled year (their own random stream, so the year itself is unchanged).

**Targets** (agreed): 1–3 sheet breaks a day (1.46), 15–25 unplanned stops over 1 h a year (20), 10–20 RCFAs (14),
8 outages of 20 h on the 6-week grid.

**Planted faults**: F1 2nd press top felt fills early (HP shower nozzles plugged, changed at 34 days) ·
F2 reel drum DS bearing found on the route, missed at the Aug 19 outage (no bearing in stores), now 0.42 in/s ·
F3 REF 2 plates wearing fast, both refiners due Nov 11 with one set on hand · F4 forming fabric holed by a wad, its
wad-detector action six months overdue · F5 3rd section DS rotary joint leaks three times, no RCFA.

**Load** (the org is created by its first ingest token; make it public once loaded):
```sql
select public.mm_llm_new_ingest_token('Sim Mill', 3);
select public.mm_llm_set_public('Sim Mill', true);
```
```
python3 tools/ingest/load.py --source demo-data/sim-mill/out --backbone demo-data/sim-mill/backbone \
    --url https://<project>.supabase.co --key <publishable key> --token <token> --files --embed
python3 tools/ingest/verify_answers.py --emit-sql --org 'Sim Mill'     # paste in the SQL editor: 31 checks
```
