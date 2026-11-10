# State machines in Machine Manager

Where the app's states live, what they are called, and which code owns each one. When a page needs to know "who is
looking", "is this saved" or "which org's data", use the owner listed here rather than combining flags.

## Made explicit (one owner, named states)

### 1. Who is looking: `MMCloud.access(tool?)` (mm-cloud.js)
| kind | Situation | Data the page uses | Edit |
|---|---|---|---|
| `unavailable` | Supabase isn't configured for this copy | this browser only | yes (local) |
| `offline` | the server can't be reached | this browser only | yes (local) |
| `signed-out` | nobody signed in, no public demo for this page | this browser only | yes (local) |
| `public-demo` | nobody signed in, viewing the public demo org (Sim Mill) | the demo org | no |
| `no-org` | signed in, in no organization yet | this browser only | yes (local) |
| `demo-member` | signed in to a public demo org (the demo account) | the demo org | by role |
| `member` | signed in to a real organization (PM1) | its own data only, **never** demo data | by role |

Used by: Outage Planning, the board tools (Whiteboard, Ops Task Library, Consumables), the mill-data
pages through `MMLLMOrg.resolve`, MM LLM and the home page. Tested in `tests/unit/cloud_states.test.js`.

### 2. Which org's mill data: `MMLLMOrg.resolve()` (mm-llm-org.js)
Built on `access()`. Returns `{ org, orgs, empty, real, error }`:
- `member` → its own org; `empty: true` until its data is loaded, and the page shows `MMLLMOrg.placeholder`.
- everyone else → the public demo orgs (a picker if there are several).
- `offline` → `error`.

Used by the Daily Journal, Downtime / RCFA, Vendor Reports, Bonvoy Report and MM LLM (which had its own copy of this logic).

### 3. Save indicator: `MMCloud.saveIndicator(el, opts)` (mm-cloud.js)
States shown: `saved` · `saving` · `viewonly` · `error` (Not saved) · `notloaded`. With several stores (Outage
Planning has two) the worst one wins: Not saved > Saving… > View only > Saved. "Can't reach the server" is shown
once per outage and again only after everything has recovered. Conflicts and refused changes are toasted. Live-update
status (`live` / `reconnecting`) goes to `opts.onConnection`.

Used by My Machine, Outage Planning and the board tools (three copies of this logic before).

### 4. A store's sync state: `store.state()` (mm-cloud.js `openStore`)
`{ phase: 'loading' | 'viewonly' | 'saving' | 'retrying' | 'idle', live: boolean }`, read-only. The store still
reports transitions through `onStatus` (`saving`, `saved`, `error`, `viewonly`, `rejected`, `live`, `reconnecting`).

## Already explicit (left as they are)
- **Appearance:** `MMTheme.pref()` is `system` | `light` | `dark` (mm-theme.js).
- **Fabric / roll due status:** `level` is `ok` | `soon` | `over` from `MM.lifeDays` and `MM.WARN_DAYS` (mm-machine.js), plus
  a position's `condition` flag.
- **Outage Planning screen:** `gate()` shows one of Loading · Couldn't load · Set up My Machine first · No outages scheduled,
  else the board.

## Small and local (left as they are)
- **MM LLM live question:** idle → asking (button disabled, "Thinking…") → answered or error, in `ask()` (MMLLM.html).
- **Example questions panel:** collapsed on load; the first question opens when it is expanded on a wide screen.

## Data, not app state
JDE WO status codes, Planner progress, RCFA status, Bonvoy direction and outage kinds come from the mill's own exports
and are stored as they arrive. The assistant reads them through its tools; the app doesn't drive them.
