// Unit tests for mm-machine.js, mm-demo.js and mm-records.js (plain Node, no browser).
//   node tests/unit/machine.test.js
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '../..');
const ctx = { window: {}, JSON, Object, Array, Math, Date, String, Number, console };
vm.createContext(ctx);
for (const f of ['mm-machine.js', 'mm-demo.js', 'mm-records.js']) vm.runInContext(fs.readFileSync(path.join(root, f), 'utf8'), ctx);
const M = ctx.window.MMMachine, D = ctx.window.MMDemo, R = ctx.window.MMRecords;
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

console.log(`\n${failures.length ? 'FAILED: ' + failures.join(', ') : 'all passed'}`);
process.exit(failures.length ? 1 : 0);
