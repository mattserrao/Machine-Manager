// Machine Manager — which organization's MM LLM data a page shows, and a few small helpers the data pages share
// (Vendor Reports, Daily, Downtime / RCFA, MM LLM).
//
// Signed out, or signed in to a demo org (the demo account): the public demo orgs (Sim Mill), with a dropdown if
// several are published, remembered in this browser. ?org=<name> in the URL picks one.
// Signed in to a real org (e.g. PM1): only that org. It never sees demo data; until its own data is loaded the
// pages show a placeholder (st.empty, MMLLMOrg.placeholder).
//
//   const st = await MMLLMOrg.resolve();             // { db, s, orgs: [{ id, name, demo }], org } or { error }
//   MMLLMOrg.picker(el, st, org => reload(org));     // a select when there's more than one org
//   const rows = await MMLLMOrg.rpc(st, 'mm_llm_production', { p_from, p_to });   // p_org is added
//   MMLLMOrg.table(rows, [['day', 'Day'], ['tons', 'Tons', 'n']])                   // a plain table element
(() => {
  const KEY = 'mm-llm-org';
  // A caption for each demo org. Its "today" comes from its data: Sim Mill's year is regenerated every 6 weeks, so the
  // last day loaded is the demo's today and the year runs back 364 days from it.
  const DEMO = {
    'Demo Mill': { about: 'Fictional twin-wire linerboard machine (scripted year)' },
    'Sim Mill': { about: 'The Paper Mill’s recycled-board machine, one modelled year' },
  };
  const info = name => DEMO[name] ? { ...DEMO[name] } : null;

  async function resolve(){
    if (!window.MMCloud || !MMCloud.enabled) return { error: 'The data lives in Supabase, which isn’t set up for this copy of the site.' };
    const db = MMCloud.client;
    const a = await MMCloud.access();          // who is looking: one named state (mm-cloud.js)
    if (a.kind === 'offline') return { error: 'Couldn’t reach the server: ' + ((a.error && a.error.message) || a.error) };
    const s = a.session && !a.session.demo ? a.session : null;
    if (a.kind === 'member'){
      // a real organization: its own data only, never a demo org's
      const own = { id: a.org.id, name: a.org.name, demo: false };
      let has = false;
      try { const { data } = await db.rpc('mm_llm_summary', { p_org: a.org.id }); has = !!(data && data.some(r => r.n > 0)); } catch (e) {}
      return { db, s, access: a, orgs: [own], org: own, info: null, real: true, empty: !has };
    }
    let pubs = [];
    try { const { data, error } = await db.rpc('mm_llm_public_org'); if (error) throw error; pubs = data || []; }
    catch (e) { return { error: 'Couldn’t reach the server: ' + (e.message || e) }; }
    const orgs = pubs.map(p => ({ id: p.id, name: p.name, demo: true }));
    if (!orgs.length) return { error: 'No organization with MM LLM data is published yet.', db, s };
    const want = new URLSearchParams(location.search).get('org') || (() => { try { return localStorage.getItem(KEY); } catch (e) { return null; } })();
    const org = orgs.find(o => o.name === want || o.id === want) || orgs[0];
    return { db, s, access: a, orgs, org, info: info(org.name) };
  }

  function choose(st, org){
    st.org = org; st.info = info(org.name);
    try { localStorage.setItem(KEY, org.name); } catch (e) {}
    const u = new URL(location.href); u.searchParams.set('org', org.name); history.replaceState(null, '', u);
  }

  function picker(el, st, onChange){
    el.textContent = '';
    if (st.orgs.length < 2){ const b = document.createElement('b'); b.textContent = st.org.name; el.appendChild(b); return; }
    const sel = document.createElement('select'); sel.className = 'mm-orgpick'; sel.setAttribute('aria-label', 'Organization');
    st.orgs.forEach(o => { const op = document.createElement('option'); op.value = o.id; op.textContent = o.name + (o.demo ? ' (demo)' : ''); op.selected = o.id === st.org.id; sel.appendChild(op); });
    sel.addEventListener('change', () => { const o = st.orgs.find(x => x.id === sel.value); choose(st, o); onChange(o); });
    el.appendChild(sel);
  }

  async function rpc(st, fn, args){
    const { data, error } = await st.db.rpc(fn, Object.assign({ p_org: st.org.id }, args || {}));
    if (error) throw new Error(`${fn}: ${error.message}`);
    return data || [];
  }

  // "Today" for an org: the last day of its production or BUS data. A demo org also gets st.info.today and .from
  // (the 365-day year ending today) for captions and default ranges.
  async function today(st){
    if (st.info && st.info.today) return st.info.today;
    const sm = await rpc(st, 'mm_llm_summary');
    const d = sm.map(r => r.last_day).filter(Boolean).sort().pop() || new Date().toISOString().slice(0, 10);
    if (st.info){
      const f = new Date(d + 'T12:00:00Z'); f.setUTCDate(f.getUTCDate() - 364);
      Object.assign(st.info, { today: d, from: f.toISOString().slice(0, 10) });
    }
    return d;
  }

  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const num = (v, d = 0) => v == null || v === '' || isNaN(+v) ? '—' : (+v).toLocaleString(undefined, { maximumFractionDigits: d, minimumFractionDigits: d });
  const day = v => { if (!v) return '—'; const [y, m, d] = String(v).slice(0, 10).split('-').map(Number); return new Date(y, m - 1, d).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }); };
  const time = v => v ? new Date(v).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', timeZone: 'America/New_York' }) : '—';

  // cols: [key, label, kind?] — kind 'n' (number), 'n1', 'n2', 'd' (date), 't' (time), or a function(row) -> html string
  function table(rows, cols, empty){
    const wrap = document.createElement('div'); wrap.className = 'dt-wrap';
    if (!rows.length){ const p = document.createElement('p'); p.className = 'dt-empty'; p.textContent = empty || 'Nothing here.'; wrap.appendChild(p); return wrap; }
    const t = document.createElement('table'); t.className = 'dt';
    t.innerHTML = '<thead><tr>' + cols.map(c => `<th${/^n/.test(c[2] || '') ? ' class="n"' : ''}>${esc(c[1])}</th>`).join('') + '</tr></thead>';
    const tb = document.createElement('tbody');
    for (const r of rows){
      const tr = document.createElement('tr');
      tr.innerHTML = cols.map(([k, , kind]) => {
        const v = r[k];
        if (typeof kind === 'function') return `<td>${kind(r)}</td>`;
        if (kind === 'n') return `<td class="n">${num(v)}</td>`;
        if (kind === 'n1') return `<td class="n">${num(v, 1)}</td>`;
        if (kind === 'n2') return `<td class="n">${num(v, 2)}</td>`;
        if (kind === 'd') return `<td class="n">${day(v)}</td>`;
        if (kind === 't') return `<td class="n">${time(v)}</td>`;
        return `<td>${esc(Array.isArray(v) ? v.join(', ') : v == null ? '—' : v)}</td>`;
      }).join('');
      tb.appendChild(tr);
    }
    t.appendChild(tb); wrap.appendChild(t); return wrap;
  }

  // One-hue horizontal bars (magnitude): [{ label, value, note }]. Hover shows the exact value; the numbers are
  // also printed at the bar end, and the same rows are in a table on the page.
  function bars(items, unit){
    const max = Math.max(1e-9, ...items.map(i => +i.value || 0));
    const box = document.createElement('div'); box.className = 'hb'; box.setAttribute('role', 'img');
    box.setAttribute('aria-label', items.map(i => `${i.label}: ${num(i.value, 1)} ${unit}`).join('; '));
    for (const i of items){
      const row = document.createElement('div'); row.className = 'hb-r'; row.title = `${i.label}: ${num(i.value, 1)} ${unit}${i.note ? ' · ' + i.note : ''}`;
      row.innerHTML = `<span class="hb-l">${esc(i.label)}</span><span class="hb-t"><span class="hb-b" style="width:${(100 * (+i.value || 0) / max).toFixed(1)}%"></span></span><span class="hb-v">${num(i.value, 1)}</span>`;
      box.appendChild(row);
    }
    return box;
  }

  // A signed URL for a stored original (bucket mm-files, <org>/llm/<path>), readable for members and public demo orgs.
  async function fileUrl(st, path){
    const { data, error } = await st.db.storage.from('mm-files').createSignedUrl(`${st.org.id}/llm/${path}`, 3600);
    if (error) throw error;
    return data.signedUrl;
  }

  // The page a real organization sees before its own data is loaded: what the page will show and what feeds it.
  //   MMLLMOrg.placeholder(st, { title, text, needs: ['BUS daily sheet', …], links: [['DailyNotes.html', 'Notes board']] })
  function placeholder(st, o){
    const $ = id => document.getElementById(id);
    document.querySelectorAll('.dbar > :not(.org):not(.grow):not(.nb)').forEach(e => { e.hidden = true; });
    const org = $('org'); if (org) { org.textContent = ''; const b = document.createElement('b'); b.textContent = st.org.name; org.appendChild(b); }
    const sub = $('sub'); if (sub) sub.hidden = true;
    const body = $('body'); if (!body) return;
    body.innerHTML = `<section class="ph"><div class="ph-i" aria-hidden="true">${window.MMIcons ? MMIcons.svg(o.icon || 'file') : ''}</div>
      <h2>${esc(o.title || 'Nothing here yet')}</h2><p>${esc(o.text || '')}</p>
      ${o.needs && o.needs.length ? `<p class="ph-l">It fills in from ${esc(st.org.name)}’s own:</p><ul>${o.needs.map(n => `<li>${esc(n)}</li>`).join('')}</ul>` : ''}
      <p class="ph-n">Nothing is shown until your organization’s files are loaded. The demo data lives in the demo account.</p>
      ${o.links && o.links.length ? `<div class="ph-a">${o.links.map(([h, t]) => `<a class="btn" href="${esc(h)}">${esc(t)}</a>`).join('')}</div>` : ''}
    </section>`;
  }

  window.MMLLMOrg = { resolve, placeholder, choose, picker, rpc, today, table, bars, fileUrl, esc, num, day, time, DEMO };
})();
