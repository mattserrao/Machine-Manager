// Machine Manager — machine model shared by My Machine and Operations Outage Planning.
// Positions (fabrics, rolls, refiner plates) come from the machine setup; an item is the
// saved state of one position (a dryer section can also list felt rolls: dryers[i].feltRolls → d<s>-froll-<n>): { installed:'YYYY-MM-DD', target, targetUnit, note, vendor, style, serial,
// condition:'good'|'wear'|'worn'|'damaged', conditionNote, conditionDate, history:[] }.
(() => {
  const DEFAULT_MACHINE = {
    name: 'PM1',
    former: { type: 'twin', lumpbreaker: true },
    press: { nips: 2, tandem: true },
    dryers: [{ type: 'uno' }, { type: 'double' }, { type: 'double' }],
    calender: true,
    refiners: null      // filled from DEFAULT_REFINERS
  };
  const DEFAULT_REFINERS = [{ id: 'bp1', name: 'BP 1' }, { id: 'bp2', name: 'BP 2' }, { id: 'tp1', name: 'TP 1' }, { id: 'tp2', name: 'TP 2' }];
  const DEFAULT_TARGET = { refiner: { target: 12, unit: 'weeks' } };   // plate life
  const WARN_DAYS = 42; // 6 weeks

  const pad = n => String(n).padStart(2, '0');
  const ymd = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const todayStr = () => ymd(new Date());
  // A calendar day as 'YYYY-MM-DD'. Anything else (wrong format, Feb 30) is not a day.
  const isDay = s => {
    if (typeof s !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(s)) return false;
    const [y, m, d] = s.split('-').map(Number), t = new Date(y, m - 1, d);
    return t.getFullYear() === y && t.getMonth() === m - 1 && t.getDate() === d;
  };
  const parseDay = s => { const [y, m, d] = String(s).split('-').map(Number); return new Date(y, m - 1, d); };
  const daysBetween = (a, b) => isDay(a) && isDay(b) ? Math.round((parseDay(b) - parseDay(a)) / 864e5) : NaN;
  const addDays = (s, n) => { if (!isDay(s)) return ''; const d = parseDay(s); d.setDate(d.getDate() + n); return ymd(d); };
  const ord = n => n + (n === 1 ? 'st' : n === 2 ? 'nd' : n === 3 ? 'rd' : 'th');

  // Fill anything missing from the defaults and drop anything malformed, so a partial, older, imported
  // or tampered setup can't break a page. Every value that ends up in HTML or an id is checked here.
  const str = (v, max = 2000) => (typeof v === 'string' ? v : v == null ? '' : String(v)).slice(0, max);
  const SAFE_ID = /^[a-z0-9-]{1,40}$/;
  function normalize(m){
    const d = DEFAULT_MACHINE;
    m = m && typeof m === 'object' ? m : {};
    const f = m.former && typeof m.former === 'object' ? m.former : {}, p = m.press && typeof m.press === 'object' ? m.press : {};
    const nips = Math.round(Number(p.nips));
    const out = {
      name: str(m.name != null ? m.name : d.name, 60),
      former: { type: f.type === 'fourdrinier' ? 'fourdrinier' : 'twin', lumpbreaker: f.lumpbreaker == null ? d.former.lumpbreaker : !!f.lumpbreaker },
      press: { nips: nips >= 1 && nips <= 3 ? nips : d.press.nips, tandem: p.tandem == null ? d.press.tandem : !!p.tandem },
      dryers: (Array.isArray(m.dryers) && m.dryers.length ? m.dryers : d.dryers).slice(0, 8)
        .map(x => {
          const o = { type: x && x.type === 'uno' ? 'uno' : 'double' };
          const fr = Math.round(Number(x && x.feltRolls));          // felt rolls tracked as roll positions (optional, 0–12)
          if (fr >= 1 && fr <= 12) o.feltRolls = fr;
          return o;
        }),
      calender: m.calender == null ? d.calender : !!m.calender,
      refiners: null
    };
    const seen = new Set();
    out.refiners = (Array.isArray(m.refiners) ? m.refiners : DEFAULT_REFINERS).slice(0, 8).map((r, i) => {
      r = r && typeof r === 'object' ? r : {};
      let id = typeof r.id === 'string' && SAFE_ID.test(r.id) ? r.id : 'r' + i;
      while (seen.has(id)) id += 'x';          // two refiners must never share one record
      seen.add(id);
      return { id, name: str(r.name, 40) };
    });
    return out;
  }
  // One position's saved state with every field checked (shape at the top of this file). Only fields that are
  // present are kept, and valid values pass through unchanged, so clean data comes out byte-for-byte the same
  // (pages compare records to decide what to save; cleaning must never look like an edit).
  const COND_IDS = ['good', 'wear', 'worn', 'damaged'], REASON_IDS = ['planned', 'worn', 'damaged', 'performance', 'other'];
  const day = v => isDay(v) ? v : '';
  const has = (o, k) => Object.prototype.hasOwnProperty.call(o, k);
  function pick(src, spec){
    const out = {};
    for (const [k, fix] of Object.entries(spec)) if (has(src, k)) { const v = fix(src[k]); if (v !== undefined) out[k] = v; }
    return out;
  }
  const text = max => v => str(v, max);
  const oneOf = (list, dflt) => v => list.includes(v) ? v : dflt;
  const RUN = { installed: day, removed: day, vendor: text(200), style: text(200), serial: text(200), reason: oneOf(REASON_IDS, 'other'),
    condition: oneOf(COND_IDS, 'good'), note: text(), runNote: text(), conditionNote: text(500), conditionDate: day,
    days: v => Number.isFinite(v) && v >= 0 ? v : undefined };
  function cleanRun(h){
    h = h && typeof h === 'object' ? h : {};
    const r = pick(h, RUN);
    if (r.days === undefined){ const n = daysBetween(r.installed, r.removed); r.days = Number.isFinite(n) ? Math.max(0, n) : 0; }
    return r;
  }
  const ITEM = { installed: day, note: text(), vendor: text(200), style: text(200), serial: text(200), condition: oneOf(COND_IDS, 'good'),
    conditionNote: text(500), conditionDate: day, target: v => { const n = Number(v); return Number.isFinite(n) && n >= 0 && n < 10000 ? n : undefined; },
    targetUnit: oneOf(['weeks', 'days'], 'weeks'), history: v => (Array.isArray(v) ? v : []).slice(0, 500).map(cleanRun) };
  function cleanItem(it){
    if (!it || typeof it !== 'object' || Array.isArray(it)) return null;
    return pick(it, ITEM);
  }
  // { positionId: item } with unsafe ids and malformed items dropped.
  function cleanItems(items){
    const out = {};
    if (items && typeof items === 'object') for (const [k, v] of Object.entries(items)) {
      if (!/^[a-z0-9-]{1,60}$/.test(k)) continue;
      const it = cleanItem(v); if (it) out[k] = it;
    }
    return out;
  }
  const twinFormer = m => m.former.type === 'twin';
  function sections(m){
    const S = [];
    if (m.refiners.length) S.push({ id: 'sec-refiners', name: 'Refiners' });
    if (twinFormer(m)) S.push({ id: 'sec-topply', name: 'Top ply wire' }, { id: 'sec-baseply', name: 'Base ply wire' });
    else S.push({ id: 'sec-forming', name: 'Forming' });
    S.push({ id: 'sec-press', name: 'Press section' });
    m.dryers.forEach((d, i) => S.push({ id: `sec-dryer-${i + 1}`, name: `${ord(i + 1)} dryer section` }));
    if (m.calender) S.push({ id: 'sec-calender', name: 'Calender' });
    S.push({ id: 'sec-reel', name: 'Reel' });
    return S;
  }
  function positions(m){
    const P = [];
    const add = (id, name, kind, cat, section) => P.push({ id, name, kind, cat, section });
    m.refiners.forEach(r => add(`ref-${r.id}`, `${r.name} refiner`, 'refiner', 'refiner', 'Refiners'));
    if (twinFormer(m)) {
      add('form-top', 'Top ply forming fabric', 'fabric', 'forming', 'Top ply wire');
      add('form-bottom', 'Base ply forming fabric', 'fabric', 'forming', 'Base ply wire');
    } else {
      add('form-bottom', 'Forming fabric', 'fabric', 'forming', 'Forming');
    }
    if (m.former.lumpbreaker) add('lumpbreaker', 'Lumpbreaker roll', 'roll', 'roll', twinFormer(m) ? 'Base ply wire' : 'Forming');
    const tandem = m.press.tandem && m.press.nips > 1;
    for (let n = 1; n <= m.press.nips; n++) {
      add(`p${n}-felt-top`, `${ord(n)} press top felt`, 'fabric', 'press', 'Press section');
      if (!tandem) add(`p${n}-felt-bottom`, `${ord(n)} press bottom felt`, 'fabric', 'press', 'Press section');
    }
    if (tandem) add('p-tandem-felt', 'Tandem felt', 'fabric', 'press', 'Press section');
    for (let n = 1; n <= m.press.nips; n++) {
      add(`p${n}-roll-top`, `${ord(n)} press top roll`, 'roll', 'roll', 'Press section');
      add(`p${n}-roll-bottom`, `${ord(n)} press bottom roll`, 'roll', 'roll', 'Press section');
    }
    m.dryers.forEach((d, i) => {
      const s = i + 1, sec = `${ord(s)} dryer section`;
      if (d.type === 'uno') add(`d${s}-felt`, `${ord(s)} section unorun felt`, 'fabric', 'dryer', sec);
      else {
        add(`d${s}-felt-top`, `${ord(s)} section top felt`, 'fabric', 'dryer', sec);
        add(`d${s}-felt-bottom`, `${ord(s)} section bottom felt`, 'fabric', 'dryer', sec);
      }
      for (let k = 1; k <= (d.feltRolls || 0); k++) add(`d${s}-froll-${k}`, `${ord(s)} section felt roll ${k}`, 'roll', 'roll', sec);
    });
    if (m.calender) {
      add('cal-top', 'Calender top roll', 'roll', 'roll', 'Calender');
      add('cal-bottom', 'Calender bottom roll', 'roll', 'roll', 'Calender');
    }
    return P;
  }

  // Target life for a position: its own setting, else the default for its kind (refiner plates).
  function targetOf(it, id){
    if (it && it.target > 0) return { target: it.target, unit: it.targetUnit === 'days' ? 'days' : 'weeks', dflt: false };
    const d = id.startsWith('ref-') ? DEFAULT_TARGET.refiner : null;
    return d ? { target: d.target, unit: d.unit, dflt: true } : null;
  }
  function lifeDays(it, id){ const t = targetOf(it, id); return t ? Math.round(t.target * (t.unit === 'days' ? 1 : 7)) : null; }
  const dueDate = (it, id) => { const L = lifeDays(it, id); return it && isDay(it.installed) && L != null ? addDays(it.installed, L) : null; };
  // Condition of what's on the machine now. Anything but Good flags it to be changed at the next outage.
  const CONDITIONS = [
    { id: 'good', label: 'Good' },
    { id: 'wear', label: 'Wear' },
    { id: 'worn', label: 'Worn' },
    { id: 'damaged', label: 'Damaged' }
  ];
  const condLabel = c => (CONDITIONS.find(x => x.id === c) || {}).label || '';
  const flagged = it => !!(it && it.condition && it.condition !== 'good');
  // Why a run came off the machine.
  const REASONS = [
    { id: 'planned', label: 'Planned – target life' },
    { id: 'worn', label: 'Worn out' },
    { id: 'damaged', label: 'Damaged' },
    { id: 'performance', label: 'Performance / quality' },
    { id: 'other', label: 'Other' }
  ];
  const reasonLabel = r => (REASONS.find(x => x.id === r) || {}).label || '';
  const defaultReason = it => !flagged(it) ? 'planned' : it.condition === 'damaged' ? 'damaged' : 'worn';

  // A new run starting on `date`: the current run moves into history (same as "Log change-out" in My Machine).
  // History entry: { installed, removed, days, vendor, style, serial, reason, condition, note }.
  // `extra` can override the logged entry (reason, condition, note) and the new run (vendor, style, serial).
  function replaced(it, date, extra = {}){
    it = Object.assign({ installed: '', note: '', history: [] }, it || {});
    if (!isDay(date)) throw new RangeError('Not a valid date.');
    if (it.installed && date < it.installed) throw new RangeError('The change date can’t be before the install date.');
    const history = (it.history || []).slice();
    if (it.installed) history.push({
      installed: it.installed, removed: date, days: Math.max(0, daysBetween(it.installed, date)),
      vendor: it.vendor || '', style: it.style || '', serial: it.serial || '',
      reason: extra.reason || defaultReason(it),
      condition: extra.condition || it.condition || 'good',
      note: extra.note != null ? extra.note : [it.note, it.conditionNote].filter(Boolean).join(' — '),
      // what the run looked like before it came off, so undo can put it back exactly
      runNote: it.note || '', conditionNote: it.conditionNote || '', conditionDate: it.conditionDate || ''
    });
    const next = Object.assign({}, it, {
      installed: date, history, note: '', condition: 'good', conditionNote: '', conditionDate: '',
      vendor: extra.vendor != null ? extra.vendor : (it.vendor || ''),
      style: extra.style != null ? extra.style : (it.style || ''),
      serial: extra.serial || ''
    });
    return next;
  }
  // Undo the last change-out: the last history entry becomes the current run again.
  function unreplaced(it){
    it = JSON.parse(JSON.stringify(it));
    const last = (it.history || []).pop();
    if (!last) return it;
    const exact = last.runNote != null;       // logged by this version: restore the run as it was
    return Object.assign(it, { installed: last.installed, vendor: last.vendor || '', style: last.style || '', serial: last.serial || '',
      condition: last.condition || 'good',
      conditionNote: exact ? last.conditionNote || '' : '', conditionDate: exact ? last.conditionDate || '' : '',
      note: exact ? last.runNote : last.note || '' });
  }

  window.MMMachine = { DEFAULT_MACHINE, DEFAULT_REFINERS, DEFAULT_TARGET, WARN_DAYS,
    CONDITIONS, condLabel, flagged, REASONS, reasonLabel, defaultReason,
    normalize, cleanItem, cleanItems, sections, positions, targetOf, lifeDays, dueDate, replaced, unreplaced,
    todayStr, isDay, parseDay, daysBetween, addDays, ord, ymd };
})();
