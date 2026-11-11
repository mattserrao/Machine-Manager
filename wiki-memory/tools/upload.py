"""Upload a trained wiki + memory to Supabase (llm.wiki_* / llm.memory) for one org, and write the graph JSON for the app.
    python3 tools/upload.py sim-mill|demodemo-rag --checkpoint ck1 [--live]"""
import json, sys, urllib.request
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from wikigraph import parse, lint, front   # noqa: E402
H = Path(__file__).resolve().parents[1]; REPO = Path('/home/claude/machine-manager')
C = json.loads((H / '.secrets/config.json').read_text())
URL = C['url'].replace('mm-mcp-dev', 'mm-dev-wiki-upload')
ORG = {'sim-mill': 'Sim Mill', 'demodemo-rag': 'Demodemo RAG'}
def post(body):
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), method='POST', headers={'content-type': 'application/json', 'x-mm-ingest-token': C['tokens'][ORG[org]]})
    try: return json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e: sys.exit(f'{body.get("action")}: HTTP {e.code} {e.read()[:300]}')
org = sys.argv[1]; ck = sys.argv[sys.argv.index('--checkpoint') + 1]
pages, edges = parse(org); L = lint(org, pages, edges)
b = post({'action': 'build', 'checkpoint': ck, 'lint': {k: v for k, v in L.items() if k not in ('orphans', 'not_indexed')}, 'note': 'wiki-memory training run'})['build_id']
rows = [{k: p[k] for k in ('slug', 'path', 'type', 'title', 'description', 'aliases', 'body', 'bytes', 'citations', 'conflicts', 'open_q')} for p in pages.values()]
n = 0
for i in range(0, len(rows), 25): n += post({'action': 'pages', 'build_id': b, 'pages': rows[i:i + 25]})['pages']
links = [{'from_slug': e['from'], 'to_slug': e['to'], 'weight': e['weight'], 'is_redlink': e['redlink']} for e in edges]
m = 0
for i in range(0, len(links), 500): m += post({'action': 'links', 'build_id': b, 'links': links[i:i + 500]})['links']
mem = []
for p in sorted((H / 'memory' / org).glob('*.md')):
    t = p.read_text(); meta, body = front(t)
    mem.append({'topic': p.stem.lower(), 'title': meta.get('description', p.stem), 'body': t, 'kind': 'lesson', 'source': f'wiki-memory training {ck}'})
k = post({'action': 'memory', 'items': mem})['memory']
if '--live' in sys.argv: post({'action': 'live', 'build_id': b})
out = REPO / 'demo-data/wiki'; out.mkdir(parents=True, exist_ok=True)
nodes = [{k2: p[k2] for k2 in ('slug', 'type', 'title', 'description', 'bytes', 'citations', 'conflicts')} for p in pages.values()]
(out / f'{org}.json').write_text(json.dumps({'org': ORG[org], 'checkpoint': ck, 'build_id': b,
    'lint': {k2: v for k2, v in L.items() if k2 not in ('orphans', 'not_indexed', 'oversized', 'types')}, 'nodes': nodes, 'edges': edges}, separators=(',', ':')))
print(f'{org}: build {b}, {n} pages, {m} links, {k} memory topics; graph json {(out / f"{org}.json").stat().st_size // 1024} KB')
