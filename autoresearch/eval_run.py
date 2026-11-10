"""Run one autoresearch round: Sonnet answers through mm-llm-ask-dev, Opus judges through mm-llm-eval, results land in
llm.eval_runs / llm.eval_results and in autoresearch/runs/<run_id>-<label>.json.

Needs two short-lived ingest tokens (Sim Mill and Demodemo RAG), e.g.
    select public.mm_llm_new_ingest_token('Sim Mill', 2);  select public.mm_llm_new_ingest_token('Demodemo RAG', 2);

    MM_TOKEN_SIM=... MM_TOKEN_RAG=... python3 autoresearch/eval_run.py --round 0 --label baseline --split all \
        [--change "what changed"] [--only pm01 sm03] [--workers 3] [--round-cap 9]

The $50 total budget is enforced by mm-llm-eval; --round-cap stops this round early.
"""
import argparse, concurrent.futures as cf, json, os, subprocess, sys, threading, time, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/ingest'))
from ask_demo import config, grade   # noqa: E402  (Supabase URL / key; deterministic chart & regex checks)

def post(url, key, token, body, timeout=300):
    req = urllib.request.Request(url, method='POST', data=json.dumps(body).encode(),
        headers={'apikey': key, 'x-mm-ingest-token': token, 'Content-Type': 'application/json'})
    try: return json.load(urllib.request.urlopen(req, timeout=timeout))
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read())
        except Exception: return {'error': f'HTTP {e.code}'}
    except Exception as e: return {'error': str(e)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--round', type=int, required=True); ap.add_argument('--label', required=True)
    ap.add_argument('--split', choices=['train', 'heldout', 'all'], default='train'); ap.add_argument('--change', default=None)
    ap.add_argument('--only', nargs='*', default=[]); ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--round-cap', type=float, default=9.0)
    ap.add_argument('--run-id', type=int, default=None, help='add to (or redo questions in) an existing run instead of starting one')
    a = ap.parse_args()
    tokens = {'Sim Mill': os.environ['MM_TOKEN_SIM'], 'Demodemo RAG': os.environ['MM_TOKEN_RAG']}
    url, key = config()
    qs = json.loads((ROOT / 'autoresearch/questions.json').read_text())['questions']
    qs = [q for q in qs if (a.split == 'all' or q['split'] == a.split) and (not a.only or q['id'] in a.only)]
    demo = {k['id']: k for k in json.loads((ROOT / 'demo-data/sim-mill/answers/answer_key.json').read_text())['questions']}
    sha = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if a.run_id: run_id = a.run_id; print(f"adding {len(qs)} questions to run {run_id}", flush=True)
    else:
        start = post(f'{url}/functions/v1/mm-llm-eval', key, tokens['Sim Mill'],
                     {'action': 'start', 'round': a.round, 'label': a.label, 'change': a.change, 'sha': sha, 'split': a.split})
        if 'run_id' not in start: sys.exit(f"start failed: {start}")
        run_id = start['run_id']; print(f"run {run_id}: {len(qs)} questions, spent so far ${start['spent']:.2f} of ${start['budget']}", flush=True)
    lock, spent_round, out, stop = threading.Lock(), [0.0], {}, threading.Event()

    def one(q):
        if stop.is_set(): return
        t = tokens[q['org']]
        r = post(f'{url}/functions/v1/mm-llm-ask-dev', key, t, {'question': q['question'], 'eval': True})
        if r.get('error') and 'answer' not in r: r = {'status': 'error', 'answer': r['error']}
        auto = grade(demo[q['ref']], r) if q.get('ref') and r.get('status') == 'ok' else []
        g = post(f'{url}/functions/v1/mm-llm-eval', key, t, {'action': 'judge', 'run_id': run_id, 'q': q, 'result': r, 'auto': auto})
        with lock:
            c = (g.get('answer_cost') or 0) + (g.get('judge_cost') or 0); spent_round[0] += c
            out[q['id']] = {'q': q, 'answer': r.get('answer'), 'status': r.get('status'), 'usage': r.get('usage'), 'ms': r.get('ms'),
                            'tools': [x.get('tool') for x in r.get('trace') or []], 'auto': auto, 'grade': g}
            print(f"{q['id']:5} {q['section']}/{q['split']:7} score {g.get('score', 'ERR'):>5}  ${c:.3f}  "
                  f"{(r.get('ms') or 0)/1000:5.1f}s  {g.get('notes') or g.get('error') or ''}"[:200], flush=True)
            if spent_round[0] >= a.round_cap or 'budget' in str(g.get('error', '')): stop.set()

    with cf.ThreadPoolExecutor(a.workers) as ex: list(ex.map(one, qs))
    post(f'{url}/functions/v1/mm-llm-eval', key, tokens['Sim Mill'], {'action': 'finish', 'run_id': run_id})
    Path(ROOT / 'autoresearch/runs').mkdir(exist_ok=True)
    path = ROOT / f'autoresearch/runs/{run_id}-{a.label}.json'
    if a.run_id and path.exists():           # merge redone questions into the run's file
        prev = json.loads(path.read_text()); prev['results'].update(out); out = prev['results']; spent_round[0] += prev.get('cost', 0)
    path.write_text(json.dumps({'run_id': run_id, 'round': a.round, 'label': a.label,
        'sha': sha, 'split': a.split, 'change': a.change, 'cost': round(spent_round[0], 4), 'results': out}, indent=1))
    scores = [v['grade']['score'] for v in out.values() if 'score' in v['grade']]
    print(f"\nrun {run_id} done: {len(out)}/{len(qs)} graded, mean {sum(scores)/max(1,len(scores)):.1f}, round cost ${spent_round[0]:.2f}"
          + ('  (stopped early: cap)' if stop.is_set() else ''))

if __name__ == '__main__':
    main()
