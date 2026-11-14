// Unit tests for mm-machine.js, mm-demo.js, mm-records.js and mm-plates.js (plain Node, no browser).
//   node tests/unit/machine.test.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '../..');
const ctx = { window: {}, JSON, Object, Array, Math, Date, String, Number, console, setTimeout };
vm.createContext(ctx);
for (const f of ['mm-machine.js', 'mm-demo.js', 'mm-records.js', 'mm-plates.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx);
const M = ctx.window.MMMachine, D = ctx.window.MMDemo, R = ctx.window.MMRecords, P = ctx.window.MMPlates;
const failures = [];
const check = (n, ok, d = '') => { if (!ok) failures.push(n); console.log((ok ? 'PASS ' : 'FAIL ') + n + (d ? ' — ' + d : '')); };
const canon = v => Array.isArray(v) ? '[' + v.map(canon).join(',') + ']' : (v && typeof v === 'object') ? '{' + Object.keys(v).sort().map(k => JSON.stringify(k) + ':' + canon(v[k])).join(',') + '}' : JSON.stringify(v);

// dates
for (const tz of ['America/New_York', 'Europe/London', 'Australia/Sydney']){
  process.env.TZ = tz;
  check(`day counts across daylight saving (${tz})`, M.daysBetween('2026-03-01', '2026-03-15') === 14 && M.daysBetween('2026-10-25', '2026-11-08') === 14
    && M.addDays('2026-03-07', 1) === '2026-03-08' && M.addDays('2026-10-31', 2) === '2026-11-02');
}
process.env.TZ = 'America/New_York';
check('isDay accepts real days only', M.isDay('2026-02-28') && !M.isDay('2026-02-30') && !M.isDay('11/07/2026') && !M.isDay(null) && !M.isDay(20261107));
check('bad dates give blanks, not NaN-NaN-NaN', M.addDays('11/07/2026', 3) === '' && Number.isNaN(M.daysBetween('x', '2026-01-01'))
  && M.dueDate({ installed: 'nope', target: 6 }, 'x') === null);

// normalize: the setup is checked, and clean setups pass through unchanged
const live = { name: 'PM1', press: { nips: 2, tandem: true }, dryers: [{ type: 'uno' }, { type: 'double' }, { type: 'double' }],
  former: { type: 'twin', lumpbreaker: true }, calender: true,
  refiners: [{ id: 'bp1', name: 'BP 1' }, { id: 'bp2', name: 'BP 2' }, { id: 'tp1', name: 'TP 1' }, { id: 'tp2', name: 'TP 2' }] };
check('normalize leaves a valid setup unchanged', canon(M.normalize(live)) === canon(live));
check('normalize fills a missing setup', M.positions(M.normalize(null)).length === 21);
const evil = M.normalize({ refiners: [{ id: 'x"><img src=x>', name: 'A' }, { id: 'a' }, { id: 'a' }], press: { nips: 99 }, dryers: [{ type: '<b>' }], former: 'x' });
check('normalize drops unsafe refiner ids and splits duplicates', evil.refiners.every(r => /^[a-z0-9-]+$/.test(r.id)) && new Set(evil.refiners.map(r => r.id)).size === 3);
check('normalize keeps press nips and dryer types in range', evil.press.nips === 2 && evil.dryers[0].type === 'double' && evil.former.type === 'twin');

// felt rolls (Sim Mill): optional per dryer section, kept only when 1-12, each a roll position
const sim = M.normalize({ name: 'PM1', former: { type: 'fourdrinier', lumpbreaker: false }, press: { nips: 2, tandem: false },
  dryers: [{ type: 'uno', feltRolls: 5 }, { type: 'uno', feltRolls: 5 }, { type: 'uno', feltRolls: 5 }, { type: 'uno', feltRolls: 5 }],
  calender: false, refiners: [{ id: 'refa', name: 'REF 1' }, { id: 'refb', name: 'REF 2' }] });
const sp = M.positions(sim);
check('felt rolls become roll positions', sp.filter(p => /^d\d-froll-\d+$/.test(p.id) && p.kind === 'roll').length === 20 && sp.length === 35,
  sp.length + ' positions');
check('felt-roll names read like the rest', sp.some(p => p.id === 'd3-froll-2' && p.name === '3rd section felt roll 2'));
check('feltRolls out of range is dropped', M.normalize({ dryers: [{ type: 'uno', feltRolls: 40 }, { type: 'uno', feltRolls: -1 }] }).dryers.every(d => !('feltRolls' in d)));

// cleanItem: valid data passes through byte-for-byte, bad values are fixed or dropped
const demo = D.build();
const changed = Object.entries(demo.items).filter(([k, v]) => canon(M.cleanItem(v)) !== canon(v)).map(([k]) => k);
check('cleanItem leaves every demo item unchanged', changed.length === 0, changed.join(','));
const liveItem = { note: '', target: 26, history: [], installed: '2026-05-14', targetUnit: 'weeks' };
check('cleanItem leaves a live record unchanged', canon(M.cleanItem(liveItem)) === canon(liveItem));
const bad = M.cleanItem({ condition: 'worn" onx="1', installed: '11/07/2026', target: 'abc', history: [{ reason: '<x>', days: -4, installed: '2026-01-01', removed: '2026-02-01' }], extra: '<script>' });
check('cleanItem fixes unknown condition, bad date, bad target, bad history', bad.condition === 'good' && bad.installed === '' && !('target' in bad)
  && bad.history[0].reason === 'other' && bad.history[0].days === 31 && !('extra' in bad), JSON.stringify(bad));
check('cleanItems drops unsafe position ids', Object.keys(M.cleanItems({ 'form-top': {}, 'bad"id': {}, '<x>': {} })).join() === 'form-top');

// change-outs
const it = { installed: '2026-01-01', target: 12, vendor: 'NB', style: 'S', serial: '1', condition: 'worn', conditionNote: 'edge wear', conditionDate: '2026-02-01', note: 'n' };
const round = M.unreplaced(M.replaced(it, '2026-03-01', { serial: '2' }));
const lost = ['installed', 'vendor', 'style', 'serial', 'condition', 'conditionNote', 'conditionDate', 'note'].filter(k => it[k] !== round[k]);
check('undo of a change-out restores the run exactly', lost.length === 0, lost.join(','));
let threw = ''; try { M.replaced({ installed: '2026-10-01' }, '2026-09-01'); } catch (e) { threw = e.message; }
check('a change date before the install date is refused', /before the install date/.test(threw));
threw = ''; try { M.replaced({ installed: '2026-10-01' }, 'soon'); } catch (e) { threw = e.message; }
check('an invalid change date is refused', /valid date/.test(threw));
let long = { installed: '2000-01-01' };
for (let i = 1; i <= 2000; i++) long = M.replaced(long, M.addDays('2000-01-01', i * 42));
check('2,000 change-outs on one position stays well under 1 MB', JSON.stringify(long).length < 1e6);

// demo data
const neg = Object.entries(demo.items).flatMap(([k, v]) => (v.history || []).filter(h => h.days < 0 || h.removed < h.installed).map(() => k));
check('demo history has no negative runs', neg.length === 0, neg.join(','));
const unknown = Object.keys(demo.items).filter(k => !M.positions(demo.machine).some(p => p.id === k));
check('demo items all match machine positions', unknown.length === 0, unknown.join(','));

// record ids
check('board record ids round-trip', canon(R.boards.parse(R.boards.note('b1', 'n1'))) === canon({ kind: 'note', board: 'b1', item: 'n1' })
  && R.boards.parse(R.boards.board('b1')).kind === 'board' && R.boards.parse('seeded').kind === 'seeded' && R.boards.parse('item:x') === null && R.boards.parse('n:b1') === null);
const col = R.boards.collect({ 'p:b1': { name: 'A' }, 'n:b1:n1': { text: 'x' }, 'f:b1:f1': { title: 'F' }, 'n:gone:n2': { text: 'orphan' }, 'seeded': { at: 1 } });
check('collect groups a board\'s records and drops orphans', Object.keys(col).join() === 'b1' && col.b1.notes.n1.id === 'n1' && col.b1.frames[0].id === 'f1');
check('My Machine ids', R.mymachine.parse(R.mymachine.item('p1-felt-top')).pos === 'p1-felt-top' && R.mymachine.parse('machine').kind === 'machine' && R.mymachine.parse('p:x') === null);
check('Outage Planning ids keep everything after the first colon', canon(R.outages.parse('pkd:pkg1:step2')) === canon({ kind: 'pkd', id: 'pkg1:step2' })
  && R.outages.parse('settings').kind === 'settings' && R.outages.parse('bogus:1') === null && R.outages.key('man', 'o1:night') === 'man:o1:night');

// refiner plates (mm-plates.js): plate types from Consumables cards, fits, taking and giving back sets
{
  const card = (rows, fits, extra) => ({ text: 'Refiner plates\nnote', cons: Object.assign({ type: 'plates', kind: 'inv', unit: 'sets', rows, fits }, extra || {}) });
  const recs = {
    'p:b1': { name: 'PM1 Consumables' },
    'n:b1:c1': card([{ id: 'r1', a: 'Vendor A', b: 'LC pattern', c: 'RP-2210', q: 2 }, { id: 'r2', a: 'Vendor B', b: 'HC pattern', q: 0 }, { id: 'r3', a: '', b: '', q: 5 }], { mode: 'all', list: '' }),
    'n:b1:c2': card([{ id: 'r1', a: 'Vendor C', b: 'TP only', q: 1 }], { mode: 'some', list: 'TP 1, tp2' }),
    'n:b1:c3': { text: 'Dryer rope', cons: { type: 'rope', kind: 'inv', rows: [{ id: 'r1', a: 'Red', b: '', q: 3 }] } },
    'n:gone:c9': card([{ id: 'r1', a: 'Old', b: 'Orphan', q: 9 }], { mode: 'all' }),
  };
  const all = P.types(recs);
  check('plate types: plate rows only, blank rows and orphan cards skipped', all.length === 3 && all.every(t => t.vendor !== 'Red' && t.vendor !== 'Old'), all.map(t => t.key).join(' '));
  const bp1 = P.types(recs, 'BP 1'), tp2 = P.types(recs, 'TP 2');
  check('plate types: fits lists match refiner names loosely; fitting types first', !bp1.find(t => t.vendor === 'Vendor C').fits && tp2.find(t => t.vendor === 'Vendor C').fits
    && bp1[0].fits && bp1[bp1.length - 1].vendor === 'Vendor C');
  const a = all.find(t => t.vendor === 'Vendor A');
  check('plate type key, label and part #', a.key === 'b1:c1:r1' && a.part === 'RP-2210' && P.label(a) === 'Vendor A — LC pattern · RP-2210' && a.boardName === 'PM1 Consumables');
  const t1 = P.adjust(recs, 'b1:c1:r2', -1);
  check('taking a set with none on hand goes below zero', t1.id === 'n:b1:c1' && t1.data.cons.rows[1].q === -1 && recs['n:b1:c1'].cons.rows[1].q === 0);
  check('adjust leaves other rows alone and refuses unknown keys', t1.data.cons.rows[0].q === 2 && P.adjust(recs, 'b1:c1:nope', -1) === null
    && P.adjust(recs, 'b1:c3:r1', -1) === null && P.adjust(recs, 'bad', 1) === null);
  // old two-column cards (Manufacturer · Pattern / part #) read as plate types too
  const old = { 'p:b2': {}, 'n:b2:c1': { text: 'Refiner plates', cons: { kind: 'inv', unit: 'sets', cols: ['Manufacturer', 'Pattern / part #'], fits: { mode: 'all' }, rows: [{ id: 'x', a: 'Vendor A', b: 'LC · RP-2210', q: 4 }] } } };
  check('older plate cards still work', P.types(old).length === 1 && P.types(old)[0].model === 'LC · RP-2210' && P.cols(old['n:b2:c1'].cons).join() === 'Vendor,Model,Part #');
  // a stock keeps its records, takes and gives back, and replays its own change after a conflict
  let saved = 0; const st = P.stock(), store = { edit: true, save: () => saved++ };
  for (const [k, v] of Object.entries(recs)) st.onChange(k, v);
  check('stock does nothing without a store', st.take('b1:c1:r1') === null && st.records['n:b1:c1'].cons.rows[0].q === 2);
  st.attach(store);
  const left = st.take('b1:c1:r1');
  check('stock take', left.onHand === 1 && saved === 1);
  const theirs = JSON.parse(JSON.stringify(recs['n:b1:c1'])); theirs.cons.rows[0].q = 7;      // someone recounted first
  st.onChange('n:b1:c1', theirs, { conflict: true });
  check('stock replays its take on top of a conflicting edit', st.find('b1:c1:r1').onHand === 6);
  st.onStatus('saved'); st.onChange('n:b1:c1', theirs, { conflict: true });
  check('stock forgets changes once saved', st.find('b1:c1:r1').onHand === 7);
  check('stock give', st.give('b1:c1:r1').onHand === 8);
  // My Machine keeps the plates a run took, and only for that run
  const pl = P.runPlate(a);
  let it = M.replaced({ installed: '2026-08-01', vendor: 'Vendor A', style: 'LC' }, '2026-10-01', { plate: pl, vendor: 'Vendor A', style: 'LC pattern · RP-2210' });
  check('a plate change keeps the plates taken', it.plate.key === 'b1:c1:r1' && it.plate.part === 'RP-2210');
  it = M.replaced(it, '2026-11-11');
  check('the next change without stock does not inherit them; history does', !it.plate && !it.history[0].plate && it.history[1].plate.key === 'b1:c1:r1');
  check('undo puts the plates back on the run', M.unreplaced(it).plate.key === 'b1:c1:r1');
  check('cleanItem keeps a good plate and drops a bad one', M.cleanItem({ plate: pl }).plate.key === 'b1:c1:r1'
    && M.cleanItem({ plate: { key: 'x"><' } }).plate === undefined && M.cleanItem({ history: [{ installed: '2026-01-01', removed: '2026-02-01', plate: pl }] }).history[0].plate.vendor === 'Vendor A');
}

console.log(`\n${failures.length ? 'FAILED: ' + failures.join(', ') : 'all passed'}`);
process.exit(failures.length ? 1 : 0);
