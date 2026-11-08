// Machine Manager — the record ids each tool keeps in mm_records, in one place.
// A tool that reads another tool's data (Outage Planning reads My Machine and the Ops Task Library)
// goes through these instead of spelling out prefixes, so a format change breaks in one file, loudly.
(() => {
  // Board tools (Whiteboard, Ops Task Library, Consumables Tracker): one record per board, card,
  // arrow and frame.   p:<board> · n:<board>:<card> · l:<board>:<arrow> · f:<board>:<frame> · seeded
  const BOARD_KINDS = { p: 'board', n: 'note', l: 'link', f: 'frame' };
  const boards = {
    board: b => 'p:' + b,
    note: (b, n) => `n:${b}:${n}`,
    link: (b, l) => `l:${b}:${l}`,
    frame: (b, f) => `f:${b}:${f}`,
    seeded: 'seeded',
    // → { kind: 'board' | 'note' | 'link' | 'frame' | 'seeded', board, item } or null if it isn't a board record
    parse(id){
      if (id === 'seeded') return { kind: 'seeded', board: null, item: null };
      const [k, board, item] = String(id).split(':');
      const kind = BOARD_KINDS[k];
      if (!kind || !board || (kind !== 'board' && !item)) return null;
      return { kind, board, item: kind === 'board' ? null : item };
    },
    // { recordId: data } → { boardId: { id, data, notes: { id: data+id }, links: [data+id], frames: [data+id] } }
    collect(records){
      const out = {};
      const get = id => out[id] || (out[id] = { id, data: null, notes: {}, links: [], frames: [] });
      for (const [rid, d] of Object.entries(records || {})){
        const r = boards.parse(rid); if (!r || r.kind === 'seeded' || !d) continue;
        const b = get(r.board);
        if (r.kind === 'board') b.data = d;
        else if (r.kind === 'note') b.notes[r.item] = { ...d, id: r.item };
        else (r.kind === 'link' ? b.links : b.frames).push({ ...d, id: r.item });
      }
      for (const id of Object.keys(out)) if (!out[id].data) delete out[id];   // cards of a board that's gone
      return out;
    },
  };

  // My Machine: the machine setup, and one record per tracked position.   machine · item:<position>
  const mymachine = {
    machine: 'machine',
    item: pos => 'item:' + pos,
    parse(id){
      if (id === 'machine') return { kind: 'machine' };
      if (String(id).startsWith('item:')) return { kind: 'item', pos: id.slice(5) };
      return null;
    },
  };

  // Outage Planning.   settings · outage:<id> · task:<id> · pkg:<id> (package on an outage)
  //                    pkd:<pkg>:<step> (step done) · man:<outage>:<shift> (manning)
  const OUTAGE_KINDS = ['outage', 'task', 'pkg', 'pkd', 'man'];
  const outages = {
    settings: 'settings',
    KINDS: OUTAGE_KINDS,
    key: (kind, id) => `${kind}:${id}`,
    parse(id){
      if (id === 'settings') return { kind: 'settings' };
      const i = String(id).indexOf(':'), kind = id.slice(0, i);
      return i > 0 && OUTAGE_KINDS.includes(kind) ? { kind, id: id.slice(i + 1) } : null;
    },
  };

  window.MMRecords = { boards, mymachine, outages };
})();
