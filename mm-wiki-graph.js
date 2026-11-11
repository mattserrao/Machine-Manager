/* MM wiki graph: a force-laid-out map of a wiki's pages and [[links]] (canvas).
   Node area is proportional to the page's size (bytes), colour shows the page type, lines are links (width = mention count),
   dashed ghost nodes are links to pages not written yet. Hover for details, click to focus a page and its neighbours.
     MMWikiGraph.mount(el, { sources: [{ label: 'Sim Mill', url: 'demo-data/wiki/sim-mill.json' }, ...] })
   Data (tools in the wiki-memory branch write it): { org, lint:{...}, nodes:[{slug,type,title,description,bytes,citations,conflicts}],
   edges:[{from,to,weight,redlink}] } */
(function () {
  const css = (n, el) => getComputedStyle(el || document.documentElement).getPropertyValue(n).trim() || '#888';
  const TYPE_ORDER = ['position', 'equipment', 'outage', 'failure-mode', 'document', 'topic', 'vendor', 'rcfa', 'root', 'other'];
  const TYPE_LABEL = { position: 'Position', equipment: 'Equipment', outage: 'Outage', 'failure-mode': 'Failure mode', document: 'Document',
    topic: 'Topic', vendor: 'Vendor', rcfa: 'RCFA', root: 'Index', other: 'Other', ghost: 'Not written yet' };
  const kb = (b) => b >= 10240 ? Math.round(b / 1024) + ' KB' : (b / 1024).toFixed(1) + ' KB';

  function palette() {   // greys plus the app accent and its warm attention colour, in lightness steps
    const a = css('--accent'), ai = css('--accent-ink'), w = css('--warn'), wi = css('--warn-ink'), i2 = css('--ink-2'), m = css('--muted'), f = css('--faint');
    return { position: a, equipment: ai, outage: w, 'failure-mode': wi, document: a, topic: i2, vendor: m, rcfa: wi, root: i2, other: f,
      line: css('--line-strong'), ink: css('--ink'), muted: css('--muted'), bg: css('--surface'), accent: a, faint: f };
  }

  function layout(nodes, edges, W, H) {
    // Fruchterman–Reingold with gravity; seeded so the map is the same each visit.
    let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;
    const idx = new Map(nodes.map((n, i) => [n.slug, i]));
    nodes.forEach((n) => { n.x = W / 2 + (rnd() - .5) * W * .8; n.y = H / 2 + (rnd() - .5) * H * .8; n.vx = 0; n.vy = 0; });
    const E = edges.map((e) => [idx.get(e.from), idx.get(e.to), e.weight]).filter((e) => e[0] !== undefined && e[1] !== undefined);
    const k = Math.sqrt((W * H) / Math.max(1, nodes.length)) * .55;
    for (let it = 0; it < 320; it++) {
      const t = (1 - it / 320) * k * .6;
      for (const n of nodes) { n.dx = 0; n.dy = 0; }
      for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j]; let dx = a.x - b.x, dy = a.y - b.y; let d2 = dx * dx + dy * dy || .01;
        const d = Math.sqrt(d2), f = (k * k) / d + (a.r + b.r) * 2 / Math.max(d, 1);
        dx /= d; dy /= d; a.dx += dx * f; a.dy += dy * f; b.dx -= dx * f; b.dy -= dy * f;
      }
      for (const [i, j, w] of E) {
        const a = nodes[i], b = nodes[j]; const dx = a.x - b.x, dy = a.y - b.y, d = Math.sqrt(dx * dx + dy * dy) || .01;
        const f = (d * d) / k * Math.min(1.6, .5 + Math.log2(1 + w) * .25);
        a.dx -= dx / d * f; a.dy -= dy / d * f; b.dx += dx / d * f; b.dy += dy / d * f;
      }
      for (const n of nodes) {
        n.dx += (W / 2 - n.x) * .02 * k / 40; n.dy += (H / 2 - n.y) * .02 * k / 40;   // gravity
        const d = Math.sqrt(n.dx * n.dx + n.dy * n.dy) || 1;
        n.x += n.dx / d * Math.min(d, t); n.y += n.dy / d * Math.min(d, t);
        n.x = Math.max(n.r + 4, Math.min(W - n.r - 4, n.x)); n.y = Math.max(n.r + 4, Math.min(H - n.r - 4, n.y));
      }
    }
  }

  function mount(el, opts) {
    el.classList.add('wg');
    el.innerHTML = `
      <div class="wg-bar">
        <div class="wg-seg" role="group" aria-label="Wiki"></div>
        <label class="wg-f">Size <select class="wg-size">
          <option value="bytes">Page size</option><option value="in">Links in</option><option value="cites">Citations</option></select></label>
        <label class="wg-f">Show <select class="wg-type"><option value="">All types</option></select></label>
        <input class="wg-q" type="search" placeholder="Find a page" aria-label="Find a page">
      </div>
      <div class="wg-health" aria-live="polite"></div>
      <div class="wg-main">
        <div class="wg-canvas"><canvas role="img" aria-label="Wiki pages and their links"></canvas><div class="wg-tip" hidden></div></div>
        <aside class="wg-side"><p class="wg-hint">Hover a circle for its page; click to focus it and its neighbours. Circle area = page size.</p></aside>
      </div>
      <div class="wg-key"></div>`;
    const $ = (s) => el.querySelector(s);
    const cv = $('canvas'), ctx = cv.getContext('2d'), tip = $('.wg-tip'), side = $('.wg-side');
    let data = null, nodes = [], edges = [], sel = null, hover = null, sizeBy = 'bytes', typeF = '', q = '', P = palette(), W = 0, H = 0;
    const cache = {};

    opts.sources.forEach((s, i) => {
      const b = document.createElement('button'); b.type = 'button'; b.className = 'btn sm'; b.textContent = s.label;
      b.setAttribute('aria-pressed', String(i === 0)); b.onclick = () => { el.querySelectorAll('.wg-seg button').forEach((x) => x.setAttribute('aria-pressed', String(x === b))); load(s); };
      $('.wg-seg').appendChild(b);
    });
    $('.wg-size').onchange = (e) => { sizeBy = e.target.value; build(); };
    $('.wg-type').onchange = (e) => { typeF = e.target.value; draw(); };
    $('.wg-q').oninput = (e) => { q = e.target.value.trim().toLowerCase(); draw(); };

    async function load(s) {
      side.innerHTML = '<p class="wg-hint">Loading…</p>';
      try { data = cache[s.url] ??= await (await fetch(s.url, { cache: 'no-cache' })).json(); }
      catch { side.innerHTML = '<p class="wg-hint">Could not load the wiki map.</p>'; return; }
      sel = null; build(); health(); showSide(null);
    }
    function health() {
      const L = data.lint || {};
      const items = [['Pages', L.pages], ['Links', L.links], ['Not written yet', L.redlink_targets], ['Conflicts marked', L.conflicts],
        ['Fact lines cited', L.fact_lines ? Math.round(100 * (1 - L.uncited_lines / L.fact_lines)) + '%' : '–'],
        ['Wiki size vs sources', L.ratio != null ? Math.round(L.ratio * 100) + '%' : '–']];
      $('.wg-health').innerHTML = items.map(([k, v]) => `<span><b>${v ?? '–'}</b>${k}</span>`).join('');
    }
    function build() {
      if (!data) return;
      const rect = $('.wg-canvas').getBoundingClientRect(); W = Math.max(320, rect.width); H = Math.max(360, Math.min(720, W * .62));
      const dpr = window.devicePixelRatio || 1; cv.width = W * dpr; cv.height = H * dpr; cv.style.height = H + 'px'; ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      const inb = {}; data.edges.forEach((e) => { if (!e.redlink) inb[e.to] = (inb[e.to] || 0) + e.weight; });
      const ghosts = new Map();
      data.edges.forEach((e) => { if (e.redlink && !ghosts.has(e.to)) ghosts.set(e.to, { slug: e.to, type: 'ghost', title: e.to.replace(/-/g, ' '), bytes: 0, ghost: true }); });
      nodes = [...data.nodes.map((n) => ({ ...n, inb: inb[n.slug] || 0 })), ...ghosts.values()];
      const val = (n) => n.ghost ? 0 : sizeBy === 'in' ? n.inb : sizeBy === 'cites' ? n.citations : n.bytes;
      const max = Math.max(1, ...nodes.map(val)), rMax = Math.min(30, W / 28), rMin = 2.5;
      nodes.forEach((n) => { n.r = n.ghost ? 2.5 : Math.max(rMin, rMax * Math.sqrt(val(n) / max)); n.val = val(n); });
      edges = data.edges; layout(nodes, edges, W, H);
      const types = [...new Set(nodes.map((n) => n.type))].sort((a, b) => TYPE_ORDER.indexOf(a) - TYPE_ORDER.indexOf(b));
      $('.wg-type').innerHTML = '<option value="">All types</option>' + types.filter((t) => t !== 'ghost').map((t) => `<option value="${t}">${TYPE_LABEL[t] || t}</option>`).join('');
      $('.wg-type').value = types.includes(typeF) ? typeF : (typeF = '');
      const unit = sizeBy === 'bytes' ? kb : (v) => Math.round(v) + (sizeBy === 'in' ? ' links' : ' cites');
      const refs = [max, max / 4, max / 16].map((v) => ({ v, r: Math.max(rMin, rMax * Math.sqrt(v / max)) }));
      $('.wg-key').innerHTML = types.map((t) => `<span><i class="${t === 'ghost' ? 'ghost' : t === 'root' ? 'root' : ''}" style="${t === 'ghost' || t === 'root' ? '' : 'background:' + (P[t] || P.other)}"></i>${TYPE_LABEL[t] || t}</span>`).join('')
        + `<span class="wg-scale">${refs.map((x) => `<svg width="${2 * x.r + 4}" height="${2 * rMax + 4}"><circle cx="${x.r + 2}" cy="${rMax + 2}" r="${x.r}" fill="none" stroke="currentColor"/></svg><em>${unit(x.v)}</em>`).join('')}</span>`;
      draw();
    }
    const nb = (s) => { const out = new Set([s]); edges.forEach((e) => { if (e.from === s) out.add(e.to); if (e.to === s) out.add(e.from); }); return out; };
    function draw() {
      if (!data) return;
      P = palette(); ctx.clearRect(0, 0, W, H);
      const focus = sel ? nb(sel.slug) : null, byS = new Map(nodes.map((n) => [n.slug, n]));
      const dim = (n) => (focus && !focus.has(n.slug)) || (typeF && n.type !== typeF) || (q && !(n.slug.includes(q) || (n.title || '').toLowerCase().includes(q)));
      for (const e of edges) {
        const a = byS.get(e.from), b = byS.get(e.to); if (!a || !b) continue;
        const on = focus ? (e.from === sel.slug || e.to === sel.slug) : !(dim(a) || dim(b));
        ctx.strokeStyle = on && focus ? P.accent : P.line; ctx.globalAlpha = focus ? (on ? .9 : .04) : (on ? .22 : .05);
        ctx.lineWidth = Math.min(3, .6 + Math.log2(1 + e.weight) * .5); ctx.setLineDash(e.redlink ? [3, 3] : []);
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }
      ctx.setLineDash([]);
      for (const n of nodes) {
        ctx.globalAlpha = dim(n) ? .12 : 1; ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        if (n.ghost) { ctx.setLineDash([2, 2]); ctx.strokeStyle = P.muted; ctx.lineWidth = 1; ctx.stroke(); ctx.setLineDash([]); continue; }
        if (n.type === 'root') { ctx.strokeStyle = P.ink; ctx.lineWidth = 1.5; ctx.stroke(); continue; }
        ctx.fillStyle = P[n.type] || P.other; ctx.fill();
        if (n.conflicts) { ctx.strokeStyle = P['failure-mode']; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 2.5, 0, Math.PI * 2); ctx.stroke(); }
        if (n === hover || n === sel) { ctx.strokeStyle = P.ink; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 1, 0, Math.PI * 2); ctx.stroke(); }
      }
      ctx.globalAlpha = 1; ctx.fillStyle = P.ink; ctx.font = '11px system-ui, sans-serif'; ctx.textAlign = 'center';
      const big = [...nodes].filter((n) => !n.ghost && !dim(n)).sort((a, b) => b.r - a.r).slice(0, focus ? 40 : 14);
      for (const n of big) if (n.r > 7 || focus) ctx.fillText(n.slug.length > 26 ? n.slug.slice(0, 25) + '…' : n.slug, n.x, n.y - n.r - 4);
    }
    const at = (ev) => { const r = cv.getBoundingClientRect(), x = ev.clientX - r.left, y = ev.clientY - r.top;
      let best = null, bd = 1e9; for (const n of nodes) { const d = Math.hypot(n.x - x, n.y - y); if (d < Math.max(n.r, 6) && d < bd) { best = n; bd = d; } } return [best, x, y]; };
    function info(n) {
      const largest = Math.max(...nodes.map((m) => m.bytes || 0)) || 1;
      const out = edges.filter((e) => e.from === n.slug).length, inn = edges.filter((e) => e.to === n.slug).length;
      return n.ghost ? `<b>${n.slug}</b><span>Linked from ${inn} page${inn === 1 ? '' : 's'}; not written yet</span>`
        : `<b>${n.title || n.slug}</b><span>${TYPE_LABEL[n.type] || n.type} · ${kb(n.bytes)} (${Math.round(100 * n.bytes / largest)}% of the largest) · ${n.citations} citations · links ${inn} in / ${out} out${n.conflicts ? ' · ' + n.conflicts + ' CONFLICT' : ''}</span>`;
    }
    function showSide(n) {
      if (!n) { side.innerHTML = '<p class="wg-hint">Hover a circle for its page; click to focus it and its neighbours. Circle area = page size.</p>'; return; }
      const linked = [...nb(n.slug)].filter((s) => s !== n.slug).slice(0, 30);
      side.innerHTML = `<div class="wg-info">${info(n)}</div>${n.description ? `<p class="wg-desc">${n.description.replace(/[<>&]/g, '')}</p>` : ''}
        <p class="wg-sub">Linked pages (${linked.length})</p><ul>${linked.map((s) => `<li><button type="button" data-s="${s}">${s}</button></li>`).join('')}</ul>`;
      side.querySelectorAll('button[data-s]').forEach((b) => b.onclick = () => { sel = nodes.find((m) => m.slug === b.dataset.s) || sel; showSide(sel); draw(); });
    }
    cv.addEventListener('mousemove', (ev) => { const [n, x, y] = at(ev); if (n !== hover) { hover = n; draw(); }
      if (n) { tip.hidden = false; tip.innerHTML = info(n); tip.style.left = Math.min(x + 12, W - 240) + 'px'; tip.style.top = (y + 12) + 'px'; } else tip.hidden = true; });
    cv.addEventListener('mouseleave', () => { hover = null; tip.hidden = true; draw(); });
    cv.addEventListener('click', (ev) => { const [n] = at(ev); sel = n && sel !== n ? n : null; showSide(sel); draw(); });
    let rt; window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => { if (el.offsetParent) build(); }, 200); });
    load(opts.sources[0]);
    return { redraw: () => { if (data) build(); } };
  }
  window.MMWikiGraph = { mount };
})();
