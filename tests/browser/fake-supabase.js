// Stand-in for vendor/supabase-*.js in browser tests: a signed-in editor of org "PM1" and an in-memory
// mm_records table with mm_apply's rules. Seed rows with window.__seedRows before the page loads; every
// mm_apply call is kept in window.__rpcLog.
(() => {
  const rows = new Map(), log = (window.__rpcLog = []);
  let clock = Date.parse('2026-11-07T12:00:00Z');
  const ORG = window.__orgId || 'org-pm1', ORG_NAME = window.__orgName || 'PM1', clone = o => JSON.parse(JSON.stringify(o));
  const key = (t, id) => `${t}|${id}`;
  // Rows live in sessionStorage so they survive a reload of the page (like a real server would).
  let saved = null; try { saved = JSON.parse(sessionStorage.getItem('__fakeRows')); } catch (e) {}
  const persist = () => { try { sessionStorage.setItem('__fakeRows', JSON.stringify([...rows.values()])); } catch (e) {} };
  if (saved) for (const r of saved) rows.set(key(r.tool, r.id), r);
  else for (const r of (window.__seedRows || [])) rows.set(key(r.tool, r.id), Object.assign({ org_id: ORG, deleted: false, version: 1, updated_at: new Date(clock).toISOString() }, r));
  const stamp = r => { r.updated_at = new Date(clock += 1000).toISOString(); };
  function apply(tool, changes){
    return changes.map(c => {
      const k = key(tool, c.id), cur = rows.get(k);
      if (c.base == null){
        if (cur && !cur.deleted) return { id: c.id, ok: false, row: clone(cur) };
        const r = cur || { org_id: ORG, tool, id: c.id, version: 0 };
        Object.assign(r, { data: c.data || {}, deleted: !!c.deleted, version: r.version + 1 }); stamp(r); rows.set(k, r);
        return { id: c.id, ok: true, version: r.version };
      }
      if (!cur || cur.version !== c.base) return { id: c.id, ok: false, row: cur ? clone(cur) : null };
      if (c.data !== undefined) cur.data = c.data; if (c.deleted != null) cur.deleted = c.deleted; cur.version++; stamp(cur);
      return { id: c.id, ok: true, version: cur.version };
    });
  }
  function query(table){
    const f = [], q = {};
    const api = {
      select(){ return api; }, order(){ return api; },
      eq(k, v){ f.push(r => r[k] === v); return api; }, gt(k, v){ f.push(r => r[k] > v); return api; },
      gte(k, v){ f.push(r => r[k] >= v); return api; }, limit(n){ q.limit = n; return api; }, range(a, b){ q.range = [a, b]; return api; },
      then(res, rej){
        Promise.resolve().then(() => {
          if (table === 'memberships') return { data: [{ role: 'editor', org: { id: ORG, name: ORG_NAME } }], error: null };
          let all = [...rows.values()].filter(r => f.every(fn => fn(r))).sort((a, b) => a.id < b.id ? -1 : 1);
          if (q.range) all = all.slice(q.range[0], q.range[1] + 1); else if (q.limit) all = all.slice(0, q.limit);
          return { data: clone(all), error: null };
        }).then(res, rej);
      },
    };
    return api;
  }
  const session = { user: { id: 'user-1', email: 'matt@example.com', user_metadata: window.__userMeta || {} } };
  window.supabase = {
    createClient: () => ({
      auth: { getSession: async () => ({ data: { session } }), signOut: async () => ({}), signInWithPassword: async () => ({}),
        updateUser: async ({ data }) => { session.user.user_metadata = Object.assign({}, session.user.user_metadata, data); window.__metaSaved = session.user.user_metadata; return { data: { user: session.user }, error: null }; } },
      from: query,
      async rpc(name, args){
        if (name === 'mm_apply'){ log.push(clone(args)); const data = apply(args.p_tool, args.p_changes); persist(); return { data, error: null }; }
        if (name === 'mm_file_refs') return { data: [], error: null };
        // MM LLM data pages: one public demo org (Sim Mill); PM1 has no data of its own. Every call is kept, so a
        // test can check the real org never asks for the demo org's rows.
        (window.__llmCalls = window.__llmCalls || []).push({ name, args: clone(args || {}) });
        if (name === 'mm_llm_public_org') return { data: [{ id: 'org-sim', name: 'Sim Mill' }], error: null };
        if (name === 'mm_llm_summary') return { data: args.p_org === 'org-sim' ? [{ source: 'BUS lines', n: 10, last_day: '2026-10-31' }] : [], error: null };
        if (name === 'mm_llm_my_access') return { data: ORG === 'org-sim' ? [{ org_id: ORG, org_name: ORG_NAME, daily_limit: 40, used_today: 0 }] : [], error: null };
        if (name === 'mm_llm_saved_answers' || name === 'mm_llm_my_answers') return { data: [], error: null };
        return { data: null, error: { message: 'unknown rpc ' + name } };
      },
      functions: { invoke: async (name, { body }) => { (window.__invokes = window.__invokes || []).push({ name, body: clone(body) });
        return { data: { id: 1, status: 'ok', answer: 'Six actions are overdue [Action: SM-0008].', model: body.model === 'opus' ? 'claude-opus-5-5' : 'claude-sonnet-5-5',
          provider: 'anthropic', ms: 1200, remaining: 39, trace: [{ tool: 'overdue_actions', rows: 6 }],
          charts: [{ title: 'Overdue by owner', type: 'bar', unit: 'actions', labels: ['A', 'B'], series: [{ name: 'Actions', values: [4, 2] }] }] }, error: null }; } },
      channel(){ const ch = { on(){ return ch; }, subscribe(cb){ setTimeout(() => cb('SUBSCRIBED'), 1); return ch; } }; return ch; },
      storage: { from: () => ({ list: async () => ({ data: [], error: null }), remove: async () => ({ error: null }),
        upload: async () => ({ error: null }), download: async () => ({ data: null, error: { message: 'none' } }) }) },
    }),
  };
  window.__rows = () => clone([...rows.values()]);
})();
