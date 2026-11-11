"""Pull every corpus table for both orgs into corpus/raw/<org>/<table>.json via mm-dev-export."""
import json, urllib.request, sys
from pathlib import Path
H = Path(__file__).resolve().parents[1]
C = json.loads((H / '.secrets/config.json').read_text())
URL = C['url'].replace('mm-mcp-dev', 'mm-dev-export')
TABLES = {'Sim Mill': ['documents', 'doc_chunks', 'reports', 'work_orders', 'bus_items', 'rcfa', 'actions', 'downtime', 'position_runs',
                       'outages', 'equipment', 'bonvoy', 'bonvoy_reports', 'pi_tags', 'production_daily'],
          'Demodemo RAG': ['documents', 'doc_pages']}
for org, tables in TABLES.items():
    d = H / 'corpus/raw' / org.lower().replace(' ', '-'); d.mkdir(parents=True, exist_ok=True)
    for t in tables:
        rows, off = [], 0
        while True:
            req = urllib.request.Request(URL, data=json.dumps({'table': t, 'offset': off, 'limit': 1000}).encode(),
                  headers={'content-type': 'application/json', 'x-mm-ingest-token': C['tokens'][org]}, method='POST')
            r = json.load(urllib.request.urlopen(req, timeout=120))
            if 'error' in r: sys.exit(f'{org} {t}: {r["error"]}')
            rows += r['rows']; off += 1000
            if len(r['rows']) < 1000: break
        (d / f'{t}.json').write_text(json.dumps(rows))
        print(f'{org:13} {t:16} {len(rows):6} rows  {len(json.dumps(rows))//1024:6} KB', flush=True)
