"""Sim Mill model: the year as it happened. Grade campaigns, clothing / plate / roll life, and every stop.

Ported from The Paper Mill's sim (reference/catalog.json, exported from the-paper-mill `sim-headless`):
  · grade wheel and campaign sizes (05b planner, GCOST.mix), full-speed t/h = k · fpm · bw (03 P.K)
  · upsets: the game's catalogue (04 EVENTS), each with its MTBF x rates.upset_mtbf_x and its duration range
  · sheet breaks: grade hazard factors (GCOST.brk), duration by where the sheet broke (07 step: reel / dryer / press)
  · critical-asset reliability (07i): bearing faults develop over a P-F interval and are found on the monthly
    vibration route or fail; motor faults are found on the electrical test or fail; drives fail without warning
New for a realistic year: per-position life (fabrics, felts, plates, press and felt rolls), outage change rules, the
five planted faults (config/plants.yaml), RCFA trigger rule. Everything is seeded: one seed, one year.
"""
import datetime as dt, math, random
from .base import B, tx, SHIFT
from . import engine as ENG
from . import degrade
from .base import (CFG, PLANTS, CATALOG, D, DT, DAY, HOUR, MIN, T0, T_END, Y0, TODAY, OUTAGES, NEXT_OUTAGE, GRADES,
                   full_tph, crew_at)

SEED = 20251101

# ═════════════════════════ Grade campaigns ═════════════════════════
def grade_schedule(rnd):
    """[(start, end, grade)] from T0 to T_END. With the engine: its grade changes. Without: walk the wheel, a campaign
    being a tonnage at ~92% of full rate."""
    if ENG.ON:
        ch = [(e['t'], e['grade']) for e in ENG.events() if e['type'] == 'grade']
        ch[0] = (T0, ch[0][1])                       # the engine starts at 6 AM; its first grade covers the night before
        out = []
        for (a, g), nxt in zip(ch, ch[1:] + [(T_END, None)]):
            a, b = max(a, T0), min(nxt[0], T_END)
            if b > a: out.append((a.replace(second=0, microsecond=0), b.replace(second=0, microsecond=0), g))
        return out
    wheel = CFG['wheel']; out, t, i = [], T0, 0
    while t < T_END:
        g = wheel[i % len(wheel)]; lo, hi = GRADES[g]['mix']
        hours = (lo + rnd.random() * (hi - lo)) / (full_tph(g) * 0.92)
        e = min(T_END, t + dt.timedelta(hours=hours))
        e = e.replace(second=0, microsecond=0)
        out.append((t, e, g)); t = e; i += 1
    return out

def grade_at(sched, t):
    for a, b, g in sched:
        if a <= t < b: return g
    return sched[-1][2]


# ═════════════════════════ Position life ═════════════════════════
def position_runs(rnd):
    """Every position's runs: [{position, installed, removed, reason, condition, vendor, style, serial, note, story}].
    Fabrics, felts and plates change at the outage once they're within 3 weeks of target life; rolls the same, by
    their own (long) life. The planted faults add the early and damaged removals."""
    P = CFG['positions']; runs = {}
    ser = [40000]
    def serial(vendor):
        ser[0] += rnd.randint(3, 40); return ''.join(w[0] for w in vendor.replace('.', '').split()).upper() + f'-{ser[0]}'
    def life_days(p): return p['life_w'] * 7
    spec = dict(P)
    for s, d in enumerate(CFG['machine']['dryers'], 1):
        for k in range(1, d.get('feltRolls', 0) + 1):
            # felt rolls: on since a random date in the last three years (seeded), recovered at the outage when due
            since = B('2023-06-01') + DAY * rnd.randint(0, 900)
            spec[f'd{s}-froll-{k}'] = dict(kind='roll', **CFG['felt_roll'], since=since)
    planted_breaks = {   # position -> [(when, reason, condition, note, story)] unplanned removals
        PLANTS['F1']['position']: [(DT(PLANTS['F1']['change']), 'performance', 'worn',
                                    'Filled at 3 weeks: Uhle vacuum up 4.6 inHg, press solids down 1.8 points, 4th section steam at its limit on 34 Super. '
                                    + tx('Changed early in a 7.5 h shut. 22% of the HP shower nozzles were plugged (Spraywell audit May 13).'), 'F1')],
        PLANTS['F4']['position']: [(DT(PLANTS['F4']['event']), 'damaged', 'damaged',
                                    '5-inch hole at the TS from a wad off the headbox approach. 9.5 h unplanned shut; spare off the floor.', 'F4')],
    }
    for pos, p in spec.items():
        life = life_days(p); r = []
        if 'phase' in p:
            o = OUTAGES[p['phase']]; installed = o['end'] - HOUR * 6          # changed during the outage
        else:
            installed = dt.datetime.combine(D(p['since']), dt.time(14))
        cur = dict(position=pos, installed=installed, vendor=p['vendor'], style=p['style'], serial=serial(p['vendor']), story='')
        events = sorted(planted_breaks.get(pos, []))
        # the outages after the current piece went on, plus the planted removals, in time order
        for o in OUTAGES:
            if o['end'] <= cur['installed']: continue
            while events and events[0][0] < o['start']:
                when, reason, cond, note, story = events.pop(0)
                r.append(dict(cur, removed=when + HOUR * 2, reason=reason, condition=cond, note=note, story=story))
                cur = dict(position=pos, installed=when + HOUR * 2, vendor=p['vendor'], style=p['style'], serial=serial(p['vendor']), story=story)
            age = (o['start'] - cur['installed']).days
            if o['date'] > TODAY: break
            if age >= life - 21:
                cond = 'worn' if age >= life - 3 else 'wear'
                note = {'refiner': 'Bars worn as expected; energy per ton steady to the end.', 'roll': 'Sent out to recover and regrind.',
                        'fabric': 'Normal wear at removal.'}[p['kind']]
                story = ''
                if pos == PLANTS['F3']['position'] and o['date'] == D(PLANTS['F3']['previous_removed_worn']):
                    cond, note, story = 'worn', tx('Bars 85% worn at 12 weeks (normal ~60%); leading edges rounded. Ridgeway report RR-PL-260930-B.'), 'F3'
                if p['kind'] == 'fabric' and pos.startswith('p') and rnd.random() < .25:
                    note = 'Some filling at the edges; cleaned with the HP shower at mid-life.'
                r.append(dict(cur, removed=o['start'] + HOUR * 2, reason='planned', condition=cond, note=note, story=story))
                cur = dict(position=pos, installed=o['end'] - HOUR * 6, vendor=p['vendor'], style=p['style'], serial=serial(p['vendor']),
                           story='F3' if pos == PLANTS['F3']['position'] and o['date'] == D(PLANTS['F3']['installed']) else '')
        cur.update(removed=None, reason='', condition='good', note='')
        r.append(cur)
        r = earlier_runs(pos, p, r) + r
        for x in r: x['target_days'] = life; x['kind'] = p['kind']
        runs[pos] = r
    return runs

HISTORY_NOTES = {
    'fabric': ['Normal wear at removal.', 'Ran to target; caliper and air perm within the vendor\'s end-of-life range.',
               'Some filling at the edges; cleaned with the HP shower at mid-life.'],
    'dryer': ['Normal wear at removal.', 'Seam held; slight edge fray at the DS.', 'Ran to target; permeability down about 25%.'],
    'forming': ['Normal wear; edge wear at the TS.', 'Ran to target; vac box loads crept up over the last two weeks.'],
    'refiner': ['Bars worn as expected; energy per ton steady to the end.', 'Normal wear; Ridgeway plate report on file.'],
    'roll': ['Sent out to recover and regrind.', 'Cover hardness up 2 P&J; recovered and reground.', 'Bearings replaced at the shop; cover reground.'],
}

def earlier_runs(pos, p, r):
    """Two or three runs before the first modelled piece, so every position has a history to look back on. Their own
    random stream (by position), so the rest of the year draws exactly what it did without them. Changes land on the
    6-week outage grid."""
    rh = random.Random(f'history:{pos}')
    life = p['life_w'] * 7
    n = 3 if life <= 90 else 2 if life <= 500 else 1
    kind = p['kind'] if p['kind'] != 'fabric' else ('forming' if pos == 'form-bottom' else 'dryer' if pos.startswith('d') else 'fabric')
    cad, anchor = CFG['outages']['cadence_days'], D(CFG['outages']['anchor'])
    first = r[0]; nxt_installed = first['installed']; num = int(first['serial'].rsplit('-', 1)[1]); prefix = first['serial'].rsplit('-', 1)[0]
    out = []
    for i in range(n):
        removed = nxt_installed - HOUR * 12 if nxt_installed.hour == 20 else nxt_installed - HOUR * 2
        want = removed - DAY * round(life * rh.uniform(.86, 1.04))
        k = round((want.date() - anchor).days / cad); g = anchor + DAY * (k * cad)
        installed = dt.datetime.combine(g, dt.time(20))
        if installed >= removed - DAY * 14: installed = dt.datetime.combine(g - DAY * cad, dt.time(20))
        num -= rh.randint(40, 400)
        early = kind in ('fabric', 'forming') and rh.random() < .12
        out.insert(0, dict(position=pos, installed=installed, removed=removed, vendor=p['vendor'], style=p['style'], serial=f'{prefix}-{num}',
                           story='', reason='performance' if early else 'planned', condition='worn' if not early else 'wear',
                           note='Pulled a cycle early: drainage falling off, couldn\'t hold speed on 34 Super.' if early else rh.choice(HISTORY_NOTES[kind])))
        nxt_installed = installed
    return out

def piece_at(runs, pos, t):
    for r in runs[pos]:
        if r['installed'] <= t and (r['removed'] is None or t < r['removed']): return r
    return runs[pos][0]

def age_frac(runs, pos, t):
    r = piece_at(runs, pos, t); return max(0.0, (t - r['installed']).total_seconds() / 86400 / r['target_days'])

def due_at_next_outage(runs, pos):
    """True if the current piece will be within 3 weeks of target life at the next outage."""
    r = runs[pos][-1]; return (NEXT_OUTAGE['start'] - r['installed']).days >= r['target_days'] - 21


# ═════════════════════════ Stops ═════════════════════════
# catalogue event -> (asset, effect). effect: 'stop' (machine down), 'slow' (stock prep short: machine at 70%),
# 'none' (no machine time: the winder or a chest)
EVENT_ASSET = {
    'refclash': ('REF 2 refiner', 'slow'), 'shaft': ('Dryer drive lineup', 'stop'), 'dryerfire': ('Hood exhaust fan', 'stop'),
    'fabric': ('Forming fabric', 'stop'), 'felt': ('1st press bottom felt', 'stop'), 'slime': ('Headbox', 'stop'),
    'ragger': ('Ragger', 'slow'), 'overflow': ('Stock chest', 'none'), 'winderdown': ('Winder drums', 'none'),
    'wrap': ('Dryer can 7', 'stop'), 'dye': ('Machine chest', 'slow'), 'hdblow': ('HD cleaners', 'slow'),
    'lwplug': ('LW cleaners', 'slow'), 'cscreen': ('Coarse screen', 'slow'), 'fscreen': ('Fine screens', 'slow'),
    'lcplug': ('LC cleaners', 'slow'), 'fogfan': ('Hood supply fan', 'stop'), 'thkblow': ('Thickener', 'slow'),
    'tiedrolls': ('Winder slitters', 'none'), 'syphon': ('2nd section rotary joint (DS)', 'stop'),
    'steamjoint': ('1st section rotary joint (DS)', 'stop'), 'boiler': ('Steam header', 'stop'), 'chestover': ('Machine chest', 'none'),
}
CAUSE_TEXT = {e['id']: e['name'] for e in CATALOG['events']}
CAUSE_TEXT.update(degrade.CAUSES)
CAUSE_TEXT.update(bearingfail='Bearing failure', motorfail='Motor failure', drivefail='Drive trip', bearingplan='Bearing change (found on the vibration route)',
                  outage='Planned outage', break_='Sheet break', feltchange='Unplanned felt change', fabrichole='Forming fabric hole',
                  jointleak='Rotary joint leak', rectfail='Rectifier fault (MCC DC bus down)', hbdoor='Headbox side door blew off',
                  motorplan='Motor change (found on test)')
EVENT_ASSET.setdefault('hbdoor', ('Headbox', 'stop'))
# Critical assets (07i ASSETS) and the Pi tag that watches each one's bearings
CRITICAL = [('pulp', 'Pulper rotor', 'PULPER_VIB'), ('refA', 'REF 1 refiner motor', 'REF_A_VIB'), ('refB', 'REF 2 refiner motor', 'REF_B_VIB'),
            ('fan', 'Fan pump', 'FAN_PUMP_VIB'), ('couch', 'Couch roll', 'COUCH_DS_VIB'), ('pr1', '1st press drive', 'PRESS1_DS_VIB'),
            ('pr2', '2nd press drive', 'PRESS2_DS_VIB'), ('dry', 'Dryer drive lineup', 'DRYER_DRIVE_VIB'),
            ('reel', 'Reel drum DS bearing', 'REEL_DRUM_DS_VIB'), ('wind', 'Winder drums', 'WINDER_DRUM_VIB')]
VIB_BASE, VIB_ALERT, VIB_DANGER = 0.06, 0.15, 0.40

def route_dates():
    """Keel monthly vibration route: the second Wednesday of each month of the base year, moved with the roll (so the
    planted Aug 12 finding stays on a route day)."""
    out, d, end = [], D('2025-09-01'), TODAY - SHIFT
    while d <= end:
        first = d.replace(day=1); wed = first + DAY * ((2 - first.weekday()) % 7) + DAY * 7
        if wed + SHIFT not in out and wed <= end: out.append(wed + SHIFT)
        d = (first + DAY * 32).replace(day=1)
    return out
ROUTES = route_dates()

def in_outage(t):
    return next((o for o in OUTAGES if o['start'] <= t < o['end']), None)

def engine_stops(ev, rnd, busy):
    """The engine's sheet breaks, upsets and reliability failures as Sim Mill stops (appended to ev). Returns the bearing
    faults behind the engine's bearing failures, for the vibration series: each rises over a P-F interval to the failure
    the engine had (missed on the route, so 'not caught')."""
    AID = {aid: (asset, tag) for aid, asset, tag in CRITICAL}
    planted = [e for e in ev if e.get('story')]
    clash = lambda a, b: any(e['start'] < b and a < e['end'] for e in planted)
    faults = []
    for e in ENG.events():
        if e['type'] not in ('break', 'upset', 'failure', 'planned') or e['start'] < T0 or e['start'] >= T_END: continue
        a, b = e['start'].replace(second=0, microsecond=0), e['end'].replace(second=0, microsecond=0)
        if b <= a or in_outage(a) or clash(a, b): continue
        k = int(a.timestamp()) // 60                         # a deterministic pick where the engine doesn't say
        if e['type'] == 'break':
            where = e.get('where') or 'dryer'
            sec = {'reel': 'Reel drum', 'press': '2nd press top felt'}.get(where) or ['Dryer can 3', 'Dryer can 6', 'Dryer can 11', 'Dryer can 16'][k % 4]
            ev.append(dict(start=a, end=b, kind='break', cause='break_', asset=sec, note=f'Sheet break at the {where}', story='', where=where))
        elif e['type'] == 'upset':
            if e['id'] not in EVENT_ASSET: continue
            asset, eff = EVENT_ASSET[e['id']]
            if eff == 'none': continue
            if e['id'] == 'felt': asset = ['1st press top felt', '1st press bottom felt', '2nd press bottom felt'][k % 3]
            if e['id'] in ('syphon', 'steamjoint'): asset = ['1st section rotary joint (DS)', '2nd section rotary joint (DS)', '4th section rotary joint (DS)'][k % 3]
            if e['id'] == 'wrap': asset = f'Dryer can {k % 20 + 1}'
            if e['id'] == 'refclash': asset = ['REF 1 refiner', 'REF 2 refiner'][k % 2]
            head = next((c['head'] for c in CATALOG['events'] if c['id'] == e['id']), CAUSE_TEXT.get(e['id'], e['id']))
            ev.append(dict(start=a, end=b, kind='unplanned' if eff == 'stop' else 'slowdown', cause=e['id'], asset=asset, note=head,
                           story='', speed=0.7 if eff == 'slow' else 0.0))
        elif e['type'] == 'failure':
            if e['kind'] == 'rect':
                if e.get('line') == 'WD': continue           # the winder: no machine time
                asset = 'Dryer drive lineup' if e.get('line') == 'PM' else 'Pulper rotor'
                mcc = 'MCC-2' if e.get('line') == 'PM' else 'MCC-1'
                ev.append(dict(start=a, end=b, kind='unplanned', cause='rectfail', asset=asset, story='',
                               note=f'{mcc} DC bus down: rectifier fault, {asset.lower()} and everything on the bus stopped.'))
                continue
            if e.get('asset') not in AID: continue
            asset, tag = AID[e['asset']]
            if e['kind'] == 'vib':
                pf = 18 + rnd.random() * 27
                faults.append(dict(asset=asset, tag=tag, onset=a - DAY * pf, pf_days=pf, story='', found=None, fail=a, fixed=b, fix_outage=None))
                ev.append(dict(start=a, end=b, kind='unplanned', cause='bearingfail', asset=asset, story='',
                               note=f"{asset} bearing failed (not caught on the route)."))
            else:
                cause = 'motorfail' if e['kind'] == 'adx' else 'drivefail'
                ev.append(dict(start=a, end=b, kind='unplanned', cause=cause, asset=asset.replace(' DS bearing', ''), story='',
                               note=f"{asset}: {CAUSE_TEXT[cause].lower()}."))
        elif e['type'] == 'planned' and e.get('asset') in AID:
            asset, _ = AID[e['asset']]
            ev.append(dict(start=a, end=b, kind='planned', cause='bearingplan', asset=asset, story='', note=f'{asset}: planned repair (found by reliability).'))
    return faults

def stops(rnd, sched, runs):
    """Every stop and slowdown of the year (and the warm-up): dicts with start, end, kind, cause, asset, note, story.
    kind: planned (outages, planned repairs) | unplanned | break | slowdown. Also returns the bearing faults (for the
    vibration series and the vibration route) and the motor faults found on test."""
    ev = []
    for o in OUTAGES:
        if o['start'] < T_END:
            ev.append(dict(start=o['start'], end=o['end'], kind='planned', cause='outage', asset='', note=o['note'], story='', outage=o['id']))
    pl = PLANTS
    # F1 felt change, F4 fabric hole, F5 joint leaks
    a = DT(pl['F1']['change'])
    ev.append(dict(start=a, end=a + HOUR * pl['F1']['change_hours'], kind='unplanned', cause='feltchange', asset='2nd press top felt',
                   note='2nd press top felt filled at 3 weeks: changed early (Uhle vacuum up 4.6 inHg, 4th section steam at its limit).', story='F1'))
    a = DT(pl['F4']['event'])
    ev.append(dict(start=a, end=a + HOUR * pl['F4']['hours'], kind='unplanned', cause='fabrichole', asset='Forming fabric',
                   note='5-inch hole at the TS from a wad off the headbox approach; fabric changed (spare off the floor).', story='F4'))
    for x in pl['F5']['events']:
        a = DT(x['start'])
        ev.append(dict(start=a, end=a + HOUR * x['hours'], kind='unplanned', cause='jointleak', asset=pl['F5']['asset'],
                       note='Steam blowing at the 3rd section DS rotary joint; seal kit changed.', story='F5'))
    busy = lambda a, b: any(e['start'] < b + HOUR * 6 and a < e['end'] + HOUR * 6 for e in ev if e['kind'] in ('planned', 'unplanned'))

    # emergent upsets: the game's catalogue at a year's rates (Poisson per running hour); with the engine, its own upsets
    X = CFG['rates']['upset_mtbf_x']
    t = T0
    for e in ([] if ENG.ON else CATALOG['events']):
        rate = 1 / (e['mtbf_h'] * X); t = T0
        asset, eff = EVENT_ASSET[e['id']]
        while True:
            t = t + dt.timedelta(hours=rnd.expovariate(rate))
            if t >= T_END: break
            lo, hi = e['dur']; minutes = lo + rnd.random() * (hi - lo)
            b = t + MIN * minutes
            if in_outage(t) or busy(t, b): continue
            if e['id'] == 'felt': asset = rnd.choice(['1st press top felt', '1st press bottom felt', '2nd press bottom felt'])
            if e['id'] in ('syphon', 'steamjoint'): asset = rnd.choice(['1st section rotary joint (DS)', '2nd section rotary joint (DS)', '4th section rotary joint (DS)'])
            if e['id'] == 'wrap': asset = f'Dryer can {rnd.randint(1, 20)}'
            if e['id'] == 'refclash': asset = rnd.choice(['REF 1 refiner', 'REF 2 refiner'])
            if eff == 'none': continue
            ev.append(dict(start=t.replace(second=0, microsecond=0), end=b.replace(second=0, microsecond=0),
                           kind='unplanned' if eff == 'stop' else 'slowdown', cause=e['id'], asset=asset, note=e['head'], story='',
                           speed=0.7 if eff == 'slow' else 0.0))

    # critical-asset reliability
    faults = []
    rate_b = 0.7 / (365 * 24)
    for aid, asset, tag in CRITICAL:
        if aid == 'reel':
            f = dict(asset=asset, tag=tag, onset=dt.datetime.combine(D(pl['F2']['start']), dt.time(10)), pf_days=None, story='F2'); faults.append(f); continue
        t = T0 - DAY * 60
        while True:
            t = t + dt.timedelta(hours=rnd.expovariate(rate_b))
            if t >= T_END: break
            faults.append(dict(asset=asset, tag=tag, onset=t, pf_days=18 + rnd.random() * 27, story=''))
    for f in faults:
        if f['story'] == 'F2':
            f.update(found=DT(pl['F2']['route_found'] + 'T10:00') if isinstance(pl['F2']['route_found'], str) else dt.datetime.combine(D(pl['F2']['route_found']), dt.time(10)),
                     fail=None, fixed=None, fix_outage=NEXT_OUTAGE['id'], missed_outage=f"OUT-{D(pl['F2']['outage_missed']).isoformat()}")
            continue
        fail = f['onset'] + DAY * f['pf_days']
        alert_t = f['onset'] + DAY * f['pf_days'] * math.sqrt((VIB_ALERT - VIB_BASE) / (VIB_DANGER - VIB_BASE))
        route = next((dt.datetime.combine(r, dt.time(10)) for r in ROUTES if alert_t <= dt.datetime.combine(r, dt.time(10)) < fail), None)
        f['found'] = route; f['fail'] = None; f['fixed'] = None; f['fix_outage'] = None
        if route:
            o = next((o for o in OUTAGES if o['start'] > route), None)
            if o and o['start'] < fail - DAY * 2 and o['start'] < T_END:
                f['fixed'] = o['start'] + HOUR * 4; f['fix_outage'] = o['id']
            else:   # can't wait for the outage: a planned 3 h stop two days after the route
                a = (route + DAY * 2).replace(hour=8, minute=0)
                while busy(a, a + HOUR * 3): a += HOUR * 6
                if a < T_END:
                    ev.append(dict(start=a, end=a + HOUR * 3, kind='planned', cause='bearingplan', asset=f['asset'],
                                   note=f"{f['asset']} bearing changed: found on the {route:%b %d} vibration route.", story=''))
                f['fixed'] = a + HOUR * 3
        else:
            if ENG.ON: f['drop'] = True; continue          # missed on the route: the engine's failures stand in for these
            if fail >= T_END: continue
            if in_outage(fail): f['fixed'] = fail; continue
            h = 3 + rnd.random() * 3.5
            while busy(fail, fail + HOUR * h): fail += HOUR * 3
            if fail >= T_END: continue
            ev.append(dict(start=fail.replace(second=0, microsecond=0), end=(fail + HOUR * h).replace(second=0, microsecond=0), kind='unplanned',
                           cause='bearingfail', asset=f['asset'], note=f"{f['asset']} bearing failed (not caught on the route).", story=''))
            f['fail'] = fail; f['fixed'] = fail + HOUR * h
    # motors (found on the monthly electrical test half the time) and drives (no warning)
    faults = [f for f in faults if not f.get('drop')]
    if ENG.ON: faults += engine_stops(ev, rnd, busy)
    for aid, asset, tag in ([] if ENG.ON else CRITICAL):
        if aid == 'reel': continue
        for kind, rate, hrs in (('motorfail', 0.13, (4, 7)), ('drivefail', 0.12, (1, 2.2))):
            t = T0
            while True:
                t = t + dt.timedelta(hours=rnd.expovariate(rate / (365 * 24)))
                if t >= T_END: break
                h = hrs[0] + rnd.random() * (hrs[1] - hrs[0]); b = t + HOUR * h
                if in_outage(t) or busy(t, b): continue
                if kind == 'motorfail' and rnd.random() < .5: continue      # found on the test, changed at an outage
                ev.append(dict(start=t.replace(second=0, microsecond=0), end=b.replace(second=0, microsecond=0), kind='unplanned', cause=kind,
                               asset=asset.replace(' DS bearing', ''), note=f"{asset}: {CAUSE_TEXT[kind].lower()}.", story=''))

    # sheet breaks: hazard per running hour by grade, a summer bump, clothing age (2nd press felts, forming fabric)
    bpd = CFG['rates']['breaks_per_day']
    t = dt.datetime.combine(B('2026-05-01'), dt.time(0)) if ENG.ON else T0
    t_end = DT(PLANTS['F1']['change']) if ENG.ON else T_END
    while t < t_end:
        t += dt.timedelta(minutes=rnd.randint(20, 40))
        if in_outage(t) or any(e['start'] <= t < e['end'] for e in ev if e['kind'] in ('planned', 'unplanned', 'break')): continue
        g = grade_at(sched, t)
        haz = bpd / 24 * GRADES[g]['brk'] / 1.15 * (1.25 if (t - SHIFT).month in (6, 7, 8) else 1.0)
        haz *= 1 + 0.6 * max(0, age_frac(runs, 'p2-felt-top', t) - 0.7) + 0.4 * max(0, age_frac(runs, 'form-bottom', t) - 0.8)
        if dt.datetime.combine(B('2026-05-01'), dt.time(0)) <= t < DT(PLANTS['F1']['change']): haz *= 2.2 if not ENG.ON else 1.2   # F1: the filled felt (with the engine: the extra only)
        if rnd.random() < haz * 0.5:      # (30 min steps)
            r = rnd.random()
            where = 'reel' if r < .35 else 'dryer' if r < .75 else 'press'
            u = rnd.random()
            m = 2 * (4 + u * 6 if where == 'reel' else 12 + u * 14 if where == 'dryer' else 26 + u * 20)
            sec = {'reel': 'Reel drum', 'dryer': rnd.choice(['Dryer can 3', 'Dryer can 6', 'Dryer can 11', 'Dryer can 16']), 'press': '2nd press top felt'}[where]
            ev.append(dict(start=t.replace(second=0, microsecond=0), end=(t + MIN * m).replace(second=0, microsecond=0), kind='break',
                           cause='break_', asset=sec, note=f'Sheet break at the {where}', story='', where=where))
            t += MIN * m
    ev.sort(key=lambda e: e['start'])
    for i, e in enumerate(ev):
        e['grade'] = grade_at(sched, e['start']); e['crew'] = crew_at(e['start'])
        e['minutes'] = round((e['end'] - e['start']).total_seconds() / 60, 1)
    return ev, faults


# ═════════════════════════ RCFA rule ═════════════════════════
def rcfa_events(ev):
    """Unplanned stops that get an RCFA: >= rcfa_min_hours, or the 2nd on the same asset within 60 days (the
    planted ones decide for themselves: F1 and F4 yes, F5 no)."""
    lim = CFG['rates']['rcfa_min_hours'] * 60; out = []; last = {}
    for e in ev:
        if e['kind'] != 'unplanned' or e['start'].date() < Y0 or e['start'].date() > TODAY: continue
        rep = e['asset'] in last and (e['start'] - last[e['asset']]).days <= 60
        last[e['asset']] = e['start']
        if e['story'] == 'F5': continue
        if e['story'] in ('F1', 'F4') or e['minutes'] >= lim or rep: out.append(e)
    return out


def build(seed=SEED):
    rnd = random.Random(seed)
    sched = grade_schedule(rnd)
    runs = position_runs(rnd)
    ev, faults = stops(rnd, sched, runs)
    dev = degrade.build(seed, ev, in_outage)                 # developing failures (their own random stream)
    ev.sort(key=lambda e: e['start'])
    for e in ev:
        e['grade'] = grade_at(sched, e['start']); e['crew'] = crew_at(e['start'])
        e['minutes'] = round((e['end'] - e['start']).total_seconds() / 60, 1)
    return dict(seed=seed, sched=sched, runs=runs, events=ev, faults=faults, developing=dev, rcfa_events=rcfa_events(ev))
