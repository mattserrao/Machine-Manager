"""Sim Mill: configuration, calendar and the backbone (equipment register, Pi tags, outages, crews, people, vendors).

Everything here is deterministic from config/mill.yaml; nothing random.
"""
import csv, datetime as dt, json, os, re
import yaml

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # tools/sim-mill
ROOT = os.path.dirname(os.path.dirname(HERE))                                # repo root
CFG = yaml.safe_load(open(os.path.join(HERE, 'config', 'mill.yaml')))
PLANTS = yaml.safe_load(open(os.path.join(HERE, 'config', 'plants.yaml')))

# ═════════════════════════ The 6-week roll ═════════════════════════
# The year is written for Nov 2025 – Oct 2026 (the "base year"). SIM_SHIFT_CYCLES = k moves every date by k × 42 days,
# so the outage grid, weekdays and the planted faults keep their places while the demo stays current. Config dates
# are shifted here; dates written in the code use B() / BT() (a base-year date, moved) and md() for the text.
SHIFT_CYCLES = int(os.environ.get('SIM_SHIFT_CYCLES') or 0)
SHIFT = dt.timedelta(days=CFG['outages']['cadence_days'] * SHIFT_CYCLES)
_ISO = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?)?$')
def _shift(v):
    if isinstance(v, (dt.date, dt.datetime)): return v + SHIFT
    if isinstance(v, str) and _ISO.match(v):
        return (dt.datetime.fromisoformat(v) + SHIFT).isoformat(timespec='minutes') if 'T' in v else (dt.date.fromisoformat(v) + SHIFT).isoformat()
    if isinstance(v, dict): return {k: _shift(x) for k, x in v.items()}
    if isinstance(v, list): return [_shift(x) for x in v]
    return v
CFG, PLANTS = _shift(CFG), _shift(PLANTS)
CATALOG = json.load(open(os.path.join(HERE, 'reference', 'catalog.json')))
DATA = os.path.join(ROOT, 'demo-data', 'sim-mill')

D = lambda v: v if isinstance(v, dt.date) and not isinstance(v, dt.datetime) else (dt.date.fromisoformat(str(v)[:10]) if v else None)
DT = lambda v: v if isinstance(v, dt.datetime) else dt.datetime.fromisoformat(str(v))
B = lambda s: dt.date.fromisoformat(s) + SHIFT                  # a base-year date written in the code, moved with the roll
BT = lambda s: dt.datetime.fromisoformat(s) + SHIFT
_MON = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
_FULL = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')
_TXT = re.compile(r'(?P<iso>\b20\d\d-\d\d-\d\d\b)|(?P<us>\b\d\d/\d\d/20\d\d\b)|(?P<id>(?<=[A-Z]-)\d{6}\b)'
                  r'|(?P<mon>\b(?:' + '|'.join(f'{f}|{a}' if f != a else a for a, f in zip(_MON, _FULL)) + r')\b)(?P<day> \d{1,2}\b(?!:))?(?P<yr>, 20\d\d)?')
def tx(text):
    """A text written in base-year terms, with its dates moved by the roll: 2026-11-11, 11/11/2026, KV-VR-261111, 'Nov 11',
    'Nov 11, 2026', and month names on their own ('in May' moves by the 15th). The identity when there is no shift."""
    if not SHIFT or not text: return text
    def one(m):
        if m['iso']: return (dt.date.fromisoformat(m['iso']) + SHIFT).isoformat()
        if m['us']: return (dt.datetime.strptime(m['us'], '%m/%d/%Y').date() + SHIFT).strftime('%m/%d/%Y')
        if m['id']: return (dt.datetime.strptime(m['id'], '%y%m%d').date() + SHIFT).strftime('%y%m%d')
        name = m['mon']
        k = (_FULL.index(name) if name in _FULL and name not in _MON else _MON.index(name)) + 1
        long = (name in _FULL and name not in _MON) or (name == 'May' and not m['day'])   # "in May" -> "in June"
        yr = int(m['yr'][2:]) if m['yr'] else 2026
        d = dt.date(yr, k, int(m['day']) if m['day'] else 15) + SHIFT
        out = (_FULL if long else _MON)[d.month - 1]
        if m['day']: out += f' {d.day}'
        if m['yr']: out += f', {d.year}'
        return out
    return _TXT.sub(one, text)
md = lambda d, fmt='%b %-d': D(d).strftime(fmt) if not isinstance(d, dt.datetime) else d.strftime(fmt)   # 'Nov 11'
DAY, HOUR, MIN = dt.timedelta(days=1), dt.timedelta(hours=1), dt.timedelta(minutes=1)
Y = CFG['year']
T0 = dt.datetime.combine(D(Y['warmup_start']), dt.time(0))     # model start (Envoy warm-up)
Y0, TODAY, Y1 = D(Y['start']), D(Y['today']), D(Y['end'])
T_END = dt.datetime.combine(Y1, dt.time(0))
H = int((T_END - T0).total_seconds() // 3600)                   # hours modelled
MACHINE = CFG['machine']['name']
ORD = lambda n: f"{n}{'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th'}"
us = lambda d: d.strftime('%m/%d/%Y') if d else ''
hidx = lambda t: (t - T0).total_seconds() / 3600
ts = lambda h: T0 + HOUR * h


# ═════════════════════════ Calendar ═════════════════════════
def outages():
    """The 6-week grid (anchor Nov 11 2026) from the warm-up to the next outage after today. 20 h each."""
    o = CFG['outages']; anchor = D(o['anchor']); out = []
    k = -((anchor - D(Y['warmup_start'])).days // o['cadence_days'])
    while True:
        d = anchor + DAY * (k * o['cadence_days'])
        if d > anchor: break
        if d >= D(Y['warmup_start']):
            s = dt.datetime.combine(d, dt.time(o['start_hour'])); e = s + HOUR * o['hours']
            out.append(dict(id=f'OUT-{d.isoformat()}', type='normal', start=s, end=e, date=d,
                            note=f"{o['hours']} h normal outage"))
        k += 1
    for i, x in enumerate(out): x['idx'] = i
    return out

OUTAGES = outages()
OUT_BY_ID = {o['id']: o for o in OUTAGES}
IN_YEAR = [o for o in OUTAGES if Y0 <= o['date'] <= TODAY]
NEXT_OUTAGE = OUTAGES[-1]

def outage_on(d):
    return next((o for o in OUTAGES if o['date'] == d), None)

def next_outage(d):
    """The first outage starting on or after d."""
    return next((o for o in OUTAGES if o['date'] >= d), NEXT_OUTAGE)

def outage_index_at(t):
    """The index of the last outage that ended at or before t (-1 before the first)."""
    i = -1
    for o in OUTAGES:
        if o['end'] <= t: i = o['idx']
    return i

DUPONT = 'NNNNOOODDDONNNOOODDDDOOOOOOO'   # 28-day cycle per crew; crews offset by 7 days (same rotation as Demo Mill)

def crews(d):
    k = (d - B('2025-11-03')).days
    on = {c: DUPONT[(k + 7 * i) % 28] for i, c in enumerate('ABCD')}
    return next(c for c, s in on.items() if s == 'D'), next(c for c, s in on.items() if s == 'N')

def crew_at(t):
    day, night = crews(t.date() if t.hour >= 6 else t.date() - DAY)
    return day if 6 <= t.hour < 18 else night

GRADES = CFG['grades']
GRADE_IDS = list(GRADES)
GLABEL = {g: v['label'] for g, v in GRADES.items()}
def full_tph(g): return CFG['k_tph'] * GRADES[g]['sp'] * GRADES[g]['bw']


# ═════════════════════════ People and companies ═════════════════════════
PEOPLE = {p['id']: p for p in CFG['roster']}
NAME = lambda pid: PEOPLE[pid]['name'] if pid in PEOPLE else pid
LEAD_OF = {p['crew']: p['id'] for p in CFG['roster'] if p.get('crew')}
VENDORS = {v['name']: v for v in CFG['vendors']}


# ═════════════════════════ Equipment register ═════════════════════════
SECTIONS = [('sec-stockprep', 'Stock prep'), ('sec-refiners', 'Refiners'), ('sec-forming', 'Forming'), ('sec-press', 'Press section'),
            ('sec-dryer-1', '1st dryer section'), ('sec-dryer-2', '2nd dryer section'), ('sec-dryer-3', '3rd dryer section'),
            ('sec-dryer-4', '4th dryer section'), ('sec-reel', 'Reel'), ('sec-winder', 'Winder')]
SECTION_NAME = dict(SECTIONS)
NDRY = len(CFG['machine']['dryers']); CANS = CFG['machine']['cans_per_section']

def position_names():
    """My Machine position id -> name, as mm-machine.js names them for this machine setup."""
    P = {}
    for r in CFG['machine']['refiners']: P[f"ref-{r['id']}"] = f"{r['name']} refiner"
    P['form-bottom'] = 'Forming fabric'
    for n in (1, 2):
        P[f'p{n}-felt-top'] = f'{ORD(n)} press top felt'; P[f'p{n}-felt-bottom'] = f'{ORD(n)} press bottom felt'
    for n in (1, 2):
        P[f'p{n}-roll-top'] = f'{ORD(n)} press top roll'; P[f'p{n}-roll-bottom'] = f'{ORD(n)} press bottom roll'
    for s, d in enumerate(CFG['machine']['dryers'], 1):
        P[f'd{s}-felt'] = f'{ORD(s)} section unorun felt'
        for k in range(1, d.get('feltRolls', 0) + 1): P[f'd{s}-froll-{k}'] = f'{ORD(s)} section felt roll {k}'
    return P

POS_NAME = position_names()

def equipment():
    rows, n = [], [72000]
    def add(name, section, kind, pos='', parent=''):
        n[0] += 7; no = f'{n[0]:08d}'
        rows.append(dict(asset_no=no, name=name, section=section, kind=kind, position_id=pos, parent_asset=parent)); return no
    sec = {sid: add(f'{MACHINE} {name}', sid, 'section') for sid, name in SECTIONS}
    s = sec['sec-stockprep']
    pulper = add('Pulper', 'sec-stockprep', 'pulper', parent=s)
    add('Pulper rotor', 'sec-stockprep', 'motor', parent=pulper)
    for nm, k in (('HD cleaners', 'cleaner'), ('Coarse screen', 'screen'), ('Fine screens', 'screen'), ('LC cleaners', 'cleaner'),
                  ('LW cleaners', 'cleaner'), ('Thickener', 'thickener'), ('Stock chest', 'chest'), ('Machine chest', 'chest'),
                  ('Ragger', 'ragger'), ('Steam header', 'steam')):
        add(nm, 'sec-stockprep', k, parent=s)
    s = sec['sec-refiners']
    for r in CFG['machine']['refiners']:
        x = add(f"{r['name']} refiner", 'sec-refiners', 'refiner', f"ref-{r['id']}", s)
        add(f"{r['name']} refiner motor", 'sec-refiners', 'motor', parent=x)
    s = sec['sec-forming']
    for nm, k in (('Headbox', 'headbox'), ('Fan pump', 'pump'), ('Breast roll', 'roll'), ('Couch roll', 'roll'), ('Flat boxes', 'vacuum'),
                  ('Forming HP shower', 'shower'), ('Wire guide', 'guide'), ('Vacuum pump', 'pump')):
        add(nm, 'sec-forming', k, parent=s)
    add('Forming fabric', 'sec-forming', 'fabric', 'form-bottom', s)
    s = sec['sec-press']
    for n_ in (1, 2):
        for side in ('top', 'bottom'):
            f = add(f'{ORD(n_)} press {side} felt', 'sec-press', 'fabric', f'p{n_}-felt-{side}', s)
            add(f'{ORD(n_)} press {side} felt Uhle box', 'sec-press', 'vacuum', parent=f)
            add(f'{ORD(n_)} press {side} felt HP shower', 'sec-press', 'shower', parent=f)
        for side in ('top', 'bottom'):
            add(f'{ORD(n_)} press {side} roll', 'sec-press', 'roll', f'p{n_}-roll-{side}', s)
        add(f'{ORD(n_)} press drive', 'sec-press', 'drive', parent=s)
    can = 0
    for i in range(1, NDRY + 1):
        sid = f'sec-dryer-{i}'; s = sec[sid]
        add(f'{ORD(i)} section unorun felt', sid, 'fabric', f'd{i}-felt', s)
        for _ in range(CANS):
            can += 1; add(f'Dryer can {can}', sid, 'can', parent=s)
        for k in range(1, CFG['machine']['dryers'][i - 1].get('feltRolls', 0) + 1):
            add(f'{ORD(i)} section felt roll {k}', sid, 'roll', f'd{i}-froll-{k}', s)
        add(f'{ORD(i)} section rotary joint (DS)', sid, 'joint', parent=s)
        add(f'{ORD(i)} section PV fan', sid, 'fan', parent=s)
    add('Dryer drive lineup', 'sec-dryer-2', 'drive', parent=sec['sec-dryer-2'])
    add('Hood supply fan', 'sec-dryer-4', 'fan', parent=sec['sec-dryer-4'])
    add('Hood exhaust fan', 'sec-dryer-4', 'fan', parent=sec['sec-dryer-4'])
    s = sec['sec-reel']
    reel = add('Reel drum', 'sec-reel', 'roll', parent=s)
    add('Reel drum DS bearing', 'sec-reel', 'bearing', parent=reel)
    add('Reel drive', 'sec-reel', 'drive', parent=s)
    s = sec['sec-winder']
    for nm, k in (('Winder drums', 'roll'), ('Winder drive', 'drive'), ('Winder slitters', 'knife')):
        add(nm, 'sec-winder', k, parent=s)
    return rows

EQUIP = equipment()
BY_NAME = {e['name']: e for e in EQUIP}
BY_NO = {e['asset_no']: e for e in EQUIP}
BY_POS = {e['position_id']: e for e in EQUIP if e['position_id']}

def section_name(asset_name):
    return SECTION_NAME.get(BY_NAME[asset_name]['section'], '')


# ═════════════════════════ Pi tags ═════════════════════════
# tag, description, units, asset, decimals, by_grade (Envoy baseline per grade), sheet_only (blank when the sheet is off)
TAGS = [
    ('SPEED', 'Reel speed', 'fpm', 'Reel drum', 0, True, False),
    ('PROD', 'Production rate', 't/h', 'Reel drum', 2, True, False),
    ('BREAKS', f'Sheet break counter (since {md(Y0)})', 'count', 'Reel drum', 0, False, False),
    ('REEL_MOIST', 'Reel moisture', '%', 'Reel drum', 2, False, True),
    ('REEL_BW', 'Reel basis weight', 'lb/1000 ft2', 'Reel drum', 2, True, True),
    ('PULPER_AMPS', 'Pulper rotor current', 'A', 'Pulper rotor', 1, False, False),
    ('PULPER_CONS', 'Pulper consistency', '%', 'Pulper', 2, False, False),
    ('STOCK_CHEST_LVL', 'Stock chest level', '%', 'Stock chest', 1, False, False),
    ('REF_A_KW', 'REF 1 refiner motor load', 'kW', 'REF 1 refiner', 0, True, False),
    ('REF_B_KW', 'REF 2 refiner motor load', 'kW', 'REF 2 refiner', 0, True, False),
    ('REF_A_SE', 'REF 1 specific energy', 'kWh/t', 'REF 1 refiner', 1, True, True),
    ('REF_B_SE', 'REF 2 specific energy', 'kWh/t', 'REF 2 refiner', 1, True, True),
    ('FREENESS', 'Machine chest freeness', 'mL CSF', 'Machine chest', 0, False, True),
    ('HB_CONS', 'Headbox consistency', '%', 'Headbox', 3, False, True),
    ('HB_P', 'Headbox pressure', 'psi', 'Headbox', 2, True, False),
    ('FAN_PUMP_FLOW', 'Fan pump flow', 'gpm', 'Fan pump', 0, True, False),
    ('FLATBOX_VAC', 'Flat box vacuum', 'inHg', 'Flat boxes', 2, False, False),
    ('COUCH_VAC', 'Couch vacuum', 'inHg', 'Couch roll', 2, False, False),
    ('COUCH_SOLIDS', 'Couch solids', '%', 'Couch roll', 2, False, True),
    ('UHLE_P1T_VAC', '1st press top felt Uhle box vacuum', 'inHg', '1st press top felt Uhle box', 2, False, False),
    ('UHLE_P1B_VAC', '1st press bottom felt Uhle box vacuum', 'inHg', '1st press bottom felt Uhle box', 2, False, False),
    ('UHLE_P2T_VAC', '2nd press top felt Uhle box vacuum', 'inHg', '2nd press top felt Uhle box', 2, False, False),
    ('UHLE_P2B_VAC', '2nd press bottom felt Uhle box vacuum', 'inHg', '2nd press bottom felt Uhle box', 2, False, False),
    ('PRESS1_LOAD', '1st press nip load', 'pli', '1st press drive', 0, True, False),
    ('PRESS2_LOAD', '2nd press nip load', 'pli', '2nd press drive', 0, True, False),
    ('PRESS_SOLIDS', 'Press exit solids', '%', '2nd press bottom roll', 2, False, True),
    ('DRY1_STEAM_P', '1st section steam pressure', 'psig', '1st section rotary joint (DS)', 1, True, False),
    ('DRY2_STEAM_P', '2nd section steam pressure', 'psig', '2nd section rotary joint (DS)', 1, True, False),
    ('DRY3_STEAM_P', '3rd section steam pressure', 'psig', '3rd section rotary joint (DS)', 1, True, False),
    ('DRY4_STEAM_P', '4th section steam pressure', 'psig', '4th section rotary joint (DS)', 1, True, False),
    ('DRY1_DP', '1st section syphon differential', 'psi', '1st section rotary joint (DS)', 2, True, False),
    ('DRY2_DP', '2nd section syphon differential', 'psi', '2nd section rotary joint (DS)', 2, True, False),
    ('DRY3_DP', '3rd section syphon differential', 'psi', '3rd section rotary joint (DS)', 2, True, False),
    ('DRY4_DP', '4th section syphon differential', 'psi', '4th section rotary joint (DS)', 2, True, False),
    ('STEAM_FLOW', 'Dryer steam flow', 't/h', 'Steam header', 1, True, False),
    ('HOOD_EXH_TEMP', 'Hood exhaust temperature', 'degF', 'Hood exhaust fan', 1, False, False),
    ('PULPER_VIB', 'Pulper rotor bearing vibration', 'in/s', 'Pulper rotor', 3, False, False),
    ('REF_A_VIB', 'REF 1 refiner bearing vibration', 'in/s', 'REF 1 refiner motor', 3, False, False),
    ('REF_B_VIB', 'REF 2 refiner bearing vibration', 'in/s', 'REF 2 refiner motor', 3, False, False),
    ('FAN_PUMP_VIB', 'Fan pump bearing vibration', 'in/s', 'Fan pump', 3, False, False),
    ('COUCH_DS_VIB', 'Couch roll DS bearing vibration', 'in/s', 'Couch roll', 3, False, False),
    ('PRESS1_DS_VIB', '1st press drive bearing vibration', 'in/s', '1st press drive', 3, False, False),
    ('PRESS2_DS_VIB', '2nd press drive bearing vibration', 'in/s', '2nd press drive', 3, False, False),
    ('DRYER_DRIVE_VIB', 'Dryer drive lineup bearing vibration', 'in/s', 'Dryer drive lineup', 3, False, False),
    ('REEL_DRUM_DS_VIB', 'Reel drum DS bearing vibration', 'in/s', 'Reel drum DS bearing', 3, False, False),
    ('REEL_DRUM_DS_TEMP', 'Reel drum DS bearing temperature', 'degF', 'Reel drum DS bearing', 1, False, False),
    ('WINDER_DRUM_VIB', 'Winder drum bearing vibration', 'in/s', 'Winder drums', 3, False, False),
]
TAG = {f'{MACHINE}:{t[0]}': dict(tag=f'{MACHINE}:{t[0]}', short=t[0], description=t[1], units=t[2], asset=t[3], decimals=t[4],
                                  by_grade=t[5], sheet_only=t[6]) for t in TAGS}
for t in TAG.values():
    assert t['asset'] in BY_NAME, t
    e = BY_NAME[t['asset']]; t['asset_no'] = e['asset_no']; t['section'] = e['section']
    p = e['position_id']; q = e['parent_asset']
    while not p and q:                      # nearest position up the tree (a Uhle box belongs to its felt)
        p = BY_NO[q]['position_id']; q = BY_NO[q]['parent_asset']
    t['position_id'] = p
T = lambda short: f'{MACHINE}:{short}'


# ═════════════════════════ Backbone files ═════════════════════════
def write_csv(path, cols, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator='\r\n'); w.writeheader(); w.writerows(rows)

def write_backbone(folder):
    write_csv(os.path.join(folder, 'equipment.csv'), ['asset_no', 'name', 'section', 'kind', 'position_id', 'parent_asset'], EQUIP)
    write_csv(os.path.join(folder, 'pi_tags.csv'), ['tag', 'description', 'units', 'asset_no', 'section', 'position_id'],
              [{k: t[k] for k in ('tag', 'description', 'units', 'asset_no', 'section', 'position_id')} for t in TAG.values()])
    write_csv(os.path.join(folder, 'outages.csv'), ['id', 'type', 'start', 'end', 'note'],
              [dict(id=o['id'], type=o['type'], start=o['start'].isoformat(timespec='minutes'), end=o['end'].isoformat(timespec='minutes'),
                    note=o['note']) for o in OUTAGES if o['date'] >= Y0])
    write_csv(os.path.join(folder, 'roster.csv'), ['id', 'name', 'role', 'crew'], [dict(p, crew=p.get('crew', '')) for p in CFG['roster']])
    write_csv(os.path.join(folder, 'vendors.csv'), ['id', 'name', 'scope', 'rep'], CFG['vendors'])
    rows, d = [], Y0
    while d < Y1:
        a, b = crews(d); rows.append(dict(date=d.isoformat(), day_crew=a, night_crew=b)); d += DAY
    write_csv(os.path.join(folder, 'crew_schedule.csv'), ['date', 'day_crew', 'night_crew'], rows)
