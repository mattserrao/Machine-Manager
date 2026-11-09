// Unit tests for mm-outage-export.js: the outline the Word export is built from, and a real .docx build.
//   node tests/unit/outage_export.test.js        (the .docx part needs vendor/docx-*.js, already in the repo)
const fs = require('fs'), vm = require('vm'), path = require('path');
const root = path.join(__dirname, '../..');
const X = require(path.join(root, 'mm-outage-export.js'));
const failures = [];
const check = (n, ok, d = '') => { if (!ok) failures.push(n); console.log((ok ? 'PASS ' : 'FAIL ') + n + (d ? ' — ' + d : '')); };

check('areas from sections and package areas', X.areaOf('Stock prep') === 'SP' && X.areaOf('Refiners') === 'SP' && X.areaOf('Base ply wire') === 'WE'
  && X.areaOf('Press section') === 'WE' && X.areaOf('2nd dryer section') === 'DE' && X.areaOf('Calender') === 'DE' && X.areaOf('Somewhere') === '');
check('package phases map to outage phases', X.phaseOfTitle('Before the outage') === 'prep' && X.phaseOfTitle('Shutdown & lockout') === 'shutdown'
  && X.phaseOfTitle('Install new felt') === 'day' && X.phaseOfTitle('Startup') === 'startup');

const POS = ['SPOT', 'WET', 'DET'];
const SHIFTS = [{ k: 'shutdown', grp: 'Shutdown', name: 'Nights' }, { k: 'shortoff', grp: 'Outage', name: 'Short Off' }, { k: 'day', grp: 'Outage', name: 'Day Shift' }, { k: 'startup', grp: 'Startup', name: 'Nights' }];
const seat = v => ({ v, inherited: false });
const model = {
  machine: 'PM1',
  outage: { date: '2026-11-11', type: 'normal', shutdown: '2026-11-11T04:00', onReel: '2026-11-11T20:00', hours: 16 },
  due: [
    { name: 'Tandem felt', section: 'Press section', due: '2026-11-11', accepted: true },
    { name: 'BP 2 refiner', section: 'Refiners', due: '2026-11-11' },
    { name: '2nd press bottom roll', section: 'Press section', due: '2026-09-30', declined: true, to: '2026-12-23' },
    { name: 'Lumpbreaker roll', section: 'Base ply wire', due: '2026-12-09', deferred: '2026-09-30' },
    { name: 'Changed one', section: 'Press section', changed: true },
  ],
  tasks: [
    { text: 'Count plates', phase: 'prep', area: 'SP', crew: 'B', who: 'B. Fortin', done: false },
    { text: 'Wash up headbox', phase: 'shutdown', area: 'WE', crew: 'A', who: 'K. Lavoie', done: true },
    { text: 'Uhle covers', phase: 'day', area: 'WE', crew: 'D', who: 'M. Belanger' },
    { text: 'Pocket vent dampers', phase: 'day', area: 'DE' },
    { text: 'Hose the press pit', phase: 'shortoff' },
    { text: 'Book the crane' },
  ],
  packages: [{ name: 'Dryer Felt Change', area: 'Dryer section', phases: [
    { title: 'Before the outage', steps: [{ title: 'Pre-job brief', who: 'Shift lead', hrs: 0.5, lines: ['- [ ] Walk the job'], subs: [], done: true }] },
    { title: 'Shutdown & lockout', steps: [{ title: 'Cool down', lines: [], subs: [] }] },
    { title: 'Change the felt', steps: [{ title: 'Pull in at crawl', lines: [], subs: ['Hazards: nip points'] }] },
    { title: 'Startup', steps: [{ title: 'Steam up', lines: [], subs: [] }] },
  ] }],
  positions: POS, shifts: SHIFTS,
  manning: { shutdown: { SPOT: seat('R. Dube'), WET: seat('K. Lavoie'), DET: seat('') }, shortoff: {}, day: { SPOT: seat('J. Hebert') }, startup: { SPOT: { v: 'R. Dube', inherited: true } } },
  crews: { A: { names: ['R. Dube', 'K. Lavoie'] }, B: { names: ['B. Fortin'] } },
};
const ol = X.outline(model);
const sec = k => ol.sections.find(s => s.k === k);
check('sections in order', ol.sections.map(s => s.k).join(',') === 'prep,resources,shutdown,shortoff,day,startup,other', ol.sections.map(s => s.k).join(','));
check('times and duration in the title block', /Wed Nov 11 04:00/.test(ol.times) && /Wed Nov 11 20:00/.test(ol.times) && /16 h planned/.test(ol.times), ol.times);
const fab = sec('prep').fabrics;
check('prep: accepted first, then to decide; declined and changed left out of the table', fab.map(f => f.decision).join(',') === 'Accepted,To decide,To decide'
  && !fab.some(f => /bottom roll|Changed one/.test(f.name)), fab.map(f => f.name + ':' + f.decision).join(' | '));
check('prep: declined listed with where it moved', sec('prep').declined.length === 1 && sec('prep').declined[0].to === 'Dec 23');
check('prep: deferred noted', fab.find(f => f.name === 'Lumpbreaker roll').note.includes('Deferred from Sep 30'));
check('prep: tasks and the package prep step by area', sec('prep').groups.map(g => g.k).join(',') === 'SP,DE');
check('shutdown: sheet-off time and who is on', sec('shutdown').time === 'Sheet off Wed Nov 11 04:00' && sec('shutdown').crew.length === 2);
check('days: tasks by area plus package steps (DE from the package area)', sec('day').groups.map(g => `${g.k}:${g.items.length}`).join(',') === 'WE:1,DE:2');
check('start-up: on-reel time, inherited crew shown', sec('startup').time === 'On reel Wed Nov 11 20:00' && sec('startup').crew[0].v === 'R. Dube');
check('short off: task with no area under "No area set"', sec('shortoff').groups.length === 1 && sec('shortoff').groups[0].k === '');
check('tasks with no phase get their own section', sec('other').groups[0].items[0].text === 'Book the crane');
check('resources: assignments per person, crews listed', sec('resources').assignments.length === 3 && sec('resources').crews.length === 2);
check('package step lines cleaned of checkboxes', sec('prep').groups.find(g => g.k === 'DE').items[0].lines[0] === 'Walk the job');

// A real Word file from the vendored library
const vend = fs.readdirSync(path.join(root, 'vendor')).find(f => /^docx-.*\.js$/.test(f));
const c = { console, setTimeout, clearTimeout, TextEncoder, TextDecoder, Uint8Array, ArrayBuffer, Promise, Blob, URL, Buffer, process };
c.globalThis = c; c.window = c; c.self = c;
vm.createContext(c);
vm.runInContext(fs.readFileSync(path.join(root, 'vendor', vend), 'utf8') + ';globalThis.docx = docx;', c);
const doc = X.render(c.docx, ol);
c.docx.Packer.toBuffer(doc).then(buf => {
  const s = buf.toString('latin1');
  check('builds a .docx (zip with word/document.xml)', buf[0] === 0x50 && buf[1] === 0x4b && s.includes('word/document.xml'), `${buf.length} bytes`);
  done();
}).catch(e => { check('builds a .docx', false, String(e)); done(); });
function done(){
  if (failures.length){ console.log(`\n${failures.length} failed`); process.exit(1); }
  console.log('\nall passed');
}
