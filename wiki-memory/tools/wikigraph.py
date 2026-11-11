"""Parse a wiki directory into pages + links + lint, for the graph, the upload and the size checks.
    python3 tools/wikigraph.py ORG_SLUG [--json out.json]
Lint: pages, links, redlinks, orphans, oversized (>20 KB), stubs, index gaps, uncited fact lines, wiki/source size ratio."""
import json, re, sys
from collections import Counter
from pathlib import Path

H = Path(__file__).resolve().parents[1]
CITE = re.compile(r'\[(?:WO|RCFA|Action|Shift Report|Production Report|BUS|Bonvoy|DOC|position_life|downtime|outage|source)[^\]]*\]', re.I)
ROOT_TYPES = {'_index': 'root', 'watchlist': 'root', 'SKILL': 'root', '_schema': 'root'}


def front(t):
    m = re.match(r'^---\n(.*?)\n---\n?', t, re.S)
    meta = {}
    if m:
        for line in m.group(1).splitlines():
            k, _, v = line.partition(':')
            if v.strip(): meta[k.strip()] = v.strip()
    return meta, (t[m.end():] if m else t)


def parse(org):
    W = H / 'wiki' / org
    pages = {}
    for p in sorted(W.rglob('*.md')):
        if p.name == '_schema.md': continue
        t = p.read_text(errors='replace'); meta, body = front(t)
        if body.strip().startswith('MOVED TO'): continue
        slug = p.stem
        aliases = re.findall(r'"([^"]+)"', meta.get('aliases', ''))
        typ = ROOT_TYPES.get(slug) or meta.get('type') or (meta.get('metadata', '') if 'type' in meta.get('metadata', '') else '') or ('topic' if 'topics' in p.parts else 'entity')
        typ = typ.split('|')[0].strip().lower() or 'entity'
        lines = [l for l in body.splitlines() if l.strip().startswith(('-', '*')) and len(l.strip()) > 3]
        pages[slug] = {'slug': slug, 'path': str(p.relative_to(W)), 'type': typ, 'title': meta.get('title') or slug.replace('-', ' '),
                       'description': meta.get('description', ''), 'aliases': aliases, 'body': t, 'bytes': len(t.encode()),
                       'citations': len(CITE.findall(body)), 'fact_lines': len(lines),
                       'uncited': sum(1 for l in lines if not CITE.search(l)), 'conflicts': len(re.findall(r'CONFLICT', body)),
                       'open_q': len(re.findall(r'(?i)open question|unresolved', body))}
    links = Counter()
    for s, pg in pages.items():
        for tgt in re.findall(r'\[\[([^\]|#]+)', pg['body']):
            tgt = tgt.strip().lower()
            if tgt != s: links[(s, tgt)] += 1
    edges = [{'from': a, 'to': b, 'weight': w, 'redlink': b not in pages} for (a, b), w in links.items()]
    return pages, edges


def lint(org, pages, edges):
    src = sum(f.stat().st_size for f in (H / 'corpus/batches' / org).glob('*.txt'))
    inbound = Counter(e['to'] for e in edges if not e['redlink'])
    idx = pages.get('_index', {}).get('body', '')
    return {'pages': len(pages), 'links': sum(1 for e in edges if not e['redlink']), 'redlinks': sum(1 for e in edges if e['redlink']),
            'redlink_targets': len({e['to'] for e in edges if e['redlink']}),
            'orphans': sorted(s for s in pages if not inbound[s] and pages[s]['type'] != 'root')[:40],
            'n_orphans': sum(1 for s in pages if not inbound[s] and pages[s]['type'] != 'root'),
            'oversized': sorted(((s, p['bytes']) for s, p in pages.items() if p['bytes'] > 20000), key=lambda x: -x[1]),
            'not_indexed': sorted(s for s in pages if pages[s]['type'] != 'root' and f'[[{s}]]' not in idx)[:40],
            'n_not_indexed': sum(1 for s in pages if pages[s]['type'] != 'root' and f'[[{s}]]' not in idx),
            'fact_lines': sum(p['fact_lines'] for p in pages.values()), 'uncited_lines': sum(p['uncited'] for p in pages.values()),
            'conflicts': sum(p['conflicts'] for p in pages.values()),
            'wiki_bytes': sum(p['bytes'] for p in pages.values()), 'source_bytes': src,
            'ratio': round(sum(p['bytes'] for p in pages.values()) / max(1, src), 3),
            'types': Counter(p['type'] for p in pages.values()).most_common()}


if __name__ == '__main__':
    org = sys.argv[1]
    pages, edges = parse(org)
    L = lint(org, pages, edges)
    print(json.dumps({k: v for k, v in L.items() if k not in ('orphans', 'not_indexed')}, indent=1))
    if '--json' in sys.argv:
        out = Path(sys.argv[sys.argv.index('--json') + 1])
        nodes = [{k: p[k] for k in ('slug', 'type', 'title', 'description', 'bytes', 'citations', 'conflicts')} for p in pages.values()]
        out.write_text(json.dumps({'org': org, 'lint': {k: v for k, v in L.items() if k not in ('orphans', 'not_indexed', 'oversized')},
                                   'nodes': nodes, 'edges': [e for e in edges]}, separators=(',', ':')))
        print('wrote', out, out.stat().st_size // 1024, 'KB')
