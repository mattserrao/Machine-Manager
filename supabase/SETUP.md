# Accounts and shared data (Supabase)

Machine Manager runs in two modes:

- **Demo**: anyone who isn't signed in. Each tool saves to that browser only. Nothing is sent to the server.
- **Signed in**: data lives in the Supabase project `machine-manager` and is shared live with everyone in the same organization.

The schema (`schema.sql`) is already applied to the project. Re-running it is safe if it ever needs to be reapplied.

## One-time setup

1. **Turn off open sign-up.** In the Supabase dashboard go to **Authentication → Sign In / Providers** and, under **User Signups**, turn off **Allow new users to sign up**. Accounts are then created only by you. Even without this step, a self-registered account sees nothing until it's added to an organization.

## Adding a person

1. **Create the login.** Go to **Authentication → Users → Add user → Create new user**. Enter their email and a password, and tick **Auto Confirm User**.
2. **Give them access.** Go to **SQL Editor** and run:
   ```sql
   select public.mm_add_member('PM1', 'person@example.com', 'editor');
   ```
   The organization (`'PM1'` here) is created the first time it's used. Run the same line again with a different role to change their access.

| Role | Can do |
|---|---|
| `viewer` | See everything in the organization. Changes aren't saved. |
| `editor` | See and change everything in the organization. |
| `admin` | Same as editor, and can see the organization's member list. |

To remove someone, delete their user under **Authentication → Users**, which also removes their memberships.

### Shared (generic) logins

They work, but everyone on a shared login appears as the same person in the change history, and you can't remove one person without changing the password for all of them. Individual logins are better for anything holding customer data.

## How it fits together

- **Organizations** keep mills or customers apart. Every row and file belongs to one organization, and the database refuses access to anyone who isn't a member. This is enforced by row-level security, not by the web page.
- **Every tool uses the same sign-in.** Sign in from the account box on the home page or on any tool. Signing in or out in one tab updates the others.
- **Moving demo data:** the first time someone signs in to an organization that has nothing yet, My Machine and the Whiteboard offer to copy what they'd saved in that browser while in demo mode.
- **Every tool's data is in one table, `mm_records`**, one row per record (`tool` says which tool), and every tool's files are in the private `mm-files` bucket under `<organization id>/<tool>/`. Files are limited to 25 MB each. No database changes are needed to add a tool. Record ids for each tool are listed in `mm-records.js`.
- **Saving:** each record has a version number. A save only goes through if nobody changed that record since you loaded it; if someone did, you get their version and a short notice, so nothing is silently overwritten. Each change in a save stands on its own: one bad change is reported and skipped, the rest still save. Other people's changes appear live.
- **Whiteboard, Ops Task Library, Consumables Tracker** share one board engine (`mm-board.js`) and store each board, card, arrow and frame as its own record (tools `whiteboard`, `task-packages`, `consumables`). Attachments go to `mm-files` under `<organization id>/<tool>/<board id>/`. The five example task packages are added once per organization, the first time an editor opens the tool; the Consumables Tracker starts an organization with one empty PM1 board.
- **My Machine** stores the machine setup and each fabric, roll and refiner position as separate records, so two people updating different positions never collide. **Outage Planning** reads My Machine and the Ops Task Library and keeps its own outages, tasks and manning.
- **Deleting** is soft at first, so it syncs live and can be undone. A nightly job removes records deleted more than 90 days ago, and editors' pages remove stored files that no record points to any more (checked at most weekly).
- **Pan, zoom and the current board** are kept per person, in their browser.

## MM LLM data (the assistant's sources)

The assistant reads its own tables in the `llm` schema (`supabase/llm.sql`): BUS sheet lines, work orders, actions,
RCFAs, Envoy exceptions, Pi series, and documents split into searchable chunks. Members of an organization can
read its rows; nobody writes to them from the web page.

**Loading files** (BUS sheets, JDE / Planner exports, Envoy CSVs, Pi data, vendor reports, drawings):

1. In the **SQL Editor**, create a short-lived ingest token for the organization:
   ```sql
   select public.mm_llm_new_ingest_token('Demo Mill', 3);   -- org name, hours it stays valid
   ```
   Copy the token it returns; only a hash is stored.
2. Run the loader (see `tools/ingest/`) with that token. It sends everything through the `mm-llm-ingest` edge
   function, which checks the token, loads the rows, stores the original files in `mm-files` under
   `<organization id>/llm/`, and embeds document chunks with Supabase's built-in `gte-small` model (no outside key).
3. When it's done, remove the token: `delete from private.llm_ingest_tokens;`

A load replaces that organization's MM LLM rows. **Demo Mill** is the fictional organization the demo uses; it
has no members yet, so nobody can see it until someone is added with `mm_add_member('Demo Mill', ...)`.

## Updating the database

`schema.sql` is the full, current schema and builds a new project in one go (safe to re-run). For the existing project, apply the steps in `migrations/` in order; see `migrations/README.md`.

## Free plan limits to know about

- **Pausing:** the project pauses after 7 days with no activity. Restore it from the dashboard. No data is lost.
- **Backups:** there are no automatic backups on the free plan. Before customer data goes in, move to Pro ($25/month), which keeps daily backups for 7 days. Until then, export each tool regularly (**File → Export** on boards, **Export** in My Machine).
- **Limits**, and what uses them up (quotas cover every project in your Supabase organization, so the other app counts too):

| Limit | Free plan | What uses it |
|---|---|---|
| Database size | 500 MB per project (about 750,000 records) | Records; deleted ones are purged after 90 days |
| File storage | 1 GB | Attachments; files no record points to are removed |
| Egress | 5 GB / month | Loading tools (each record once), catching up after time away (only what changed), file downloads |
| Realtime messages | 2 million / month, 100 / second | One message per change for each open page of the same tool |
| Realtime connections | 200 at once | One per open tool page |

Check **Organization → Usage** in the dashboard monthly, and look closer if any line passes half its quota.

## Security settings

- **Authentication → Sign In / Providers:** keep **Allow new users to sign up** off (accounts are created by you).
- **Authentication → Password security:** turn on **leaked password protection** (blocks passwords known from data breaches; it's the one item the security advisor flags).
