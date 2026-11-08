# Migrations for an existing project

`../schema.sql` is the end state and builds a new project in one go. An existing project
(the live `machine-manager` project) moves to it in these steps, in order. Each file is
safe to run again.

| Step | When | What it does |
|---|---|---|
| `01-review-fixes.sql` | Any time (applied 2026-11-07) | `mm_apply` saves each change on its own, locks rows in id order, checks its input and can bring back a deleted record; adds `mm_file_refs`, `created_by`, an index for catch-up fetches and the nightly purge of old deletes. Works with both the old and new pages. |
| `02-copy-whiteboard.sql` | Right after the new Whiteboard is live on GitHub Pages | Copies every board, note, arrow and frame from `wb_boards` / `wb_items` into `mm_records` (tool `whiteboard`). Run it after the merge so nothing written by the old page is missed; running it again only adds what's missing. |
| `03-drop-old-whiteboard.sql` | Once the copied boards look right in the new Whiteboard | Removes `wb_boards`, `wb_items`, `wb_apply` and the `wb-files` storage policies. Can't be undone. |

After step 3, delete the empty `wb-files` bucket under **Storage** in the dashboard
(Supabase doesn't allow deleting buckets from SQL).
