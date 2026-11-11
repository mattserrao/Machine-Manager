"""Final one-off API run: mm-llm-ask-dev (Sonnet, the API harness) on held-out + new questions, judged by judge v2. PAID.
    python3 tools/final_run.py --label LABEL [--no-wiki] [--split heldout,new] [--workers 3]"""
import argparse, concurrent.futures as cf, json, sys, urllib.request, urllib.error
from pathlib import Path
H = Path(__file__).resolve().parents[1]; REPO = Path('/home/claude/machine-manager')
sys.path.insert(0, str(REPO / 'tools/ingest'))
from ask_demo import grade   # noqa: E402
C = json.loads((H / '.secrets/config.json').read_text()); BASE = C['url'].rsplit('/', 1)[0]
def post(url, tok, body, timeout=400):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method='POST', headers={'content-type': 'application/json', 'x-mm-ingest-token': tok})
    try: return json.load(urllib.request.urlopen(req, timeout=timeout))
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read())
        except Exception: return {'error': f'HTTP {e.code}'}
    except Exception as e: return {'error': str(e)}
ap = argparse.ArgumentParser(); ap.add_argument('--label', required=True); ap.add_argument('--no-wiki', action='store_true')
ap.add_argument('--split', default='heldout,new'); ap.add_argument('--workers', type=int, default=3); ap.add_argument('--only', nargs='*', default=[])
a = ap.parse_args(); splits = a.split.split(',')
qs = []
if 'heldout' in splits: qs += [q for q in json.loads((REPO / 'autoresearch/questions.json').read_text())['questions'] if q['split'] == 'heldout']
if 'new' in splits: qs += json.loads((H / 'eval/new_questions.json').read_text())['questions']
if a.only: qs = [q for q in qs if q['id'] in a.only]
demo = {k['id']: k for k in json.loads((REPO / 'demo-data/sim-mill/answers/answer_key.json').read_text())['questions']}
tok = C['tokens']['Sim Mill']
start = post(f'{BASE}/mm-llm-eval', tok, {'action': 'start', 'round': 20, 'label': a.label, 'sha': 'wiki-memory', 'split': a.split,
             'change': 'final API run, ' + ('no wiki/memory' if a.no_wiki else 'wiki + memory'), 'answer_model': 'claude-sonnet-5-5'})
if 'run_id' not in start: sys.exit(f'start failed: {start}')
run = start['run_id']; print(f'eval run {run}: {len(qs)} questions; spent so far ${start["spent"]:.2f}', flush=True)
out = {}
def one(q):
    r = post(f'{BASE}/mm-llm-ask-dev', C['tokens'][q['org']], {'question': q['question'], 'eval': True, **({'no_wiki': True} if a.no_wiki else {})})
    if r.get('error') and 'answer' not in r: r = {'status': 'error', 'answer': r['error']}
    auto = grade(demo[q['ref']], r) if q.get('ref') and r.get('status') == 'ok' else []
    g = post(f'{BASE}/mm-llm-eval', tok, {'action': 'judge', 'run_id': run, 'q': q, 'result': r, 'auto': auto})
    kn = sum(1 for t in r.get('trace', []) if t['tool'].startswith(('wiki_', 'memory_')))
    out[q['id']] = {'q': q['id'], 'section': q['section'], 'split': q['split'], 'score': g.get('score'), 'notes': g.get('notes') or g.get('error'),
                    'cost': (g.get('answer_cost') or 0) + (g.get('judge_cost') or 0), 'knowledge_calls': kn, 'calls': len(r.get('trace', [])),
                    'usage': r.get('usage'), 'answer': r.get('answer'), 'citations': r.get('citations')}
    print(f"{q['id']:5} {q['split']:7} {g.get('score','ERR'):>5}  ${out[q['id']]['cost']:.3f}  calls {len(r.get('trace',[]))} (wiki/mem {kn})  {str(out[q['id']]['notes'])[:110]}", flush=True)
with cf.ThreadPoolExecutor(a.workers) as ex: list(ex.map(one, qs))
post(f'{BASE}/mm-llm-eval', tok, {'action': 'finish', 'run_id': run})
d = H / 'runs/final'; d.mkdir(parents=True, exist_ok=True)
by = {}
for v in out.values():
    if isinstance(v['score'], (int, float)): by.setdefault(v['section'] if v['split'] != 'new' else 'new', []).append(v['score'])
summ = {'eval_run': run, 'label': a.label, 'by': {k: round(sum(x) / len(x), 1) for k, x in by.items()},
        'mean': round(sum(sum(x) for x in by.values()) / max(1, sum(len(x) for x in by.values())), 1), 'cost': round(sum(v['cost'] for v in out.values()), 3)}
(d / f'{a.label}.json').write_text(json.dumps({'summary': summ, 'results': out}, indent=1))
print(json.dumps(summ))
