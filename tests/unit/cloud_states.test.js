// The named states in mm-cloud.js: MMCloud.access() (who is looking) and MMCloud.saveIndicator() (Saved / Saving… /
// Not saved / View only), plus a store's state(). Runs the real file in a VM with a tiny fake Supabase client.
//
//   node tests/unit/cloud_states.test.js      (from the repo root)
const fs = require('fs'), vm = require('vm'), path = require('path');
const SRC = fs.readFileSync(path.join(__dirname, '../../mm-cloud.js'), 'utf8');
const failures = [];
const check = (name, ok, detail = '') => { if (!ok) failures.push(name); console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail ? ' — ' + detail : '')); };

// who: null (signed out) | { orgs: [{ id, name, role }] }; publicIds: the public demo orgs; demoOrg: mm_demo_org's row
function load({ enabled = true, who = null, publicIds = ['org-sim'], demoOrg = { id: 'org-sim', name: 'Sim Mill' }, down = false } = {}){
  const client = {
    auth: { getSession: async () => { if (down) throw new Error('network'); return { data: { session: who ? { user: { id: 'u1', email: 'a@b', user_metadata: {} } } : null } }; } },
    from(){ const api = { select: () => api, eq: () => api, then: (res) => res({ data: (who ? who.orgs : []).map(o => ({ role: o.role, org: { id: o.id, name: o.name } })), error: null }) }; return api; },
    rpc: async (name) => {
      if (name === 'mm_llm_public_org') return { data: publicIds.map(id => ({ id, name: id })), error: null };
      if (name === 'mm_demo_org') return demoOrg ? { data: [demoOrg], error: null } : { data: [], error: null };
      return { data: null, error: { message: 'unknown ' + name } };
    },
  };
  const win = { MM_CONFIG: enabled ? { supabaseUrl: 'x', supabaseKey: 'y' } : {}, supabase: enabled ? { createClient: () => client } : undefined, addEventListener(){} };
  const store = new Map();
  const ctx = { window: win, document: { addEventListener(){}, createElement: () => ({}) }, location: { reload(){} }, console,
    localStorage: { getItem: k => store.get(k) ?? null, setItem: (k, v) => store.set(k, String(v)), removeItem: k => store.delete(k) },
    setTimeout, clearTimeout, Promise, JSON, Object, Array, Map, Set, Math, Date, Number, String, Error };
  win.window = win; vm.createContext(ctx); vm.runInContext(SRC, ctx);
  return win.MMCloud;
}

(async () => {
  // ---- access(): exactly one named kind for each situation ----
  const kind = async (o, tool) => (await load(o).access(tool)).kind;
  check('access: no Supabase → unavailable', await kind({ enabled: false }) === 'unavailable');
  check('access: server down → offline', await kind({ down: true }) === 'offline');
  check('access: signed out, demo tool → public-demo', await kind({}, 'mymachine') === 'public-demo');
  check('access: signed out, no tool → public-demo when a demo org exists', await kind({}) === 'public-demo');
  check('access: signed out, not a demo tool → signed-out', await kind({}, 'whiteboard') === 'signed-out');
  check('access: signed out, no demo org → signed-out', await kind({ demoOrg: null }) === 'signed-out');
  check('access: signed in, no org → no-org', await kind({ who: { orgs: [] } }) === 'no-org');
  const pm1 = await load({ who: { orgs: [{ id: 'org-pm1', name: 'PM1', role: 'editor' }] } }).access();
  check('access: real org → member, can edit, not demo', pm1.kind === 'member' && pm1.canEdit && !pm1.demo && pm1.org.name === 'PM1');
  const demo = await load({ who: { orgs: [{ id: 'org-sim', name: 'Sim Mill', role: 'viewer' }] } }).access();
  check('access: the demo account → demo-member, view only, demo', demo.kind === 'demo-member' && !demo.canEdit && demo.demo);
  const pub = await load({}).access('outages');
  check('access: public demo is view only', pub.kind === 'public-demo' && !pub.canEdit && pub.demo && pub.role === 'viewer');

  // ---- saveIndicator(): worst state across stores, one warning per problem ----
  const C = load();
  const el = { textContent: '', dataset: {} }, toasts = [];
  const ind = C.saveIndicator(el, { toast: m => toasts.push(m), viewOnlyText: () => 'demo view only' });
  const a = { conflicts: 0 }, b = { conflicts: 0 }, ha = ind.handler(() => a), hb = ind.handler(() => b);
  ha('saving'); check('indicator: saving shows', el.textContent === 'Saving…' && el.dataset.state === 'saving');
  ha('saved'); check('indicator: saved shows', el.textContent === 'Saved');
  hb('error'); ha('saved');
  check('indicator: one store saved can’t hide the other failing', el.textContent === 'Not saved', el.textContent);
  hb('error'); check('indicator: the server warning is shown once', toasts.filter(t => /reach the server/.test(t)).length === 1, toasts.join(' | '));
  hb('saved'); check('indicator: back to saved when both are', el.textContent === 'Saved');
  a.conflicts = 2; ha('saved'); check('indicator: conflicts are reported, plural', toasts.some(t => /^2 items were changed/.test(t)));
  ha('viewonly'); ha('viewonly'); check('indicator: view only, own wording, warned once', el.textContent === 'View only' && toasts.filter(t => t === 'demo view only').length === 1);
  const before = el.textContent; ha('rejected', 'value too long');
  check('indicator: a refused change toasts without changing the state', el.textContent === before && toasts.some(t => /value too long/.test(t)));
  let conn = null; const ind2 = C.saveIndicator(el, { onConnection: x => { conn = x; } }); ind2.handler(null)('reconnecting');
  check('indicator: live updates go to onConnection', conn === 'reconnecting');
  ind.show('notloaded'); check('indicator: show() sets a state directly', el.textContent === 'Not loaded' && el.dataset.state === 'notloaded');

  console.log(`\n${failures.length ? 'FAILED: ' + failures.join(', ') : 'all passed'}`);
  process.exit(failures.length ? 1 : 0);
})();
