// Machine Manager — app switcher. The menu button top left (☰) on every page opens a list
// of all apps; the one you're on is shown greyed out. Add new tools to APPS below.
(() => {
  const APPS = [
    { href: 'index.html', name: 'Overview', sub: 'All tools' },
    { href: 'ConsumablesTracker.html', name: 'Consumables Tracker' },
    { href: 'MyMachine.html', name: 'My Machine' },
    { href: 'OperationsOutagePlanning.html', name: 'Operations Outage Planning' },
    { href: 'PM1LLM.html', name: 'PM1 LLM' },
    { href: 'TaskPackageLibrary.html', name: 'Task Package Library' },
    { href: 'VendorReports.html', name: 'Vendor Reports' },
    { href: 'Whiteboard.html', name: 'Whiteboard' },
    { href: 'http://10.15.212.124:8000', name: 'FieldAgent', sub: 'Mill network only', external: true },
  ];

  const css = document.createElement('style');
  css.textContent = `
  button.mmnav{border:0;padding:0;cursor:pointer;font:inherit;flex:none}
  button.mmnav:hover{background:#000}
  button.mmnav:focus-visible{outline:2px solid #2563eb;outline-offset:2px}
  button.mmnav svg{display:block}
  .mmnav-menu{position:fixed;z-index:10000;min-width:240px;max-height:calc(100vh - 24px);overflow:auto;background:#fff;
    border:1px solid #e5e7eb;border-radius:12px;box-shadow:0 12px 32px rgba(0,0,0,.16);padding:6px;
    font:13px/1.3 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:#1f2328}
  .mmnav-menu[hidden]{display:none}
  .mmnav-menu .ml{font-size:11px;font-weight:600;color:#6b7280;text-transform:uppercase;letter-spacing:.06em;padding:6px 10px 4px}
  .mmnav-menu a,.mmnav-menu .cur{display:flex;align-items:baseline;justify-content:space-between;gap:12px;padding:7px 10px;border-radius:8px;
    text-decoration:none;color:inherit;font-weight:500}
  .mmnav-menu a:hover,.mmnav-menu a:focus-visible{background:#f5f5f4;outline:none}
  .mmnav-menu .cur{color:#a8a29e;cursor:default}
  .mmnav-menu small{font-size:11px;font-weight:400;color:#a8a29e;white-space:nowrap}
  .mmnav-menu hr{border:0;border-top:1px solid #e5e7eb;margin:5px 4px}`;
  document.head.appendChild(css);

  const file = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  const isCurrent = a => !a.external && a.href.toLowerCase() === (file.endsWith('.html') ? file : 'index.html');

  function init(){
    const btn = document.querySelector('button.mmnav');
    if (!btn) return;
    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M2.5 4h11M2.5 8h11M2.5 12h11" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>';
    const menu = document.createElement('div');
    menu.className = 'mmnav-menu'; menu.hidden = true; menu.setAttribute('role', 'menu'); menu.id = 'mmnavMenu';
    btn.setAttribute('aria-controls', menu.id);
    const label = document.createElement('div'); label.className = 'ml'; label.textContent = 'Apps'; menu.appendChild(label);
    APPS.forEach((a, i) => {
      if (i === 1 || a.external) menu.appendChild(document.createElement('hr'));
      let el;
      if (isCurrent(a)){
        el = document.createElement('div'); el.className = 'cur'; el.setAttribute('aria-disabled', 'true'); el.setAttribute('aria-current', 'page');
      } else {
        el = document.createElement('a'); el.href = a.href;
        if (a.external){ el.target = '_blank'; el.rel = 'noopener'; }
      }
      el.setAttribute('role', 'menuitem');
      const n = document.createElement('span'); n.textContent = a.name + (a.external ? ' ↗' : ''); el.appendChild(n);
      const sub = isCurrent(a) ? 'You’re here' : a.sub;
      if (sub){ const s = document.createElement('small'); s.textContent = sub; el.appendChild(s); }
      menu.appendChild(el);
    });
    document.body.appendChild(menu);

    const links = () => [...menu.querySelectorAll('a')];
    function open(){
      const r = btn.getBoundingClientRect();
      menu.style.left = Math.max(8, r.left) + 'px'; menu.style.top = (r.bottom + 8) + 'px';
      menu.hidden = false; btn.setAttribute('aria-expanded', 'true');
      const first = links()[0]; if (first) first.focus({ preventScroll: true });
    }
    function close(refocus){ if (menu.hidden) return; menu.hidden = true; btn.setAttribute('aria-expanded', 'false'); if (refocus) btn.focus(); }
    btn.addEventListener('click', e => { e.stopPropagation(); menu.hidden ? open() : close(); });
    menu.addEventListener('pointerdown', e => e.stopPropagation());
    menu.addEventListener('click', e => e.stopPropagation());
    document.addEventListener('pointerdown', e => { if (!menu.hidden && !btn.contains(e.target) && !menu.contains(e.target)) close(); }, true);
    menu.addEventListener('keydown', e => {
      const ls = links(), i = ls.indexOf(document.activeElement);
      if (e.key === 'Escape'){ e.preventDefault(); e.stopPropagation(); close(true); }
      else if (e.key === 'ArrowDown'){ e.preventDefault(); ls[(i + 1) % ls.length].focus(); }
      else if (e.key === 'ArrowUp'){ e.preventDefault(); ls[(i - 1 + ls.length) % ls.length].focus(); }
      else if (e.key === 'Tab'){ close(); }
      e.stopPropagation();       // keep tool shortcuts (e.g. the Whiteboard's) from firing while the menu is open
    });
    window.addEventListener('resize', () => close());
    window.addEventListener('blur', () => close());
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
