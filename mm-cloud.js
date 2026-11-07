// Machine Manager — shared sign-in, data and file storage for every tool page.
// Load after vendor/supabase-*.js and mm-config.js. Exposes window.MMCloud.
//
// Signed out  → demo mode: each tool keeps its data in this browser only.
// Signed in   → data lives in Supabase under the chosen org, shared live with its members.
//
//   MMCloud.mountAccount(el)        account chip + sign-in, the same on every page
//   MMCloud.openStore(tool, opts)   synced records for a tool (see below)
//   MMCloud.files(tool)             upload / download / remove files for a tool
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
        const { data: rows, error } = await client.from('memberships').select('role, org:orgs(id, name)').eq('user_id', s.user.id);
        if (error) throw error;
        const orgs = (rows || []).filter(r => r.org).map(r => ({ id: r.org.id, name: r.org.name, role: r.role }))
          .sort((a, b) => a.name.localeCompare(b.name));
        const want = lsGet(ORG_KEY);
        cached = { user: s.user, orgs, org: orgs.find(o => o.id === want) || orgs[0] || null };
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
  const canEdit = s => !!(s && s.org && s.org.role !== 'viewer');

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
  .mmc{display:inline-flex;align-items:center;gap:10px;background:#fff;border:1px solid #e5e7eb;border-radius:12px;
    padding:6px 8px 6px 12px;box-shadow:0 2px 10px rgba(0,0,0,.06);font:13px/1.3 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#1f2328;position:relative}
  .mmc.compact{padding:4px 4px 4px 10px;border-radius:10px;font-size:12px;gap:8px}
  .mmc .who b{display:block;font-weight:600}
  .mmc .who > span{color:#6b7280;font-size:12px}
  .mmc.compact .who b{display:inline;font-weight:600}
  .mmc.compact .who > span{display:none}
  .mmc select{font:inherit;font-size:12px;border:1px solid #e5e7eb;border-radius:6px;padding:1px 4px;color:#6b7280;background:#fff;max-width:160px}
  .mmc-pill{display:inline-block;font-size:10.5px;font-weight:600;border-radius:999px;padding:2px 8px;background:#fef3c7;color:#92400e;margin-left:6px;vertical-align:1px}
  .mmc-pill.ok{background:#dcfce7;color:#166534}
  .mmc-pill.ro{background:#e0e7ff;color:#3730a3}
  .mmc-btn{font:inherit;font-size:12.5px;font-weight:500;border:1px solid #e5e7eb;background:#fff;border-radius:8px;padding:5px 11px;cursor:pointer;color:#1f2328;white-space:nowrap}
  .mmc-btn:hover{background:#f5f5f4}
  .mmc-btn.primary{background:#1f2328;border-color:#1f2328;color:#fff}
  .mmc-btn.primary:hover{background:#000}
  .mmc-btn:disabled{opacity:.6;cursor:default}
  .mmc-dlg{border:none;border-radius:14px;padding:0;box-shadow:0 20px 60px rgba(0,0,0,.25);width:min(360px,calc(100vw - 32px));
    font:14px/1.4 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#1f2328}
  .mmc-dlg::backdrop{background:rgba(28,25,23,.35)}
  .mmc-dlg form{padding:22px 22px 18px;display:flex;flex-direction:column;gap:12px}
  .mmc-dlg h3{margin:0;font-size:16px}
  .mmc-dlg p{margin:0;font-size:12.5px;color:#6b7280;line-height:1.45}
  .mmc-dlg label{display:flex;flex-direction:column;gap:4px;font-size:12px;font-weight:500;color:#3f3f46}
  .mmc-dlg input{font:inherit;font-size:14px;border:1px solid #e5e7eb;border-radius:8px;padding:8px 10px}
  .mmc-dlg input:focus{outline:2px solid #2563eb;outline-offset:-1px;border-color:transparent}
  .mmc-err{color:#b91c1c;font-size:12.5px;min-height:1em}
  .mmc-row{display:flex;justify-content:flex-end;gap:8px}`;
  let dlg = null;
  const mk = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; };
  function ensureUI(){
    if (dlg) return;
    const st = mk('style'); st.textContent = CSS; document.head.appendChild(st);
    dlg = mk('dialog', 'mmc-dlg');
    dlg.innerHTML = `<form>
      <h3>Sign in</h3>
      <p>Use the account your administrator set up for you. Without signing in you're using the demo, which saves only in this browser.</p>
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
    const box = mk('div', 'mmc' + (opts.compact ? ' compact' : '')), who = mk('div', 'who'), b = mk('b');
    who.appendChild(b); box.appendChild(who);
    if (failed){
      b.append('Offline', mk('span', 'mmc-pill', 'Can’t reach server'));
      who.appendChild(mk('span', '', 'Showing this browser’s copy'));
    } else if (!s){
      b.append('Demo', mk('span', 'mmc-pill', 'This browser only'));
      who.appendChild(mk('span', '', 'Try the tools with sample data'));
      const go = mk('button', 'mmc-btn primary', 'Sign in'); go.addEventListener('click', openSignIn); box.appendChild(go);
    } else {
      b.append(opts.compact && s.org ? s.org.name : s.user.email,
        s.org ? mk('span', 'mmc-pill ' + (s.org.role === 'viewer' ? 'ro' : 'ok'), s.org.role === 'viewer' ? 'View only' : 'Shared') : mk('span', 'mmc-pill', 'No access'));
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
       onChange: (id, data | null) => {},      // someone else changed (or deleted) a record
       onStatus: s => {},                      // 'saving' | 'saved' | 'error' | 'viewonly' | 'live' | 'reconnecting'
     });
     const data = await store.ready;           // null if signed out / no org (use demo storage), else { id: data }
     store.save();                             // after any local change: sends what differs, with version checks
   A record that someone else changed first is refused by the server; their version comes
   back through onChange, so nothing is silently overwritten. */
  const canon = v => Array.isArray(v) ? '[' + v.map(x => canon(x === undefined ? null : x)).join(',') + ']'
    : (v && typeof v === 'object') ? '{' + Object.keys(v).filter(k => v[k] !== undefined).sort().map(k => JSON.stringify(k) + ':' + canon(v[k])).join(',') + '}'
    : JSON.stringify(v === undefined ? null : v);

  function openStore(tool, opts = {}){
    const st = { tool, edit: false, org: null, user: null, conflicts: 0 };
    const shadow = new Map(), inflight = new Map(), buffer = [];
    let loaded = false, busy = false, again = false, timer = null, retry = null, failing = false, subs = 0;
    const status = x => { try { opts.onStatus && opts.onStatus(x); } catch (e) {} };
    const notify = (id, data, info) => { try { opts.onChange && opts.onChange(id, data, info || {}); } catch (e) { console.error(e); } };

    function applyRow(row, forced){
      const sh = shadow.get(row.id), s = canon(row.data), inf = inflight.get(row.id);
      if (!forced && sh && row.version <= sh.v) return;
      const same = (inf && inf.s === s && inf.deleted === row.deleted) || (sh && sh.s === s && sh.deleted === row.deleted);
      shadow.set(row.id, { v: row.version, s, deleted: row.deleted });
      if (same && !forced) return;
      if (loaded) notify(row.id, row.deleted ? null : row.data, { conflict: !!forced });
    }
    async function fetchAll(){
      const rows = [], PAGE = 1000;
      for (let from = 0; ; from += PAGE){
        const { data, error } = await client.from('mm_records').select('*').eq('org_id', st.org.id).eq('tool', tool)
          .order('id').range(from, from + PAGE - 1);
        if (error) throw error;
        rows.push(...data);
        if (data.length < PAGE) return rows;
      }
    }
    const refetch = async () => { try { (await fetchAll()).forEach(r => applyRow(r)); } catch (e) {} };

    st.ready = (async () => {
      const s = await session();
      if (!s || !s.org) return null;
      Object.assign(st, { org: s.org, user: s.user, edit: canEdit(s) });
      await new Promise(res => {
        const t = setTimeout(res, 8000);
        st.channel = client.channel(`mm-${tool}-${s.org.id}`)
          .on('postgres_changes', { event: '*', schema: 'public', table: 'mm_records', filter: `org_id=eq.${s.org.id}` }, p => {
            const row = p.new; if (!row || row.tool !== tool) return;
            loaded ? applyRow(row) : buffer.push(row);
          })
          .subscribe(x => {
            if (x === 'SUBSCRIBED'){ if (subs++ && loaded) refetch(); clearTimeout(t); res(); status('live'); }
            else if (x === 'CHANNEL_ERROR' || x === 'TIMED_OUT' || x === 'CLOSED') status('reconnecting');
          });
      });
      const rows = await fetchAll();
      rows.forEach(r => applyRow(r));
      const data = {};
      for (const r of rows) if (!r.deleted) data[r.id] = r.data;
      loaded = true;
      buffer.splice(0).forEach(r => applyRow(r));
      document.addEventListener('visibilitychange', () => { if (!document.hidden) refetch(); });
      window.addEventListener('online', () => { refetch(); flush(); });
      window.addEventListener('beforeunload', e => { if (st.pending()){ flush(); e.preventDefault(); e.returnValue = ''; } });
      return data;
    })();

    function changes(){
      const snap = (opts.snapshot && opts.snapshot()) || {}, out = [];
      for (const [id, data] of Object.entries(snap)){
        if (data == null) continue;
        const s = canon(data), sh = shadow.get(id);
        if (!sh || sh.deleted || sh.s !== s) out.push({ s, deleted: false, c: { id, data, deleted: false, base: sh ? sh.v : null } });
      }
      for (const [id, sh] of shadow) if (!sh.deleted && snap[id] == null) out.push({ s: sh.s, deleted: true, c: { id, deleted: true, base: sh.v } });
      return out;
    }
    async function flush(){
      clearTimeout(timer); timer = null;
      if (!loaded || !st.edit) return;
      if (busy){ again = true; return; }
      busy = true; clearTimeout(retry);
      let conflicts = 0;
      try {
        const ch = changes();
        for (let i = 0; i < ch.length; i += 200){
          const part = ch.slice(i, i + 200);
          part.forEach(x => inflight.set(x.c.id, { s: x.s, deleted: x.deleted }));
          let res;
          try { res = await client.rpc('mm_apply', { p_org: st.org.id, p_tool: tool, p_changes: part.map(x => x.c) }); }
          finally { part.forEach(x => inflight.delete(x.c.id)); }
          if (res.error) throw res.error;
          res.data.forEach((r, j) => {
            const x = part[j];
            if (r.ok){ const sh = shadow.get(x.c.id); if (!sh || sh.v < r.version) shadow.set(x.c.id, { v: r.version, s: x.s, deleted: x.deleted }); }
            else if (r.row){ conflicts++; applyRow(r.row, true); }
            else { conflicts++; shadow.delete(x.c.id); notify(x.c.id, null, { conflict: true }); }
          });
        }
        failing = false; st.conflicts = conflicts;
        status('saved');
      } catch (e) {
        failing = true; status('error');
        retry = setTimeout(flush, 5000);
      } finally {
        busy = false;
        if (again){ again = false; flush(); }
      }
    }
    st.save = () => {
      if (!loaded) return;
      if (!st.edit){ if (changes().length) status('viewonly'); return; }
      status('saving'); clearTimeout(timer); timer = setTimeout(flush, 350);
    };
    st.flush = flush;
    st.pending = () => st.edit && (busy || !!timer || failing);
    return st;
  }

  /* ───────────── Files for a tool ─────────────
     const f = MMCloud.files('vendor-reports');
     const path = await f.upload(file);        // stored privately under <org>/<tool>/
     const blob = await f.download(path);  const link = await f.url(path);  await f.remove(path); */
  function files(tool){
    const need = async () => { const s = await session(); if (!s || !s.org) throw new Error('Sign in to store files.'); return s; };
    const bucket = () => client.storage.from('mm-files');
    return {
      async upload(file, name){
        const s = await need();
        const n = (name || file.name || 'file').replace(/[^\w.-]+/g, '_').slice(-100);
        const path = `${s.org.id}/${tool}/${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}-${n}`;
        const { error } = await bucket().upload(path, file, { contentType: file.type || 'application/octet-stream' });
        if (error) throw new Error(/size|large/i.test(error.message) ? 'Files are limited to 25 MB.' : error.message);
        return path;
      },
      async download(path){ await need(); const { data, error } = await bucket().download(path); if (error) throw error; return data; },
      async url(path, seconds = 3600){ await need(); const { data, error } = await bucket().createSignedUrl(path, seconds); if (error) throw error; return data.signedUrl; },
      async remove(path){ await need(); const { error } = await bucket().remove([path]); if (error) throw error; },
    };
  }

  window.MMCloud = { enabled, client, session, signIn, signOut, setOrg, canEdit, openSignIn, mountAccount, openStore, files, canon };
})();
