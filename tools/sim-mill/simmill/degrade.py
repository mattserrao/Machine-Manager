"""Developing failures: the gradual faults that make the Bonvoy reports, shift notes and RCFAs worth reading.

The engine gives Sim Mill its sudden events (breaks, upsets, trips). Real equipment mostly goes another way: a felt
fills, a pump wears, a syphon loosens, a transmitter drifts. Each of those leaves a signature on its Pi tags for days
or weeks before anyone acts, and then one of three things happens:

  outage   found (Bonvoy, rounds or the operators) and fixed at the next outage: the signature stops there
  stop     found, but it can't wait for the outage: a short planned stop to fix it
  missed   nobody acts: it ends in an unplanned stop (and usually an RCFA)

Instrument drifts are the fourth kind: the tag moves but the process doesn't (or the control loop follows the bad
reading). They end with a calibration, never a stop, and teach the reader that not every flag is a failure.

Everything here has its own random stream, so adding or tuning a mode never changes the engine's year, the planted
faults F1–F5 (whose tags are left alone) or any other draw.
"""
import random
from .base import DAY, HOUR, T0, T_END, OUTAGES, BY_NAME

# Tags the planted faults own: nothing developing touches them, so F1–F5 and their answer key stay exact.
PLANTED_TAGS = {'UHLE_P2T_VAC', 'REEL_DRUM_DS_VIB', 'REEL_DRUM_DS_TEMP', 'REF_B_SE', 'REF_B_KW', 'DRY3_DP'}

# A mode: what fails, the tags it shows on (amplitude at the end of its P-F interval, in the tag's units), how it
# develops, how often, and what each outcome costs.
#   shape   pf (slow then fast: x²), drift (linear), intermittent (bursts that grow more frequent), step (an offset)
#   rate    expected faults a year across the mode's assets
#   caught  chance someone acts before it fails
#   fail    (cause, hours lo, hi) of the unplanned stop when missed; None for instrument drifts
#   fix     (cause, hours lo, hi) of the planned stop when it can't wait for the outage
MODES = [
    dict(id='felt_fill', sign='Uhle vacuum creeping up', label='press felt filling', shape='pf', rate=6.5, caught=.5, pf=(12, 28),
         assets=[('1st press top felt', {'UHLE_P1T_VAC': 2.8, 'PRESS_SOLIDS': -0.9}), ('1st press bottom felt', {'UHLE_P1B_VAC': 2.6, 'PRESS_SOLIDS': -0.8}),
                 ('2nd press bottom felt', {'UHLE_P2B_VAC': 2.7, 'PRESS_SOLIDS': -1.0})],
         fail=('feltfill', 3, 6), fix=('feltplan', 2.5, 4), craft='MILL', owner='P16',
         finding='Uhle vacuum climbing and press solids falling: the felt is filling',
         acts=['Raise HP shower pressure and check the nozzles', 'Chemical felt wash planned'], text='Felt plugged'),
    dict(id='shower_plug', sign='felt looks wet coming out of the nip', label='press HP shower plugging', shape='drift', rate=4.0, caught=.7, pf=(14, 30),
         assets=[('1st press top felt HP shower', {'UHLE_P1T_VAC': 1.2, 'PRESS_SOLIDS': -0.6}), ('2nd press bottom felt HP shower', {'UHLE_P2B_VAC': 1.3, 'PRESS_SOLIDS': -0.7})],
         fail=('showerplug', 1.5, 3), fix=('showerclean', 1.2, 2), craft='OPS', owner='P16',
         finding='HP shower nozzles plugging: felt conditioning falling off',
         acts=['Pull and clean the nozzles on the next break', 'Strainer cleaned; watching Uhle vacuum'], text='Shower nozzles plugged'),
    dict(id='vacpump', sign='couch vacuum down a bit', label='vacuum pump wear', shape='drift', rate=2.5, caught=.5, pf=(20, 45),
         assets=[('Vacuum pump', {'COUCH_VAC': -2.4, 'COUCH_SOLIDS': -0.7, 'FLATBOX_VAC': -0.6})],
         fail=('vacpump', 3, 6), fix=('vacpumpplan', 2.5, 4), craft='MECH', owner='P05',
         finding='Couch vacuum falling off with the pump at full speed: vane or seal wear',
         acts=['Check seal water and the pump clearances', 'Pump rebuild scheduled'], text='Vacuum pump wore out'),
    dict(id='syphon', sign='section differential lower than normal', label='syphon or rotary joint wear', shape='pf', rate=5.5, caught=.45, pf=(10, 24),
         assets=[('1st section rotary joint (DS)', {'DRY1_DP': -0.9}), ('2nd section rotary joint (DS)', {'DRY2_DP': -1.1, 'REEL_MOIST': 0.35}),
                 ('4th section rotary joint (DS)', {'DRY4_DP': -1.2, 'REEL_MOIST': 0.45})],
         fail=('syphonfail', 2, 5), fix=('jointplan', 1.5, 3), craft='MECH', owner='P17',
         finding='Syphon differential falling: a can is flooding (syphon or joint)',
         acts=['Steam and condensate to survey the section', 'Joint seal kit and syphon check planned'], text='Syphon came loose'),
    dict(id='hoodfan', sign='hood feels hotter and more humid than usual', label='hood exhaust fan', shape='pf', rate=2.0, caught=.5, pf=(15, 35),
         assets=[('Hood exhaust fan', {'HOOD_EXH_TEMP': 9.0, 'REEL_MOIST': 0.5})],
         fail=('hoodfan', 3, 6), fix=('hoodfanplan', 2, 3.5), craft='MECH', owner='P05',
         finding='Hood exhaust temperature up and moisture drifting: exhaust fan losing flow',
         acts=['Check fan belts and the damper', 'Fan repair planned'], text='Hood exhaust fan failed'),
    dict(id='fanpump', sign='headbox pressure bouncing now and then', label='fan pump cavitation', shape='intermittent', rate=2.0, caught=.5, pf=(14, 30),
         assets=[('Fan pump', {'FAN_PUMP_FLOW': -900, 'HB_P': -0.45, 'FAN_PUMP_VIB': 0.05})],
         fail=('fanpump', 3, 7), fix=('fanpumpplan', 3, 4.5), craft='MECH', owner='P05',
         finding='Fan pump flow and headbox pressure dipping in bursts: cavitation or impeller wear',
         acts=['Check silo level and the pump suction', 'Impeller change planned'], text='Fan pump impeller failed'),
    dict(id='bearing', sign='bearing sounds rough on rounds', label='bearing', shape='pf', rate=8.5, caught=.5, pf=(18, 45),
         assets=[('Pulper rotor', {'PULPER_VIB': 0.34}), ('REF 1 refiner motor', {'REF_A_VIB': 0.34}), ('REF 2 refiner motor', {'REF_B_VIB': 0.34}),
                 ('Fan pump', {'FAN_PUMP_VIB': 0.34}), ('Couch roll', {'COUCH_DS_VIB': 0.34}), ('1st press drive', {'PRESS1_DS_VIB': 0.34}),
                 ('2nd press drive', {'PRESS2_DS_VIB': 0.34}), ('Dryer drive lineup', {'DRYER_DRIVE_VIB': 0.34}), ('Winder drums', {'WINDER_DRUM_VIB': 0.34})],
         fail=('bearingfail', 4, 8), fix=('bearingplan', 2.5, 4), craft='MECH', owner='P03',
         finding='Bearing vibration rising (Bonvoy)', acts=['Grease and take daily readings', 'Bearing change planned'], text='Bearing failed'),
    dict(id='cons_drift', sign='basis weight running light on the scanner', label='consistency transmitter drift', shape='drift', rate=2.5, caught=.9, pf=(12, 30), instrument=True,
         assets=[('Headbox', {'HB_CONS': 0.045, 'REEL_BW': -1.1})],
         fail=None, fix=None, craft='INST', owner='P14',
         finding='Headbox consistency reading drifting with basis weight off target: transmitter drift suspected',
         acts=['Grab samples against the transmitter', 'Transmitter recalibrated; BW back on target'], text='Transmitter drift'),
    dict(id='moist_drift', sign='scanner moisture reading high', label='moisture scanner drift', shape='step', rate=1.5, caught=.9, pf=(5, 14), instrument=True,
         assets=[('Reel drum', {'REEL_MOIST': 0.7})],
         fail=None, fix=None, craft='INST', owner='P14',
         finding='Reel moisture reading high but the sheet tests dry at the lab: scanner standardization',
         acts=['Lab moisture against the scanner each roll', 'Scanner standardized'], text='Scanner drift'),
]

CAUSES = {
    'feltfill': 'Press felt plugged (emergency felt wash)', 'feltplan': 'Press felt chemical wash (planned)',
    'showerplug': 'Press shower nozzles plugged', 'showerclean': 'Press shower nozzle clean (planned)',
    'vacpump': 'Vacuum pump failure', 'vacpumpplan': 'Vacuum pump repair (planned)',
    'syphonfail': 'Syphon failure (can flooded)', 'jointplan': 'Rotary joint / syphon repair (planned)',
    'hoodfan': 'Hood exhaust fan failure', 'hoodfanplan': 'Hood exhaust fan repair (planned)',
    'fanpump': 'Fan pump impeller failure', 'fanpumpplan': 'Fan pump impeller change (planned)',
}

RCFA_TEMPL = {
    'feltfill': ('Clothing', 'Press felt plugged mid-life; conditioning could not keep it open, so the sheet would not hold',
                 'Uhle vacuum trend not acted on; shower nozzle checks overdue', ['Add Uhle vacuum rate-of-rise to the shift checks for {a}', 'Review felt design with the felt vendor']),
    'showerplug': ('Process', 'HP shower nozzles plugged: strainer on the shower supply blinded',
                   'Strainer not on the outage clean list', ['Add the shower strainer to every outage clean list', 'Weekly nozzle check for {a}']),
    'vacpump': ('Equipment failure', 'Vacuum pump vanes worn through; seal water starved', 'Seal water strainer plugged; no vibration on the pump',
                ['Seal water flow switch on {a}', 'Add {a} to the vibration route']),
    'syphonfail': ('Equipment failure', 'Syphon came loose in the can and flooded it', 'Syphon differential fell for days before the stop',
                   ['Check syphon clearances on {a} cans at the next outage', 'Alarm on syphon differential below 60% of normal']),
    'hoodfan': ('Equipment failure', 'Hood exhaust fan bearing and belt failure', 'Exhaust temperature rose for weeks; belts not on the PM',
                ['Add hood exhaust fan belts to the monthly PM', 'Vibration point on {a}']),
    'fanpump': ('Equipment failure', 'Fan pump impeller eroded by cavitation', 'Silo level run low on heavy grades',
                ['Raise the silo low-level alarm', 'Impeller inspection at every second outage']),
}


def _outcome_times(rnd, mode, onset, pf, busy, planted_clash):
    """When it's found (or None), how it ends, and the stop it costs. Returns a dict or None if it can't be placed."""
    fail_t = onset + DAY * pf
    caught = rnd.random() < mode['caught']
    found = onset + DAY * (pf * rnd.uniform(.4, .7)) if caught else None
    out = dict(found=found, fail=None, fixed=None, fix_outage=None, outcome='', stop=None)
    if mode.get('instrument'):
        # an instrument drift: noticed (or not) and recalibrated a few days later; nothing stops
        if not found: found = onset + DAY * pf * rnd.uniform(.75, .95)
        out.update(found=found, fixed=found + DAY * rnd.randint(1, 3), outcome='calibrated')
        return out
    if found:
        o = next((o for o in OUTAGES if o['start'] > found), None)
        if o and o['start'] < fail_t - DAY * 2:
            out.update(fixed=o['start'] + HOUR * 4, fix_outage=o['id'], outcome='outage')
            return out
        a = (found + DAY * rnd.randint(1, 3)).replace(hour=rnd.choice([8, 9, 10, 13]), minute=0, second=0, microsecond=0)
        h = rnd.uniform(*mode['fix'][1:])
        for _ in range(12):
            if not busy(a, a + HOUR * h) and not planted_clash(a, a + HOUR * h): break
            a += HOUR * 7
        else:
            return None
        if a >= fail_t: found = None   # couldn't get to it in time: it fails after all
        else:
            out.update(found=found, fixed=a + HOUR * h, outcome='stop',
                       stop=dict(start=a, end=(a + HOUR * h).replace(second=0, microsecond=0), kind='planned', cause=mode['fix'][0]))
            return out
    # missed: it fails
    h = rnd.uniform(*mode['fail'][1:])
    a = fail_t.replace(second=0, microsecond=0)
    for _ in range(12):
        if not busy(a, a + HOUR * h) and not planted_clash(a, a + HOUR * h): break
        a += HOUR * 5
    else:
        return None
    out.update(found=None, fail=a, fixed=a + HOUR * h, outcome='missed',
               stop=dict(start=a, end=(a + HOUR * h).replace(second=0, microsecond=0), kind='unplanned', cause=mode['fail'][0]))
    return out


def build(seed, ev, in_outage):
    """Draw the year's developing faults; add the stops they cost to `ev`. Returns the faults (for the process model,
    records, shift notes and reports). Sheet breaks and slowdowns inside a new stop are dropped (the machine was down)."""
    rnd = random.Random(f'degrade:{seed}')
    stops = lambda: [e for e in ev if e['kind'] in ('planned', 'unplanned')]
    busy = lambda a, b: in_outage(a) or in_outage(b) or any(e['start'] < b + HOUR * 3 and a < e['end'] + HOUR * 3 for e in stops())
    planted = [e for e in ev if e.get('story')]
    planted_clash = lambda a, b: any(e['start'] < b + DAY and a < e['end'] + DAY for e in planted)
    faults = []
    lo, hi = T0 + DAY * 20, T_END
    for mode in MODES:
        assert all(a in BY_NAME for a, _ in mode['assets']), mode['id']
        assert not any(t in PLANTED_TAGS for _, tags in mode['assets'] for t in tags), mode['id']
        t = lo + DAY * rnd.uniform(0, 365 / mode['rate'])
        while True:
            t = t + DAY * rnd.gammavariate(4, 365 / mode['rate'] / 4)     # steadier than Poisson: a year looks like a year
            if t >= hi: break
            asset, tags = rnd.choice(mode['assets'])
            pf = rnd.uniform(*mode['pf'])
            onset = t.replace(minute=0, second=0, microsecond=0)
            # one developing fault per asset at a time
            if any(f['asset'] == asset and f['onset'] < onset + DAY * pf and onset < (f['fixed'] or f['onset'] + DAY * f['pf_days']) for f in faults): continue
            oc = _outcome_times(rnd, mode, onset, pf, busy, planted_clash)
            if not oc: continue
            f = dict(mode=mode['id'], label=mode['label'], asset=asset, tags=dict(tags), shape=mode['shape'], onset=onset, pf_days=pf,
                     craft=mode['craft'], owner=mode['owner'], instrument=bool(mode.get('instrument')), story='', **oc)
            f['end'] = f['fixed'] or (onset + DAY * pf)
            f['bursts'] = _bursts(rnd, f) if mode['shape'] == 'intermittent' else []
            if f['stop']:
                s = f['stop']
                s.update(asset=asset, story='', degrade=mode['id'],
                         note=(f"{CAUSES.get(s['cause'], s['cause'])}: {mode['finding'].split(':')[0].lower()} for "
                               f"{(s['start'] - onset).days} days before." if s['kind'] == 'unplanned' else
                               f"{CAUSES.get(s['cause'], s['cause'])}: found {f['found']:%b %d} ({mode['finding'].split(':')[0].lower()})."))
                if s['kind'] == 'unplanned': s['speed'] = 0.0
                # the machine was down: drop any break or slowdown that started inside the stop
                ev[:] = [e for e in ev if not (e['kind'] in ('break', 'slowdown') and s['start'] <= e['start'] < s['end'])]
                ev.append(s); f['event'] = s
            faults.append(f)
    return faults


def _bursts(rnd, f):
    """Intermittent faults: bursts of 2–6 h that get more frequent and stronger towards the end."""
    out, d = [], 0.0
    while d < (f['end'] - f['onset']).total_seconds() / 86400:
        x = d / f['pf_days']
        if rnd.random() < .12 + .55 * x:
            a = f['onset'] + DAY * d + HOUR * rnd.randint(0, 20)
            out.append((a, a + HOUR * rnd.randint(2, 6), min(1.0, .45 + .6 * x + rnd.uniform(-.1, .1))))
        d += 1
    return out


def signature(f, tt):
    """The fault's fraction of full amplitude at each hour (0 before onset and after it's fixed)."""
    import numpy as np
    out = np.zeros(len(tt))
    for i, t in enumerate(tt):
        if t < f['onset'] or t >= f['end']: continue
        x = min(1.0, (t - f['onset']).total_seconds() / 86400 / f['pf_days'])
        if f['shape'] == 'pf': out[i] = x ** 2
        elif f['shape'] == 'drift': out[i] = x
        elif f['shape'] == 'step': out[i] = 1.0
        elif f['shape'] == 'intermittent':
            out[i] = max((s for a, b, s in f['bursts'] if a <= t < b), default=.08 * x)
    return out


def apply(R, faults, tt):
    """Add every fault's signature to the process values (before the engine merge and the noise)."""
    for f in faults:
        s = signature(f, tt)
        for k, amp in f['tags'].items():
            R[k] = R[k] + s * amp
