// Machine Manager — app switcher. The menu button top left (☰) on every page opens a list
// of all apps; the one you're on is highlighted. Add new tools to APPS below.
(() => {
  const APPS = [
    { href: 'index.html', name: 'Overview', ic: 'board' },
    { href: 'MyMachine.html', name: 'My Machine', ic: 'machine' },
    { href: 'OperationsOutagePlanning.html', name: 'Operations Outage Planning', ic: 'calendar' },
    { href: 'TaskPackageLibrary.html', name: 'Ops Task Library', ic: 'list' },
    { href: 'ConsumablesTracker.html', name: 'Consumables Tracker', ic: 'box' },
    { href: 'Whiteboard.html', name: 'Whiteboard', ic: 'frame' },
    { href: 'Daily.html', name: 'Daily', sub: 'Planned', ic: 'book' },
    { href: 'MMLLM.html', name: 'MM LLM', sub: 'Planned', ic: 'message' },
    { href: 'VendorReports.html', name: 'Vendor Reports', sub: 'Planned', ic: 'file' },
    { href: 'http://10.15.212.124:8000', name: 'FieldAgent', sub: 'Mill network', external: true, ic: 'network' },
  ];

  const css = document.createElement('style');
  css.textContent = `
  button.mmnav{padding:0;cursor:pointer;font:inherit;flex:none}
  button.mmnav svg{display:block}
  .mmnav-menu{position:fixed;z-index:10000;min-width:248px;max-height:calc(100vh - 24px);overflow:auto;background:var(--overlay);
    border:1px solid var(--line-strong);border-radius:var(--r-lg);box-shadow:var(--shadow-pop);padding:4px;
    font:13px/1.3 var(--font);color:var(--ink)}
  .mmnav-menu[hidden]{display:none}
  .mmnav-menu a,.mmnav-menu .cur{display:flex;align-items:center;gap:10px;padding:0 8px;height:32px;border-radius:var(--r-sm);
    text-decoration:none;color:var(--ink-2);font-weight:500}
  .mmnav-menu a .mi-ic,.mmnav-menu .cur .mi-ic{color:var(--muted)}
  .mmnav-menu a:hover,.mmnav-menu a:focus-visible{background:var(--hover-2);color:var(--ink);outline:none}
  .mmnav-menu .cur{color:var(--ink);background:var(--hover);cursor:default}
  .mmnav-menu .cur .mi-ic{color:var(--accent)}
  .mmnav-menu .nm{flex:1}
  .mmnav-menu small{font-size:11px;font-weight:400;color:var(--ink-3);white-space:nowrap}
  .mmnav-menu hr{border:0;border-top:1px solid var(--line);margin:4px 2px}
  .mmnav-set{padding:6px 8px 6px}
  .mmnav-set .lb{font-size:12px;font-weight:500;color:var(--muted);margin:0 0 6px}
  .mmnav-seg{display:grid;grid-template-columns:repeat(3,1fr);gap:2px;padding:2px;border-radius:var(--r-sm);background:var(--hover)}
  .mmnav-seg button{display:flex;align-items:center;justify-content:center;gap:5px;height:26px;border:0;border-radius:5px;background:transparent;
    color:var(--muted);font:500 12px var(--font);cursor:pointer}
  .mmnav-seg button:hover{color:var(--ink)}
  .mmnav-seg button[aria-checked="true"]{background:var(--surface);color:var(--ink);box-shadow:0 0 0 1px var(--line-strong)}
  .mmnav-ver{display:none;padding:6px 8px 4px;font-size:11px;color:var(--ink-3);text-align:right}
  @media (max-width:760px){
    .mmnav-menu{left:8px!important;right:8px;max-height:calc(100dvh - 72px)}
    .mmnav-ver:not(:empty){display:block}
  }
  @media (pointer:coarse){
    .mmnav-menu a,.mmnav-menu .cur{height:44px}
    .mmnav-seg button{height:36px}
  }`;
  document.head.appendChild(css);

  const file = (location.pathname.split('/').pop() || 'index.html').toLowerCase();
  const isCurrent = a => !a.external && a.href.toLowerCase() === (file.endsWith('.html') ? file : 'index.html');

  function init(){
    const btn = document.querySelector('button.mmnav');
    if (!btn) return;
    btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true"><path d="M2.5 4h11M2.5 8h11M2.5 12h11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>';
    const menu = document.createElement('div');
    menu.className = 'mmnav-menu'; menu.hidden = true; menu.setAttribute('role', 'menu'); menu.id = 'mmnavMenu';
    btn.setAttribute('aria-controls', menu.id);
    APPS.forEach((a, i) => {
      if (i === 1 || (a.sub === 'Planned' && APPS[i - 1].sub !== 'Planned') || a.external) menu.appendChild(document.createElement('hr'));
      let el;
      if (isCurrent(a)){
        el = document.createElement('div'); el.className = 'cur'; el.setAttribute('aria-disabled', 'true'); el.setAttribute('aria-current', 'page');
      } else {
        el = document.createElement('a'); el.href = a.href;
        if (a.external){ el.target = '_blank'; el.rel = 'noopener'; }
      }
      el.setAttribute('role', 'menuitem');
      if (window.MMIcons && a.ic) el.appendChild(MMIcons.el(a.ic, 'sm'));
      const n = document.createElement('span'); n.className = 'nm'; n.textContent = a.name; el.appendChild(n);
      if (a.external && window.MMIcons) el.appendChild(MMIcons.el('external', 'xs'));
      const sub = a.sub;
      if (sub){ const s = document.createElement('small'); s.textContent = sub; el.appendChild(s); }
      menu.appendChild(el);
    });
    // Settings, at the bottom: appearance (mm-theme.js). Saved with the signed-in account.
    if (window.MMTheme){
      menu.appendChild(document.createElement('hr'));
      const set = document.createElement('div'); set.className = 'mmnav-set';
      const lb = document.createElement('div'); lb.className = 'lb'; lb.id = 'mmnavAppearance'; lb.textContent = 'Appearance';
      const seg = document.createElement('div'); seg.className = 'mmnav-seg'; seg.setAttribute('role', 'radiogroup'); seg.setAttribute('aria-labelledby', lb.id);
      const OPTS = [['system', 'System', 'monitor'], ['light', 'Light', 'sun'], ['dark', 'Dark', 'moon']];
      const btns = OPTS.map(([v, label, ic]) => {
        const b = document.createElement('button'); b.type = 'button'; b.setAttribute('role', 'radio'); b.dataset.theme = v;
        b.title = v === 'system' ? 'Follow this computer’s light / dark setting' : label + ' mode';
        if (window.MMIcons) b.appendChild(MMIcons.el(ic, 'xs'));
        b.append(label);
        b.addEventListener('click', () => MMTheme.set(v));
        seg.appendChild(b); return b;
      });
      const sync = () => btns.forEach(b => b.setAttribute('aria-checked', String(b.dataset.theme === MMTheme.pref())));
      MMTheme.onChange(sync); sync();
      set.append(lb, seg); menu.appendChild(set);
    }
    // Phones hide the floating version footer; show it at the bottom of this menu instead.
    const ver = document.createElement('div'); ver.className = 'mmnav-ver'; menu.appendChild(ver);
    document.body.appendChild(menu);

    const links = () => [...menu.querySelectorAll('a')];
    function open(){
      const v = document.getElementById('ver'); ver.textContent = v ? v.textContent.trim() : '';
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
    // Phone browsers resize the window as their address bar slides away; only a real width change closes the menu.
    let lastW = innerWidth;
    window.addEventListener('resize', () => { if (innerWidth !== lastW){ lastW = innerWidth; close(); } });
    window.addEventListener('blur', () => close());
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();

  // Tool rows that scroll sideways on phones: mark which ends have more buttons hidden, so mm-theme.css can fade that edge.
  function watchRows(){
    const rows = document.querySelectorAll('.mm-top .bar:not(.brand), body.mm-canvas #toolbar');
    rows.forEach(row => {
      const mark = () => {
        const more = [];
        if (row.scrollLeft > 2) more.push('l');
        if (row.scrollLeft + row.clientWidth < row.scrollWidth - 2) more.push('r');
        const v = more.join(' ');
        if (row.dataset.more !== v) row.dataset.more = v;
      };
      row.addEventListener('scroll', mark, { passive: true });
      if (window.ResizeObserver) new ResizeObserver(mark).observe(row);
      new MutationObserver(mark).observe(row, { childList: true, subtree: true, attributes: true, attributeFilter: ['hidden'] });
      mark();
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', watchRows); else watchRows();
  // Paper is white: print with the light colour set from mm-theme.css (one copy, shared with the print preview).
  window.addEventListener('beforeprint', () => document.documentElement.classList.add('mm-light'));
  window.addEventListener('afterprint', () => document.documentElement.classList.remove('mm-light'));
})();
