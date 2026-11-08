// Machine Manager — sample data for Operations Outage Planning in demo mode (signed out).
// Outages sit on the 6-week grid (anchored Nov 11, 2026) counting from today, so the demo always shows:
//   · the last outage, finished: tasks done, a package worked through, full manning
//   · the next outage, mid-planning: tasks, two packages with the prep steps ticked, manning filled
//   · the one after, started: a wire change package, a couple of tasks, the shutdown crew
//   · two more normal outages and an annual one, mostly empty
// Package steps are copied from the Ops Task Library examples (mm-task-examples.js) by the page,
// which passes phasesOf(packageId) and metaOf(packageId) in.
(() => {
  const ANCHOR = '2026-11-11', CADENCE = 42;

  // Generic crew names: initial + surname, the way a shift sheet reads.
  const CREW_A = ['R. Dube', 'K. Lavoie', 'M. Tremblay', 'J. Ouellet', 'S. Martin', 'D. Gagnon', 'P. Roy', 'T. Bouchard', 'L. Pelletier', 'A. Cote'];
  const CREW_B = ['B. Fortin', 'C. Morin', 'G. Leblanc', 'H. Nadeau', 'N. Caron', 'E. Girard', 'F. Poirier', 'V. Simard', 'W. Boucher', 'Y. Paquette'];
  const CREW_D = ['J. Hebert', 'M. Belanger', 'R. Levesque', 'K. Bergeron', 'S. Cloutier', 'D. Dion', 'P. Lapointe', 'T. Mercier', 'O. Gauthier', 'I. Ricard'];
  const POS = ['SPOT', 'WET', 'DET', 'SPAT', 'WT', 'WAT', 'IB1', 'IB2', 'OB1', 'EXTRA'];
  const seats = (names, n = POS.length) => Object.fromEntries(POS.slice(0, n).map((p, i) => [p, names[i]]));

  const TASK_COLORS = ['#fff4b8', '#d4ecff', '#d9f3d3', '#ffd8e1', '#e9e0ff', '#ffe2c4'];

  function build({ addDays, daysBetween, today, phasesOf, metaOf }){
    // Outage dates: the last one on the grid on or before today, then the next five.
    const n = Math.floor(daysBetween(ANCHOR, today) / CADENCE);
    let first = addDays(ANCHOR, n * CADENCE);
    if (first > today) first = addDays(first, -CADENCE);       // before the anchor, floor() rounds toward zero
    const D = k => addDays(first, k * CADENCE);                 // D(0) = last, D(1) = next, …
    const ids = ['demo-o0', 'demo-o1', 'demo-o2', 'demo-o3', 'demo-o4', 'demo-o5'];
    const r = { settings: { cadenceDays: CADENCE, anchor: ANCHOR, setUp: true, demo: true } };
    ids.forEach((id, k) => { r['outage:' + id] = { date: D(k), type: k === 5 ? 'annual' : 'normal' }; });

    let at = Date.parse(first + 'T08:00:00Z') - 30 * 864e5, tn = 0;
    const task = (o, text, done) => { r[`task:${o}-t${++tn}`] = { outage: o, text, done: !!done, at: at += 60000, color: TASK_COLORS[tn % TASK_COLORS.length] }; };
    // A package on an outage: the library copy at the time it was added, plus which steps are ticked.
    const pkg = (o, src, tick) => {
      const phases = phasesOf(src); if (!phases || !phases.length) return;
      const m = metaOf(src) || {}, id = `${o}-${src}`;
      r['pkg:' + id] = { outage: o, source: src, name: m.name, area: m.area || null, desc: m.desc || null,
        hours: Number(m.hours) || null, crew: Number(m.crew) || null, at: at += 60000, phases, demo: true };
      phases.forEach((ph, i) => ph.steps.forEach(st => { if (tick(i, phases.length)) r[`pkd:${id}:${st.id}`] = { done: true, at: at += 1000 }; }));
    };
    const man = (o, shift, names, nSeats) => { r[`man:${o}:${shift}`] = seats(names, nSeats); };

    // ---- Last outage: done ----
    const o0 = ids[0];
    task(o0, 'Clean and check all whitewater showers — top & base former', true);
    task(o0, 'Pull and clean Uhle box covers, check for wear', true);
    task(o0, 'Hose down press pit and clear felt hairs from saveall', true);
    task(o0, 'Check doctor blades on 2nd section cans — log any changed', true);
    pkg(o0, 'ex-stock-prep-cleaners', () => true);
    man(o0, 'shutdown', CREW_A); man(o0, 'shortoff', CREW_B); man(o0, 'day', CREW_D);
    r[`man:${o0}:startup`] = { WT: 'G. Leblanc', EXTRA: 'N. Caron' };      // two changes from the shutdown crew

    // ---- Next outage: being planned ----
    const o1 = ids[1];
    task(o1, 'Stage new press felt and tandem felt at the press — confirm sizes with Halden', true);
    task(o1, 'Order pintle wire and seam kit for 2nd section top felt', true);
    task(o1, 'Clean HP shower nozzles on both formers; replace any plugged', false);
    task(o1, 'Uhle box covers: swap the two worst (inventory UB-07, UB-11)', false);
    task(o1, 'Refiner plates: count sets on hand before BP 2 change', false);
    task(o1, 'Confirm crane and riggers booked for 06:00', false);
    pkg(o1, 'ex-press-felt-change', i => i === 0);                         // prep phase done
    pkg(o1, 'ex-dryer-felt-change', i => i === 0);
    man(o1, 'shutdown', CREW_A); man(o1, 'shortoff', CREW_B, 8); man(o1, 'day', CREW_D, 9);
    r[`man:${o1}:startup`] = { SPAT: 'H. Nadeau' };

    // ---- The one after: started ----
    const o2 = ids[2];
    task(o2, 'Get the BP wire on site — check delivery date with Northbank', false);
    task(o2, 'Book an extra hand for the wire pull-in', false);
    pkg(o2, 'ex-bp-wire-change', () => false);
    man(o2, 'shutdown', CREW_B, 6);

    // ---- Further out ----
    task(ids[3], 'Plan TP wire change if the trial style isn’t back by then', false);
    task(ids[5], 'Annual: get the maintenance scope list from the planner', false);
    task(ids[5], 'Annual: book contractors for the hood clean', false);
    return r;
  }

  window.MMDemoOutages = { build };
})();
