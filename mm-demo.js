// Machine Manager — sample data for My Machine when signed out and the server can't be reached (otherwise signed-out visitors
// see the Sim Mill demo org, read-only). Also what the home page shows in that case.
// Dates are laid out on the 6-week outage grid (anchored Nov 11, 2026, same as Outage Planning) counting
// back from today, so the ages stay realistic whenever the demo is opened.
(() => {
  const MM = window.MMMachine;
  const ANCHOR = '2026-11-11', CADENCE = 42;

  function build(){
    const today = MM.todayStr();
    const n = Math.floor(MM.daysBetween(ANCHOR, today) / CADENCE);
    const last = MM.addDays(ANCHOR, n * CADENCE);              // most recent outage on or before today
    const O = k => MM.addDays(last, -(k - 1) * CADENCE);       // O(1) = last outage, O(2) = the one before…
    const run = (installed, removed, x) => Object.assign({ installed, removed, days: MM.daysBetween(installed, removed) }, x);
    const items = {};

    // ---------- Base ply forming fabric: six runs, fully filled out ----------
    const NB = { vendor: 'Northbank Fabrics', style: 'NX-2740 triple layer' };
    const shut = MM.addDays(O(6), 29);                         // unplanned shut after a hole
    items['form-bottom'] = {
      installed: O(2), target: 12, targetUnit: 'weeks', ...NB, serial: 'NB-26-21907',
      condition: 'wear', conditionDate: MM.addDays(today, -5),
      conditionNote: 'Edge wear at TS starting to show; vac box pressures creeping up.',
      note: 'Normal break-in. Drainage and retention steady through week 8.',
      history: [
        run(O(11), O(9), { ...NB, serial: 'NB-25-11842', reason: 'planned', condition: 'worn',
          note: 'Ran full 12 weeks. Couch vac up 1.5 inHg over the last two weeks; sheet moisture at the press still in spec.' }),
        run(O(9), O(8), { vendor: 'Halden Felt Co.', style: 'PF-3315 (trial)', serial: 'HF-25-40377', reason: 'performance', condition: 'good',
          note: 'Vendor trial style. Formation was fine but drainage was slower — had to run 4% more vacuum and lost ~15 fpm. Pulled at the outage and went back to the NX-2740.' }),
        run(O(8), O(6), { ...NB, serial: 'NB-25-12610', reason: 'planned', condition: 'worn',
          note: 'Full 12 weeks. Light filling at the edges, cleaned with HP showers at week 9.' }),
        run(O(6), shut, { ...NB, serial: 'NB-26-13054', reason: 'damaged', condition: 'damaged',
          note: '4-inch hole at the TS from a wad off the lumpbreaker. 10-hour unplanned shut to change. Lumpbreaker doctor blade replaced at the same time.' }),
        run(shut, O(4), { ...NB, serial: 'NB-26-13981', reason: 'planned', condition: 'wear',
          note: 'Spare off the floor. Changed early at the outage to get back on the outage cycle.' }),
        run(O(4), O(2), { ...NB, serial: 'NB-26-20455', reason: 'planned', condition: 'worn',
          note: 'Ran full 12 weeks. Seam held well; wear on the machine side was even across the width.' })
      ]
    };

    // ---------- Everything else: realistic ages and a couple of earlier runs ----------
    // cur = installed at outage O(cur); life = target in weeks
    const SPEC = {
      'ref-bp1':        { cur: 1,  life: 12, vendor: 'Ridgeway Refining', style: '36" LC plate, 3.0/4.0 bar/groove' },
      'ref-bp2':        { cur: 2,  life: 12, vendor: 'Ridgeway Refining', style: '36" LC plate, 3.0/4.0 bar/groove' },
      'ref-tp1':        { cur: 1,  life: 12, vendor: 'Brennock Plates', style: '34" plate, 2.5/3.5 bar/groove' },
      'ref-tp2':        { cur: 1,  life: 12, vendor: 'Brennock Plates', style: '34" plate, 2.5/3.5 bar/groove' },
      'form-top':       { cur: 2,  life: 14, vendor: 'Northbank Fabrics', style: 'TP 2160 triple layer' },
      'lumpbreaker':    { cur: 8,  life: 52, vendor: 'Pellham Roll Service', style: 'Rubber cover, 35 P&J', roll: true },
      'p1-felt-top':    { cur: 1,  life: 6,  vendor: 'Halden Felt Co.', style: 'Seamed felt, 1350 g/m²' },
      'p2-felt-top':    { cur: 2,  life: 12, vendor: 'Halden Felt Co.', style: 'Seamed felt, 1450 g/m²' },
      'p-tandem-felt':  { cur: 1,  life: 6,  vendor: 'Marlow Press Fabrics', style: 'Bottom felt, 1600 g/m²',
                          condition: 'worn', conditionNote: 'Filling up — Uhle box vacuum up 2 inHg, moisture streak at the FS.', flaggedDaysAgo: 3 },
      'p1-roll-top':    { cur: 9,  life: 104, vendor: 'Pellham Roll Service', style: 'Granite-style composite cover', roll: true },
      'p1-roll-bottom': { cur: 6,  life: 104, vendor: 'Pellham Roll Service', style: 'Suction roll, rubber 10 P&J', roll: true },
      'p2-roll-top':    { cur: 11, life: 78, vendor: 'Pellham Roll Service', style: 'Composite cover', roll: true },
      'p2-roll-bottom': { cur: 14, life: 78, vendor: 'Pellham Roll Service', style: 'Blind-drilled rubber, 12 P&J', roll: true,
                          condition: 'wear', conditionNote: 'Cover hardness up 3 P&J; crown OK on last check.', flaggedDaysAgo: 12 },
      'd1-felt':        { cur: 7,  life: 52, vendor: 'Northbank Fabrics', style: 'Dryer fabric, spiral seam' },
      'd2-felt-top':    { cur: 5,  life: 52, vendor: 'Northbank Fabrics', style: 'Dryer fabric, pin seam',
                          condition: 'damaged', conditionNote: 'Seam starting to open at the FS (~6 in). Patched to hold until the outage.', flaggedDaysAgo: 1 },
      'd2-felt-bottom': { cur: 8,  life: 52, vendor: 'Northbank Fabrics', style: 'Dryer fabric, pin seam' },
      'd3-felt-top':    { cur: 4,  life: 65, vendor: 'Corrie Textiles', style: 'Dryer fabric, spiral seam' },
      'd3-felt-bottom': { cur: 10, life: 78, vendor: 'Corrie Textiles', style: 'Dryer fabric, spiral seam' },
      'cal-top':        { cur: 12, life: 104, vendor: 'Teague Roll Works', style: 'Chilled iron', roll: true },
      'cal-bottom':     { cur: 3,  life: 104, vendor: 'Teague Roll Works', style: 'Soft cover, 85 Shore D', roll: true }
    };
    const NOTES = {
      fabric: ['Normal wear at removal.', 'Ran to target; even wear across the width.', 'Some edge filling, nothing unusual.'],
      roll: ['Sent out for regrind; crown re-checked.', 'Recovered and reground at the shop.', 'Normal cover wear; regrind.'],
      refiner: ['Bars worn as expected; energy per ton steady to the end.', 'Normal wear; slight rounding at the leading edge.', 'Changed on schedule.']
    };
    let sn = 30000;
    const serial = v => `${v.split(/\s+/).map(w => w[0]).join('').toUpperCase()}-${++sn}`;
    for (const [id, s] of Object.entries(SPEC)){
      const kind = id.startsWith('ref-') ? 'refiner' : s.roll ? 'roll' : 'fabric';
      const len = Math.max(1, Math.round(s.life * 7 / CADENCE));   // outages per run at target life
      const runs = kind === 'roll' ? 1 : 2;
      const history = [];
      for (let r = runs; r >= 1; r--){
        const a = O(s.cur + r * len), b = O(s.cur + (r - 1) * len);
        history.push(run(a, b, { vendor: s.vendor, style: s.style, serial: serial(s.vendor), reason: 'planned',
          condition: r % 2 ? 'worn' : 'wear', note: NOTES[kind][(sn + r) % 3] }));
      }
      items[id] = {
        installed: O(s.cur), target: s.life, targetUnit: 'weeks', vendor: s.vendor, style: s.style, serial: serial(s.vendor),
        note: '', condition: s.condition || 'good', conditionNote: s.conditionNote || '',
        conditionDate: s.condition ? MM.addDays(today, -(s.flaggedDaysAgo || 0)) : '',
        history
      };
    }
    return { machine: MM.normalize(JSON.parse(JSON.stringify(MM.DEFAULT_MACHINE))), items, demo: true };
  }

  window.MMDemo = { build };
})();
