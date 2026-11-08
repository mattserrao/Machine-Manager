// Machine Manager — light / dark / system appearance. Load in <head>, before any stylesheet paints,
// so the page never flashes the wrong colours.
//
//   MMTheme.pref()            'system' | 'light' | 'dark'   (what the person picked; default 'system')
//   MMTheme.mode()            'light' | 'dark'              (what's showing now)
//   MMTheme.set(pref)         pick one: applies now, remembers it, and saves it to the signed-in account
//   MMTheme.onChange(fn)      fn(pref, mode) whenever either changes
//
// The choice is kept with the signed-in account (Supabase user metadata, via mm-cloud.js) so it follows the
// person to any computer, and cached in this browser so pages open in the right mode before sign-in loads.
// Signed out / demo: this browser only. <html data-theme="light|dark"> drives the tokens in mm-theme.css.
(() => {
  const KEY = 'mm-theme', PREFS = ['system', 'light', 'dark'];
  const mq = window.matchMedia ? matchMedia('(prefers-color-scheme: light)') : null;
  const ls = { get(){ try { return localStorage.getItem(KEY); } catch (e) { return null; } },
               set(v){ try { localStorage.setItem(KEY, v); } catch (e) {} } };
  const subs = [];
  let pref = PREFS.includes(ls.get()) ? ls.get() : 'system';

  const mode = () => pref === 'system' ? (mq && mq.matches ? 'light' : 'dark') : pref;
  function apply(){
    const m = mode(), root = document.documentElement;
    if (root.dataset.theme !== m) root.dataset.theme = m;
    root.dataset.themePref = pref;
    subs.forEach(fn => { try { fn(pref, m); } catch (e) {} });
  }
  function use(p, { remember = true } = {}){
    if (!PREFS.includes(p)) return;
    pref = p; if (remember) ls.set(p); apply();
  }

  window.MMTheme = {
    pref: () => pref, mode, prefs: PREFS.slice(),
    onChange(fn){ subs.push(fn); },
    // the person picked one in the menu
    set(p){
      use(p);
      if (window.MMCloud && MMCloud.saveTheme) MMCloud.saveTheme(p).catch(() => {});
    },
    // the signed-in account's saved choice (from mm-cloud.js once the session loads)
    fromAccount(p){ if (PREFS.includes(p) && p !== pref) use(p); },
  };

  if (mq) (mq.addEventListener ? mq.addEventListener('change', apply) : mq.addListener(apply));
  // another tab changed it
  window.addEventListener('storage', e => { if (e.key === KEY && PREFS.includes(e.newValue)) use(e.newValue, { remember: false }); });
  apply();
})();
