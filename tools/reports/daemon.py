"""The report daemon: one idempotent reconcile loop for every report type in registry.yaml.

    reconcile(producer, outbox, first_day, last_day, through)     generate + validate + submit what's due and missing
    python3 tools/reports/daemon.py push --outbox <dir> --dsn ... --token ...      ingest + extract + index (local Postgres)
    python3 tools/reports/daemon.py push --outbox <dir> --url ... --key ... --token ...   (Supabase, through mm-llm-ingest)
    python3 tools/reports/daemon.py status --outbox <dir>                          counts by type and state

A producer is anything with  generate(rtype, mill_day, shift) -> envelope  (lifecycle.py). Sim Mill's is
tools/sim-mill/simmill/reports.py (run in batch by run.py over the whole year); a live job would run the same loop each
shift with `through` = now, and a real mill's producer would read a supervisor's form or the MES instead.

Running it again changes nothing: a period that already has a submitted report is skipped, a report that failed
validation is written as `failed` (with the error) and is generated again on the next run. Ingest upserts by report id
and extraction only picks reports that are `ingested`, so pushing twice is safe too.
"""
import argparse, collections, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lifecycle as L

def reconcile(producer, outbox, first_day, last_day, through=None, types=None, at=None, log=print):
    n = collections.Counter()
    for rtype in (types or L.REGISTRY['types']):
        for day, shift in L.periods(rtype, first_day, last_day, through):
            rid = L.report_id(rtype, producer.machine, day.isoformat(), shift)
            p = L.path_for(outbox, dict(type=rtype, mill_day=day.isoformat(), report_id=rid))
            if os.path.exists(p) and json.load(open(p)).get('status') != 'failed':
                n['skipped'] += 1; continue
            rep = producer.generate(rtype, day, shift)
            L.advance(rep, 'generated', at)
            try:
                L.validate(rep)
            except L.InvalidReport as e:
                L.advance(rep, 'failed', at, str(e)); L.write(outbox, rep); n['failed'] += 1; continue
            L.advance(rep, 'submitted', at); L.write(outbox, rep); n[rtype] += 1
    log('reports: ' + ', '.join(f'{k} {v}' for k, v in sorted(n.items())))
    return n

def outbox_reports(outbox, status='submitted'):
    out = []
    for p in sorted(glob.glob(os.path.join(outbox, '*', '*', '*.json'))):
        r = json.load(open(p))
        if status is None or r.get('status') == status: out.append((p, r))
    return out

def rows(outbox, root=None):
    """llm.reports rows for every submitted report in the outbox (file_path relative to `root`, the load's source)."""
    out = []
    for p, r in outbox_reports(outbox):
        out.append(dict(report_id=r['report_id'], type=r['type'], schema_version=r.get('schema', L.SCHEMA), machine=r['machine'],
                        period_start=r['period_start'], period_end=r['period_end'], mill_day=r['mill_day'], shift=r.get('shift'),
                        crew=r.get('crew'), author=(r.get('author') or {}).get('name'), author_role=(r.get('author') or {}).get('role'),
                        source=r.get('source'), body=r['body'], text=r['text'], history=r.get('history', []),
                        file_path=os.path.relpath(p, root or outbox).replace(os.sep, '/')))
    return out

def push(target, outbox, root=None, log=print):
    """Ingest the outbox's submitted reports (upsert) and process them (extract + index). `target` is load.py's Local or
    Supabase. Returns the processing counts."""
    rs = rows(outbox, root); n = 0
    for i in range(0, len(rs), 300): n += target.ingest('reports', rs[i:i + 300]) or 0
    log(f'  reports      {n:>8,} ingested')
    done = process(target)
    log(f"  reports      {done.get('extracted', 0):>8,} extracted and indexed, {done.get('failed', 0)} failed")
    return done

def process(target, batch=500):
    total = collections.Counter()
    while True:
        r = target.process_reports(batch) or {}
        for k, v in r.items(): total[k] += v
        if not r.get('picked'): return total

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd', choices=['push', 'status'])
    ap.add_argument('--outbox', required=True); ap.add_argument('--dsn'); ap.add_argument('--url'); ap.add_argument('--key'); ap.add_argument('--token')
    a = ap.parse_args()
    if a.cmd == 'status':
        c = collections.Counter((r['type'], r.get('status')) for _, r in outbox_reports(a.outbox, None))
        for (t, s), v in sorted(c.items()): print(f'{t:12s} {s:10s} {v:>6}')
        sys.exit(0)
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ingest'))
    import load
    token = a.token or os.environ.get('MM_INGEST_TOKEN') or sys.exit('need --token or MM_INGEST_TOKEN')
    target = load.Local(a.dsn, token) if a.dsn else load.Supabase(a.url, a.key, token)
    push(target, a.outbox)
