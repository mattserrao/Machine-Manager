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
- **My Machine** stores the machine setup and each fabric, roll and refiner position as separate records, so two people updating different positions never collide.
- **Task Package Library** stores each package, step card, arrow and frame as its own record in `mm_records` (tool `task-packages`), with the same version checks and live updates as the Whiteboard. Attachments go to `mm-files` under `<organization id>/task-packages/<package id>/`. The five example packages are added once per organization, the first time an editor opens the tool.
- **Other tools** (Vendor Reports and the rest) are placeholders for now. When built, they store their data in the shared `mm_records` table and their files in the private `mm-files` bucket under `<organization id>/<tool>/`, with the same organization rules. No database changes are needed to add a tool.
- **Whiteboard**: each board, note, arrow and frame is its own row with a version number. A save only goes through if nobody changed that item since you loaded it. If someone did, you get their version and a short notice, so nothing is silently overwritten. Other people's changes appear live.
- **Whiteboard attachments** are stored in the private `wb-files` bucket under `<organization id>/<board id>/`. Files in both buckets are limited to 25 MB each.
- **Pan, zoom and the current board** are kept per person, in their browser.

## Free plan limits to know about

- **Pausing:** the project pauses after 7 days with no activity. Restore it from the dashboard. No data is lost.
- **Backups:** there are no automatic backups on the free plan. Use **File → Export** on important boards regularly, or move to Pro, which keeps daily backups for 7 days.
- **Limits:** 500 MB database, 1 GB file storage, 200 simultaneous live connections.
