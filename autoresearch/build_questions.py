"""Build autoresearch/questions.json: three sections, 18 questions each, 12 train + 6 held-out.

Sections
  pm  papermaking knowledge          asked of the Demodemo RAG org (the reference library)
  ce  industrial / chemical eng.     asked of the Demodemo RAG org
  sm  Sim Mill data                  asked of the Sim Mill org; train questions reuse the demo answer key by id

Kinds
  library  the key comes from a library document (doc id + page in `sources`)
  gap      the library doesn't cover it today; the key is standard engineering knowledge.
           These are where adding the right PDF should raise the score.
  calc     a worked number; the judge checks the value within `tolerance`
  data     Sim Mill data (tool results); premise = the question's premise is false

Held-out questions are never shown to the improver (Claude building tools / RAG / memory). Run them only on
baseline, every third round and the final round.
    python3 autoresearch/build_questions.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAG, SIM = 'Demodemo RAG', 'Sim Mill'

def q(id, section, split, kind, question, must, sources=(), tolerance=None, org=None, ref=None, nice=()):
    d = {'id': id, 'section': section, 'split': split, 'kind': kind, 'org': org or (SIM if section == 'sm' else RAG),
         'question': question, 'must': list(must), 'nice': list(nice), 'sources': list(sources)}
    if tolerance: d['tolerance'] = tolerance
    if ref: d['ref'] = ref
    return d

VOITH, AJ_GUIDE, BLADE, CDM = '09275f87-d36f-41a5-af70-b22e0d0c57c7', '59151609-8cbd-461a-874e-aaeb006dfc27', '5d797427-af61-43ca-9fb8-4f8bcd8261ee', 'dcf8af26-db8b-4545-b1a6-80cb9239b6c5'
TRIM, SAMPLE, VAC, SHOWER = 'dcdb0d87-3ad5-4f05-8bb0-5454dea7c99c', 'bb3f776f-3519-4875-88bc-e6524716d692', '56ec08f5-d829-4786-b810-b1a7de9c7f74', 'a1b709c1-b90f-4687-ad80-b9fb21515901'
TENSO, SMOOK8, SMOOK12, REFMAN = 'd08922bf-54ab-4869-b4c6-b7c0d251f22a', '01a335fe-bfba-4f11-b32c-df2de03d8521', '30d870b7-8b32-475a-9f65-e8f3bd87bd7b', '573e2f9c-afca-42a5-b4a6-10980694ab2e'
FORMULAS, HEAD, STEAM, LRVP = '2324ca0e-e2cb-4ac4-8f6c-1c90e2a03701', 'a58b3808-c123-425c-8a4d-636b917678f9', 'f2d6b892-8f3a-49f6-bfb1-8f6beada12e7', 'a92ccac2-eca7-4b0a-a2cc-bd07d3da9fa5'

QS = [
  # ---------------- papermaking knowledge ----------------
  q('pm01', 'pm', 'train', 'library', 'What start-up sequence is recommended for a new press felt?',
    ['square the felt, tradeline parallel to CD; stretch roll snug', 'jog to inspect and centre (at dead-weight load if it can\'t jog with the nip open)',
     'raise tension to the running range', 'lube shower on and crawl at dead-weight load until uniformly wet',
     'then normal load and full Uhle box vacuum; run 15-20 min before tailing', 'start-up HP shower no more than 200 psi (150 ideal)'],
    [f'{VOITH} p2-3']),
  q('pm02', 'pm', 'train', 'library', 'What lube and high-pressure shower settings are recommended for press felts?',
    ['lube: 15-25 psi, continuous, 0.04-0.08 gpm per inch, 3-6 in spacing, 90-120 degree fan, single coverage',
     'HP: 175-250 psi, continuous, 0.05-0.10 gpm per inch, oscillating',
     'oscillation rate (in/min) = felt speed (fpm) x nozzle size (in) / felt length (ft)'], [f'{VOITH} p4']),
  q('pm03', 'pm', 'train', 'library', 'Our forming fabric keeps walking toward one side. What should we check?',
    ['guide roll location (between stationary rolls, not beside the stretch roll) and alignment: the fabric guides toward the side it touches first',
     'low or uneven tension; low friction (polyamide CD yarns ~30% less friction; water at the guide roll)',
     'wrap angle: at least 25 degrees on a fourdrinier', 'guide palm sensitivity',
     'flatbox misalignment; drilled suction box covers matching the fabric twill (slotted covers fix it)'], [f'{AJ_GUIDE} p2-4']),
  q('pm04', 'pm', 'train', 'library', 'A doctor blade is wearing much faster at one end. What causes that and how do we fix it?',
    ['the doctor is misaligned, not parallel to the roll axis', 'shim or move the bearings and brackets to align it parallel to the axis'], [f'{BLADE} p1']),
  q('pm05', 'pm', 'train', 'library', 'We have a CD moisture streak at the reel. Give me a troubleshooting checklist.',
    ['locate with a FLIR / thermal image', 'scanner (dirty, mapping, edge sensing)', 'steambox and rewet shower (mapping, actuators, air lines, plugged nozzles)',
     'dryer can build-up (doctoring; brass or abrasive blades need a safety review: fire risk)', 'dryer felt and wet felt permeability; sleeve or roll cover failure; wire permeability',
     'headbox: plugged header holes, warped slice lip (check with a Teflon, not metal, feeler gauge), apron'], [f'{CDM} p1-2']),
  q('pm06', 'pm', 'train', 'library', 'How should edge trim squirt nozzles be set up in the forming section?',
    ['ruby nozzles with laminar jets; check the cut with a stroboscope', 'for 0.4-0.5 mm jets filter to 200 um or finer, pre-filter about 50 um',
     'water about 50-60 C (warmer than the air)', 'tilt 15-40 degrees from vertical in MD to cut bounce-back and fibre mist',
     'single jets are enough up to about 500 m/min; nozzle distance is secondary to jet quality'], [f'{TRIM} p3-5']),
  q('pm07', 'pm', 'train', 'library', 'How do we take a press exit solids sample?',
    ['at the next wet end break, crew briefed, own SOP/JHA', 'machine at normal conditions (load, showers, vacuum, steambox)',
     'narrow tail 3-4 in if possible; poly wand; never break the plane of the press, keep clear of ingoing nips',
     'tennis-ball sized sample sealed at once in a labelled 1-gallon zip bag; record the operating parameters'], [f'{SAMPLE} p2']),
  q('pm08', 'pm', 'train', 'library', 'How much Uhle box slot area does a press felt need, and how should the vacuum be sized?',
    ['slot area depends only on machine speed: about 1 in total slot width at 2,500 fpm; no more than about 2 ms dwell',
     'airflow = slot area x vacuum factor of 15-20 cfm per square inch', 'two boxes per felt only where cleaning needs it, not for extra dewatering'], [f'{VAC} p5-6']),
  q('pm09', 'pm', 'train', 'library', 'How can I tell if a low-vacuum forming table element is pulling too hard?',
    ['pulsing vacuum piping, whitewater pouring from its separator', 'one element can take 10-30% of headbox flow (confirm with a drainage study)',
     'valves left wide open put full header vacuum on early elements: aggressive dewatering, poor formation, sheet sealing',
     'maximum vacuum is set by elevation: water no higher than 2 in below the outlet (a tape measure)'], [f'{VAC} p3']),
  q('pm10', 'pm', 'train', 'gap', 'What is press crushing, and how do we stop it?',
    ['crushing: water can\'t escape the nip fast enough, hydraulic pressure disrupts the wet web (mottled, crushed sheet)',
     'causes: too much water/too low solids into the nip, too high first-nip load, filled or wet felt, low Uhle vacuum',
     'fixes: reduce first-nip load, better felt conditioning/dewatering, more nip void volume (grooved / blind-drilled covers), raise couch solids']),
  q('pm11', 'pm', 'train', 'library', 'What does the breast roll shower do, and what water should it use?',
    ['outside the forming fabric, aimed at the centre of the breast roll', 'fills the fabric void volume to slow drainage just after the slice',
     'white water, to avoid thermal and pH shock'], [f'{SHOWER} p4']),
  q('pm12', 'pm', 'train', 'library', 'How do we measure forming fabric tension with a Tensometer safely and correctly?',
    ['reads tension in PLI', 'keep away from ingoing nips (about 2 ft minimum from a roll), never on top of a roll', 'long side of the frame in MD; do not touch the frame',
     'measure near a support on slack webs; apply gently'], [f'{TENSO} p4-7']),
  q('pm13', 'pm', 'heldout', 'library', 'How can you tell by eye that a shower nozzle is worn out?',
    ['a good nozzle has a laminar zone before the jet breaks up', 'if the stream disperses immediately, replace the nozzle',
     'some nozzles (e.g. self-purging) never have a laminar zone'], [f'{SHOWER} p3']),
  q('pm14', 'pm', 'heldout', 'library', 'Why do most mills use disc refiners rather than conical refiners?',
    ['lower no-load energy', 'higher consistency, loading and speed', 'more versatile plate design', 'wear is self-correcting', 'smaller footprint'], [f'{SMOOK8} p1']),
  q('pm15', 'pm', 'heldout', 'library', 'In two-ply kraft linerboard, how is the furnish usually split between the base and the top liner?',
    ['base: high-yield kraft (about 55-60% yield), hot-stock refined', 'top: lower-yield, well-refined unbleached kraft (sometimes bleached) for appearance and printability',
     'internal starch for stiffness; top liner lightly sized at the calender'], [f'{SMOOK12} p1']),
  q('pm16', 'pm', 'heldout', 'calc', 'What is specific edge load? Work it out for a refiner at 363 kW net, 30 km/rev bar edge length and 600 rpm.',
    ['SEL = net power / (bar edge length x rev/s): refining intensity, in Ws/m', 'separate from specific energy (amount of refining, net kWh/t or hpd/t)',
     'answer about 1.2 Ws/m'], [f'{REFMAN} p23-24, p41'], tolerance='1.2 +/- 0.05 Ws/m'),
  q('pm17', 'pm', 'heldout', 'library', 'What drives refiner no-load power, and why does it matter?',
    ['no-load = pumping and viscous shear; it does no refining', 'scales with speed cubed and plate diameter to about the 4.3 power; groove depth and hydraulic section ratio matter',
     'not the rotor mass', 'reduced-diameter plates can save 30-150 hp (e.g. 46 to 40 in about 150 hp)'], [f'{REFMAN} p29, p32-33']),
  q('pm18', 'pm', 'heldout', 'gap', 'What is the difference between ring crush (RCT) and short-span compression (SCT/STFI), and which better predicts box performance?',
    ['SCT: very short span (about 0.7 mm) so the strip can\'t buckle, measures intrinsic compressive strength',
     'RCT: strip formed into a ring in a holder; affected by buckling and caliper, more operator-sensitive',
     'SCT (with caliper) correlates better with ECT and box compression (McKee)']),
  # ---------------- industrial / chemical engineering ----------------
  q('ce01', 'ce', 'train', 'library', 'What are the pump affinity laws, and how do you work out hydraulic pump power?',
    ['flow ~ speed; head ~ speed squared; power ~ speed cubed', 'hydraulic hp = differential psi x gpm / 1714 (kW = kPa x L/min / 60,000)'], [f'{FORMULAS} p3']),
  q('ce02', 'ce', 'train', 'library', 'What pipe velocity is acceptable from the pressure screen to the headbox?',
    ['7-14 ft/s (2.1-4.3 m/s)'], [f'{FORMULAS} p3']),
  q('ce03', 'ce', 'train', 'library', 'How is headbox jet velocity related to the head behind the slice?',
    ['Bernoulli: Vj = sqrt(2gH), or K x sqrt(H) with a unit constant', 'H is total head: pressure plus velocity head plus elevation, not just the transmitter reading'],
    [f'{HEAD} p2', f'{FORMULAS} p5']),
  q('ce04', 'ce', 'train', 'calc', 'Roughly what jet speed does a headbox at 12 psig give?',
    ['V = 732.3 x sqrt(psig) ft/min', 'about 2,540 ft/min (neglecting velocity and elevation head)'], [f'{FORMULAS} p5'], tolerance='2,537 +/- 40 ft/min'),
  q('ce05', 'ce', 'train', 'library', 'Why do dryer cans with stationary syphons need a differential pressure, and how much?',
    ['steam side must be higher than the condensate side to push condensate out', 'about 0.1-0.2 bar for stationary syphons',
     'too little and the can floods; cascade reuses the blow-through and flash steam'], [f'{STEAM} p2-3']),
  q('ce06', 'ce', 'train', 'library', 'What happens in the dryer steam system on a sheet break, and what should the controls do?',
    ['condensation and steam use drop at once (no sheet cooling the cans)', 'hard to hold the group differential',
     'drop pressures to a break set point, automatically if possible'], [f'{STEAM} p3']),
  q('ce07', 'ce', 'train', 'library', 'How does condensate behave inside a dryer can as speed rises?',
    ['above about 350 m/min it moves with the shell', 'above about 500 m/min it rims: a 6-10 mm ring on the shell, which insulates',
     'below rimming speed scoops are used and cannot flood'], [f'{STEAM} p3, p5']),
  q('ce08', 'ce', 'train', 'library', 'Why do most paper machines feed superheated steam to the first dryers?',
    ['steam arrives superheated (about 10 C above saturation, ~165 C) at the main distributor', 'pressure reductions alone barely lower the temperature',
     'reaching low can temperatures needs steam cooling (desuperheating); low pressure is not low temperature'], [f'{STEAM} p6-10']),
  q('ce09', 'ce', 'train', 'library', 'How much seal water should a liquid ring vacuum pump get, and how should it be controlled?',
    ['each model has a standard flow; +/-10-20% has little effect', 'too little loses vacuum, too much adds horsepower',
     'orifice or nozzle at a controlled supply pressure with local gauges (a linear regulating valve lets it be retuned as vane-cone clearance grows)',
     'clean once-through water best; recirculated cooling-tower water means frequent rebuilds'], [f'{VAC} p7', f'{LRVP} p2-3']),
  q('ce10', 'ce', 'train', 'calc', 'A refiner takes 900 gpm at 4% consistency and draws 487 hp net. What are the throughput and net specific energy?',
    ['t/d = gpm x 6 x consistency (fraction) = 216 short t/d', 'net specific energy = 487 / 216 = about 2.3 hpd/t'], [f'{REFMAN} p25, p41'], tolerance='216 t/d; 2.25 +/- 0.05 hpd/t'),
  q('ce11', 'ce', 'train', 'gap', 'What is the saturation temperature of steam at 10 barg, and roughly how much latent heat does it give up?',
    ['10 barg = about 11 bar abs, saturation about 184 C', 'latent heat about 2,000 kJ/kg'], tolerance='184 +/- 2 C; 1,950-2,050 kJ/kg'),
  q('ce12', 'ce', 'train', 'gap', 'What is NPSH, and how do I tell if a whitewater pump is cavitating?',
    ['NPSH available must exceed NPSH required with margin', 'signs: gravel-like noise, vibration, unsteady discharge pressure/flow, lost head, pitted impeller eye',
     'causes: low suction level, hot liquid (vapour pressure), blocked suction; distinguish from entrained air']),
  q('ce13', 'ce', 'heldout', 'calc', 'A rectangular weir with end contractions has a 2 ft opening and 0.5 ft of head. What flow is that?',
    ['Q = 3.33 x (L - 0.2H) x H^1.5 ft3/s', 'about 2.24 ft3/s (about 1,000 gpm)'], [f'{FORMULAS} p4'], tolerance='2.24 +/- 0.05 ft3/s'),
  q('ce14', 'ce', 'heldout', 'calc', 'How much vacuum airflow does one Uhle box need on a 300-inch machine at 2,500 fpm?',
    ['about 1 in total slot width at 2,500 fpm, so about 300 in2 of slot', 'x 15-20 cfm/in2 = about 4,500-6,000 cfm'], [f'{VAC} p5'], tolerance='4,500-6,000 cfm'),
  q('ce15', 'ce', 'heldout', 'calc', 'What hydraulic power does a pump need for 1,500 gpm at 60 psi differential?',
    ['hp = psi x gpm / 1714', 'about 52.5 hydraulic hp (motor power higher by pump efficiency)'], [f'{FORMULAS} p3'], tolerance='52.5 +/- 1 hp'),
  q('ce16', 'ce', 'heldout', 'calc', 'If we slow a refiner from 900 to 720 rpm, how much does its no-load power change?',
    ['no-load ~ speed cubed', '(720/900)^3 = 0.51, so about 49% less no-load'], [f'{REFMAN} p33'], tolerance='0.51 +/- 0.01'),
  q('ce17', 'ce', 'heldout', 'gap', 'How do you decide whether pipe flow is laminar or turbulent, and how is pulp stock different?',
    ['Reynolds number = rho V D / mu', 'below about 2,300 laminar, above about 4,000 turbulent', 'pulp suspensions are non-Newtonian: plug flow, then mixed, then turbulent; head loss curve has a hump/dip']),
  q('ce18', 'ce', 'heldout', 'gap', 'How does a thermocompressor work in a dryer steam system?',
    ['high-pressure motive steam through a nozzle entrains low-pressure blow-through / flash steam', 'recompresses it to an intermediate pressure to reuse in the dryers',
     'keeps the differential for condensate removal; alternative to a cascade']),
]

# ---------------- Sim Mill data ----------------
SM_TRAIN = ['F2-Q1', 'F1-Q1', 'H2', 'O1', 'O2', 'F5-Q1', 'H4', 'P1', 'S1', 'S2', 'P2', 'AC-Q1']   # from the demo answer key
key = {k['id']: k for k in json.loads((ROOT / 'demo-data/sim-mill/answers/answer_key.json').read_text())['questions']}
for i, rid in enumerate(SM_TRAIN, 1):
    k = key[rid]
    QS.append(q(f'sm{i:02d}', 'sm', 'train', 'premise' if rid.startswith('P') else 'data', k['question'], [k['expect']], ref=rid))
QS += [
  q('sm13', 'sm', 'heldout', 'data', 'What happened to the bottom forming fabric in February, and is the follow-up done?',
    ['Feb 9: a wad off the headbox approach put a 5-inch hole at the TS; fabric changed with the spare', 'about 9.5 h unplanned down',
     'RCFA-SM-26-006', 'its action, a wad detector camera at the breast roll (due Apr 30), is still open/overdue']),
  q('sm14', 'sm', 'heldout', 'data', 'What has cost us the most downtime since August 1, apart from planned outages?',
    ['press sheet breaks: about 68 h from 56 breaks', 'then dryer breaks about 31 h (46)', 'then bearing failures about 14 h (2 events); reel breaks about 10 h (36)']),
  q('sm15', 'sm', 'heldout', 'data', 'How did OME compare across August, September and October?',
    ['OME about 79.9%, 79.3%, 81.0%', 'tons about 21,160 / 20,310 / 20,680', 'breaks about 37 / 49 / 50']),
  q('sm16', 'sm', 'heldout', 'data', 'How long did the last three 2nd press top felts run against target, and where is the current one?',
    ['May 19 to Jul 8: 50 days', 'Jul 8 to Aug 19: 41 days; Aug 19 to Sep 30: 41 days', 'target 42 days; current felt in Sep 30, 30 days on Oct 31']),
  q('sm17', 'sm', 'heldout', 'data', 'Where did most of our October sheet breaks happen?',
    ['press section: 19 breaks, about 23 h - the large majority of break time', 'reel 12 (about 3 h); dryer sections 4-7 each']),
  q('sm18', 'sm', 'heldout', 'premise', 'Why did this year\'s annual outage run long?',
    ['premise is false: Sim Mill has no annual outage', 'outages are 20 h every 6 weeks', 'offers what the data does show (e.g. outage overruns or the next outage)']),
]

if __name__ == '__main__':
    from collections import Counter
    out = {'about': __doc__.strip().split('\n')[0], 'questions': QS}
    (ROOT / 'autoresearch/questions.json').write_text(json.dumps(out, indent=1) + '\n')
    print(Counter((x['section'], x['split']) for x in QS), len(QS))
