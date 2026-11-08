// Runs the real mm-cloud.js openStore() for several simulated browsers against an in-memory server
// that behaves like mm_apply + Supabase realtime (version checks, per-change errors, revive of deleted
// records, tool-filtered live updates, paging by id). No network, no browser.
//
//   node tests/sync/sync_sim.js            (from the repo root)
const fs = require('fs'), vm = require('vm'), path = require('path');
const SRC = fs.readFileSync(path.join(__dirname, '../../mm-cloud.js'), 'utf8');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const failures = [];
const check = (name, ok, detail = '') => { if (!ok) failures.push(name); console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail ? ' — ' + detail : '')); };
const clone = o => JSON.parse(JSON.stringify(o));

function makeServer(){
  const rows = new Map(), subs = new Set();
  let clock = Date.parse('2026-11-07T12:00:00Z');
  const S = { rows, subs, down: false, latency: 5, failNext: 0, rpcCalls: 0, fetched: 0, msgs: 0, invalid: new Set() };
  const stamp = r => { r.updated_at = new Date(clock += 60000).toISOString(); };   // a minute per write
  S.broadcast = row => { for (const s of subs) if (s.filter(row)){ S.msgs++; setTimeout(() => s.cb(clone(row)), S.latency + Math.random() * 20); } };
  S.apply = (org, tool, changes) => {
    const order = changes.map((c, i) => i).sort((a, b) => String(changes[a].id) < String(changes[b].id) ? -1 : 1);
    const res = [];
    for (const i of order){
      const c = changes[i], k = `${org}|${tool}|${c.id}`, cur = rows.get(k);
      if (S.invalid.has(c.id)){ res[i] = { id: c.id, ok: false, row: null, error: 'value too long' }; continue; }
      if (c.base == null){
        if (cur && !cur.deleted){ res[i] = { id: c.id, ok: false, version: null, row: clone(cur) }; continue; }
        const r = cur || { org_id: org, tool, id: c.id, version: 0 };
        Object.assign(r, { data: c.data || {}, deleted: !!c.deleted, version: r.version + 1 }); stamp(r);
        rows.set(k, r); S.broadcast(r); res[i] = { id: c.id, ok: true, version: r.version, row: null }; continue;
      }
      if (!cur || cur.version !== c.base){ res[i] = { id: c.id, ok: false, version: null, row: cur ? clone(cur) : null }; continue; }
      if (c.data !== undefined) cur.data = c.data; if (c.deleted != null) cur.deleted = c.deleted; cur.version++; stamp(cur);
      S.broadcast(cur); res[i] = { id: c.id, ok: true, version: cur.version, row: null };
    }
    return res;
  };
  return S;
}

function makeClient(S, uid, role){
  const net = () => sleep(S.latency);
  return {
    auth: { getSession: async () => ({ data: { session: { user: { id: uid, email: uid + '@x' } } } }), signOut: async () => {} },
    from(table){
      const f = [], q = { limit: 1e9 };
      const api = {
        select(){ return api; }, order(){ return api; },
        eq(k, v){ f.push(r => r[k] === v); return api; },
        gt(k, v){ f.push(r => r[k] > v); return api; },
        gte(k, v){ f.push(r => r[k] >= v); return api; },
        limit(n){ q.limit = n; return api; },
        range(a, b){ q.range = [a, b]; return api; },
        then(res, rej){
          (async () => {
            await net();
            if (S.down) return { data: null, error: { message: 'offline' } };
            if (table === 'memberships') return { data: [{ role, org: { id: 'org1', name: 'PM1' } }], error: null };
            let all = [...S.rows.values()].filter(r => f.every(fn => fn(r))).sort((a, b) => a.id < b.id ? -1 : 1);
            all = q.range ? all.slice(q.range[0], q.range[1] + 1) : all.slice(0, q.limit);
            S.fetched += all.length;
            return { data: all.map(clone), error: null };
          })().then(res, rej);
        },
      };
      return api;
    },
    async rpc(name, args){
      await net(); S.rpcCalls++;
      if (S.down) return { data: null, error: { message: 'offline' } };
      if (S.failNext > 0){ S.failNext--; return { data: null, error: { message: 'boom' } }; }
      if (role === 'viewer') return { data: args.p_changes.map(c => ({ id: c.id, ok: false, row: null, error: 'row-level security' })), error: null };
      return { data: S.apply(args.p_org, args.p_tool, clone(args.p_changes)), error: null };
    },
    channel(){
      let cb, filter = () => true;
      const ch = {
        on(_, spec, fn){ cb = fn; const m = /^(\w+)=eq\.(.+)$/.exec(spec.filter || ''); if (m) filter = r => String(r[m[1]]) === m[2]; return ch; },
        subscribe(st){ S.subs.add({ filter, cb: row => cb({ new: row }) }); setTimeout(() => st('SUBSCRIBED'), 1); return ch; },
      };
      return ch;
    },
    storage: { from(){ return {}; } },
  };
}

function loadInstance(S, uid, role){
  const store = new Map(), listeners = {};
  const doc = { hidden: false, addEventListener(t, f){ (listeners['doc:' + t] = listeners['doc:' + t] || []).push(f); }, createElement: () => ({}) };
  const win = { MM_CONFIG: { supabaseUrl: 'x', supabaseKey: 'y' }, supabase: { createClient: () => makeClient(S, uid, role) },
    addEventListener(t, f){ (listeners[t] = listeners[t] || []).push(f); } };
  const ctx = { window: win, document: doc, location: { reload(){} }, console: { ...console, warn(){} },
    localStorage: { getItem: k => store.get(k) ?? null, setItem: (k, v) => store.set(k, String(v)), removeItem: k => store.delete(k) },
    setTimeout, clearTimeout, Promise, JSON, Object, Array, Map, Set, Math, Date, Number, String };
  win.window = win;
  vm.createContext(ctx); vm.runInContext(SRC, ctx);
  return { MMCloud: win.MMCloud, doc, fire: t => (listeners[t] || []).forEach(f => f({ preventDefault(){} })) };
}

function page(S, uid, role = 'editor', tool = 'consumables'){
  const inst = loadInstance(S, uid, role);
  const p = { data: {}, statuses: [], conflicts: 0, inst };
  p.store = inst.MMCloud.openStore(tool, {
    snapshot: () => p.data,
    onChange: (id, d, info) => { if (info.conflict) p.conflicts++; if (d == null) delete p.data[id]; else p.data[id] = clone(d); },
    onStatus: (s, d) => p.statuses.push(d ? `${s}:${d}` : s),
  });
  return p;
}
const ready = async (...ps) => { for (const p of ps) p.data = (await p.store.ready) || {}; };
const view = p => JSON.stringify(Object.keys(p.data).sort().map(k => [k, p.data[k]]));

(async () => {
  {
    const S = makeServer(), a = page(S, 'a'), b = page(S, 'b'); await ready(a, b);
    for (let i = 0; i < 50; i++){ a.data['a' + i] = { n: i }; a.store.save(); b.data['b' + i] = { n: i }; b.store.save(); await sleep(7); }
    await sleep(2500);
    check('two editors, 100 creates at once, converge', view(a) === view(b) && Object.keys(a.data).length === 100, `a=${Object.keys(a.data).length} b=${Object.keys(b.data).length}`);
  }
  {
    const S = makeServer(), a = page(S, 'a'), b = page(S, 'b'); await ready(a, b);
    a.data.x = { count: 1 }; a.store.save(); await sleep(800);
    a.data.x = { count: 5 }; b.data.x = { count: 9 }; a.store.save(); b.store.save(); await sleep(1500);
    check('same record edited at once: both end on one value', view(a) === view(b), `a=${JSON.stringify(a.data.x)} b=${JSON.stringify(b.data.x)}`);
  }
  {
    const S = makeServer(); S.latency = 400; const a = page(S, 'a'), b = page(S, 'b'); await ready(a, b);
    for (let i = 0; i <= 40; i++){ a.data.note = { text: 'x'.repeat(i) }; a.store.save(); await sleep(60); }
    await sleep(4000);
    check('typing on a slow connection: last text wins everywhere', a.data.note.text.length === 40 && view(a) === view(b));
  }
  {
    const S = makeServer(), a = page(S, 'a'), b = page(S, 'b'); await ready(a, b);
    S.down = true;
    for (let i = 0; i < 10; i++){ a.data['off' + i] = { i }; a.store.save(); }
    await sleep(600); const pend = a.store.pending();
    S.down = false; await sleep(6500);
    check('edits made offline are saved when the server is back', pend && Object.keys(b.data).length === 10, `b sees ${Object.keys(b.data).length}/10`);
  }
  {
    const S = makeServer(), a = page(S, 'a'), b = page(S, 'b'); await ready(a, b);
    a.data.card = { v: 1 }; a.store.save(); await sleep(800);
    delete a.data.card; b.data.card = { v: 2 }; a.store.save(); b.store.save(); await sleep(1500);
    check('delete vs edit at once converges', view(a) === view(b));
  }
  {
    const S = makeServer(), v = page(S, 'v', 'viewer'); await ready(v);
    v.data.z = { a: 1 }; v.store.save(); await sleep(500);
    check('viewer changes are not sent', S.rpcCalls === 0 && v.statuses.includes('viewonly'));
  }
  {
    const S = makeServer(), a = page(S, 'a'); await ready(a);
    S.invalid.add('bad');
    a.data.bad = { v: 1 }; a.data.good = { v: 1 }; a.store.save(); await sleep(800);
    const calls = S.rpcCalls;
    a.data.other = { v: 1 }; a.store.save(); await sleep(800);
    const resent = [...S.rows.keys()].some(k => k.endsWith('|bad'));
    check('a rejected change is reported once and not resent', a.statuses.some(s => s.startsWith('rejected:')) && !resent && S.rpcCalls === calls + 1 && !!a.data.bad,
      `statuses=${a.statuses.filter(s => s !== 'live' && s !== 'saving').join(',')}`);
    check('…the good change in the same batch was saved', [...S.rows.keys()].some(k => k.endsWith('|good')));
  }
  {
    const S = makeServer(), a = page(S, 'a'); await ready(a);
    S.down = true; a.data.k = { v: 1 }; a.store.save();
    await sleep(17000);
    const calls = S.rpcCalls;
    check('retries back off while the server is down', calls >= 2 && calls <= 3, `${calls} attempts in 17 s (fixed 5 s would be 4)`);
    S.down = false; await sleep(22000);
    check('…and save once it is back', S.rows.size === 1);
  }
  {
    const S = makeServer(), a = page(S, 'a', 'editor', 'consumables'), o = page(S, 'o', 'editor', 'outages'); await ready(a, o);
    const before = S.msgs;
    for (let i = 0; i < 10; i++){ a.data['c' + i] = { i }; } a.store.save(); await sleep(800);
    check('live updates go only to pages of the same tool', S.msgs - before === 10, `${S.msgs - before} messages for 10 changes with 2 pages open (one per tool)`);
  }
  {
    const S = makeServer(), a = page(S, 'a'), b = page(S, 'b'); await ready(a, b);
    for (let i = 0; i < 300; i++) a.data['r' + String(i).padStart(4, '0')] = { i };
    a.store.save(); await sleep(1500);
    delete a.data.r0001; a.store.save(); await sleep(800);
    const c = page(S, 'c'); await ready(c);
    check('initial load skips deleted records', Object.keys(c.data).length === 299 && !('r0001' in c.data));
    c.data.r0001 = { i: 'back' }; c.store.save(); await sleep(800);
    check('re-creating a deleted record brings it back for everyone', a.data.r0001 && a.data.r0001.i === 'back' && b.data.r0001 && b.data.r0001.i === 'back');
    // b misses live updates for a while, then catches up with only what changed
    S.subs.clear(); a.data.r0002 = { i: 'changed' }; a.store.save(); await sleep(600);
    const before = S.fetched; b.inst.doc.hidden = true; b.inst.fire('doc:visibilitychange');
    await sleep(10); b.inst.doc.hidden = false; await b.store.catchUp();
    check('catching up fetches only what changed', b.data.r0002 && b.data.r0002.i === 'changed' && S.fetched - before < 20, `${S.fetched - before} rows fetched (the tool has 300)`);
  }
  {
    const S = makeServer(), a = page(S, 'a'); await ready(a);
    for (let i = 0; i < 2500; i++) a.data['r' + String(i).padStart(5, '0')] = { i, text: 'Shower nozzle '.repeat(10) };
    a.store.save(); await a.store.flush();
    const b = page(S, 'b'); await ready(b);
    check('loading 2,500 records pages by id', Object.keys(b.data).length === 2500);
    let t = process.hrtime.bigint(); a.data.r00001.i = -1; a.store.save(); await a.store.flush(); const fullMs = Number(process.hrtime.bigint() - t) / 1e6;
    t = process.hrtime.bigint(); a.data.r00002.i = -2; a.store.save(['r00002']); await a.store.flush(); const oneMs = Number(process.hrtime.bigint() - t) / 1e6;
    check('saving one named record skips comparing the rest', S.rows.get('org1|consumables|r00002').data.i === -2, `full compare ${fullMs.toFixed(0)} ms, named ${oneMs.toFixed(0)} ms`);
  }
  console.log(`\n${failures.length ? 'FAILED: ' + failures.join(', ') : 'all passed'}`);
  process.exit(failures.length ? 1 : 0);
})();
