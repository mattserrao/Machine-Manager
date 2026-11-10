// Machine Manager — shared sign-in, data and file storage for every tool page.
// Load after vendor/supabase-*.js and mm-config.js. Exposes window.MMCloud.
//
// Signed out  → demo mode. The demo tools (My Machine, Outage Planning, Consumables, Ops Task Library) show the
//               public demo org (Sim Mill) read-only; the other tools keep their data in this browser only.
// Signed in   → data lives in Supabase under the chosen org, shared live with its members.
//
//   MMCloud.mountAccount(el)        account chip + sign-in, the same on every page
//   MMCloud.openStore(tool, opts)   synced records for a tool (see below)
//   MMCloud.files(tool)             upload / download / remove files for a tool
//   MMCloud.demoSession(tool)       signed out, a demo tool: a view-only session on the public demo org, else null
//   MMCloud.access(tool?)           who is looking, as one named state (see "Who is looking" below)
//   MMCloud.saveIndicator(el, o)    the Saved / Saving… / Not saved / View only indicator for one or more stores
(() => {
  const cfg = window.MM_CONFIG || {};
  const enabled = !!(cfg.supabaseUrl && cfg.supabaseKey && window.supabase);
  const ORG_KEY = 'mm-org';
  const client = enabled ? window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseKey, {
    auth: { storageKey: 'mm-auth', persistSession: true, autoRefreshToken: true, detectSessionInUrl: false },
  }) : null;

  let cached = null, pending = null;   // { user, orgs:[{id,name,role}], org }

  const lsGet = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const lsSet = (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) {} };

  // null in demo mode, otherwise { user, orgs, org }. org is null if the account isn't in an org yet.
  function session(force){
    if (!enabled) return Promise.resolve(null);
    if (cached && !force) return Promise.resolve(cached);
    if (pending && !force) return pending;
    pending = (async () => {
      try {
        const { data: { session: s } } = await client.auth.getSession();
        if (!s) { cached = null; return null; }
        const { data: rows, error } = await client.from('memberships').select('role, created_at, org:orgs(id, name)').eq('user_id', s.user.id);
        if (error) throw error;
        const orgs = (rows || []).filter(r => r.org).map(r => ({ id: r.org.id, name: r.org.name, role: r.role, since: r.created_at }))
          .sort((a, b) => a.name.localeCompare(b.name));
        // No saved choice: the org the account joined first (a later side org, e.g. a RAG test org, never takes over).
        const first = orgs.slice().sort((a, b) => String(a.since).localeCompare(String(b.since)))[0];
        const want = lsGet(ORG_KEY);
        cached = { user: s.user, orgs, org: orgs.find(o => o.id === want) || first || null };
        // appearance follows the account (mm-theme.js)
        if (window.MMTheme) MMTheme.fromAccount((s.user.user_metadata || {}).mm_theme);
        return cached;
      } finally { pending = null; }
    })();
    return pending;
  }
  async function signIn(email, password){
    if (!enabled) throw new Error('Sign-in isn’t set up for this site yet.');
    const { error } = await client.auth.signInWithPassword({ email: email.trim(), password });
    if (error) throw new Error(error.message === 'Invalid login credentials' ? 'Wrong email or password.' : error.message);
    return session(true);
  }
  async function signOut(){
    if (enabled) await client.auth.signOut({ scope: 'local' });
    cached = null; lsSet(ORG_KEY, null);
  }
  function setOrg(id){ lsSet(ORG_KEY, id); cached = null; }
  // Save the light / dark / system choice on the signed-in account (Supabase user metadata: no table needed).
  // Signed out it stays in this browser only (mm-theme.js).
  async function saveTheme(pref){
    const s = await session();
    if (!s) return;
    const { data, error } = await client.auth.updateUser({ data: { mm_theme: pref } });
    if (error) throw error;
    if (data && data.user && cached) cached.user = data.user;
  }
  const canEdit = s => !!(s && s.org && s.org.role !== 'viewer' && !s.demo);

  // Signed out: the demo tools read the public demo org (mm_demo_org / mm_demo_records), view only.
  const DEMO_TOOLS = ['mymachine', 'outages', 'consumables', 'task-packages'];
  let demoOrg = null;
  function demoOrgInfo(){
    if (!enabled) return Promise.resolve(null);
    return demoOrg || (demoOrg = client.rpc('mm_demo_org').then(({ data, error }) => {
      if (error) throw error;
      const o = (data || [])[0]; return o ? { id: o.id, name: o.name, role: 'viewer' } : null;
    }).catch(e => { demoOrg = null; throw e; }));
  }
  async function demoSession(tool){
    if (!DEMO_TOOLS.includes(tool) || await session()) return null;
    const org = await demoOrgInfo();
    return org ? { demo: true, user: { id: 'demo', email: null }, orgs: [org], org } : null;
  }

  /* ───────────── Who is looking: one explicit access state ─────────────
     const a = await MMCloud.access(tool?)   // tool: a demo tool name, to see whether signed-out visitors get its demo org
     a.kind is exactly one of:
       'unavailable'  Supabase isn't configured for this copy of the site       (data: this browser only)
       'offline'      the server can't be reached (a.error)                     (data: this browser only)
       'signed-out'   nobody signed in, no public demo for this page             (data: this browser only)
       'public-demo'  nobody signed in, viewing the public demo org (a.org)      (view only)
       'no-org'       signed in (a.user) but in no organization yet              (data: this browser only)
       'demo-member'  signed in to a public demo org, e.g. the demo account      (sees demo data; a.canEdit by role)
       'member'       signed in to a real organization (a.org, a.role)           (its own data only, never demo data)
     Every result also has canEdit, demo (true for 'public-demo' and 'demo-member') and, when there is one,
     session (the object session() / demoSession() give). Decide what a page shows from a.kind, not from
     combinations of session fields. */
  let publicIds = null;
  function publicOrgIds(){
    return publicIds || (publicIds = client.rpc('mm_llm_public_org').then(({ data, error }) => {
      if (error) throw error;
      return new Set((data || []).map(o => o.id));
    }).catch(e => { publicIds = null; throw e; }));
  }
  async function access(tool){
    if (!enabled) return { kind: 'unavailable', canEdit: false, demo: false };
    let s;
    try { s = await session(); } catch (error) { return { kind: 'offline', error, canEdit: false, demo: false }; }
    if (!s){
      let d = null;
      try { d = tool ? await demoSession(tool) : await demoOrgInfo().then(org => org && { demo: true, user: { id: 'demo', email: null }, orgs: [org], org }); }
      catch (e) { d = null; }                  // the server answered the session check; no demo is the safe reading
      return d ? { kind: 'public-demo', org: d.org, role: 'viewer', session: d, canEdit: false, demo: true }
               : { kind: 'signed-out', canEdit: false, demo: false };
    }
    if (!s.org) return { kind: 'no-org', user: s.user, session: s, canEdit: false, demo: false };
    // Unknown (the lookup failed) counts as a real organization: it then sees placeholders, never demo data.
    let pub = false; try { pub = (await publicOrgIds()).has(s.org.id); } catch (e) {}
    return { kind: pub ? 'demo-member' : 'member', user: s.user, org: s.org, role: s.org.role, session: s, canEdit: canEdit(s), demo: pub };
  }

  /* ───────────── The "Saved / Saving… / Not saved / View only" indicator ─────────────
     One indicator for one or more stores: it shows the worst state across them (Not saved > Saving… > View only >
     Saved), warns once per problem, and reports conflicts and refused changes.
       const ind = MMCloud.saveIndicator(el, { toast, fadeSaved: true, viewOnlyText: () => '…', onConnection: x => {} });
       MMCloud.openStore('tool', { …, onStatus: ind.handler(() => store) });   // one handler per store
       ind.show('saved' | 'saving' | 'error' | 'viewonly' | 'notloaded' | '')  // for saves that don't go through a store
     onConnection gets 'live' or 'reconnecting' (live updates from others), for pages that show it. */
  const SAVE_TEXT = { saved: 'Saved', saving: 'Saving…', viewonly: 'View only', error: 'Not saved', notloaded: 'Not loaded', '': '' };
  const SAVE_RANK = { saved: 0, viewonly: 1, saving: 2, error: 3 };
  function saveIndicator(el, o = {}){
    const per = new Map(), toast = msg => { try { o.toast && o.toast(msg); } catch (e) {} };
    let warned = false, viewWarned = false, fade = null;
    function show(state){
      clearTimeout(fade);
      if (!el) return;
      el.textContent = SAVE_TEXT[state] != null ? SAVE_TEXT[state] : '';
      el.dataset.state = state || 'idle';
      if (state === 'saved' && o.fadeSaved) fade = setTimeout(() => { if (el.dataset.state === 'saved'){ el.textContent = ''; el.dataset.state = 'idle'; } }, 1600);
    }
    function render(){
      let worst = 'saved';
      for (const v of per.values()) if (SAVE_RANK[v] > SAVE_RANK[worst]) worst = v;
      show(worst);
    }
    function handler(storeOf){
      const key = {};
      return (x, detail) => {
        if (x === 'rejected') return toast('A change couldn’t be saved: ' + (detail || 'not allowed') + '.');
        if (x === 'live' || x === 'reconnecting'){ try { o.onConnection && o.onConnection(x); } catch (e) {} return; }
        if (!(x in SAVE_RANK)) return;
        per.set(key, x);
        if (x === 'saved'){
          if (![...per.values()].includes('error')) warned = false;   // warn again only after everything has recovered
          const st = typeof storeOf === 'function' ? storeOf() : storeOf, c = st && st.conflicts;
          if (c) toast(c === 1 ? 'Someone else changed that at the same moment — showing their version.'
                               : `${c} items were changed by someone else at the same moment — showing their versions.`);
        } else if (x === 'error' && !warned){ warned = true; toast('Can’t reach the server — keep this page open, it will keep retrying.'); }
        else if (x === 'viewonly' && !viewWarned){
          viewWarned = true; toast((o.viewOnlyText && o.viewOnlyText()) || 'You have view-only access — changes you make here aren’t saved.');
        }
        render();
      };
    }
    return { handler, show };
  }

  // Reload open tool pages when this browser signs in or out (or switches org) in another tab.
  // Token refreshes also touch mm-auth, so only react when the signed-in user changes.
  if (enabled) {
    const uidOf = v => { try { return (JSON.parse(v) || {}).user.id; } catch (e) { return null; } };
    window.addEventListener('storage', e => {
      if (e.key === ORG_KEY || (e.key === 'mm-auth' && uidOf(e.oldValue) !== uidOf(e.newValue))) location.reload();
    });
  }

  /* ───────────── Account chip + sign-in dialog (same on every page) ───────────── */

  const CSS = `
  .mmc{display:inline-flex;align-items:center;gap:10px;font:12.5px/1.3 var(--font);color:var(--ink);position:relative}
  .mmc .who{display:flex;align-items:center;gap:8px;min-width:0}
  .mmc .who b{font-weight:500;color:var(--ink-2);white-space:nowrap;display:inline-flex;align-items:center;gap:6px}
  .mmc .who b::before{content:"";width:7px;height:7px;border-radius:50%;background:var(--faint);flex:none}
  .mmc.live .who b::before{background:var(--ok)}
  .mmc.off .who b::before{background:var(--bad)}
  .mmc .who > span{color:var(--muted);font-size:12px;white-space:nowrap}
  .mmc.compact .who > span{display:none}
  .mmc select{font:inherit;font-size:12px;border:1px solid var(--line);border-radius:var(--r-sm);padding:2px 4px;color:var(--ink-2);background:var(--surface-2);max-width:160px}
  .mmc-pill{font-size:12px;font-weight:400;color:var(--muted)}
  .mmc-pill::before{content:"·";margin:0 6px 0 0;color:var(--ink-3)}
  .mmc-pill.ro{color:var(--accent-ink)}
  .mmc-btn{font:inherit;font-size:13px;font-weight:500;border:1px solid var(--line);background:transparent;border-radius:var(--r-sm);height:30px;padding:0 10px;cursor:pointer;color:var(--ink);white-space:nowrap}
  .mmc-btn:hover{background:var(--hover);border-color:var(--line-strong)}
  .mmc-btn.primary{background:var(--primary);border-color:var(--primary);color:var(--on-primary)}
  .mmc-btn.primary:hover{background:var(--primary-hover)}
  .mmc-btn:disabled{opacity:.6;cursor:default}
  .mmc-dlg{border:1px solid var(--line-strong);border-radius:var(--r-lg);padding:0;box-shadow:var(--shadow-pop);width:min(360px,calc(100vw - 32px));
    font:13px/1.4 var(--font);color:var(--ink);background:var(--overlay)}
  .mmc-dlg::backdrop{background:var(--scrim)}
  .mmc-dlg form{padding:20px 20px 16px;display:flex;flex-direction:column;gap:12px}
  .mmc-dlg h3{margin:0;font-size:15px;font-weight:600}
  .mmc-dlg p{margin:0;font-size:13px;color:var(--muted);line-height:1.5}
  .mmc-dlg label{display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:500;color:var(--ink-2)}
  .mmc-dlg input{font:inherit;font-size:13px;border:1px solid var(--line-strong);border-radius:var(--r-sm);padding:0 10px;height:34px;background:var(--surface-2);color:var(--ink)}
  .mmc-dlg input:focus{outline:none;border-color:var(--accent)}
  .mmc-err{color:var(--bad-ink);font-size:13px}
  .mmc-err:empty{display:none}
  @media (pointer:coarse){ .mmc-dlg input{height:44px} }
  @media (max-width:760px){
    .mmc-dlg{width:100%;max-width:none;margin:auto 0 0;border-radius:14px 14px 0 0;border-bottom:0;padding-bottom:env(safe-area-inset-bottom)}
    .mmc-row .mmc-btn{flex:1;height:44px}
  }
  .mmc-row{display:flex;justify-content:flex-end;gap:8px}`;
  let dlg = null;
  const mk = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
  function ensureUI(){
    if (dlg) return;
    const st = mk('style'); st.textContent = CSS; document.head.appendChild(st);
    dlg = mk('dialog', 'mmc-dlg');
    dlg.innerHTML = `<form>
      <h3>Sign in</h3>
      <p>Use the account your administrator set up for you. Without signing in you're looking at the demo mill.</p>
      <label>Email<input name="email" type="email" autocomplete="username" required></label>
      <label>Password<input name="password" type="password" autocomplete="current-password" required></label>
      <div class="mmc-err"></div>
      <div class="mmc-row"><button class="mmc-btn" type="button" data-x>Cancel</button><button class="mmc-btn primary" type="submit">Sign in</button></div>
    </form>`;
    document.body.appendChild(dlg);
    const f = dlg.querySelector('form'), err = dlg.querySelector('.mmc-err'), go = dlg.querySelector('[type=submit]');
    dlg.querySelector('[data-x]').addEventListener('click', () => dlg.close());
    f.addEventListener('submit', async e => {
      e.preventDefault(); go.disabled = true; err.textContent = '';
      try { await signIn(f.email.value, f.password.value); f.password.value = ''; dlg.close(); location.reload(); }
      catch (x) { err.textContent = x.message; }
      finally { go.disabled = false; }
    });
  }
  function openSignIn(){ ensureUI(); dlg.querySelector('.mmc-err').textContent = ''; dlg.showModal(); dlg.querySelector('[name=email]').focus(); }

  // Renders the account chip into el. compact: smaller, for tool top bars.
  async function mountAccount(el, opts = {}){
    if (!enabled || !el) return;
    ensureUI();
    let s = null, failed = false;
    try { s = await session(); } catch (e) { failed = true; }
    el.textContent = '';
    const box = mk('div', 'mmc' + (opts.compact ? ' compact' : '') + (failed ? ' off' : '')), who = mk('div', 'who'), b = mk('b');
    who.appendChild(b); box.appendChild(who);
    if (failed){
      b.append('Offline', mk('span', 'mmc-pill', 'Can’t reach server'));
      who.appendChild(mk('span', '', 'Showing this browser’s copy'));
    } else if (!s){
      let d = null;
      if (opts.tool || opts.demo) { try { d = await demoSession(opts.tool || 'mymachine'); } catch (e) {} }
      if (d){
        b.append('Demo', mk('span', 'mmc-pill ro', 'view only'));
        who.appendChild(mk('span', '', d.org.name));
        box.title = `Demo: ${d.org.name}, a simulated mill, read-only. Sign in to work on your own machine.`;
      } else {
        b.append('Demo', mk('span', 'mmc-pill', 'saved in this browser'));
        box.title = 'Demo mode: sample data, saved only in this browser. Sign in to share with your team.';
      }
      const go = mk('button', 'mmc-btn primary', 'Sign in'); go.addEventListener('click', openSignIn); box.appendChild(go);
    } else {
      b.append(opts.compact && s.org ? s.org.name : s.user.email,
        s.org ? mk('span', 'mmc-pill ' + (s.org.role === 'viewer' ? 'ro' : 'ok'), s.org.role === 'viewer' ? 'view only' : 'shared') : mk('span', 'mmc-pill', 'no access'));
      if (s.org) box.classList.add('live');
      box.title = `Signed in as ${s.user.email}` + (s.org ? ` · ${s.org.name} (${s.org.role})` : '');
      if (s.orgs.length > 1){
        const sel = mk('select'); sel.title = 'Organization';
        s.orgs.forEach(o => { const op = mk('option', '', o.name); op.value = o.id; op.selected = s.org && o.id === s.org.id; sel.appendChild(op); });
        sel.addEventListener('change', () => { setOrg(sel.value); location.reload(); });
        who.appendChild(sel);
      } else who.appendChild(mk('span', '', s.org ? s.org.name : 'Ask your administrator to add you to an organization'));
      const out = mk('button', 'mmc-btn', 'Sign out');
      out.addEventListener('click', async () => { await signOut(); location.reload(); });
      box.appendChild(out);
    }
    el.appendChild(box);
  }

  /* ───────────── Synced records for a tool ─────────────
     const store = MMCloud.openStore('mymachine', {
       snapshot: () => ({ id: data, ... }),    // the tool's current records, called when saving
       onChange: (id, data | null, info) => {},// someone else changed (or deleted) a record; info.conflict if it was ours too
       onStatus: (s, detail) => {},            // 'saving' | 'saved' | 'error' | 'viewonly' | 'live' | 'reconnecting' | 'rejected'
     });
     const data = await store.ready;           // null if signed out / no org (use demo storage), else { id: data }
     store.save();                             // after any local change: sends what differs, with version checks
     store.save(['item:x']);                   // same, but only compares these records (plus deletions)
   A record that someone else changed first is refused by the server; their version comes back through
   onChange, so nothing is silently overwritten. A change the server rejects as invalid or not allowed is
   reported once ('rejected', with the reason) and not retried until that record changes again. */
  const canon = v => Array.isArray(v) ? '[' + v.map(x => canon(x === undefined ? null : x)).join(',') + ']'
    : (v && typeof v === 'object') ? '{' + Object.keys(v).filter(k => v[k] !== undefined).sort().map(k => JSON.stringify(k) + ':' + canon(v[k])).join(',') + '}'
    : JSON.stringify(v === undefined ? null : v);
  const PAGE = 1000, CHUNK = 200, RETRY_MIN = 5000, RETRY_MAX = 60000, CATCHUP_AFTER = 60000;

  // Every row of a tool, paged by id (each page is an index range, so page 50 costs what page 1 does).
  // includeDeleted: also rows that were deleted (needed when catching up on what changed).
  async function fetchRows(org, tool, opts = {}){
    const rows = [];
    for (let after = null; ; ){
      let q = client.from('mm_records').select('*').eq('org_id', org).eq('tool', tool);
      if (!opts.includeDeleted) q = q.eq('deleted', false);
      if (opts.since) q = q.gte('updated_at', opts.since);
      if (after != null) q = q.gt('id', after);
      const { data, error } = await q.order('id').limit(PAGE);
      if (error) throw error;
      rows.push(...data);
      if (data.length < PAGE) return rows;
      after = data[data.length - 1].id;
    }
  }

  function openStore(tool, opts = {}){
    const st = { tool, edit: false, org: null, user: null, conflicts: 0, rejected: 0 };
    const shadow = new Map(), inflight = new Map(), buffer = [], refused = new Map(), dirty = new Set();
    let loaded = false, busy = false, again = false, timer = null, retry = null, failing = false, subs = 0;
    let delay = RETRY_MIN, full = true, since = null, hiddenAt = 0, live = false;
    const status = (x, d) => { try { opts.onStatus && opts.onStatus(x, d); } catch (e) {} };
    const notify = (id, data, info) => { try { opts.onChange && opts.onChange(id, data, info || {}); } catch (e) { console.error(e); } };

    function applyRow(row, forced){
      if (row.updated_at && (!since || row.updated_at > since)) since = row.updated_at;
      const sh = shadow.get(row.id), s = canon(row.data), inf = inflight.get(row.id);
      if (!forced && sh && row.version <= sh.v) return;
      const same = (inf && inf.s === s && inf.deleted === row.deleted) || (sh && sh.s === s && sh.deleted === row.deleted);
      shadow.set(row.id, { v: row.version, s, deleted: row.deleted });
      if (same && !forced) return;
      if (loaded) notify(row.id, row.deleted ? null : row.data, { conflict: !!forced });
    }
    // Catch up on what changed while live updates weren't arriving (a little overlap is harmless:
    // rows already seen are ignored by version).
    const catchUp = async () => {
      if (!loaded || st.demo) return;
      try {
        const from = since ? new Date(Date.parse(since) - 2 * 60000).toISOString() : null;
        (await fetchRows(st.org.id, tool, { includeDeleted: true, since: from })).forEach(r => applyRow(r));
      } catch (e) {}
    };

    st.ready = (async () => {
      const s = await session();
      if (!s){
        const d = await demoSession(tool);
        if (!d) return null;
        Object.assign(st, { org: d.org, user: d.user, edit: false, demo: true });
        const { data: rows, error } = await client.rpc('mm_demo_records', { p_tool: tool });
        if (error) throw error;
        rows.forEach(r => applyRow(r));
        const data = {};
        for (const r of rows) data[r.id] = r.data;
        loaded = true;
        return data;
      }
      if (!s.org) return null;
      Object.assign(st, { org: s.org, user: s.user, edit: canEdit(s) });
      await new Promise(res => {
        const t = setTimeout(res, 8000);
        // Filtered by tool: a page only hears about its own tool. Rows of other organizations are
        // already withheld by row-level security; the org check is for people in several.
        st.channel = client.channel(`mm-${tool}-${s.org.id}`)
          .on('postgres_changes', { event: '*', schema: 'public', table: 'mm_records', filter: `tool=eq.${tool}` }, p => {
            const row = p.new; if (!row || row.org_id !== st.org.id) return;
            loaded ? applyRow(row) : buffer.push(row);
          })
          .subscribe(x => {
            if (x === 'SUBSCRIBED'){ live = true; if (subs++ && loaded) catchUp(); clearTimeout(t); res(); status('live'); }
            else if (x === 'CHANNEL_ERROR' || x === 'TIMED_OUT' || x === 'CLOSED'){ live = false; status('reconnecting'); }
          });
      });
      const rows = await fetchRows(s.org.id, tool);
      rows.forEach(r => applyRow(r));
      const data = {};
      for (const r of rows) if (!r.deleted) data[r.id] = r.data;
      loaded = true;
      buffer.splice(0).forEach(r => applyRow(r));
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) hiddenAt = Date.now();
        else if (!live || (hiddenAt && Date.now() - hiddenAt > CATCHUP_AFTER)) catchUp();
      });
      window.addEventListener('online', () => { catchUp(); flush(); });
      window.addEventListener('beforeunload', e => { if (st.pending()){ flush(); e.preventDefault(); e.returnValue = ''; } });
      return data;
    })();

    function changes(){
      const snap = (opts.snapshot && opts.snapshot()) || {}, out = [];
      const ids = full ? Object.keys(snap) : [...dirty].filter(id => snap[id] != null);
      for (const id of ids){
        const data = snap[id];
        if (data == null) continue;
        const s = canon(data), sh = shadow.get(id);
        if (refused.get(id) === s) continue;              // the server already said no to exactly this
        if (!sh || sh.deleted || sh.s !== s) out.push({ s, deleted: false, c: { id, data, deleted: false, base: sh ? sh.v : null } });
      }
      for (const [id, sh] of shadow) if (!sh.deleted && snap[id] == null) out.push({ s: sh.s, deleted: true, c: { id, deleted: true, base: sh.v } });
      return out.sort((a, b) => a.c.id < b.c.id ? -1 : a.c.id > b.c.id ? 1 : 0);
    }
    async function flush(){
      clearTimeout(timer); timer = null;
      if (!loaded || !st.edit) return;
      if (busy){ again = true; return; }
      busy = true; clearTimeout(retry);
      let conflicts = 0, rejected = 0, reason = '';
      try {
        const ch = changes();
        full = false; dirty.clear();
        for (let i = 0; i < ch.length; i += CHUNK){
          const part = ch.slice(i, i + CHUNK);
          part.forEach(x => inflight.set(x.c.id, { s: x.s, deleted: x.deleted }));
          let res;
          try { res = await client.rpc('mm_apply', { p_org: st.org.id, p_tool: tool, p_changes: part.map(x => x.c) }); }
          finally { part.forEach(x => inflight.delete(x.c.id)); }
          if (res.error) throw res.error;
          res.data.forEach((r, j) => {
            const x = part[j];
            if (r.ok){ refused.delete(x.c.id); const sh = shadow.get(x.c.id); if (!sh || sh.v < r.version) shadow.set(x.c.id, { v: r.version, s: x.s, deleted: x.deleted }); }
            else if (r.error){ rejected++; reason = r.error; refused.set(x.c.id, x.s); console.warn(`[${tool}] ${x.c.id} not saved: ${r.error}`); }
            else if (r.row){ conflicts++; applyRow(r.row, true); }
            else { conflicts++; shadow.delete(x.c.id); notify(x.c.id, null, { conflict: true }); }
          });
        }
        failing = false; delay = RETRY_MIN; st.conflicts = conflicts; st.rejected = rejected;
        if (rejected) status('rejected', reason);
        status('saved');
      } catch (e) {
        full = true;                                     // compare everything on the retry
        failing = true; status('error');
        retry = setTimeout(flush, delay);
        delay = Math.min(RETRY_MAX, delay * 2);
      } finally {
        busy = false;
        if (again){ again = false; flush(); }
      }
    }
    st.save = ids => {
      if (!loaded) return;
      if (Array.isArray(ids)) ids.forEach(id => dirty.add(id)); else full = true;
      if (!st.edit){ if (changes().length) status('viewonly'); return; }
      status('saving'); clearTimeout(timer); timer = setTimeout(flush, 350);
    };
    st.flush = flush;
    st.pending = () => st.edit && (busy || !!timer || failing);
    // The store's state, named: 'loading' until ready, then 'viewonly' (can't edit), 'saving' (a save is queued or
    // in flight), 'retrying' (the last save failed; it retries with backoff) or 'idle'. live: live updates arriving.
    st.state = () => ({ phase: !loaded ? 'loading' : !st.edit ? 'viewonly' : failing ? 'retrying' : (busy || timer) ? 'saving' : 'idle', live });
    st.catchUp = catchUp;
    return st;
  }

  /* ───────────── Files for a tool ─────────────
     const f = MMCloud.files('vendor-reports');
     const path = await f.upload(file);        // stored privately under <org>/<tool>/
     const blob = await f.download(path);  const link = await f.url(path);  await f.remove(path);
     await f.sweep();                          // editors: remove files no record points to (at most weekly) */
  const SWEEP_EVERY = 7 * 864e5, SWEEP_MIN_AGE = 2 * 864e5;
  function files(tool){
    const need = async () => { const s = await session(); if (!s || !s.org) throw new Error('Sign in to store files.'); return s; };
    const bucket = () => client.storage.from('mm-files');
    // Every stored file under <org>/<tool>/, walking sub-folders.
    async function listAll(prefix){
      const out = [];
      for (let offset = 0; ; offset += 1000){
        const { data, error } = await bucket().list(prefix, { limit: 1000, offset, sortBy: { column: 'name', order: 'asc' } });
        if (error) throw error;
        for (const o of data){
          const p = `${prefix}/${o.name}`;
          if (o.id == null) out.push(...await listAll(p)); else out.push({ path: p, created: Date.parse(o.created_at) || 0 });
        }
        if (data.length < 1000) return out;
      }
    }
    return {
      async upload(file, name){
        const s = await need();
        const n = (name || file.name || 'file').replace(/[^\w.-]+/g, '_').slice(-100);
        const path = `${s.org.id}/${tool}/${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}-${n}`;
        const { error } = await bucket().upload(path, file, { contentType: file.type || 'application/octet-stream' });
        if (error) throw new Error(/size|large/i.test(error.message) ? 'Files are limited to 30 MB.' : error.message);
        return path;
      },
      async download(path){ await need(); const { data, error } = await bucket().download(path); if (error) throw error; return data; },
      async url(path, seconds = 3600){ await need(); const { data, error } = await bucket().createSignedUrl(path, seconds); if (error) throw error; return data.signedUrl; },
      async remove(path){ await need(); const { error } = await bucket().remove([path]); if (error) throw error; },
      // Files stay while any record (deleted ones included, until the nightly purge) points to them,
      // and for 2 days after upload so a file isn't removed before its record is saved.
      async sweep(force){
        const s = await need();
        if (!canEdit(s)) return 0;
        const key = `mm-sweep:${s.org.id}:${tool}`;
        if (!force && Date.now() - (Number(lsGet(key)) || 0) < SWEEP_EVERY) return 0;
        lsSet(key, String(Date.now()));
        const { data: refs, error } = await client.rpc('mm_file_refs', { p_org: s.org.id, p_tool: tool });
        if (error) throw error;
        const keep = new Set((refs || []).map(r => typeof r === 'string' ? r : r.mm_file_refs));
        const old = (await listAll(`${s.org.id}/${tool}`)).filter(f => !keep.has(f.path) && Date.now() - f.created > SWEEP_MIN_AGE).map(f => f.path);
        for (let i = 0; i < old.length; i += 100){ const { error: e2 } = await bucket().remove(old.slice(i, i + 100)); if (e2) throw e2; }
        return old.length;
      },
    };
  }

  window.MMCloud = { enabled, client, session, demoSession, access, signIn, signOut, setOrg, canEdit, saveTheme, openSignIn, mountAccount, openStore, saveIndicator, files, canon };
})();
