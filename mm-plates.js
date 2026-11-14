// Machine Manager — refiner plate types and stock, shared by My Machine, Outage Planning and the Consumables Tracker.
// Load after mm-records.js. Exposes window.MMPlates.
//
// A plate type is one row of a "Refiner plates" card in the Consumables Tracker (any board of the org):
//   card note:  n:<board>:<card>  { text, cons: { type:'plates', kind:'inv', unit:'sets', cols, rows:[{ id, a, b, c, q }], fits } }
//   row:        a = vendor · b = model · c = part # (optional) · q = sets on hand (can go negative when a change
//               is logged with none on hand: a count that's wrong shows up instead of being hidden)
// A plate type's key is "<board>:<card>:<row>". Logging a plate change takes one set (one refiner = one set);
// undoing it gives the set back. The run in My Machine keeps { plate: { key, vendor, model, part } }.
(() => {
  const COLS = ['Vendor', 'Model', 'Part #'];
  const norm = s => String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '');
  const isPlates = c => !!(c && c.kind === 'inv' && (c.type === 'plates' || c.fits));
  // Older plate cards had two columns (Manufacturer · Pattern / part #): shown as Vendor · Model · Part #.
  const cols = c => (isPlates(c) ? COLS.slice() : (c && c.cols) || []);
  // Does a card's fits setting include this refiner? ('all', or a list like "BP 1, BP 2")
  function fits(c, refinerName){
    const f = c && c.fits;
    if (!f || f.mode !== 'some' || !String(f.list || '').trim()) return true;
    const want = norm(refinerName);
    return !!want && String(f.list).split(/[,;\n]+/).some(x => norm(x) === want);
  }
  const label = t => [t.vendor, t.model].filter(Boolean).join(' — ') + (t.part ? ' · ' + t.part : '');
  const keyOf = (board, card, row) => `${board}:${card}:${row}`;
  function parseKey(key){
    const p = String(key || '').split(':');
    return p.length === 3 && p.every(Boolean) ? { board: p[0], card: p[1], row: p[2] } : null;
  }
  // Every plate type in a Consumables store's records, those that fit `refinerName` first.
  //   → [{ key, board, card, row, vendor, model, part, onHand, unit, fits, cardTitle, boardName }]
  function types(records, refinerName){
    const out = [];
    const boards = window.MMRecords.boards.collect(records || {});
    for (const b of Object.values(boards)){
      for (const n of Object.values(b.notes)){
        const c = n.cons; if (!isPlates(c)) continue;
        const ok = refinerName == null ? true : fits(c, refinerName);
        for (const r of c.rows || []){
          const vendor = String(r.a || '').trim(), model = String(r.b || '').trim(), part = String(r.c || '').trim();
          if (!vendor && !model) continue;
          out.push({ key: keyOf(b.id, n.id, r.id), board: b.id, card: n.id, row: r.id, vendor, model, part,
            onHand: Number(r.q) || 0, unit: c.unit || 'sets', fits: ok,
            cardTitle: String(n.text || '').split('\n')[0].trim(), boardName: (b.data && b.data.name) || '' });
        }
      }
    }
    return out.sort((x, y) => (y.fits - x.fits) || x.vendor.localeCompare(y.vendor) || x.model.localeCompare(y.model));
  }
  // Change the sets on hand of one plate type by `d` (−1 takes a set, +1 gives it back).
  // → { id, data } for the card record to save, or null if the type isn't there any more.
  function adjust(records, key, d){
    const k = parseKey(key); if (!k) return null;
    const id = window.MMRecords.boards.note(k.board, k.card), card = records && records[id];
    if (!card || !isPlates(card.cons)) return null;
    const rows = card.cons.rows || [];
    if (!rows.some(r => r.id === k.row)) return null;
    const data = JSON.parse(JSON.stringify(card));
    data.cons.rows = data.cons.rows.map(r => r.id === k.row ? { ...r, q: (Number(r.q) || 0) + d } : r);
    return { id, data };
  }
  // What a run records about the plates it took.
  const runPlate = t => t ? { key: t.key, vendor: t.vendor, model: t.model, part: t.part || '' } : null;

  // A small helper for pages that take plates: keeps the Consumables records, applies takes / give-backs and
  // re-applies them if someone else's edit of the same card won the save race (mm-cloud refuses ours and hands
  // back theirs as a conflict). A change is pending until the store next reports 'saved'.
  //   const stock = MMPlates.stock();
  //   store = MMCloud.openStore('consumables', { snapshot: () => stock.records, onChange: stock.onChange, onStatus: stock.onStatus });
  //   stock.attach(store)
  function stock(){
    const recs = {};
    let store = null, pending = [];    // our own changes not yet confirmed saved: { id, key, d }
    const api = {
      records: recs,
      attach(s){ store = s; },
      get canEdit(){ return !!(store && store.edit); },
      types: refinerName => types(recs, refinerName),
      find: key => types(recs).find(t => t.key === key) || null,
      onChange(id, data, info){
        if (data) recs[id] = data; else delete recs[id];
        if (!(info && info.conflict) || !data) return;
        // Our change to this card was refused because someone else saved it first: apply ours again on top of theirs.
        const mine = pending.filter(x => x.id === id);
        for (const x of mine){ const r = adjust(recs, x.key, x.d); if (r) recs[id] = r.data; }
        if (mine.length && store) setTimeout(() => store.save([id]), 0);
      },
      onStatus(s){ if (s === 'saved') pending = []; },
      // → the plate type after the change, or null (type gone, or nowhere to save it)
      change(key, d){
        if (!store) return null;
        const r = adjust(recs, key, d); if (!r) return null;
        recs[r.id] = r.data;
        pending.push({ id: r.id, key, d });
        store.save([r.id]);
        return api.find(key);
      },
      take: key => api.change(key, -1),
      give: key => api.change(key, +1),
    };
    return api;
  }

  window.MMPlates = { COLS, cols, isPlates, fits, types, adjust, label, keyOf, parseKey, runPlate, stock };
})();
