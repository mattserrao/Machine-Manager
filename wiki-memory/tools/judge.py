"""Judge one answering pass with the pinned API judge (mm-llm-eval, judge-v2) — PAID: ~$0.02-0.03 per answer.
    python3 tools/judge.py CK REP --label LABEL [--round N] [--questions eval/train.json] [--change TEXT]
For each runs/CK/REP/<qid>/answer.md: the citation check + trace come from mm-mcp-dev /check (the MCP call log of that run),
then mm-llm-eval scores it (answer cost 0: the answer came from a subagent). Results: llm.eval_runs / eval_results and
runs/CK/REP/results.json."""
import argparse, concurrent.futures as cf, json, sys, urllib.request, urllib.error
from pathlib import Path
H = Path(__file__).resolve().parents[1]; REPO = Path('/home/claude/machine-manager')
sys.path.insert(0, str(REPO / 'tools/ingest'))
from ask_demo import grade   # noqa: E402
C = json.loads((H / '.secrets/config.json').read_text())
BASE = C['url'].rsplit('/', 1)[0]

def post(url, token, body, timeout=300):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method='POST',
          headers={'content-type': 'application/json', 'x-mm-ingest-token': token})
    try: return json.load(urllib.request.urlopen(req, timeout=timeout))
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read())
        except Exception: return {'error': f'HTTP {e.code}'}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('ck'); ap.add_argument('rep'); ap.add_argument('--label', required=True)
    ap.add_argument('--round', type=int, default=100); ap.add_argument('--questions', default='eval/train.json'); ap.add_argument('--change', default=None)
    ap.add_argument('--split', default='train')
    a = ap.parse_args()
    qs = json.loads((H / a.questions).read_text())['questions']
    demo = {k['id']: k for k in json.loads((REPO / 'demo-data/sim-mill/answers/answer_key.json').read_text())['questions']}
    tok = C['tokens']['Sim Mill']
    start = post(f'{BASE}/mm-llm-eval', tok, {'action': 'start', 'round': a.round, 'label': a.label, 'change': a.change,
                 'sha': 'wiki-memory', 'split': a.split, 'answer_model': 'claude-sonnet-5-5 (MCP subagent)'})
    if 'run_id' not in start: sys.exit(f'start failed: {start}')
    run_id = start['run_id']; print(f"eval run {run_id}; spent so far ${start['spent']:.2f} of ${start['budget']}", flush=True)
    out = {}
    def one(q):
        d = H / 'runs' / a.ck / a.rep / q['id']; meta = json.loads((d / 'meta.json').read_text())
        ans = (d / 'answer.md').read_text().strip() if (d / 'answer.md').exists() else ''
        chk = post(f"{C['url']}/check", C['tokens'][q['org']], {'run_id': meta['run_id'], 'answer': ans})
        r = {'answer': ans, 'status': 'ok' if ans else 'error', 'trace': chk.get('trace', []), 'charts': chk.get('charts', []),
             'citations': chk.get('citations'), 'model': 'claude-sonnet-5-5', 'usage': {}, 'ms': chk.get('ms', 0)}
        auto = grade(demo[q['ref']], r) if q.get('ref') and ans else []
        g = post(f'{BASE}/mm-llm-eval', tok, {'action': 'judge', 'run_id': run_id, 'q': q, 'result': r, 'auto': auto})
        local = sorted((H / 'runs/calls').glob(f"{meta['run_id']}.jsonl"))
        kcalls = sum(1 for _ in open(local[0])) if local else 0
        out[q['id']] = {'score': g.get('score'), 'criteria': g.get('criteria'), 'notes': g.get('notes') or g.get('error'),
                        'cost': (g.get('judge_cost') or 0), 'tool_calls': chk.get('calls'), 'wiki_memory_calls': kcalls,
                        'words': len(ans.split()), 'citations': r['citations'], 'auto': auto}
        print(f"{q['id']:5} {g.get('score', 'ERR'):>5}  calls {chk.get('calls')}+{kcalls}  cites {(r['citations'] or {}).get('supported')}/{(r['citations'] or {}).get('total')}  {str(out[q['id']]['notes'])[:110]}", flush=True)
    with cf.ThreadPoolExecutor(4) as ex: list(ex.map(one, qs))
    post(f'{BASE}/mm-llm-eval', tok, {'action': 'finish', 'run_id': run_id})
    sc = [v['score'] for v in out.values() if isinstance(v['score'], (int, float))]
    by = {}
    for q in qs:
        s = out[q['id']]['score']
        if isinstance(s, (int, float)): by.setdefault(q['section'], []).append(s)
    summ = {'eval_run': run_id, 'label': a.label, 'mean': round(sum(sc) / max(1, len(sc)), 1), 'n': len(sc),
            'by_section': {k: round(sum(v) / len(v), 1) for k, v in by.items()}, 'judge_cost': round(sum(v['cost'] for v in out.values()), 3)}
    (H / 'runs' / a.ck / a.rep / 'results.json').write_text(json.dumps({'summary': summ, 'results': out}, indent=1))
    print(json.dumps(summ))

if __name__ == '__main__':
    main()
