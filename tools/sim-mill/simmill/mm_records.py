"""Sim Mill's Machine Manager records (mm_records rows), loaded through the token-guarded ingest like everything else:

    out/records/mymachine.json      machine setup + one item per position, with its run history (My Machine)
    out/records/task-packages.json  Sim Mill's task-package library (Ops Task Library), built by ../packages.js
    out/records/outages.json        the 6-week schedule around "today": the last three outages done, the next one being
                                    planned, the one after started, two more with a note each (Outage Planning)
    out/records/consumables.json    one "PM1 Consumables" board with inventory cards (counts and reorder points)

Each file is {record id: data}, the shapes mm-machine.js, OperationsOutagePlanning.html and mm-board.js save. Packages on
an outage come from what the model actually changed (past outages) or what is due (coming ones), so Outage Planning, My
Machine and the assistant agree. Every date follows the 6-week roll (base.SHIFT).
"""
import datetime as dt, json, os, random, subprocess
from .base import B, BT, md, tx, SHIFT
from .base import CFG, PLANTS, D, DAY, HOUR, TODAY, OUTAGES, NEXT_OUTAGE, POS_NAME, MACHINE, NAME, HERE, crews
from .model import piece_at, due_at_next_outage

def _day(t): return t.date().isoformat() if t else ''
def _ms(t): return int(t.replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
def _tx_all(v):
    """tx() over every string in a JSON value (ids and colours have no dates in them, so they pass through)."""
    if isinstance(v, str): return tx(v)
    if isinstance(v, dict): return {k: _tx_all(x) for k, x in v.items()}
    if isinstance(v, list): return [_tx_all(x) for x in v]
    return v

# ═════════════════════════ The change plan ═════════════════════════
def change_plan(runs):
    """What the next four outages change: {outage date: [positions]}, stepping through them in order so a piece changed
    at one isn't due again at the next. Shared by My Machine's notes and Outage Planning's packages."""
    cad = CFG['outages']['cadence_days']; dates = [NEXT_OUTAGE['date'] + DAY * cad * k for k in range(4)]
    plan = {d: [] for d in dates}
    for pos, rr in runs.items():
        cur = rr[-1]; last = cur['installed'].date()
        for d in dates:
            due = (due_at_next_outage(runs, pos) or pos == PLANTS['F3']['position']) if d == dates[0] else (d - last).days >= cur['target_days'] - 21
            if due: plan[d].append(pos); last = d
    return plan

# ═════════════════════════ My Machine ═════════════════════════
def mymachine(m):
    mc = CFG['machine']
    machine = {'name': mc['name'], 'former': mc['former'], 'press': mc['press'], 'dryers': mc['dryers'], 'calender': mc['calender'],
               'refiners': mc['refiners']}
    rec = {'machine': machine}; plan = change_plan(m['runs'])
    today = dt.datetime.combine(TODAY, dt.time(23)); nxt = md(NEXT_OUTAGE['date'])
    cond = {   # the current pieces worth flagging today
        PLANTS['F3']['position']: ('wear', f"Specific energy climbing ~1.4%/day since {md(PLANTS['F3']['rise_from'])} (Envoy flags since). "
                                           f"Ridgeway: change at the {nxt} outage with REF 1; one set on hand.", 5),
        'p2-felt-top': ('good', '', 0),
    }
    for pos, runs in m['runs'].items():
        past = [r for r in runs if r['removed'] and r['removed'] <= today]
        cur = next((r for r in runs if r['installed'] <= today and (not r['removed'] or r['removed'] > today)), runs[-1])
        hist = [{'installed': _day(r['installed']), 'removed': _day(r['removed']), 'days': (r['removed'] - r['installed']).days,
                 'vendor': r['vendor'], 'style': r['style'], 'serial': r['serial'], 'reason': r['reason'] or 'planned',
                 'condition': r['condition'] if r['condition'] in ('good', 'wear', 'worn', 'damaged') else 'worn', 'note': r['note']} for r in past][-8:]
        c, note, ago = cond.get(pos, ('good', '', 0))
        age = (today - cur['installed']).days / cur['target_days']
        when = next((d for d, ps in plan.items() if pos in ps), None)
        if pos not in cond and age > .9:
            c, ago = 'wear', 3
            at = f'change planned for the {md(when)} outage' if when else 'not on an outage plan yet'
            note = f'Near target life. Recovered spare from Pellham on site; {at}.' if cur['kind'] == 'roll' else f'Near target life; {at}.'
        elif pos not in cond and cur['kind'] == 'roll' and age > .85:
            c, ago = 'wear', 20
            note = 'Cover hardness up on the last Pellham check' + (f'; recovery planned for the {md(when)} outage.' if when else '; plan the recovery within the next few outages.')
        item = {'installed': _day(cur['installed']), 'target': cur['target_days'] // 7, 'targetUnit': 'weeks', 'vendor': cur['vendor'],
                'style': cur['style'], 'serial': cur['serial'], 'note': '', 'condition': c, 'conditionNote': note,
                'conditionDate': (TODAY - DAY * ago).isoformat() if c != 'good' else '', 'history': hist}
        rec[f'item:{pos}'] = item
    return rec

# ═════════════════════════ Task packages ═════════════════════════
def task_packages(out):
    """Runs packages.js (the page's own layout code) and returns (records, {package id: {name, meta, phases}})."""
    subprocess.run(['node', os.path.join(HERE, 'packages.js'), out, BT('2026-10-01T12:00').strftime('%Y-%m-%dT%H:%M:%S.000Z')],
                   check=True, stdout=subprocess.DEVNULL)
    d = os.path.join(out, 'records')
    recs = _tx_all(json.load(open(os.path.join(d, 'task-packages.json'))))
    phases = _tx_all(json.load(open(os.path.join(d, '_package_phases.json'))))
    os.remove(os.path.join(d, '_package_phases.json'))
    return recs, phases

def package_for(pos):
    if pos == 'form-bottom': return 'sm-forming-fabric'
    if pos.startswith('ref-'): return 'sm-refiner-plates'
    if '-froll-' in pos: return 'sm-felt-roll'
    if pos.startswith('p') and '-felt-' in pos: return 'sm-press-felt'
    if pos.startswith('d') and pos.endswith('-felt'): return 'sm-dryer-felt'
    return None                                                     # press rolls: a task, not a package

# ═════════════════════════ Outage Planning ═════════════════════════
CREW_NAMES = {
    'A': ['H. Mbeki', 'T. Lindgren', 'A. Osei', 'P. Delgado', 'R. Kowal', 'S. Iqbal', 'J. Fontaine', 'M. Healy', 'D. Novak', 'L. Ahn'],
    'B': ['L. Brandt', 'K. Mwangi', 'E. Duarte', 'G. Pryor', 'N. Ferris', 'O. Stavros', 'C. Lund', 'V. Achter', 'B. Quarles', 'F. Imrie'],
    'C': ['R. Okonkwo', 'Y. Tanaka', 'M. Rocha', 'W. Hale', 'I. Bergstrom', 'Z. Coyle', 'U. Petrov', 'H. Lyle', 'J. Ndiaye', 'S. Varga'],
    'D': ['W. Castellano', 'P. Yoon', 'A. Lachance', 'E. Mahler', 'T. Obi', 'K. Rudd', 'B. Sorensen', 'N. Pike', 'G. Ferrante', 'D. Wilde'],
}
POS = ['SPOT', 'WET', 'DET', 'SPAT', 'WT', 'WAT', 'IB1', 'IB2', 'OB1', 'EXTRA']
COLORS = ['#fff4b8', '#d4ecff', '#d9f3d3', '#ffd8e1', '#e9e0ff', '#ffe2c4']
CREW_TASKS = [   # routine outage jobs, a few per finished outage
    'Clean and check all HP showers: forming and both presses', 'Clean the 2nd press shower supply strainer',
    'Pull and clean Uhle box covers, check for wear', 'Hose down the press pit and clear felt hairs from the saveall',
    'Check doctor blades on the dryer cans: log any changed', 'Empty the LC cleaner sand traps',
    'Clean the headbox approach piping', 'Grease the felt roll bearings, 1st to 4th section', 'Inspect the reel spool arms and rails',
]
FELTS = ('sm-press-felt', 'sm-forming-fabric', 'sm-dryer-felt')

def outages(m, rec_, lib):
    rnd = random.Random(7707)
    runs = m['runs']; cad = CFG['outages']['cadence_days']
    r = {'settings': {'cadenceDays': cad, 'anchor': str(CFG['outages']['anchor']), 'setUp': True}}
    past = [o for o in OUTAGES if TODAY - DAY * 130 <= o['date'] <= TODAY]
    nxt = NEXT_OUTAGE
    later = [nxt['date'] + DAY * cad * k for k in (1, 2, 3)]
    at = [_ms(dt.datetime.combine(past[0]['date'] - DAY * 45, dt.time(8)))]; tn = [0]
    def stamp(step=60000): at[0] += step; return at[0]
    def task(oid, text, done):
        tn[0] += 1
        r[f'task:{oid}-t{tn[0]}'] = {'outage': oid, 'text': text, 'done': bool(done), 'at': stamp(), 'color': COLORS[tn[0] % len(COLORS)]}
    def pkg(oid, src, positions, tick):
        L = lib[src]; meta = L['meta']; pid = f'{oid}-{src}'
        names = ', '.join(POS_NAME[p] for p in positions)
        r['pkg:' + pid] = {'outage': oid, 'source': src, 'name': L['name'], 'area': meta.get('area'),
                           'desc': (names + '. ' if names else '') + meta.get('desc', ''), 'hours': meta.get('hours'), 'crew': meta.get('crew'),
                           'at': stamp(), 'phases': L['phases']}
        for i, ph in enumerate(L['phases']):
            for st in ph['steps']:
                if tick(i, st): r[f'pkd:{pid}:{st["id"]}'] = {'done': True, 'at': stamp(1000)}
    def man(oid, d, seats_day=10, seats_short=8):
        day, night = crews(d - DAY)
        r[f'man:{oid}:shutdown'] = dict(zip(POS, CREW_NAMES[night]))
        r[f'man:{oid}:day'] = dict(zip(POS[:seats_day], CREW_NAMES[day]))
        other = [c for c in 'ABCD' if c not in (day, night)]
        r[f'man:{oid}:shortoff'] = dict(zip(POS[:seats_short], CREW_NAMES[other[0]]))
        # Startup runs the shutdown crew with a change or two (Outage Planning stores only the changes)
        spare = CREW_NAMES[other[1]]
        r[f'man:{oid}:startup'] = {p: rnd.choice(spare) for p in rnd.sample(['WT', 'SPAT', 'EXTRA', 'IB2'], rnd.choice((1, 2)))}
    def group(positions):
        g = {}
        for p in positions:
            src = package_for(p)
            if src: g.setdefault(src, []).append(p)
        return g
    plan = change_plan(runs)

    # ---- the last outages: done ----
    for o in past:
        oid = 'sm-' + o['date'].isoformat(); r[f'outage:{oid}'] = {'date': o['date'].isoformat(), 'type': 'normal'}
        changed = sorted({pos for pos, rr in runs.items() for x in rr if x['removed'] and o['start'] <= x['removed'] <= o['end'] + HOUR * 3})
        for src, poss in group(changed).items(): pkg(oid, src, poss, lambda i, st: True)
        if o is past[-1]: pkg(oid, 'sm-stock-prep-cleaners', [], lambda i, st: True)
        for p in changed:
            if package_for(p) is None: task(oid, f'Change the {POS_NAME[p]} (recovered roll from Pellham)', True)
        for a in rec_['actions']:
            if a.bucket == 'Outage prep' and f"{o['date']:%b %d}" in a.title: task(oid, a.title.replace(f" for the {o['date']:%b %d} outage", ''), True)
        for t in rnd.sample(CREW_TASKS, 3): task(oid, t, True)
        man(oid, o['date'])

    # ---- the next outage: being planned ----
    nid = 'sm-' + nxt['date'].isoformat(); r[f'outage:{nid}'] = {'date': nxt['date'].isoformat(), 'type': 'normal'}
    due = plan[nxt['date']]
    for src, poss in group(due).items():
        # prep phase done, except the plates: only one set is on hand
        pkg(nid, src, poss, (lambda i, st: i == 0 and not st['title'].startswith('Plates on hand')) if src == 'sm-refiner-plates' else (lambda i, st: i == 0))
    pkg(nid, 'sm-stock-prep-cleaners', [], lambda i, st: i == 0 and st['title'].startswith('Plan'))
    for p in due:
        if package_for(p) is None: task(nid, f'Change the {POS_NAME[p]}: recovered spare from Pellham on site', True)
    fel = [POS_NAME[p] for p in due if package_for(p) in FELTS]
    for text, done in ((f"Order clothing for {md(nxt['date'])}: {', '.join(fel)}" if fel else None, True),
                       ('Refiner plates: REF 1 and REF 2 both due, one Ridgeway set on hand. Order the second set (SM action)', False),
                       (f"Reel drum DS bearing: confirm the 22238 arrives {md(B('2026-11-05'))}; plan 10 h job with millwrights", False),
                       ('Brightwater: replace the 3rd section DS rotary joint and re-align the bracket (3 seal failures this year)', False),
                       ('Couch roll seal strips and 2nd section PV fan belts: parts not reserved', False),
                       ('Confirm crane and riggers booked for 06:00', True), ('Scaffold request for the reel and 3rd section joint', False)):
        if text: task(nid, text, done)
    man(nid, nxt['date'], seats_day=9, seats_short=8)

    # ---- the one after: started; then two more with a note each ----
    for k, d in enumerate(later):
        oid = 'sm-' + d.isoformat(); r[f'outage:{oid}'] = {'date': d.isoformat(), 'type': 'normal'}
        due = plan[d]
        if k == 0:
            for src, poss in group(due).items(): pkg(oid, src, poss, lambda i, st: False)
            fel = [POS_NAME[p] for p in due if package_for(p) in FELTS]
            if fel: task(oid, f"Order clothing for {md(d)}: {', '.join(fel)}", False)
            for p in due:
                if package_for(p) is None: task(oid, f'Change the {POS_NAME[p]}: confirm the recovered spare ships from Pellham', False)
            task(oid, 'Book an extra hand for the felt pull-ins', False)
            day, night = crews(d - DAY)
            r[f'man:{oid}:shutdown'] = dict(zip(POS[:6], CREW_NAMES[night]))
        elif due:
            task(oid, f"Due by {md(d)}: {', '.join(POS_NAME[p] for p in due[:4])}{' and more' if len(due) > 4 else ''}. Check My Machine nearer the time", False)
    return r

# ═════════════════════════ Consumables ═════════════════════════
def consumables():
    bid = 'sm-pm1-consumables'; nxt = md(NEXT_OUTAGE['date']); counted = TODAY.isoformat()
    cats = [('plates', 'Refiner plates', '#9333ea'), ('blade', 'Doctor blades', '#d97706'), ('nozzle', 'Shower nozzles', '#2563eb'),
            ('rope', 'Dryer rope', '#dc2626'), ('uhle', 'Uhle box covers', '#16a34a'), ('deckle', 'Deckle strips', '#0891b2'),
            ('parts', 'Bearings and seals', '#475569')]
    FW, FH, FG = 600, 580, 56
    r = {f'p:{bid}': {'name': f'{MACHINE} Consumables', 'meta': {'area': MACHINE, 'desc': f"Sim Mill stores: counts as of {md(TODAY, '%b %-d, %Y')}, with reorder points."},
                      'created': f'{counted}T12:00:00.000Z'}}
    frames = {}
    for i, (k, t, c) in enumerate(cats):
        fid = f'{bid}-f-{k}'; x, y = (i % 3) * (FW + FG), (i // 3) * (FH + FG); frames[k] = (fid, x, y)
        r[f'f:{bid}:{fid}'] = {'x': x, 'y': y, 'w': FW, 'h': FH, 'title': t, 'color': c}
    cards = [
        ('plates', 'Refiner plates', '#e9e0ff', 'sets', ['Manufacturer', 'Pattern / part #'],
         [('Ridgeway Refining', '34" LC, 3.0/4.0 bar/groove · RR-34LC-30', 1)], 2,
         f'REF 1 and REF 2 both due {nxt} (REF 2 early: plates wearing fast). Second set on order.', {'mode': 'all', 'list': ''}),
        ('uhle', 'Uhle box covers', '#d9f3d3', 'each', ['Cover', 'Part #'],
         [('1st press top felt', 'UB-1PT', 2), ('1st press bottom felt', 'UB-1PB', 1), ('2nd press top felt', 'UB-2PT', 1), ('2nd press bottom felt', 'UB-2PB', 0)], 4, '', None),
        ('rope', 'Dryer rope', '#ffd8e1', 'spools', ['Colour', 'Size / part #'], [('Red', '5/8 in · RP-58R', 3), ('Blue', '5/8 in · RP-58B', 2)], 2, '', None),
        ('nozzle', 'HP shower nozzles (2nd press)', '#d4ecff', 'each', ['Nozzle', 'Part #'], [('Needle 1.0 mm', 'NZ-N100', 140)], 60,
         tx('Spraywell audit May 13 found 22% plugged on the 2nd press top shower.'), None),
        ('blade', 'Dryer doctor blades', '#ffe2c4', 'each', ['Blade', 'Part #'], [('Steel 1.2 mm, 4.6 m', 'DB-DRY-S12', 22)], 20, '', None),
        ('deckle', 'Deckle strips', '#fff4b8', 'each', ['Strip', 'Inventory #'], [('Forming board', 'INV 51207', 5)], 2, '', None),
        ('parts', 'Rotary joint seal kits', '#ffffff', 'kits', ['Kit', 'Part #'], [('Brightwater carbon ring kit', 'BS-RJ-2200', 1)], 2,
         '3rd section DS joint used three this year.', None),
    ]
    for n, (cat, title, color, unit, cols, rows, mn, note, fits) in enumerate(cards):
        fid, x, y = frames[cat]; cid = f'{bid}-c{n + 1}'
        cons = {'type': cat if cat != 'parts' else 'inv', 'kind': 'inv', 'unit': unit, 'cols': cols, 'counted': counted,
                'rows': [{'id': f'{cid}-r{i + 1}', 'a': a, 'b': b, 'q': q} for i, (a, b, q) in enumerate(rows)], 'min': mn}
        if fits: cons['fits'] = fits
        r[f'n:{bid}:{cid}'] = {'x': x + 24, 'y': y + 58, 'z': n + 1, 'color': color, 'w': 268, 'text': title + ('\n' + note if note else ''),
                              'cons': cons, 'attachments': [], 'children': [], 'parent': None, 'cat': fid}
    r[f'n:{bid}:{bid}-c8'] = {'x': frames['parts'][1] + 24 + 284, 'y': frames['parts'][2] + 58, 'z': 8, 'cat': frames['parts'][0], 'color': '#ffffff', 'w': 268,
                              'text': f"Reel drum DS bearing\nOn order for the {nxt} outage, ETA {md(B('2026-11-05'))}.",
                              'cons': {'type': 'inv', 'kind': 'inv', 'unit': 'each', 'cols': ['Item', 'Part #'], 'counted': counted,
                                       'rows': [{'id': 'b1', 'a': 'Spherical roller bearing', 'b': '22238 CCK/W33', 'q': 0}], 'min': 1},
                              'attachments': [], 'children': [], 'parent': None}
    r['seeded'] = {'at': f'{counted}T12:00:00.000Z'}
    return r

def write(m, rec_, out):
    d = os.path.join(out, 'records'); os.makedirs(d, exist_ok=True)
    tp, lib = task_packages(out)
    for name, data in (('mymachine', mymachine(m)), ('task-packages', tp), ('outages', outages(m, rec_, lib)), ('consumables', consumables())):
        json.dump(data, open(os.path.join(d, f'{name}.json'), 'w'), indent=1)
