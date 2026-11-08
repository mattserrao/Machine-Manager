"""MM LLM demo data, phase 2: the structured sources, written the way they would arrive from the mill.

    demo-data/out/bus/BUS_PM1_YYYY-MM-DD.xlsx         one BUS daily sheet per day (same layout every day)
    demo-data/out/teams/Planner_PM1_YYYY-MM-DD.csv    weekly Teams/Planner export (Mondays; the whole plan)
    demo-data/out/jde/WO_PM1_YYYY-MM-DD.csv           weekly JDE export (Mondays; WOs created or changed in the last 7 days)
    demo-data/out/jde/WO_PM1_full_2026-10-31.csv      one full export as of demo "today"
    demo-data/out/rcfa/RCFA_log_PM1.csv               the RCFA log
    demo-data/out/_truth/*.csv                        ground truth for later phases and checks (never shown to the model)

    python3 tools/demo-data/structured.py            # generate
    python3 tools/demo-data/structured.py --check    # generate to a temp folder and run the checks (CI)

Built from demo-data/backbone/ and the `records:` in tools/demo-data/storylines/. Seeded: the CSVs come out
byte-identical every run. Everyone and every company is fictional.
"""
import csv, os, sys, math, random, shutil, tempfile, datetime as dt
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BACKBONE = os.path.join(ROOT, 'demo-data', 'backbone')
STORIES = os.path.join(HERE, 'storylines')
SEED = 2202
YEAR_START, YEAR_END = dt.date(2025, 11, 1), dt.date(2026, 10, 31)
TODAY = YEAR_END
DAY = dt.timedelta(days=1)

def D(v):
    if v is None or v == '': return None
    if isinstance(v, dt.datetime): return v.date()
    if isinstance(v, dt.date): return v
    return dt.date.fromisoformat(str(v)[:10])

def DT(v):
    if isinstance(v, dt.datetime): return v
    return dt.datetime.fromisoformat(str(v))

def read(name):
    with open(os.path.join(BACKBONE, name)) as f: return list(csv.DictReader(f))

def us(d): return d.strftime('%m/%d/%Y') if d else ''


# ═════════════════════════ Backbone ═════════════════════════
EQUIP = read('equipment.csv'); BY_NAME = {e['name']: e for e in EQUIP}
OUTAGES = read('outages.csv'); OUT = {o['id']: o for o in OUTAGES}
for o in OUTAGES: o['date'] = D(o['start']); o['last'] = D(o['end'])
NORMAL = [o for o in OUTAGES if o['type'] == 'normal']
CREWS = {r['date']: r for r in read('crew_schedule.csv')}
GRADES = read('grade_schedule.csv')
PEOPLE = {p['id']: p for p in read('roster.csv')}
LEADS = {p['crew']: p['id'] for p in PEOPLE.values() if p['role'] == 'Shift lead'}
NAME = lambda pid: PEOPLE[pid]['name']
SECTION_NAME = {e['section']: e['name'][4:] for e in EQUIP if e['kind'] == 'section'}

def outage_on(d):
    return next((o for o in OUTAGES if o['date'] <= d <= o['last']), None)

def next_outage(d, include_annual=True):
    return next((o for o in OUTAGES if o['date'] > d and (include_annual or o['type'] == 'normal')), None)

def grade_at(t):
    s = t.isoformat(timespec='minutes')
    for g in GRADES:
        if g['start'] <= s < g['end']: return g['grade']
    return GRADES[-1]['grade']

def grades_on(d):
    a, b = dt.datetime.combine(d, dt.time(0)).isoformat(timespec='minutes'), dt.datetime.combine(d + DAY, dt.time(0)).isoformat(timespec='minutes')
    seen = []
    for g in GRADES:
        if g['start'] < b and g['end'] > a and g['grade'] != 'DOWN' and g['grade'] not in seen: seen.append(g['grade'])
    return seen


def load_stories():
    import yaml
    out = []
    for fn in sorted(os.listdir(STORIES)):
        if fn.endswith('.yaml'):
            s = yaml.safe_load(open(os.path.join(STORIES, fn)))
            s['records'] = s.get('records') or {}
            out.append(s)
    return out


# ═════════════════════════ Models ═════════════════════════
STATUS = {10: 'Entered', 20: 'Approved', 30: 'Planned - parts not reserved', 35: 'Deferred - next opportunity',
          40: 'Scheduled', 45: 'Waiting on parts', 70: 'In progress', 90: 'Completed', 99: 'Closed'}
WO_TYPE = {'CM': '1 - Corrective', 'PM': '2 - Preventive', 'EM': '3 - Emergency', 'PJ': '4 - Project / outage'}
CRAFT_LEAD = {'MECH': 'P05', 'E&I': 'P20', 'OPS': None, 'MILL': 'P19'}

class WO:
    def __init__(self, **k):
        self.key = k.get('key', ''); self.story = k.get('story', '')
        self.asset = BY_NAME[k['asset']]; self.type = k['type']; self.priority = int(k.get('priority', 3))
        self.desc = k['desc']; self.created = D(k['created']); self.originator = k.get('originator', 'P02')
        self.craft = k.get('craft', 'MECH'); self.est = float(k.get('est_hours', 4))
        self.outage = k.get('outage') or ''; self.completed = D(k.get('completed'))
        self.parts = k.get('parts') or ('NA' if self.type == 'PM' and self.craft == 'OPS' else 'Reserved')
        self.notes = k.get('notes', '') or ''
        self.approved = D(k.get('approved')) or self.created + DAY * (0 if self.type == 'EM' else (1 if self.priority <= 2 else 2))
        self.planned = D(k.get('planned')) or (OUT[self.outage]['date'] if self.outage else None)
        self.resched = None          # (date, new outage id)
        self.deferred_on = None      # date it was deferred
        self.wait_parts = k.get('wait_parts')  # (from, to) dates
        self.act = k.get('act_hours')
        self.no = None
    def outage_at(self, d):
        if self.resched and d >= self.resched[0]: return self.resched[1]
        return self.outage
    def status_at(self, d):
        if self.completed and self.completed <= d:
            return 99 if (d - self.completed).days >= 10 else 90
        if d < self.approved: return 10
        if self.deferred_on and d >= self.deferred_on: return 35
        if self.wait_parts and D(self.wait_parts[0]) <= d < D(self.wait_parts[1]): return 45
        if self.outage_at(d):
            return 30 if self.parts == 'Not reserved' else 40
        if self.planned and d >= self.planned: return 70
        return 20
    def changes(self):
        c = [self.created, self.approved]
        if self.completed: c += [self.completed, self.completed + DAY * 10]
        if self.resched: c.append(self.resched[0])
        if self.deferred_on: c.append(self.deferred_on)
        if self.wait_parts: c += [D(self.wait_parts[0]), D(self.wait_parts[1])]
        return c

class Action:
    def __init__(self, **k):
        self.key = k.get('key', ''); self.story = k.get('story', '')
        self.title = k['title']; self.asset = BY_NAME[k['asset']] if k.get('asset') else None
        self.created = D(k['created']); self.due = D(k['due']); self.completed = D(k.get('completed'))
        self.owner = k['owner']; self.bucket = k.get('bucket', 'General'); self.ref = k.get('ref', '') or ''
        self.creator = k.get('creator') or {'BUS follow-up': 'P01', 'Annual punch list': 'P02', 'Outage punch list': 'P02', 'Outage prep': 'P02'}.get(k.get('bucket'), k['owner']); self.priority = k.get('priority', 'Medium')
        self.started = D(k.get('started')) or (self.created + DAY * 2 if not self.completed or (self.completed - self.created).days > 3 else None)
        self.desc = k.get('desc', '') or ''
        self.id = None
    def progress_at(self, d):
        if self.completed and self.completed <= d: return 'Completed'
        if self.started and self.started <= d: return 'In progress'
        return 'Not started'

class Issue:  # one BUS line, carried day to day until it closes
    def __init__(self, **k):
        self.key = k.get('key', ''); self.story = k.get('story', '')
        self.asset = BY_NAME[k['asset']]; self.start = D(k['start']); self.end = D(k.get('end'))
        self.issue = k['issue']; self.action = k['action']; self.owner = k['owner']
        self.updates = {D(a): b for a, b in (k.get('updates') or {}).items()}
        self.wo_key = k.get('wo') or ''; self.wo = None; self.status = k.get('status')
    def open_on(self, d):
        return self.start <= d and (self.end is None or d <= self.end)
    def action_on(self, d):
        a = self.action
        for u in sorted(self.updates):
            if u <= d: a = self.updates[u]
        return a


# ═════════════════════════ Background templates ═════════════════════════
CORRECTIVE = {   # asset kind → (description templates, craft, typical hours)
    'dryer-can': (['Steam joint leak on {a}', 'Siphon check {a} - flooding suspected', 'Doctor holder repair {a}',
                   'Grease line broken at {a} DS bearing', 'Rotary joint packing leak {a}'], 'MECH', 4),
    'shower': (['Replace plugged nozzles - {a}', 'Oscillator not traversing - {a}', 'Header leak at flange - {a}'], 'MECH', 3),
    'pump': (['Packing leak - {a}', 'Seal water flow low - {a}', 'High vibration, check alignment - {a}'], 'MECH', 5),
    'vacuum': (['Replace worn cover strips - {a}', 'Seal water leak - {a}', 'Vacuum low, check for air leaks - {a}'], 'MECH', 4),
    'roll': (['Doctor blade chatter - {a}', 'Bearing temp running high, check lube - {a}', 'Cover damage inspection - {a}'], 'MECH', 4),
    'refiner': (['Plate gap control fault - {a}', 'Seal water flow low - {a}', 'Refiner loading erratic - {a}'], 'E&I', 3),
    'motor': (['Motor bearing noise - {a}', 'Cooling fan guard loose - {a}'], 'E&I', 3),
    'headbox': (['Slice lip actuator fault - {a}', 'Leak at inlet flange - {a}', 'Pressure transmitter drifting - {a}'], 'E&I', 4),
    'drive': (['Drive trip, investigate - {a}', 'Coupling guard loose - {a}', 'Encoder fault - {a}'], 'E&I', 3),
    'steam': (['Steam trap failed - {a}', 'Condensate valve sticking - {a}', 'DP control unstable - {a}'], 'MECH', 4),
    'ventilation': (['Damper actuator fault - {a}', 'Fan belt replacement - {a}'], 'E&I', 3),
    'hydraulics': (['Hydraulic leak at loading cylinder - {a}', 'Accumulator precharge low - {a}'], 'MECH', 5),
    'instrument': (['Scanner fault, recalibrate - {a}', 'Moisture sensor drift - {a}'], 'E&I', 3),
    'mechanical': (['Spool clamp adjustment - {a}', 'Rail wear inspection - {a}'], 'MECH', 3),
    'fabric': (['Guide paddle sticking - {a}', 'Stretcher near limit - {a}', 'Seam inspection - {a}'], 'MECH', 2),
    'doctor': (['Doctor loading low - {a}', 'Blade wear uneven - {a}'], 'MECH', 2),
}
KIND_WEIGHT = {'dryer-can': 7, 'shower': 4, 'pump': 4, 'vacuum': 3, 'roll': 4, 'refiner': 2, 'motor': 1, 'headbox': 2,
               'drive': 2, 'steam': 4, 'ventilation': 1, 'hydraulics': 1, 'instrument': 2, 'mechanical': 1, 'fabric': 3, 'doctor': 1}
BUS_ISSUE = {   # what an operator would write on the BUS sheet, per asset kind
    'dryer-can': ['{a} - steam leak at joint', '{a} flooding, cold spot on profile', '{a} doctor not loading'],
    'shower': ['{a} - plugged nozzles, streaks', '{a} oscillator stopped', '{a} header leaking'],
    'pump': ['{a} packing leaking', '{a} running noisy', '{a} seal water low'],
    'vacuum': ['{a} vacuum low', '{a} covers worn, wear on fabric', '{a} seal water leak'],
    'roll': ['{a} bearing running hot', '{a} doctor chattering', '{a} cover marked'],
    'refiner': ['{a} load swinging', '{a} plate gap fault', '{a} seal water alarm'],
    'motor': ['{a} noisy', '{a} running hot'],
    'headbox': ['{a} slice actuator fault', '{a} pressure swinging', '{a} small leak at inlet'],
    'drive': ['{a} tripped', '{a} load swinging', '{a} coupling guard loose'],
    'steam': ['{a} - trap blowing through', '{a} DP control hunting', '{a} condensate valve sticking'],
    'ventilation': ['{a} damper not responding', '{a} fan belt squealing'],
    'hydraulics': ['{a} small oil leak', '{a} pressure drifting'],
    'instrument': ['{a} profile looks off, recal requested', '{a} faulted twice overnight'],
    'mechanical': ['{a} clamp not seating', '{a} rails need cleaning'],
    'fabric': ['{a} guiding to TS', '{a} stretcher near the end', '{a} seam marking'],
    'doctor': ['{a} loading low', '{a} uneven blade wear'],
}
BUS_ACTION = {  # next step as written on the sheet, by who owns it; with_wo: once a WO exists
    'MECH': ['Millwrights to look at today', 'Check on next walk-down', 'Monitor, write WO if worse', 'Tightened up, monitoring'],
    'MILL': ['Millwrights to look at today', 'Check on next walk-down', 'Monitor, write WO if worse'],
    'E&I': ['E&I to troubleshoot', 'E&I checking loop today', 'Monitor, E&I on call if it trips again'],
    'OPS': ['Ops adjusted, monitoring', 'Process eng. reviewing trends', 'Crews to watch on next grade change', 'Quality checking reel samples'],
    'with_wo': ['WO written', 'WO written, parts on hand', 'WO written, planner scheduling'],
}
CRAFT_OWNERS = {'MECH': ['P05', 'P19'], 'MILL': ['P19'], 'E&I': ['P20']}
PROCESS_ISSUES = [('Base ply headbox', 'Base ply formation blotchy on 33# - check headbox consistency'),
                  ('QCS scanner', 'Moisture profile edges wet on DS'), ('PM1 Reel', 'Reel turn-up misses x2 overnight'),
                  ('Top ply headbox', 'Top ply streaks at TS'), ('PM1 Press section', 'Press moisture higher after grade change'),
                  ('PM1 Refiners', 'Freeness swinging on base ply'), ('PM1 Calender', 'Caliper profile high at DS edge')]
OUTAGE_PMS = ['Outage wash-up - wet end', 'Outage wash-up - press section', 'Change 1st press doctor blades', 'Change 2nd press doctor blades',
              'Inspect couch roll seal strips - base ply', 'Inspect couch roll seal strips - top ply', 'Clean HP shower nozzles - base ply',
              'Clean HP shower nozzles - top ply', 'Inspect Uhle box covers - press', 'Inspect dryer doctor blades - 2nd section',
              'Inspect dryer doctor blades - 3rd section', 'Change calender doctor blades', 'Inspect reel spool rails',
              'Steam trap survey - 2nd section', 'Steam trap survey - 3rd section', 'Lubrication check - press section bearings',
              'Lubrication check - dryer bearings 1st section', 'Inspect felt run rolls - press', 'Inspect lumpbreaker cover',
              'Check fan pump couplings', 'Inspect headbox slice lips', 'Inspect vacuum pump seals', 'Rope run inspection - 2nd/3rd section',
              'Inspect pocket ventilation ducts', 'Calender hydraulic filter change', 'Inspect refiner seal water', 'Clean flat box covers',
              'Inspect press loading cylinders', 'Check dryer fabric seams', 'Inspect felt conditioning showers']
OUTAGE_PM_ASSET = lambda t: ('PM1 Press section' if 'press' in t.lower() else 'PM1 2nd dryer section' if '2nd' in t
                             else 'PM1 3rd dryer section' if '3rd' in t or 'dryer' in t.lower() or 'rope' in t.lower() else 'PM1 Calender' if 'calender' in t.lower()
                             else 'PM1 Reel' if 'reel' in t.lower() else 'PM1 Base ply wire' if 'base ply' in t or 'lumpbreaker' in t else 'PM1 Top ply wire' if 'top ply' in t
                             else 'PM1 Refiners' if 'refiner' in t.lower() else 'PM1 Press section')
PUNCH = ['Replace missing guard bolts at {s}', 'Touch up insulation on steam header - {s}', 'Clean up hydraulic oil at {s}',
         'Re-label valves after annual work - {s}', 'Return spare parts to stores - {s}', 'Fix handrail at {s} walkway',
         'Close out lockout tags review - {s}', 'Re-check doctor loading after restart - {s}', 'Update drawings for annual changes - {s}',
         'Repair leaking sight glass - {s}', 'Re-torque flange bolts at {s}', 'Remove temporary scaffolding at {s}', 'Clean drains - {s}',
         'Verify instrument loop checks - {s}', 'Re-install insulation blankets - {s}']
GENERAL_ACTIONS = [('Process', 'Review grade change procedure 26# to 33#', 'P04'), ('Process', 'Trial new retention aid dosage', 'P04'),
                   ('Reliability', 'Update vibration route points list', 'P03'), ('Reliability', 'Lube route review - dryer section', 'P03'),
                   ('Safety', 'Walkway lighting survey - dryer aisle', 'P05'), ('Quality', 'Moisture profile study on 26#', 'P22'),
                   ('Training', 'Crew training on felt change procedure', 'P01'), ('Process', 'Steam/condensate audit with energy team', 'P04'),
                   ('Reliability', 'Bearing temperature alarm limits review', 'P03'), ('Quality', 'Caliper profile complaint follow-up', 'P22')]
SECTION_FOR_PUNCH = ['wet end', 'press section', '1st dryer section', '2nd dryer section', '3rd dryer section', 'calender', 'reel', 'refiners']

# My Machine clothing / plate / roll changes on the outage grid (consistent with the storylines)
CHANGES = {
    'p2-felt-top':   ['2025-12-10', '2026-03-04', '2026-04-15', '2026-07-08', 'ANNUAL'],
    'form-bottom':   ['2025-12-10', '2026-01-21', '2026-03-04', '2026-05-27', '2026-08-19', '2026-11-11'],
    'form-top':      ['2025-12-10', '2026-03-04', '2026-05-27', '2026-08-19', '2026-11-11'],
    'ref-bp1':       ['2025-12-10', '2026-03-04', '2026-05-27', '2026-08-19', '2026-11-11'],
    'ref-bp2':       ['2025-12-10', '2026-03-04', '2026-05-27', '2026-08-19'],     # Nov 11 change is S04-WO2
    'ref-tp1':       ['2026-01-21', '2026-04-15', '2026-07-08', 'ANNUAL'],
    'ref-tp2':       ['2026-01-21', '2026-04-15', '2026-07-08', 'ANNUAL'],
    'd1-felt':       ['2026-04-15'],
    'd2-felt-bottom': ['2026-07-08'],
    'd2-felt-top':   ['ANNUAL'],
    'd3-felt-bottom': ['ANNUAL'],
    'p1-roll-bottom': ['ANNUAL'],
}
EVERY_OUTAGE = ['p1-felt-top', 'p-tandem-felt']
BACKGROUND_RCFA = [  # id, event, title, asset, downtime h, category, root cause, contributing, lead, action titles
    ('RCFA-2025-11', '2025-11-14', 'Calender top roll bearing temperature trip', 'Calender top roll', 3.5, 'Equipment - lubrication',
     'Grease line to DS bearing blocked', 'Auto-lube alarm not wired to DCS', 'P03', ['Replace DS grease line', 'Wire auto-lube fault to DCS alarm']),
    ('RCFA-2025-12', '2025-12-02', 'Wet-end breaks after press felt change', 'Tandem felt', 2.0, 'Operations - procedure',
     'Felt break-in showers left at full pressure', 'Start-up checklist missing shower step', 'P04', ['Add shower setpoints to felt change checklist', 'Crew review of break-in procedure']),
    ('RCFA-2025-13', '2025-12-29', '2nd section drive trip - encoder cable', '2nd section drive group', 1.5, 'Equipment - electrical',
     'Encoder cable chafed on guard edge', 'Cable not in tray after previous repair', 'P20', ['Re-route encoder cable in tray', 'Check other drive encoders for same issue']),
    ('RCFA-2026-01', '2026-01-09', 'Frozen shower header after cold snap', 'Base ply HP shower', 4.0, 'Equipment - design',
     'Shower supply line not heat traced at wall penetration', 'Building door left open overnight', 'P05', ['Install heat trace on shower supply', 'Add cold weather checks to shift rounds']),
    ('RCFA-2026-04', '2026-05-08', 'Vacuum pump 3 seal failure', 'Vacuum pump 3', 2.5, 'Equipment - wear',
     'Seal water flow lost - plugged strainer', 'No low-flow alarm on seal water', 'P03', ['Add seal water flow switch with alarm', 'Strainer cleaning to weekly PM']),
    ('RCFA-2026-05', '2026-06-11', 'Reel spool dropped during turn-up', 'Reel spool handling', 1.0, 'Safety - near miss',
     'Spool clamp not fully seated before lift', 'Clamp position sensor dirty', 'P01', ['Clean and test clamp sensors weekly', 'Interlock review with E&I']),
    ('RCFA-2026-06', '2026-07-21', 'Base ply slice actuator failure', 'Base ply headbox', 3.0, 'Equipment - electrical',
     'Actuator motor failed - water ingress', 'Cover gasket missing after last repair', 'P20', ['Replace actuator and cover gasket', 'Inspect all slice actuator covers at next outage']),
    ('RCFA-2026-07', '2026-08-07', '3rd section flooding can 52 - steam trap failure', '3rd section steam & condensate', 2.0, 'Equipment - wear',
     'Failed thermodynamic trap on can 52 condensate', 'Trap survey overdue by 2 months', 'P03', ['Replace can 52 trap', 'Bring trap survey back on schedule']),
    ('RCFA-2026-08', '2026-09-03', 'Tandem felt seam failure', 'Tandem felt', 7.0, 'Equipment - clothing',
     'Seam loop damage from wad in 2nd nip', 'Felt at end of life (6 weeks)', 'P04', ['Review tandem felt seam inspection', 'Ask Marlow for seam failure analysis']),
    ('RCFA-2026-09', '2026-10-12', 'Start-up delay after annual - 2nd press loading hydraulics', 'PM1 Press section', 6.0, 'Maintenance - workmanship',
     'Hydraulic valve installed reversed during annual rebuild', 'No functional test in start-up checklist', 'P05', ['Add hydraulic functional test to annual start-up checklist', 'Tag valve orientation on rebuild drawings']),
    ('RCFA-2026-10', '2026-10-24', 'QCS scanner failure - off-spec moisture roll', 'QCS scanner', 0.0, 'Equipment - instrument',
     'Scanner head cooling air blocked', 'Filter change missed', 'P22', ['Add scanner air filter to monthly PM', 'Rejected roll disposition with quality']),
]


# ═════════════════════════ Build ═════════════════════════
def build():
    rnd = random.Random(SEED)
    stories = load_stories()
    wos, actions, issues, downtime, rcfas = [], [], [], [], []

    # ---- Storyline records ----
    for s in stories:
        r, sid = s['records'], s['id']
        for w in r.get('wo', []): wos.append(WO(story=sid, **w))
        for a in r.get('action', []): actions.append(Action(story=sid, **a))
        for i in r.get('bus', []): issues.append(Issue(story=sid, **i))
        for dtm in r.get('downtime', []):
            downtime.append(dict(start=DT(dtm['start']), hours=float(dtm['hours']), asset=dtm['asset'], kind=dtm['kind'], note=dtm['note'], story=sid))
        for b in r.get('breaks', []):
            t = DT(b['at'])
            downtime.append(dict(start=t, hours=b['minutes'] / 60, asset=b['asset'], kind='break', note=b['note'], story=sid))
            nd = t.date() + DAY
            issues.append(Issue(story=sid, asset=b['asset'], start=nd, end=nd,
                                issue=f"Break {t.strftime('%H:%M')} {t.strftime('%a')} - {b['note']} ({grade_at(t)})",
                                action='Rethreaded, no cause found', owner=LEADS[CREWS[t.date().isoformat()]['day_crew' if 6 <= t.hour < 18 else 'night_crew']]))
        for rc in r.get('rcfa', []): rcfas.append(dict(rc, story=sid))
        for p in r.get('pm_series', []):
            if p.get('every') == 'outage':
                for o in OUTAGES:
                    if D(p['start']) <= o['date'] <= TODAY + DAY * 30:
                        wos.append(WO(story=sid, asset=p['asset'], type='PM', priority=3, desc=p['desc'], created=o['date'] - DAY * 14,
                                      craft=p['craft'], est_hours=p['est_hours'], outage=o['id'], completed=o['date'] if o['date'] <= TODAY else None))
            else:
                d = D(p['start'])
                while d <= TODAY:
                    wos.append(WO(story=sid, asset=p['asset'], type='PM', priority=4, desc=p['desc'], created=d - DAY * 7, planned=d,
                                  craft=p['craft'], est_hours=p['est_hours'], completed=d, parts='NA'))
                    d += DAY * p['every_days']

    # ---- Clothing, plates and rolls changed at outages ----
    pos_asset = {e['position_id']: e['name'] for e in EQUIP if e['position_id']}
    verb = lambda pos: 'Recover' if pos.endswith('roll-bottom') else 'Change'
    def change_wo(pos, oid, story=''):
        o = OUT[oid]; nm = pos_asset[pos]
        what = f'{nm} plates' if pos.startswith('ref-') else nm
        return WO(story=story, asset=nm, type='PM', priority=3, desc=f'{verb(pos)} {what}', created=o['date'] - DAY * 21, craft='MECH',
                  est_hours=6 if pos.startswith('ref-') else 8, outage=oid, completed=o['date'] if o['date'] <= TODAY else None)
    for pos, dates in CHANGES.items():
        for d in dates:
            oid = 'OUT-2026-ANNUAL' if d == 'ANNUAL' else f'OUT-{d}'
            if pos == 'form-bottom' and d == '2026-03-04':
                continue   # S03 changed it early on Feb 18 by emergency WO; the outage change is below
            w = change_wo(pos, oid)
            if pos == 'form-bottom' and d == '2025-12-10': w.desc = 'Install Halden PF-3315 trial fabric - base ply'; w.story = 'S06'
            if pos == 'form-bottom' and d == '2026-01-21': w.desc = 'Change base ply forming fabric - back to Northbank NX-2740 after trial'; w.story = 'S06'
            if pos == 'p2-felt-top' and d == '2026-04-15': w.desc = 'Change 2nd press top felt - pulled early, high fill'; w.created = D('2026-04-09'); w.approved = D('2026-04-10'); w.story = 'S02'
            if pos == 'ref-bp1' and d == '2026-11-11': w.parts = 'Reserved'; w.story = 'S04'
            if pos.startswith('ref-bp') and d == '2026-08-19': w.story = 'S04'
            if pos == 'p1-roll-bottom': w.desc = 'Change 1st press bottom roll - send for recover (Pellham)'
            wos.append(w)
    wos.append(WO(story='S03', asset='Base ply forming fabric', type='PM', priority=3, desc='Change base ply forming fabric - back on outage cycle',
                  created=D('2026-02-23'), craft='MECH', est_hours=8, outage='OUT-2026-03-04', completed=D('2026-03-04')))
    for o in OUTAGES:
        for pos in EVERY_OUTAGE:
            wos.append(change_wo(pos, o['id']))

    # ---- Background RCFAs: downtime, emergency WO, BUS line, actions ----
    for rid, ev, title, asset, hrs, cat, root, contrib, lead, acts in BACKGROUND_RCFA:
        e = D(ev); t = dt.datetime.combine(e, dt.time(rnd.randint(0, 23), rnd.choice([0, 15, 30, 45])))
        if hrs: downtime.append(dict(start=t, hours=hrs, asset=asset, kind='equipment', note=title, story=''))
        key = rid + '-WO'
        wos.append(WO(key=key, asset=asset, type='EM' if hrs >= 2 else 'CM', priority=1 if hrs >= 2 else 2, desc=f'{title} - repair',
                      created=e, craft='E&I' if 'electrical' in cat or 'instrument' in cat else 'MECH', est_hours=max(2, hrs), completed=e + DAY * (0 if hrs >= 2 else 1)))
        issues.append(Issue(asset=asset, start=e + DAY, end=e + DAY * 3, issue=f'{title}' + (f' - {hrs:g} h down' if hrs else ''),
                            action='Repaired, running. RCFA opened', owner=lead, wo=key))
        opened = e + DAY * rnd.randint(3, 6); keys = []
        for n, a in enumerate(acts):
            due = opened + DAY * rnd.randint(14, 45)
            done = None if (rid == 'RCFA-2026-10' or (rid == 'RCFA-2026-09' and n == 1)) and due > TODAY else min(due - DAY * rnd.randint(0, 6), TODAY - DAY)
            if done and done < opened: done = opened + DAY
            k = f'{rid}-A{n + 1}'; keys.append(k)
            actions.append(Action(key=k, title=a, asset=asset, created=opened, due=due, completed=done, owner=lead if n == 0 else rnd.choice(['P02', 'P05', 'P03', 'P20']),
                                  bucket='RCFA', ref=rid))
        closed = max([a.completed for a in actions if a.key in keys and a.completed] or [None], default=None) if all(
            a.completed for a in actions if a.key in keys) else None
        rcfas.append(dict(id=rid, event=e, opened=opened, closed=closed, title=title, asset=asset, downtime_h=hrs, category=cat,
                          root_cause=root, contributing=contrib, lead=lead, actions=keys, story=''))

    # ---- Normal-outage PMs and punch lists ----
    for o in NORMAL:
        picks = rnd.sample(OUTAGE_PMS, rnd.randint(22, 30))
        for t in picks:
            wos.append(WO(asset=OUTAGE_PM_ASSET(t), type='PM', priority=3, desc=t, created=o['date'] - DAY * rnd.randint(10, 21), craft='MECH' if 'Inspect' in t or 'Change' in t else 'OPS',
                          est_hours=rnd.choice([1, 2, 2, 3, 4]), outage=o['id'], completed=o['date'] if o['date'] <= TODAY else None))
        if o['date'] <= TODAY:
            for _ in range(rnd.randint(6, 10)):
                s = rnd.choice(SECTION_FOR_PUNCH); c = o['date'] + DAY
                actions.append(Action(title=rnd.choice(PUNCH).format(s=s), created=c, due=c + DAY * rnd.randint(7, 21), completed=c + DAY * rnd.randint(2, 7),
                                      owner=rnd.choice(['P05', 'P19', 'P20', 'P02']), bucket='Outage punch list', ref=o['id']))

    # ---- Weekly lube routes, monthly vibration route, steam trap surveys ----
    d = YEAR_START
    while d <= TODAY:
        if d.weekday() == 1:
            for sec in ['wet end', 'press section', 'dryer section', 'calender & reel']:
                wos.append(WO(asset={'wet end': 'PM1 Base ply wire', 'press section': 'PM1 Press section', 'dryer section': 'PM1 2nd dryer section',
                                     'calender & reel': 'PM1 Calender'}[sec], type='PM', priority=4, desc=f'Weekly lube route - {sec}',
                              created=d - DAY * 7, planned=d, craft='MILL', est_hours=2, completed=d if not outage_on(d) else d + DAY, parts='NA'))
        if d.day == 14 or (d.day == 19 and d.month == 10 and d.year == 2026):
            if not (d.day == 14 and d.month == 10 and d.year == 2026):  # October route ran on the 19th (annual)
                wos.append(WO(asset='PM1 2nd dryer section', type='PM', priority=4, desc='Monthly vibration route - Keel Vibration Services',
                              created=d - DAY * 10, planned=d, craft='MECH', est_hours=8, completed=d, parts='NA'))
        if d.day == 5 and d.month in (11, 2, 5, 8):
            wos.append(WO(asset='3rd section steam & condensate', type='PM', priority=4, desc='Quarterly steam trap survey - dryers',
                          created=d - DAY * 14, planned=d, craft='MECH', est_hours=12, completed=d if d.month != 5 else None,
                          wait_parts=None))
        d += DAY
    # the May survey slipped (RCFA-2026-07 "trap survey overdue"); it gets done in August
    for w in wos:
        if w.desc == 'Quarterly steam trap survey - dryers' and w.created.month == 4:
            w.completed = D('2026-08-10'); w.notes = 'Slipped from May; done after RCFA-2026-07'

    # ---- Annual outage scope (S09) and punch list (S08) ----
    sc = next(s for s in stories if s['records'].get('annual_scope'))['records']['annual_scope']
    annual = [w for w in wos if w.outage == 'OUT-2026-ANNUAL']
    a0, a1 = D(sc['created'][0]), D(sc['created'][1])
    pool = list(OUTAGE_PMS) + [f'{t} - annual' for t in ['Rebuild 2nd press loading hydraulics', 'Replace 3rd section rope sheaves', 'Overhaul vacuum pump 1',
                                                       'Inspect all dryer can journals - 2nd section', 'Replace headbox inlet gaskets - base ply',
                                                       'Calender hydraulic unit service', 'Re-tube steam header - 1st section', 'Replace reel drum bearings',
                                                       'Overhaul fan pump - top ply', 'Inspect refiner shafts and bearings', 'Replace pocket ventilation dampers - 3rd section',
                                                       'NDT dryer cans 11-20 (insurance)', 'NDT dryer cans 45-54 (insurance)', 'Replace doctor backs - 2nd section',
                                                       'Thermal survey MCC - dryer drives', 'Replace flat box covers - top ply', 'Inspect couch roll shell - base ply']]
    n = 0
    while len(annual) < sc['total']:
        t = pool[n % len(pool)] + ('' if n < len(pool) else f' ({n // len(pool) + 1})'); n += 1
        cr = a0 + DAY * rnd.randint(0, (a1 - a0).days)
        w = WO(story='S09', asset=OUTAGE_PM_ASSET(t), type='PJ' if 'annual' in t else 'PM', priority=3, desc=t, created=cr,
               craft=rnd.choice(['MECH', 'MECH', 'E&I', 'MILL']), est_hours=rnd.choice([4, 6, 8, 12, 16, 24]), outage='OUT-2026-ANNUAL',
               completed=OUT['OUT-2026-ANNUAL']['date'] + DAY * rnd.randint(0, 6))
        wos.append(w); annual.append(w)
    extra = [w for w in annual if w.story == 'S09' and 'annual' in w.desc]
    for w in extra[:sc['deferred']]:
        w.completed = None; w.deferred_on = D('2026-10-02'); w.wait_parts = ('2026-09-08', '2026-10-02'); w.notes = 'Deferred - parts not received'
    for w in extra[sc['deferred']:sc['deferred'] + sc['not_finished']]:
        w.completed = None; w.resched = (D('2026-10-12'), 'OUT-2026-11-11'); w.notes = 'Not finished in the annual - carried to Nov 11'
    pl = next(s for s in stories if s['records'].get('punch_list'))['records']['punch_list']
    c0, c1 = D(pl['created'][0]), D(pl['created'][1])
    for i in range(pl['count']):
        s = SECTION_FOR_PUNCH[i % len(SECTION_FOR_PUNCH)]; c = c0 if i % 2 == 0 else c1
        overdue = i < pl['overdue_at_end']
        due = c + DAY * (rnd.randint(7, 15) if overdue else rnd.randint(7, 30))
        done = None if overdue or due > TODAY else min(due, TODAY) - DAY * rnd.randint(0, 3)
        if not overdue and due <= TODAY and done is None: done = due
        actions.append(Action(story='S08', title=PUNCH[i % len(PUNCH)].format(s=s), created=c, due=due, completed=done,
                              owner=['P05', 'P19', 'P20', 'P02', 'P03'][i % 5], bucket='Annual punch list', ref='OUT-2026-ANNUAL'))

    # ---- Background breaks ----
    d = YEAR_START
    while d <= TODAY:
        if not outage_on(d) and rnd.random() < .33:
            t = dt.datetime.combine(d, dt.time(rnd.randint(0, 23), rnd.randint(0, 59)))
            downtime.append(dict(start=t, hours=rnd.randint(15, 70) / 60, asset=rnd.choice(['Tandem felt', 'Base ply forming fabric', '1st section unorun felt', 'Reel drum', 'Calender top roll']),
                                 kind='break', note=rnd.choice(['break at press pickup', 'turn-up miss', 'wet end break', 'break in 1st section']), story=''))
        d += DAY

    # ---- Background BUS issues, some with WOs and actions ----
    kinds = [k for k in KIND_WEIGHT for _ in range(KIND_WEIGHT[k])]
    by_kind = defaultdict(list)
    for e in EQUIP:
        if e['kind'] in KIND_WEIGHT: by_kind[e['kind']].append(e['name'])
    def owner_for(craft, d):
        return rnd.choice(CRAFT_OWNERS[craft]) if craft in CRAFT_OWNERS else LEADS[CREWS[d.isoformat()]['day_crew']]
    d = YEAR_START
    while d <= TODAY:
        active = sum(1 for i in issues if i.open_on(d))
        want = rnd.choice([1, 1, 2, 2, 2, 3]) if d.weekday() < 5 else rnd.choice([0, 1, 1])
        if outage_on(d - DAY): want += 2
        want = max(want, 5 - active)
        if active >= 11: want = 0
        for _ in range(want):
            if rnd.random() < .15:
                a, txt = rnd.choice(PROCESS_ISSUES); craft = 'OPS'; own = rnd.choice(['P04', 'P22'])
            else:
                k = rnd.choice(kinds); a = rnd.choice(by_kind[k]); craft = CORRECTIVE[k][1]
                txt = rnd.choice(BUS_ISSUE[k]).format(a=a); own = owner_for(craft, d)
            dur = min(14, max(0, int(rnd.expovariate(1 / 2.4))))
            it = Issue(asset=a, start=d, end=d + DAY * dur, issue=txt, action=rnd.choice(BUS_ACTION[craft]), owner=own)
            if craft != 'OPS' and rnd.random() < .45:
                k = BY_NAME[a]['kind']; tmpl, cr, hrs = CORRECTIVE.get(k, CORRECTIVE['roll'])
                at_outage = rnd.random() < .3
                o = next_outage(d + DAY * 3, include_annual=False) if at_outage else None
                w = WO(asset=a, type='CM', priority=rnd.choice([2, 3, 3, 3]), desc=rnd.choice(tmpl).format(a=a), created=d, originator=own if own in ('P03', 'P04') else 'P02',
                       craft=cr, est_hours=hrs + rnd.randint(-1, 3), outage=o['id'] if o else '',
                       completed=(o['date'] if o and o['date'] <= TODAY else None) if o else min(d + DAY * max(1, dur), TODAY + DAY * 30))
                if w.completed and w.completed > TODAY: w.completed = None
                if not o and rnd.random() < .15:
                    w.wait_parts = (d + DAY, d + DAY * (3 + dur)); it.status = 'Waiting parts' if dur > 2 else None
                if o: it.end = d + DAY * min(dur, 4); it.action = f"WO for {o['date'].strftime('%b %d')} outage"
                if not o: it.action = rnd.choice(BUS_ACTION['with_wo'])
                if w.wait_parts and dur > 2: it.action = 'WO written, waiting on parts'
                w.key = f'BG-WO-{len(wos)}'; it.wo_key = w.key; wos.append(w)
            if (craft == 'OPS' and rnd.random() < .6) or (craft != 'OPS' and rnd.random() < .12):
                due = d + DAY * rnd.randint(7, 21); done = d + DAY * rnd.randint(3, 20)
                actions.append(Action(title=('Follow up: ' + txt) if craft != 'OPS' else txt, asset=a if a in BY_NAME else None,
                                      created=d, due=due, completed=done if done < TODAY else (None if due >= TODAY else TODAY - DAY),
                                      owner=own, bucket='BUS follow-up'))
            if it.end and it.end > TODAY: it.end = None if rnd.random() < .5 else TODAY
            issues.append(it)
        d += DAY

    # ---- Background corrective WOs that never hit the BUS sheet ----
    d = YEAR_START
    while d <= TODAY:
        for _ in range(rnd.choice([1, 2, 2, 3, 3, 4]) if d.weekday() < 5 else rnd.choice([0, 1])):
            k = rnd.choice(kinds); a = rnd.choice(by_kind[k]); tmpl, cr, hrs = CORRECTIVE[k]
            o = next_outage(d + DAY * 3, include_annual=False) if rnd.random() < .25 else None
            done = o['date'] if o else d + DAY * rnd.randint(1, 25)
            wos.append(WO(asset=a, type='CM', priority=rnd.choice([2, 3, 3, 3, 4, 4]), desc=rnd.choice(tmpl).format(a=a), created=d,
                          originator=rnd.choice(['P02', 'P05', 'P03'] + list(LEADS.values())), craft=cr, est_hours=hrs + rnd.randint(-1, 4),
                          outage=o['id'] if o else '', completed=done if done <= TODAY else None))
        d += DAY

    # ---- General improvement actions ----
    for n in range(60):
        b, t, own = GENERAL_ACTIONS[n % len(GENERAL_ACTIONS)]
        c = YEAR_START + DAY * rnd.randint(0, 350)
        due = c + DAY * rnd.randint(14, 60)
        actions.append(Action(title=t + ('' if n < len(GENERAL_ACTIONS) else f' ({c.strftime("%b")})'), created=c, due=due,
                              completed=None if due > TODAY else due - DAY * rnd.randint(0, 10), owner=own, bucket=b))

    # ---- Numbering ----
    wos.sort(key=lambda w: (w.created, w.desc))
    no = 2584113
    for w in wos:
        no += rnd.randint(1, 9); w.no = str(no)
    keyed = {w.key: w for w in wos if w.key}
    for i in issues:
        if i.wo_key: i.wo = keyed[i.wo_key]
    actions.sort(key=lambda a: (a.created, a.title))
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
    for a in actions:
        a.id = ''.join(rnd.choice(alphabet) for _ in range(28))
    akey = {a.key: a for a in actions if a.key}
    for a in actions:   # RCFA actions point at the RCFA; WO-linked actions show the WO number
        if a.ref in keyed: a.desc = f'WO {keyed[a.ref].no}'
        elif a.ref.startswith('RCFA'): a.desc = a.ref
    for r in rcfas:
        r['action_ids'] = [akey[k].id for k in r['actions']]
        if r.get('story'):
            acts = [akey[k] for k in r['actions']]
            r['closed'] = max(a.completed for a in acts) if all(a.completed for a in acts) else None
    issues.sort(key=lambda i: (i.start, i.issue))
    downtime.sort(key=lambda x: x['start'])
    return dict(wos=wos, actions=actions, issues=issues, downtime=downtime, rcfas=sorted(rcfas, key=lambda r: r['id']), stories=stories)


# ═════════════════════════ Writers ═════════════════════════
JDE_COLS = ['Order Number', 'Order Type', 'Type of WO', 'Description', 'Asset Number', 'Asset Description', 'Location',
            'Priority', 'Status', 'Status Description', 'Requested Date', 'Planned Start', 'Completed Date', 'Originator',
            'Assigned To', 'Craft', 'Est Hours', 'Act Hours', 'Outage', 'Parts Status', 'Completion Notes']

def wo_row(w, d):
    st = w.status_at(d); out = w.outage_at(d)
    act = '' if st < 90 else f"{w.est * (0.8 + (int(w.no) % 7) / 10):.1f}"
    return {'Order Number': w.no, 'Order Type': 'WM', 'Type of WO': WO_TYPE[w.type], 'Description': w.desc,
            'Asset Number': w.asset['asset_no'], 'Asset Description': w.asset['name'], 'Location': f"PM1 / {SECTION_NAME.get(w.asset['section'], '')}",
            'Priority': w.priority, 'Status': st, 'Status Description': STATUS[st], 'Requested Date': us(w.created),
            'Planned Start': us(OUT[out]['date'] if out else w.planned), 'Completed Date': us(w.completed) if st >= 90 else '',
            'Originator': NAME(w.originator), 'Assigned To': NAME(CRAFT_LEAD[w.craft]) if CRAFT_LEAD.get(w.craft) else 'Operations',
            'Craft': w.craft, 'Est Hours': f'{w.est:g}', 'Act Hours': act,
            'Outage': (out.replace('OUT-', '') if out else ''), 'Parts Status': w.parts if st < 90 else '',
            'Completion Notes': w.notes if st >= 90 or st == 35 or w.resched else ''}

PLANNER_COLS = ['Task ID', 'Task Name', 'Bucket Name', 'Progress', 'Priority', 'Assigned To', 'Created By', 'Created Date',
                'Start Date', 'Due Date', 'Late', 'Completed Date', 'Completed By', 'Labels', 'Description']

def action_row(a, d):
    p = a.progress_at(d)
    return {'Task ID': a.id, 'Task Name': a.title, 'Bucket Name': a.bucket, 'Progress': p, 'Priority': a.priority,
            'Assigned To': NAME(a.owner), 'Created By': NAME(a.creator), 'Created Date': us(a.created),
            'Start Date': us(a.started) if a.started and a.started <= d else '', 'Due Date': us(a.due),
            'Late': 'true' if p != 'Completed' and a.due < d else 'false', 'Completed Date': us(a.completed) if p == 'Completed' else '',
            'Completed By': NAME(a.owner) if p == 'Completed' else '',
            'Labels': ';'.join(x for x in ['PM1', SECTION_NAME.get(a.asset['section'], '') if a.asset else ''] if x), 'Description': a.desc}

RCFA_COLS = ['RCFA ID', 'Event Date', 'Opened', 'Closed', 'Status', 'Title', 'Area', 'Asset Number', 'Asset', 'Downtime (h)',
             'Production Loss', 'Category', 'Root Cause', 'Contributing Factors', 'Lead', 'Action IDs (Planner)']

def write_csv(path, cols, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator='\r\n'); w.writeheader(); w.writerows(rows)

def bus_rows(data, d):
    rows = []
    for i in data['issues']:
        if not i.open_on(d): continue
        closing = i.end == d
        st = 'Closed' if closing else ('New' if i.start == d else (i.status or 'Open'))
        wo = i.wo.no if i.wo and i.wo.created <= d else ''
        rows.append(dict(area=SECTION_NAME.get(i.asset['section'], ''), equip=i.asset['name'], issue=i.issue, action=i.action_on(d),
                         owner=NAME(i.owner), status=st, days=(d - i.start).days + 1, wo=wo, key=i.key, story=i.story))
    order = {'New': 0, 'Open': 1, 'Waiting parts': 2, 'Closed': 3}
    return sorted(rows, key=lambda r: (order[r['status']], r['area'], r['equip']))

def write_bus(data, out_dir):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    os.makedirs(out_dir, exist_ok=True)
    head = PatternFill('solid', fgColor='D9D9D9'); thin = Side(style='thin', color='BFBFBF')
    cols = ['#', 'Area', 'Equipment / Position', 'Issue', 'Action / Next step', 'Owner', 'Status', 'Days Open', 'WO #']
    widths = [4, 16, 28, 52, 46, 20, 13, 10, 11]
    counts = {}
    d = YEAR_START
    while d <= TODAY:
        rows = bus_rows(data, d); counts[d] = len(rows)
        crew = CREWS[d.isoformat()]
        y0, y1 = dt.datetime.combine(d - DAY, dt.time(7)), dt.datetime.combine(d, dt.time(7))
        brk = [x for x in data['downtime'] if x['kind'] == 'break' and y0 <= x['start'] < y1]
        down = sum(min(x['start'] + dt.timedelta(hours=x['hours']), y1).timestamp() - max(x['start'], y0).timestamp()
                   for x in data['downtime'] if x['start'] < y1 and x['start'] + dt.timedelta(hours=x['hours']) > y0) / 3600
        o = outage_on(d - DAY) or outage_on(d)
        if o:
            a, b = max(dt.datetime.fromisoformat(o['start']), y0), min(dt.datetime.fromisoformat(o['end']), y1)
            down += max(0, (b - a).total_seconds() / 3600)
        wb = Workbook(); ws = wb.active; ws.title = 'BUS'
        ws['A1'] = 'PM1 BUS Daily Sheet'; ws['A1'].font = Font(bold=True, size=14)
        meta = [('Date', d.strftime('%a %m/%d/%Y')), ('Day crew', crew['day_crew']), ('Night crew', crew['night_crew']),
                ('Grades (last 24 h)', ', '.join(grades_on(d - DAY)) or 'Down'), ('Breaks (last 24 h)', len(brk)),
                ('Downtime (last 24 h, h)', round(down, 1)), ('Next outage', next_outage(d - DAY)['date'].strftime('%m/%d/%Y'))]
        for n, (k, v) in enumerate(meta):
            ws.cell(row=2 + n, column=1, value=k).font = Font(bold=True); ws.cell(row=2 + n, column=3, value=v)
        r0 = 10
        for c, (h, w) in enumerate(zip(cols, widths), 1):
            cell = ws.cell(row=r0, column=c, value=h); cell.font = Font(bold=True); cell.fill = head
            cell.border = Border(bottom=thin); ws.column_dimensions[cell.column_letter].width = w
        for n, r in enumerate(rows, 1):
            vals = [n, r['area'], r['equip'], r['issue'], r['action'], r['owner'], r['status'], r['days'], r['wo']]
            for c, v in enumerate(vals, 1):
                cell = ws.cell(row=r0 + n, column=c, value=v); cell.alignment = Alignment(wrap_text=c in (4, 5), vertical='top')
                cell.border = Border(bottom=thin)
        ws.freeze_panes = ws.cell(row=r0 + 1, column=1)
        wb.properties.creator = 'PM1 BUS'; wb.properties.created = wb.properties.modified = dt.datetime.combine(d, dt.time(7, 45))
        wb.save(os.path.join(out_dir, f'BUS_PM1_{d.isoformat()}.xlsx'))
        d += DAY
    return counts

def write_all(data, out):
    if os.path.exists(out): shutil.rmtree(out)
    mondays = [d for d in (YEAR_START + DAY * k for k in range((TODAY - YEAR_START).days + 1)) if d.weekday() == 0]
    # JDE: weekly delta (created or changed in the 7 days to Monday 06:00) + one full export
    for m in mondays:
        rows = [wo_row(w, m) for w in data['wos'] if w.created <= m and any(m - DAY * 7 < c <= m for c in w.changes())]
        write_csv(os.path.join(out, 'jde', f'WO_PM1_{m.isoformat()}.csv'), JDE_COLS, rows)
    write_csv(os.path.join(out, 'jde', f'WO_PM1_full_{TODAY.isoformat()}.csv'), JDE_COLS, [wo_row(w, TODAY) for w in data['wos'] if w.created <= TODAY])
    # Planner: weekly whole-plan export + one as of today
    for m in mondays + [TODAY]:
        write_csv(os.path.join(out, 'teams', f'Planner_PM1_{m.isoformat()}.csv'), PLANNER_COLS,
                  [action_row(a, m) for a in data['actions'] if a.created <= m])
    # RCFA log as of today
    akey = {a.key: a for a in data['actions'] if a.key}
    rows = []
    for r in data['rcfas']:
        a = BY_NAME[r['asset']]
        rows.append({'RCFA ID': r['id'], 'Event Date': us(D(r['event'])), 'Opened': us(D(r['opened'])), 'Closed': us(r['closed']),
                     'Status': 'Closed' if r['closed'] else 'Open - actions pending', 'Title': r['title'], 'Area': SECTION_NAME.get(a['section'], ''),
                     'Asset Number': a['asset_no'], 'Asset': a['name'], 'Downtime (h)': f"{float(r['downtime_h']):g}", 'Production Loss': r.get('loss', ''),
                     'Category': r['category'], 'Root Cause': r['root_cause'], 'Contributing Factors': r['contributing'], 'Lead': NAME(r['lead']),
                     'Action IDs (Planner)': '; '.join(r['action_ids'])})
    write_csv(os.path.join(out, 'rcfa', 'RCFA_log_PM1.csv'), RCFA_COLS, rows)
    # Ground truth for later phases and checks
    T = os.path.join(out, '_truth')
    write_csv(os.path.join(T, 'downtime.csv'), ['start', 'hours', 'kind', 'asset', 'asset_no', 'note', 'story'],
              [dict(start=x['start'].isoformat(timespec='minutes'), hours=f"{x['hours']:.2f}", kind=x['kind'], asset=x['asset'],
                    asset_no=BY_NAME[x['asset']]['asset_no'], note=x['note'], story=x['story']) for x in data['downtime']])
    write_csv(os.path.join(T, 'wo_keys.csv'), ['key', 'story', 'wo_no', 'desc'], [dict(key=w.key, story=w.story, wo_no=w.no, desc=w.desc) for w in data['wos'] if w.key or w.story])
    write_csv(os.path.join(T, 'action_keys.csv'), ['key', 'story', 'task_id', 'title'], [dict(key=a.key, story=a.story, task_id=a.id, title=a.title) for a in data['actions'] if a.key or a.story])
    write_csv(os.path.join(T, 'bus_issues.csv'), ['key', 'story', 'start', 'end', 'asset', 'issue', 'wo_no'],
              [dict(key=i.key, story=i.story, start=i.start, end=i.end or '', asset=i.asset['name'], issue=i.issue, wo_no=i.wo.no if i.wo else '') for i in data['issues']])
    return write_bus(data, os.path.join(out, 'bus'))


# ═════════════════════════ Checks ═════════════════════════
REAL_NAMES = ['AstenJohnson', 'Albany', 'Andritz', 'Valmet', 'Voith', 'Xerium', 'Stowe', 'Kadant', 'Spraying Systems', 'Buckman', 'Solenis', 'Nalco']

def check(data, out, counts):
    errs = []
    def need(ok, msg):
        if not ok: errs.append(msg)
    wos, acts, issues = data['wos'], data['actions'], data['issues']
    year_wos = [w for w in wos if w.created <= TODAY]
    need(1500 <= len(year_wos) <= 2600, f'{len(year_wos)} WOs, want 1,500–2,600')
    need(280 <= len(acts) <= 450, f'{len(acts)} actions, want 280–450')
    need(12 <= len(data['rcfas']) <= 20, f"{len(data['rcfas'])} RCFAs, want 12–20")
    need(len(counts) == 365, f'{len(counts)} BUS sheets, want 365')
    need(min(counts.values()) >= 5, f'a BUS sheet has {min(counts.values())} items (min 5)')
    need(max(counts.values()) <= 18, f'a BUS sheet has {max(counts.values())} items (max 18)')
    item_days = sum(counts.values()); need(2000 <= item_days <= 3200, f'{item_days} BUS item-days, want ~2,500')
    need(450 <= len(issues) <= 800, f'{len(issues)} distinct BUS issues, want ~600')
    nos = [w.no for w in wos]; need(len(nos) == len(set(nos)), 'duplicate WO numbers')
    for w in wos:
        need(w.approved >= w.created, f'WO {w.no} approved before created')
        if w.completed: need(w.completed >= w.created, f'WO {w.no} completed before created')
        if w.outage: need(w.outage in OUT, f'WO {w.no} unknown outage')
    for a in acts:
        need(a.due >= a.created, f'action "{a.title}" due before created')
        if a.completed: need(a.created <= a.completed <= TODAY, f'action "{a.title}" completed outside its window')
    overdue = [a for a in acts if a.progress_at(TODAY) != 'Completed' and a.due < TODAY]
    need(len(overdue) == 14, f'{len(overdue)} overdue actions on {TODAY}, storyline S08 says 14')
    annual = [w for w in wos if w.outage == 'OUT-2026-ANNUAL']
    done = [w for w in annual if w.completed]; carried = [w for w in annual if w.resched]; deferred = [w for w in annual if w.deferred_on]
    need(len(annual) == 120 and len(done) == 108 and len(carried) == 6 and len(deferred) == 6,
         f'annual scope {len(annual)} / done {len(done)} / carried {len(carried)} / deferred {len(deferred)}, want 120/108/6/6')
    nov = [w for w in wos if w.outage_at(TODAY) == 'OUT-2026-11-11' and w.parts == 'Not reserved']
    need(len(nov) == 2, f'{len(nov)} Nov 11 WOs without parts reserved, S08 says 2')
    # every storyline record made it into the output
    keys = {w.key for w in wos} | {a.key for a in acts} | {i.key for i in issues}
    for s in data['stories']:
        for kind in ('wo', 'action', 'bus'):
            for r in s['records'].get(kind, []):
                need(r['key'] in keys, f"{s['id']}: {r['key']} missing from output")
    for i in issues:
        if i.wo_key: need(i.wo is not None, f'BUS issue "{i.issue}" links a missing WO')
    # S05: 22 summer breaks; S01: can 27 WO scheduled Nov 11 with parts not reserved
    need(sum(1 for x in data['downtime'] if x['story'] == 'S05') == 22, 'S05 should have 22 breaks')
    s01 = next(w for w in wos if w.key == 'S01-WO'); need(s01.status_at(TODAY) == 30, f'S01-WO status {s01.status_at(TODAY)}, want 30')
    # fictional names only
    for root, _, files in os.walk(out):
        for f in files:
            if f.endswith('.csv'):
                txt = open(os.path.join(root, f)).read()
                for n in REAL_NAMES:
                    need(n not in txt, f'real company name "{n}" in {f}')
    # deterministic CSVs
    return errs

def run(out, checking):
    data = build()
    counts = write_all(data, out)
    errs = check(data, out, counts) if checking else []
    if checking:
        tmp2 = out + '-again'; build2 = build(); write_all(build2, tmp2)
        for root, _, files in os.walk(out):
            for f in files:
                if f.endswith('.csv'):
                    p1 = os.path.join(root, f); p2 = os.path.join(tmp2, os.path.relpath(p1, out))
                    if open(p1).read() != open(p2).read(): errs.append(f'{f} differs between runs (not seeded)')
        shutil.rmtree(tmp2)
    return data, counts, errs

if __name__ == '__main__':
    checking = '--check' in sys.argv
    out = tempfile.mkdtemp() + '/out' if checking else os.path.join(ROOT, 'demo-data', 'out')
    data, counts, errs = run(out, checking)
    summary = (f"{sum(1 for w in data['wos'] if w.created <= TODAY)} WOs · {len(data['actions'])} actions · {len(data['rcfas'])} RCFAs · "
               f"{len(counts)} BUS sheets ({sum(counts.values())} item-days, {len(data['issues'])} issues) · "
               f"{sum(1 for x in data['downtime'] if x['kind'] == 'break')} breaks")
    if checking:
        shutil.rmtree(os.path.dirname(out))
        for e in errs: print('FAIL', e)
        if errs: sys.exit(1)
        print('structured ok —', summary)
    else:
        print('wrote demo-data/out —', summary)
