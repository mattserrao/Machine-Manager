// Machine Manager — shared sign-in and Supabase access for every tool page.
// Load after vendor/supabase-*.js and mm-config.js. Exposes window.MMCloud.
//
// Signed out  → demo mode: tools keep their data in this browser only.
// Signed in   → data lives in Supabase under the chosen org, shared with its members.
(() => {
  const cfg = window.MM_CONFIG || {};
  const enabled = !!(cfg.supabaseUrl && cfg.supabaseKey && window.supabase);
  const ORG_KEY = 'mm-org';
  const client = enabled ? window.supabase.createClient(cfg.supabaseUrl, cfg.supabaseKey, {
    auth: { storageKey: 'mm-auth', persistSession: true, autoRefreshToken: true, detectSessionInUrl: false },
  }) : null;

  let cached = null;   // { user, orgs:[{id,name,role}], org }

  const lsGet = k => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  const lsSet = (k, v) => { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch (e) {} };

  // Resolves to null in demo mode, otherwise { user, orgs, org }. org is null if the
  // account hasn't been added to any org yet.
  async function session(force){
    if (!enabled) return null;
    if (cached && !force) return cached;
    const { data: { session: s } } = await client.auth.getSession();
    if (!s) { cached = null; return null; }
    const { data: rows, error } = await client.from('memberships')
      .select('role, org:orgs(id, name)').eq('user_id', s.user.id);
    if (error) throw error;
    const orgs = (rows || []).filter(r => r.org).map(r => ({ id: r.org.id, name: r.org.name, role: r.role }))
      .sort((a, b) => a.name.localeCompare(b.name));
    const want = lsGet(ORG_KEY);
    const org = orgs.find(o => o.id === want) || orgs[0] || null;
    cached = { user: s.user, orgs, org };
    return cached;
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

  // Reload every open tool page when this browser signs in or out in another tab.
  if (enabled) {
    // (Token refreshes also touch mm-auth, so only reload when the signed-in user changes.)
    const uidOf = v => { try { return (JSON.parse(v) || {}).user.id; } catch (e) { return null; } };
    window.addEventListener('storage', e => {
      if (e.key === ORG_KEY || (e.key === 'mm-auth' && uidOf(e.oldValue) !== uidOf(e.newValue))) location.reload();
    });
  }

  window.MMCloud = { enabled, client, session, signIn, signOut, setOrg, canEdit };
})();
