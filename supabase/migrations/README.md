# Migrations for an existing project

`../schema.sql` is the end state and builds a new project in one go. An existing project
(the live `machine-manager` project) moves to it in these steps, in order. Each file is
safe to run again.

| Step | When | What it does |
|---|---|---|
| `01-review-fixes.sql` | Any time (applied 2026-11-07) | `mm_apply` saves each change on its own, locks rows in id order, checks its input and can bring back a deleted record; adds `mm_file_refs`, `created_by`, an index for catch-up fetches and the nightly purge of old deletes. Works with both the old and new pages. |
| `02-copy-whiteboard.sql` | Right after the new Whiteboard is live on GitHub Pages | Copies every board, note, arrow and frame from `wb_boards` / `wb_items` into `mm_records` (tool `whiteboard`). Run it after the merge so nothing written by the old page is missed; running it again only adds what's missing. |
| `03-drop-old-whiteboard.sql` | Once the copied boards look right in the new Whiteboard | Removes `wb_boards`, `wb_items`, `wb_apply` and the `wb-files` storage policies. Can't be undone. |

| `../llm.sql` (step 04) | Any time (applied 2026-11-08) | MM LLM: the `llm` schema (equipment, BUS lines, WOs, actions, RCFAs, Bonvoy, packed Pi series, documents and searchable chunks with embeddings), ingest tokens, the `mm_llm_*` tool functions, and public demo orgs (`mm_llm_set_public`; Demo Mill is public). Only adds things; `mm_records` is untouched. The same file is the end state, so it is applied directly rather than copied here. |

| `05-sim-mill.sql` | Any time after step 04 (applied 2026-11-08) | Sim Mill: `llm.downtime`, `llm.production_daily`, `llm.position_runs`; the ingest also loads `records:mymachine` / `records:outages` / `records:consumables` for the token's org; `mm_llm_public_org` lists every public org (Demo Mill stays first); `mm_llm_summary` and `mm_llm_position_history` cover the new tables; new tools `mm_llm_downtime`, `mm_llm_downtime_summary`, `mm_llm_repeat_stops`, `mm_llm_rcfa_status`, `mm_llm_position_life`, `mm_llm_production`, `mm_llm_documents`, `mm_llm_bus_day`. Only adds; the same statements are in `../llm.sql` (end state). |

| `06-demo-sim-mill.sql` | Any time after step 05 (applied 2026-11-08) | Sim Mill becomes the only demo: `mm_demo_org` and `mm_demo_records` let signed-out visitors read the public demo org's My Machine, Outage Planning, Consumables and task-package records (read-only, no user ids). Access was switched with the admin functions: `mm_llm_set_public('Demo Mill', false)` (data kept), `mm_add_member('Sim Mill', 'demodemo@gmail.com', 'viewer')`, `mm_llm_grant_query('demodemo@gmail.com', 'Sim Mill', 40)` and `… 'Demo Mill', 0)`, and demodemo's Demo Mill membership removed. PM1 untouched. |

After step 3, delete the empty `wb-files` bucket under **Storage** in the dashboard
(Supabase doesn't allow deleting buckets from SQL).
