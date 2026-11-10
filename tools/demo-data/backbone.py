"""MM LLM demo data — phase 1: the shared backbone every mock source is built on.

Writes demo-data/backbone/*.csv (equipment register, outages, grade schedule, crew schedule, roster,
vendors, Pi tags) for one fixed demo year, and checks the storylines in tools/demo-data/storylines/.

    python3 tools/demo-data/backbone.py           # regenerate the CSVs
    python3 tools/demo-data/backbone.py --check   # exit 1 if the CSVs are stale or a storyline is invalid (CI)

Everything is seeded, so the output only changes when this file or a storyline changes.
All people and companies are fictional.
"""
import csv, io, os, random, sys, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'demo-data', 'backbone')
STORIES = os.path.join(ROOT, 'tools', 'demo-data', 'storylines')
SEED = 1101

YEAR_START, YEAR_END = dt.date(2025, 11, 1), dt.date(2026, 10, 31)
DEMO_TODAY = dt.date(2026, 10, 31)       # "now" in the demo: the brief is for the Nov 11 outage
D = dt.date.fromisoformat
days = lambda a, b: (b - a).days


# ───────────────────────── Outages ─────────────────────────
# Normal outages sit on the app's 6-week grid (anchored Nov 11, 2026). The annual outage replaces the
# Sep 30 slot and runs one week in October.
def outages():
    anchor, grid = D('2026-11-11'), []
    d = anchor
    while d >= YEAR_START:
        grid.append(d); d -= dt.timedelta(days=42)
    rows = []
    for d in sorted(grid):
        if d == D('2026-09-30'):
            rows.append(dict(id='OUT-2026-ANNUAL', type='annual', start='2026-10-05T07:00', end='2026-10-11T19:00',
                             note='One-week annual outage (replaces the Sep 30 slot)'))
        else:
            rows.append(dict(id=f'OUT-{d.isoformat()}', type='normal', start=f'{d}T06:00', end=f'{d}T20:00',
                             note='14 h normal outage'))
    return rows


# ───────────────────────── Grades ─────────────────────────
GRADES = [  # linerboard, lb/MSF; speeds are demo assumptions
    dict(grade='26#', share=.25, speed=2450),
    dict(grade='30#', share=.35, speed=2250),
    dict(grade='33#', share=.40, speed=2050),
]

def grade_schedule(outs):
    rnd = random.Random(SEED)
    down = [(dt.datetime.fromisoformat(o['start']), dt.datetime.fromisoformat(o['end'])) for o in outs]
    t, end = dt.datetime.combine(YEAR_START, dt.time(0)), dt.datetime.combine(YEAR_END, dt.time(23, 59))
    rows, last = [], None
    while t < end:
        g = rnd.choices([x for x in GRADES if x['grade'] != last], [x['share'] for x in GRADES if x['grade'] != last])[0]
        hrs = rnd.uniform(26, 46)                    # 4–5 grade changes a week on average
        stop = min(t + dt.timedelta(hours=hrs), end)
        for a, b in down:                            # an outage interrupts the run
            if t < a < stop:
                stop = a
        rows.append(dict(start=t.isoformat(timespec='minutes'), end=stop.isoformat(timespec='minutes'), grade=g['grade'], speed_fpm=g['speed']))
        last = g['grade']; t = stop
        for a, b in down:
            if t == a:
                rows.append(dict(start=a.isoformat(timespec='minutes'), end=b.isoformat(timespec='minutes'), grade='DOWN', speed_fpm=0))
                t = b; last = None
    return rows


# ───────────────────────── Crews (DuPont 12 h) ─────────────────────────
DUPONT = 'NNNNOOODDDONNNOOODDDDOOOOOOO'   # 28-day cycle per crew; crews offset by 7 days

def crew_schedule():
    rows, d = [], YEAR_START
    while d <= YEAR_END:
        k = days(D('2025-11-03'), d)
        on = {c: DUPONT[(k + 7 * i) % 28] for i, c in enumerate('ABCD')}
        rows.append(dict(date=d.isoformat(), day_crew=next(c for c, s in on.items() if s == 'D'),
                         night_crew=next(c for c, s in on.items() if s == 'N')))
        d += dt.timedelta(days=1)
    return rows


# ───────────────────────── People and companies (all fictional) ─────────────────────────
ROSTER = [
    ('P01', 'Garrett Holloway', 'PM1 superintendent', ''),
    ('P02', 'Denise Varga', 'Maintenance planner', ''),
    ('P03', 'Owen Achterberg', 'Reliability engineer', ''),
    ('P04', 'Priya Lunsford', 'Process engineer', ''),
    ('P05', 'Curtis Mabry', 'Maintenance supervisor', ''),
    ('P06', 'Lena Strahorn', 'Production manager', ''),
    ('P07', 'Wade Kittredge', 'Shift lead', 'A'),
    ('P08', 'Marisol Pena-Hart', 'Shift lead', 'B'),
    ('P09', 'Russ Delacroix', 'Shift lead', 'C'),
    ('P10', 'Tammy Odegaard', 'Shift lead', 'D'),
    ('P11', 'Jonah Brisbin', 'Machine tender', 'A'),
    ('P12', 'Kelsey Farrand', 'Machine tender', 'B'),
    ('P13', 'Dwight Umbach', 'Machine tender', 'C'),
    ('P14', 'Rafael Quist', 'Machine tender', 'D'),
    ('P15', 'Bonnie Szalay', 'Back tender', 'A'),
    ('P16', 'Travis Hallock', 'Back tender', 'B'),
    ('P17', 'Nadine Corbett-Oyelaran', 'Back tender', 'C'),
    ('P18', 'Elijah Pumphrey', 'Back tender', 'D'),
    ('P19', 'Hank Vosburgh', 'Millwright lead', ''),
    ('P20', 'Sierra Tolliver', 'E&I technician', ''),
    ('P21', 'Lyle Brackenridge', 'Stock prep operator', ''),
    ('P22', 'Corinne Ashdown', 'Quality / QCS engineer', ''),
]
VENDORS = [  # id, name, scope, rep
    ('V-NB', 'Northbank Fabrics', 'Forming fabrics and dryer fabrics; clothing surveys', 'Mitch Rennard'),
    ('V-HF', 'Halden Felt Co.', 'Press felts; felt surveys', 'Joanne Kebbel'),
    ('V-MP', 'Marlow Press Fabrics', 'Tandem felt', 'Arlo Fennimore'),
    ('V-CT', 'Corrie Textiles', '3rd section dryer fabrics', 'Bea Lindqvist-Moore'),
    ('V-RR', 'Ridgeway Refining', 'Base ply refiner plates; plate reports', 'Stan Oberholt'),
    ('V-BP', 'Brennock Plates', 'Top ply refiner plates', 'Gail Prentiss'),
    ('V-PR', 'Pellham Roll Service', 'Press and lumpbreaker roll covers, grinding', 'Vic Amundsen'),
    ('V-TR', 'Teague Roll Works', 'Calender rolls, grinding', 'Rhonda Esterly'),
    ('V-KV', 'Keel Vibration Services', 'Monthly vibration route', 'Darnell Whitcomb'),
    ('V-SN', 'Spraywell Nozzle Supply', 'Shower audits, vendor-managed nozzles', 'Ingrid Pasko'),
]


# ───────────────────────── Equipment register ─────────────────────────
# My Machine positions (same ids as mm-machine.js) plus the sub-equipment WOs, vibration routes and Pi need.
SECTIONS = [('sec-refiners', 'Refiners'), ('sec-topply', 'Top ply wire'), ('sec-baseply', 'Base ply wire'),
            ('sec-press', 'Press section'), ('sec-dryer-1', '1st dryer section'), ('sec-dryer-2', '2nd dryer section'),
            ('sec-dryer-3', '3rd dryer section'), ('sec-calender', 'Calender'), ('sec-reel', 'Reel')]
CANS = {'sec-dryer-1': range(1, 11), 'sec-dryer-2': range(11, 45), 'sec-dryer-3': range(45, 75)}

def equipment():
    rows, n = [], [41000]
    def add(name, section, kind, position='', parent=''):
        n[0] += 7
        a = f'{n[0]:08d}'
        rows.append(dict(asset_no=a, name=name, section=section, kind=kind, position_id=position, parent_asset=parent))
        return a
    sec = {sid: add(f'PM1 {name}', sid, 'section') for sid, name in SECTIONS}
    for r, nm in [('bp1', 'BP 1'), ('bp2', 'BP 2'), ('tp1', 'TP 1'), ('tp2', 'TP 2')]:
        ref = add(f'{nm} refiner', 'sec-refiners', 'refiner', f'ref-{r}', sec['sec-refiners'])
        add(f'{nm} refiner motor', 'sec-refiners', 'motor', '', ref)
    for ply, s, pos in [('Top ply', 'sec-topply', 'form-top'), ('Base ply', 'sec-baseply', 'form-bottom')]:
        add(f'{ply} headbox', s, 'headbox', '', sec[s])
        add(f'{ply} fan pump', s, 'pump', '', sec[s])
        add(f'{ply} forming fabric', s, 'fabric', pos, sec[s])
        add(f'{ply} couch roll', s, 'roll', '', sec[s])
        add(f'{ply} flat boxes', s, 'vacuum', '', sec[s])
        add(f'{ply} HP shower', s, 'shower', '', sec[s])
    add('Lumpbreaker roll', 'sec-baseply', 'roll', 'lumpbreaker', sec['sec-baseply'])
    add('Lumpbreaker doctor', 'sec-baseply', 'doctor', '', sec['sec-baseply'])
    for pos, nm in [('p1-felt-top', '1st press top felt'), ('p2-felt-top', '2nd press top felt'), ('p-tandem-felt', 'Tandem felt')]:
        f = add(nm, 'sec-press', 'fabric', pos, sec['sec-press'])
        add(f'{nm} Uhle box', 'sec-press', 'vacuum', '', f)
        add(f'{nm} HP shower', 'sec-press', 'shower', '', f)
    for pos, nm in [('p1-roll-top', '1st press top roll'), ('p1-roll-bottom', '1st press bottom roll'),
                    ('p2-roll-top', '2nd press top roll'), ('p2-roll-bottom', '2nd press bottom roll')]:
        add(nm, 'sec-press', 'roll', pos, sec['sec-press'])
    for i in (1, 2, 3, 4):
        add(f'Vacuum pump {i}', 'sec-press', 'pump', '', sec['sec-press'])
    fab = {'sec-dryer-1': [('d1-felt', '1st section unorun felt')],
           'sec-dryer-2': [('d2-felt-top', '2nd section top felt'), ('d2-felt-bottom', '2nd section bottom felt')],
           'sec-dryer-3': [('d3-felt-top', '3rd section top felt'), ('d3-felt-bottom', '3rd section bottom felt')]}
    for s, cans in CANS.items():
        for pos, nm in fab[s]:
            add(nm, s, 'fabric', pos, sec[s])
        o = {'1': '1st', '2': '2nd', '3': '3rd'}[s[-1]]
        add(f'{o} section drive group', s, 'drive', '', sec[s])
        add(f'{o} section steam & condensate', s, 'steam', '', sec[s])
        add(f'{o} section pocket ventilation', s, 'ventilation', '', sec[s])
        for c in cans:
            add(f'Dryer can {c}', s, 'dryer-can', '', sec[s])
    add('Calender top roll', 'sec-calender', 'roll', 'cal-top', sec['sec-calender'])
    add('Calender bottom roll', 'sec-calender', 'roll', 'cal-bottom', sec['sec-calender'])
    add('Calender loading hydraulics', 'sec-calender', 'hydraulics', '', sec['sec-calender'])
    add('Reel drum', 'sec-reel', 'roll', '', sec['sec-reel'])
    add('Reel spool handling', 'sec-reel', 'mechanical', '', sec['sec-reel'])
    add('QCS scanner', 'sec-reel', 'instrument', '', sec['sec-reel'])
    return rows


# ───────────────────────── Pi tags ─────────────────────────
# tag, description, units, asset name (resolved to asset_no), mean, sigma (hourly noise in the mock Pi series).
# Bonvoy flags beyond ±3σ of its own trailing baseline (see pi_bonvoy.py).
TAGS = [
    *[(f'PM1:REF_{r}_KW', f'{r} refiner motor load', 'kW', f'{n} refiner', 1150, 40) for r, n in [('BP1', 'BP 1'), ('BP2', 'BP 2'), ('TP1', 'TP 1'), ('TP2', 'TP 2')]],
    *[(f'PM1:REF_{r}_SE', f'{r} refiner specific energy', 'kWh/t', f'{n} refiner', 95, 1.0) for r, n in [('BP1', 'BP 1'), ('BP2', 'BP 2'), ('TP1', 'TP 1'), ('TP2', 'TP 2')]],
    ('PM1:HB_TOP_P', 'Top ply headbox pressure', 'psi', 'Top ply headbox', 9.8, .15),
    ('PM1:HB_BASE_P', 'Base ply headbox pressure', 'psi', 'Base ply headbox', 11.2, .15),
    ('PM1:HB_BASE_CONS', 'Base ply headbox consistency', '%', 'Base ply headbox', .82, .02),
    ('PM1:FORM_TOP_FLATBOX_VAC', 'Top ply flat box vacuum', 'inHg', 'Top ply flat boxes', 8.5, .3),
    ('PM1:FORM_BASE_COUCH_VAC', 'Base ply couch vacuum', 'inHg', 'Base ply couch roll', 18.0, .5),
    ('PM1:PRESS1_LOAD', '1st press nip load', 'pli', 'PM1 Press section', 1500, 20),
    ('PM1:PRESS2_LOAD', '2nd press nip load', 'pli', 'PM1 Press section', 2200, 25),
    ('PM1:UHLE_P1_VAC', '1st press felt Uhle box vacuum', 'inHg', '1st press top felt Uhle box', 11.0, .4),
    ('PM1:UHLE_P2_VAC', '2nd press felt Uhle box vacuum', 'inHg', '2nd press top felt Uhle box', 12.0, .4),
    ('PM1:UHLE_TAN_VAC', 'Tandem felt Uhle box vacuum', 'inHg', 'Tandem felt Uhle box', 12.5, .4),
    ('PM1:PRESS_OUT_MOIST', 'Sheet moisture after press (calc.)', '%', 'PM1 Press section', 58.0, .6),
    ('PM1:DRY1_STEAM_P', '1st section steam pressure', 'psig', '1st section steam & condensate', 25, 1.5),
    ('PM1:DRY2_STEAM_P', '2nd section steam pressure', 'psig', '2nd section steam & condensate', 75, 3),
    ('PM1:DRY3_STEAM_P', '3rd section steam pressure', 'psig', '3rd section steam & condensate', 110, 2),
    ('PM1:DRY3_PV_FAN_AMPS', '3rd section pocket ventilation fan', 'A', '3rd section pocket ventilation', 62, 1.0),
    ('PM1:DRY1_C05_DS_VIB', 'Dryer can 5 DS bearing velocity', 'in/s', 'Dryer can 5', .06, .006),
    ('PM1:DRY2_C15_DS_VIB', 'Dryer can 15 DS bearing velocity', 'in/s', 'Dryer can 15', .07, .006),
    ('PM1:DRY2_C21_DS_VIB', 'Dryer can 21 DS bearing velocity', 'in/s', 'Dryer can 21', .07, .006),
    ('PM1:DRY2_C27_DS_VIB', 'Dryer can 27 DS bearing velocity', 'in/s', 'Dryer can 27', .07, .006),
    ('PM1:DRY2_C27_DS_TEMP', 'Dryer can 27 DS bearing temperature', 'degF', 'Dryer can 27', 185, 1.5),
    ('PM1:DRY2_C27_TS_VIB', 'Dryer can 27 TS bearing velocity', 'in/s', 'Dryer can 27', .06, .006),
    ('PM1:DRY2_C33_DS_VIB', 'Dryer can 33 DS bearing velocity', 'in/s', 'Dryer can 33', .07, .006),
    ('PM1:DRY3_C49_DS_VIB', 'Dryer can 49 DS bearing velocity', 'in/s', 'Dryer can 49', .07, .006),
    ('PM1:DRY3_C61_DS_VIB', 'Dryer can 61 DS bearing velocity', 'in/s', 'Dryer can 61', .07, .006),
    ('PM1:PRESS2_BOT_DS_VIB', '2nd press bottom roll DS bearing velocity', 'in/s', '2nd press bottom roll', .08, .007),
    ('PM1:CAL_BOT_DS_VIB', 'Calender bottom roll DS bearing velocity', 'in/s', 'Calender bottom roll', .05, .006),
    ('PM1:DRY_DRIVE_2_LOAD', '2nd section drive load', '%', '2nd section drive group', 62, 3),
    ('PM1:REEL_MOIST', 'Reel moisture (QCS)', '%', 'QCS scanner', 7.5, .3),
    ('PM1:REEL_BW', 'Reel basis weight (QCS)', 'lb/MSF', 'QCS scanner', 0, .25),
    ('PM1:SPEED', 'Machine speed', 'fpm', 'PM1 Reel', 0, 5),
    ('PM1:BREAKS', 'Sheet break counter', 'count', 'PM1 Reel', 0, 0),
]

def pi_tags(equip):
    by_name = {e['name']: e for e in equip}
    rows = []
    for tag, desc, units, asset, mean, sigma in TAGS:
        e = by_name[asset]
        rows.append(dict(tag=tag, description=desc, units=units, asset_no=e['asset_no'], section=e['section'],
                         position_id=e['position_id'], mean=mean if mean else 'by grade', sigma=sigma, bonvoy_sigma=3))
    return rows


# ───────────────────────── Write / check ─────────────────────────
def build():
    outs = outages(); equip = equipment()
    return {
        'outages.csv': outs,
        'grade_schedule.csv': grade_schedule(outs),
        'crew_schedule.csv': crew_schedule(),
        'roster.csv': [dict(id=i, name=n, role=r, crew=c) for i, n, r, c in ROSTER],
        'vendors.csv': [dict(id=i, name=n, scope=s, rep=r) for i, n, s, r in VENDORS],
        'equipment.csv': equip,
        'pi_tags.csv': pi_tags(equip),
    }

def to_csv(rows):
    f = io.StringIO(); w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
    return f.getvalue()

def validate(data):
    """Backbone sanity plus every storyline's references. Returns a list of problems."""
    errs = []
    # crews: exactly one day crew and one night crew, every crew works
    for r in data['crew_schedule.csv']:
        if r['day_crew'] == r['night_crew']: errs.append(f"crew clash {r['date']}")
    # grade changes: 4–5 a week on average
    runs = [r for r in data['grade_schedule.csv'] if r['grade'] != 'DOWN']
    per_week = (len(runs) - 1) / (days(YEAR_START, YEAR_END) / 7)
    if not 3.8 <= per_week <= 5.4: errs.append(f'grade changes {per_week:.2f}/week, want 4–5')
    # names are unique
    names = [r['name'] for r in data['roster.csv']] + [r['rep'] for r in data['vendors.csv']]
    if len(names) != len(set(names)): errs.append('duplicate person names')
    # storylines
    try:
        import yaml
    except ImportError:
        return errs + ['pip install pyyaml to check storylines']
    names = {e['name'] for e in data['equipment.csv']}
    positions = {e['position_id'] for e in data['equipment.csv'] if e['position_id']}
    tags = {t['tag'] for t in data['pi_tags.csv']}
    out_ids = {o['id'] for o in data['outages.csv']}
    people = {r['id'] for r in data['roster.csv']}
    vendors = {v['id'] for v in data['vendors.csv']}
    SOURCES = {'pi', 'bonvoy', 'bus', 'rcfa', 'teams', 'jde', 'vendor', 'drawing', 'mm'}
    files = sorted(f for f in os.listdir(STORIES) if f.endswith('.yaml'))
    if not files: errs.append('no storylines')
    for fn in files:
        s = yaml.safe_load(open(os.path.join(STORIES, fn)))
        where = f'storylines/{fn}'
        for k in ('id', 'title', 'summary', 'assets', 'timeline', 'demo_questions'):
            if k not in s: errs.append(f'{where}: missing {k}')
        for a in s.get('assets', []):
            if a not in names: errs.append(f'{where}: unknown asset "{a}"')
        for p in s.get('positions', []):
            if p not in positions: errs.append(f'{where}: unknown position "{p}"')
        for t in s.get('pi_tags', []):
            if t not in tags: errs.append(f'{where}: unknown Pi tag "{t}"')
        for o in s.get('outages', []):
            if o not in out_ids: errs.append(f'{where}: unknown outage "{o}"')
        for p in s.get('people', []):
            if p not in people: errs.append(f'{where}: unknown person "{p}"')
        for v in s.get('vendors', []):
            if v not in vendors: errs.append(f'{where}: unknown vendor "{v}"')
        last = None
        for ev in s.get('timeline', []):
            d = ev.get('date'); d = d if isinstance(d, dt.date) else D(str(d))
            if not YEAR_START <= d <= YEAR_END: errs.append(f'{where}: {d} is outside the demo year')
            if last and d < last: errs.append(f'{where}: timeline out of order at {d}')
            last = d
            for src in ev.get('sources', []):
                if src not in SOURCES: errs.append(f'{where}: unknown source "{src}" on {d}')
        for q in s.get('demo_questions', []):
            if not q.get('q') or not q.get('expect'): errs.append(f'{where}: demo question needs q and expect')
    return errs

if __name__ == '__main__':
    data = build()
    errs = validate(data)
    if '--check' in sys.argv:
        stale = [n for n, rows in data.items()
                 if not os.path.exists(os.path.join(OUT, n)) or open(os.path.join(OUT, n)).read() != to_csv(rows)]
        if stale: errs.append('stale CSVs (run python3 tools/demo-data/backbone.py): ' + ', '.join(stale))
        for e in errs: print('FAIL', e)
        if errs: sys.exit(1)
        print(f'backbone ok — {len(data["equipment.csv"])} assets, {len(data["pi_tags.csv"])} Pi tags, '
              f'{len(data["outages.csv"])} outages, {len(os.listdir(STORIES))} storylines')
        sys.exit(0)
    os.makedirs(OUT, exist_ok=True)
    for n, rows in data.items():
        open(os.path.join(OUT, n), 'w').write(to_csv(rows))
    for e in errs: print('WARN', e)
    print('wrote', ', '.join(f'{n} ({len(r)})' for n, r in data.items()))
