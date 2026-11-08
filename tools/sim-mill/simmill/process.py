"""Sim Mill process model: hourly Pi values for every tag, 1-minute windows around the planted faults, and the daily
Envoy exception reports derived from them.

The running values are calibrated to the reference year (reference/grade_stats.json, the-paper-mill sim-headless):
steam by grade, refining energy, vacuums, solids, moisture, syphon differential. On top: clothing and plate age (from
the model's position runs), bearing faults (P-F curves), the planted faults, AR(1) noise at each tag's sigma, and the
stops, breaks and slowdowns (hour-weighted, like a historian's hourly average).
"""
import datetime as dt, math
import numpy as np
from .base import (T0, H, HOUR, MIN, DAY, Y0, Y1, TODAY, TAG, T, MACHINE, GRADES, GRADE_IDS, GLABEL, full_tph, hidx, ts, D, DT,
                   PLANTS, BY_NAME, SECTION_NAME, us)
from .model import grade_at, age_frac, piece_at, VIB_BASE, VIB_DANGER

GI = {g: i for i, g in enumerate(GRADE_IDS)}
# running values by grade (reference medians; the dryer sections split the game's 3rd-section steam over four)
BY_G = {
    'DRY1_STEAM_P': [38, 39, 41, 41], 'DRY2_STEAM_P': [72, 76, 84, 82], 'DRY3_STEAM_P': [101, 106, 115, 112], 'DRY4_STEAM_P': [119.7, 124.3, 134.6, 131.5],
    'DRY1_DP': [2.40, 2.20, 2.18, 2.18], 'DRY2_DP': [3.45, 2.95, 2.71, 2.52], 'DRY3_DP': [4.10, 3.80, 3.60, 3.45], 'DRY4_DP': [4.56, 4.06, 3.81, 3.63],
    'HB_P': [11.6, 9.0, 7.9, 7.1], 'PRESS1_LOAD': [520, 540, 560, 580], 'PRESS2_LOAD': [610, 640, 670, 700],
    'SE': [59.5, 58.5, 61.0, 62.5], 'STEAM_X': [1.42, 1.45, 1.47, 1.43],
}
SIGMA = {'SPEED': 6, 'PROD': .25, 'REEL_MOIST': .12, 'REEL_BW': .22, 'PULPER_AMPS': 4, 'PULPER_CONS': .05, 'STOCK_CHEST_LVL': 1.6,
         'REF_A_KW': 14, 'REF_B_KW': 14, 'REF_A_SE': .7, 'REF_B_SE': .7, 'FREENESS': 5, 'HB_CONS': .006, 'HB_P': .06, 'FAN_PUMP_FLOW': 70,
         'FLATBOX_VAC': .08, 'COUCH_VAC': .12, 'COUCH_SOLIDS': .1, 'UHLE_P1T_VAC': .12, 'UHLE_P1B_VAC': .12, 'UHLE_P2T_VAC': .12,
         'UHLE_P2B_VAC': .12, 'PRESS1_LOAD': 4, 'PRESS2_LOAD': 4, 'PRESS_SOLIDS': .12, 'DRY1_STEAM_P': .6, 'DRY2_STEAM_P': .8,
         'DRY3_STEAM_P': .9, 'DRY4_STEAM_P': 1.0, 'DRY1_DP': .05, 'DRY2_DP': .06, 'DRY3_DP': .06, 'DRY4_DP': .07, 'STEAM_FLOW': .5,
         'HOOD_EXH_TEMP': 1.2, 'REEL_DRUM_DS_TEMP': 1.0, 'BREAKS': 0}
for k in ('PULPER_VIB', 'REF_A_VIB', 'REF_B_VIB', 'FAN_PUMP_VIB', 'COUCH_DS_VIB', 'PRESS1_DS_VIB', 'PRESS2_DS_VIB', 'DRYER_DRIVE_VIB',
          'REEL_DRUM_DS_VIB', 'WINDER_DRUM_VIB'):
    SIGMA[k] = .004
STEAM_LIMIT = 140.0
SHEET_ONLY = {t for t, v in TAG.items() if v['sheet_only']}


def overlap(a, b, x, y):
    return max(0.0, (min(b, y) - max(a, x)).total_seconds())

def machine_state(m):
    """Per hour: on (machine turning), sheet (sheet on), slow (speed factor from slowdowns), stockprep (running),
    grade index, breaks so far (counter from Nov 1)."""
    on = np.ones(H); sheet = np.ones(H); slow = np.ones(H); stock = np.ones(H); grade = np.zeros(H, dtype=int); brk = np.zeros(H)
    for h in range(H):
        grade[h] = GI[grade_at(m['sched'], ts(h) + MIN * 30)]
    y0 = dt.datetime.combine(Y0, dt.time(0)); n = 0
    for e in m['events']:
        a, b = e['start'], e['end']
        h0, h1 = max(0, int(hidx(a))), min(H - 1, int(hidx(b - MIN)))
        for h in range(h0, h1 + 1):
            f = overlap(a, b, ts(h), ts(h + 1)) / 3600
            if e['kind'] in ('planned', 'unplanned'):
                on[h] -= f; sheet[h] -= f
                if e['cause'] == 'outage': stock[h] -= f
            elif e['kind'] == 'break': sheet[h] -= f
            elif e['kind'] == 'slowdown': slow[h] -= f * (1 - e.get('speed', .7))
    for e in m['events']:
        if e['kind'] == 'break' and e['start'] >= y0:
            brk[max(0, int(hidx(e['start']))):] += 1
    return dict(on=np.clip(on, 0, 1), sheet=np.clip(sheet, 0, 1), slow=np.clip(slow, 0.5, 1), stock=np.clip(stock, 0, 1), grade=grade, breaks=brk)


def vib_curve(m):
    """Bearing vibration (in/s) per critical-asset tag, hourly: baseline plus each fault's P-F curve until it's fixed."""
    out = {}
    for f in m['faults']:
        out.setdefault(f['tag'], np.zeros(H))
    P = PLANTS['F2']
    for f in m['faults']:
        x = out[f['tag']]
        end = f['fixed'] or (f['fail'] or dt.datetime.combine(Y1, dt.time(0)))
        for h in range(max(0, int(hidx(f['onset']))), min(H, int(hidx(end)) + 1)):
            days = (ts(h) - f['onset']).total_seconds() / 86400
            if f['story'] == 'F2':
                # fitted through the route readings: 0.06 at onset, 0.17 on Aug 12, 0.43 on Oct 31
                d1 = (D(P['route_found']) - D(P['start'])).days; d2 = (D('2026-10-31') - D(P['start'])).days
                p = math.log((P['at_today'] - VIB_BASE) / (0.17 - VIB_BASE)) / math.log(d2 / d1); a = (0.17 - VIB_BASE) / d1 ** p
                x[h] = max(x[h], a * max(days, 0) ** p)
            else:
                x[h] = max(x[h], (VIB_DANGER - VIB_BASE) * (days / f['pf_days']) ** 2)
    return out


def build(m, seed=3303):
    rng = np.random.default_rng(seed)
    st = machine_state(m); on, sheet, slow, stock, grade = st['on'], st['sheet'], st['slow'], st['stock'], st['grade']
    runs = m['runs']
    tt = [ts(h) + MIN * 30 for h in range(H)]
    G = lambda k: np.array([BY_G[k][g] for g in grade], dtype=float)
    age = lambda pos: np.array([age_frac(runs, pos, t) for t in tt])
    sp = np.array([GRADES[GRADE_IDS[g]]['sp'] for g in grade], dtype=float)
    bw = np.array([GRADES[GRADE_IDS[g]]['bw'] for g in grade], dtype=float)
    tph = np.array([full_tph(GRADE_IDS[g]) for g in grade], dtype=float)
    day = np.array([(t - dt.datetime.combine(Y0, dt.time(0))).total_seconds() / 86400 for t in tt])
    R = {}

    # clothing and plates
    a_fab = age('form-bottom'); a_p1t, a_p1b, a_p2t, a_p2b = age('p1-felt-top'), age('p1-felt-bottom'), age('p2-felt-top'), age('p2-felt-bottom')
    a_ra, a_rb = age('ref-refa'), age('ref-refb')
    felt = lambda a: 9.4 + 2.6 * np.clip(a, 0, 1.4) ** 1.6
    R['UHLE_P1T_VAC'], R['UHLE_P1B_VAC'], R['UHLE_P2T_VAC'], R['UHLE_P2B_VAC'] = felt(a_p1t), felt(a_p1b), felt(a_p2t), felt(a_p2b)
    # F1: the 2nd press top felt fills early
    F1 = PLANTS['F1']; f1a, f1b = DT(f"{F1['fill_from']}T00:00"), DT(F1['change'])
    f1 = np.array([max(0.0, (min(t, f1b) - f1a).total_seconds() / 86400) if f1a <= t < f1b else 0.0 for t in tt])
    R['UHLE_P2T_VAC'] = R['UHLE_P2T_VAC'] + f1 * F1['uhle_per_day']
    R['PRESS_SOLIDS'] = 44.3 - 0.8 * (a_p1t + a_p1b + a_p2t + a_p2b) / 4 - f1 * 0.09
    R['FLATBOX_VAC'] = 8.6 + 1.1 * a_fab
    R['COUCH_VAC'] = 18.2 + 1.8 * a_fab
    R['COUCH_SOLIDS'] = 19.3 - 0.6 * a_fab
    # F3: REF 2 plates wear fast after Oct 7
    F3 = PLANTS['F3']; f3a = DT(f"{F3['rise_from']}T00:00")
    f3 = np.array([max(0.0, (t - f3a).total_seconds() / 86400) for t in tt])
    se_a = G('SE') * (1 + 0.08 * np.clip(a_ra, 0, 1.3))
    se_b = G('SE') * (1 + 0.08 * np.clip(a_rb, 0, 1.3)) * (1 + F3['per_day'] * f3)
    # the Jul 8 – Sep 30 set wore early too (removed 85% worn): +0.15%/day after week 6
    prev = [r for r in runs['ref-refb'] if r['story'] == 'F3' and r['removed']]
    if prev:
        a0 = prev[0]['installed'] + DAY * 42; b0 = prev[0]['removed']
        se_b = se_b * np.array([1 + 0.0015 * max(0.0, (t - a0).total_seconds() / 86400) if a0 <= t < b0 else 1.0 for t in tt])
    R['REF_A_SE'], R['REF_B_SE'] = se_a, se_b
    flow = tph / 2
    R['REF_A_KW'], R['REF_B_KW'] = se_a * flow, se_b * flow
    R['FREENESS'] = 455 - 1.6 * (se_a + se_b - 2 * G('SE')) / 2
    # steam: section pressures by grade, more steam when the press leaves a wetter sheet; the 4th section has a limit
    wet = 44.3 - R['PRESS_SOLIDS']
    for s in (1, 2, 3):
        R[f'DRY{s}_STEAM_P'] = G(f'DRY{s}_STEAM_P') + wet * (1.5 * s)
    want4 = G('DRY4_STEAM_P') + wet * 6.5
    R['DRY4_STEAM_P'] = np.minimum(want4, STEAM_LIMIT - 0.6)
    short = np.clip(want4 - STEAM_LIMIT, 0, None)            # steam the 4th section couldn't give: the machine slows
    sp_run = sp * (1 - short * 0.0045)
    R['REEL_MOIST'] = 7.95 + short * 0.015 + 0.05 * np.sin(day / 58)
    for s in (1, 2, 3, 4):
        R[f'DRY{s}_DP'] = G(f'DRY{s}_DP')
    # F5: the 3rd section joint loses its differential for a few days before each leak
    for x in PLANTS['F5']['events']:
        a = DT(x['start'])
        drop = np.array([max(0.0, 1 - (a - t).total_seconds() / 86400 / 5) if a - DAY * 5 <= t < a else 0.0 for t in tt])
        R['DRY3_DP'] = R['DRY3_DP'] - 1.3 * drop
    R['STEAM_FLOW'] = tph * G('STEAM_X') * (1 + wet * 0.02)
    R['HOOD_EXH_TEMP'] = 158 + 3 * np.sin((day - 200) / 365 * 2 * math.pi) + wet * 0.8
    R['SPEED'] = sp_run
    # the two hours after a grade change: part of the product goes to broke while basis weight and moisture settle.
    # A short campaign (under 5 h: the 28 between 24 and 31) runs on the change all the way through.
    chg = np.zeros(H)
    for a, b, g in m['sched']:
        n = int(hidx(b)) - int(hidx(a)) + 1 if (b - a).total_seconds() < 5 * 3600 else 2
        for k in range(n):
            h = int(hidx(a)) + k
            if 0 <= h < H: chg[h] = 1
    R['PROD'] = tph * sp_run / sp * 0.985 * (1 - 0.18 * chg)
    R['REEL_BW'] = bw
    R['PULPER_AMPS'] = np.full(H, 410.0); R['PULPER_CONS'] = np.full(H, 5.0); R['STOCK_CHEST_LVL'] = np.full(H, 52.5)
    R['HB_CONS'] = np.full(H, 0.80); R['HB_P'] = G('HB_P'); R['FAN_PUMP_FLOW'] = 15800 * tph / 34.8
    R['PRESS1_LOAD'], R['PRESS2_LOAD'] = G('PRESS1_LOAD'), G('PRESS2_LOAD')
    vib = vib_curve(m)
    offs = {'PULPER_VIB': .01, 'REF_A_VIB': .005, 'REF_B_VIB': .006, 'FAN_PUMP_VIB': .0, 'COUCH_DS_VIB': .008, 'PRESS1_DS_VIB': .004,
            'PRESS2_DS_VIB': .003, 'DRYER_DRIVE_VIB': .007, 'REEL_DRUM_DS_VIB': .0, 'WINDER_DRUM_VIB': .012}
    for k, o in offs.items():
        R[k] = VIB_BASE + o + vib.get(k, np.zeros(H))
    R['REEL_DRUM_DS_TEMP'] = 132 + 95 * (R['REEL_DRUM_DS_VIB'] - VIB_BASE) + 2 * np.sin((day - 200) / 365 * 2 * math.pi)
    R['BREAKS'] = st['breaks']

    # noise (AR(1), each tag at its sigma) and the stops
    OUT = {}
    for tag, meta in TAG.items():
        k = meta['short']; x = R[k].astype(float).copy(); s = SIGMA.get(k, 0)
        if s:
            e = rng.standard_normal(H); n = np.zeros(H)
            for h in range(1, H): n[h] = .8 * n[h - 1] + .6 * e[h]
            x = x + n * s
        if k == 'BREAKS': v = x
        elif k == 'SPEED': v = x * (sheet + 0.25 * (on - sheet)) * slow
        elif k in ('PROD', 'STEAM_FLOW', 'FAN_PUMP_FLOW', 'REF_A_KW', 'REF_B_KW'):
            v = x * (sheet * slow + (0.35 if k != 'PROD' else 0) * (on - sheet))
        elif k in ('PULPER_AMPS', 'PULPER_CONS', 'STOCK_CHEST_LVL'): v = x * stock + (1 - stock) * {'PULPER_AMPS': 0, 'PULPER_CONS': 0, 'STOCK_CHEST_LVL': 18}[k]
        elif k.endswith('_STEAM_P'): v = x * on + (1 - on) * 12
        elif k.endswith('_VIB'): v = x * on + (1 - on) * 0.01
        elif k == 'REEL_DRUM_DS_TEMP': v = x * on + (1 - on) * 85
        elif k == 'HOOD_EXH_TEMP': v = x * on + (1 - on) * 95
        elif k in SHEET_ONLY or tag in SHEET_ONLY: v = np.where(sheet > 0.25, x, np.nan)
        else: v = x * on
        OUT[tag] = np.round(v, meta['decimals'])
    return dict(OUT=OUT, R=R, grade=grade, on=on, sheet=sheet, state=st)


# ═════════════════════════ Envoy (same rule as Demo Mill's pi_envoy.py) ═════════════════════════
ENVOY_TAGS = [t for t in TAG if TAG[t]['short'] not in ('SPEED', 'PROD', 'BREAKS')]

def eligible_mask(sheet, on):
    ok = sheet >= .95
    restart = np.zeros(H, dtype=bool)
    for h in range(1, H):
        if on[h - 1] < .99 or sheet[h - 1] < .5: restart[h:h + 2] = True
    return ok & ~restart

ENVOY_COLS = ['Report Date', 'Period', 'Tag', 'Description', 'Area', 'Asset Number', 'Asset', 'Units', 'Grade', 'Baseline Mean',
              'Baseline Std Dev', 'Low Limit', 'High Limit', 'Min', 'Max', 'Hours Outside', 'First Outside', 'Last Outside', 'Direction']

def envoy(values, grade, sheet, on, days):
    """For each tag and calendar day: hours with the sheet on (not within 2 h of a restart) against the mean +/- 3 sigma of
    the same tag 67 to 7 days back (same grade for grade-dependent tags). >= 3 hours outside is an exception."""
    elig = eligible_mask(sheet, on)
    out = {d: [] for d in days}
    for t in ENVOY_TAGS:
        x = values[t]; byg = TAG[t]['by_grade']; meta = TAG[t]
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
                mu, s = bm
                if abs(x[h] - mu) > 3 * s: outside.append((h, x[h], mu, s))
            if len(outside) >= 3:
                worst = max(outside, key=lambda o: abs(o[1] - o[2]) / o[3])
                mu, s = worst[2], worst[3]; dec = meta['decimals'] + 1
                e = BY_NAME[meta['asset']]
                out[d].append({'Report Date': us(d + DAY), 'Period': us(d), 'Tag': t, 'Description': meta['description'],
                               'Area': SECTION_NAME.get(e['section'], ''), 'Asset Number': e['asset_no'], 'Asset': e['name'], 'Units': meta['units'],
                               'Grade': ', '.join(sorted({GLABEL[GRADE_IDS[int(grade[o[0]])]] for o in outside})) if byg else '',
                               'Baseline Mean': round(mu, dec), 'Baseline Std Dev': round(s, dec + 1),
                               'Low Limit': round(mu - 3 * s, dec), 'High Limit': round(mu + 3 * s, dec),
                               'Min': round(min(o[1] for o in outside), dec), 'Max': round(max(o[1] for o in outside), dec),
                               'Hours Outside': len(outside), 'First Outside': ts(outside[0][0]).strftime('%H:%M'),
                               'Last Outside': (ts(outside[-1][0]) + HOUR).strftime('%H:%M'),
                               'Direction': 'High' if worst[1] > mu else 'Low'})
    return out


# 1-minute windows around the planted faults
MINUTE_WINDOWS = [
    ('F1', '2026-05-18T00:00', '2026-05-20T00:00', ['UHLE_P2T_VAC', 'PRESS_SOLIDS', 'DRY4_STEAM_P', 'SPEED', 'BREAKS']),
    ('F2', '2026-10-28T00:00', '2026-11-01T00:00', ['REEL_DRUM_DS_VIB', 'REEL_DRUM_DS_TEMP', 'SPEED']),
    ('F3', '2026-10-27T00:00', '2026-10-30T00:00', ['REF_B_SE', 'REF_B_KW', 'REF_A_SE', 'SPEED']),
    ('F4', '2026-02-09T06:00', '2026-02-10T06:00', ['COUCH_VAC', 'FLATBOX_VAC', 'SPEED', 'BREAKS']),
    ('F5', '2026-06-22T00:00', '2026-06-24T00:00', ['DRY3_DP', 'DRY3_STEAM_P', 'SPEED']),
]

def minute_series(p, m, tag, a, b, rng):
    n = int((b - a).total_seconds() // 60)
    meta = TAG[tag]
    if meta['short'] == 'BREAKS':
        y0 = dt.datetime.combine(Y0, dt.time(0))
        brks = sorted(e['start'] for e in m['events'] if e['kind'] == 'break' and e['start'] >= y0)
        return np.array([sum(1 for s in brks if s <= a + MIN * i) for i in range(n)], dtype=float)
    hh = np.array([int(hidx(a + MIN * i)) for i in range(n)])
    run = p['R'][meta['short']][hh] + rng.standard_normal(n) * SIGMA.get(meta['short'], 0) * .8
    stops = [(e['start'], e['end']) for e in m['events'] if e['kind'] in ('planned', 'unplanned') and e['end'] > a and e['start'] < b]
    brks = [(e['start'], e['end']) for e in m['events'] if e['kind'] == 'break' and e['end'] > a and e['start'] < b]
    when = [a + MIN * i for i in range(n)]
    on = np.array([0.0 if any(s <= w < e for s, e in stops) else 1.0 for w in when])
    sh = np.array([0.0 if on[i] == 0 or any(s <= w < e for s, e in brks) else 1.0 for i, w in enumerate(when)])
    k = meta['short']
    if k == 'SPEED': v = run * (sh + .25 * (on - sh))
    elif k.endswith('_STEAM_P'): v = run * on + (1 - on) * 12
    elif k in ('PRESS_SOLIDS', 'REF_B_SE', 'REF_A_SE'): v = np.where(sh > 0, run, np.nan)
    elif k == 'REF_B_KW': v = run * (sh + .35 * (on - sh))
    else: v = run * on + (1 - on) * (0.01 if k.endswith('VIB') else 85 if k.endswith('TEMP') else 0)
    return np.round(v, meta['decimals'])
