// Machine Manager — the example task packages: shown in the Ops Task Library (demo and new organizations)
// and used by Operations Outage Planning's demo. Exposes window.MMTaskExamples = { examples, buildExample }.
window.MMTaskExamples = (() => {
  /* ================= Example packages ================= */
  // Each phase is a frame (left → right); each step is a card; arrows run step to step.
  // Ids are fixed so two people seeding the same organization at once end up with one copy.
  const PH = { prep:'#64748b', lock:'#dc2626', out:'#d97706', insp:'#0891b2', in:'#2563eb', start:'#16a34a' };
  const HAZ = '#ffd8e1', SPEC = '#d4ecff';
  const S = (text, who, hrs, sub) => ({ text, who, hrs, sub });
  const sub = (text, color) => ({ text, color });

  function wireSteps(ply){
    const bp = ply === 'BP', former = bp ? 'base former' : 'top former', box = bp ? 'base ply headbox' : 'top ply headbox';
    return [
      ['Before the outage', PH.prep, [
        S(`Confirm the new ${ply} wire\n- [ ] On site: right position, length & width\n- [ ] Style matches the spec sheet\n- [ ] Run direction & seam marked`, 'Superintendent', 1,
          [sub(`Wire spec card\n- Supplier · style · length × width\n- Target tension (kN/m)\n- Last install date (My Machine)`, SPEC)]),
        S(`Stage tools & equipment\n- [ ] Wire carts / pull ropes\n- [ ] Cantilever beams & jacks checked\n- [ ] Knives, tape, wire markers\n- [ ] Spare shower nozzles`, 'Back tender', 1),
        S(`Pre-job brief\n- [ ] Walk the job with the crew\n- [ ] Assign tender / drive side roles\n- [ ] Review JSA & lockout list`, 'Shift lead', 0.5,
          [sub(`Hazards\n- Pinch points at rolls\n- Wet, slippery floors\n- Overhead lifts — use tag lines`, HAZ)]),
      ]],
      ['Shutdown & lockout', PH.lock, [
        S(`Wash up & shut down\n- [ ] Stock off the ${box}\n- [ ] Wash up wire, foils & pans\n- [ ] Vacuum off`, 'Machine tender', 1),
        S(`Lock out the ${former}\n- [ ] Wire & couch drives\n- [ ] Vacuum pumps & showers\n- [ ] Stretch & guide air bled\n- [ ] Try-out verified`, 'Shift lead', 0.5,
          [sub(`Isolation list\n- Attach the PM1 ${former} lockout sheet`, HAZ)]),
      ]],
      ['Remove old wire', PH.out, [
        S(`Cantilever the ${former}\n- [ ] Install cantilever beams\n- [ ] Pull back-side fillers / spool pieces\n- [ ] Tag & bag all hardware`, 'Maint mechanic', 1.5),
        S(`Slack & cut out the old wire\n- [ ] Stretch roll to minimum\n- [ ] Center the guide\n- [ ] Cut and pull out tender side`, 'Back tender', 0.5,
          [sub(`Hazards\n- Cut wire edges are sharp — cut gloves\n- Stored energy in the stretch roll`, HAZ)]),
      ]],
      ['Clean & inspect', PH.insp, [
        S(bp ? `Forming section\n- [ ] Forming board & foils: wear, chips\n- [ ] Vacuum box covers\n- [ ] Lumpbreaker roll & doctor\n- [ ] Couch roll holes & seal strips`
             : `Top former\n- [ ] Forming shoe / blades: wear, chips\n- [ ] Vacuum box covers\n- [ ] Ply combining point & transfer box\n- [ ] Couch / turning roll covers`, 'Machine tender', 1.5),
        S(`Rolls, showers & doctors\n- [ ] Wire return rolls & bearings\n- [ ] Showers clear, oscillators work\n- [ ] Doctor blades changed\n- [ ] Saveall pans clean`, 'Back tender', 1),
      ]],
      ['Install new wire', PH.in, [
        S(`Pull in the new wire\n- [ ] Run direction arrow correct\n- [ ] Pull evenly tender → drive side\n- [ ] Seam square to machine direction`, 'Wet end crew', 1),
        S(`Close up the ${former}\n- [ ] Fillers / spool pieces back in\n- [ ] Cantilever beams out\n- [ ] All hardware accounted for`, 'Maint mechanic', 1),
        S(`Tension & square\n- [ ] Tension to spec\n- [ ] Diagonals equal (squareness)\n- [ ] Guide centered`, 'Back tender', 0.5,
          [sub(`Record\n- Tension (kN/m):\n- Diagonals TS / DS:`, SPEC)]),
      ]],
      ['Startup', PH.start, [
        S(`Remove locks & walk down\n- [ ] Area clear, tools out\n- [ ] Locks off per procedure\n- [ ] Showers on before the wire moves`, 'Shift lead', 0.5),
        S(`Run in the wire\n- [ ] Crawl with showers on, watch the seam\n- [ ] Check guiding & tracking\n- [ ] Up to speed, then stock on`, 'Machine tender', 1),
        S(`Close out\n- [ ] Log the install date in My Machine\n- [ ] Wear findings → vendor report\n- [ ] Punch list to maintenance`, 'Superintendent', 0.5),
      ]],
    ];
  }

  const EXAMPLES = [
    { id:'ex-bp-wire-change', name:'BP Wire Change',
      meta:{ area:'Base ply wire', hours:8, crew:6, desc:'Change the base ply forming wire on the base former: cantilever, cut out, clean & inspect, pull in, tension and run in.' },
      phases:wireSteps('BP') },
    { id:'ex-tp-wire-change', name:'TP Wire Change',
      meta:{ area:'Top ply wire', hours:8, crew:6, desc:'Change the top ply forming wire on the top former, including a check of the ply combining point before close-up.' },
      phases:wireSteps('TP') },
    { id:'ex-dryer-felt-change', name:'Dryer Felt Change',
      meta:{ area:'Dryer section', hours:6, crew:5, desc:'One dryer felt position — 1st section (unorun), or 2nd / 3rd section top or bottom. New felt is pulled in behind the old one and pin-seamed.' },
      phases:[
        ['Before the outage', PH.prep, [
          S(`Confirm the new felt\n- [ ] Which position: section & top / bottom\n- [ ] Length, width & seam type\n- [ ] Pintle wire & seam tools on site`, 'Superintendent', 1,
            [sub(`Felt path on PM1\n- Top felts wrap the bottom of the top cans\n- Bottom felts wrap the top of the bottom cans`, SPEC)]),
          S(`Stage tools & equipment\n- [ ] Felt cart / lifting sling\n- [ ] Pull-in rope & clamps\n- [ ] Radios for both sides\n- [ ] Heat-resistant gloves`, 'Dryer tender', 1),
          S(`Pre-job brief\n- [ ] Roles: tender side / drive side / drive control\n- [ ] Review JSA & lockout list\n- [ ] Agree crawl signals`, 'Shift lead', 0.5,
            [sub(`Hazards\n- Hot cans, steam & condensate\n- In-running nips at felt rolls\n- Working in the hood`, HAZ)]),
        ]],
        ['Shutdown & lockout', PH.lock, [
          S(`Cool down the section\n- [ ] Steam off, condensate drained\n- [ ] Hood doors open, ventilation on\n- [ ] Cans cool enough to work near`, 'Dryer tender', 1.5),
          S(`Lock out\n- [ ] Steam & condensate valves\n- [ ] Felt stretch & guide air\n- [ ] Drive: crawl only under the controlled procedure`, 'Shift lead', 0.5),
        ]],
        ['Change the felt', PH.out, [
          S(`Join new felt to old\n- [ ] Lay new felt at the lead-in point\n- [ ] Run direction arrow correct\n- [ ] Clamp / rope lead end to old felt`, 'Dryer crew', 0.5),
          S(`Pull in at crawl\n- [ ] Spotters on both sides with radios\n- [ ] Stop with the seam at the join position\n- [ ] Detach and roll out the old felt`, 'Dryer crew', 1,
            [sub(`Hazards\n- Never reach into a moving felt run\n- Stop the crawl on any signal`, HAZ)]),
        ]],
        ['Clean & inspect', PH.insp, [
          S(`Felt rolls & guide\n- [ ] Felt rolls turn freely, bearings OK\n- [ ] Guide palm & stretch travel\n- [ ] Felt roll doctors`, 'Maint mechanic', 1),
          S(`Cans & pockets\n- [ ] Can doctor blades\n- [ ] Pocket ventilation boxes\n- [ ] Tail ropes & sheaves`, 'Dryer tender', 1),
        ]],
        ['Close & tension', PH.in, [
          S(`Close the seam\n- [ ] Loops lined up edge to edge\n- [ ] Insert pintle full width\n- [ ] Trim & secure pintle ends`, 'Dryer crew', 0.5),
          S(`Tension & guide\n- [ ] Tension to spec\n- [ ] Guide centered, edges clear the frames`, 'Dryer tender', 0.5,
            [sub(`Record\n- Tension:\n- Seam closed by:`, SPEC)]),
        ]],
        ['Startup', PH.start, [
          S(`Remove locks & walk down\n- [ ] Hood clear, tools out\n- [ ] Locks off per procedure`, 'Shift lead', 0.5),
          S(`Steam up & run in\n- [ ] Warm up on the steam curve\n- [ ] Watch the seam pass at crawl\n- [ ] Check tracking at speed`, 'Dryer tender', 1),
          S(`Close out\n- [ ] Log the install date in My Machine\n- [ ] Old felt condition → vendor report`, 'Superintendent', 0.5),
        ]],
      ] },
    { id:'ex-press-felt-change', name:'Press Felt Change',
      meta:{ area:'Press section', hours:6, crew:5, desc:'One felt on the 2-nip press — 1st top felt, 2nd top felt or tandem felt. Includes Uhle box and shower checks.' },
      phases:[
        ['Before the outage', PH.prep, [
          S(`Confirm the new felt\n- [ ] Position: 1st top / 2nd top / tandem\n- [ ] Length, width & design\n- [ ] Endless or seamed — install method`, 'Superintendent', 1,
            [sub(`Felt spec card\n- Supplier · design · size\n- Target tension\n- Last install date (My Machine)`, SPEC)]),
          S(`Stage tools & equipment\n- [ ] Felt cart / sling\n- [ ] Cantilever equipment checked\n- [ ] Shower nozzles & Uhle cover spares`, 'Back tender', 1),
          S(`Pre-job brief\n- [ ] Walk the job with the crew\n- [ ] Review JSA & lockout list`, 'Shift lead', 0.5,
            [sub(`Hazards\n- Press nips & stored hydraulic energy\n- Heavy rolls & overhead lifts\n- Hot shower water`, HAZ)]),
        ]],
        ['Shutdown & lockout', PH.lock, [
          S(`Wash up & unload the press\n- [ ] Sheet off\n- [ ] Open the nips (unload)\n- [ ] Showers & Uhle vacuum off`, 'Machine tender', 0.5),
          S(`Lock out the press\n- [ ] Press drives\n- [ ] Loading hydraulics bled down\n- [ ] Vacuum, showers, stretch & guide air\n- [ ] Try-out verified`, 'Shift lead', 0.5),
        ]],
        ['Remove old felt', PH.out, [
          S(`Cantilever the press\n- [ ] Cantilever / lift equipment in\n- [ ] Back-side fillers out on the felt run`, 'Maint mechanic', 1),
          S(`Slack & remove the old felt\n- [ ] Stretch to minimum, guide centered\n- [ ] Cut out (endless) or open the seam\n- [ ] Pull out tender side`, 'Back tender', 0.5),
        ]],
        ['Clean & inspect', PH.insp, [
          S(`Uhle boxes\n- [ ] Covers: wear, grooves, edges\n- [ ] Deckles set\n- [ ] Clear plugged slots`, 'Machine tender', 1),
          S(`Rolls & showers\n- [ ] Felt rolls: covers, bearings, doctors\n- [ ] HP oscillating shower: nozzles & traverse\n- [ ] Lube showers clear\n- [ ] Press roll doctor blades`, 'Back tender', 1),
        ]],
        ['Install new felt', PH.in, [
          S(`Install the new felt\n- [ ] Run direction arrow correct\n- [ ] Slide on evenly tender → drive side\n- [ ] Close the seam if seamed`, 'Wet end crew', 1),
          S(`Close up & tension\n- [ ] Fillers back in, cantilever out\n- [ ] Tension to spec\n- [ ] Guide centered`, 'Maint mechanic', 0.5,
            [sub(`Record\n- Tension:\n- Uhle vacuum at start-up:`, SPEC)]),
        ]],
        ['Startup', PH.start, [
          S(`Remove locks & load the press\n- [ ] Walk down, locks off\n- [ ] Showers on before the felt moves\n- [ ] Load nips to setpoint`, 'Shift lead', 0.5),
          S(`Run in & condition\n- [ ] Crawl with HP & lube showers on\n- [ ] Watch Uhle vacuum & felt moisture\n- [ ] Sheet on, check press solids`, 'Machine tender', 1),
          S(`Close out\n- [ ] Log the install date in My Machine\n- [ ] Old felt sample / findings → vendor report`, 'Superintendent', 0.5),
        ]],
      ] },
    { id:'ex-stock-prep-cleaners', name:'Stock Prep Cleaners',
      meta:{ area:'Stock prep', hours:6, crew:3, desc:'Centrifugal cleaner banks, BP and TP systems: isolate, pull and inspect cones, clear rejects, reassemble and set pressure drop.' },
      phases:[
        ['Before the outage', PH.prep, [
          S(`Plan the scope\n- [ ] Which banks: BP / TP, which stages\n- [ ] Pull pressure-drop trends & last findings\n- [ ] Cones, tips & gaskets on hand`, 'Superintendent', 1),
          S(`Stage tools\n- [ ] Cleaner wrenches, hoses, buckets\n- [ ] Flashlight & inspection mirror\n- [ ] Tote for debris`, 'Stock prep operator', 0.5),
          S(`Pre-job brief\n- [ ] Review JSA & lockout list\n- [ ] Assign banks to people`, 'Shift lead', 0.5,
            [sub(`Hazards\n- Hot stock & water\n- Lines under pressure until drained\n- Slippery floors`, HAZ)]),
        ]],
        ['Shutdown & lockout', PH.lock, [
          S(`Isolate & drain\n- [ ] Stop cleaner feed pumps\n- [ ] Close feed, accepts, rejects & dilution valves\n- [ ] Drain headers`, 'Stock prep operator', 1),
          S(`Lock out\n- [ ] Feed & rejects pumps\n- [ ] Dilution / elutriation water\n- [ ] Zero pressure on every gauge`, 'Shift lead', 0.5),
        ]],
        ['Clean & inspect', PH.insp, [
          S(`Pull & inspect cones\n- [ ] Remove cones bank by bank\n- [ ] Apex tips: wear & plugging\n- [ ] Inlet nozzles & vortex finders`, 'Stock prep crew', 2,
            [sub(`Record per bank\n- Plugged:\n- Worn tips replaced:\n- Cones replaced:`, SPEC)]),
          S(`Headers & rejects\n- [ ] Flush inlet & accepts headers\n- [ ] Clear rejects lines & sight glasses\n- [ ] Rejects valves, sand trap & timers`, 'Stock prep crew', 1),
          S(`Gauges & water\n- [ ] Feed / accepts / rejects gauges\n- [ ] Dilution & elutriation water flow`, 'Instrument tech', 0.5),
        ]],
        ['Reassemble', PH.in, [
          S(`Re-install cones\n- [ ] New gaskets / O-rings\n- [ ] Worn tips & cones replaced\n- [ ] Clamps tight, every port filled or capped`, 'Stock prep crew', 1),
        ]],
        ['Startup', PH.start, [
          S(`Leak check & restart\n- [ ] Locks off\n- [ ] Fill slowly, check every cone\n- [ ] Start feed pumps`, 'Stock prep operator', 0.5),
          S(`Set & verify\n- [ ] Feed pressure & pressure drop to target\n- [ ] Rejects flow / consistency\n- [ ] Readings logged for the trend`, 'Stock prep operator', 0.5),
          S(`Close out\n- [ ] Findings → vendor report\n- [ ] Parts used → reorder`, 'Superintendent', 0.5),
        ]],
      ] },
  ];

  // Rough card height on the board, so phases line up without overlapping.
  const estH = s => 92 + s.text.split('\n').reduce((t, l) => t + Math.max(1, Math.ceil(l.length / 32)), 0) * 19 + (s.sub ? 34 + s.sub.length * 32 : 0);
  function buildExample(x){
    const b = { id:x.id, name:x.name, meta:{ ...x.meta, example:true }, created:new Date().toISOString(), notes:{}, links:[], frames:[], pan:{ x:0, y:0 }, zoom:1, z:1 };
    const FW = 288, GAP = 56, TOP = 58, VG = 30;
    let k = 0;
    const colH = x.phases.map(([, , steps]) => steps.reduce((t, s) => t + estH(s) + VG, 0));
    const FH = Math.max(...colH) + TOP;
    const chain = [];
    x.phases.forEach(([title, color, steps], i) => {
      const fx = i * (FW + GAP);
      b.frames.push({ id:`${x.id}-f${i}`, x:fx, y:0, w:FW, h:FH, title, color });
      let y = TOP;
      steps.forEach(s => {
        const id = `${x.id}-s${++k}`;
        const n = { id, x:fx + 26, y, z:++b.z, color:'#ffffff', text:s.text, owner:s.who || null, hrs:s.hrs || null, attachments:[], children:[], parent:null };
        b.notes[id] = n; chain.push(id);
        (s.sub || []).forEach((c, j) => {
          const cid = `${id}-c${j + 1}`;
          b.notes[cid] = { id:cid, x:n.x, y:n.y, z:++b.z, color:c.color || '#ffffff', text:c.text, attachments:[], children:[], parent:id };
          n.children.push(cid);
        });
        y += estH(s) + VG;
      });
    });
    for (let i = 1; i < chain.length; i++) b.links.push({ id:`${x.id}-a${i}`, from:chain[i - 1], to:chain[i], label:'' });
    return b;
  }

  return { examples: EXAMPLES, buildExample };
})();
