"""Sim Mill's Machine Manager records (mm_records rows), loaded through the token-guarded ingest like everything else:

    out/records/mymachine.json     machine setup + one item per position, with its full run history (My Machine)
    out/records/outages.json       the 6-week schedule, tasks and manning for the recent and next outages (Outage Planning)
    out/records/consumables.json   one "PM1 Consumables" board with inventory cards (counts and reorder points)

Each file is {record id: data}, the shapes mm-machine.js, OperationsOutagePlanning.html and mm-board.js save.
"""
import datetime as dt, json, os, random
from .base import CFG, PLANTS, D, DAY, HOUR, TODAY, OUTAGES, NEXT_OUTAGE, POS_NAME, MACHINE, NAME
from .model import piece_at

def _day(t): return t.date().isoformat() if t else ''

def mymachine(m):
    mc = CFG['machine']
    machine = {'name': mc['name'], 'former': mc['former'], 'press': mc['press'], 'dryers': mc['dryers'], 'calender': mc['calender'],
               'refiners': mc['refiners']}
    rec = {'machine': machine}
    today = dt.datetime.combine(TODAY, dt.time(23))
    cond = {   # the current pieces worth flagging on Oct 31
        PLANTS['F3']['position']: ('wear', 'Specific energy climbing ~1.4%/day since Oct 7 (Envoy flags from mid-October). Ridgeway: change Nov 11 with REF 1; one set on hand.', 5),
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
        if pos not in cond and age > .9: c, note, ago = 'wear', 'Near target life; planned for the next outage.', 3
        item = {'installed': _day(cur['installed']), 'target': cur['target_days'] // 7, 'targetUnit': 'weeks', 'vendor': cur['vendor'],
                'style': cur['style'], 'serial': cur['serial'], 'note': '', 'condition': c, 'conditionNote': note,
                'conditionDate': (TODAY - DAY * ago).isoformat() if c != 'good' else '', 'history': hist}
        rec[f'item:{pos}'] = item
    return rec

CREW_NAMES = {
    'A': ['H. Mbeki', 'T. Lindgren', 'A. Osei', 'P. Delgado', 'R. Kowal', 'S. Iqbal', 'J. Fontaine', 'M. Healy', 'D. Novak', 'L. Ahn'],
    'B': ['L. Brandt', 'K. Mwangi', 'E. Duarte', 'G. Pryor', 'N. Ferris', 'O. Stavros', 'C. Lund', 'V. Achter', 'B. Quarles', 'F. Imrie'],
    'C': ['R. Okonkwo', 'Y. Tanaka', 'M. Rocha', 'W. Hale', 'I. Bergstrom', 'Z. Coyle', 'U. Petrov', 'H. Lyle', 'J. Ndiaye', 'S. Varga'],
    'D': ['W. Castellano', 'P. Yoon', 'A. Lachance', 'E. Mahler', 'T. Obi', 'K. Rudd', 'B. Sorensen', 'N. Pike', 'G. Ferrante', 'D. Wilde'],
}
POS = ['SPOT', 'WET', 'DET', 'SPAT', 'WT', 'WAT', 'IB1', 'IB2', 'OB1', 'EXTRA']
COLORS = ['#fff4b8', '#d4ecff', '#d9f3d3', '#ffd8e1', '#e9e0ff', '#ffe2c4']

def outages(m, rec_):
    from .base import crews
    rnd = random.Random(7707)
    r = {'settings': {'cadenceDays': CFG['outages']['cadence_days'], 'anchor': str(CFG['outages']['anchor']), 'setUp': True}}
    show = [o for o in OUTAGES if o['date'] >= TODAY - DAY * 140] + [dict(date=NEXT_OUTAGE['date'] + DAY * 42 * k, id=f"OUT-{(NEXT_OUTAGE['date'] + DAY * 42 * k).isoformat()}") for k in (1, 2, 3)]
    at = [int(dt.datetime(2026, 8, 1).timestamp() * 1000)]; tn = [0]
    def task(oid, text, done):
        tn[0] += 1; at[0] += 60000
        r[f'task:{oid}-t{tn[0]}'] = {'outage': oid, 'text': text, 'done': bool(done), 'at': at[0], 'color': COLORS[tn[0] % len(COLORS)]}
    for o in show:
        oid = 'sm-' + o['date'].isoformat(); r[f'outage:{oid}'] = {'date': o['date'].isoformat(), 'type': 'normal'}
        if o['date'] <= TODAY:
            for a in rec_['actions']:
                if a.bucket == 'Outage prep' and f"{o['date']:%b %d}" in a.title: task(oid, a.title.replace(f" for the {o['date']:%b %d} outage", ''), True)
            day, night = crews(o['date'] - DAY)
            r[f'man:{oid}:shutdown'] = dict(zip(POS, CREW_NAMES[night])); r[f'man:{oid}:day'] = dict(zip(POS, CREW_NAMES[day]))
            r[f'man:{oid}:shortoff'] = dict(zip(POS[:8], CREW_NAMES[[c for c in 'ABCD' if c not in (day, night)][0]]))
    nid = 'sm-' + NEXT_OUTAGE['date'].isoformat()
    for text, done in (('Order clothing for Nov 11 (2nd press top felt, 1st press bottom felt)', True),
                       ('Refiner plates: REF 1 and REF 2 both due, one Ridgeway set on hand. Order the second set (SM action)', False),
                       ('Reel drum DS bearing: confirm the 22238 arrives Nov 5; plan 10 h job with millwrights', False),
                       ('Brightwater: replace the 3rd section DS rotary joint and re-align the bracket (3 seal failures this year)', False),
                       ('Couch roll seal strips and 2nd section PV fan belts: parts not reserved', False),
                       ('Confirm crane and riggers booked for 06:00', True), ('Scaffold request for the reel and 3rd section joint', False)):
        task(nid, text, done)
    day, night = crews(NEXT_OUTAGE['date'] - DAY)
    r[f'man:{nid}:shutdown'] = dict(zip(POS, CREW_NAMES[night]))
    r[f'man:{nid}:day'] = dict(zip(POS[:9], CREW_NAMES[day]))
    return r

def consumables():
    bid = 'sm-pm1-consumables'
    cats = [('plates', 'Refiner plates', '#9333ea'), ('blade', 'Doctor blades', '#d97706'), ('nozzle', 'Shower nozzles', '#2563eb'),
            ('rope', 'Dryer rope', '#dc2626'), ('uhle', 'Uhle box covers', '#16a34a'), ('deckle', 'Deckle strips', '#0891b2')]
    FW, FH, FG = 600, 580, 56
    r = {f'p:{bid}': {'name': f'{MACHINE} Consumables', 'meta': {'area': MACHINE, 'desc': 'Sim Mill stores: counts as of Oct 31, 2026, with reorder points.'},
                      'created': '2026-10-31T12:00:00.000Z'}}
    frames = {}
    for i, (k, t, c) in enumerate(cats):
        fid = f'{bid}-f-{k}'; x, y = (i % 3) * (FW + FG), (i // 3) * (FH + FG); frames[k] = (fid, x, y)
        r[f'f:{bid}:{fid}'] = {'x': x, 'y': y, 'w': FW, 'h': FH, 'title': t, 'color': c}
    cards = [
        ('plates', 'Refiner plates', '#e9e0ff', 'sets', ['Manufacturer', 'Pattern / part #'],
         [('Ridgeway Refining', '34" LC, 3.0/4.0 bar/groove · RR-34LC-30', 1)], 2,
         'REF 1 and REF 2 both due Nov 11 (REF 2 early: plates wearing fast). Second set on order.', {'mode': 'all', 'list': ''}),
        ('uhle', 'Uhle box covers', '#d9f3d3', 'each', ['Cover', 'Part #'],
         [('1st press top felt', 'UB-1PT', 2), ('1st press bottom felt', 'UB-1PB', 1), ('2nd press top felt', 'UB-2PT', 1), ('2nd press bottom felt', 'UB-2PB', 0)], 4, '', None),
        ('rope', 'Dryer rope', '#ffd8e1', 'spools', ['Colour', 'Size / part #'], [('Red', '5/8 in · RP-58R', 3), ('Blue', '5/8 in · RP-58B', 2)], 2, '', None),
        ('nozzle', 'HP shower nozzles (2nd press)', '#d4ecff', 'each', ['Nozzle', 'Part #'], [('Needle 1.0 mm', 'NZ-N100', 140)], 60,
         'Spraywell audit May 13 found 22% plugged on the 2nd press top shower.', None),
        ('blade', 'Dryer doctor blades', '#ffe2c4', 'each', ['Blade', 'Part #'], [('Steel 1.2 mm, 4.6 m', 'DB-DRY-S12', 22)], 20, '', None),
        ('deckle', 'Rotary joint seal kits', '#fff4b8', 'kits', ['Kit', 'Part #'], [('Brightwater carbon ring kit', 'BS-RJ-2200', 1)], 2,
         '3rd section DS joint used three this year.', None),
    ]
    for n, (cat, title, color, unit, cols, rows, mn, note, fits) in enumerate(cards):
        fid, x, y = frames[cat]; cid = f'{bid}-c{n + 1}'
        cons = {'type': cat if cat != 'deckle' else 'inv', 'kind': 'inv', 'unit': unit, 'cols': cols, 'counted': '2026-10-31',
                'rows': [{'id': f'{cid}-r{i + 1}', 'a': a, 'b': b, 'q': q} for i, (a, b, q) in enumerate(rows)], 'min': mn}
        if fits: cons['fits'] = fits
        r[f'n:{bid}:{cid}'] = {'x': x + 24, 'y': y + 58, 'z': n + 1, 'color': color, 'w': 268, 'text': title + ('\n' + note if note else ''),
                              'cons': cons, 'attachments': [], 'children': [], 'parent': None, 'cat': fid}
    r[f'n:{bid}:{bid}-c7'] = {'x': frames['plates'][1] + 24, 'y': frames['plates'][2] + 260, 'z': 7, 'color': '#ffffff', 'w': 268,
                              'text': 'Reel drum DS bearing\nOn order for the Nov 11 outage, ETA Nov 5.',
                              'cons': {'type': 'inv', 'kind': 'inv', 'unit': 'each', 'cols': ['Item', 'Part #'], 'counted': '2026-10-31',
                                       'rows': [{'id': 'b1', 'a': 'Spherical roller bearing', 'b': '22238 CCK/W33', 'q': 0}], 'min': 1},
                              'attachments': [], 'children': [], 'parent': None}
    r['seeded'] = {'at': '2026-10-31T12:00:00.000Z'}
    return r

def write(m, rec_, out):
    d = os.path.join(out, 'records'); os.makedirs(d, exist_ok=True)
    for name, data in (('mymachine', mymachine(m)), ('outages', outages(m, rec_)), ('consumables', consumables())):
        json.dump(data, open(os.path.join(d, f'{name}.json'), 'w'), indent=1)
