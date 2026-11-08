// Sim Mill's task-package library (Ops Task Library) and the step lists Outage Planning copies onto an outage.
// Built with the page's own MMTaskExamples.buildExample, so cards, frames and arrows are laid out exactly as the
// Task Library lays out its examples. Worded for Sim Mill's PM1: a fourdrinier, a 2-nip press with four felts,
// four uno-run dryer sections with felt rolls, and twin refiners (REF 1, REF 2).
//
//   node tools/sim-mill/packages.js <out dir> <created ISO time>
//     -> <out>/records/task-packages.json   { record id: data }  (p: / n: / l: / f: records, as the Task Library saves)
//     -> <out>/records/_package_phases.json { package id: { name, meta, phases } }  (what Outage Planning stores on a pkg)
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.resolve(__dirname, '..', '..');
const [out, created] = [process.argv[2], process.argv[3] || '2026-10-31T12:00:00.000Z'];
const ctx = { window: {} }; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(ROOT, 'mm-task-examples.js'), 'utf8'), ctx);
const { buildExample } = ctx.window.MMTaskExamples;

const PH = { prep: '#64748b', lock: '#dc2626', out: '#d97706', insp: '#0891b2', in: '#2563eb', start: '#16a34a' };
const HAZ = '#ffd8e1', SPEC = '#d4ecff';
const S = (text, who, hrs, sub) => ({ text, who, hrs, sub });
const sub = (text, color) => ({ text, color });

const PACKAGES = [
  { id: 'sm-forming-fabric', name: 'Forming Fabric Change',
    meta: { area: 'Forming', hours: 8, crew: 6, desc: 'Change the fourdrinier forming fabric: cantilever, cut out, clean the table and boxes, pull in, tension and run in.' },
    phases: [
      ['Before the outage', PH.prep, [
        S('Confirm the new fabric\n- [ ] On site: NX-1850 double layer, right length & width\n- [ ] Seam and run direction marked\n- [ ] Spare off the floor checked too', 'Superintendent', 1,
          [sub('Fabric spec card\n- Northbank Fabrics · NX-1850\n- Target tension (kN/m)\n- Last install date (My Machine)', SPEC)]),
        S('Stage tools & equipment\n- [ ] Fabric cart / pull ropes\n- [ ] Cantilever beams & jacks checked\n- [ ] Knives, tape, markers\n- [ ] Spare HP shower nozzles', 'Back tender', 1),
        S('Pre-job brief\n- [ ] Walk the job with the crew\n- [ ] Assign tender / drive side roles\n- [ ] Review JSA & lockout list', 'Shift lead', 0.5,
          [sub('Hazards\n- Pinch points at rolls\n- Wet, slippery floors\n- Overhead lifts: tag lines', HAZ)]),
      ]],
      ['Shutdown & lockout', PH.lock, [
        S('Wash up & shut down\n- [ ] Stock off the headbox\n- [ ] Wash up fabric, foils & flat boxes\n- [ ] Vacuum off', 'Machine tender', 1),
        S('Lock out the fourdrinier\n- [ ] Fabric & couch drives\n- [ ] Fan pump & vacuum pump\n- [ ] Stretch & guide air bled\n- [ ] Try-out verified', 'Shift lead', 0.5,
          [sub('Isolation list\n- PM1 forming section lockout sheet', HAZ)]),
      ]],
      ['Remove old fabric', PH.out, [
        S('Cantilever the table\n- [ ] Cantilever beams in\n- [ ] Back-side fillers / spool pieces out\n- [ ] Tag & bag all hardware', 'Maint mechanic', 1.5),
        S('Slack & cut out the old fabric\n- [ ] Stretch roll to minimum\n- [ ] Center the guide\n- [ ] Cut and pull out tender side', 'Back tender', 0.5,
          [sub('Hazards\n- Cut fabric edges are sharp: cut gloves\n- Stored energy in the stretch roll', HAZ)]),
      ]],
      ['Clean & inspect', PH.insp, [
        S('Table & boxes\n- [ ] Forming board & foils: wear, chips\n- [ ] Flat box covers & slots\n- [ ] Couch roll holes & seal strips\n- [ ] Breast roll cover', 'Machine tender', 1.5),
        S('Headbox approach\n- [ ] Approach piping clean (no wads)\n- [ ] Slice lip & edges\n- [ ] Fan pump strainer', 'Back tender', 1,
          [sub('Why: the Feb hole was a wad off the approach piping. Clean it every change.', SPEC)]),
        S('Rolls, showers & doctors\n- [ ] Return rolls & bearings\n- [ ] Showers clear, oscillators work\n- [ ] Doctor blades changed\n- [ ] Saveall pans clean', 'Back tender', 1),
      ]],
      ['Install new fabric', PH.in, [
        S('Pull in the new fabric\n- [ ] Run direction arrow correct\n- [ ] Pull evenly tender → drive side\n- [ ] Seam square to machine direction', 'Wet end crew', 1),
        S('Close up the table\n- [ ] Fillers / spool pieces back in\n- [ ] Cantilever beams out\n- [ ] All hardware accounted for', 'Maint mechanic', 1),
        S('Tension & square\n- [ ] Tension to spec\n- [ ] Diagonals equal\n- [ ] Guide centered', 'Back tender', 0.5,
          [sub('Record\n- Tension (kN/m):\n- Diagonals TS / DS:', SPEC)]),
      ]],
      ['Startup', PH.start, [
        S('Remove locks & walk down\n- [ ] Area clear, tools out\n- [ ] Locks off per procedure\n- [ ] Showers on before the fabric moves', 'Shift lead', 0.5),
        S('Run in the fabric\n- [ ] Crawl with showers on, watch the seam\n- [ ] Guiding & tracking\n- [ ] Up to speed, then stock on', 'Machine tender', 1),
        S('Close out\n- [ ] Log the install date in My Machine\n- [ ] Wear findings → Northbank survey\n- [ ] Punch list to maintenance', 'Superintendent', 0.5),
      ]],
    ] },
  { id: 'sm-press-felt', name: 'Press Felt Change',
    meta: { area: 'Press section', hours: 6, crew: 5, desc: 'One felt on the 2-nip press: 1st or 2nd press, top or bottom. Includes the Uhle box, HP shower and strainer checks.' },
    phases: [
      ['Before the outage', PH.prep, [
        S('Confirm the new felt\n- [ ] Position: 1st / 2nd press, top / bottom\n- [ ] Design & size match the spec\n- [ ] Endless or seamed: install method', 'Superintendent', 1,
          [sub('Felt spec card\n- 1st press: Halden (1300 gsm seamed top, 1500 gsm endless bottom)\n- 2nd press: Marlow (1400 gsm seamed top, 1600 gsm endless bottom)\n- Target tension', SPEC)]),
        S('Stage tools & equipment\n- [ ] Felt cart / sling\n- [ ] Cantilever equipment checked\n- [ ] HP shower nozzles & Uhle cover spares', 'Back tender', 1),
        S('Pre-job brief\n- [ ] Walk the job with the crew\n- [ ] Review JSA & lockout list', 'Shift lead', 0.5,
          [sub('Hazards\n- Press nips & stored hydraulic energy\n- Heavy rolls & overhead lifts\n- Hot shower water', HAZ)]),
      ]],
      ['Shutdown & lockout', PH.lock, [
        S('Wash up & unload the press\n- [ ] Sheet off\n- [ ] Open the nips\n- [ ] Showers & Uhle vacuum off', 'Machine tender', 0.5),
        S('Lock out the press\n- [ ] Press drives\n- [ ] Loading hydraulics bled down\n- [ ] Vacuum, showers, stretch & guide air\n- [ ] Try-out verified', 'Shift lead', 0.5),
      ]],
      ['Remove old felt', PH.out, [
        S('Cantilever the press\n- [ ] Cantilever / lift equipment in\n- [ ] Back-side fillers out on the felt run', 'Maint mechanic', 1),
        S('Slack & remove the old felt\n- [ ] Stretch to minimum, guide centered\n- [ ] Cut out (endless) or open the seam\n- [ ] Pull out tender side\n- [ ] Cut a sample for the vendor', 'Back tender', 0.5),
      ]],
      ['Clean & inspect', PH.insp, [
        S('Uhle box\n- [ ] Cover: wear, grooves, edges\n- [ ] Deckles set\n- [ ] Clear plugged slots', 'Machine tender', 1),
        S('Showers & strainer\n- [ ] HP oscillating shower: every nozzle clear\n- [ ] Shower supply strainer cleaned\n- [ ] Lube showers clear', 'Back tender', 1,
          [sub('Why: plugged nozzles let the 2nd press top felt fill in 3 weeks in May. Clean the strainer every outage.', SPEC)]),
        S('Rolls & doctors\n- [ ] Felt rolls: covers, bearings\n- [ ] Press roll doctor blades', 'Maint mechanic', 0.5),
      ]],
      ['Install new felt', PH.in, [
        S('Install the new felt\n- [ ] Run direction arrow correct\n- [ ] Slide on evenly tender → drive side\n- [ ] Close the seam if seamed', 'Wet end crew', 1),
        S('Close up & tension\n- [ ] Fillers back in, cantilever out\n- [ ] Tension to spec\n- [ ] Guide centered', 'Maint mechanic', 0.5,
          [sub('Record\n- Tension:\n- Uhle vacuum at start-up:', SPEC)]),
      ]],
      ['Startup', PH.start, [
        S('Remove locks & load the press\n- [ ] Walk down, locks off\n- [ ] Showers on before the felt moves\n- [ ] Load nips to setpoint', 'Shift lead', 0.5),
        S('Run in & condition\n- [ ] Crawl with HP & lube showers on\n- [ ] Watch Uhle vacuum & felt moisture\n- [ ] Sheet on, check press solids', 'Machine tender', 1),
        S('Close out\n- [ ] Log the install date in My Machine\n- [ ] Felt sample → vendor\n- [ ] Note Uhle vacuum for the trend', 'Superintendent', 0.5),
      ]],
    ] },
  { id: 'sm-dryer-felt', name: 'Dryer Felt Change',
    meta: { area: 'Dryer section', hours: 6, crew: 5, desc: 'One uno-run dryer felt (sections 1 to 4). The new felt is pulled in behind the old one and seamed; the section’s five felt rolls are checked on the way.' },
    phases: [
      ['Before the outage', PH.prep, [
        S('Confirm the new felt\n- [ ] Section 1-2: Northbank, 3-4: Corrie\n- [ ] Length, width & seam type\n- [ ] Pintle wire & seam tools on site', 'Superintendent', 1),
        S('Stage tools & equipment\n- [ ] Felt cart / sling\n- [ ] Pull-in rope & clamps\n- [ ] Radios for both sides\n- [ ] Heat-resistant gloves', 'Dryer tender', 1),
        S('Pre-job brief\n- [ ] Roles: tender side / drive side / drive control\n- [ ] Review JSA & lockout list\n- [ ] Agree crawl signals', 'Shift lead', 0.5,
          [sub('Hazards\n- Hot cans, steam & condensate\n- In-running nips at felt rolls\n- Working in the hood', HAZ)]),
      ]],
      ['Shutdown & lockout', PH.lock, [
        S('Cool down the section\n- [ ] Steam off, condensate drained\n- [ ] Hood doors open, ventilation on\n- [ ] Cans cool enough to work near', 'Dryer tender', 1.5),
        S('Lock out\n- [ ] Steam & condensate valves\n- [ ] Felt stretch & guide air\n- [ ] Drive: crawl only under the controlled procedure', 'Shift lead', 0.5),
      ]],
      ['Change the felt', PH.out, [
        S('Join new felt to old\n- [ ] Lay new felt at the lead-in point\n- [ ] Run direction arrow correct\n- [ ] Clamp / rope lead end to old felt', 'Dryer crew', 0.5),
        S('Pull in at crawl\n- [ ] Spotters on both sides with radios\n- [ ] Stop with the seam at the join position\n- [ ] Detach and roll out the old felt', 'Dryer crew', 1,
          [sub('Hazards\n- Never reach into a moving felt run\n- Stop the crawl on any signal', HAZ)]),
      ]],
      ['Clean & inspect', PH.insp, [
        S('Felt rolls 1-5\n- [ ] Each turns freely, no bearing noise\n- [ ] Cover cracks or swelling\n- [ ] Felt roll doctors', 'Maint mechanic', 1,
          [sub('Any roll near its 3-year target: log it in My Machine and plan the Felt Roll Change.', SPEC)]),
        S('Cans & pockets\n- [ ] Can doctor blades\n- [ ] Pocket ventilation boxes\n- [ ] Rotary joints & syphons: leaks\n- [ ] Tail ropes & sheaves', 'Dryer tender', 1),
      ]],
      ['Close & tension', PH.in, [
        S('Close the seam\n- [ ] Loops lined up edge to edge\n- [ ] Insert pintle full width\n- [ ] Trim & secure pintle ends', 'Dryer crew', 0.5),
        S('Tension & guide\n- [ ] Tension to spec\n- [ ] Guide centered, edges clear the frames', 'Dryer tender', 0.5),
      ]],
      ['Startup', PH.start, [
        S('Remove locks & walk down\n- [ ] Hood clear, tools out\n- [ ] Locks off per procedure', 'Shift lead', 0.5),
        S('Steam up & run in\n- [ ] Warm up on the steam curve\n- [ ] Watch the seam pass at crawl\n- [ ] Check tracking at speed', 'Dryer tender', 1),
        S('Close out\n- [ ] Log the install date in My Machine\n- [ ] Old felt condition → vendor', 'Superintendent', 0.5),
      ]],
    ] },
  { id: 'sm-felt-roll', name: 'Felt Roll Change',
    meta: { area: 'Dryer section', hours: 4, crew: 4, desc: 'Swap a dryer felt roll for a recovered spare from Pellham Roll Service. Usually done with the section’s felt slack.' },
    phases: [
      ['Before the outage', PH.prep, [
        S('Spare roll ready\n- [ ] Recovered spare on site, serial noted\n- [ ] Bearings & journals checked on receipt\n- [ ] Lifting lugs & sling rated', 'Superintendent', 0.5),
        S('Plan the lift\n- [ ] Crane booked & inspected\n- [ ] Rigging plan for the section\n- [ ] Roll cradle staged', 'Maint mechanic', 1,
          [sub('Hazards\n- Suspended loads over walkways\n- Hot cans next to the roll\n- Pinch points at the bearing housings', HAZ)]),
      ]],
      ['Shutdown & lockout', PH.lock, [
        S('Cool down & slack the felt\n- [ ] Steam off, section cooled\n- [ ] Felt stretch to minimum', 'Dryer tender', 1),
        S('Lock out\n- [ ] Drive group\n- [ ] Stretch & guide air\n- [ ] Lube oil to the roll', 'Shift lead', 0.5),
      ]],
      ['Change the roll', PH.out, [
        S('Remove the old roll\n- [ ] Disconnect lube lines\n- [ ] Unbolt bearing housings\n- [ ] Lift out to the cradle', 'Maint mechanic', 1),
        S('Install the spare\n- [ ] Bearings seated, housings torqued\n- [ ] Level & aligned to the cans\n- [ ] Lube lines reconnected, oil flowing', 'Maint mechanic', 1,
          [sub('Record\n- Serial in:\n- Serial out:\n- Alignment readings:', SPEC)]),
      ]],
      ['Startup', PH.start, [
        S('Restore & run\n- [ ] Felt re-tensioned, guide centered\n- [ ] Locks off\n- [ ] Listen at crawl: bearing noise, rubbing', 'Dryer tender', 0.5),
        S('Close out\n- [ ] Log the roll in My Machine\n- [ ] Old roll shipped to Pellham for recovery', 'Superintendent', 0.5),
      ]],
    ] },
  { id: 'sm-refiner-plates', name: 'Refiner Plate Change',
    meta: { area: 'Refiners', hours: 4, crew: 3, desc: 'Change one set of 34" LC plates on REF 1 or REF 2 (Ridgeway Refining): open the refiner, swap rotor and stator plates, set the gap.' },
    phases: [
      ['Before the outage', PH.prep, [
        S('Plates on hand\n- [ ] Ridgeway 34" LC set, pattern RR-34LC-30\n- [ ] Bolts, gaskets & plate tools\n- [ ] One set per refiner being changed', 'Superintendent', 0.5,
          [sub('If both refiners are due, two sets are needed. Check Consumables before the outage.', SPEC)]),
        S('Pre-job brief\n- [ ] Review JSA & lockout list\n- [ ] Plan the lift for the door', 'Shift lead', 0.5,
          [sub('Hazards\n- Heavy plates: two-person lift or hoist\n- Sharp bar edges\n- Stock lines under pressure until drained', HAZ)]),
      ]],
      ['Shutdown & lockout', PH.lock, [
        S('Isolate the refiner\n- [ ] Stock off, line drained\n- [ ] Motor locked out\n- [ ] Gap actuator & hydraulics bled', 'Shift lead', 0.5),
      ]],
      ['Change the plates', PH.out, [
        S('Open & remove\n- [ ] Open the refiner door\n- [ ] Remove rotor & stator plates\n- [ ] Clean the seats', 'Maint mechanic', 1),
        S('Inspect the old set\n- [ ] Bar wear (%) & pattern\n- [ ] Leading edges rounded?\n- [ ] Sand or tramp metal marks', 'Superintendent', 0.5,
          [sub('Record\n- Bar wear:\n- Days in service:\n- Send photos to Ridgeway', SPEC)]),
        S('Fit the new set\n- [ ] Plates seated, bolts torqued in pattern\n- [ ] Door closed, gasket OK', 'Maint mechanic', 1),
      ]],
      ['Startup', PH.start, [
        S('Set the gap & load\n- [ ] Zero the gap\n- [ ] Stock on, load slowly\n- [ ] Specific energy to target', 'Stock prep operator', 0.5),
        S('Close out\n- [ ] Log the plate change in My Machine\n- [ ] Plate report request to Ridgeway\n- [ ] Plates used → Consumables', 'Superintendent', 0.5),
      ]],
    ] },
  { id: 'sm-stock-prep-cleaners', name: 'Stock Prep Cleaners',
    meta: { area: 'Stock prep', hours: 6, crew: 3, desc: 'HD, LC and LW cleaner banks: isolate, pull and inspect cones, clear rejects and sand traps, reassemble and set pressure drop.' },
    phases: [
      ['Before the outage', PH.prep, [
        S('Plan the scope\n- [ ] Which banks: HD / LC / LW\n- [ ] Pull pressure-drop trends & last findings\n- [ ] Cones, tips & gaskets on hand', 'Superintendent', 1),
        S('Pre-job brief\n- [ ] Review JSA & lockout list\n- [ ] Assign banks to people', 'Shift lead', 0.5,
          [sub('Hazards\n- Hot stock & water\n- Lines under pressure until drained\n- Slippery floors', HAZ)]),
      ]],
      ['Shutdown & lockout', PH.lock, [
        S('Isolate & drain\n- [ ] Stop cleaner feed pumps\n- [ ] Close feed, accepts, rejects & dilution valves\n- [ ] Drain headers', 'Stock prep operator', 1),
      ]],
      ['Clean & inspect', PH.insp, [
        S('Pull & inspect cones\n- [ ] Remove cones bank by bank\n- [ ] Apex tips: wear & plugging\n- [ ] Inlet nozzles & vortex finders', 'Stock prep crew', 2,
          [sub('Why: sand carry-over from the LC cleaners wears the REF 2 plates. Check the LC sand trap and reject rates.', SPEC)]),
        S('Headers, rejects & sand traps\n- [ ] Flush inlet & accepts headers\n- [ ] Clear rejects lines & sight glasses\n- [ ] Sand traps emptied, timers checked', 'Stock prep crew', 1),
      ]],
      ['Startup', PH.start, [
        S('Leak check & restart\n- [ ] Locks off\n- [ ] Fill slowly, check every cone\n- [ ] Pressure drop to target', 'Stock prep operator', 0.5),
        S('Close out\n- [ ] Readings logged for the trend\n- [ ] Parts used → reorder', 'Superintendent', 0.5),
      ]],
    ] },
];

// The step list Outage Planning copies onto an outage (same as libPhases() in OperationsOutagePlanning.html).
const firstLine = t => { const ls = (t || '').split('\n'); const i = ls.findIndex(l => l.trim()); return { title: i < 0 ? '' : ls[i].replace(/^#+\s*/, '').trim(), rest: i < 0 ? [] : ls.slice(i + 1) }; };
function phasesOf(b){
  const notes = b.notes, tops = Object.values(notes).filter(n => !n.parent || !notes[n.parent]);
  const cx = n => (n.x || 0) + (n.w || 236) / 2, cy = n => (n.y || 0) + 50;
  const byPos = (a, c) => ((a.y || 0) - (c.y || 0)) || ((a.x || 0) - (c.x || 0));
  const step = n => { const { title, rest } = firstLine(n.text);
    return { id: n.id, title: title || 'Untitled step', lines: rest.filter(l => l.trim()), who: n.owner || null, hrs: Number(n.hrs) > 0 ? Number(n.hrs) : null,
             subs: (n.children || []).map(c => notes[c]).filter(Boolean).map(c => (c.text || '').trim()).filter(Boolean) }; };
  const used = new Set(), phases = [];
  for (const f of b.frames.slice().sort((a, c) => ((a.x || 0) - (c.x || 0)) || ((a.y || 0) - (c.y || 0)))){
    const inF = tops.filter(n => !used.has(n.id) && cx(n) >= f.x && cx(n) <= f.x + f.w && cy(n) >= f.y && cy(n) <= f.y + f.h).sort(byPos);
    inF.forEach(n => used.add(n.id));
    if (inF.length) phases.push({ title: f.title || 'Phase', color: f.color || null, steps: inF.map(step) });
  }
  return phases;
}

const rec = {}, phases = {};
PACKAGES.forEach((x, i) => {
  const b = buildExample(x);
  b.created = created; b.meta = { ...x.meta };                      // Sim Mill's own library, not the stock examples
  rec['p:' + b.id] = { name: b.name, meta: b.meta, created, sort: i };
  for (const n of Object.values(b.notes)){ const d = { ...n }; delete d.id; d.attachments = []; rec[`n:${b.id}:${n.id}`] = d; }
  for (const l of b.links){ const d = { ...l }; delete d.id; rec[`l:${b.id}:${l.id}`] = d; }
  for (const f of b.frames){ const d = { ...f }; delete d.id; rec[`f:${b.id}:${f.id}`] = d; }
  phases[b.id] = { name: b.name, meta: b.meta, phases: phasesOf(b) };
});
rec.seeded = { at: created };
fs.mkdirSync(path.join(out, 'records'), { recursive: true });
fs.writeFileSync(path.join(out, 'records', 'task-packages.json'), JSON.stringify(rec, null, 1));
fs.writeFileSync(path.join(out, 'records', '_package_phases.json'), JSON.stringify(phases, null, 1));
console.log(`task packages: ${PACKAGES.length} (${Object.keys(rec).length} records)`);
