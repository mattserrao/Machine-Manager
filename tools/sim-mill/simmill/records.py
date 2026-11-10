"""Sim Mill records: work orders (JDE), Planner actions, BUS daily-sheet issues and RCFAs, all built from the model's
year (stops, faults, position changes, outages) plus a seeded background of routine work.

Same shapes and status logic the importers (tools/ingest/importers.py) expect.
"""
import random
from .base import B, md, tx
from .base import (PLANTS, D, DT, DAY, HOUR, Y0, TODAY, OUTAGES, NEXT_OUTAGE, OUT_BY_ID, BY_NAME, POS_NAME, LEAD_OF)
from .model import CAUSE_TEXT, ROUTES, due_at_next_outage
from . import degrade
MODE = {x['id']: x for x in degrade.MODES}

STATUS = {10: 'Entered', 20: 'Approved', 30: 'Planned - parts not reserved', 35: 'Deferred - next opportunity',
          40: 'Scheduled', 45: 'Waiting on parts', 70: 'In progress', 90: 'Completed', 99: 'Closed'}
WO_TYPE = {'CM': '1 - Corrective', 'PM': '2 - Preventive', 'EM': '3 - Emergency', 'PJ': '4 - Project / outage'}
CRAFT_LEAD = {'MECH': 'P12', 'E&I': 'P13', 'OPS': None, 'MILL': 'P12', 'INST': 'P14'}


class WO:
    def __init__(self, asset, type, desc, created, priority=3, craft='MECH', est=4, outage='', completed=None, parts=None, notes='',
                 originator='P02', story='', key='', planned=None, approved=None):
        assert asset in BY_NAME, asset
        self.asset = BY_NAME[asset]; self.type = type; self.desc = desc; self.created = D(created); self.priority = priority
        self.craft = craft; self.est = est; self.outage = outage; self.completed = D(completed); self.notes = notes
        self.parts = parts or ('NA' if type == 'PM' and craft == 'OPS' else 'Reserved'); self.originator = originator
        self.story = story; self.key = key; self.planned = D(planned) or (OUT_BY_ID[outage]['date'] if outage else None)
        self.approved = D(approved) or self.created + DAY * (0 if type == 'EM' else (1 if priority <= 2 else 2))
        self.resched = None; self.deferred_on = None; self.wait_parts = None; self.no = None
    def outage_at(self, d):
        if self.resched and d >= self.resched[0]: return self.resched[1]
        return self.outage
    def status_at(self, d):
        if self.completed and self.completed <= d: return 99 if (d - self.completed).days >= 10 else 90
        if d < self.approved: return 10
        if self.wait_parts and self.wait_parts[0] <= d < self.wait_parts[1]: return 45
        if self.deferred_on and d >= self.deferred_on and not (self.resched and d >= self.resched[0]): return 35
        if self.outage_at(d): return 30 if self.parts == 'Not reserved' else 40
        if self.planned and d >= self.planned: return 70
        return 20
    def changes(self):
        c = [self.created, self.approved]
        if self.completed: c += [self.completed, self.completed + DAY * 10]
        if self.resched: c.append(self.resched[0])
        if self.deferred_on: c.append(self.deferred_on)
        if self.wait_parts: c += list(self.wait_parts)
        return c


class Action:
    def __init__(self, title, bucket, owner, created, due, completed=None, started=None, priority='Medium', desc='', creator='P01',
                 asset=None, story='', key=''):
        self.title = title; self.bucket = bucket; self.owner = owner; self.created = D(created); self.due = D(due)
        self.completed = D(completed); self.started = D(started) or (self.created + DAY * 2 if self.completed or self.due - DAY * 10 < TODAY else None)
        self.priority = priority; self.desc = desc; self.creator = creator; self.asset = BY_NAME.get(asset) if asset else None
        self.story = story; self.key = key; self.id = None
    def progress_at(self, d):
        if self.completed and self.completed <= d: return 'Completed'
        if self.started and self.started <= d: return 'In progress'
        return 'Not started'


class Issue:   # one BUS line, carried day to day until it closes
    def __init__(self, start, end, asset, issue, actions, owner, wo=None, story='', status=None):
        self.start = D(start); self.end = D(end); self.asset = BY_NAME[asset]; self.issue = issue; self.actions = actions
        self.owner = owner; self.wo = wo; self.story = story; self.status = status; self.key = ''
    def open_on(self, d): return self.start <= d and (self.end is None or d <= self.end)
    def action_on(self, d):
        n = len(self.actions)
        if n == 1 or (self.end and d >= self.end): return self.actions[-1]   # the last step is what closed it
        span = max(1, ((self.end or TODAY + DAY) - self.start).days)
        return self.actions[min(n - 2 if self.end else n - 1, (d - self.start).days * (n - 1 if self.end else n) // span)]


# Routine issues for the background of the BUS sheet: (asset, issue, [actions], craft, owner)
ROUTINE = [
    ('Pulper', 'Pulper rotor amps swinging with bale feed', ['Operators checking bale breaker feed rate', 'Feed rate steadied; watch'], 'OPS', 'P07'),
    ('HD cleaners', 'HD cleaner reject valve sticking', ['Instrument tech to stroke the valve', 'Valve rebuilt'], 'INST', 'P14'),
    ('Coarse screen', 'Coarse screen rejects high', ['Check screen basket for damage', 'Basket OK; reject rate back down'], 'MECH', 'P07'),
    ('Fine screens', 'Fine screen ΔP creeping up', ['Flush the screen at the next grade change', 'Flushed; ΔP normal'], 'OPS', 'P07'),
    ('Thickener', 'Thickener shower nozzles plugging', ['Clean nozzles on day shift', 'Cleaned'], 'OPS', 'P07'),
    ('Machine chest', 'Machine chest level control hunting', ['Tune LIC loop', 'Retuned; steady'], 'INST', 'P14'),
    ('Headbox', 'Headbox edge flow streak at the FS', ['Adjust FS edge valve', 'Streak gone on the scanner'], 'OPS', 'P04'),
    ('Fan pump', 'Fan pump packing leaking', ['Adjust packing gland', 'Leak down to a drip'], 'MECH', 'P05'),
    ('Wire guide', 'Wire guide palm drifting to the TS', ['Check guide air supply', 'Regulator replaced'], 'INST', 'P14'),
    ('Forming HP shower', 'Forming HP shower oscillator stalling', ['Check oscillator drive', 'Oscillator motor coupling replaced'], 'MECH', 'P05'),
    ('Flat boxes', 'Flat box cover wear at the TS edge', ['Inspect at the next outage', 'Added to outage scope'], 'MECH', 'P02'),
    ('Couch roll', 'Couch roll seal strip water low', ['Check seal water flow', 'Strainer cleaned'], 'OPS', 'P04'),
    ('1st press top felt', '1st press top felt conditioning low', ['Raise Uhle vacuum setpoint 0.5 inHg', 'Holding'], 'OPS', 'P16'),
    ('2nd press bottom felt', '2nd press bottom felt guide hunting', ['Check guide paddle', 'Paddle cleaned'], 'OPS', 'P16'),
    ('1st press top roll', '1st press doctor chatter', ['Change doctor blade', 'Blade changed; chatter gone'], 'OPS', 'P05'),
    ('Dryer can 4', 'Dryer can 4 doctor blade worn', ['Change blade on the next break', 'Changed'], 'OPS', 'P05'),
    ('Dryer can 13', 'Dryer can 13 condensate flooding (cold can)', ['Check syphon clearance', 'Syphon reset at the outage'], 'MECH', 'P17'),
    ('2nd section PV fan', '2nd section PV fan amps low', ['Check belts', 'Belts tensioned'], 'MECH', 'P05'),
    ('Hood exhaust fan', 'Hood exhaust humidity high', ['Check exhaust fan damper', 'Damper linkage repaired'], 'INST', 'P14'),
    ('Hood supply fan', 'Hood supply fan bearing noisy', ['Grease and monitor', 'Quiet after greasing'], 'MECH', 'P05'),
    ('Reel drive', 'Reel turn-up missed twice on nights', ['Check turn-up sequence timing', 'Timing adjusted'], 'E&I', 'P06'),
    ('Reel drum', 'Spool bar damage at the reel', ['Pull damaged spool', 'Spool sent for repair'], 'OPS', 'P08'),
    ('Winder slitters', 'Winder slitter dust', ['Change slitter blades', 'Changed'], 'OPS', 'P18'),
    ('Winder drums', 'Winder telescoping rolls', ['Check winder tension tapers', 'Taper adjusted'], 'OPS', 'P18'),
    ('Vacuum pump', 'Vacuum pump seal water temperature high', ['Check cooling water', 'Strainer cleaned'], 'MECH', 'P05'),
    ('Steam header', 'Steam header pressure dips at grade changes', ['Review boiler master response', 'Ramp rate changed'], 'INST', 'P17'),
    ('LC cleaners', 'LC cleaner tips plugging', ['Clean tips', 'Cleaned'], 'OPS', 'P07'),
    ('Ragger', 'Ragger rope breaking', ['Re-thread the rope', 'Rethreaded; new rope ordered'], 'OPS', 'P07'),
]

BREAK_WHERE = {'reel': 'Reel drum', 'dryer': 'Dryer can 6', 'press': '2nd press top felt'}


def build(m, proc, seed=5505):
    rnd = random.Random(seed)
    ev, runs, faults = m['events'], m['runs'], m['faults']
    yr = lambda d: Y0 <= d <= TODAY
    wos, actions, issues, rcfas = [], [], [], []

    # ─── PMs: weekly, every two weeks, monthly ───
    PMS = [('Operator rounds: stock prep', 'Pulper', 7, 'OPS', 1), ('Operator rounds: wet end', 'Headbox', 7, 'OPS', 1),
           ('Operator rounds: dry end', 'Dryer can 10', 7, 'OPS', 1), ('Grease felt roll bearings, 1st and 2nd sections', '1st section felt roll 1', 7, 'MILL', 2),
           ('Grease felt roll bearings, 3rd and 4th sections', '3rd section felt roll 1', 7, 'MILL', 2), ('Clean reel scanner heads', 'Reel drum', 7, 'INST', 1),
           ('Lube route: stock prep', 'Pulper', 7, 'MILL', 3), ('Lube route: wet end and press', 'Couch roll', 7, 'MILL', 3),
           ('Lube route: dryers and reel', 'Dryer drive lineup', 7, 'MILL', 4), ('Doctor blade check: dryers', 'Dryer can 1', 7, 'OPS', 2),
           ('Press shower nozzle check', '2nd press top felt HP shower', 7, 'OPS', 1), ('Winder slitter blade change', 'Winder slitters', 7, 'OPS', 1.5),
           ('Press hydraulic unit inspection', '1st press drive', 14, 'MECH', 2), ('Vacuum pump seal water check', 'Vacuum pump', 14, 'MECH', 1),
           ('Screen basket ΔP check', 'Fine screens', 14, 'OPS', 1), ('Rotary joint inspection, all sections', '3rd section rotary joint (DS)', 14, 'MECH', 2),
           ('ADX motor test round', 'REF 1 refiner motor', 30, 'E&I', 6), ('Steam trap survey', 'Steam header', 30, 'MECH', 4),
           ('MCC thermography', 'Dryer drive lineup', 30, 'E&I', 3), ('Felt roll bearing grease, all sections', '2nd section felt roll 1', 30, 'MILL', 4),
           ('Refiner plate gap check, REF 1', 'REF 1 refiner', 30, 'MECH', 1), ('Refiner plate gap check, REF 2', 'REF 2 refiner', 30, 'MECH', 1),
           ('Fan pump seal inspection', 'Fan pump', 30, 'MECH', 1.5), ('Hood fan belt check', 'Hood exhaust fan', 30, 'MECH', 1.5),
           ('Reel spool inspection', 'Reel drum', 30, 'OPS', 2), ('Thickener wire wash', 'Thickener', 30, 'OPS', 3)]
    for i, (desc, asset, every, craft, est) in enumerate(PMS):
        d = Y0 - DAY * 21 + DAY * (i % every)
        while d <= TODAY + DAY * 10:
            if d >= Y0 - DAY * 7:
                done = d + DAY * rnd.choice([0, 0, 0, 1, 2]) if d + DAY * 2 <= TODAY else None
                if done and done > TODAY: done = None
                wos.append(WO(asset, 'PM', desc, d - DAY * 7, priority=4, craft=craft, est=est, planned=d, completed=done))
            d += DAY * every
    for r in ROUTES:
        if r >= Y0 - DAY * 7:
            wos.append(WO('Dryer drive lineup', 'PM', 'Monthly vibration route (Keel Vibration Services)', r - DAY * 7, priority=4, craft='MECH', est=6,
                          planned=r, completed=r))

    # ─── outages: scope (clothing, plates, rolls due; bearings found on the route; inspections) ───
    for o in OUTAGES[2:]:
        od = o['date']; out = o['id']; created = od - DAY * 35
        done = od if od <= TODAY else None
        def ow(asset, desc, craft='MECH', est=8, parts='Reserved', notes='', story='', key='', created_=None, pr=2):
            w = WO(asset, 'PJ', desc, created_ or created, priority=pr, craft=craft, est=est, outage=out, completed=done, parts=parts,
                   notes=notes if done else '', story=story, key=key)
            wos.append(w); return w
        for pos, rr in runs.items():
            for r in rr:
                if r['removed'] and o['start'] <= r['removed'] <= o['end'] + HOUR * 3:
                    nm = POS_NAME[pos]
                    verb = 'Change' if r['kind'] != 'roll' else 'Change out (send to roll shop)'
                    ow(nm, f'{verb} {nm}', 'MILL', 10 if r['kind'] != 'refiner' else 6,
                       notes=f"Removed after {(r['removed'] - r['installed']).days} days. {r['note']}", story=r['story'])
        if o['date'] > TODAY:      # the next outage: what's due
            for pos in runs:
                if due_at_next_outage(runs, pos) or pos == PLANTS['F3']['position']:   # F3: REF 2's Sep 30 set is wearing out early
                    nm = POS_NAME[pos]
                    parts = 'Not reserved' if pos in ('ref-refa', 'ref-refb') else 'Reserved'
                    ow(nm, f"{'Change' if not pos.startswith('ref') else 'Change'} {nm}{' plates' if pos.startswith('ref') else ''}", 'MILL', 8,
                       parts=parts, story='F3' if pos.startswith('ref') else '', created_=TODAY - DAY * rnd.randint(5, 20))
        for desc, asset, craft in (('Inspect dryer can heads and syphons, all sections', 'Dryer can 10', 'MECH'),
                                   ('Change all dryer doctor blades', 'Dryer can 1', 'OPS'),
                                   ('Inspect flat box covers', 'Flat boxes', 'MECH'),
                                   ('Inspect and clean Uhle box covers', '1st press top felt Uhle box', 'OPS'),
                                   ('Headbox slice inspection and clean', 'Headbox', 'OPS'),
                                   ('Pulper extraction plate inspection', 'Pulper', 'MECH'),
                                   ('Screen basket inspection', 'Fine screens', 'MECH'),
                                   ('Rotary joint seal inspection, all sections', '3rd section rotary joint (DS)', 'MECH'),
                                   ('Felt roll bearing checks, all sections', '3rd section felt roll 2', 'MILL'),
                                   ('Hood fan inspection', 'Hood supply fan', 'MECH'),
                                   ('Reel drum bearing inspection', 'Reel drum', 'MECH'),
                                   ('Winder drum alignment check', 'Winder drums', 'MECH'),
                                   ('Change HP shower nozzles, press section', '2nd press top felt HP shower', 'OPS'),
                                   ('MCC lineup clean and torque check', 'Dryer drive lineup', 'E&I'),
                                   ('Calibrate reel scanner', 'Reel drum', 'INST')):
            ow(asset, desc, craft, rnd.choice([4, 6, 8]))
        # deferred / carried items so the next outage has a history to it
        if o['date'] > TODAY:
            for desc, asset in (('Replace 2nd section PV fan belts and sheaves', '2nd section PV fan'), ('Rebuild couch roll seal strips', 'Couch roll')):
                w = ow(asset, desc, 'MECH', 8, parts='Not reserved', created_=B('2026-09-15'))

    # ─── stops: an emergency WO for each, a corrective one for each slowdown ───
    for e in ev:
        d = e['start'].date()
        if not yr(d) or e['kind'] not in ('unplanned', 'slowdown'): continue
        h = e['minutes'] / 60
        if e['kind'] == 'unplanned':
            craft = 'E&I' if e['cause'] in ('motorfail', 'drivefail') else 'MILL' if e['cause'] in ('feltchange', 'fabrichole', 'feltfill') else 'MECH'
            e['wo'] = WO(e['asset'], 'EM', f"{CAUSE_TEXT[e['cause']]}: {e['asset']}", d, priority=1, craft=craft, est=round(h * 3, 1),
                         completed=(e['end']).date(), notes=e['note'], story=e['story'], originator=LEAD_OF[e['crew']])
            wos.append(e['wo'])
        else:
            e['wo'] = WO(e['asset'], 'CM', f"{CAUSE_TEXT[e['cause']]}: {e['asset']}", d, priority=2, craft='MECH', est=4,
                         completed=d + DAY, notes=e['note'], originator=LEAD_OF[e['crew']])
            wos.append(e['wo'])

    # ─── bearing faults found on the route ───
    for f in faults:
        if not f.get('found') or not yr(f['found'].date()): continue
        fd = f['found'].date()
        if f['story'] == 'F2':
            w = WO(f['asset'], 'CM', tx('Change reel drum DS bearing (outer race defect, Keel route Aug 12)'), fd, priority=2, craft='MECH', est=10,
                   outage=f['missed_outage'], parts='Reserved', story='F2', key='F2-wo',
                   notes=tx('Aug 18: bearing not in stores (22238 CCK/W33). Deferred from the Aug 19 outage; ordered, ETA Nov 5. Rescheduled for Nov 11.'))
            w.deferred_on = B('2026-08-18'); w.resched = (B('2026-08-20'), NEXT_OUTAGE['id']); w.wait_parts = (B('2026-08-20'), B('2026-11-05'))
            w.parts = 'On order'
            f['wo'] = w; wos.append(w); continue
        if f['fix_outage']:
            w = WO(f['asset'], 'CM', f"Change {f['asset']} bearing (found on the {fd:%b %d} vibration route)", fd, priority=2, craft='MECH',
                   est=8, outage=f['fix_outage'], completed=OUT_BY_ID[f['fix_outage']]['date'] if OUT_BY_ID[f['fix_outage']]['date'] <= TODAY else None)
        else:
            w = WO(f['asset'], 'CM', f"Change {f['asset']} bearing (found on the {fd:%b %d} vibration route)", fd, priority=1, craft='MECH',
                   est=6, completed=(f['fixed'].date() if f['fixed'] and f['fixed'].date() <= TODAY else None))
        f['wo'] = w; wos.append(w)

    # ─── developing failures someone caught (Bonvoy, rounds, the operators): a WO and a BUS line ───
    for f in m.get('developing', []):
        if not f['found'] or not yr(f['found'].date()): continue
        fd = f['found'].date(); mode = MODE[f['mode']]
        done = f['fixed'].date() if f['fixed'] and f['fixed'].date() <= TODAY else None
        if f['outcome'] == 'calibrated':
            w = WO(f['asset'], 'CM', f"Calibrate: {mode['label']} on {f['asset']}", fd, priority=3, craft='INST', est=2, completed=done, originator=f['owner'])
        elif f['outcome'] == 'outage':
            o = OUT_BY_ID[f['fix_outage']]
            w = WO(f['asset'], 'CM', f"{f['asset']}: {mode['label']} (found {fd:%b %d})", fd, priority=2, craft=f['craft'], est=6,
                   outage=f['fix_outage'], completed=o['date'] if o['date'] <= TODAY else None, originator=f['owner'])
        else:   # a short planned stop
            w = WO(f['asset'], 'CM', f"{CAUSE_TEXT[f['stop']['cause']]}: {f['asset']}", fd, priority=1, craft=f['craft'], est=round(3 * (f['stop']['end'] - f['stop']['start']).total_seconds() / 3600, 1),
                   completed=done, originator=f['owner'], planned=f['stop']['start'].date())
            f['stop']['wo'] = w
        f['wo'] = w; wos.append(w)
        issues.append(Issue(fd, done, f['asset'], f"{f['asset']}: {mode['finding']}",
                            mode['acts'] + ([f"Fixed at the {OUT_BY_ID[f['fix_outage']]['date']:%b %d} outage"] if f['outcome'] == 'outage' else ['Done; running normal']),
                            f['owner'], w))

    # ─── routine corrective work behind the BUS background ───
    d = Y0 - DAY * 10
    while d <= TODAY:
        for _ in range(rnd.choice([0, 1, 1, 2, 2, 3])):
            a, issue, acts, craft, owner = rnd.choice(ROUTINE)
            length = rnd.choice([1, 1, 2, 2, 3, 4, 6, 9])
            end = d + DAY * length if d + DAY * length <= TODAY or rnd.random() < .7 else None
            if end and end > TODAY: end = None
            w = None
            if craft != 'OPS' and rnd.random() < .7:
                w = WO(a, 'CM', issue, d, priority=3, craft=craft, est=rnd.choice([2, 3, 4, 6]), completed=end, originator=owner)
                wos.append(w)
            if d >= Y0 - DAY * 3: issues.append(Issue(d, end, a, issue, acts, owner, w))
        d += DAY

    # ─── BUS lines for the stops, breaks, findings and the planted faults ───
    for e in ev:
        d = e['start'].date()
        if not yr(d): continue
        if e['kind'] == 'unplanned':
            issues.append(Issue(d, d + DAY * rnd.choice([1, 2, 2, 3]), e['asset'], f"{CAUSE_TEXT[e['cause']]}: {e['minutes'] / 60:.1f} h down. {e['note']}",
                                ['Repaired; running', 'Watching after restart', 'Closed'], 'P05' if e['cause'] not in ('motorfail', 'drivefail') else 'P06',
                                e.get('wo'), e['story']))
        elif e['kind'] == 'slowdown':
            issues.append(Issue(d, d + DAY, e['asset'], f"{CAUSE_TEXT[e['cause']]}: machine slowed {e['minutes'] / 60:.1f} h", ['Fixed; back to full rate'], 'P07', e.get('wo')))
    # days with 4+ breaks
    bdays = {}
    for e in ev:
        if e['kind'] == 'break' and yr(e['start'].date()): bdays.setdefault(e['start'].date(), []).append(e)
    for d, bs in sorted(bdays.items()):
        if len(bs) >= 4:
            where = max(sorted(set(b['where'] for b in bs)), key=lambda w: sum(1 for b in bs if b['where'] == w))   # sorted: ties break the same way every run
            issues.append(Issue(d + DAY, d + DAY * 2, BREAK_WHERE[where], f"{len(bs)} sheet breaks in 24 h, mostly at the {where}",
                                ['Shift leads to review break tapes', 'Watching'], 'P04'))
    for f in faults:
        if f.get('found') and yr(f['found'].date()) and f['story'] != 'F2':
            fd = f['found'].date(); end = f['fixed'].date() if f['fixed'] else None
            issues.append(Issue(fd + DAY, end, f['asset'], f"{f['asset']} bearing in Alert on the vibration route",
                                ['WO raised; scheduled' if f['fix_outage'] else 'Planned stop to change it', 'Monitoring daily'], 'P03', f.get('wo')))
    P = PLANTS
    w2 = next(f['wo'] for f in faults if f['story'] == 'F2')
    issues += [
        Issue(B('2026-08-13'), B('2026-08-20'), 'Reel drum DS bearing', tx('Reel drum DS bearing in Alert on the Aug 12 route (0.17 in/s, outer race defect)'),
              [tx('WO raised for the Aug 19 outage'), 'Bearing not in stores; ordering', tx('Deferred from Aug 19: rescheduled Nov 11, parts on order')], 'P03', w2, 'F2', 'Waiting parts'),
        Issue(B('2026-09-09'), None, 'Reel drum DS bearing', tx('Reel drum DS bearing vibration rising (Bonvoy); bearing for Nov 11 on order, ETA Nov 5'),
              ['Daily vibration readings by the shift; grease per Keel', 'Keel to re-check weekly', 'Danger at 0.40 in/s: decide run or stop'], 'P03', w2, 'F2', 'Waiting parts'),
        Issue(B('2026-05-04'), B('2026-05-20'), '2nd press top felt', '2nd press top felt filling: Uhle vacuum up, press solids down',
              ['Raise HP shower pressure; check nozzles', tx('Spraywell audit pulled forward to May 13'), '22% nozzles plugged: cleaned; felt still filling',
               tx('Felt changed May 19 (7.5 h shut)')], 'P16', None, 'F1'),
        Issue(B('2026-05-09'), B('2026-05-19'), '4th section rotary joint (DS)', '4th section steam at its limit on 34 Super: speed held back ~80 fpm',
              ['Running slower on 34 Super until the felt is changed'], 'P17', None, 'F1'),
        Issue(B('2026-10-13'), None, 'REF 2 refiner', tx('REF 2 specific energy climbing fast on the new plates (Sep 30 set)'),
              ['Check plate gap and pattern', 'Gap OK: plates wearing; Ridgeway to look', tx('Both refiners due Nov 11: one plate set on hand, order another')], 'P04', None, 'F3'),
        Issue(B('2026-02-10'), B('2026-02-13'), 'Forming fabric', tx('Forming fabric hole Feb 9 (wad off the headbox approach): 9.5 h down'),
              ['Spare fabric on; RCFA opened', 'Clean headbox approach piping at the outage'], 'P04', None, 'F4'),
    ]
    for x in P['F5']['events']:
        a = DT(x['start']).date()
        issues.append(Issue(a, a + DAY, P['F5']['asset'], f"Steam leak at the 3rd section DS rotary joint: {x['hours']} h down to change the seal",
                            ['Seal kit changed; running'], 'P17', None, 'F5'))

    # ─── RCFAs and their actions ───
    TEMPL = {
        'bearingfail': ('Equipment failure', 'Bearing failed between vibration routes (P-F interval shorter than the monthly route)',
                        'Lubrication interval; monthly route frequency; no online vibration on this asset',
                        ['Add {a} to a two-weekly route', 'Install an online vibration sensor on {a}', 'Review grease type and interval for {a}']),
        'motorfail': ('Equipment failure', 'Motor winding insulation failure', 'Motor not on the ADX test list that month; heat in the MCC room',
                      ['Add {a} motor to the monthly ADX test', 'Rewind and stock a spare motor for {a}', 'MCC room cooling check']),
        'drivefail': ('Electrical', 'Drive tripped on overcurrent; IGBT module failed', 'Drive at 95%+ load on heavy grades',
                      ['Load study for {a} on 34 Super', 'Spare drive module to stores']),
        'syphon': ('Equipment failure', 'Syphon came loose in the can and flooded it', 'Syphon clearance not checked at the last outage',
                   ['Check syphon clearances on {a} section cans at the next outage', 'Add syphon ΔP to the Bonvoy watch list']),
        'steamjoint': ('Equipment failure', 'Rotary joint carbon ring worn through', 'Joint seal kit beyond its life',
                       ['Seal kit change on a fixed interval for {a}']),
        'wrap': ('Process', 'Sheet wrapped the can after a break', 'Doctor blade worn; tail chute air low',
                 ['Change doctor blades on a fixed interval', 'Check tail chute air pressure']),
        'fabric': ('Clothing', 'Forming fabric seam failure', 'Seam stress on heavy grades late in fabric life',
                   ['Review fabric life target with Northbank', 'Seam inspection at mid-life']),
        'felt': ('Clothing', 'Press felt damaged (lump through the nip)', 'Lumps from the save-all',
                 ['Clean the save-all at the outage', 'Check felt shower coverage']),
        'shaft': ('Equipment failure', 'Dryer driveshaft universal joint failed', 'Joint grease interval missed',
                  ['Add driveshaft u-joints to the weekly lube route']),
        'dryerfire': ('Safety / process', 'Dust and broke in the hood ignited', 'Hood cleaning overdue',
                      ['Hood clean at every outage', 'Fire suppression inspection']),
        'boiler': ('Utilities', 'Steam supply dropped: boiler trip', 'Boiler feedwater level control', ['Review boiler trip with utilities']),
        'slime': ('Process', 'Slime break-off at the headbox', 'Biocide program gap', ['Review biocide dosing with the chemical vendor']),
        'fogfan': ('Equipment failure', 'Hood supply fan bearing failure', 'No vibration monitoring on the fan', ['Add the hood fans to the vibration route']),
        'feltchange': ('Clothing', '2nd press top felt filled early: HP shower nozzles plugged (22%) so the felt wasn\'t conditioned',
                       tx('Shower nozzles not checked since the Feb audit; heavier 34 Super run in May; strainer on the shower supply not cleaned'),
                       ['Weekly press shower nozzle check by operations', 'Clean the HP shower supply strainer every outage',
                        'Add Uhle vacuum rate-of-rise to the Bonvoy watch list']),
        'fabrichole': ('Clothing', 'A wad of stock off the headbox approach piping holed the forming fabric',
                       'Stock build-up in the approach piping; no wad detection at the breast roll',
                       [tx('Clean headbox approach piping at the Mar 4 outage'), P['F4']['overdue_action'], 'Add the approach piping to the outage clean list']),
    }
    TEMPL.update(degrade.RCFA_TEMPL)
    dev_of = {id(f['event']): f for f in m.get('developing', []) if f.get('event')}
    def act(title, bucket, owner, created, due, completed=None, **k):
        a = Action(title, bucket, owner, created, due, completed, **k); actions.append(a); return a
    for n, e in enumerate(m['rcfa_events'], 1):
        rid = f'RCFA-SM-{e["start"]:%y}-{n:03d}'
        d = e['start'].date(); opened = d + DAY
        cat, root, contrib, acts = TEMPL.get(e['cause'], ('Equipment failure', f"{CAUSE_TEXT[e['cause']]}", 'Under review', ['Review with the vendor']))
        f = dev_of.get(id(e))
        if f:   # a developing failure nobody acted on: say how long the trend was there
            tags = ', '.join(f'PM1:{k}' for k in f['tags'])
            contrib = f"{contrib}. The trend was in Pi ({tags}) for about {max(1, round(f['pf_days'] * .5))} days before the stop"
        a_short = e['asset']
        lead = 'P04' if cat in ('Process', 'Clothing') else 'P03'
        aids = []
        for k, t in enumerate(acts):
            title = t.format(a=a_short)
            due = opened + DAY * (21 + 21 * k)
            comp = None
            if due + DAY * 5 <= TODAY and rnd.random() < .8: comp = due - DAY * rnd.randint(0, 10)
            elif due <= TODAY and rnd.random() < .3: comp = min(TODAY, due + DAY * rnd.randint(3, 20))
            if e['story'] == 'F4':      # the planted overdue action; the other two were done
                if t == P['F4']['overdue_action']: due, comp = B('2026-04-30'), None
                else: comp = min(due, B('2026-03-04'))
            if e['story'] == 'F1' and k == 2: comp = None; due = B('2026-07-15')
            owner = {'MECH': 'P05', 'E&I': 'P06'}.get('E&I' if e['cause'] in ('motorfail', 'drivefail') else 'MECH')
            if cat in ('Clothing', 'Process'): owner = rnd.choice(['P04', 'P16', 'P07'])
            if e['story'] == 'F4' and k == 1: owner = 'P14'
            if 'Bonvoy' in title: owner = 'P03'
            a = act(f'{title} ({rid})', 'RCFA actions', owner, opened + DAY * 2, due, comp, priority='Important', creator=lead,
                    desc=f'From {rid}: {CAUSE_TEXT[e["cause"]]} on {e["asset"]}, {d:%b %d}. WO {{wo}}.', asset=e['asset'] if e['asset'] in BY_NAME else None,
                    story=e['story'])
            a.rcfa = rid; aids.append(a)
        closed = max((a.completed for a in aids), default=None) if all(a.completed for a in aids) else None
        rcfas.append(dict(id=rid, event=e, opened=opened, closed=closed, status='Closed' if closed else 'Open - actions pending', title=f"{CAUSE_TEXT[e['cause']]}: {e['asset']}",
                          category=cat, root_cause=root, contributing=contrib, lead=lead, actions=aids,
                          downtime_h=round(e['minutes'] / 60, 1), loss=f"{round(e['minutes'] / 60 * 31):,} t", story=e['story']))

    # BUS follow-ups and outage prep in Planner
    for i in issues:
        if i.start >= Y0 and rnd.random() < .22 and i.asset['name'] in BY_NAME:
            due = i.start + DAY * rnd.choice([7, 14, 21])
            comp = (i.end + DAY * rnd.randint(0, 3)) if i.end and i.end + DAY * 3 <= TODAY else (due - DAY * 2 if due + DAY * 5 <= TODAY and rnd.random() < .85 else None)
            if comp and comp > TODAY: comp = None
            act(f"Follow up: {i.issue[:70]} ({i.asset['name']})", 'BUS follow-ups', i.owner, i.start, due, comp, asset=i.asset['name'], creator='P01',
                desc=f'From the BUS sheet, {i.start:%b %d}.')
    for o in OUTAGES[2:]:
        od = o['date']
        for t, own, k in (('Order clothing for the {d} outage', 'P16', 35), ('Confirm crane and riggers for the {d} outage', 'P02', 21),
                          ('Scaffold request for the {d} outage', 'P02', 14), ('Lockout plan for the {d} outage', 'P05', 7),
                          ('Startup checklist for the {d} outage', 'P08', 2)):
            due = od - DAY * k + DAY * 3
            comp = due - DAY * rnd.randint(0, 3) if due <= TODAY else None
            act(t.format(d=f'{od:%b %d}'), 'Outage prep', own, od - DAY * (k + 10), due, comp, creator='P02')
    act(tx('Order a second set of 34" LC refiner plates (REF 1 and REF 2 both due Nov 11)'), 'Outage prep', 'P15', B('2026-10-20'), B('2026-10-28'),
        None, priority='Urgent', creator='P04', asset='REF 2 refiner', story='F3', desc=tx('One Ridgeway set on hand; REF 2 wearing fast. Quote requested Oct 21.'))
    act(tx('Expedite the reel drum DS bearing (22238 CCK/W33), ETA Nov 5'), 'Reliability', 'P15', B('2026-08-20'), B('2026-10-15'), None, priority='Urgent',
        creator='P03', asset='Reel drum DS bearing', story='F2', desc=tx('Deferred from Aug 19: not in stores.') + ' WO {wo}.')
    act(f"Root cause review: 3rd section rotary joint leaks ({', '.join(md(D(e['start']), '%b') for e in PLANTS['F5']['events'])})", 'Reliability', 'P17', B('2026-10-03'), B('2026-11-20'), None,
        priority='Important', creator='P01', asset='3rd section rotary joint (DS)', story='F5', desc='Three seal failures this year; none hit the RCFA threshold.')

    # number everything (by creation date) and fill in WO references
    wos.sort(key=lambda w: (w.created, w.desc))
    for i, w in enumerate(wos): w.no = str(26100000 + 7 * i)
    actions.sort(key=lambda a: (a.created, a.title))
    for i, a in enumerate(actions): a.id = f'SM-{i + 1:04d}'
    for a in actions:
        if '{wo}' in a.desc:
            w = next((f['wo'] for f in faults if f['story'] == 'F2'), None) if a.story == 'F2' else \
                next((e.get('wo') for e in m['rcfa_events'] if getattr(a, 'rcfa', None) and e.get('wo') and a.desc.startswith('From ' + a.rcfa)), None)
            a.desc = a.desc.replace('{wo}', w.no if w else '-')
    for r in rcfas: r['action_ids'] = [a.id for a in r['actions']]
    return dict(wos=wos, actions=actions, issues=issues, rcfas=rcfas)
