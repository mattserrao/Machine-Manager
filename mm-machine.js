// Machine Manager — machine model shared by My Machine and Operations Outage Planning.
// Positions (fabrics, rolls, refiner plates) come from the machine setup; an item is the
// saved state of one position: { installed:'YYYY-MM-DD', target, targetUnit, note, history:[] }.
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

  const clone = o => JSON.parse(JSON.stringify(o));
  const pad = n => String(n).padStart(2, '0');
  const ymd = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  const todayStr = () => ymd(new Date());
  const parseDay = s => { const [y, m, d] = s.split('-').map(Number); return new Date(y, m - 1, d); };
  const daysBetween = (a, b) => Math.round((parseDay(b) - parseDay(a)) / 864e5);
  const addDays = (s, n) => { const d = parseDay(s); d.setDate(d.getDate() + n); return ymd(d); };
  const ord = n => n + (n === 1 ? 'st' : n === 2 ? 'nd' : n === 3 ? 'rd' : 'th');

  // Fill anything missing from the defaults, so a partial or older saved setup can't break a page.
  function normalize(m){
    const d = DEFAULT_MACHINE;
    m = Object.assign({}, clone(d), m || {});
    m.former = Object.assign({}, d.former, m.former || {});
    m.press = Object.assign({}, d.press, m.press || {});
    if (!Array.isArray(m.dryers) || !m.dryers.length) m.dryers = clone(d.dryers);
    if (!Array.isArray(m.refiners)) m.refiners = clone(DEFAULT_REFINERS);
    return m;
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
  const dueDate = (it, id) => { const L = lifeDays(it, id); return it && it.installed && L != null ? addDays(it.installed, L) : null; };
  // A new run starting on `date`: the current run moves into history (same as "Replaced today" in My Machine).
  function replaced(it, date){
    it = Object.assign({ installed: '', note: '', history: [] }, it || {});
    const history = (it.history || []).slice();
    if (it.installed) history.push({ installed: it.installed, removed: date, days: Math.max(0, daysBetween(it.installed, date)) });
    return Object.assign({}, it, { installed: date, history });
  }

  window.MMMachine = { DEFAULT_MACHINE, DEFAULT_REFINERS, DEFAULT_TARGET, WARN_DAYS,
    normalize, sections, positions, targetOf, lifeDays, dueDate, replaced,
    todayStr, parseDay, daysBetween, addDays, ord, ymd };
})();
