"""MM LLM demo data, phase 3: mock Pi historian series and the Bonvoy exception reports derived from them.

    demo-data/out/pi/hourly/PM1_hourly_YYYY-MM.csv   hourly averages, every tag, Nov 2025 – Oct 2026 (wide: Timestamp + one column per tag)
    demo-data/out/pi/minute/<story>_<from>_<to>.csv  1-minute data around the storyline events
    demo-data/out/pi/points.json                     point metadata (what the mock PI Web API serves for /points)
    demo-data/out/bonvoy/Bonvoy_PM1_YYYY-MM-DD.csv     one exception report per day (header only when nothing tripped)

    python3 tools/demo-data/pi_bonvoy.py            # generate (run structured.py first: it writes _truth/downtime.csv)
    python3 tools/demo-data/pi_bonvoy.py --check    # generate to a temp folder, re-derive Bonvoy from the CSVs, check storyline anchors

How the series are made: the grade schedule, outages and _truth/downtime.csv (breaks and equipment stops) decide
when the machine turns and when the sheet is on. Each tag has a running value (by grade where it matters, plus
clothing and plate age), AR(1) noise at the tag's sigma, a few random process upsets, and the storyline effects
(S01 bearing, S02 felt fill and steam, S04 plate wear, S05 PV fan, S06 trial fabric). The model starts two months
before the demo year so Bonvoy has a baseline on day one.

Bonvoy rule (one place, used by the generator and the check): for each selected tag and calendar day, take the
hours with the sheet on (and not within 2 h of a restart). Baseline = mean and standard deviation of the same
tag's eligible hours from 67 to 7 days back (same grade only, for grade-dependent tags). An exception is >= 3
hours outside mean ± 3σ.
"""
import csv, json, os, sys, math, shutil, tempfile, datetime as dt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BACKBONE = os.path.join(ROOT, 'demo-data', 'backbone')
SEED = 3303
T0 = dt.datetime(2025, 9, 1)                    # model start (warm-up for the Bonvoy baseline)
Y0, Y1 = dt.date(2025, 11, 1), dt.date(2026, 10, 31)
T_END = dt.datetime(2026, 11, 1)
H = int((T_END - T0).total_seconds() // 3600)
HOUR = dt.timedelta(hours=1)

def read(name, base=BACKBONE):
    with open(os.path.join(base, name)) as f: return list(csv.DictReader(f))

def hidx(t): return (t - T0).total_seconds() / 3600
def ts(h): return T0 + HOUR * h

TAGS = read('pi_tags.csv'); TAG = {t['tag']: t for t in TAGS}
EQUIP = {e['asset_no']: e for e in read('equipment.csv')}
SECTION_NAME = {e['section']: e['name'][4:] for e in EQUIP.values() if e['kind'] == 'section'}
OUTAGES = read('outages.csv')
GRADES = read('grade_schedule.csv')
GIDX = {'26#': 0, '30#': 1, '33#': 2}
SPEED = np.array([2450, 2250, 2050.])
BW = np.array([26, 30, 33.])

# Clothing / plate changes (same schedule as structured.py, plus the changes before the demo year)
CHANGES = {
    'p1-felt-top': 'every', 'p-tandem-felt': 'every',
    'p2-felt-top': ['2025-09-17', '2025-12-10', '2026-03-04', '2026-04-15', '2026-07-08', '2026-10-05'],
    'form-bottom': ['2025-09-17', '2025-12-10', '2026-01-21', '2026-02-18', '2026-03-04', '2026-05-27', '2026-08-19'],
    'form-top': ['2025-09-17', '2025-12-10', '2026-03-04', '2026-05-27', '2026-08-19'],
    'ref-bp1': ['2025-09-17', '2025-12-10', '2026-03-04', '2026-05-27', '2026-08-19'],
    'ref-bp2': ['2025-09-17', '2025-12-10', '2026-03-04', '2026-05-27', '2026-08-19'],
    'ref-tp1': ['2025-10-29', '2026-01-21', '2026-04-15', '2026-07-08', '2026-10-05'],
    'ref-tp2': ['2025-10-29', '2026-01-21', '2026-04-15', '2026-07-08', '2026-10-05'],
}
LIFE_WEEKS = {'p1-felt-top': 6, 'p-tandem-felt': 6, 'p2-felt-top': 12, 'form-bottom': 12, 'form-top': 12,
              'ref-bp1': 12, 'ref-bp2': 12, 'ref-tp1': 12, 'ref-tp2': 12}

# Storyline tuning (chosen so Bonvoy's first flags land on the storyline dates; the check holds them there).
# Dates are the day a flag happens (the report's Period); the report itself arrives the next morning.
S01 = dict(start='2026-09-01', base=.07, at=[(21, .014), (41, .14)], g33=1.2, gother=.8, tail=.35)
S02 = dict(start='2026-03-10', end='2026-04-15 06:00', uhle_per_day=.115, moist_per_day=.06, slow='2026-03-16', cap='2026-03-24',
           steam_held=126.5, steam_cap=134.6, speed_loss=40)
S04 = dict(start='2026-09-28', per_run_day=.12, power=1.0)
S05 = dict(long_days=['2026-07-14', '2026-07-18'], depth=6.4)
S06 = dict(start='2025-12-10 20:00', end='2026-01-21 06:00', couch=.7, speed_loss=15)

BONVOY_TAGS = [t['tag'] for t in TAGS if t['tag'] not in ('PM1:SPEED', 'PM1:BREAKS')]
BY_GRADE = {'PM1:DRY1_STEAM_P', 'PM1:DRY2_STEAM_P', 'PM1:DRY3_STEAM_P', 'PM1:HB_TOP_P', 'PM1:HB_BASE_P', 'PM1:HB_BASE_CONS',
            'PM1:PRESS1_LOAD', 'PM1:PRESS2_LOAD', 'PM1:REEL_BW', 'PM1:REF_BP1_KW', 'PM1:REF_BP2_KW', 'PM1:REF_TP1_KW', 'PM1:REF_TP2_KW'}
SHEET_ONLY = {'PM1:REF_BP1_SE', 'PM1:REF_BP2_SE', 'PM1:REF_TP1_SE', 'PM1:REF_TP2_SE', 'PM1:PRESS_OUT_MOIST', 'PM1:REEL_MOIST', 'PM1:REEL_BW', 'PM1:HB_BASE_CONS'}
def DECIMALS(tag):
    u = TAG[tag]['units']
    if u == 'in/s' or tag.endswith('_CONS'): return 3
    if tag in ('PM1:SPEED', 'PM1:BREAKS') or u in ('kW', 'pli'): return 0
    if u in ('kWh/t', 'degF', 'A'): return 1
    return 2


# ═════════════════════════ Machine state ═════════════════════════
def machine_state(truth):
    """Per hour: grade index (-1 down), fraction of the hour turning (on), fraction with sheet on (sheet). Plus event lists."""
    grade = np.full(H, -1, dtype=int)
    rows = [r for r in GRADES if r['grade'] != 'DOWN']
    shift = dt.timedelta(days=61)        # warm-up (Sep–Oct 2025): the Nov–Dec pattern shifted back
    def paint(a, b, gi):
        i, j = max(0, math.floor(hidx(a))), min(H, math.ceil(hidx(b)))
        if j > i: grade[i:j] = gi
    for r in rows:
        a, b = dt.datetime.fromisoformat(r['start']), dt.datetime.fromisoformat(r['end'])
        if a - shift < dt.datetime.combine(Y0, dt.time(0)): paint(a - shift, min(b - shift, dt.datetime.combine(Y0, dt.time(0))), GIDX[r['grade']])
    for r in rows:
        paint(dt.datetime.fromisoformat(r['start']), dt.datetime.fromisoformat(r['end']), GIDX[r['grade']])
    for h in range(H):                   # outage hours: carry the grade that was running
        if grade[h] < 0: grade[h] = grade[h - 1] if h and grade[h - 1] >= 0 else 1
    stops = []   # (start, end, kind) — machine stopped
    for o in OUTAGES:
        stops.append((dt.datetime.fromisoformat(o['start']), dt.datetime.fromisoformat(o['end']), 'outage'))
    for d in ('2025-09-17', '2025-10-29'):
        stops.append((dt.datetime.fromisoformat(d + 'T06:00'), dt.datetime.fromisoformat(d + 'T20:00'), 'outage'))
    breaks = []
    for x in truth:
        a = dt.datetime.fromisoformat(x['start']); b = a + dt.timedelta(hours=float(x['hours']))
        (breaks if x['kind'] == 'break' else stops).append((a, b, x['kind']))
    on, sheet = np.ones(H), np.ones(H)
    def cut(arr, a, b):
        ha, hb = hidx(a), hidx(b)
        for h in range(max(0, math.floor(ha)), min(H, math.ceil(hb))):
            arr[h] -= max(0, min(hb, h + 1) - max(ha, h))
    for a, b, _ in stops: cut(on, a, b); cut(sheet, a, b)
    for a, b, _ in breaks: cut(sheet, a, b)
    on, sheet = np.clip(on, 0, 1), np.clip(np.minimum(sheet, on), 0, 1)
    return grade, on, sheet, stops, breaks

def change_dates(pos):
    c = CHANGES[pos]
    if c == 'every':
        ds = ['2025-09-17', '2025-10-29'] + [o['start'][:10] for o in OUTAGES]
    else:
        ds = c
    return sorted(dt.datetime.fromisoformat(d + 'T20:00') if len(d) == 10 else dt.datetime.fromisoformat(d) for d in ds)

def age_frac(pos):
    """Fraction of target life used, per hour (resets at each change)."""
    ch = [hidx(c) for c in change_dates(pos)]
    h = np.arange(H, dtype=float); last = np.full(H, -1e9)
    for c in ch: last = np.where(h >= c, c, last)
    return np.clip((h - last) / (LIFE_WEEKS[pos] * 7 * 24), 0, 1.6)

def ramp(a, b=None, per_day=1.0, run=None):
    """0 before a, then rising per day (calendar days, or running days when run is given), 0 again after b."""
    ia = hidx(dt.datetime.fromisoformat(a)); ib = hidx(dt.datetime.fromisoformat(b)) if b else H + 1
    h = np.arange(H, dtype=float)
    if run is None: days = (h - ia) / 24
    else: days = np.cumsum(np.where(h >= ia, run, 0)) / 24
    return np.where((h >= ia) & (h < ib), np.maximum(days, 0) * per_day, 0)

def window(a, b):
    h = np.arange(H, dtype=float)
    return (h >= hidx(dt.datetime.fromisoformat(a))) & (h < hidx(dt.datetime.fromisoformat(b)))


# ═════════════════════════ Series ═════════════════════════
def build(truth):
    rng = np.random.default_rng(SEED)
    grade, on, sheet, stops, breaks = machine_state(truth)
    g = grade; is33 = g == 2
    hod = np.arange(H) % 24
    R, DOWN = {}, {}
    mean = lambda tag: float(TAG[tag]['mean']) if TAG[tag]['mean'] != 'by grade' else 0.0

    # speed and its storyline losses
    spd = SPEED[g].copy()
    spd -= np.where(window(S02['slow'], S02['end'].replace(' ', 'T')) & is33, S02['speed_loss'], 0)
    spd -= np.where(window(S06['start'].replace(' ', 'T'), S06['end'].replace(' ', 'T')) & is33, S06['speed_loss'], 0)
    R['PM1:SPEED'] = spd; DOWN['PM1:SPEED'] = 0
    tons = spd * BW[g] / (2250 * 30)
    R['PM1:REEL_BW'] = BW[g]; R['PM1:REEL_MOIST'] = np.full(H, 7.5)

    for r, pos in [('BP1', 'ref-bp1'), ('BP2', 'ref-bp2'), ('TP1', 'ref-tp1'), ('TP2', 'ref-tp2')]:
        se = 95 + 2.0 * age_frac(pos)
        if r == 'BP2': se = se + S04['per_run_day'] * ramp(S04['start'] + 'T00:00', '2026-11-11T00:00', 1.0, run=on) ** S04['power']
        R[f'PM1:REF_{r}_SE'] = se
        R[f'PM1:REF_{r}_KW'] = 1150 * tons * se / 95; DOWN[f'PM1:REF_{r}_KW'] = 0
    R['PM1:HB_TOP_P'] = 9.8 * (spd / 2250) ** 2; R['PM1:HB_BASE_P'] = 11.2 * (spd / 2250) ** 2
    R['PM1:HB_BASE_CONS'] = np.array([.78, .82, .86])[g]
    R['PM1:FORM_TOP_FLATBOX_VAC'] = 8.5 + .6 * age_frac('form-top')
    R['PM1:FORM_BASE_COUCH_VAC'] = 18.0 + 1.5 * age_frac('form-bottom') + np.where(window(S06['start'].replace(' ', 'T'), S06['end'].replace(' ', 'T')), S06['couch'], 0)
    R['PM1:PRESS1_LOAD'] = np.array([1450, 1500, 1550.])[g]; R['PM1:PRESS2_LOAD'] = np.array([2150, 2200, 2250.])[g]
    s02 = ramp(S02['start'] + 'T00:00', S02['end'].replace(' ', 'T'), 1.0)        # days into the S02 fill-up
    R['PM1:UHLE_P1_VAC'] = 11.0 + 1.0 * age_frac('p1-felt-top')
    R['PM1:UHLE_P2_VAC'] = 12.0 + 1.0 * age_frac('p2-felt-top') + S02['uhle_per_day'] * s02
    R['PM1:UHLE_TAN_VAC'] = 12.5 + 1.0 * age_frac('p-tandem-felt')
    R['PM1:PRESS_OUT_MOIST'] = 58.0 + .8 * age_frac('p2-felt-top') + S02['moist_per_day'] * s02
    R['PM1:DRY1_STEAM_P'] = np.array([20, 25, 28.])[g]; R['PM1:DRY2_STEAM_P'] = np.array([65, 75, 85.])[g]
    d3 = np.array([100, 110, 120.])[g] + 4 * (R['PM1:PRESS_OUT_MOIST'] - 58)
    held = window(S02['slow'], S02['cap']) & is33; capped = window(S02['cap'], S02['end'].replace(' ', 'T')) & is33
    d3 = np.where(held, S02['steam_held'], np.where(capped, S02['steam_cap'], np.minimum(d3, 135)))
    R['PM1:DRY3_STEAM_P'] = d3
    for k in ('PM1:DRY1_STEAM_P', 'PM1:DRY2_STEAM_P', 'PM1:DRY3_STEAM_P'): DOWN[k] = 8
    pv = np.full(H, 62.0)
    summer = window('2026-06-01T00:00', '2026-09-01T00:00')
    s05_days = {dt.datetime.fromisoformat(x['start']).date() for x in truth if x['story'] == 'S05'}
    for day in sorted(s05_days):
        long = day.isoformat() in S05['long_days']
        a = hidx(dt.datetime.combine(day, dt.time(13 if not long else 12)))
        n = 4 if long else 2
        pv[int(a):int(a) + n] -= S05['depth']
    R['PM1:DRY3_PV_FAN_AMPS'] = pv; DOWN['PM1:DRY3_PV_FAN_AMPS'] = 0
    # vibration: bearings and rolls; S01 on can 27
    for t in [k for k in TAG if k.endswith('_VIB')]:
        R[t] = np.full(H, mean(t)); DOWN[t] = .01
    (n1, v1), (n2, v2) = S01['at']
    k = brentq(lambda k: (math.exp(n2 * k) - 1) / (math.exp(n1 * k) - 1) - v2 / v1, 1e-4, 1.0); a = v1 / (math.exp(n1 * k) - 1)
    rd = ramp(S01['start'] + 'T00:00', None, 1.0, run=on)
    base_rise = np.where(rd > 0, a * (np.exp(k * rd) - 1), 0)
    slope = a * k * math.exp(k * n2) * S01['tail']          # after the Oct route: keeps climbing, but roughly linearly
    base_rise = np.where(rd > n2, v2 + slope * (rd - n2), base_rise)
    gf = np.where(is33, S01['g33'], S01['gother']) - 1          # 33# runs higher; the grade swing is capped at ±0.03 in/s
    rise = base_rise + gf * np.minimum(base_rise, .03 / abs(S01['g33'] - 1))
    R['PM1:DRY2_C27_DS_VIB'] = S01['base'] + rise
    R['PM1:DRY2_C27_TS_VIB'] = R['PM1:DRY2_C27_TS_VIB'] + .1 * rise
    temp = np.full(H, 185.0)
    h = np.arange(H, dtype=float); r0 = hidx(dt.datetime(2026, 10, 11, 19)); r1 = hidx(dt.datetime(2026, 10, 14, 19))
    temp += np.where(h >= r0, np.minimum((h - r0) / (r1 - r0), 1) * 8 + np.maximum(h - r1, 0) / (24 * 17) * 4, 0)
    R['PM1:DRY2_C27_DS_TEMP'] = temp; DOWN['PM1:DRY2_C27_DS_TEMP'] = 90
    R['PM1:DRY_DRIVE_2_LOAD'] = 62 + 3 * (spd / 2250 - 1) * 10 / 3; DOWN['PM1:DRY_DRIVE_2_LOAD'] = 0
    for t in ('PM1:FORM_TOP_FLATBOX_VAC', 'PM1:FORM_BASE_COUCH_VAC', 'PM1:UHLE_P1_VAC', 'PM1:UHLE_P2_VAC', 'PM1:UHLE_TAN_VAC',
              'PM1:PRESS1_LOAD', 'PM1:PRESS2_LOAD', 'PM1:HB_TOP_P', 'PM1:HB_BASE_P'):
        DOWN[t] = 0

    # background process upsets (keep clear of the storyline tags around their story windows)
    quiet = {'PM1:DRY2_C27_DS_VIB': ('2026-08-01', '2026-11-01'), 'PM1:DRY2_C27_DS_TEMP': ('2026-09-15', '2026-11-01'),
             'PM1:REF_BP2_SE': ('2026-08-15', '2026-11-01'), 'PM1:UHLE_P2_VAC': ('2026-02-15', '2026-04-20'),
             'PM1:DRY3_STEAM_P': ('2026-02-15', '2026-04-20'), 'PM1:DRY3_PV_FAN_AMPS': ('2026-05-15', '2026-09-10'),
             'PM1:FORM_BASE_COUCH_VAC': ('2025-11-25', '2026-02-05')}
    upsets = []
    for t in BONVOY_TAGS:
        sig = float(TAG[t]['sigma'])
        for day in range(H // 24):
            if rng.random() < .11:
                st = day * 24 + int(rng.integers(0, 20)); n = int(rng.integers(3, 7))
                when = ts(st)
                q = quiet.get(t)
                if q and dt.datetime.fromisoformat(q[0]) <= when < dt.datetime.fromisoformat(q[1]): continue
                amp = sig * float(rng.uniform(5.5, 8)) * (1 if (t.endswith('_VIB') or t.endswith('_TEMP') or rng.random() < .6) else -1)
                R[t] = R[t].copy(); R[t][st:st + n] += amp; upsets.append((t, when, n))

    # noise (AR(1), unit variance) and the hourly values
    NOISE, OUT = {}, {}
    for t in TAG:
        sig = float(TAG[t]['sigma'])
        if t == 'PM1:BREAKS': continue
        z = rng.standard_normal(H); e = np.empty(H); e[0] = z[0]
        for i in range(1, H): e[i] = .6 * e[i - 1] + .8 * z[i]
        if t == 'PM1:DRY3_STEAM_P': e = np.where(capped, e * .15, np.where(held, e * .3, e))    # held off / pinned at the steam limit
        NOISE[t] = e * sig
        run = R[t] + NOISE[t]
        if t in SHEET_ONLY:
            v = np.where(sheet >= .25, run, np.nan)
        elif t in ('PM1:DRY1_STEAM_P', 'PM1:DRY2_STEAM_P', 'PM1:DRY3_STEAM_P'):
            v = sheet * run + (on - sheet) * run * .6 + (1 - on) * DOWN[t]
        else:
            v = on * run + (1 - on) * DOWN.get(t, 0)
        OUT[t] = np.round(v, DECIMALS(t))
    cnt = np.zeros(H)
    for a, _, _ in breaks:
        i = math.floor(hidx(a))
        if 0 <= i < H: cnt[i:] += 1
    OUT['PM1:BREAKS'] = cnt
    return dict(OUT=OUT, R=R, NOISE=NOISE, DOWN=DOWN, grade=grade, on=on, sheet=sheet, stops=stops, breaks=breaks, upsets=upsets)

def brentq(f, a, b):
    fa = f(a)
    for _ in range(200):
        m = (a + b) / 2; fm = f(m)
        if (fm > 0) == (fa > 0): a, fa = m, fm
        else: b = m
    return (a + b) / 2


# ═════════════════════════ Bonvoy ═════════════════════════
def eligible_mask(sheet, on):
    ok = sheet >= .95
    restart = np.zeros(H, dtype=bool)
    for h in range(1, H):
        if on[h - 1] < .99 or sheet[h - 1] < .5: restart[h:h + 2] = True
    return ok & ~restart

def bonvoy(values, grade, sheet, on, days):
    """values: tag -> hourly array (as written to the CSV). Returns {day: [row dict, ...]}."""
    elig = eligible_mask(sheet, on)
    out = {d: [] for d in days}
    for t in BONVOY_TAGS:
        x = values[t]; byg = t in BY_GRADE
        for d in days:
            i = int(hidx(dt.datetime.combine(d, dt.time(0)))); j = i + 24
            b0, b1 = i - 67 * 24, i - 7 * 24
            hrs = [h for h in range(i, j) if elig[h] and not np.isnan(x[h])]
            if not hrs: continue
            base = {}
            for gi in (set(int(grade[h]) for h in hrs) if byg else {None}):
                sel = elig[b0:b1] & ~np.isnan(x[b0:b1])
                if byg: sel &= grade[b0:b1] == gi
                xs = x[b0:b1][sel]
                if len(xs) >= 100: base[gi] = (float(xs.mean()), float(xs.std()))
            outside = []
            for h in hrs:
                bm = base.get(int(grade[h]) if byg else None)
                if not bm or bm[1] <= 0: continue
                m, s = bm
                if abs(x[h] - m) > 3 * s: outside.append((h, x[h], m, s))
            if len(outside) >= 3:
                worst = max(outside, key=lambda o: abs(o[1] - o[2]) / o[3])
                m, s = worst[2], worst[3]; dec = DECIMALS(t) + 1
                e = EQUIP[TAG[t]['asset_no']]
                out[d].append({'Report Date': (d + dt.timedelta(days=1)).strftime('%m/%d/%Y'), 'Period': d.strftime('%m/%d/%Y'),
                               'Tag': t, 'Description': TAG[t]['description'], 'Area': SECTION_NAME.get(e['section'], ''),
                               'Asset Number': e['asset_no'], 'Asset': e['name'], 'Units': TAG[t]['units'],
                               'Grade': ', '.join(sorted({['26#', '30#', '33#'][int(grade[o[0]])] for o in outside})) if byg else '',
                               'Baseline Mean': round(m, dec), 'Baseline Std Dev': round(s, dec + 1),
                               'Low Limit': round(m - 3 * s, dec), 'High Limit': round(m + 3 * s, dec),
                               'Min': round(min(o[1] for o in outside), dec), 'Max': round(max(o[1] for o in outside), dec),
                               'Hours Outside': len(outside), 'First Outside': ts(outside[0][0]).strftime('%H:%M'),
                               'Last Outside': (ts(outside[-1][0]) + HOUR).strftime('%H:%M'),
                               'Direction': 'High' if worst[1] > m else 'Low'})
    return out

BONVOY_COLS = ['Report Date', 'Period', 'Tag', 'Description', 'Area', 'Asset Number', 'Asset', 'Units', 'Grade', 'Baseline Mean',
              'Baseline Std Dev', 'Low Limit', 'High Limit', 'Min', 'Max', 'Hours Outside', 'First Outside', 'Last Outside', 'Direction']


# ═════════════════════════ Writers ═════════════════════════
def fmt(v, t):
    if isinstance(v, float) and math.isnan(v): return ''
    d = DECIMALS(t); return f'{v:.{d}f}'

def write_csv(path, cols, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator='\r\n'); w.writeheader(); w.writerows(rows)

MINUTE_WINDOWS = [   # story, from, to, tags
    ('S01', '2026-10-19T00:00', '2026-10-22T00:00', ['PM1:DRY2_C27_DS_VIB', 'PM1:DRY2_C27_TS_VIB', 'PM1:DRY2_C27_DS_TEMP', 'PM1:DRY2_STEAM_P', 'PM1:SPEED']),
    ('S02', '2026-03-23T00:00', '2026-03-26T00:00', ['PM1:UHLE_P2_VAC', 'PM1:PRESS_OUT_MOIST', 'PM1:DRY3_STEAM_P', 'PM1:SPEED']),
    ('S03', '2026-02-17T18:00', '2026-02-18T18:00', ['PM1:FORM_BASE_COUCH_VAC', 'PM1:SPEED', 'PM1:BREAKS']),
    ('S04', '2026-10-13T00:00', '2026-10-16T00:00', ['PM1:REF_BP2_SE', 'PM1:REF_BP2_KW', 'PM1:REF_BP1_SE', 'PM1:SPEED']),
    ('S05', '2026-07-12T00:00', '2026-07-21T00:00', ['PM1:DRY3_PV_FAN_AMPS', 'PM1:BREAKS', 'PM1:SPEED', 'PM1:REEL_MOIST']),
    ('S06', '2025-12-21T00:00', '2025-12-24T00:00', ['PM1:FORM_BASE_COUCH_VAC', 'PM1:SPEED']),
]

def minute_series(m, tag, a, b, rng):
    """1-minute values that average back to the hourly ones: hourly running value + hourly noise, plus minute noise, with exact stops."""
    n = int((b - a).total_seconds() // 60)
    tmin = np.array([hidx(a) + i / 60 for i in range(n)])
    if tag == 'PM1:BREAKS':
        return np.array([sum(1 for s, _, _ in m['breaks'] if s <= a + dt.timedelta(minutes=i)) for i in range(n)], dtype=float)
    hh = np.floor(tmin).astype(int)
    run = m['R'][tag][hh] + m['NOISE'][tag][hh] + rng.standard_normal(n) * float(TAG[tag]['sigma']) * .8
    when = [a + dt.timedelta(minutes=i) for i in range(n)]
    on = np.array([0.0 if any(s <= w < e for s, e, _ in m['stops']) else 1.0 for w in when])
    sheet = np.array([0.0 if on[i] == 0 or any(s <= w < e for s, e, _ in m['breaks']) else 1.0 for i, w in enumerate(when)])
    if tag in SHEET_ONLY: v = np.where(sheet > 0, run, np.nan)
    elif 'STEAM' in tag: v = sheet * run + (on - sheet) * run * .6 + (1 - on) * m['DOWN'][tag]
    else: v = on * run + (1 - on) * m['DOWN'].get(tag, 0)
    return np.round(v, DECIMALS(tag))

def write_all(m, out):
    if os.path.exists(out): shutil.rmtree(out)
    tags = [t['tag'] for t in TAGS]
    i0 = int(hidx(dt.datetime.combine(Y0, dt.time(0))))
    by_month = {}
    for h in range(i0, H):
        t = ts(h); by_month.setdefault(t.strftime('%Y-%m'), []).append(h)
    for mon, hs in by_month.items():
        rows = []
        for h in hs:
            r = {'Timestamp': ts(h).isoformat(timespec='minutes')}
            for t in tags: r[t] = fmt(float(m['OUT'][t][h]), t)
            rows.append(r)
        write_csv(os.path.join(out, 'pi', 'hourly', f'PM1_hourly_{mon}.csv'), ['Timestamp'] + tags, rows)
    rng = np.random.default_rng(SEED + 1)
    for story, a, b, wtags in MINUTE_WINDOWS:
        a, b = dt.datetime.fromisoformat(a), dt.datetime.fromisoformat(b)
        cols = {t: minute_series(m, t, a, b, rng) for t in wtags}
        n = len(next(iter(cols.values())))
        rows = [dict({'Timestamp': (a + dt.timedelta(minutes=i)).isoformat(timespec='minutes')}, **{t: fmt(float(cols[t][i]), t) for t in wtags}) for i in range(n)]
        write_csv(os.path.join(out, 'pi', 'minute', f'{story}_{a.date()}_{(b - dt.timedelta(minutes=1)).date()}.csv'), ['Timestamp'] + wtags, rows)
    points = []
    for t in TAGS:
        e = EQUIP[t['asset_no']]
        points.append({'Name': t['tag'], 'Descriptor': t['description'], 'EngineeringUnits': t['units'], 'PointClass': 'classic',
                       'PointType': 'Float32' if t['tag'] != 'PM1:BREAKS' else 'Int32', 'Step': t['tag'] == 'PM1:BREAKS',
                       'Area': SECTION_NAME.get(e['section'], ''), 'AssetNumber': e['asset_no'], 'Asset': e['name'], 'PositionId': e['position_id']})
    os.makedirs(os.path.join(out, 'pi'), exist_ok=True)
    json.dump({'server': 'MILLPI01', 'demo_now': '2026-10-31T23:00:00', 'points': points}, open(os.path.join(out, 'pi', 'points.json'), 'w'), indent=1)
    days = [Y0 + dt.timedelta(days=k) for k in range((Y1 - Y0).days + 1)]
    ev = bonvoy(m['OUT'], m['grade'], m['sheet'], m['on'], days)
    for d, rows in ev.items():
        write_csv(os.path.join(out, 'bonvoy', f'Bonvoy_PM1_{d.isoformat()}.csv'), BONVOY_COLS, rows)
    return ev


# ═════════════════════════ Checks ═════════════════════════
def read_hourly(out):
    vals, times = {}, []
    folder = os.path.join(out, 'pi', 'hourly')
    for fn in sorted(os.listdir(folder)):
        for r in csv.DictReader(open(os.path.join(folder, fn))):
            times.append(r.pop('Timestamp'))
            for k, v in r.items(): vals.setdefault(k, []).append(float(v) if v != '' else np.nan)
    return times, {k: np.array(v) for k, v in vals.items()}

def flags(ev, tag):
    return sorted(d for d, rows in ev.items() if any(r['Tag'] == tag for r in rows))

def check(m, ev, out, truth):
    errs = []
    def need(ok, msg):
        if not ok: errs.append(msg)
    days = sorted(ev)
    # 1) the CSVs re-read from disk produce exactly the same Bonvoy reports
    times, vals = read_hourly(out)
    need(len(times) == 365 * 24, f'{len(times)} hourly rows, want {365 * 24}')
    i0 = int(hidx(dt.datetime.combine(Y0, dt.time(0))))
    full = {t: np.concatenate([m['OUT'][t][:i0], vals[t]]) for t in vals}
    for t in vals:
        a, b = m['OUT'][t][i0:], vals[t]
        need(np.allclose(np.nan_to_num(a, nan=-1), np.nan_to_num(b, nan=-1), atol=10 ** -DECIMALS(t)), f'{t}: CSV differs from the model')
    ev2 = bonvoy(full, m['grade'], m['sheet'], m['on'], days)
    for d in days:
        disk = list(csv.DictReader(open(os.path.join(out, 'bonvoy', f'Bonvoy_PM1_{d.isoformat()}.csv'))))
        need([r['Tag'] for r in disk] == [r['Tag'] for r in ev2[d]], f'Bonvoy {d}: report not reproducible from the Pi CSVs')
    # 2) machine stopped for outages and equipment stops; break counter matches the truth table
    spd = vals['PM1:SPEED']
    for a, b, kind in m['stops']:
        if a.date() < Y0: continue
        ha, hb = math.ceil(hidx(a)) - i0, math.floor(hidx(b)) - i0
        if hb > ha: need(np.all(spd[ha:hb] == 0), f'speed not 0 during {kind} {a}')
    need(int(vals['PM1:BREAKS'][-1]) == sum(1 for x in truth if x['kind'] == 'break'), 'break counter does not match _truth/downtime.csv')
    need(np.all(spd[(m['on'][i0:] >= 1)] > 1900), 'speed low while running')
    # 3) Bonvoy volume
    per_day = [len(ev[d]) for d in days]
    need(2 <= float(np.median(per_day)) <= 15, f'median {np.median(per_day)} Bonvoy exceptions/day, want 3–15')
    # 4) storyline anchors
    D = dt.date.fromisoformat
    f = flags(ev, 'PM1:DRY2_C27_DS_VIB'); fs = [d for d in f if d >= D('2026-08-01')]
    need(fs and fs[0] == D('2026-09-22'), f'S01: first can 27 flag {fs[:1]}, want 2026-09-22')
    nxt = [d for d in fs if D('2026-09-23') <= d <= D('2026-10-04')]
    need(len(nxt) >= 8, f'S01: {len(nxt)} flag days in the 12 days after Sep 22, want most of them')
    need(all(d in fs for d in [D('2026-10-1' + str(k)) for k in range(3, 10)]), 'S01: should flag daily after the restart')
    daily = lambda tag, day: float(np.nanmean(vals[tag][(int(hidx(dt.datetime.combine(D(day), dt.time(0)))) - i0):][:24]))
    need(abs(daily('PM1:DRY2_C27_DS_VIB', '2026-09-14') - .07) <= .008, f"S01: Sep 14 can 27 {daily('PM1:DRY2_C27_DS_VIB', '2026-09-14'):.3f} in/s, route says 0.07")
    need(abs(daily('PM1:DRY2_C27_DS_VIB', '2026-10-19') - .24) <= .015, f"S01: Oct 19 can 27 {daily('PM1:DRY2_C27_DS_VIB', '2026-10-19'):.3f} in/s, route says 0.24")
    need(not [d for d in fs if D('2026-08-01') <= d < D('2026-09-22')], 'S01: flagged before Sep 22')
    u = [d for d in flags(ev, 'PM1:UHLE_P2_VAC') if D('2026-03-01') <= d <= D('2026-04-20')]
    st = [d for d in flags(ev, 'PM1:DRY3_STEAM_P') if D('2026-03-01') <= d <= D('2026-04-20')]
    need(u and u[0] == D('2026-03-24'), f'S02: first Uhle flag {u[:1]}, want 2026-03-24')
    need(st and st[0] == D('2026-03-25'), f'S02: first 3rd section steam flag {st[:1]}, want 2026-03-25 (first 33# run after the cap)')
    b = [d for d in flags(ev, 'PM1:REF_BP2_SE') if d >= D('2026-08-15')]
    need(b and b[0] == D('2026-10-13'), f'S04: first BP2 SE flag {b[:1]}, want the Oct 13 period (report Oct 14)')
    pv = [d for d in flags(ev, 'PM1:DRY3_PV_FAN_AMPS') if D('2026-07-12') <= d <= D('2026-07-20')]
    need(len(pv) == 2, f'S05: {len(pv)} PV fan flags Jul 12–20, want 2')
    wk = lambda tag, day: float(np.mean([daily(tag, (D(day) + dt.timedelta(days=k)).isoformat()) for k in range(7)]))
    need(wk('PM1:FORM_BASE_COUCH_VAC', '2025-12-18') - wk('PM1:FORM_BASE_COUCH_VAC', '2026-01-29') > .4,
         'S06: couch vac not higher on the trial fabric than on the next fabric at the same age (days 8–14)')
    # 5) minute windows average back to the hourly values
    for fn in os.listdir(os.path.join(out, 'pi', 'minute')):
        rows = list(csv.DictReader(open(os.path.join(out, 'pi', 'minute', fn))))
        for t in [k for k in rows[0] if k != 'Timestamp' and k != 'PM1:BREAKS']:
            for hr in range(0, len(rows) // 60, 7):
                chunk = [float(r[t]) for r in rows[hr * 60:(hr + 1) * 60] if r[t] != '']
                hv = vals[t][int(hidx(dt.datetime.fromisoformat(rows[hr * 60]['Timestamp']))) - i0]
                if len(chunk) == 60 and not np.isnan(hv):
                    need(abs(np.mean(chunk) - hv) <= 1.5 * float(TAG[t]['sigma']) + 10 ** -DECIMALS(t), f'{fn} {t}: minute mean {np.mean(chunk):.3f} vs hourly {hv}')
    return errs

def run(out):
    truth = read('downtime.csv', os.path.join(ROOT, 'demo-data', 'out', '_truth'))
    m = build(truth)
    ev = write_all(m, out)
    return m, ev, truth

if __name__ == '__main__':
    checking = '--check' in sys.argv
    if not os.path.exists(os.path.join(ROOT, 'demo-data', 'out', '_truth', 'downtime.csv')):
        sys.exit('Run tools/demo-data/structured.py first (it writes _truth/downtime.csv).')
    out = os.path.join(tempfile.mkdtemp(), 'out') if checking else os.path.join(ROOT, 'demo-data', 'out')
    if not checking:   # keep phase 2's files; replace only ours
        for sub in ('pi', 'bonvoy'):
            shutil.rmtree(os.path.join(out, sub), ignore_errors=True)
        tmp = os.path.join(tempfile.mkdtemp(), 'out'); m, ev, truth = run(tmp)
        for sub in ('pi', 'bonvoy'): shutil.move(os.path.join(tmp, sub), os.path.join(out, sub))
    else:
        m, ev, truth = run(out)
    n = sum(len(v) for v in ev.values())
    summary = f'{len(TAGS)} tags hourly · {len(MINUTE_WINDOWS)} minute windows · {len(ev)} Bonvoy reports, {n} exceptions (median {int(np.median([len(v) for v in ev.values()]))}/day)'
    if checking:
        errs = check(m, ev, out, truth)
        sys.path.insert(0, HERE); import mock_piwebapi
        errs += mock_piwebapi.selftest(os.path.join(out, 'pi'))
        shutil.rmtree(os.path.dirname(out))
        for e in errs: print('FAIL', e)
        if errs: sys.exit(1)
        print('pi/bonvoy ok —', summary)
    else:
        print('wrote demo-data/out/pi and bonvoy —', summary)
