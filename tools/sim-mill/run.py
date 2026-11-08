"""Sim Mill: one seeded year of a recycled-board mill (The Paper Mill's own), as every Machine Manager source.

    python3 tools/sim-mill/run.py              # generate: demo-data/sim-mill/backbone/ (committed) and demo-data/sim-mill/out/
    python3 tools/sim-mill/run.py --check      # generate to a temp folder and check counts, targets and the planted faults
    python3 tools/sim-mill/run.py --seed 7     # another year (the answer key is written for the default seed)
    python3 tools/sim-mill/run.py --cycles 2   # the same year moved forward 2 x 6 weeks (84 days)
    python3 tools/sim-mill/run.py --auto       # as many whole 6-week cycles as have passed, so the year ends just before today

The year is written for Nov 1 2025 - Oct 31 2026 (the base year). Rolling moves every date by whole outage cycles, so
the outage grid, weekdays and the planted faults keep their places; the answer key (answers/answer_key.base.json) is
rendered to answers/answer_key.json with its dates moved the same way. out/_truth/roll.json says which cycle was built.

Then load it like Demo Mill (an ingest token for the 'Sim Mill' org):
    python3 tools/ingest/load.py --source demo-data/sim-mill/out --backbone demo-data/sim-mill/backbone --url ... --key ... [--files] [--embed]
"""
import argparse, collections, csv, datetime as dt, glob, json, os, shutil, sys, tempfile, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BASE_END, CADENCE = dt.date(2026, 11, 1), 42          # the base year's last day + 1, and the outage cycle
def cycles_for(today):
    """Whole 6-week cycles to move the base year so its last day is before `today` (0 until the base year is past)."""
    return max(0, (today - BASE_END).days // CADENCE)
# The roll is read when simmill.base is imported, so settle it from the command line first.
if '--auto' in sys.argv: os.environ['SIM_SHIFT_CYCLES'] = str(cycles_for(dt.date.today()))
elif '--cycles' in sys.argv: os.environ['SIM_SHIFT_CYCLES'] = sys.argv[sys.argv.index('--cycles') + 1]

from simmill import base, model, process, records, emit, docs, mm_records
from simmill.base import Y0, TODAY, DATA, PLANTS, MACHINE, D, B, BT, md

def generate(out, seed=model.SEED, log=print):
    t0 = time.time()
    if os.path.exists(out): shutil.rmtree(out)
    base.write_backbone(os.path.join(DATA, 'backbone'))
    m = model.build(seed); log(f'model: {len(m["events"])} events, {sum(len(r) for r in m["runs"].values())} position runs ({time.time() - t0:.1f}s)')
    p = process.build(m); log(f'process: {len(p["OUT"])} tags x {base.H} h ({time.time() - t0:.1f}s)')
    rec = records.build(m, p); log(f'records: {len(rec["wos"])} WOs, {len(rec["actions"])} actions, {len(rec["issues"])} BUS issues, {len(rec["rcfas"])} RCFAs')
    emit.write_structured(m, rec, out)
    bus = emit.write_bus(m, rec, os.path.join(out, 'bus'))
    ev = emit.write_pi_envoy(m, p, out); log(f'pi + envoy written ({time.time() - t0:.1f}s)')
    emit.write_new_feeds(m, p, rec, out)
    man = docs.build(m, p, rec, out); log(f'documents: {len(man)} ({time.time() - t0:.1f}s)')
    mm_records.write(m, rec, out)
    emit.write_truth(m, rec, ev, out)
    json.dump(man, open(os.path.join(out, '_truth', 'documents.json'), 'w'), indent=1)
    roll = dict(cycles=base.SHIFT_CYCLES, shift_days=base.SHIFT.days, start=Y0.isoformat(), today=TODAY.isoformat(),
                next_outage=base.NEXT_OUTAGE['date'].isoformat(), seed=seed)
    json.dump(roll, open(os.path.join(out, '_truth', 'roll.json'), 'w'), indent=1)
    write_answer_key(out)
    log(f"roll: cycle {roll['cycles']} (+{roll['shift_days']} d), {roll['start']} to {roll['today']}, next outage {roll['next_outage']}")
    return dict(m=m, p=p, rec=rec, bus=bus, ev=ev, docs=man)

def month_facts(out):
    """The month-bucket facts the key quotes, from the production files the way mm_llm_production groups them
    (sum of breaks, mean of the daily kWh/t). Calendar months don't move with the roll, so these are read, not shifted."""
    by = collections.defaultdict(list)
    for fn in glob.glob(os.path.join(out, 'production', '*.csv')):
        for r in csv.DictReader(open(fn)):
            if Y0.isoformat() <= r['Mill Day'] <= TODAY.isoformat(): by[r['Mill Day'][:7]].append(r)
    brk = {m: sum(int(r['Sheet Breaks']) for r in rs) for m, rs in by.items()}
    kwh = {m: round(sum(float(r['Refining (kWh/t)']) for r in rs) / len(rs), 1) for m, rs in by.items()}
    bm = max(sorted(brk), key=lambda m: brk[m]); km = max(sorted(kwh), key=lambda m: kwh[m])
    name = lambda m: dt.date.fromisoformat(m + '-01').strftime('%B')
    return {'BRK_MONTH': bm, 'BRK_MONTH_NAME': name(bm), 'BRK_MONTH_N': str(brk[bm]),
            'KWH_MONTH': km, 'KWH_MONTH_NAME': name(km), 'KWH_MONTH_VAL': f'{kwh[km]:.1f}'}

def write_answer_key(out):
    """answers/answer_key.json: the base-year key with every date moved by the roll (questions, expectations and checks),
    and the {{…}} month facts filled from this run's data."""
    d = os.path.join(DATA, 'answers'); key = json.load(open(os.path.join(d, 'answer_key.base.json')))
    facts = month_facts(out)
    def fill(s):
        s = base.tx(s)
        for k, v in facts.items(): s = s.replace('{{' + k + '}}', v)
        return s
    walk = lambda v: fill(v) if isinstance(v, str) else {k: walk(x) for k, x in v.items()} if isinstance(v, dict) else [walk(x) for x in v] if isinstance(v, list) else v
    key = walk(key); key['roll'] = dict(cycles=base.SHIFT_CYCLES, today=TODAY.isoformat(), start=Y0.isoformat())
    with open(os.path.join(d, 'answer_key.json'), 'w') as f: json.dump(key, f, indent=1, ensure_ascii=False); f.write('\n')


def check(g, out):
    fails = []
    ok = lambda cond, msg: (print(('PASS ' if cond else 'FAIL ') + msg), None if cond else fails.append(msg))
    m, rec, ev = g['m'], g['rec'], g['ev']
    yr = [e for e in m['events'] if Y0 <= e['start'].date() <= TODAY]
    c = collections.Counter(e['kind'] for e in yr)
    bpd = c['break'] / 365
    ok(1.0 <= bpd <= 3.0, f'sheet breaks {bpd:.2f}/day (target 1-3)')
    u = sum(1 for e in yr if e['kind'] == 'unplanned' and e['minutes'] > 60)
    ok(15 <= u <= 25, f'{u} unplanned stops over 1 h (target 15-25)')
    ok(10 <= len(rec['rcfas']) <= 20, f"{len(rec['rcfas'])} RCFAs (target 10-20)")
    ok(len([e for e in yr if e['cause'] == 'outage']) == 8, '8 outages in the year, 20 h each, on the 6-week grid')
    ok(all(e['minutes'] == 1200 for e in yr if e['cause'] == 'outage'), 'every outage is 20 h')
    ok(1000 <= len(rec['wos']) <= 2500, f"{len(rec['wos'])} work orders")
    days = sorted(g['bus']); n = [g['bus'][d] for d in days]
    ok(len(days) == 365 and sum(n) / len(n) >= 4, f'{len(days)} BUS sheets, {sum(n) / len(n):.1f} lines a day')
    names = set(base.BY_NAME)
    ok(all(w.asset['name'] in names for w in rec['wos']), 'every WO resolves to an asset in the register')
    ok(all(a.due >= a.created for a in rec['actions']), 'no action is due before it was created')
    od = [a for a in rec['actions'] if a.progress_at(TODAY) != 'Completed' and a.due < TODAY]
    ok(5 <= len(od) <= 25, f'{len(od)} overdue actions on {md(TODAY)}')
    flags = lambda tag: sorted(d for d, rows in ev.items() if any(r['Tag'] == f'{MACHINE}:{tag}' for r in rows))
    f1 = [d for d in flags('UHLE_P2T_VAC') if B('2026-05-01') <= d <= B('2026-05-19')]
    ok(len(f1) >= 3, f'F1: Envoy flags the 2nd press top Uhle vacuum before the felt change ({len(f1)} days, first {f1[:1]})')
    f2 = [d for d in flags('REEL_DRUM_DS_VIB') if d >= B('2026-08-01')]
    ok(len(f2) >= 15 and f2[0] <= B('2026-09-20'), f'F2: Envoy flags the reel drum DS bearing ({len(f2)} days, first {f2[:1]})')
    f3 = [d for d in flags('REF_B_SE') if d >= B('2026-10-01')]
    ok(len(f3) >= 5, f'F3: Envoy flags REF 2 specific energy in October ({len(f3)} days)')
    f5 = flags('DRY3_DP'); hit = [x for x in PLANTS['F5']['events'] if any(dt.datetime.fromisoformat(x['start']).date() - dt.timedelta(days=5) <= d <= dt.datetime.fromisoformat(x['start']).date() for d in f5)]
    ok(len(hit) >= 2, f'F5: Envoy flags the 3rd section syphon differential before {len(hit)} of 3 joint leaks')
    ok(not any(r['story'] == 'F5' for r in rec['rcfas']), 'F5: no RCFA for the 3rd section joint leaks')
    ok(any(r['story'] == 'F1' for r in rec['rcfas']) and any(r['story'] == 'F4' for r in rec['rcfas']), 'F1 and F4 have RCFAs')
    f4 = [a for a in rec['actions'] if a.story == 'F4' and a.progress_at(TODAY) != 'Completed' and a.due < TODAY]
    ok(len(f4) == 1, 'F4: the wad-detector action is overdue')
    nx = [w for w in rec['wos'] if w.outage_at(TODAY) == base.NEXT_OUTAGE['id']]
    ok(any('reel drum DS bearing' in w.desc and w.status_at(TODAY) == 45 for w in nx), f"F2: {md(base.NEXT_OUTAGE['date'])} scope has the reel drum bearing WO, waiting on parts")
    ok(sum(1 for w in nx if 'refiner plates' in w.desc) == 2, f"F3: both refiner plate changes in the {md(base.NEXT_OUTAGE['date'])} scope")
    # Envoy is backed by Pi: re-derive one month from the written CSVs
    vals = {}
    for fn in sorted(glob.glob(os.path.join(out, 'pi', 'hourly', '*.csv'))):
        for r in csv.DictReader(open(fn)):
            for k, v in r.items():
                if k != 'Timestamp': vals.setdefault(k, []).append(v)
    ok(len(vals[f'{MACHINE}:SPEED']) == (base.Y1 - Y0).days * 24, 'Pi hourly covers the year')
    p = g['p']; i0 = int(base.hidx(dt.datetime.combine(Y0, dt.time(0))))
    same = all(abs(float(vals[t][h - i0] or 'nan') - p['OUT'][t][h]) < 1e-6 or (vals[t][h - i0] == '') for t in list(base.TAG)[:10] for h in range(i0, i0 + 500))
    ok(same, 'Pi CSVs hold the model values the Envoy reports were derived from')
    ok(os.path.exists(os.path.join(out, 'records', 'mymachine.json')), 'My Machine, Outage Planning and Consumables records written')
    mm = json.load(open(os.path.join(out, 'records', 'mymachine.json')))
    ok(len([k for k in mm if k.startswith('item:')]) == len(base.POS_NAME), f'My Machine: one item per position ({len(base.POS_NAME)})')
    print(f"{len(fails)} failing" if fails else 'all Sim Mill checks pass')
    return not fails


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--check', action='store_true'); ap.add_argument('--seed', type=int, default=model.SEED)
    ap.add_argument('--cycles', type=int, help='move the year forward this many 6-week cycles'); ap.add_argument('--auto', action='store_true')
    ap.add_argument('--out', default=os.path.join(DATA, 'out'))
    a = ap.parse_args()
    if a.check:
        out = tempfile.mkdtemp(prefix='simmill-')
        g = generate(out, a.seed); sys.exit(0 if check(g, out) else 1)
    generate(a.out, a.seed)
