# Machine-Manager
Various tools for machine management.

Without signing in, every tool runs as a demo that saves only in your browser. Signed-in users share data through Supabase, scoped to their organization. See [supabase/SETUP.md](supabase/SETUP.md) for adding people and how access works.

## Layout

| File | What |
|---|---|
| `index.html`, `*.html` | One page per tool. Without signing in, every tool runs as a demo saved in your browser. |
| `mm-cloud.js` | Sign-in, synced records (`openStore`) and files for every tool |
| `mm-board.js`, `mm-board*.css` | The board engine behind the Whiteboard, Ops Task Library, Consumables Tracker and Daily |
| `mm-machine.js`, `mm-demo.js` | The machine model shared by My Machine and Outage Planning, and its demo data |
| `mm-records.js` | Each tool's record ids |
| `mm-theme.css` | The theme every page loads first: dark and light colour tokens, top bar, buttons, chips, toast (print always uses the light set) |
| `mm-theme.js` | Light / dark / system appearance, picked at the bottom of the app menu; saved on the signed-in account (or this browser when signed out) |
| `mm-icons.js` | The line-icon set used instead of emoji (`data-ic="name"` or `MMIcons.svg(name)`) |
| `mm-ui.js`, `mm-nav.js`, `mm-config.js` | Small shared helpers, the app menu, the Supabase project |
| `supabase/` | Database schema, migrations and setup notes |
| `tests/`, `tools/` | Tests (run on every pull request) and helper scripts |

After changing any shared file (`mm-*.js`, `mm-*.css`, `vendor/`), run `python3 tools/stamp.py` so browsers load the new versions together.

