# Machine-Manager
Various tools for machine management.

Without signing in, every tool runs as a demo that saves only in your browser. Signed-in users share data through Supabase, scoped to their organization. A real organization (e.g. PM1) only ever sees what its own people add or load: the mill-data pages (Daily, Downtime / RCFA, Vendor Reports, Bonvoy Report, MM LLM) show a placeholder until its files are loaded, and the Ops Task Library starts empty (the example packages can be added on request). The demo account and signed-out visitors see the Sim Mill demo. `RAG.html` is a placeholder for uploading documents for the assistant to search. See [supabase/SETUP.md](supabase/SETUP.md) for adding people and how access works.

## Layout

| File | What |
|---|---|
| `index.html`, `*.html` | One page per tool. Without signing in, every tool runs as a demo saved in your browser. |
| `mm-cloud.js` | Sign-in, who is looking (`access`), synced records (`openStore`), the save indicator and files for every tool. The app's named states are mapped in [docs/state-machines.md](docs/state-machines.md) |
| `mm-board.js`, `mm-board*.css` | The board engine behind the Whiteboard, Ops Task Library, Consumables Tracker and Daily |
| `mm-machine.js`, `mm-demo.js` | The machine model shared by My Machine and Outage Planning, and its demo data |
| `mm-demo-outages.js`, `mm-task-examples.js` | Outage Planning's demo outages, and the example task packages (Ops Task Library, and the outage demo) |
| `mm-records.js` | Each tool's record ids |
| `mm-theme.css` | The theme every page loads first: dark and light colour tokens, top bar, buttons, chips, toast (print always uses the light set) |
| `mm-theme.js` | Light / dark / system appearance, picked at the bottom of the app menu; saved on the signed-in account (or this browser when signed out) |
| `mm-icons.js` | The line-icon set used instead of emoji (`data-ic="name"` or `MMIcons.svg(name)`) |
| `mm-ui.js`, `mm-nav.js`, `mm-config.js` | Small shared helpers, the app menu, the Supabase project |
| `supabase/` | Database schema (`schema.sql`, MM LLM in `llm.sql`), migrations, the `mm-llm-ingest` edge function and setup notes |
| `tools/ingest/` | MM LLM importers, loader and answer-key check |
| `tools/demo-data/`, `demo-data/` | The original scripted demo year (Demo Mill: kept, no longer published) |
| `tools/sim-mill/`, `demo-data/sim-mill/` | Sim Mill: a data-generating model of The Paper Mill's mill (Python port of its sim), one modelled year, its answer key |
| `Daily.html`, `Downtime.html`, `VendorReports.html` | The data pages: the mill day, downtime / RCFA, vendor reports by position and run (`mm-llm-org.js`, `mm-data.css`). `DailyNotes.html` is the old Daily notes board |
| `tests/`, `tools/` | Tests (run on every pull request) and helper scripts |

After changing any shared file (`mm-*.js`, `mm-*.css`, `vendor/`), run `python3 tools/stamp.py` so browsers load the new versions together.

