# MM LLM demo data

One fictional PM1 year (**Nov 1, 2025 – Oct 31, 2026**, demo "today" = Oct 31, 2026) for every MM LLM source.
All people and companies are fictional. Plan: *MM LLM - Demo Data Plan* in the Machine Manager Claude project.

| Path | What |
|---|---|
| `backbone.py` | Phase 1. Writes `demo-data/backbone/*.csv` and checks the storylines. `--check` runs in CI. |
| `storylines/*.yaml` | The planted stories the demo is built around. Each has a timeline (dates, the sources it shows up in, what happens) and demo questions with expected answers. |
| `../../demo-data/backbone/` | Equipment register (My Machine position ids, fake JDE asset nos.), outages, grade schedule, DuPont crew schedule, roster, vendors, Pi tags |

Machine assumptions: 26/30/33# linerboard at ~2,450/2,250/2,050 fpm, with 4–5 grade changes a week. Normal outages run 14 h on the 6-week grid. The one-week annual outage (Oct 5–11) replaces the Sep 30 slot.

```
pip install pyyaml
python3 tools/demo-data/backbone.py           # regenerate
python3 tools/demo-data/backbone.py --check   # what CI runs
```

Next phases generate the source files themselves (BUS sheets, Envoy CSVs, Pi series, JDE/Teams exports, RCFAs, vendor PDFs, drawings) from the backbone and storylines.
