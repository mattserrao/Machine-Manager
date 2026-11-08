// Machine Manager — the board engine shared by the Whiteboard, Ops Task Library, Consumables Tracker and Daily.
// Notes (cards) with sub-cards, arrows and frames on a pannable board; undo, search, print, export; saved in
// this browser (demo) or synced through MMCloud.openStore (signed in). Each page calls MMBoard.start(cfg):
//
//   shell      'tabs' (Whiteboard: boards as tabs, templates) | 'library' (a library page of boards)
//   tool, title, version, idb, idPrefix, viewKey, fileExt, appTag, urlParam   — names and storage keys
//   words      { board, Board, boards, card, Card, cards, sub, subs, owner } — what the page calls things
//   text       other page wording (see T below)
//   startInLibrary  open on the library page rather than the last board
//   statusMenu show the status row in note menus · areas / areaColors / areaDefault (library)
//   noDrag     extra selector that must not start a drag (e.g. quantity buttons)
//   plugin(api) → hooks for page-specific cards and library content (see the P.* calls below)
window.MMBoard = { start(cfg){
  const VERSION = cfg.version;
  const W = Object.assign({ board:'board', Board:'Board', boards:'boards', card:'card', Card:'Card', cards:'cards', sub:'sub-card', subs:'sub-cards', owner:'Who' }, cfg.words || {});
  const T = Object.assign({ newBoard:'New board', newBoardName:'New board', libTitle:'Boards', yours:'Your boards', makeOwn:'Start blank or from a copy of any board',
    frame:'Frame', moreFrames:'more', printEmpty:'Nothing to print — this board is empty.', reportEmpty:'This board is empty.', loadWhat:'your boards',
    demo:'the demo board', fileLabel:'board' }, cfg.text || {});
  const LIB = cfg.shell !== 'tabs';
  let P = {};                       // page hooks, set from cfg.plugin(api) just before start-up
  const MAX_TUCK = 3;      // sub-cards per card, at every level (same rules as the Whiteboard)
  const MAX_DEPTH = 4;     // main note = level 1
  const DEFAULT_W = 236;
  const TOUCH = matchMedia('(hover:none) and (pointer:coarse)');   // phones and tablets: no hover, finger-sized targets
  const GRID = 24;
  const COLORS = ['#ffffff','#fff4b8','#ffd8e1','#d4ecff','#d9f3d3','#e9e0ff','#ffe2c4'];
  const FRAME_COLORS = ['#2563eb','#16a34a','#d97706','#9333ea','#dc2626','#0891b2','#64748b'];
  // Colour is kept for what needs attention: in progress uses the accent, blocked the attention colour;
  // the rest are grey (mm-theme.css). Note and frame colours chosen in older versions stay in the data
  // but show neutral, and the pickers are off (SHOW_COLORS).
  const SHOW_COLORS = false;
  const STATUSES = {
    planned:  { label:'Planned',     c:'var(--muted)' },
    progress: { label:'In progress', c:'var(--accent)' },
    done:     { label:'Done',        c:'var(--muted)' },
    blocked:  { label:'Blocked',     c:'var(--warn)' },
  };

  const $ = id => document.getElementById(id);
  const board = $('board'), world = $('world'), emptyEl = $('empty'), saveStateEl = $('saveState');
  const lg = $('lg'), tmpLink = $('tmpLink');
  $('ver').textContent = cfg.title + ' ' + VERSION;

  /* ================= State ================= */
  let app = { boards:{}, order:[], current:null, snap:false };
  let B = null;                     // current board
  const N = id => B && B.notes[id];
  const uid = MMUI.uid;

  function newBoard(name){
    const b = { id:bid(), name, meta:{}, created:new Date().toISOString(), notes:{}, links:[], frames:[], pan:{ x:0, y:0 }, zoom:1, z:1 };
    if (!LIB) b.sort = Date.now();                // tabs keep their order
    app.boards[b.id] = b; app.order.push(b.id);
    return b;
  }
  function fixBoard(b){
    b.meta = b.meta || {}; b.notes = b.notes || {}; b.links = b.links || []; b.frames = b.frames || []; b.pan = b.pan || { x:0, y:0 }; b.zoom = b.zoom || 1; b.z = b.z || 1;
    for (const n of Object.values(b.notes)){
      n.attachments = (n.attachments || []).filter(a => a && (a.blob || a.path));
      n.children = (n.children || []).filter(id => b.notes[id]);
      if (n.parent && !b.notes[n.parent]) n.parent = null;
      n.text = n.text || ''; n.color = n.color || COLORS[0];
    }
    b.links = b.links.filter(l => b.notes[l.from] && b.notes[l.to]);
  }

  /* ================= Storage (IndexedDB, this browser) ================= */
  const store = (() => {
    let dbp = null;
    function open(){
      if (dbp) return dbp;
      dbp = new Promise((res, rej) => {
        try {
          const r = indexedDB.open(cfg.idb, 1);
          r.onupgradeneeded = () => r.result.createObjectStore('kv');
          r.onsuccess = () => res(r.result);
          r.onerror = () => rej(r.error);
        } catch (e) { rej(e); }
      });
      return dbp;
    }
    async function get(k){
      const db = await open();
      return new Promise((res, rej) => { const q = db.transaction('kv').objectStore('kv').get(k); q.onsuccess = () => res(q.result); q.onerror = () => rej(q.error); });
    }
    async function set(k, v){
      const db = await open();
      return new Promise((res, rej) => {
        const tx = db.transaction('kv', 'readwrite'); tx.objectStore('kv').put(v, k);
        tx.oncomplete = () => res(); tx.onerror = () => rej(tx.error); tx.onabort = () => rej(tx.error);
      });
    }
    return { get, set };
  })();
  let saveTimer = null, storageOk = true;
  function save(quiet){
    libDirty = true;
    if (cloud.on) return cloudSave();
    clearTimeout(saveTimer);
    if (!quiet || !storageOk) saveStateEl.textContent = storageOk ? 'Saving…' : 'Not saved';
    saveTimer = setTimeout(async () => {
      saveTimer = null;
      try { await store.set('app', app); storageOk = true; saveStateEl.textContent = 'Saved'; }
      catch (e) { storageOk = false; saveStateEl.textContent = 'Not saved'; toast('Couldn’t save in this browser — export a backup from the File menu.'); }
    }, 350);
  }

  /* ================= Cloud sync (Supabase) =================
     Signed out: packages live in this browser (IndexedDB) — the demo.
     Signed in:  stored in the shared mm_records table under the page's tool, one record
     per board, card, arrow and frame, so two people editing different cards never
     collide. MMCloud.openStore sends only what changed, each with the version it was based
     on; if someone else changed that record first, their version comes back instead.
     Record ids:  p:<package>  ·  n:<package>:<card>  ·  l:<package>:<arrow>  ·  f:<package>:<frame>  ·  seeded */
  const TOOL = cfg.tool;
  const RID = MMRecords.boards;      // record ids (mm-records.js)
  const cloud = { on:false, org:null, user:null, edit:false, st:null, warned:false, viewWarned:false, pending:new Map() };
  const bid = () => (cfg.idPrefix || '') + ((window.crypto && crypto.randomUUID) ? crypto.randomUUID() : uid() + uid() + uid());
  const noteData = n => { const d = { ...n }; delete d.id; d.attachments = (n.attachments || []).map(a => ({ id:a.id, name:a.name, type:a.type, size:a.size, path:a.path || null })); return d; };
  const plain = o => { const d = { ...o }; delete d.id; return d; };
  const pkgData = b => Object.assign({ name:b.name, meta:b.meta || {}, created:b.created || null }, b.sort != null ? { sort:b.sort } : {});

  function setMode(text, title, href){
    const m = $('mode'); if (!m) return;
    m.textContent = text; m.title = title || ''; m.hidden = !text;
    if (href) m.href = href; else m.removeAttribute('href');
  }

  /* ---- per-person view settings (pan, zoom, current package, snap): this browser only ---- */
  const viewKey = () => `${cfg.viewKey}:${cloud.org.id}:${cloud.user.id}`;
  function loadView(){ try { return JSON.parse(localStorage.getItem(viewKey())) || {}; } catch (e) { return {}; } }
  function storeView(){
    const v = { current:app.current, snap:!!app.snap, tipsSeen:!!app.tipsSeen, printOpts:app.printOpts || null, boards:{} };
    for (const b of Object.values(app.boards)) v.boards[b.id] = { pan:b.pan, zoom:b.zoom, seen:!!b.seen };
    try { localStorage.setItem(viewKey(), JSON.stringify(v)); } catch (e) {}
  }
  let viewCache = {};

  // Everything the server should hold, as { recordId: data }. MMCloud diffs it against what it last confirmed.
  function records(){
    const out = {};
    for (const id of app.order){
      const b = app.boards[id]; if (!b) continue;
      out[RID.board(id)] = pkgData(b);
      for (const n of Object.values(b.notes)) out[RID.note(id, n.id)] = noteData(n);
      for (const l of b.links) out[RID.link(id, l.id)] = plain(l);
      for (const f of b.frames) out[RID.frame(id, f.id)] = plain(f);
    }
    if (app.seeded) out[RID.seeded] = { at:app.seeded };
    return out;
  }

  /* ---- attachments: files go to Storage (mm-files/<org>/<tool>/<board>/…), cards keep a path ---- */
  const uploading = new Set(), fetching = new Set();
  const bucket = () => MMCloud.client.storage.from('mm-files');
  async function uploadPending(){
    for (const id of app.order){
      const b = app.boards[id]; if (!b) continue;
      for (const n of Object.values(b.notes)) for (const a of n.attachments){
        if (a.path || !a.blob || uploading.has(a.id)) continue;
        const path = `${cloud.org.id}/${TOOL}/${b.id}/${a.id}-${(a.name || 'file').replace(/[^\w.-]+/g, '_').slice(-80)}`;
        uploading.add(a.id);
        try {
          const { error } = await bucket().upload(path, a.blob, { contentType:a.type || 'application/octet-stream', upsert:true });
          if (error) throw error;
          a.path = path;
        } catch (e) { toastSoft(`“${a.name}” didn’t upload${/size|large/i.test(e.message || '') ? ' (files are limited to 25 MB)' : ' — will retry'}.`); }
        finally { uploading.delete(a.id); }
      }
    }
  }
  function fetchBlobs(n){
    if (!cloud.on) return;
    for (const a of n.attachments){
      if (a.blob || !a.path || fetching.has(a.path)) continue;
      fetching.add(a.path);
      bucket().download(a.path).then(({ data, error }) => {
        fetching.delete(a.path);
        if (error || !data) return;
        for (const b of Object.values(app.boards)) for (const m of Object.values(b.notes)) for (const x of m.attachments)
          if (x.path === a.path && !x.blob){ x.blob = data; urlCache.delete(x.id); }
        remoteRender();
      }, () => fetching.delete(a.path));
    }
  }
  async function ensureBlobs(b){
    if (!cloud.on) return;
    const missing = [];
    for (const n of Object.values(b.notes)) for (const a of n.attachments) if (!a.blob && a.path) missing.push(a);
    await Promise.all(missing.map(async a => { const { data } = await bucket().download(a.path); if (data) a.blob = data; }));
  }

  /* ---- send changes ---- */
  let upTimer = null;
  function cloudSave(){
    storeView();
    if (!cloud.st) return;
    if (!cloud.edit){ cloud.st.save(); return; }
    saveStateEl.textContent = 'Saving…';
    clearTimeout(upTimer);
    upTimer = setTimeout(async () => { upTimer = null; await uploadPending(); cloud.st.save(); }, 300);
  }
  function cloudStatus(s, detail){
    if (s === 'rejected'){ toast('A change couldn’t be saved: ' + (detail || 'not allowed') + '.'); return; }
    if (s === 'saving') saveStateEl.textContent = 'Saving…';
    else if (s === 'saved'){
      saveStateEl.textContent = 'Saved'; cloud.warned = false;
      const c = cloud.st && cloud.st.conflicts;
      if (c) toast(c === 1 ? 'Someone else changed that at the same moment — showing their version.' : `${c} items were changed by someone else at the same moment — showing their versions.`);
    }
    else if (s === 'error'){ saveStateEl.textContent = 'Not saved'; if (!cloud.warned){ cloud.warned = true; toast('Can’t reach the server — keep this tab open, it will keep retrying.'); } }
    else if (s === 'viewonly'){ saveStateEl.textContent = 'View only'; if (!cloud.viewWarned){ cloud.viewWarned = true; toast('You have view-only access — changes you make here aren’t saved.'); } }
    else if (s === 'live') setMode('');
    else if (s === 'reconnecting') setMode('Reconnecting…', 'Live updates from others are paused. Your changes still save.');
  }

  /* ---- receive changes (on load, live, after a reconnect, or as a conflict answer) ---- */
  function applyRecord(id, data){
    const r = RID.parse(id); if (!r) return;
    if (r.kind === 'seeded'){ if (data) app.seeded = data.at || true; return; }
    const pid = r.board, iid = r.item;
    if (r.kind === 'board'){
      const b = app.boards[pid];
      if (!data){ if (b) removeBoardLocal(pid, true); return; }
      if (!b){
        const v = viewCache.boards && viewCache.boards[pid];
        app.boards[pid] = { id:pid, name:data.name || W.Board, meta:data.meta || {}, created:data.created || null, notes:{}, links:[], frames:[],
          pan:(v && v.pan) || { x:0, y:0 }, zoom:(v && v.zoom) || 1, z:1, seen:!!(v && v.seen) };
        if (data.sort != null) app.boards[pid].sort = data.sort;
        app.order.push(pid);
        const o = cloud.pending.get(pid);
        if (o){ cloud.pending.delete(pid); o.forEach(([i, d]) => applyRecord(i, d)); }
      } else { b.name = data.name || b.name; b.meta = data.meta || {}; b.created = data.created || b.created || null; if (data.sort != null) b.sort = data.sort; }
      libChanged(); if (B && B.id === pid) remoteRender();
      return;
    }
    const b = app.boards[pid];
    if (!b){
      const o = cloud.pending.get(pid) || [];
      const i = o.findIndex(x => x[0] === id); if (i >= 0) o.splice(i, 1);
      if (data) o.push([id, data]);
      cloud.pending.set(pid, o); return;
    }
    if (r.kind === 'note'){
      if (!data){
        if (!b.notes[iid]) return;
        delete b.notes[iid];
        if (b === B){ sel.delete(iid); if (editId === iid){ editId = null; modal.hidden = true; toast(`The ${W.card} you were editing was deleted by someone else.`); } }
      } else {
        const old = b.notes[iid], n = { ...data, id:iid };
        n.attachments = (n.attachments || []).map(a => { const o = old && old.attachments.find(x => x.id === a.id); return o && o.blob ? { ...a, blob:o.blob } : { ...a }; });
        n.children = n.children || []; n.text = n.text || ''; n.color = n.color || COLORS[0];
        b.notes[iid] = n; b.z = Math.max(b.z || 1, n.z || 0);
        fetchBlobs(n);
        if (b === B && editId === iid){
          if (edText.value !== n.text) edText.value = n.text;
          if (edHrs && document.activeElement !== edHrs) edHrs.value = n.hrs == null ? '' : n.hrs;
          if (edDue) edDue.value = n.due || '';
          if (document.activeElement !== edOwner) edOwner.value = n.owner || '';
          paintEditor(); toastSoft(`Someone else just changed this ${W.card}.`);
        }
      }
    } else if (r.kind === 'link' || r.kind === 'frame'){
      const arr = r.kind === 'link' ? b.links : b.frames, i = arr.findIndex(x => x.id === iid);
      if (!data){ if (i < 0) return; arr.splice(i, 1); if (r.kind === 'link' && selLink === iid){ selLink = null; hideLinkPop(); } }
      else { const o = { ...data, id:iid }; if (i >= 0) arr[i] = o; else arr.push(o); }
    } else return;
    libChanged();
    if (b === B) remoteRender();
  }
  function removeBoardLocal(id, remote){
    const b = app.boards[id]; if (!b) return;
    delete app.boards[id]; app.order = app.order.filter(x => x !== id);
    libChanged();
    if (!LIB){
      if (B && B.id === id){
        B = null;
        if (!app.order.length) newBoard(W.Board + ' 1');
        switchBoard(app.order[0]);
        if (remote) toast(`“${b.name}” was deleted by someone else.`);
      } else if (B) remoteRender();
      return;
    }
    if (B && B.id === id){
      B = null; app.current = null;
      if (editId){ editId = null; modal.hidden = true; }
      if (!pkgDlg.hidden) pkgDlg.hidden = true;
      openLibrary();
      if (remote) toast(`“${b.name}” was deleted by someone else.`);
    }
  }

  // Don't redraw under someone's mouse: cards are rebuilt on render, which would break a drag.
  let rrPending = false, pointerDown = false;
  function flushRemote(){ if (!rrPending || pointerDown || !B) return; rrPending = false; render(); }
  function remoteRender(){ rrPending = true; if (!pointerDown) requestAnimationFrame(flushRemote); }
  window.addEventListener('pointerdown', () => { pointerDown = true; }, true);
  const ptrUp = () => { pointerDown = false; if (rrPending) requestAnimationFrame(flushRemote); };
  window.addEventListener('pointerup', ptrUp, true);
  window.addEventListener('pointercancel', ptrUp, true);

  /* ---- load ---- */
  async function loadCloud(s){
    Object.assign(cloud, { on:true, org:s.org, user:s.user, edit:MMCloud.canEdit(s) });
    viewCache = loadView();
    app = { boards:{}, order:[], current:viewCache.current || null, snap:!!viewCache.snap, tipsSeen:!!viewCache.tipsSeen, printOpts:viewCache.printOpts || undefined };
    cloud.st = MMCloud.openStore(TOOL, { snapshot:records, onChange:(id, data) => applyRecord(id, data), onStatus:cloudStatus });
    const data = await cloud.st.ready;
    if (!data) throw new Error('not signed in to an organization');
    const isBoard = id => (RID.parse(id) || {}).kind === 'board';
    const ids = Object.keys(data).sort((a, b) => (isBoard(b) - isBoard(a)) || a.localeCompare(b));
    ids.forEach(id => applyRecord(id, data[id]));
    const key = b => b.sort != null ? b.sort : Date.parse(b.created) || 0;
    if (!LIB) app.order.sort((x, y) => key(app.boards[x]) - key(app.boards[y]));
    // Editors tidy up stored files nothing points to any more (at most weekly).
    if (cloud.edit) setTimeout(() => MMCloud.files(TOOL).sweep().catch(() => {}), 5000);
  }

  /* ================= Undo / redo ================= */
  const hist = {};
  const H = () => B ? (hist[B.id] || (hist[B.id] = { u:[], r:[] })) : { u:[], r:[] };
  let seq = 0;
  const deletedBoards = [];       // for undoing a board delete
  const snap = () => structuredClone({ notes:B.notes, links:B.links, frames:B.frames, z:B.z, name:B.name });
  function checkpoint(){ const h = H(); h.u.push(snap()); if (h.u.length > 100) h.u.shift(); h.r.length = 0; h.seq = ++seq; updateUndo(); }
  function restore(s){ B.notes = s.notes; B.links = s.links; B.frames = s.frames || []; B.z = s.z; if (s.name) B.name = s.name; }
  function undo(){
    const db = deletedBoards[deletedBoards.length - 1];
    if (db && db.seq > (H().seq || 0)) return restoreBoard();
    const h = H(); if (!h.u.length) return; h.r.push(snap()); restore(h.u.pop()); sel.clear(); selLink = null; render(); save();
  }
  function restoreBoard(){
    const d = deletedBoards.pop(); if (!d) return;
    app.boards[d.board.id] = d.board; app.order.splice(Math.min(d.index, app.order.length), 0, d.board.id);
    libChanged(); save(); showBoard(d.board.id); toast(`Restored “${d.board.name}”`);
  }
  function redo(){ const h = H(); if (!h.r.length) return; h.u.push(snap()); restore(h.r.pop()); sel.clear(); selLink = null; render(); save(); }
  function updateUndo(){ $('undoBtn').disabled = !H().u.length && !deletedBoards.length; $('redoBtn').disabled = !H().r.length; }

  /* ================= Helpers ================= */
  const { el, esc } = MMUI;                     // mm-ui.js
  // line icons (mm-icons.js); a chip is an icon plus text
  const I = (name, cls) => window.MMIcons ? MMIcons.el(name, cls || 'xs') : document.createTextNode('');
  const chipI = (cls, ic, txt) => { const c = el('span', cls); c.append(I(ic), document.createTextNode(txt)); return c; };
  const urlCache = new Map();
  function urlFor(att){
    if (!urlCache.has(att.id)) { try { urlCache.set(att.id, URL.createObjectURL(att.blob)); } catch(e){ return ''; } }
    return urlCache.get(att.id);
  }
  const isImg = a => /^image\//.test(a.type || '');
  const ext = name => { const m = /\.([a-z0-9]{1,5})$/i.exec(name || ''); return m ? m[1] : 'file'; };
  const fmtSize = b => b < 1024 ? b + ' B' : b < 1048576 ? (b/1024).toFixed(0) + ' KB' : (b/1048576).toFixed(1) + ' MB';
  const heightOf = n => 1 + Math.max(0, ...n.children.map(id => N(id) ? heightOf(N(id)) : 0));
  const levelOf = n => { let l = 1; while (n.parent && N(n.parent)){ n = N(n.parent); l++; } return l; };
  const rootOf = n => { while (n.parent && N(n.parent)) n = N(n.parent); return n; };
  const tops = () => Object.values(B.notes).filter(n => !n.parent);
  const { toast, toastSoft } = MMUI;            // mm-ui.js
  function toWorld(cx, cy){ const r = board.getBoundingClientRect(); return { x:(cx - r.left - B.pan.x) / B.zoom, y:(cy - r.top - B.pan.y) / B.zoom }; }
  function worldRect(e){
    const r = e.getBoundingClientRect(), br = board.getBoundingClientRect();
    return { x:(r.left - br.left - B.pan.x) / B.zoom, y:(r.top - br.top - B.pan.y) / B.zoom, w:r.width / B.zoom, h:r.height / B.zoom };
  }
  const noteEl = id => world.querySelector(`.note[data-id="${id}"]`);
  const miniEl = id => world.querySelector(`.mini[data-id="${id}"]`);
  const snapV = v => app.snap ? Math.round(v / GRID) * GRID : Math.round(v);
  const typing = () => { const a = document.activeElement; return a && (/^(INPUT|TEXTAREA|SELECT)$/.test(a.tagName) || a.isContentEditable); };

  /* ---------- text model: first line = title, then bullets / checkboxes / paragraphs ---------- */
  function parseText(t){
    const lines = (t || '').split('\n');
    let ti = lines.findIndex(l => l.trim() !== '');
    if (ti < 0) return { title:'', titleIdx:-1, rest:[], lines };
    const rest = [];
    for (let i = ti + 1; i < lines.length; i++) rest.push({ i, s:lines[i] });
    while (rest.length && rest[rest.length - 1].s.trim() === '') rest.pop();
    return { title:lines[ti].trim(), titleIdx:ti, rest, lines };
  }
  function inline(s){
    let h = esc(s);
    const links = [];
    h = h.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (m, t, u) => { links.push(`<a href="${u}" target="_blank" rel="noopener">${t}</a>`); return `\u0000${links.length - 1}\u0000`; });
    h = h.replace(/(^|[\s(])(https?:\/\/[^\s<]+[^\s<.,;:!?)])/g, (m, p, u) => { links.push(`<a href="${u}" target="_blank" rel="noopener">${u}</a>`); return `${p}\u0000${links.length - 1}\u0000`; });
    h = h.replace(/\*\*([^*]+?)\*\*/g, '<b>$1</b>');
    h = h.replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?![*\w])/g, '$1<i>$2</i>');
    h = h.replace(/\u0000(\d+)\u0000/g, (m, i) => links[+i]);
    return h;
  }
  const lineIndent = s => Math.min(3, Math.floor(s.replace(/\t/g, '  ').length / 2));
  function checklist(t){
    let done = 0, total = 0;
    for (const l of (t || '').split('\n')){ const m = /^\s*[-*] \[( |x|X)\] /.exec(l); if (m){ total++; if (m[1] !== ' ') done++; } }
    return { done, total };
  }
  function buildText(n){
    const { rest } = parseText(n.text);
    const wrap = el('div', 'text');
    for (const { i, s } of rest){
      let m;
      if ((m = /^(\s*)[-*] \[( |x|X)\] ?(.*)$/.exec(s))){
        const on = m[2] !== ' ';
        const row = el('div', 'ln ck' + (on ? ' on' : ''));
        row.style.paddingLeft = (lineIndent(m[1]) * 16) + 'px';
        const cb = el('span', 'cb' + (on ? ' on' : '')); if (on) cb.appendChild(I('check', 'xs'));
        cb.dataset.line = i; cb.dataset.id = n.id;
        const tx = el('span'); tx.innerHTML = inline(m[3]);
        row.append(cb, tx); wrap.appendChild(row);
      } else if ((m = /^(\s*)[-*] (.*)$/.exec(s))){
        const lvl = lineIndent(m[1]);
        const row = el('div', 'ln bl l' + (lvl % 3));
        row.style.paddingLeft = (lvl * 16) + 'px';
        const tx = el('span'); tx.innerHTML = inline(m[2]);
        row.appendChild(tx); wrap.appendChild(row);
      } else if (s.trim() === ''){
        wrap.appendChild(el('div', 'gap'));
      } else {
        const row = el('div', 'ln'); row.innerHTML = inline(s); wrap.appendChild(row);
      }
    }
    return wrap;
  }
  function toggleCheck(id, line){
    const n = N(id); if (!n) return;
    checkpoint();
    const lines = n.text.split('\n');
    lines[line] = lines[line].replace(/\[( |x|X)\]/, m => m === '[ ]' ? '[x]' : '[ ]');
    n.text = lines.join('\n');
    render(); save();
  }
  function fmtDue(d){
    if (!d) return '';
    const dt = new Date(d + 'T00:00:00');
    if (isNaN(dt)) return d;
    return dt.toLocaleDateString(undefined, { month:'short', day:'numeric' });
  }
  function isLate(n){
    if (!n.due || n.status === 'done') return false;
    const t = new Date(); t.setHours(0,0,0,0);
    return new Date(n.due + 'T00:00:00') < t;
  }

  /* ================= Rendering ================= */
  const sel = new Set();     // selected top-level note ids
  let selLink = null;

  function applyView(){
    world.style.transform = `translate(${B.pan.x}px,${B.pan.y}px) scale(${B.zoom})`;
    board.style.backgroundSize = `${24 * B.zoom}px ${24 * B.zoom}px`;
    board.style.backgroundPosition = `${B.pan.x}px ${B.pan.y}px`;
    $('zoomPct').textContent = Math.round(B.zoom * 100) + '%';
  }

  function render(){
    applyView();
    world.querySelectorAll(':scope > .note, :scope > .link-label, :scope > .frame').forEach(e => e.remove());
    const svgEl = $('links');
    for (const f of B.frames) world.insertBefore(buildFrame(f), svgEl);
    const list = tops().sort((a, b) => a.z - b.z);
    for (const n of list) world.appendChild(buildNote(n));
    emptyEl.hidden = list.length > 0;
    for (const id of [...sel]) if (!N(id) || N(id).parent) sel.delete(id);
    applySearch();
    drawLinks();
    renderChrome();
    updateUndo();
    $('snapBtn').classList.toggle('on', !!app.snap);
  }

  function statusPill(s){
    const st = STATUSES[s]; if (!st) return null;
    const p = el('span', 'pill', st.label); p.style.setProperty('--sc', st.c); return p;
  }

  function buildNote(n){
    const e = el('div', 'note');
    if (sel.has(n.id)) e.classList.add('selected');
    if (n.status === 'done') e.classList.add('is-done');
    e.dataset.id = n.id;
    e.style.left = n.x + 'px'; e.style.top = n.y + 'px'; e.style.zIndex = n.z;
    e.style.width = (n.w || DEFAULT_W) + 'px';
    e.style.setProperty('--c', n.color);

    const body = el('div', 'note-body');
    if (n.h){ e.classList.add('sized'); body.style.height = n.h + 'px'; }

    const meta = el('div', 'meta');
    if (P.noteMeta) P.noteMeta(n, meta);
    const pill = statusPill(n.status); if (pill) meta.appendChild(pill);
    if (n.due) meta.appendChild(chipI('chip due' + (isLate(n) ? ' late' : ''), 'calendar', fmtDue(n.due)));
    if (fmtHrs(n.hrs)) meta.appendChild(chipI('chip', 'clock', fmtHrs(n.hrs)));
    if (n.owner) meta.appendChild(chipI('chip', 'user', n.owner));
    const ck = checklist(n.text); if (ck.total) meta.appendChild(chipI('chip', 'checks', `${ck.done}/${ck.total}`));
    body.appendChild(meta);

    const { title } = parseText(n.text);
    const t = el('div', 'title' + (title ? '' : ' placeholder'));
    if (title) t.innerHTML = inline(title); else t.textContent = (P.emptyTitle && P.emptyTitle(n)) || 'Empty note — click to edit';
    body.appendChild(t);
    if (P.noteBody){ const x = P.noteBody(n); if (x) body.appendChild(x); }
    body.appendChild(buildText(n));
    if (n.attachments.length) body.appendChild(buildAttRow(n.attachments));
    const rz = el('div', 'rz'); rz.title = 'Drag to resize';
    rz.addEventListener('pointerdown', ev => startResize(ev, n.id));
    const lh = el('div', 'lh'); lh.title = 'Drag to connect to another note';
    lh.addEventListener('pointerdown', ev => { ev.stopPropagation(); ev.preventDefault(); beginLink(n.id, ev, false); });
    body.append(rz, lh);
    e.appendChild(body);

    if (n.children.length) e.appendChild(buildTucked(n, 2));
    e.addEventListener('pointerdown', ev => startPointer(ev, n.id, false));
    return e;
  }

  function buildAttRow(atts){
    const row = el('div', 'atts');
    const imgs = atts.filter(isImg), files = atts.filter(a => !isImg(a));
    imgs.slice(0, 4).forEach(a => { const i = el('img'); i.src = urlFor(a); i.alt = a.name; row.appendChild(i); });
    files.slice(0, 2).forEach(a => row.appendChild(chipI('chip', 'paperclip', a.name)));
    const more = Math.max(0, imgs.length - 4) + Math.max(0, files.length - 2);
    if (more) row.appendChild(el('span', 'chip', '+' + more));
    return row;
  }

  function doneCount(n){ return n.children.filter(c => N(c) && N(c).status === 'done').length; }

  function buildTucked(n, level){
    const t = el('div', 'tucked' + (level > 2 ? ' sub' : '') + (n.collapsed ? ' is-collapsed' : ''));
    t.dataset.parent = n.id;
    if (level === 2){
      const bar = el('div', 'tbar');
      bar.appendChild(chipI('', n.collapsed ? 'right' : 'down', `${n.children.length} ${n.children.length > 1 ? W.subs : W.sub}`));
      const d = doneCount(n);
      if (d) bar.appendChild(chipI('dn', 'check', `${d}/${n.children.length} done`));
      bar.title = n.collapsed ? 'Expand' : 'Collapse';
      bar.addEventListener('pointerdown', ev => ev.stopPropagation());
      bar.addEventListener('click', () => toggleCollapse(n.id));
      t.appendChild(bar);
    }
    for (const cid of n.children){ const c = N(cid); if (c) t.appendChild(buildMini(c, level)); }
    return t;
  }

  function buildMini(c, level){
    const m = el('div', 'mini' + (c.status === 'done' ? ' is-done' : ''));
    m.dataset.id = c.id; m.dataset.level = level;
    m.style.setProperty('--c', c.color);
    const row = el('div', 'row');
    if (STATUSES[c.status]){ const d = el('span', 'dot'); d.style.setProperty('--sc', STATUSES[c.status].c); d.title = STATUSES[c.status].label; row.appendChild(d); }
    const { title } = parseText(c.text);
    const mt = el('span', 'mt' + (title ? '' : ' placeholder'));
    if (title) mt.innerHTML = inline(title); else mt.textContent = 'Empty note';
    row.appendChild(mt);
    if (c.due) row.appendChild(el('span', 'ma', fmtDue(c.due)));
    if (fmtHrs(c.hrs)) row.appendChild(el('span', 'ma', fmtHrs(c.hrs)));
    if (P.miniMeta) P.miniMeta(c, row);
    const ck = checklist(c.text); if (ck.total) row.appendChild(chipI('ma', 'checks', `${ck.done}/${ck.total}`));
    if (c.attachments.length) row.appendChild(chipI('ma', 'paperclip', String(c.attachments.length)));
    if (c.children.length){
      const d = doneCount(c);
      const cr = el('button', 'caret'); cr.append(I(c.collapsed ? 'right' : 'down'), document.createTextNode(c.children.length + (d ? ` · ${d} done` : '')));
      cr.title = c.collapsed ? 'Expand' : 'Collapse';
      cr.addEventListener('pointerdown', ev => ev.stopPropagation());
      cr.addEventListener('click', ev => { ev.stopPropagation(); toggleCollapse(c.id); });
      row.appendChild(cr);
    }
    m.appendChild(row);
    if (c.children.length) m.appendChild(buildTucked(c, level + 1));
    m.addEventListener('pointerdown', ev => { ev.stopPropagation(); startPointer(ev, c.id, true); });
    return m;
  }

  // checkbox clicks (delegated)
  const NODRAG = '.cb, a' + (cfg.noDrag ? ', ' + cfg.noDrag : '');
  world.addEventListener('pointerdown', e => { if (e.target.closest(NODRAG)) e.stopPropagation(); }, true);
  if (cfg.noDrag) world.addEventListener('dblclick', e => { if (e.target.closest(cfg.noDrag)) e.stopPropagation(); }, true);
  world.addEventListener('click', e => {
    if (P.worldClick && P.worldClick(e)){ e.stopPropagation(); return; }
    const cb = e.target.closest('.cb');
    if (cb){ e.stopPropagation(); toggleCheck(cb.dataset.id, +cb.dataset.line); }
  });

  function toggleCollapse(id){ const n = N(id); if (!n) return; checkpoint(); n.collapsed = !n.collapsed; render(); save(); }

  /* ================= Links (arrows) ================= */
  function visibleElFor(id){
    let n = N(id);
    while (n){
      const e = noteEl(n.id) || miniEl(n.id);
      if (e && e.offsetParent !== null) return e;
      n = n.parent ? N(n.parent) : null;
    }
    return null;
  }
  function edgePoint(r, tx, ty){
    const cx = r.x + r.w/2, cy = r.y + r.h/2, dx = tx - cx, dy = ty - cy;
    if (!dx && !dy) return { x:cx, y:cy };
    const s = 1 / Math.max(Math.abs(dx) / (r.w/2 + 5), Math.abs(dy) / (r.h/2 + 5));
    return { x:cx + dx*s, y:cy + dy*s };
  }
  const SVGNS = 'http://www.w3.org/2000/svg';
  function drawLinks(){
    lg.textContent = '';
    world.querySelectorAll(':scope > .link-label').forEach(e => e.remove());
    for (const l of B.links){
      if (!N(l.from) || !N(l.to)) continue;
      const ea = visibleElFor(l.from), eb = visibleElFor(l.to);
      if (!ea || !eb || ea === eb || ea.contains(eb) || eb.contains(ea)) continue;
      const ra = worldRect(ea), rb = worldRect(eb);
      const ca = { x:ra.x + ra.w/2, y:ra.y + ra.h/2 }, cb = { x:rb.x + rb.w/2, y:rb.y + rb.h/2 };
      const p1 = edgePoint(ra, cb.x, cb.y), p2 = edgePoint(rb, ca.x, ca.y);
      const d = `M${p1.x},${p1.y} L${p2.x},${p2.y}`;
      const on = selLink === l.id;
      const hiddenEnd = ea.dataset.id !== l.from || eb.dataset.id !== l.to;
      const path = document.createElementNS(SVGNS, 'path');
      path.setAttribute('d', d); path.setAttribute('class', 'lk' + (on ? ' sel' : '') + (hiddenEnd ? ' hidden' : ''));
      path.dataset.from = rootOf(N(l.from)).id; path.dataset.to = rootOf(N(l.to)).id;
      if (hiddenEnd){ const tt = document.createElementNS(SVGNS, 'title'); tt.textContent = 'Points into a collapsed stack'; path.appendChild(tt); }
      path.setAttribute('marker-end', on ? 'url(#arrowSel)' : 'url(#arrow)');
      const hit = document.createElementNS(SVGNS, 'path');
      hit.setAttribute('d', d); hit.setAttribute('class', 'lk-hit');
      hit.addEventListener('pointerdown', ev => { ev.stopPropagation(); ev.preventDefault(); selectLink(l.id, ev.clientX, ev.clientY); });
      hit.addEventListener('contextmenu', ev => { ev.preventDefault(); ev.stopPropagation(); selectLink(l.id, ev.clientX, ev.clientY); });
      lg.append(path, hit);
      if (l.label){
        const lb = el('div', 'link-label' + (on ? ' sel' : ''), l.label);
        lb.dataset.from = rootOf(N(l.from)).id; lb.dataset.to = rootOf(N(l.to)).id;
        lb.style.left = (p1.x + p2.x)/2 + 'px'; lb.style.top = (p1.y + p2.y)/2 + 'px';
        lb.addEventListener('pointerdown', ev => { ev.stopPropagation(); ev.preventDefault(); selectLink(l.id, ev.clientX, ev.clientY); });
        world.appendChild(lb);
      }
    }
  }
  let linksRaf = 0;
  const scheduleLinks = () => { if (!linksRaf) linksRaf = requestAnimationFrame(() => { linksRaf = 0; drawLinks(); }); };
  world.addEventListener('transitionend', scheduleLinks);

  const linkPop = $('linkPop'), linkLabel = $('linkLabel');
  let linkEditedOnce = false;
  function selectLink(id, cx, cy){
    closeMenu();
    clearSel();
    selLink = id; linkEditedOnce = false;
    drawLinks();
    const l = B.links.find(x => x.id === id);
    linkLabel.value = l ? (l.label || '') : '';
    linkPop.hidden = false;
    const w = linkPop.offsetWidth, h = linkPop.offsetHeight;
    linkPop.style.left = Math.max(8, Math.min(innerWidth - w - 8, cx - w/2)) + 'px';
    linkPop.style.top = Math.max(8, Math.min(innerHeight - h - 8, cy + 14)) + 'px';
    setTimeout(() => linkLabel.focus(), 0);
  }
  function hideLinkPop(){ if (!linkPop.hidden){ linkPop.hidden = true; } if (selLink){ selLink = null; drawLinks(); } }
  linkLabel.addEventListener('input', () => {
    const l = B.links.find(x => x.id === selLink); if (!l) return;
    if (!linkEditedOnce){ checkpoint(); linkEditedOnce = true; }
    l.label = linkLabel.value; drawLinks(); save();
  });
  linkLabel.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === 'Escape'){ e.preventDefault(); linkLabel.blur(); hideLinkPop(); } });
  $('linkRev').addEventListener('click', () => { const l = B.links.find(x => x.id === selLink); if (!l) return; checkpoint(); [l.from, l.to] = [l.to, l.from]; drawLinks(); save(); });
  $('linkDel').addEventListener('click', () => deleteLink(selLink));
  function deleteLink(id){
    if (!id) return; checkpoint();
    B.links = B.links.filter(l => l.id !== id);
    linkPop.hidden = true; selLink = null; drawLinks(); save();
  }

  // creating links: drag from the blue dot, or "Connect from here" then click a note
  let linkMode = null;
  function beginLink(fromId, e, sticky){
    closeMenu(); hideLinkPop();
    linkMode = { from:fromId, sticky, target:null, armed: !sticky };
    document.body.classList.add('linking');
    if (e) moveLink(e);
    if (sticky) toast('Click a note to connect to — Esc to cancel');
  }
  function linkTargetAt(e){
    const hit = document.elementFromPoint(e.clientX, e.clientY);
    const t = hit && hit.closest('#world .mini, #world > .note');
    if (!t || t.dataset.id === linkMode.from) return null;
    return t;
  }
  function moveLink(e){
    const src = visibleElFor(linkMode.from); if (!src) return;
    const p = toWorld(e.clientX, e.clientY);
    const t = linkTargetAt(e);
    if (linkMode.target && linkMode.target !== t) linkMode.target.classList.remove('link-target');
    linkMode.target = t; if (t) t.classList.add('link-target');
    let end = p;
    const ra = worldRect(src);
    if (t){ const rb = worldRect(t); end = edgePoint(rb, ra.x + ra.w/2, ra.y + ra.h/2); }
    const s = edgePoint(ra, end.x, end.y);
    tmpLink.setAttribute('d', `M${s.x},${s.y} L${end.x},${end.y}`);
  }
  function finishLink(e){
    const t = linkTargetAt(e);
    const from = linkMode.from;
    cancelLink();
    if (!t) return;
    const to = t.dataset.id;
    if (B.links.some(l => (l.from === from && l.to === to))) { toast('Those notes are already connected.'); return; }
    checkpoint();
    B.links.push({ id:uid(), from, to, label:'' });
    drawLinks(); save();
  }
  function cancelLink(){
    if (!linkMode) return;
    if (linkMode.target) linkMode.target.classList.remove('link-target');
    linkMode = null; tmpLink.setAttribute('d', '');
    document.body.classList.remove('linking');
  }
  window.addEventListener('pointerdown', e => {
    if (linkMode && linkMode.sticky){ e.preventDefault(); e.stopPropagation(); finishLink(e); }
  }, true);

  /* ================= Selection ================= */
  function syncSelClasses(){ world.querySelectorAll(':scope > .note').forEach(e => e.classList.toggle('selected', sel.has(e.dataset.id))); }
  function clearSel(){ if (sel.size){ sel.clear(); syncSelClasses(); } }
  function selectOnly(id){ sel.clear(); sel.add(id); syncSelClasses(); }
  function toggleSel(id){ sel.has(id) ? sel.delete(id) : sel.add(id); syncSelClasses(); }

  /* ================= Create / delete / move ================= */
  function createNote(x, y, extra){
    checkpoint();
    const n = Object.assign({ id:uid(), x:snapV(x), y:snapV(y), z:++B.z, color:COLORS[0], text:'', attachments:[], children:[], parent:null }, extra || {});
    B.notes[n.id] = n;
    selectOnly(n.id);
    render(); save();
    return n;
  }
  function viewCenter(){ const r = board.getBoundingClientRect(), a = openArea(); return toWorld(r.left + r.width/2, r.top + (a.top + a.bot)/2); }
  function newNoteInView(){
    const r = $('newBtn').getBoundingClientRect();
    const c = viewCenter(), j = () => (Math.random() - .5) * 60;
    if (P.newInView && P.newInView(r, c, j)) return;
    const n = createNote(c.x - DEFAULT_W/2 + j(), c.y - 70 + j());
    openEditor(n.id, true);
  }
  function removeNote(id){
    const n = N(id); if (!n) return;
    const root = rootOf(n);
    if (n.parent){ const p = N(n.parent); if (p) p.children = p.children.filter(c => c !== id); }
    n.children.forEach((cid, i) => {
      const c = N(cid); if (!c) return;
      c.parent = null; c.x = root.x + 20 + i * 28; c.y = root.y + 40 + i * 28; c.z = ++B.z;
    });
    B.links = B.links.filter(l => l.from !== id && l.to !== id);
    delete B.notes[id];
    sel.delete(id);
  }
  function deleteNotes(ids){
    if (!ids.length) return;
    checkpoint();
    ids.forEach(removeNote);
    render(); save();
  }
  function detach(id){
    const n = N(id); if (!n || !n.parent) return;
    checkpoint();
    const root = rootOf(n), p = N(n.parent), idx = p.children.indexOf(id);
    p.children.splice(idx, 1);
    n.parent = null; n.x = root.x + (root.w || DEFAULT_W) + 24; n.y = root.y + idx * 30; n.z = ++B.z;
    render(); save();
  }
  function zFront(ids){ checkpoint(); ids.forEach(id => { N(id).z = ++B.z; }); render(); save(); }
  function zBack(ids){ checkpoint(); let m = Math.min(...tops().map(n => n.z)); ids.forEach(id => { N(id).z = --m; }); render(); save(); }

  /* ---------- copy / paste / duplicate ---------- */
  let clip = null;
  function packNotes(ids){
    const all = [];
    const walk = id => { const n = N(id); if (!n) return; all.push(n); n.children.forEach(walk); };
    ids.forEach(walk);
    const set = new Set(all.map(n => n.id));
    const pack = structuredClone({
      notes:all,
      roots:ids,
      links:B.links.filter(l => set.has(l.from) && set.has(l.to)),
    });
    // nested notes being copied as roots: give them a real position next to their stack
    pack.notes.forEach(o => {
      if (ids.includes(o.id) && o.parent){
        const r = rootOf(N(o.id));
        o.x = r.x + (r.w || DEFAULT_W) + 24; o.y = r.y;
      }
    });
    pack.text = all.map(n => n.text).filter(Boolean).join('\n\n') || '(whiteboard notes)';
    return pack;
  }
  function unpack(pack, at, offset){
    checkpoint();
    const map = {};
    pack.notes.forEach(o => { map[o.id] = uid(); });
    const roots = pack.notes.filter(o => pack.roots.includes(o.id));
    const minX = Math.min(...roots.map(o => o.x)), minY = Math.min(...roots.map(o => o.y));
    sel.clear();
    pack.notes.forEach(o => {
      const n = structuredClone(o);
      n.id = map[o.id];
      n.children = o.children.map(c => map[c]).filter(Boolean);
      const isRoot = pack.roots.includes(o.id);
      n.parent = isRoot ? null : map[o.parent];
      if (isRoot){
        n.x = snapV(at ? at.x + (o.x - minX) : o.x + offset);
        n.y = snapV(at ? at.y + (o.y - minY) : o.y + offset);
        n.z = ++B.z;
        sel.add(n.id);
      }
      n.attachments = o.attachments.map(a => ({ ...a, id:uid() }));
      B.notes[n.id] = n;
    });
    pack.links.forEach(l => B.links.push({ id:uid(), from:map[l.from], to:map[l.to], label:l.label }));
    render(); save();
  }
  function copySel(){
    if (!sel.size) return false;
    clip = packNotes([...sel]); clip.n = 0;
    try { navigator.clipboard && navigator.clipboard.writeText(clip.text).catch(() => {}); } catch(e){}
    toast(`Copied ${sel.size} note${sel.size > 1 ? 's' : ''}`);
    return true;
  }
  function pasteClip(){
    if (!clip) return;
    clip.n++;
    unpack(clip, null, 24 * clip.n);
  }
  function duplicate(ids){ if (!ids.length) return; unpack(packNotes(ids), null, 24); }

  /* ---------- align / tidy ---------- */
  function rectsOf(ids){ return ids.map(id => ({ id, n:N(id), r:worldRect(noteEl(id)) })); }
  function align(kind, ids){
    if (ids.length < 2) return;
    checkpoint();
    const rs = rectsOf(ids);
    if (kind === 'left'){ const m = Math.min(...rs.map(o => o.n.x)); rs.forEach(o => o.n.x = m); }
    if (kind === 'top'){ const m = Math.min(...rs.map(o => o.n.y)); rs.forEach(o => o.n.y = m); }
    if (kind === 'h'){
      rs.sort((a, b) => a.n.x - b.n.x);
      const start = rs[0].n.x, end = Math.max(...rs.map(o => o.n.x + o.r.w));
      const gap = Math.max(16, (end - start - rs.reduce((s, o) => s + o.r.w, 0)) / (rs.length - 1));
      let x = start; rs.forEach(o => { o.n.x = Math.round(x); x += o.r.w + gap; });
    }
    if (kind === 'v'){
      rs.sort((a, b) => a.n.y - b.n.y);
      const start = rs[0].n.y, end = Math.max(...rs.map(o => o.n.y + o.r.h));
      const gap = Math.max(16, (end - start - rs.reduce((s, o) => s + o.r.h, 0)) / (rs.length - 1));
      let y = start; rs.forEach(o => { o.n.y = Math.round(y); y += o.r.h + gap; });
    }
    if (kind === 'tidy'){
      rs.sort((a, b) => (a.n.y - b.n.y) || (a.n.x - b.n.x));
      const cols = Math.ceil(Math.sqrt(rs.length));
      const x0 = Math.min(...rs.map(o => o.n.x)), y0 = Math.min(...rs.map(o => o.n.y));
      const colW = Math.max(...rs.map(o => o.r.w)) + GRID;
      let y = y0;
      for (let i = 0; i < rs.length; i += cols){
        const row = rs.slice(i, i + cols);
        row.forEach((o, j) => { o.n.x = snapV(x0 + j * colW); o.n.y = snapV(y); });
        y += Math.max(...row.map(o => o.r.h)) + GRID;
      }
    }
    render(); save();
  }

  /* ================= Drop targeting (nesting) ================= */
  function dropBlock(dragId, parentId){
    const d = N(dragId), P = N(parentId);
    for (let x = P; x; x = x.parent ? N(x.parent) : null) if (x.id === dragId) return 'Can’t drop into itself';
    if (P.children.filter(c => c !== dragId).length >= MAX_TUCK) return `Full — ${MAX_TUCK} max`;
    if (levelOf(P) + heightOf(d) > MAX_DEPTH) return `Too deep — ${MAX_DEPTH} levels max`;
    return null;
  }
  function applyDrop(dragId, tgt, fromRect){
    const d = N(dragId), P = N(tgt.parent);
    let idx = tgt.kind === 'into' ? P.children.length : tgt.index;
    if (d.parent){
      const op = N(d.parent), oi = op.children.indexOf(d.id);
      op.children.splice(oi, 1);
      if (op.id === P.id && oi < idx) idx--;
    }
    idx = Math.max(0, Math.min(idx, P.children.length));
    P.children.splice(idx, 0, d.id);
    d.parent = P.id;
    for (let x = P; x; x = x.parent ? N(x.parent) : null) x.collapsed = false;   // reveal where it landed
    rootOf(P).z = ++B.z;
    sel.delete(d.id);
    render(); save();
    const m = miniEl(d.id);
    if (m && m.animate && fromRect){
      const r = m.getBoundingClientRect();
      m.animate([
        { transform:`translate(${fromRect.left - r.left}px,${fromRect.top - r.top}px) scale(1.1)`, opacity:.5 },
        { transform:'translate(0,0) scale(1.05)', opacity:1, offset:.7 },
        { transform:'none', opacity:1 }
      ], { duration:340, easing:'cubic-bezier(.2,.8,.3,1.15)' }).onfinish = scheduleLinks;
    }
    const te = noteEl(rootOf(P).id);
    if (te && te.animate) te.animate([{ transform:'scale(1)' }, { transform:'scale(1.02)' }, { transform:'scale(1)' }], { duration:240, delay:200, easing:'ease-out' });
  }
  function pointTarget(e, rootEl){
    const hit = document.elementFromPoint(e.clientX, e.clientY);
    if (!hit || !rootEl.contains(hit)) return null;
    const mini = hit.closest('.mini');
    if (mini && rootEl.contains(mini)){
      const id = mini.dataset.id, n = N(id);
      const row = mini.querySelector(':scope > .row');
      const rowR = row.getBoundingClientRect();
      const i = N(n.parent).children.indexOf(id);
      const y = e.clientY, edge = Math.max(6, rowR.height * 0.3);
      if (row.contains(hit) || hit === mini){
        if (y < rowR.top + edge) return { kind:'line', parent:n.parent, index:i };
        if (!n.children.length && y > rowR.bottom - edge) return { kind:'line', parent:n.parent, index:i + 1 };
      }
      return { kind:'into', parent:id, el:mini };
    }
    return { kind:'into', parent:rootEl.dataset.id, el:rootEl };
  }
  let curKey = '';
  function clearIndicators(){
    world.querySelectorAll('.join-ok,.join-full,.drop-into,.drop-bad,.ins-before,.ins-after,.ins-bad')
      .forEach(x => x.classList.remove('join-ok','join-full','drop-into','drop-bad','ins-before','ins-after','ins-bad'));
    curKey = '';
  }
  function setTarget(tgt){
    const key = tgt ? `${tgt.kind}|${tgt.parent}|${tgt.index}` : '';
    if (key === curKey) return;
    clearIndicators();
    curKey = key;
    ptr.tgt = tgt;
    if (!tgt) return;
    const why = dropBlock(ptr.id, tgt.parent);
    tgt.ok = !why; tgt.why = why;
    if (tgt.kind === 'into'){
      const elx = tgt.el;
      if (why) elx.dataset.why = why;
      if (elx.classList.contains('note')) elx.classList.add(why ? 'join-full' : 'join-ok');
      else elx.classList.add(why ? 'drop-bad' : 'drop-into');
    } else {
      const pEl = noteEl(tgt.parent) || miniEl(tgt.parent);
      const cont = pEl && pEl.querySelector(':scope > .tucked');
      if (!cont) return;
      const kids = [...cont.querySelectorAll(':scope > .mini')];
      const k = kids[tgt.index] || kids[kids.length - 1];
      if (!k) return;
      k.classList.add(kids[tgt.index] ? 'ins-before' : 'ins-after');
      if (why){ k.classList.add('ins-bad'); toastSoft(why); }
    }
  }
  function expand(rootEl){
    if (ptr.exp === rootEl) return;
    collapseExp();
    ptr.exp = rootEl;
    rootEl.classList.add('expanded');
    if (ptr.el && ptr.mode === 'note'){
      ptr.el.style.transformOrigin = `${ptr.offX}px ${ptr.offY}px`;
      ptr.el.classList.add('shrunk');
    }
  }
  function collapseExp(){
    if (!ptr || !ptr.exp) return;
    ptr.exp.classList.remove('expanded');
    ptr.exp = null;
    if (ptr.el) ptr.el.classList.remove('shrunk');
    clearIndicators(); ptr.tgt = null;
  }
  function near(elx, e, m){
    const r = elx.getBoundingClientRect();
    return e.clientX > r.left - m && e.clientX < r.right + m && e.clientY > r.top - m && e.clientY < r.bottom + m + 30;
  }

  /* ================= Pointer: notes ================= */
  // ptr.mode: null (pending click), 'note', 'group', 'mini'
  let ptr = null, panPtr = null, rsz = null, marq = null, pinch = null;
  let lastClick = null;
  const touches = new Map();

  function startPointer(e, id, isChild){
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    if (pinch || linkMode) return;
    if (e.target.closest('a, textarea, input, .cb')) return;
    e.preventDefault(); e.stopPropagation();
    closeMenu(); if (!linkPop.hidden) hideLinkPop();
    ptr = { id, isChild, sx:e.clientX, sy:e.clientY, mode:null, el:null, offX:0, offY:0, tgt:null, exp:null, hoverId:null, hoverT:0, shift:e.shiftKey, type:e.pointerType };
    if (e.pointerType === 'touch'){
      const p = ptr;
      p.lp = setTimeout(() => { if (ptr === p && !p.mode){ ptr = null; openNoteMenu(p.sx, p.sy, p.id); } }, 550);
    }
  }

  function beginMini(e){
    checkpoint();
    const m = miniEl(ptr.id);
    const r = m.getBoundingClientRect();
    ptr.mode = 'mini';
    ptr.rootEl = m.closest('.note');
    ptr.gOffX = e.clientX - r.left; ptr.gOffY = e.clientY - r.top;
    const g = m.cloneNode(true);
    g.classList.add('ghost'); g.style.width = (r.width / B.zoom) + 'px'; g.style.transform = `scale(${B.zoom}) rotate(1.5deg)`;
    document.body.appendChild(g);
    ptr.ghost = g;
    m.classList.add('mini-drag');
    document.body.classList.add('is-dragging');
    expand(ptr.rootEl);
  }
  function moveMini(e){
    ptr.ghost.style.left = (e.clientX - ptr.gOffX) + 'px';
    ptr.ghost.style.top = (e.clientY - ptr.gOffY) + 'px';
    if (!near(ptr.rootEl, e, 20)){
      ptr.ghost.remove(); ptr.ghost = null;
      collapseExp();
      beginDrag(e, true);
      moveDrag(e);
      return;
    }
    setTarget(pointTarget(e, ptr.rootEl));
  }
  function endMini(){
    const p = ptr;
    const tgt = p.tgt, fromRect = p.ghost ? p.ghost.getBoundingClientRect() : null;
    if (p.ghost) p.ghost.remove();
    collapseExp(); ptr = null;
    document.body.classList.remove('is-dragging');
    if (tgt && tgt.ok) applyDrop(p.id, tgt, fromRect);
    else { H().u.pop(); updateUndo(); if (tgt && tgt.why) toast('Can’t place it there: ' + tgt.why + '.'); render(); }
  }

  function beginDrag(e, fromMini){
    const n = N(ptr.id);
    const w = toWorld(e.clientX, e.clientY);
    if (!fromMini) checkpoint();
    if (ptr.isChild){
      const m = miniEl(n.id);
      const mr = m.getBoundingClientRect();
      const p = N(n.parent);
      p.children = p.children.filter(c => c !== n.id);
      n.parent = null;
      ptr.offX = Math.max(10, Math.min((ptr.gOffX || (e.clientX - mr.left)) / B.zoom, (n.w || DEFAULT_W) - 20));
      ptr.offY = Math.max(8, Math.min((ptr.gOffY || 15) / B.zoom, 30));
      n.x = w.x - ptr.offX; n.y = w.y - ptr.offY; n.z = ++B.z;
      ptr.isChild = false;
      selectOnly(n.id);
      render();
      ptr.el = noteEl(n.id);
      ptr.el.style.animation = 'popout .22s ease-out';
    } else if (sel.has(n.id) && sel.size > 1){
      ptr.mode = 'group';
      ptr.start = toWorld(ptr.sx, ptr.sy);
      ptr.group = [...sel].map(id => ({ id, x0:N(id).x, y0:N(id).y, el:noteEl(id) }));
      ptr.group.forEach(g => { g.el.classList.add('group-drag'); N(g.id).z = ++B.z; g.el.style.zIndex = N(g.id).z; });
      document.body.classList.add('is-dragging');
      return;
    } else {
      if (!sel.has(n.id)) selectOnly(n.id);
      const w0 = toWorld(ptr.sx, ptr.sy);
      ptr.offX = w0.x - n.x; ptr.offY = w0.y - n.y;
      n.z = ++B.z;
      ptr.el = noteEl(n.id);
      ptr.el.style.zIndex = n.z;
    }
    ptr.el.classList.add('dragging');
    document.body.classList.add('is-dragging');
    ptr.mode = 'note';
    ptr.exp = null; ptr.tgt = null; curKey = '';
  }
  function moveGroup(e){
    const w = toWorld(e.clientX, e.clientY);
    const dx = w.x - ptr.start.x, dy = w.y - ptr.start.y;
    for (const g of ptr.group){
      const n = N(g.id);
      n.x = snapV(g.x0 + dx); n.y = snapV(g.y0 + dy);
      g.el.style.left = n.x + 'px'; g.el.style.top = n.y + 'px';
    }
    scheduleLinks();
  }
  function endGroup(){
    ptr.group.forEach(g => g.el.classList.remove('group-drag'));
    ptr = null;
    document.body.classList.remove('is-dragging');
    save(); drawLinks();
  }
  function bottomOverlap(){
    const dr = ptr.el.getBoundingClientRect();
    let best = null, bestScore = -Infinity;
    for (const te of world.querySelectorAll(':scope > .note')){
      if (te === ptr.el) continue;
      const r = te.getBoundingClientRect();
      const hOverlap = Math.min(dr.right, r.right) - Math.max(dr.left, r.left);
      if (hOverlap < Math.min(dr.width, r.width) * 0.35) continue;
      if (dr.top < r.top + r.height * 0.45 || dr.top > r.bottom + 26) continue;
      const score = hOverlap - Math.abs(dr.top - r.bottom) * 2;
      if (score > bestScore){ bestScore = score; best = te; }
    }
    return best;
  }
  function moveDrag(e){
    const n = N(ptr.id);
    const w = toWorld(e.clientX, e.clientY);
    n.x = snapV(w.x - ptr.offX); n.y = snapV(w.y - ptr.offY);
    ptr.el.style.left = n.x + 'px'; ptr.el.style.top = n.y + 'px';

    const hit = document.elementFromPoint(e.clientX, e.clientY);
    const hoverRoot = hit ? hit.closest('#world > .note') : null;
    const best = ptr.exp ? null : bottomOverlap();
    if (ptr.exp && ptr.exp !== hoverRoot && !near(ptr.exp, e, 24)) collapseExp();
    if (!ptr.exp){
      if (best && N(best.dataset.id).children.length) expand(best);
      else if (hoverRoot && N(hoverRoot.dataset.id).children.length){
        const now = performance.now();
        if (ptr.hoverId !== hoverRoot.dataset.id){ ptr.hoverId = hoverRoot.dataset.id; ptr.hoverT = now; }
        else if (now - ptr.hoverT > 220) expand(hoverRoot);
      } else ptr.hoverId = null;
    }
    if (ptr.exp) setTarget(pointTarget(e, ptr.exp) || { kind:'into', parent:ptr.exp.dataset.id, el:ptr.exp });
    else if (best) setTarget({ kind:'into', parent:best.dataset.id, el:best });
    else setTarget(null);
    scheduleLinks();
  }
  function endDrag(){
    const p = ptr, tgt = p.tgt, fromRect = p.el.getBoundingClientRect();
    collapseExp(); clearIndicators();
    ptr = null;
    document.body.classList.remove('is-dragging');
    if (tgt && tgt.ok) applyDrop(p.id, tgt, fromRect);
    else { if (tgt && tgt.why) toast('Can’t place it there: ' + tgt.why + '.'); render(); save(); }
  }

  function handleClick(p, e){
    if (p.shift && !p.isChild){ toggleSel(p.id); return; }
    if (!p.isChild) selectOnly(p.id);
    const now = performance.now();
    if (lastClick && lastClick.id === p.id && now - lastClick.t < 320){
      clearTimeout(lastClick.timer); lastClick = null;
      inlineEdit(p.id);
    } else {
      if (lastClick) clearTimeout(lastClick.timer);
      const id = p.id;
      lastClick = { id, t:now, timer:setTimeout(() => { lastClick = null; if (N(id)) openEditor(id); }, 260) };
    }
  }

  /* ---------- resize ---------- */
  function startResize(e, id){
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    e.preventDefault(); e.stopPropagation();
    checkpoint();
    const n = N(id), ne = noteEl(id), body = ne.querySelector('.note-body');
    rsz = { id, sx:e.clientX, sy:e.clientY, w:ne.offsetWidth, h:body.offsetHeight, ne, body };
    ne.classList.add('sized');
    ne.style.zIndex = n.z = ++B.z;
    document.body.classList.add('is-resizing');
  }
  function moveResize(e){
    const n = N(rsz.id);
    n.w = snapV(Math.max(170, Math.min(720, rsz.w + (e.clientX - rsz.sx) / B.zoom)));
    n.h = Math.round(Math.max(48, Math.min(900, rsz.h + (e.clientY - rsz.sy) / B.zoom)));
    rsz.ne.style.width = n.w + 'px';
    rsz.body.style.height = n.h + 'px';
    scheduleLinks();
  }

  /* ================= Board: pan, marquee, pinch, wheel ================= */
  board.addEventListener('pointerdown', e => {
    if (e.pointerType === 'touch'){
      touches.set(e.pointerId, { x:e.clientX, y:e.clientY });
      if (touches.size === 2){
        if (ptr){ if (ptr.ghost) ptr.ghost.remove(); clearTimeout(ptr.lp); ptr = null; document.body.classList.remove('is-dragging'); render(); }
        panPtr = null; board.classList.remove('panning');
        const [a, b] = [...touches.values()];
        const mid = { x:(a.x + b.x)/2, y:(a.y + b.y)/2 };
        pinch = { d0:Math.hypot(a.x - b.x, a.y - b.y) || 1, z0:B.zoom, w0:toWorld(mid.x, mid.y) };
      }
    }
  }, true);

  const isEmptyTarget = t => t === board || t === world || t.id === 'links' || emptyEl.contains(t);
  board.addEventListener('pointerdown', e => {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    if (!isEmptyTarget(e.target) || pinch) return;
    closeMenu(); hideLinkPop();
    if (document.activeElement && document.activeElement.blur && typing()) document.activeElement.blur();
    if (e.shiftKey){
      const br = board.getBoundingClientRect();
      marq = { sx:e.clientX, sy:e.clientY, br, base:new Set(sel) };
      const m = $('marquee'); m.hidden = false; m.style.left = (e.clientX - br.left) + 'px'; m.style.top = (e.clientY - br.top) + 'px'; m.style.width = m.style.height = '0px';
      return;
    }
    panPtr = { sx:e.clientX, sy:e.clientY, px:B.pan.x, py:B.pan.y, moved:false };
    if (e.pointerType === 'touch'){
      const p = panPtr;
      p.lp = setTimeout(() => { if (panPtr === p && !p.moved){ panPtr = null; openBoardMenu(p.sx, p.sy); } }, 550);
    }
    board.classList.add('panning');
  });
  board.addEventListener('dblclick', e => {
    if (!isEmptyTarget(e.target)) return;
    const w = toWorld(e.clientX, e.clientY);
    if (P.newAt && P.newAt(e.clientX, e.clientY, w)) return;
    const n = createNote(w.x - DEFAULT_W/2, w.y - 30);
    openEditor(n.id, true);
  });
  board.addEventListener('wheel', e => {
    if (e.target.closest('textarea')) return;
    e.preventDefault();
    if (e.ctrlKey || e.metaKey) zoomAt(e.clientX, e.clientY, B.zoom * Math.exp(-e.deltaY * (e.deltaMode ? 0.05 : 0.0025) * (e.ctrlKey && !e.metaKey && Math.abs(e.deltaY) < 50 ? 4 : 1)));
    else { B.pan.x -= e.deltaX; B.pan.y -= e.deltaY; applyView(); }
    viewChanged();
  }, { passive:false });
  let viewT;
  // Pan/zoom is per-person view state, not board data: remember it quietly, never sync it.
  function viewChanged(){ clearTimeout(viewT); viewT = setTimeout(() => cloud.on ? storeView() : save(true), 400); }

  function zoomAt(cx, cy, z){
    z = Math.max(0.2, Math.min(2.5, z));
    const w = toWorld(cx, cy), br = board.getBoundingClientRect();
    B.zoom = z;
    B.pan.x = cx - br.left - w.x * z; B.pan.y = cy - br.top - w.y * z;
    applyView();
  }
  function zoomCenter(f){ const r = board.getBoundingClientRect(), a = openArea(); zoomAt(r.left + r.width/2, r.top + (a.top + a.bot)/2, f(B.zoom)); viewChanged(); }
  function contentBox(){
    const els = [...world.querySelectorAll(':scope > .note, :scope > .link-label, :scope > .frame')];
    if (!els.length) return null;
    let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
    for (const e of els){ const r = worldRect(e); x1 = Math.min(x1, r.x); y1 = Math.min(y1, r.y); x2 = Math.max(x2, r.x + r.w); y2 = Math.max(y2, r.y + r.h); }
    return { x:x1, y:y1, w:x2 - x1, h:y2 - y1 };
  }
  // Fit every card on screen. minZoom: when a board first opens, don't shrink cards past the point where
  // their text stops being readable; if it still doesn't fit, start at the top-left of the content instead.
  const OPEN_MIN_ZOOM = 0.85;
  // The part of the board not covered by the top bar (and tool row) or the bottom strip, in board coordinates.
  function openArea(){
    const r = board.getBoundingClientRect();
    let top = 0, bot = r.height;
    for (const id of ['topleft', 'toolbar', 'topright']){ const e = $(id); if (e && e.getClientRects().length) top = Math.max(top, e.getBoundingClientRect().bottom - r.top); }
    for (const id of ['tabs', 'zoombar']){ const e = $(id); if (e && e.getClientRects().length) bot = Math.min(bot, e.getBoundingClientRect().top - r.top); }
    const narrow = r.width < 600;
    return { w:r.width, top, bot, side:narrow ? 16 : 60, pad:narrow ? 14 : 30 };
  }
  function fitAll(minZoom){
    const bb = contentBox();
    if (!bb){ B.zoom = 1; B.pan = { x:0, y:0 }; applyView(); return; }
    const a = openArea(), h = a.bot - a.top;
    const want = Math.min(1.25, (a.w - a.side * 2) / bb.w, (h - a.pad * 2) / bb.h);
    const floor = typeof minZoom === 'number' ? minZoom : 0.2;
    const z = Math.max(floor, want);
    B.zoom = z;
    if (want >= floor){
      B.pan.x = Math.round(a.w/2 - (bb.x + bb.w/2) * z);
      B.pan.y = Math.round(a.top + h/2 - (bb.y + bb.h/2) * z);
    } else {
      B.pan.x = Math.round(a.side - bb.x * z);
      B.pan.y = Math.round(a.top + a.pad - bb.y * z);       // just under the top bar
    }
    applyView(); viewChanged();
  }
  const fitOnOpen = () => fitAll(OPEN_MIN_ZOOM);
  function centerOn(id){
    const e = visibleElFor(id); if (!e) return;
    const r = worldRect(e), a = openArea();
    B.pan.x = Math.round(a.w/2 - (r.x + r.w/2) * B.zoom);
    B.pan.y = Math.round((a.top + a.bot)/2 - (r.y + r.h/2) * B.zoom);
    applyView(); viewChanged();
    if (e.animate) e.animate([{ boxShadow:'0 0 0 0 rgba(37,99,235,0)' }, { boxShadow:'0 0 0 8px rgba(37,99,235,.35)' }, { boxShadow:'0 0 0 0 rgba(37,99,235,0)' }], { duration:700 });
  }

  /* ================= Global pointer routing ================= */
  window.addEventListener('pointermove', e => {
    if (e.pointerType === 'touch' && touches.has(e.pointerId)) touches.set(e.pointerId, { x:e.clientX, y:e.clientY });
    if (pinch){
      if (touches.size >= 2){
        const [a, b] = [...touches.values()];
        const d = Math.hypot(a.x - b.x, a.y - b.y);
        const mid = { x:(a.x + b.x)/2, y:(a.y + b.y)/2 };
        const z = Math.max(0.2, Math.min(2.5, pinch.z0 * d / pinch.d0));
        const br = board.getBoundingClientRect();
        B.zoom = z;
        B.pan.x = mid.x - br.left - pinch.w0.x * z; B.pan.y = mid.y - br.top - pinch.w0.y * z;
        applyView();
      }
      return;
    }
    if (linkMode){ moveLink(e); return; }
    if (marq){
      const br = marq.br, x1 = Math.min(marq.sx, e.clientX), y1 = Math.min(marq.sy, e.clientY), x2 = Math.max(marq.sx, e.clientX), y2 = Math.max(marq.sy, e.clientY);
      const m = $('marquee'); m.style.left = (x1 - br.left) + 'px'; m.style.top = (y1 - br.top) + 'px'; m.style.width = (x2 - x1) + 'px'; m.style.height = (y2 - y1) + 'px';
      sel.clear(); marq.base.forEach(id => sel.add(id));
      for (const ne of world.querySelectorAll(':scope > .note')){
        const r = ne.getBoundingClientRect();
        if (r.right > x1 && r.left < x2 && r.bottom > y1 && r.top < y2) sel.add(ne.dataset.id);
      }
      syncSelClasses();
      return;
    }
    if (panPtr){
      if (Math.hypot(e.clientX - panPtr.sx, e.clientY - panPtr.sy) > 3){ panPtr.moved = true; clearTimeout(panPtr.lp); }
      B.pan.x = panPtr.px + (e.clientX - panPtr.sx);
      B.pan.y = panPtr.py + (e.clientY - panPtr.sy);
      applyView();
      return;
    }
    if (rsz){ moveResize(e); return; }
    if (frPtr){ moveFrame(e); return; }
    if (frRsz){ moveFrameResize(e); return; }
    if (!ptr) return;
    if (!ptr.mode){
      if (Math.hypot(e.clientX - ptr.sx, e.clientY - ptr.sy) < 5) return;
      clearTimeout(ptr.lp);
      if (lastClick){ clearTimeout(lastClick.timer); lastClick = null; }
      if (ptr.isChild) beginMini(e); else beginDrag(e);
    }
    if (ptr.mode === 'mini') moveMini(e);
    else if (ptr.mode === 'group') moveGroup(e);
    else moveDrag(e);
  });

  function pointerEnd(e){
    if (e.pointerType === 'touch'){ touches.delete(e.pointerId); if (pinch && touches.size < 2){ pinch = null; viewChanged(); } }
    if (linkMode && !linkMode.sticky){ finishLink(e); return; }
    if (marq){ marq = null; $('marquee').hidden = true; return; }
    if (panPtr){
      clearTimeout(panPtr.lp);
      const moved = panPtr.moved; panPtr = null; board.classList.remove('panning');
      if (!moved) clearSel(); else viewChanged();
      return;
    }
    if (rsz){ rsz = null; document.body.classList.remove('is-resizing'); render(); save(); return; }
    if (frPtr){ endFrame(); return; }
    if (frRsz){ frRsz = null; document.body.classList.remove('is-resizing'); save(); return; }
    if (!ptr) return;
    clearTimeout(ptr.lp);
    if (!ptr.mode){ const p = ptr; ptr = null; if (e.type === 'pointerup') handleClick(p, e); return; }
    if (ptr.mode === 'mini') endMini();
    else if (ptr.mode === 'group') endGroup();
    else endDrag();
  }
  window.addEventListener('pointerup', pointerEnd);
  window.addEventListener('pointercancel', pointerEnd);

  /* ================= Inline editing on the card ================= */
  function inlineEdit(id){
    const n = N(id); if (!n) return;
    const isMini = !!n.parent;
    const ne = isMini ? miniEl(id) : noteEl(id); if (!ne) return;
    checkpoint();
    const before = n.text;
    const ta = el('textarea', 'inline' + (isMini ? ' mini-inline' : ''));
    ta.value = n.text;
    ta.placeholder = 'Title on the first line…';
    let h = 60;
    if (isMini){ ne.querySelector(':scope > .row').replaceWith(ta); }
    else { const body = ne.querySelector('.note-body'); h = body.offsetHeight; body.textContent = ''; body.appendChild(ta); }
    ne.classList.add('editing');
    const fit = () => { ta.style.height = 'auto'; ta.style.height = Math.max(h - 26, ta.scrollHeight + 2) + 'px'; };
    fit(); ta.addEventListener('input', () => { n.text = ta.value; fit(); });
    ta.addEventListener('pointerdown', e => e.stopPropagation());
    ta.addEventListener('wheel', e => e.stopPropagation());
    let done = false;
    const finish = () => {
      if (done) return; done = true;
      n.text = ta.value;
      if (n.text === before){ H().u.pop(); updateUndo(); }
      render(); save();
    };
    textKeys(ta, finish);
    ta.addEventListener('keydown', e => { if (e.key === 'Escape'){ e.preventDefault(); e.stopPropagation(); finish(); } });
    ta.addEventListener('blur', finish);
    ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length);
  }

  // shared keyboard behaviour for note text boxes
  function textKeys(ta, onEnter){
    ta.addEventListener('keydown', e => {
      if (e.isComposing) return;
      // On a phone keyboard Return is the only way to start a new line, so it never closes the editor there (Done does).
      if (e.key === 'Enter' && !e.shiftKey && !e.altKey && !TOUCH.matches){ e.preventDefault(); e.stopPropagation(); onEnter(); return; }
      if (e.key === 'Enter' && (e.shiftKey || TOUCH.matches) && !e.altKey){
        const v = ta.value, s = ta.selectionStart;
        const ls = v.lastIndexOf('\n', s - 1) + 1;
        const line = v.slice(ls, s);
        const m = /^(\s*)([-*]) (\[[ xX]\] )?/.exec(line);
        if (m){
          e.preventDefault();
          if (line.trim() === m[0].trim()){ ta.setRangeText('', ls, s, 'end'); }
          else ta.setRangeText('\n' + m[1] + m[2] + ' ' + (m[3] ? '[ ] ' : ''), s, ta.selectionEnd, 'end');
          ta.dispatchEvent(new Event('input'));
        }
        return;
      }
      if (e.key === 'Tab'){
        e.preventDefault();
        const v = ta.value, s = ta.selectionStart, en = ta.selectionEnd;
        const ls = v.lastIndexOf('\n', s - 1) + 1;
        const le = v.indexOf('\n', en - (en > s && v[en - 1] === '\n' ? 1 : 0)); const lend = le < 0 ? v.length : le;
        const block = v.slice(ls, lend);
        const out = block.split('\n').map(l => e.shiftKey ? l.replace(/^ {1,2}|^\t/, '') : '  ' + l).join('\n');
        ta.setRangeText(out, ls, lend, 'preserve');
        const d = out.length - block.length;
        if (s === en){ const ns = Math.max(ls, s + (e.shiftKey ? (out.split('\n')[0].length - block.split('\n')[0].length) : 2)); ta.setSelectionRange(ns, ns); }
        else ta.setSelectionRange(ls, lend + d);
        ta.dispatchEvent(new Event('input'));
        return;
      }
      if ((e.ctrlKey || e.metaKey) && !e.shiftKey && (e.key === 'b' || e.key === 'i')){
        e.preventDefault();
        const w = e.key === 'b' ? '**' : '*';
        const s = ta.selectionStart, en = ta.selectionEnd, t = ta.value.slice(s, en);
        ta.setRangeText(w + t + w, s, en, 'select');
        if (s === en) ta.setSelectionRange(s + w.length, s + w.length);
        ta.dispatchEvent(new Event('input'));
      }
    });
  }

  /* ================= Editor ================= */
  const modal = $('modal'), sheet = $('sheet'), edText = $('edText'), edAtts = $('edAtts'), edDrop = $('edDrop'),
        edFile = $('edFile'), edDelete = $('edDelete'), edDetach = $('edDetach'), edLabel = $('edLabel'),
        edTucked = $('edTucked'), edSwatches = $('edSwatches'), edStatus = $('edStatus'), edHrs = $('edHrs'), edDue = $('edDue'), edOwner = $('edOwner');
  let editId = null, editBefore = '';
  const noteSig = n => JSON.stringify([n.text, P.sig ? P.sig(n) : null, n.color, n.status, n.hrs, n.due, n.owner, n.attachments.map(a => a.id), n.children, n.parent]);

  function openEditor(id, fresh){
    const n = N(id); if (!n) return;
    closeMenu(); hideLinkPop();
    if (!fresh) checkpoint();
    editId = id; editBefore = fresh ? null : noteSig(n);
    edText.value = n.text;
    if (P.editorText) P.editorText(n, edText);
    if (edHrs) edHrs.value = n.hrs == null ? '' : n.hrs;
    if (edDue) edDue.value = n.due || '';
    edOwner.value = n.owner || '';
    disarmDelete();
    paintEditor();
    modal.hidden = false;
    setTimeout(() => { edText.focus(); edText.setSelectionRange(edText.value.length, edText.value.length); }, 0);
  }
  function closeEditor(){
    if (editId == null) return;
    const n = N(editId);
    if (n && editBefore && noteSig(n) === editBefore){ H().u.pop(); updateUndo(); }
    editId = null;
    modal.hidden = true;
    render(); save();
  }
  function paintEditor(){
    const n = N(editId); if (!n) return;
    sheet.style.setProperty('--c', n.color);
    const lvl = levelOf(n), parts = [];
    if (n.parent){ const pt = parseText(N(n.parent).text).title || 'Untitled'; parts.push(`Level ${lvl} of ${MAX_DEPTH} · inside “${pt.length > 24 ? pt.slice(0, 24) + '…' : pt}”`); }
    if (n.children.length) parts.push(`${n.children.length}/${MAX_TUCK} ${W.subs}`);
    edLabel.textContent = parts.join(' · ') || `Edit ${W.card}`;
    edDetach.hidden = !n.parent;

    edSwatches.textContent = ''; edSwatches.hidden = !SHOW_COLORS;
    if (SHOW_COLORS) COLORS.forEach(c => {
      const b = el('button', 'sw' + (c === n.color ? ' on' : ''));
      b.style.background = c; b.title = 'Note color'; b.setAttribute('aria-label', 'Color ' + c);
      b.addEventListener('click', () => { n.color = c; paintEditor(); render(); save(); });
      edSwatches.appendChild(b);
    });

    edStatus.textContent = '';
    edStatus.appendChild(el('span', 'kbd-hint', 'Status'));
    Object.entries(STATUSES).forEach(([k, st]) => {
      const b = el('button', 'sp' + (n.status === k ? ' on' : ''));
      b.style.setProperty('--sc', st.c);
      const d = el('span', 'dot'); d.style.setProperty('--sc', st.c);
      b.append(d, document.createTextNode(st.label));
      b.addEventListener('click', () => { n.status = n.status === k ? null : k; paintEditor(); render(); save(); });
      edStatus.appendChild(b);
    });

    edAtts.textContent = '';
    n.attachments.forEach(a => {
      const box = el('div', 'att');
      if (isImg(a)){
        const img = el('img'); img.src = urlFor(a); img.alt = a.name;
        img.addEventListener('click', () => openLightbox(urlFor(a)));
        box.appendChild(img);
      } else box.appendChild(el('div', 'ic', ext(a.name)));
      const meta = el('div', 'meta2');
      meta.appendChild(el('div', 'nm', a.name));
      const sz = el('div', 'sz', fmtSize(a.size || 0));
      if (!isImg(a)){ const l = el('a', '', 'Open'); l.href = urlFor(a); l.target = '_blank'; l.rel = 'noopener'; sz.appendChild(l); }
      meta.appendChild(sz);
      box.appendChild(meta);
      const rm = el('button', 'rm'); rm.appendChild(I('x', 'sm')); rm.title = 'Remove attachment';
      rm.addEventListener('click', () => { n.attachments = n.attachments.filter(x => x.id !== a.id); paintEditor(); render(); save(); });
      box.appendChild(rm);
      edAtts.appendChild(box);
    });

    if (P.editorPaint) P.editorPaint(n);

    edTucked.textContent = '';
    if (n.children.length){
      edTucked.appendChild(el('div', 'lbl', 'Subnotes'));
      n.children.forEach(cid => {
        const c = N(cid); if (!c) return;
        const row = el('div', 'trow'); row.style.setProperty('--c', c.color);
        const { title } = parseText(c.text);
        const inner = c.children.length ? `  (+${c.children.length} inside)` : '';
        row.appendChild(el('span', 'tt' + (title ? '' : ' placeholder'), (title || 'Empty note') + inner));
        const open = el('button', 'btn', 'Open'); open.addEventListener('click', () => { closeEditor(); openEditor(cid); });
        const out = el('button', 'btn', 'Pop out'); out.addEventListener('click', () => { detach(cid); paintEditor(); });
        row.append(open, out);
        edTucked.appendChild(row);
      });
    }
  }
  edText.addEventListener('input', () => { const n = N(editId); if (!n) return; n.text = edText.value; save(); });
  textKeys(edText, closeEditor);
  if (edHrs) edHrs.addEventListener('input', () => { const n = N(editId); if (!n) return; const v = parseFloat(edHrs.value); n.hrs = isFinite(v) && v > 0 ? v : null; save(); });
  if (edDue) edDue.addEventListener('change', () => { const n = N(editId); if (!n) return; n.due = edDue.value || null; save(); });
  edOwner.addEventListener('input', () => { const n = N(editId); if (!n) return; n.owner = edOwner.value.trim() || null; save(); });
  [edOwner, edHrs, edDue].filter(Boolean).forEach(i => i.addEventListener('keydown', e => { if (e.key === 'Enter'){ e.preventDefault(); closeEditor(); } }));

  function addFiles(list){
    const n = N(editId); if (!n || !list || !list.length) return;
    for (const f of list) n.attachments.push({ id:uid(), name:f.name || 'pasted-file', type:f.type || '', size:f.size || 0, blob:f });
    paintEditor(); render(); save();
  }
  edFile.addEventListener('change', () => { addFiles([...edFile.files]); edFile.value = ''; });
  ['dragenter','dragover'].forEach(t => edDrop.addEventListener(t, e => { e.preventDefault(); edDrop.classList.add('over'); }));
  ['dragleave','drop'].forEach(t => edDrop.addEventListener(t, e => { e.preventDefault(); edDrop.classList.remove('over'); }));
  edDrop.addEventListener('drop', e => addFiles([...(e.dataTransfer?.files || [])]));
  sheet.addEventListener('paste', e => { const files = [...(e.clipboardData?.files || [])]; if (files.length){ e.preventDefault(); addFiles(files); } });
  sheet.addEventListener('dragover', e => e.preventDefault());
  sheet.addEventListener('drop', e => { if (!edDrop.contains(e.target)){ e.preventDefault(); addFiles([...(e.dataTransfer?.files || [])]); } });
  window.addEventListener('dragover', e => e.preventDefault());
  let fileOver = null;
  const setFileOver = t => { if (fileOver && fileOver !== t) fileOver.classList.remove('file-over'); fileOver = t; if (t) t.classList.add('file-over'); };
  board.addEventListener('dragover', e => {
    if (!e.dataTransfer || ![...e.dataTransfer.types].includes('Files')) return;
    const hit = document.elementFromPoint(e.clientX, e.clientY);
    setFileOver(hit && hit.closest('#world .mini, #world > .note'));
  });
  board.addEventListener('dragleave', e => { if (e.target === board) setFileOver(null); });
  window.addEventListener('drop', async e => {
    e.preventDefault();
    setFileOver(null);
    if (!modal.hidden) return;
    const files = [...(e.dataTransfer?.files || [])];
    if (!files.length) return;
    const boards = files.filter(f => BOARD_FILE.test(f.name));
    if (boards.length){ for (const f of boards) await importFile(f); return; }
    if ((LIB && (!libEl.hidden || !pkgDlg.hidden)) || !B) return;
    const hit = document.elementFromPoint(e.clientX, e.clientY);
    const t = hit && hit.closest('#world .mini, #world > .note');
    if (t && N(t.dataset.id)){
      const n = N(t.dataset.id);
      checkpoint();
      files.forEach(f => n.attachments.push({ id:uid(), name:f.name, type:f.type || '', size:f.size || 0, blob:f }));
      render(); save();
      toast(`Attached ${files.length} file${files.length > 1 ? 's' : ''} to “${parseText(n.text).title || 'note'}”`);
      return;
    }
    const w = toWorld(e.clientX, e.clientY);
    const n = createNote(w.x - DEFAULT_W/2, w.y - 30, { text:files.length === 1 ? files[0].name : `${files.length} files` });
    n.attachments = files.map(f => ({ id:uid(), name:f.name, type:f.type || '', size:f.size || 0, blob:f }));
    render(); save();
  });

  let armT = null;
  function disarmDelete(){ clearTimeout(armT); edDelete.classList.remove('armed'); edDelete.textContent = `Delete ${W.card}`; }
  edDelete.addEventListener('click', () => {
    if (!edDelete.classList.contains('armed')){
      edDelete.classList.add('armed'); edDelete.textContent = 'Click again to delete';
      armT = setTimeout(disarmDelete, 3000);
      return;
    }
    const id = editId; editId = null; modal.hidden = true; disarmDelete();
    H().u.pop();
    deleteNotes([id]);
  });
  edDetach.addEventListener('click', () => { const id = editId; detach(id); paintEditor(); });
  $('edDone').addEventListener('click', closeEditor);
  $('edClose').addEventListener('click', closeEditor);
  modal.addEventListener('pointerdown', e => { if (e.target === modal) closeEditor(); });

  const lb = $('lightbox');
  function openLightbox(src){ lb.querySelector('img').src = src; lb.hidden = false; }
  lb.addEventListener('click', () => { lb.hidden = true; });

  /* ================= Context menus ================= */
  const menu = $('menu');
  function closeMenu(){ menu.hidden = true; menu.textContent = ''; }
  function showMenu(x, y){
    menu.hidden = false;
    const w = menu.offsetWidth, h = menu.offsetHeight;
    menu.style.left = Math.max(6, Math.min(innerWidth - w - 6, x)) + 'px';
    menu.style.top = Math.max(6, Math.min(innerHeight - h - 6, y)) + 'px';
  }
  function mi(label, fn, key, bad){
    const b = el('button', 'mi' + (bad ? ' bad' : ''));
    b.appendChild(el('span', '', label));
    if (key) b.appendChild(el('span', 'k', key));
    b.addEventListener('click', () => { closeMenu(); fn(); });
    menu.appendChild(b);
  }
  const ms = () => menu.appendChild(el('div', 'ms'));
  function colorRow(ids){
    if (!SHOW_COLORS) return;
    menu.appendChild(el('div', 'ml', 'Color'));
    const row = el('div', 'mrow');
    COLORS.forEach(c => {
      const b = el('button', 'sw' + (ids.length === 1 && N(ids[0]).color === c ? ' on' : ''));
      b.style.background = c;
      b.addEventListener('click', () => { checkpoint(); ids.forEach(id => N(id).color = c); closeMenu(); render(); save(); });
      row.appendChild(b);
    });
    menu.appendChild(row);
  }
  function statusRow(ids){
    menu.appendChild(el('div', 'ml', 'Status'));
    const row = el('div', 'mrow');
    const cur = ids.length === 1 ? N(ids[0]).status : null;
    Object.entries(STATUSES).forEach(([k, st]) => {
      const b = el('button', 'sp' + (cur === k ? ' on' : ''));
      b.style.setProperty('--sc', st.c);
      const d = el('span', 'dot'); d.style.setProperty('--sc', st.c);
      b.append(d, document.createTextNode(st.label));
      b.addEventListener('click', () => { checkpoint(); ids.forEach(id => N(id).status = (cur === k ? null : k)); closeMenu(); render(); save(); });
      row.appendChild(b);
    });
    menu.appendChild(row);
  }
  function openNoteMenu(x, y, id){
    closeMenu(); hideLinkPop();
    const n = N(id); if (!n) return;
    const isTop = !n.parent;
    if (isTop && sel.has(id) && sel.size > 1) return openSelMenu(x, y);
    if (isTop) selectOnly(id);
    mi('Open details', () => openEditor(id), 'Enter');
    mi('Edit text on card', () => inlineEdit(id), 'Dbl-click');
    mi('Connect to…', () => beginLink(id, null, true));
    if (n.children.length) mi(n.collapsed ? `Expand ${W.subs}` : `Collapse ${W.subs}`, () => toggleCollapse(id));
    if (n.parent) mi('Pop out of stack', () => detach(id));
    ms();
    mi('Copy', () => { sel.clear(); clip = packNotes([id]); clip.n = 0; toast('Copied 1 note'); }, '⌘/Ctrl+C');
    mi('Duplicate', () => duplicate([id]), '⌘/Ctrl+D');
    if (isTop){ mi('Bring to front', () => zFront([id])); mi('Send to back', () => zBack([id])); }
    ms();
    if (cfg.statusMenu) statusRow([id]);
    colorRow([id]);
    ms();
    mi('Delete', () => deleteNotes([id]), 'Del', true);
    showMenu(x, y);
  }
  function openSelMenu(x, y){
    closeMenu();
    const ids = [...sel];
    menu.appendChild(el('div', 'ml', `${ids.length} notes selected`));
    mi('Align left edges', () => align('left', ids));
    mi('Align top edges', () => align('top', ids));
    mi('Distribute horizontally', () => align('h', ids));
    mi('Distribute vertically', () => align('v', ids));
    mi('Tidy into a grid', () => align('tidy', ids));
    ms();
    mi('Copy', () => copySel(), '⌘/Ctrl+C');
    mi('Duplicate', () => duplicate(ids), '⌘/Ctrl+D');
    mi('Bring to front', () => zFront(ids));
    mi('Send to back', () => zBack(ids));
    ms();
    if (cfg.statusMenu) statusRow(ids);
    colorRow(ids);
    ms();
    mi(`Delete ${ids.length} notes`, () => deleteNotes(ids), 'Del', true);
    showMenu(x, y);
  }
  function openBoardMenu(x, y){
    closeMenu(); hideLinkPop();
    const w = toWorld(x, y);
    if (P.newAt) mi(`New ${W.card} here…`, () => setTimeout(() => P.newAt(x, y, w), 0), 'Dbl-click');
    else mi(`New ${W.card} here`, () => { const n = createNote(w.x - DEFAULT_W/2, w.y - 30); openEditor(n.id, true); }, 'Dbl-click');
    mi('New frame here', () => createFrame(w.x - 40, w.y - 30), 'F');
    if (clip) mi('Paste here', () => unpack(clip, { x:w.x, y:w.y }, 0), '⌘/Ctrl+V');
    mi('Select all', selectAll, '⌘/Ctrl+A');
    ms();
    mi(`Fit all ${W.cards}`, () => fitAll(), 'Shift+1');
    mi(app.snap ? 'Turn off snap to grid' : 'Snap to grid', toggleSnap, 'G');
    showMenu(x, y);
  }
  board.addEventListener('contextmenu', e => {
    e.preventDefault();
    if (!menu.hidden && e.pointerType === 'touch') return;
    const m = e.target.closest('.mini'), ne = e.target.closest('#world > .note'), fe = e.target.closest('.frame');
    if (fe && !m && !ne) openFrameMenu(e.clientX, e.clientY, fe.dataset.id);
    else if (m) openNoteMenu(e.clientX, e.clientY, m.dataset.id);
    else if (ne) openNoteMenu(e.clientX, e.clientY, ne.dataset.id);
    else if (isEmptyTarget(e.target)) openBoardMenu(e.clientX, e.clientY);
  });
  document.addEventListener('pointerdown', e => {
    if (!menu.hidden && !menu.contains(e.target)) closeMenu();
    if (!linkPop.hidden && !linkPop.contains(e.target) && !e.target.closest('.lk-hit, .link-label')) hideLinkPop();
  }, true);

  /* File menu */
  $('fileBtn').addEventListener('click', e => {
    e.stopPropagation();
    closeMenu();
    const r = e.currentTarget.getBoundingClientRect();
    mi('Export this package…', () => exportBoard(), '⌘/Ctrl+S');
    mi('Import a package…', () => $('importFile').click(), '⌘/Ctrl+O');
    ms();
    mi('Print / PDF…', openPrint, '⌘/Ctrl+P');
    mi('Export as image (PNG)', exportPNG);
    showMenu(r.left, r.bottom + 6);
  });

  /* ================= Search ================= */
  const search = $('search');
  let matches = [], matchIdx = -1;
  function applySearch(){
    const q = search.value.trim().toLowerCase();
    world.classList.toggle('searching', !!q);
    world.querySelectorAll('.hit, .dim').forEach(e => e.classList.remove('hit', 'dim'));
    matches = [];
    if (!q){ $('searchCount').textContent = ''; return; }
    const hit = n => ((n.text || '') + ' ' + (n.owner || '') + ' ' + (P.searchText ? P.searchText(n) : '')).toLowerCase().includes(q);
    const any = n => hit(n) || n.children.some(c => N(c) && any(N(c)));
    const walk = n => { if (hit(n)) matches.push(n.id); n.children.forEach(c => N(c) && walk(N(c))); };
    tops().sort((a, b) => (a.y - b.y) || (a.x - b.x)).forEach(walk);
    for (const ne of world.querySelectorAll(':scope > .note')){
      const n = N(ne.dataset.id);
      ne.classList.toggle('dim', !any(n));
      ne.classList.toggle('hit', hit(n));
    }
    for (const m of world.querySelectorAll('.mini')) m.classList.toggle('hit', hit(N(m.dataset.id)));
    $('searchCount').textContent = matches.length ? `${matches.length} found` : 'none';
  }
  search.addEventListener('input', () => { matchIdx = -1; applySearch(); });
  search.addEventListener('keydown', e => {
    if (e.key === 'Enter'){
      e.preventDefault();
      if (!matches.length) return;
      matchIdx = (matchIdx + (e.shiftKey ? -1 : 1) + matches.length) % matches.length;
      const id = matches[matchIdx];
      for (let n = N(id); n && n.parent; n = N(n.parent)){ const p = N(n.parent); if (p.collapsed){ p.collapsed = false; render(); } }
      centerOn(id);
      $('searchCount').textContent = `${matchIdx + 1} of ${matches.length}`;
    }
    if (e.key === 'Escape'){ search.value = ''; applySearch(); search.blur(); }
  });

  /* ================= Library shell (Ops Task Library, Consumables Tracker) ================= */
  // A library page of boards; each board is opened on its own. Frames group the cards, arrows give the
  // order, and the usual stacking rules hold (3 sub-cards per card, 4 levels).
  const libEl = $('library'), libGrid = $('libBody'), libSearch = $('libSearch'), pkgDlg = $('pkgDlg');
  let libDirty = true, libQueued = false;
  const AREAS = cfg.areas || [];
  const AREA_COLORS = cfg.areaColors || {};
  const areaColor = a => SHOW_COLORS ? (AREA_COLORS[(a || '').trim().toLowerCase()] || cfg.areaDefault || '#78716c') : 'var(--muted)';   // areas are named, not coloured
  const fmtHrs = h => { const v = Number(h); return isFinite(v) && v > 0 ? (Math.round(v * 100) / 100) + ' h' : ''; };

  function libChanged(){
    libDirty = true;
    if (!LIB || libEl.hidden || libQueued) return;
    libQueued = true;
    requestAnimationFrame(() => { libQueued = false; if (!libEl.hidden) renderLibrary(); });
  }
  function updateUrl(){
    try {
      const u = new URL(location.href);
      if (B && libEl.hidden) u.searchParams.set(cfg.urlParam, B.id); else u.searchParams.delete(cfg.urlParam);
      history.replaceState(null, '', u);
    } catch (e) {}
  }
  function switchBoard(id){
    if (!app.boards[id]) return;
    if (B && B.id === id){ if (LIB) renderChrome(); return; }
    cancelLink(); closeMenu(); hideLinkPop();
    app.current = id; B = app.boards[id];
    sel.clear();
    render(); save(!!LIB);
  }
  // Show a board in whichever shell the page uses.
  function showBoard(id){ if (LIB) openPackage(id); else { B = null; switchBoard(id); } }
  function openPackage(id){
    if (!app.boards[id]) return;
    switchBoard(id);
    closeLibrary();
    if (!B.seen){ B.seen = true; requestAnimationFrame(fitOnOpen); save(true); }
  }
  function renderChrome(){
    if (!LIB) return renderTabs();
    $('brandSub').textContent = libEl.hidden && B ? B.name : T.libTitle;
    document.title = libEl.hidden && B ? `${B.name} · ${cfg.title}` : cfg.title;
  }
  function openLibrary(){
    cancelLink(); closeMenu(); hideLinkPop(); clearSel();
    libEl.hidden = false; document.body.classList.add('lib-open');
    $('tips').hidden = true;
    renderLibrary(); renderChrome(); updateUrl();
  }
  function closeLibrary(){
    if (!B) return;
    libEl.hidden = true; document.body.classList.remove('lib-open');
    renderChrome(); updateUrl();
    if (!app.tipsSeen) $('tips').hidden = false;
  }

function pkgStats(b){
    if (P.stats) return P.stats(b);
    const notes = Object.values(b.notes), steps = notes.filter(n => !n.parent);
    let hrs = 0, ck = 0;
    for (const n of notes){ const v = Number(n.hrs); if (isFinite(v) && v > 0) hrs += v; ck += checklist(n.text).total; }
    const phases = [...b.frames].sort((x, y) => (x.x - y.x) || (x.y - y.y));
    return { steps:steps.length, subs:notes.length - steps.length, hrs, checks:ck, phases };
  }
function pkgSummary(b){
    const st = pkgStats(b), m = b.meta || {};
    const parts = P.summaryParts ? P.summaryParts(b, st, m)
      : [m.area, `${st.steps} ${st.steps === 1 ? W.card : W.cards}`, m.hours && fmtHrs(m.hours) + ' window', m.crew && m.crew + ' crew', st.hrs && fmtHrs(st.hrs) + ` of ${W.card} time`];
    return parts.filter(Boolean).map(esc).join(' · ');
  }
  const pkgText = b => [b.name, b.meta && b.meta.area, b.meta && b.meta.desc, ...Object.values(b.notes).map(n => n.text + ' ' + (n.owner || '') + ' ' + (P.searchText ? P.searchText(n) : '')), ...b.frames.map(f => f.title)].join(' ').toLowerCase();

  function renderLibrary(){
    libDirty = false;
    const q = libSearch.value.trim().toLowerCase();
    const all = app.order.map(id => app.boards[id]).filter(Boolean);
    const shown = all.filter(b => !q || pkgText(b).includes(q));
    const byName = (a, b) => a.name.localeCompare(b.name, undefined, { numeric:true });
    const mine = shown.filter(b => !(b.meta && b.meta.example)).sort(byName);
    const ex = shown.filter(b => b.meta && b.meta.example).sort(byName);
    $('libCount').textContent = `${all.length} ${all.length === 1 ? W.board : W.boards}`;
    libGrid.textContent = '';

    const section = (title, list, emptyMsg, extra) => {
      const s = el('section', 'lib-sec');
      const h = el('div', 'lib-sh'); h.appendChild(el('h3', '', title));
      if (extra) h.appendChild(extra);
      s.appendChild(h);
      const g = el('div', 'lib-grid');
      list.forEach(b => g.appendChild(pkgCard(b)));
      if (!list.length && emptyMsg) g.appendChild(emptyMsg);
      s.appendChild(g);
      libGrid.appendChild(s);
    };

    section(T.yours, mine, q ? el('div', 'lib-none', 'No matches.') : null);
    if (!q){
      const make = el('button', 'pkg pkg-new');
      make.innerHTML = `<span class="pn-plus">${MMIcons.svg('plus', 'sm')}</span><b>Create your own</b><span>${esc(T.makeOwn)}</span>`;
      make.addEventListener('click', e => { e.stopPropagation(); openNewMenu(e.currentTarget); });
      libGrid.lastChild.querySelector('.lib-grid').appendChild(make);
    }
    let restore = null;
    const EX = P.examples || [];
    const missing = EX.filter(x => !app.boards[x.id]);
    if (missing.length && (!cloud.on || (cloud.edit && !P.seedCloud))){
      restore = el('button', 'lib-link', `Restore ${missing.length === EX.length ? 'the examples' : missing.length + ' missing example' + (missing.length > 1 ? 's' : '')}`);
      restore.addEventListener('click', () => { seedExamples(true); toast('Examples restored'); });
    }
    if (ex.length || restore || !q) section('Examples', ex, q ? el('div', 'lib-none', 'No matches.') : null, restore);
  }

  function pkgCard(b){
    const st = pkgStats(b), m = b.meta || {};
    const c = el('div', 'pkg'); c.tabIndex = 0; c.setAttribute('role', 'button');
    c.dataset.id = b.id;
    const top = el('div', 'pkg-top');
    if (m.area){ const a = el('span', 'pill', m.area); a.style.setProperty('--sc', areaColor(m.area)); top.appendChild(a); }
    // examples already sit under their own "Examples" heading, so the card doesn't repeat it
    const more = el('button', 'pkg-more', '⋯'); more.title = 'More'; more.setAttribute('aria-label', 'More actions');
    more.addEventListener('click', ev => { ev.stopPropagation(); openPkgMenu(more, b.id); });
    top.appendChild(more);
    c.appendChild(top);
    c.appendChild(el('div', 'pkg-title', b.name));
    if (m.desc) c.appendChild(el('div', 'pkg-desc', m.desc));
    const meta = el('div', 'meta');
    if (P.cardChips) P.cardChips(b, st, meta);
    else {
      meta.appendChild(el('span', 'chip', `${st.steps} ${st.steps === 1 ? W.card : W.cards}`));
      if (m.hours) meta.appendChild(chipI('chip', 'clock', fmtHrs(m.hours) + ' window'));
      if (m.crew) meta.appendChild(chipI('chip', 'users', String(m.crew)));
      if (st.checks) meta.appendChild(chipI('chip', 'checks', String(st.checks)));
    }
    c.appendChild(meta);
    if (st.phases.length){
      const t = el('div', 'tucked');
      st.phases.slice(0, 6).forEach(f => {
        const mm = el('div', 'mini pkg-ph'); mm.style.setProperty('--fc', f.color);
        const r = el('div', 'row'); r.appendChild(el('span', 'mt', f.title || T.frame));
        mm.appendChild(r); t.appendChild(mm);
      });
      if (st.phases.length > 6) t.appendChild(el('div', 'tbar', `+${st.phases.length - 6} ${T.moreFrames}`));
      c.appendChild(t);
    }
    c.addEventListener('click', () => openPackage(b.id));
    c.addEventListener('keydown', e => { if (e.key === 'Enter' && e.target === c){ e.preventDefault(); openPackage(b.id); } });
    c.addEventListener('contextmenu', e => { e.preventDefault(); openPkgMenu(null, b.id, e.clientX, e.clientY); });
    return c;
  }

  function placeMenu(anchor, x, y, h){
    if (anchor){ const r = anchor.getBoundingClientRect(); x = r.left; y = r.bottom + 6; }
    showMenu(Math.min(x, innerWidth - 240), Math.min(y, innerHeight - h - 12));
  }
  function openPkgMenu(anchor, id, x, y){
    closeMenu();
    const b = app.boards[id]; if (!b) return;
    mi('Open', () => openPackage(id), 'Enter');
    mi('Edit details…', () => openPkgInfo(id));
    mi('Duplicate', () => copyPackage(id));
    mi('Export to a file…', () => exportBoard(b));
    ms();
    mi(`Delete ${W.board}`, () => { if (confirm(`Delete “${b.name}”?\n\nYou can undo this right after.`)) deleteBoard(id); }, '', true);
    placeMenu(anchor, x, y, 200);
  }
  function openNewMenu(anchor){
    closeMenu();
    mi(T.newBoard, () => newPackage());
    const src = app.order.map(id => app.boards[id]).filter(Boolean).sort((a, b) => a.name.localeCompare(b.name));
    if (src.length){
      ms(); menu.appendChild(el('div', 'ml', 'Copy of…'));
      src.forEach(b => mi(b.name, () => copyPackage(b.id)));
    }
    ms();
    mi('Import from a file…', () => $('importFile').click());
    placeMenu(anchor, 0, 0, Math.min(460, 120 + src.length * 32));
  }

  function uniqueName(name){
    const names = new Set(Object.values(app.boards).map(b => b.name));
    if (!names.has(name)) return name;
    let i = 2; while (names.has(`${name} (${i})`)) i++;
    return `${name} (${i})`;
  }
  function newPackage(){
    const b = newBoard(uniqueName(T.newBoardName));
    b.meta = {}; b.created = new Date().toISOString(); b.seen = !P.onNewBoard;
    if (P.onNewBoard) P.onNewBoard(b);
    libChanged(); save();
    openPackage(b.id);
    openPkgInfo(b.id, true);
  }
  function copyPackage(id){
    const src = app.boards[id]; if (!src) return;
    const b = structuredClone({ ...src, pan:{ x:0, y:0 }, zoom:1 });
    b.id = bid(); b.name = uniqueName(src.name + ' (copy)');
    b.meta = { ...(src.meta || {}) }; delete b.meta.example;
    b.created = new Date().toISOString(); b.seen = false;
    app.boards[b.id] = b; app.order.push(b.id);
    libChanged(); save();
    toast(`Made “${b.name}” — it’s yours to change`, { label:'Open', fn:() => openPackage(b.id) });
    if (libEl.hidden) openPackage(b.id);
  }
  function deleteBoard(id){
    const board = app.boards[id], index = app.order.indexOf(id);
    if (!board) return;
    if (!LIB){
      deletedBoards.push({ board, index, seq:++seq });
      delete app.boards[id];
      app.order = app.order.filter(x => x !== id);
      B = null; switchBoard(app.order[Math.max(0, index - 1)]);
      toast(`Deleted “${board.name}”`, { label:'Undo', fn:restoreBoard });
      return;
    }
    deletedBoards.push({ board, index, seq:++seq });
    delete app.boards[id];
    app.order = app.order.filter(x => x !== id);
    if (B && B.id === id){ B = null; app.current = null; }
    if (!pkgDlg.hidden) pkgDlg.hidden = true;
    openLibrary(); save();
    toast(`Deleted “${board.name}”`, { label:'Undo', fn:restoreBoard });
  }

  /* ---- package details sheet ---- */
  let pkgId = null;
  const pf = { name:$('pkgName'), area:$('pkgArea'), hours:$('pkgHours'), crew:$('pkgCrew'), desc:$('pkgDesc') };
  if (LIB) $('pkgAreas').append(...AREAS.map(a => { const o = el('option'); o.value = a; return o; }));
  function openPkgInfo(id, fresh){
    const b = app.boards[id]; if (!b) return;
    closeMenu();
    pkgId = id; const m = b.meta || {};
    pf.name.value = b.name; pf.area.value = m.area || ''; pf.hours.value = m.hours || ''; pf.crew.value = m.crew || ''; pf.desc.value = m.desc || '';
    const st = pkgStats(b);
    $('pkgStats').textContent = P.statsLine ? P.statsLine(b, st)
      : `${st.steps} ${st.steps === 1 ? W.card : W.cards} · ${st.subs} ${st.subs === 1 ? W.sub : W.subs} · ${st.phases.length} phase${st.phases.length === 1 ? '' : 's'}${st.hrs ? ' · ' + fmtHrs(st.hrs) + ` of ${W.card} time` : ''}${st.checks ? ` · ${st.checks} checklist items` : ''}`;
    $('pkgExample').hidden = !m.example;
    pkgDisarm();
    pkgDlg.hidden = false;
    setTimeout(() => { (fresh ? pf.name : pf.name).focus(); if (fresh) pf.name.select(); }, 0);
  }
  function closePkgInfo(){
    if (pkgDlg.hidden) return;
    pkgDlg.hidden = true; pkgId = null;
    renderChrome(); libChanged();
  }
  function pkgEdit(){
    const b = app.boards[pkgId]; if (!b) return;
    const name = pf.name.value.trim();
    if (name) b.name = name;
    const m = { ...(b.meta || {}) };
    const set = (k, v) => { if (v) m[k] = v; else delete m[k]; };
    set('area', pf.area.value.trim()); set('desc', pf.desc.value.trim());
    const h = parseFloat(pf.hours.value); set('hours', isFinite(h) && h > 0 ? h : null);
    const c = parseInt(pf.crew.value, 10); set('crew', isFinite(c) && c > 0 ? c : null);
    b.meta = m;
    if (b === B) $('brandSub').textContent = b.name;
    save();
  }
  if (LIB){
  Object.values(pf).forEach(i => i.addEventListener('input', pkgEdit));
  [pf.name, pf.area, pf.hours, pf.crew].forEach(i => i.addEventListener('keydown', e => { if (e.key === 'Enter'){ e.preventDefault(); closePkgInfo(); } }));
  $('pkgDone').addEventListener('click', closePkgInfo);
  $('pkgClose').addEventListener('click', closePkgInfo);
  $('pkgDup').addEventListener('click', () => { const id = pkgId; closePkgInfo(); copyPackage(id); });
  pkgDlg.addEventListener('pointerdown', e => { if (e.target === pkgDlg) closePkgInfo(); });
  }
  let pkgArmT = null;
  const pkgDel = $('pkgDelete');
  function pkgDisarm(){ clearTimeout(pkgArmT); pkgDel.classList.remove('armed'); pkgDel.textContent = `Delete ${W.board}`; }
  if (LIB){
  pkgDel.addEventListener('click', () => {
    if (!pkgDel.classList.contains('armed')){ pkgDel.classList.add('armed'); pkgDel.textContent = 'Click again to delete'; pkgArmT = setTimeout(pkgDisarm, 3000); return; }
    const id = pkgId; pkgDisarm(); closePkgInfo(); deleteBoard(id);
  });

  $('libBtn').addEventListener('click', openLibrary);
  $('infoBtn').addEventListener('click', () => B && openPkgInfo(B.id));
  $('libNew').addEventListener('click', e => { e.stopPropagation(); openNewMenu(e.currentTarget); });
  libSearch.addEventListener('input', renderLibrary);
  libSearch.addEventListener('keydown', e => { if (e.key === 'Escape' && libSearch.value){ e.stopPropagation(); libSearch.value = ''; renderLibrary(); } });
  }

  /* ================= Tabs shell (Whiteboard) ================= */
    function renderTabs(){
    $('brandSub').textContent = B.name;
    const t = $('tabs'); t.textContent = '';
    if (app.order.length > 1){
      const all = el('button', 'ib'); all.appendChild(I('down', 'sm')); all.title = 'All boards';
      all.addEventListener('click', ev => {
        ev.stopPropagation(); closeMenu();
        menu.appendChild(el('div', 'ml', 'Boards'));
        app.order.forEach(id => mi((id === B.id ? '✓ ' : '\u2003') + app.boards[id].name, () => switchBoard(id)));
        const r = all.getBoundingClientRect(); showMenu(r.left, r.top - 8 - Math.min(400, 36 + app.order.length * 32));
      });
      t.appendChild(all);
    }
    for (const id of app.order){
      const b = app.boards[id]; if (!b) continue;
      const tab = el('div', 'tab' + (b.id === B.id ? ' active' : ''));
      tab.setAttribute('role', 'button'); tab.tabIndex = 0;
      tab.appendChild(el('span', '', b.name));
      tab.title = b.id === B.id ? 'Double-click to rename' : 'Switch board';
      tab.addEventListener('click', () => switchBoard(b.id));
      tab.addEventListener('dblclick', () => renameTab(tab, b));
      if (b.id === B.id && app.order.length > 1){
        const x = el('button', 'tx'); x.appendChild(I('x')); x.title = 'Delete board';
        x.addEventListener('click', ev => {
          ev.stopPropagation();
          if (!x.classList.contains('armed')){ x.classList.add('armed'); x.textContent = 'Delete?'; setTimeout(() => { x.classList.remove('armed'); x.textContent = ''; x.appendChild(I('x')); }, 2500); return; }
          deleteBoard(b.id);
        });
        tab.appendChild(x);
      }
      t.appendChild(tab);
    }
    const add = el('button', 'ib'); add.appendChild(I('plus', 'sm')); add.title = 'New board'; add.setAttribute('aria-label', 'New board');
    add.addEventListener('click', ev => {
      ev.stopPropagation(); closeMenu();
      menu.appendChild(el('div', 'ml', 'New board'));
      mi('Blank', () => newBoardFrom('blank'));
      const tpl = P.templates || [];
      tpl.forEach(t => mi(t.label, () => newBoardFrom(t.key)));
      const r = add.getBoundingClientRect(); showMenu(r.left, r.top - 58 - tpl.length * 36);
    });
    t.appendChild(add);
    const act = t.querySelector('.tab.active'); if (act && act.scrollIntoView) act.scrollIntoView({ block:'nearest', inline:'nearest' });
  }
    function renameTab(tab, b){
    tab.textContent = '';
    const inp = el('input'); inp.value = b.name; tab.appendChild(inp); inp.focus(); inp.select();
    let fin = false;
    const done = () => { if (fin) return; fin = true; const v = inp.value.trim(); if (v && v !== b.name){ if (b.id === B.id) checkpoint(); b.name = v; } renderTabs(); save(); };
    inp.addEventListener('keydown', e => { if (e.key === 'Enter') inp.blur(); if (e.key === 'Escape'){ inp.value = b.name; inp.blur(); } });
    inp.addEventListener('blur', done);
    inp.addEventListener('click', e => e.stopPropagation());
  }
  // A new tab, blank or from one of the page's templates ({ key, label, name, build(board, api) }).
  function newBoardFrom(kind){
    const t = (P.templates || []).find(x => x.key === kind);
    const existing = new Set(Object.values(app.boards).map(b => b.name));
    const base = t ? t.name : W.Board;
    let name = t ? base : `${W.Board} ${app.order.length + 1}`, i = 2;
    while (existing.has(name)) name = `${base} ${i++}`;
    const nb = newBoard(name);
    if (t) t.build(nb, api);
    switchBoard(nb.id);
    if (t) requestAnimationFrame(fitOnOpen);
  }
  // First time signed in to an empty organization: offer to bring over boards made in demo mode.
    async function offerLocalCopy(){
    if (!cloud.edit) return;
    const askKey = `mm-wb-copy-asked:${cloud.org.id}`;
    try { if (localStorage.getItem(askKey)) return; } catch (e) { return; }
    const orgHasContent = Object.values(app.boards).some(b => Object.keys(b.notes).length || b.frames.length);
    if (orgHasContent) return;
    let local = null;
    try { local = await store.get('app'); } catch (e) { return; }
    const list = local && local.order ? local.order.map(id => local.boards[id]).filter(b => b && Object.keys(b.notes || {}).length) : [];
    if (!list.length) return;
    try { localStorage.setItem(askKey, '1'); } catch (e) {}
    const n = list.reduce((t, b) => t + Object.keys(b.notes).length, 0);
    if (!confirm(`This browser has ${list.length} board${list.length === 1 ? '' : 's'} (${n} notes) saved from before you signed in.\n\nCopy ${list.length === 1 ? 'it' : 'them'} to ${cloud.org.name} so your team can see ${list.length === 1 ? 'it' : 'them'}?`)) return;
    const existing = new Set(Object.values(app.boards).map(b => b.name));
    for (const b of list){
      b.id = bid();
      if (existing.has(b.name)) b.name += ' (copied)';
      for (const n of Object.values(b.notes)) for (const a of (n.attachments || [])) delete a.path;
      fixBoard(b); b.sort = Date.now();
      app.boards[b.id] = b; app.order.push(b.id);
    }
    // Drop an untouched blank board the org started with, so the copied boards come first.
    for (const id of [...app.order]){ const b = app.boards[id]; if (!list.includes(b) && !Object.keys(b.notes).length && !b.frames.length && app.order.length > list.length) delete app.boards[id], app.order = app.order.filter(x => x !== id); }
    app.current = list[0].id;
    toast(`Copied ${list.length} board${list.length === 1 ? '' : 's'} to ${cloud.org.name}`);
  }

  /* ================= Export / import ================= */
  const BOARD_FILE = new RegExp('\\.(' + cfg.fileExt + '|whiteboard|json)$', 'i');
  function download(blob, name){
    try {
      const a = el('a'); a.href = URL.createObjectURL(blob); a.download = name;
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 4000);
      toast('Downloaded ' + name);
    } catch (e) { toast('Downloads are blocked here — open the page directly to export.'); }
  }
  const blobToDataURL = b => new Promise((res, rej) => { const r = new FileReader(); r.onload = () => res(r.result); r.onerror = rej; r.readAsDataURL(b); });
  function dataURLToBlob(u){
    const [h, d] = u.split(','); const mime = (/data:([^;]+)/.exec(h) || [])[1] || 'application/octet-stream';
    const bin = atob(d); const arr = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
    return new Blob([arr], { type:mime });
  }
  const fileStamp = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; };
  const safeName = s => (s || 'Board').replace(/[\\/:*?"<>|]+/g, '-').replace(/\s+/g, ' ').trim() || 'Board';
  async function exportBoard(Bd){
    Bd = Bd || B; if (!Bd) return;
    try {
      await ensureBlobs(Bd);
      const b = structuredClone(Bd);
      for (const n of Object.values(b.notes)) for (const a of n.attachments){ a.data = a.blob ? await blobToDataURL(a.blob) : null; delete a.blob; delete a.path; }
      delete b.pan; delete b.zoom; delete b.seen; if (b.meta) delete b.meta.example;
      const json = JSON.stringify({ app:cfg.appTag, kind:'board', version:VERSION, exported:new Date().toISOString(), board:b });
      download(new Blob([json], { type:'application/json' }), `${safeName(Bd.name)} – ${fileStamp()}.${cfg.fileExt}`);
    } catch (e) { toast('Export failed: ' + e.message); }
  }
  async function importFile(f){
    try {
      const data = JSON.parse(await f.text());
      const list = data.board ? [data.board] : data.boards || (data.notes ? [data] : null);
      if (!list || !list.length) throw new Error(`this isn’t a ${T.fileLabel} file`);
      let first = null;
      for (const b of list){
        if (!b.name) b.name = f.name.replace(BOARD_FILE, '');
        b.id = bid();                                   // always a fresh board, never someone else's id
        b.meta = b.meta || {}; delete b.meta.example; b.created = new Date().toISOString(); b.seen = false;
        b.pan = b.pan || { x:0, y:0 }; b.zoom = b.zoom || 1;
        const names = new Set(Object.values(app.boards).map(x => x.name));
        if (names.has(b.name)){ let i = 2; while (names.has(`${b.name} (${i})`)) i++; b.name = `${b.name} (${i})`; }
        for (const n of Object.values(b.notes || {})) for (const a of (n.attachments || [])){ delete a.path; if (a.data){ a.blob = dataURLToBlob(a.data); delete a.data; } }
        fixBoard(b); if (!LIB) b.sort = Date.now();
        app.boards[b.id] = b; app.order.push(b.id);
        first = first || b.id;
      }
      libChanged(); save(); showBoard(first);
      if (LIB) toast(list.length > 1 ? `Imported ${list.length} ${W.boards}` : `Imported “${app.boards[first].name}”`);
      else toast(list.length > 1 ? `Opened ${list.length} ${W.boards} in new tabs` : `Opened “${app.boards[first].name}” in a new tab`);
    } catch (err) { toast('Couldn’t open that file: ' + err.message); }
  }
  $('importFile').addEventListener('change', async e => {
    const files = [...e.target.files]; e.target.value = '';
    for (const f of files) await importFile(f);
  });

  async function boardPNG(){
    if (!window.htmlToImage) throw new Error('image library not loaded');
    sel.clear(); selLink = null; hideLinkPop(); render();
    const bb = contentBox(); if (!bb) throw new Error('board is empty');
    const pad = 40, W = Math.ceil(bb.w + pad*2), Hh = Math.ceil(bb.h + pad*2);
    return window.htmlToImage.toPng(world, {
      width:W, height:Hh, pixelRatio:Math.min(2, 4000 / Math.max(W, Hh)) || 1, backgroundColor:getComputedStyle(document.body).getPropertyValue('--bg').trim() || '#0f1113', skipFonts:true,
      style:{ transform:`translate(${-bb.x + pad}px,${-bb.y + pad}px)`, transformOrigin:'0 0' },
    });
  }
  async function exportPNG(){
    try { toast('Rendering image…'); const url = await boardPNG(); download(dataURLToBlob(url), `${safeName(B.name)}-${fileStamp()}.png`); }
    catch (e) { toast('Image export failed: ' + e.message); }
  }
  /* ---------- Print / PDF ---------- */
  const PAPERS = { letter:[8.5, 11], legal:[8.5, 14], tabloid:[11, 17], a4:[8.27, 11.69], a3:[11.69, 16.54] };
  const MARGINS = { narrow:.25, normal:.5, wide:.75 };
  const PO_DEFAULT = { kind:'picture', paper:'letter', orient:'auto', margin:'normal', area:'board', tiles:'1x1',
    arrows:true, grid:false, header:true, pageNums:true, ink:false,
    rGroup:true, rChecks:true, rDone:true, rLinks:true, rSize:'m', rCols:'1' };
  let po = { ...PO_DEFAULT };
  const PX = 96;   // CSS px per inch

  function openPrint(){
    closeMenu(); hideLinkPop();
    po = { ...PO_DEFAULT, ...(app.printOpts || {}) };
    if (po.area === 'selection' && !sel.size) po.area = 'board';
    if (po.area === 'frames' && !B.frames.length) po.area = 'board';
    $('printDlg').hidden = false;
    paintPrint();
  }
  function closePrint(){ $('printDlg').hidden = true; $('pdStage').textContent = ''; }

  function syncOpts(){
    const box = $('pdOpts');
    box.querySelectorAll('.seg[data-k]').forEach(sg => { for (const b of sg.children) b.classList.toggle('on', String(po[sg.dataset.k]) === b.dataset.v); });
    box.querySelectorAll('select[data-k]').forEach(x => { x.value = po[x.dataset.k]; });
    box.querySelectorAll('input[type=checkbox][data-k]').forEach(x => { x.checked = !!po[x.dataset.k]; });
    box.querySelectorAll('[data-only]').forEach(x => { x.hidden = x.dataset.only !== po.kind; });
    const areaSel = box.querySelector('select[data-k=area]');
    areaSel.querySelector('option[value=frames]').disabled = !B.frames.length;
    areaSel.querySelector('option[value=selection]').disabled = !sel.size;
    $('pdTilesRow').style.opacity = po.area === 'frames' ? .45 : 1;
    box.querySelector('select[data-k=tiles]').disabled = po.area === 'frames';
  }
  $('pdOpts').addEventListener('click', e => {
    const b = e.target.closest('.seg[data-k] button'); if (!b) return;
    po[b.parentElement.dataset.k] = b.dataset.v; app.printOpts = { ...po }; save(); paintPrint();
  });
  $('pdOpts').addEventListener('change', e => {
    const x = e.target; if (!x.dataset.k) return;
    po[x.dataset.k] = x.type === 'checkbox' ? x.checked : x.value; app.printOpts = { ...po }; save(); paintPrint();
  });

  function pageSize(landscape){ const [w, h] = PAPERS[po.paper]; return landscape ? [h, w] : [w, h]; }

  // What areas of the board to print: [{ bb, sub, cols, rows }]
  function pictureJobs(){
    const pad = 20;
    const padBox = r => ({ x:r.x - pad, y:r.y - pad, w:r.w + pad*2, h:r.h + pad*2 });
    const [cols, rows] = po.tiles.split('x').map(Number);
    if (po.area === 'frames' && B.frames.length){
      return [...B.frames].sort((a, b) => (a.y - b.y) || (a.x - b.x)).map(f => ({ bb:padBox({ x:f.x, y:f.y, w:f.w, h:f.h }), sub:f.title, cols:1, rows:1, only:new Set(notesInFrame(f).map(n => n.id)), frameId:f.id }));
    }
    if (po.area === 'view'){
      const r = board.getBoundingClientRect();
      const a = toWorld(r.left, r.top), z = toWorld(r.right, r.bottom);
      return [{ bb:{ x:a.x, y:a.y, w:z.x - a.x, h:z.y - a.y }, sub:'', cols, rows }];
    }
    if (po.area === 'selection' && sel.size){
      const rs = [...sel].map(id => noteEl(id)).filter(Boolean).map(worldRect);
      const x1 = Math.min(...rs.map(r => r.x)), y1 = Math.min(...rs.map(r => r.y)), x2 = Math.max(...rs.map(r => r.x + r.w)), y2 = Math.max(...rs.map(r => r.y + r.h));
      return [{ bb:padBox({ x:x1, y:y1, w:x2 - x1, h:y2 - y1 }), sub:'Selected notes', cols, rows, only:new Set(sel) }];
    }
    const bb = contentBox();
    return bb ? [{ bb:padBox(bb), sub:'', cols, rows }] : [];
  }

  function cleanClone(pageNo, only, frameId){
    const c = world.cloneNode(true);
    c.removeAttribute('id'); c.className = 'pworld'; c.style.transform = '';
    c.querySelectorAll('.rz, .lh, .frz, .lk-hit, .tmp, #tmpLink').forEach(e => e.remove());
    c.querySelectorAll('.selected, .hit, .dim, .editing, .expanded, .link-target, .file-over').forEach(e => e.classList.remove('selected', 'hit', 'dim', 'editing', 'expanded', 'link-target', 'file-over'));
    c.querySelectorAll('[id]').forEach(e => { e.id = e.id + '-p' + pageNo; });
    c.querySelectorAll('[marker-end]').forEach(e => e.setAttribute('marker-end', e.getAttribute('marker-end').replace(/#(\w+)\)/, `#$1-p${pageNo})`)));
    if (!po.arrows){ c.querySelectorAll('.link-label').forEach(e => e.remove()); const g = c.querySelector('g'); if (g) g.textContent = ''; }
    if (only){
      c.querySelectorAll(':scope > .note').forEach(e => { if (!only.has(e.dataset.id)) e.remove(); });
      c.querySelectorAll(':scope > .frame').forEach(e => { if (e.dataset.id !== frameId) e.remove(); });
      c.querySelectorAll('.lk, .link-label').forEach(e => { if (!only.has(e.dataset.from) || !only.has(e.dataset.to)) e.remove(); });
    }
    return c;
  }

  // Build print pages for the board picture. Returns { pages:[el], W, H }
  function buildPicturePages(){
    const jobs = pictureJobs();
    if (!jobs.length) return { pages:[], W:0, H:0 };
    let landscape;
    if (po.orient === 'auto'){
      let votes = 0;
      jobs.forEach(j => { if ((j.bb.w / j.cols) >= (j.bb.h / j.rows)) votes++; });
      landscape = votes * 2 >= jobs.length;
    } else landscape = po.orient === 'landscape';
    const [W, H] = pageSize(landscape);
    const m = MARGINS[po.margin];
    const hdr = po.header ? .42 : 0, ftr = po.pageNums ? .3 : 0;
    const cw = (W - 2*m) * PX, ch = (H - 2*m - hdr - ftr) * PX;
    const total = jobs.reduce((s, j) => s + j.cols * j.rows, 0);
    const date = new Date().toLocaleDateString(undefined, { dateStyle:'medium' });
    const pages = [];
    let no = 0;
    for (const j of jobs){
      let s = Math.min(cw * j.cols / j.bb.w, ch * j.rows / j.bb.h);
      if (po.area !== 'view') s = Math.min(s, 1.6);
      const tw = cw / s, th = ch / s;
      const ox0 = j.bb.x - (j.cols * tw - j.bb.w) / 2, oy0 = j.bb.y - (j.rows * th - j.bb.h) / 2;
      for (let r = 0; r < j.rows; r++) for (let c = 0; c < j.cols; c++){
        no++;
        const pg = el('div', 'ppage' + (po.ink ? ' ink' : ''));
        pg.style.width = W + 'in'; pg.style.height = H + 'in';
        if (po.header){
          const ph = el('div', 'ph');
          ph.style.left = ph.style.right = m + 'in'; ph.style.top = m + 'in';
          const tile = j.cols * j.rows > 1 ? `  ·  part ${r * j.cols + c + 1} of ${j.cols * j.rows}` : '';
          ph.appendChild(el('b', '', B.name + (j.sub ? ' — ' + j.sub : '') + tile));
          ph.appendChild(el('span', '', date));
          pg.appendChild(ph);
        }
        const vp = el('div', 'pvp' + (po.grid ? ' grid' : ''));
        vp.style.left = m + 'in'; vp.style.top = (m + hdr) + 'in';
        vp.style.width = cw + 'px'; vp.style.height = ch + 'px';
        const ox = ox0 + c * tw, oy = oy0 + r * th;
        if (po.grid){ vp.style.backgroundSize = `${24 * s}px ${24 * s}px`; vp.style.backgroundPosition = `${-ox * s}px ${-oy * s}px`; }
        const cl = cleanClone(no, j.only, j.frameId);
        cl.style.transform = `scale(${s}) translate(${-ox}px,${-oy}px)`;
        vp.appendChild(cl);
        pg.appendChild(vp);
        if (po.pageNums){
          const pf = el('div', 'pf');
          pf.style.left = pf.style.right = m + 'in'; pf.style.bottom = m + 'in';
          pf.appendChild(el('span', '', 'Machine Manager · ' + cfg.title));
          pf.appendChild(el('span', '', `Page ${no} of ${total}`));
          pg.appendChild(pf);
        }
        pages.push(pg);
      }
    }
    return { pages, W, H, landscape };
  }

  function buildReportPage(){
    const landscape = po.orient === 'landscape';
    const [W, H] = pageSize(landscape);
    const m = MARGINS[po.margin];
    const pg = el('div', 'rpage' + (po.ink ? ' ink' : ''));
    pg.style.width = W + 'in'; pg.style.minHeight = H + 'in'; pg.style.padding = m + 'in';
    let h = '';
    if (po.header) h += `<div class="rhead"><b>${esc(B.name)}</b><span>Printed ${esc(new Date().toLocaleString(undefined, { dateStyle:'medium', timeStyle:'short' }))}</span></div>`;
    pg.innerHTML = h + reportHTML(po);
    return { pages:[pg], W, H, landscape };
  }

  function paintPrint(){
    syncOpts();
    const stage = $('pdStage'); stage.textContent = '';
    const out = po.kind === 'report' ? buildReportPage() : buildPicturePages();
    if (!out.pages.length){ stage.appendChild(el('div', 'kbd-hint', po.area === 'selection' ? 'Select some notes first.' : T.printEmpty)); $('pdCount').textContent = ''; $('pdPrint').disabled = true; return; }
    $('pdPrint').disabled = false;
    const stageW = Math.max(300, stage.clientWidth - 40);
    const k = Math.min(1, stageW / (out.W * PX), po.kind === 'picture' ? (stage.clientHeight - 40) / (out.H * PX) : 1);
    for (const pg of out.pages){
      const wrap = el('div', 'pwrap');
      wrap.appendChild(pg);
      pg.style.transform = `scale(${k})`;
      stage.appendChild(wrap);
      const h = po.kind === 'report' ? pg.offsetHeight : out.H * PX;
      wrap.style.width = (out.W * PX * k) + 'px'; wrap.style.height = (h * k) + 'px';
      if (po.kind === 'report'){
        const m = MARGINS[po.margin] * PX * k, step = (out.H * PX - 2 * MARGINS[po.margin] * PX) * k;
        for (let y = m + step, i = 1; y < h * k - 4; y += step, i++){
          const g = el('div', 'pbreak', `page ${i + 1}`); g.style.top = y + 'px'; wrap.appendChild(g);
        }
      }
    }
    const [pw, ph] = PAPERS[po.paper];
    const paperName = $('pdOpts').querySelector('select[data-k=paper] option:checked').textContent.split(' (')[0];
    $('pdCount').textContent = po.kind === 'report' ? 'Report — dashed lines show about where pages break' : `${out.pages.length} page${out.pages.length > 1 ? 's' : ''}`;
    $('pdNote').textContent = `${paperName}, ${out.landscape ? 'landscape' : 'portrait'}`;
    paintPrint.last = out;
  }
  window.addEventListener('resize', () => { if (!$('printDlg').hidden) paintPrint(); });

  $('pdClose').addEventListener('click', closePrint);
  $('pdCancel').addEventListener('click', closePrint);
  $('printDlg').addEventListener('pointerdown', e => { if (e.target.id === 'printDlg') closePrint(); });
  $('pdPrint').addEventListener('click', () => {
    const out = po.kind === 'report' ? buildReportPage() : buildPicturePages();
    if (!out.pages.length) return;
    const area = $('printArea'); area.textContent = '';
    out.pages.forEach(p => area.appendChild(p));
    const m = MARGINS[po.margin];
    let css = `@page{size:${out.W}in ${out.H}in;margin:${po.kind === 'report' ? m + 'in' : '0'}}`;
    if (po.kind === 'report' && po.pageNums) css = `@page{size:${out.W}in ${out.H}in;margin:${m}in;@bottom-right{content:"Page " counter(page) " of " counter(pages);font:9px Inter,system-ui,sans-serif;color:#78716c}}`;
    $('pageStyle').textContent = css;
    const imgs = [...area.querySelectorAll('img')].filter(i => !i.complete);
    const go = () => { try { window.print(); } catch (e) { toast('Printing isn’t available here.'); } };
    if (imgs.length) Promise.all(imgs.map(i => i.decode().catch(() => {}))).then(go); else go();
  });
  window.addEventListener('afterprint', () => { $('printArea').textContent = ''; });

  function reportHTML(o){
    o = o || PO_DEFAULT;
    const all = Object.values(B.notes);
    const done = all.filter(n => n.status === 'done').length, late = all.filter(isLate).length;
    const rects = {};
    for (const n of tops()){ const e = noteEl(n.id); rects[n.id] = e ? worldRect(e) : { x:n.x, y:n.y, w:DEFAULT_W, h:100 }; }
    const inFrame = (f, id) => { const r = rects[id]; const cx = r.x + r.w/2, cy = r.y + r.h/2; return cx >= f.x && cx <= f.x + f.w && cy >= f.y && cy <= f.y + f.h; };
    const byPos = (a, b) => (rects[a.id].y - rects[b.id].y) || (rects[a.id].x - rects[b.id].x);
    const used = new Set();
    const lineHTML = s => {
      let m;
      if ((m = /^(\s*)[-*] \[( |x|X)\] ?(.*)$/.exec(s))){ if (!o.rChecks) return ''; return `<div class="rl" style="padding-left:${lineIndent(m[1])*14}px">${m[2] !== ' ' ? '☑' : '☐'} ${inline(m[3])}</div>`; }
      if ((m = /^(\s*)[-*] (.*)$/.exec(s))) return `<div class="rl" style="padding-left:${lineIndent(m[1])*14}px">• ${inline(m[2])}</div>`;
      return s.trim() ? `<div class="rl">${inline(s)}</div>` : '';
    };
    const noteHTML = n => {
      const { title, rest } = parseText(n.text);
      const st = STATUSES[n.status];
      const meta = [];
      if (n.owner) meta.push(W.owner + ': ' + esc(n.owner));
      if (n.due) meta.push(isLate(n) ? `<span class="late">Due ${esc(fmtDue(n.due))} — overdue</span>` : 'Due ' + esc(fmtDue(n.due)));
      if (fmtHrs(n.hrs)) meta.push('Time: ' + fmtHrs(n.hrs));
      const ck = checklist(n.text); if (ck.total) meta.push(`Checklist ${ck.done}/${ck.total}`);
      let h = `<div class="rn" style="--nc:${n.color === '#ffffff' ? '#d6d3d1' : n.color}">`;
      h += `<div class="rt">${title ? inline(title) : '<i>Untitled</i>'}${st ? `<span class="rs" style="color:${st.c}">● ${st.label}</span>` : ''}</div>`;
      if (meta.length) h += `<div class="rm">${meta.join(' · ')}</div>`;
      if (P.reportNote) h += P.reportNote(n);
      h += rest.map(r => lineHTML(r.s)).join('');
      if (n.attachments.length) h += `<div class="ra">📎 ${n.attachments.map(a => esc(a.name)).join(', ')}</div>`;
      h += n.children.map(c => N(c) && keep(N(c)) ? noteHTML(N(c)) : '').join('');
      return h + '</div>';
    };
    const keep = n => o.rDone || n.status !== 'done';
    let out = `<div class="rep sz-${o.rSize || 'm'}${o.rCols == 2 ? ' cols2' : ''}"><div class="sum">${LIB ? pkgSummary(B) : `${all.length} notes · ${done} done${late ? ` · <b style="color:var(--bad-ink)">${late} overdue</b>` : ''}${B.links.length ? ` · ${B.links.length} connections` : ''}`}</div>${B.meta && B.meta.desc ? `<div class="rm" style="margin-bottom:8px">${esc(B.meta.desc)}</div>` : ''}`;
    const frames = o.rGroup ? [...B.frames].sort((a, b) => (a.y - b.y) || (a.x - b.x)) : [];
    for (const f of frames){
      const ns = tops().filter(n => !used.has(n.id) && inFrame(f, n.id)).sort(byPos);
      ns.forEach(n => used.add(n.id));
      const shown = ns.filter(keep);
      out += `<h2 style="--fc:${f.color}">${esc(f.title || 'Frame')}</h2>` + (shown.length ? shown.map(noteHTML).join('') : `<div class="rm">No ${W.cards}</div>`);
    }
    const rest = tops().filter(n => !used.has(n.id) && keep(n)).sort(byPos);
    if (rest.length) out += (frames.length ? `<h2>Other ${W.cards}</h2>` : '') + rest.map(noteHTML).join('');
    if (!all.length) out += `<div class="rm">${esc(T.reportEmpty)}</div>`;
    if (o.rLinks && B.links.length){
      const nm = id => esc(parseText(N(id)?.text).title || 'Untitled');
      out += '<h2>Connections</h2><ul class="links">' + B.links.filter(l => N(l.from) && N(l.to)).map(l => `<li>${nm(l.from)} → ${nm(l.to)}${l.label ? ` — <i>${esc(l.label)}</i>` : ''}</li>`).join('') + '</ul>';
    }
    return out + '</div>';
  }

  /* ================= Frames ================= */
  let frPtr = null, frRsz = null;
  function buildFrame(f){
    const e = el('div', 'frame');
    e.dataset.id = f.id;
    e.style.left = f.x + 'px'; e.style.top = f.y + 'px'; e.style.width = f.w + 'px'; e.style.height = f.h + 'px';
    e.style.setProperty('--fc', f.color);
    const fh = el('div', 'fh');
    fh.appendChild(el('span', 'ft', f.title || 'Frame'));
    fh.title = 'Drag to move with its notes · double-click to rename';
    fh.addEventListener('pointerdown', ev => startFrame(ev, f.id));
    fh.addEventListener('dblclick', ev => { ev.stopPropagation(); renameFrame(f.id); });
    const rz = el('div', 'frz'); rz.title = 'Drag to resize';
    rz.addEventListener('pointerdown', ev => startFrameResize(ev, f.id));
    e.append(fh, rz);
    return e;
  }
  const F = id => B.frames.find(f => f.id === id);
  const frameEl = id => world.querySelector(`.frame[data-id="${id}"]`);
  function createFrame(x, y, extra){
    checkpoint();
    const f = Object.assign({ id:uid(), x:snapV(x), y:snapV(y), w:528, h:360, title:'Frame', color:FRAME_COLORS[B.frames.length % FRAME_COLORS.length] }, extra || {});
    B.frames.push(f);
    render(); save();
    renameFrame(f.id, true);
    return f;
  }
  function newFrameInView(){ const c = viewCenter(); createFrame(c.x - 264, c.y - 180); }
  function renameFrame(id, fresh){
    const f = F(id), fe = frameEl(id); if (!f || !fe) return;
    const fh = fe.querySelector('.fh'); fh.textContent = '';
    const inp = el('input'); inp.value = f.title; fh.appendChild(inp); inp.focus(); inp.select();
    inp.addEventListener('pointerdown', e => e.stopPropagation());
    let fin = false;
    const done = () => { if (fin) return; fin = true; const v = inp.value.trim(); if (v && v !== f.title){ if (!fresh) checkpoint(); f.title = v; } render(); save(); };
    inp.addEventListener('keydown', e => { e.stopPropagation(); if (e.key === 'Enter' || e.key === 'Escape') inp.blur(); });
    inp.addEventListener('blur', done);
  }
  function notesInFrame(f){
    return tops().filter(n => { const e = noteEl(n.id); if (!e) return false; const r = worldRect(e), cx = r.x + r.w/2, cy = r.y + r.h/2; return cx >= f.x && cx <= f.x + f.w && cy >= f.y && cy <= f.y + f.h; });
  }
  function startFrame(e, id){
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    if (e.target.closest('input') || linkMode) return;
    e.preventDefault(); e.stopPropagation(); closeMenu(); hideLinkPop();
    frPtr = { id, sx:e.clientX, sy:e.clientY, moved:false };
  }
  function moveFrame(e){
    if (!frPtr.moved){
      if (Math.hypot(e.clientX - frPtr.sx, e.clientY - frPtr.sy) < 4) return;
      checkpoint();
      const f = F(frPtr.id);
      frPtr.moved = true; frPtr.start = toWorld(frPtr.sx, frPtr.sy); frPtr.x0 = f.x; frPtr.y0 = f.y;
      frPtr.notes = notesInFrame(f).map(n => ({ n, x0:n.x, y0:n.y, el:noteEl(n.id) }));
      frPtr.el = frameEl(f.id); frPtr.el.classList.add('moving');
      document.body.classList.add('is-dragging');
    }
    const f = F(frPtr.id), w = toWorld(e.clientX, e.clientY);
    f.x = snapV(frPtr.x0 + w.x - frPtr.start.x); f.y = snapV(frPtr.y0 + w.y - frPtr.start.y);
    const dx = f.x - frPtr.x0, dy = f.y - frPtr.y0;
    frPtr.el.style.left = f.x + 'px'; frPtr.el.style.top = f.y + 'px';
    for (const o of frPtr.notes){ o.n.x = o.x0 + dx; o.n.y = o.y0 + dy; o.el.style.left = o.n.x + 'px'; o.el.style.top = o.n.y + 'px'; }
    scheduleLinks();
  }
  function endFrame(){
    const p = frPtr; frPtr = null;
    document.body.classList.remove('is-dragging');
    if (p.moved){ p.el.classList.remove('moving'); save(); drawLinks(); }
  }
  function startFrameResize(e, id){
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    e.preventDefault(); e.stopPropagation();
    checkpoint();
    const f = F(id);
    frRsz = { id, sx:e.clientX, sy:e.clientY, w:f.w, h:f.h, el:frameEl(id) };
    document.body.classList.add('is-resizing');
  }
  function moveFrameResize(e){
    const f = F(frRsz.id);
    f.w = snapV(Math.max(200, frRsz.w + (e.clientX - frRsz.sx) / B.zoom));
    f.h = snapV(Math.max(140, frRsz.h + (e.clientY - frRsz.sy) / B.zoom));
    frRsz.el.style.width = f.w + 'px'; frRsz.el.style.height = f.h + 'px';
  }
  function deleteFrame(id, withNotes){
    const f = F(id); if (!f) return;
    checkpoint();
    if (withNotes) notesInFrame(f).forEach(n => removeNote(n.id));
    B.frames = B.frames.filter(x => x.id !== id);
    render(); save();
  }
  function openFrameMenu(x, y, id){
    closeMenu(); hideLinkPop();
    const f = F(id); if (!f) return;
    mi('Rename', () => renameFrame(id));
    mi('Select notes in frame', () => { sel.clear(); notesInFrame(f).forEach(n => sel.add(n.id)); syncSelClasses(); });
    mi('Fit frame to its notes', () => {
      const ns = notesInFrame(f); if (!ns.length) return;
      checkpoint();
      const rs = ns.map(n => worldRect(noteEl(n.id)));
      const x1 = Math.min(...rs.map(r => r.x)), y1 = Math.min(...rs.map(r => r.y)), x2 = Math.max(...rs.map(r => r.x + r.w)), y2 = Math.max(...rs.map(r => r.y + r.h));
      f.x = Math.round(x1 - 24); f.y = Math.round(y1 - 56); f.w = Math.round(x2 - x1 + 48); f.h = Math.round(y2 - y1 + 80);
      render(); save();
    });
    ms();
    if (SHOW_COLORS){
      menu.appendChild(el('div', 'ml', 'Color'));
      const row = el('div', 'mrow');
      FRAME_COLORS.forEach(c => {
        const b = el('button', 'sw' + (f.color === c ? ' on' : '')); b.style.background = c;
        b.addEventListener('click', () => { checkpoint(); f.color = c; closeMenu(); render(); save(); });
        row.appendChild(b);
      });
      menu.appendChild(row);
      ms();
    }
    mi('Delete frame (keep notes)', () => deleteFrame(id, false), '', true);
    mi('Delete frame and its notes', () => deleteFrame(id, true), '', true);
    showMenu(x, y);
  }

  // The page's example boards (P.examples / P.buildExample). Pages with P.seedCloud set up something else
  // for a signed-in organization instead (real data only).
  function seedExamples(force){
    if (app.seeded && !force) return;
    if (cloud.on && P.seedCloud) P.seedCloud();
    else for (const x of (P.examples || [])){
      if (app.boards[x.id]) continue;
      const b = P.buildExample(x);
      app.boards[b.id] = b; app.order.push(b.id);
    }
    app.seeded = app.seeded || new Date().toISOString();
    libChanged(); save();
  }

  /* ================= Toolbar wiring ================= */
  function selectAll(){ tops().forEach(n => sel.add(n.id)); syncSelClasses(); }
  function toggleSnap(){ app.snap = !app.snap; $('snapBtn').classList.toggle('on', app.snap); toast(app.snap ? 'Snap to grid on' : 'Snap to grid off'); save(); }
  $('newBtn').addEventListener('click', newNoteInView);
  $('frameBtn').addEventListener('click', newFrameInView);
  $('tipsOk').addEventListener('click', () => { $('tips').hidden = true; app.tipsSeen = true; save(); });
  $('undoBtn').addEventListener('click', undo);
  $('redoBtn').addEventListener('click', redo);
  $('snapBtn').addEventListener('click', toggleSnap);
  $('helpBtn').addEventListener('click', () => $('help').hidden = false);
  $('helpClose').addEventListener('click', () => $('help').hidden = true);
  $('help').addEventListener('pointerdown', e => { if (e.target.id === 'help') $('help').hidden = true; });
  $('zoomIn').addEventListener('click', () => zoomCenter(z => z * 1.2));
  $('zoomOut').addEventListener('click', () => zoomCenter(z => z / 1.2));
  $('zoomPct').addEventListener('click', () => zoomCenter(() => 1));
  $('fitBtn').addEventListener('click', () => fitAll());

  /* ================= Keyboard ================= */
  let pendingPaste = null;
  document.addEventListener('keydown', e => {
    const mod = e.ctrlKey || e.metaKey;
    if (LIB && !pkgDlg.hidden){ if (e.key === 'Escape') closePkgInfo(); return; }
    if (LIB && !libEl.hidden){
      if (e.key === 'Escape' && !menu.hidden){ closeMenu(); return; }
      if (e.key === 'Escape' && B && !typing()){ closeLibrary(); return; }
      if ((e.key === '/' && !typing()) || (mod && e.key.toLowerCase() === 'f')){ e.preventDefault(); libSearch.focus(); libSearch.select(); return; }
      if (mod && e.key.toLowerCase() === 'o'){ e.preventDefault(); $('importFile').click(); }
      return;
    }
    if (e.key === 'Escape'){
      if (linkMode){ cancelLink(); return; }
      if (!menu.hidden){ closeMenu(); return; }
      if (!lb.hidden){ lb.hidden = true; return; }
      if (!$('help').hidden){ $('help').hidden = true; return; }
      if (!$('printDlg').hidden){ closePrint(); return; }
      if (!modal.hidden){ closeEditor(); return; }
      if (!linkPop.hidden){ hideLinkPop(); return; }
      if (search.value && document.activeElement !== search){ search.value = ''; applySearch(); return; }
      clearSel(); return;
    }
    if (e.key === 'Escape' && !$('printDlg').hidden){ closePrint(); return; }
    if (!modal.hidden || !$('help').hidden || !$('printDlg').hidden) return;
    if (mod && e.key.toLowerCase() === 'f'){ e.preventDefault(); search.focus(); search.select(); return; }
    if (mod && e.key.toLowerCase() === 's'){ e.preventDefault(); exportBoard(); return; }
    if (mod && e.key.toLowerCase() === 'o'){ e.preventDefault(); $('importFile').click(); return; }
    if (mod && e.key.toLowerCase() === 'p'){ e.preventDefault(); openPrint(); return; }
    if (typing()) return;
    const k = e.key;
    if (mod && k.toLowerCase() === 'z'){ e.preventDefault(); e.shiftKey ? redo() : undo(); return; }
    if (mod && k.toLowerCase() === 'y'){ e.preventDefault(); redo(); return; }
    if (mod && k.toLowerCase() === 'a'){ e.preventDefault(); selectAll(); return; }
    if (mod && k.toLowerCase() === 'd'){ e.preventDefault(); duplicate([...sel]); return; }
    if (mod && k.toLowerCase() === 'c'){ copySel(); return; }
    if (mod && k.toLowerCase() === 'x'){ if (copySel()) deleteNotes([...sel]); return; }
    if (mod && k.toLowerCase() === 'v'){ clearTimeout(pendingPaste); pendingPaste = setTimeout(() => { pendingPaste = null; pasteClip(); }, 80); return; }
    if (mod) return;
    if (k === 'Delete' || k === 'Backspace'){
      e.preventDefault();
      if (selLink) deleteLink(selLink); else deleteNotes([...sel]);
      return;
    }
    if (k === 'Enter' && sel.size === 1){ e.preventDefault(); openEditor([...sel][0]); return; }
    if (k.startsWith('Arrow') && sel.size){
      e.preventDefault();
      const s = e.shiftKey ? GRID : (app.snap ? GRID : 2);
      const dx = k === 'ArrowLeft' ? -s : k === 'ArrowRight' ? s : 0, dy = k === 'ArrowUp' ? -s : k === 'ArrowDown' ? s : 0;
      if (!e.repeat) checkpoint();
      sel.forEach(id => { const n = N(id); n.x += dx; n.y += dy; const ne = noteEl(id); ne.style.left = n.x + 'px'; ne.style.top = n.y + 'px'; });
      scheduleLinks(); save(); return;
    }
    if (k === 'n' || k === 'N'){ e.preventDefault(); newNoteInView(); return; }
    if (k === '/'){ e.preventDefault(); search.focus(); return; }
    if (k === '?'){ $('help').hidden = false; return; }
    if (k === 'g' || k === 'G'){ toggleSnap(); return; }
    if (k === 'f' || k === 'F'){ e.preventDefault(); newFrameInView(); return; }
    if (k === '+' || k === '='){ zoomCenter(z => z * 1.2); return; }
    if (k === '-' || k === '_'){ zoomCenter(z => z / 1.2); return; }
    if (k === '0'){ zoomCenter(() => 1); return; }
    if (k === '!' || (e.shiftKey && e.code === 'Digit1')){ fitAll(); return; }
  });
  document.addEventListener('copy', e => {
    if (typing() || !modal.hidden || !sel.size) return;
    const t = (clip && clip.text) || ' ';
    e.preventDefault(); e.clipboardData.setData('text/plain', t);
  });
  document.addEventListener('paste', e => {
    if (typing() || !modal.hidden || (LIB && (!libEl.hidden || !pkgDlg.hidden)) || !B) return;
    const files = [...(e.clipboardData?.files || [])];
    const text = e.clipboardData?.getData('text/plain') || '';
    const internal = clip && (!text || text === clip.text);
    if (internal && !files.length) return;           // the keydown handler pastes notes
    clearTimeout(pendingPaste); pendingPaste = null;
    e.preventDefault();
    const c = viewCenter();
    if (files.length){
      const n = createNote(c.x - DEFAULT_W/2, c.y - 60, { text:files.length === 1 ? (files[0].name || 'Pasted image') : `${files.length} files` });
      n.attachments = files.map(f => ({ id:uid(), name:f.name || 'pasted', type:f.type || '', size:f.size || 0, blob:f }));
      render(); save();
    } else if (text.trim()){
      createNote(c.x - DEFAULT_W/2, c.y - 60, { text:text.trim() });
    }
  });

  /* ================= Page hooks ================= */
  // What a page's plugin can use. Getters, because B and app are replaced as boards load and switch.
  const api = {
    cfg, W, $, el, esc, uid, bid, inline, checklist, parseText, fmtDue, fmtHrs, toast, toastSoft, DEFAULT_W, COLORS,
    get B(){ return B; }, get app(){ return app; }, get cloud(){ return cloud; }, N,
    menu, mi, ms, showMenu, closeMenu, placeMenu, edText,
    createNote, openEditor, paintEditor, render, save, checkpoint, newBoard, fitAll, centerOn, notesInFrame, worldRect, noteEl,
  };
  P = (cfg.plugin && cfg.plugin(api)) || {};

  /* ================= Load ================= */
  function start(){
    const want = new URLSearchParams(location.search).get(cfg.urlParam);
    if (want && app.boards[want]){ openPackage(want); return; }
    if (want) toast(T.notHere || `That ${W.board} isn’t here.`);
    if (cfg.startInLibrary){                        // open on the library, with the last board behind it
      B = app.boards[app.current] || null;
      if (B) render();
      return openLibrary();
    }
    const first = app.boards[app.current] ? app.current : app.order.find(id => app.boards[id]);
    if (first){ openPackage(first); return; }
    openLibrary();
  }
  async function bootTabs(){
    let sess = null;
    if (window.MMCloud && MMCloud.enabled){
      MMCloud.mountAccount($('acct'), { compact: true });
      try { sess = await MMCloud.session(); }
      catch (e) { sess = null; toast(`Can’t reach the server — showing ${T.demo} in this browser.`); }
    }
    if (sess && sess.org){
      try {
        await loadCloud(sess);
        saveStateEl.textContent = cloud.edit ? 'Saved' : 'View only';
        await offerLocalCopy();
        if (!app.order.length) newBoard(W.Board + ' 1');
        B = app.boards[app.current] || app.boards[app.order[0]];
        app.current = B.id;
        render(); save();
        if (!app.tipsSeen) $('tips').hidden = false;
      } catch (e) {
        saveStateEl.textContent = 'Not loaded';
        toast('Couldn’t load your boards: ' + (e.message || e) + ' — reload to try again.');
        cloud.edit = false;
        if (!app.order.length) newBoard(W.Board + ' 1');
        B = app.boards[app.order[0]]; app.current = B.id; render();
      }
      return;
    }
    if (sess && !sess.org) toast(`Your account isn’t in an organization yet — showing ${T.demo}.`);
    try {
      let saved = await store.get('app');
      if (!saved){
        const old = await store.get('board');          // v0.0.x single-board save
        if (old && old.notes){
          saved = { boards:{}, order:[], current:null, snap:false };
          const b = { id:uid(), name:W.Board + ' 1', notes:old.notes, links:[], pan:old.pan, zoom:1, z:old.z };
          saved.boards[b.id] = b; saved.order.push(b.id); saved.current = b.id;
        }
      }
      if (saved && saved.boards && saved.order && saved.order.length){
        app = saved;
        app.order = app.order.filter(id => app.boards[id]);
        Object.values(app.boards).forEach(fixBoard);
      }
      saveStateEl.textContent = 'Saved';
    } catch (e) { storageOk = false; saveStateEl.textContent = 'Not saved'; }
    if (!app.order.length) newBoard(W.Board + ' 1');
    B = app.boards[app.current] || app.boards[app.order[0]];
    app.current = B.id;
    render();
    if (!app.tipsSeen) $('tips').hidden = false;
  }
  if (!LIB) bootTabs(); else (async () => {
    let sess = null;
    if (window.MMCloud && MMCloud.enabled){
      MMCloud.mountAccount($('acct'), { compact: true });
      try { sess = await MMCloud.session(); }
      catch (e) { sess = null; toast(`Can’t reach the server — showing ${T.demo} in this browser.`); }
    }
    if (sess && sess.org){
      try {
        await loadCloud(sess);
        saveStateEl.textContent = cloud.edit ? 'Saved' : 'View only';
        if (cloud.edit && !app.seeded) seedExamples();
      } catch (e) {
        saveStateEl.textContent = 'Not loaded';
        toast(`Couldn’t load ${T.loadWhat}: ` + (e.message || e) + ' — reload to try again.');
        cloud.edit = false;
      }
      start();
      return;
    }
    if (sess && !sess.org) toast(`Your account isn’t in an organization yet — showing ${T.demo}.`);
    try {
      const saved = await store.get('app');
      if (saved && saved.boards && saved.order){
        app = saved;
        app.order = app.order.filter(id => app.boards[id]);
        Object.values(app.boards).forEach(fixBoard);
      }
      saveStateEl.textContent = 'Saved';
    } catch (e) { storageOk = false; saveStateEl.textContent = 'Not saved'; }
    seedExamples();
    start();
  })();
}};
