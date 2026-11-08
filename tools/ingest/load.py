"""Load mill files into the MM LLM tables of one organization.

    # into Supabase (rows, originals and embeddings all through the mm-llm-ingest edge function)
    MM_INGEST_TOKEN=... python3 tools/ingest/load.py --source demo-data/out --backbone demo-data/backbone \\
        --url https://<project>.supabase.co --key <publishable key> [--files] [--embed]

    # into a local Postgres (tests)
    python3 tools/ingest/load.py --source demo-data/out --backbone demo-data/backbone --dsn "host=... dbname=..." --token <token>

    --dry-run   parse everything and print row counts, send nothing

The token comes from an admin running  select public.mm_llm_new_ingest_token('<org name>', <hours>);  in the SQL
editor. It decides the organization; rows never carry an org id. A load replaces the organization's MM LLM rows.
"""
import argparse, base64, glob, json, os, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importers as I

ORDER = ['equipment', 'pi_tags', 'outages', 'bus_items', 'work_orders', 'actions', 'rcfa', 'envoy', 'pi_series',
         'documents', 'doc_chunks', 'downtime', 'production_daily', 'position_runs', 'ingest_files']
BATCH = {'pi_series': 1000, 'doc_chunks': 300, 'documents': 200}

def collect(source, backbone_dir, log=print):
    equipment, tags, outages = I.backbone(backbone_dir)
    tg = I.Tagger(equipment)
    g = lambda pat: sorted(glob.glob(os.path.join(source, pat)))
    t = {}; files = {}
    t['equipment'], t['pi_tags'], t['outages'] = equipment, tags, outages
    bus = g('bus/*.xlsx'); t['bus_items'] = I.bus_sheets(bus, tg); files.update({p: 'bus' for p in bus})
    jde = g('jde/*.csv'); t['work_orders'] = I.jde_exports(jde, tg); files.update({p: 'jde' for p in jde})
    pl = g('teams/*.csv'); t['actions'] = I.planner_exports(pl, tg); files.update({p: 'planner' for p in pl})
    rl = (g('rcfa/RCFA_log_*.csv') or [os.path.join(source, 'rcfa', 'RCFA_log_PM1.csv')])[0]; t['rcfa'] = I.rcfa_log(rl, tg); files[rl] = 'rcfa_log'
    ev = g('envoy/*.csv'); t['envoy'] = I.envoy_reports(ev, tg); files.update({p: 'envoy' for p in ev})
    # actions inherit the asset of the RCFA they belong to, or of the WO named in their description
    rc = {aid: r for r in t['rcfa'] for aid in r['action_ids']}
    wo = {w['wo_no']: w for w in t['work_orders']}
    for a in t['actions']:
        src = rc.get(a['task_id'])
        if not src and a.get('description'):
            m = __import__('re').search(r'WO (\d+)', a['description']); src = wo.get(m.group(1)) if m else None
        if src and not a['asset_no']: a['asset_no'], a['position_id'] = src['asset_no'], src['position_id']
    t['pi_series'] = I.pi_series(os.path.join(source, 'pi'))
    # step 05: downtime events, daily production and position runs (Sim Mill has them; Demo Mill doesn't yet)
    dtp = g('downtime/*.csv'); t['downtime'] = I.downtime_files(dtp, tg); files.update({p: 'downtime' for p in dtp})
    prp = g('production/*.csv'); t['production_daily'] = I.production_files(prp); files.update({p: 'production' for p in prp})
    psp = g('positions/*.csv'); t['position_runs'] = I.position_run_files(psp); files.update({p: 'position_runs' for p in psp})
    t['records'] = I.record_files(os.path.join(source, 'records'))
    log('parsing documents (OCR for scanned ones)…')
    t['documents'], t['doc_chunks'] = I.documents(os.path.join(source, 'docs'), tg, source)
    for d in t['documents']: files[os.path.join(source, d['file_path'])] = 'document'
    for p in g('docs/reference/tables/*.csv'): files[p] = 'reference_table'
    counts = {}
    for name, rows in (('bus_items', t['bus_items']), ('work_orders', t['work_orders']), ('actions', t['actions']), ('envoy', t['envoy']),
                       ('downtime', t['downtime']), ('production_daily', t['production_daily']), ('position_runs', t['position_runs'])):
        for r in rows: counts[r['source_file']] = counts.get(r['source_file'], 0) + 1
    t['ingest_files'] = [dict(source_file=os.path.relpath(p, source).replace(os.sep, '/'), kind=k, rows=counts.get(os.path.basename(p)))
                         for p, k in sorted(files.items())]
    return t, sorted(files)


class Supabase:
    def __init__(self, url, key, token):
        self.url, self.key, self.token = url.rstrip('/'), key, token
    def _post(self, path, body, headers=None, tries=4):
        data = json.dumps(body).encode()
        for i in range(tries):
            req = urllib.request.Request(self.url + path, data=data, method='POST',
                                         headers={'apikey': self.key, 'Content-Type': 'application/json', **(headers or {})})
            try:
                with urllib.request.urlopen(req, timeout=120) as r: return json.loads(r.read() or b'null')
            except urllib.error.HTTPError as e:
                msg = e.read().decode()[:400]
                if e.code < 500 or i == tries - 1: raise RuntimeError(f'{path}: HTTP {e.code} {msg}')
            except urllib.error.URLError:
                if i == tries - 1: raise
            time.sleep(2 * (i + 1))
    def ingest(self, table, rows, mode='upsert'):
        return self.fn(dict(action='rows', table=table, rows=rows, mode=mode))['rows']
    def fn(self, body):
        return self._post('/functions/v1/mm-llm-ingest', body, {'x-mm-ingest-token': self.token})

class Local:
    def __init__(self, dsn, token):
        import psycopg
        self.c = psycopg.connect(dsn, autocommit=True); self.token = token
    def ingest(self, table, rows, mode='upsert'):
        return self.c.execute('select public.mm_llm_ingest(%s, %s, %s::jsonb, %s)', (self.token, table, json.dumps(rows), mode)).fetchone()[0]

def push(target, tables, log=print):
    for name in reversed(ORDER): target.ingest(name, [], 'reset')
    for name in ORDER:
        rows = tables[name]; b = BATCH.get(name, 2000); n = 0
        for i in range(0, len(rows), b):
            n += target.ingest(name, rows[i:i + b]) or 0
        log(f'  {name:12s} {n:>8,} rows')
    # Machine Manager records (My Machine, Outage Planning, Consumables): only the tools the source has, each replaced whole
    for tool, rows in (tables.get('records') or {}).items():
        n = target.ingest(f'records:{tool}', [], 'reset') or 0
        for i in range(0, len(rows), 500): n += target.ingest(f'records:{tool}', rows[i:i + 500]) or 0
        log(f'  records:{tool:12s} {len(rows):>5,} records')

def upload_files(target, source, paths, log=print):
    for i, p in enumerate(paths):
        rel = os.path.relpath(p, source).replace(os.sep, '/')
        mime = ('application/pdf' if p.endswith('.pdf') else 'text/csv' if p.endswith('.csv') else
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if p.endswith('.xlsx') else
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        target.fn(dict(action='upload', path=rel, contentType=mime, data=base64.b64encode(open(p, 'rb').read()).decode()))
        if (i + 1) % 100 == 0: log(f'  uploaded {i + 1}/{len(paths)}')
    log(f'  uploaded {len(paths)} files')

def embed(target, log=print):
    """Embeds in small batches; the edge function occasionally runs out of compute, so back off and shrink."""
    total, size, fails = 0, 6, 0
    while True:
        try:
            r = target.fn(dict(action='embed', limit=size))
        except RuntimeError as e:
            if 'WORKER_RESOURCE_LIMIT' not in str(e) or fails >= 8: raise
            fails += 1; size = max(1, size // 2); time.sleep(5 * fails); continue
        fails = 0; size = min(6, size + 1)
        total += r.get('embedded', 0)
        if not r.get('embedded'): break
    log(f'  embedded {total} chunks')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True); ap.add_argument('--backbone', required=True)
    ap.add_argument('--url'); ap.add_argument('--key'); ap.add_argument('--dsn'); ap.add_argument('--token')
    ap.add_argument('--files', action='store_true'); ap.add_argument('--embed', action='store_true'); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    tables, paths = collect(a.source, a.backbone)
    for k in ORDER: print(f'  {k:12s} {len(tables[k]):>8,} rows parsed')
    for k, v in tables['records'].items(): print(f'  records:{k:12s} {len(v):>5,} records parsed')
    if a.dry_run: sys.exit(0)
    token = a.token or os.environ.get('MM_INGEST_TOKEN') or sys.exit('need --token or MM_INGEST_TOKEN')
    target = Local(a.dsn, token) if a.dsn else Supabase(a.url, a.key, token)
    print('loading rows…'); push(target, tables)
    if a.files and not a.dsn: print('uploading originals…'); upload_files(target, a.source, paths)
    if a.embed and not a.dsn: print('embedding chunks…'); embed(target)
