"""Run the demo questions (an answer key) through the live mm-llm-ask function, for the token's org.

The answers are saved in llm.answers under each question id, and signed-in users see them on the MM LLM page.
--snapshot also records them (answer, charts, tool calls) in a JSON file committed next to the key, which the page
shows to everyone, signed out too. Each answer is graded against the key's "answer" expectations (charts drawn,
series, right axis, words that must appear); a miss is reported, not fatal.
Needs a short-lived ingest token for the org (see supabase/SETUP.md). Delete the token afterwards.

    python3 tools/ingest/ask_demo.py --token <token> [--key demo-data/sim-mill/answers/answer_key.json] [--only F2-Q1]
        [--out /tmp/answers] [--snapshot demo-data/sim-mill/answers/saved_answers.json]
"""
import argparse, concurrent.futures as cf, datetime as dt, json, os, re, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def config():
    """Supabase URL and publishable key from mm-config.js."""
    import re
    s = (ROOT / 'mm-config.js').read_text()
    url = re.search(r"https://[a-z0-9]+\.supabase\.co", s).group(0)
    key = re.search(r"sb_publishable_[A-Za-z0-9_-]+", s).group(0)
    return url, key

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--token', required=True)
    ap.add_argument('--key', default='demo-data/sim-mill/answers/answer_key.json', help='answer key with the questions (Sim Mill by default)')
    ap.add_argument('--only', nargs='*', default=[])
    ap.add_argument('--out', default=None, help='also write each response as JSON here')
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--snapshot', default=None, help='record the answers in this JSON file (merged by question id)')
    a = ap.parse_args()
    url, key = config()
    qs = json.loads((ROOT / a.key).read_text())['questions']
    qs = [q for q in qs if not a.only or q['id'] in a.only]
    if a.out: os.makedirs(a.out, exist_ok=True)

    def run(q):
        req = urllib.request.Request(f'{url}/functions/v1/mm-llm-ask', method='POST',
            data=json.dumps({'question': q['question'], 'question_id': q['id']}).encode(),
            headers={'apikey': key, 'x-mm-ingest-token': a.token, 'Content-Type': 'application/json'})
        try: r = json.load(urllib.request.urlopen(req, timeout=240))
        except urllib.error.HTTPError as e:
            try: r = json.loads(e.read())
            except Exception: r = {'error': f'HTTP {e.code}'}
        if a.out: Path(a.out, q['id'] + '.json').write_text(json.dumps(r, indent=1))
        tools = len(r.get('trace') or [])
        print(f"{q['id']}: {r.get('status', 'error')} · {(r.get('ms') or 0)/1000:.1f} s · {tools} tool calls"
              + ('' if r.get('status') == 'ok' else f" · {r.get('answer') or r.get('error')}"), flush=True)
        return r

    got = {}
    def run_keep(q):
        r = run(q); got[q['id']] = r; return r.get('status') == 'ok'
    with cf.ThreadPoolExecutor(a.workers) as ex: ok = list(ex.map(run_keep, qs))
    misses = [f"{q['id']}: {m}" for q in qs if got[q['id']].get('status') == 'ok' for m in grade(q, got[q['id']])]
    for m in misses: print('GRADE ' + m)
    if a.snapshot: snapshot(ROOT / a.snapshot, qs, got)
    print(f'{sum(ok)}/{len(ok)} answered, {len(misses)} grading notes'); sys.exit(0 if all(ok) else 1)

def charts_of(r):
    if r.get('charts'): return r['charts']
    out = []   # a redraw with the same title replaces the earlier chart
    for t in r.get('trace') or []:
        if t.get('tool') != 'make_chart' or t.get('error'): continue
        i = next((k for k, c in enumerate(out) if c.get('title') == t['args'].get('title')), None)
        if i is None: out.append(t['args'])
        else: out[i] = t['args']
    return out

def grade(q, r):
    """What the key expects of the answer itself (not the data): charts, series, a right axis, words."""
    e, out, cs = q.get('answer') or {}, [], charts_of(r)
    if len(cs) < e.get('chart', 0): out.append(f"expected {e['chart']} chart(s), got {len(cs)}")
    if e.get('series_min') and not any(len(c.get('series', [])) >= e['series_min'] for c in cs): out.append(f"no chart with {e['series_min']}+ series")
    if e.get('right_axis') and not any(any(s.get('axis') == 'right' for s in c.get('series', [])) for c in cs): out.append('no right-axis series')
    for pat in e.get('re', []):
        if not re.search(pat, r.get('answer') or '', re.I): out.append(f'answer lacks /{pat}/')
    return out

def snapshot(path, qs, got):
    snap = json.loads(path.read_text()) if path.exists() else {'about': '', 'answers': {}}
    snap['about'] = ('Answers recorded from the live mm-llm-ask function (tools/ingest/ask_demo.py --snapshot): '
                     'the model, its answer text, the charts it drew and the tools it called. The MM LLM page shows them to everyone.')
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    for q in qs:
        r = got[q['id']]
        if r.get('status') != 'ok': continue
        snap['answers'][q['id']] = {'question': q['question'], 'answer': r['answer'], 'charts': charts_of(r),
            'tool_trace': [{'tool': t['tool'], 'args': t.get('args'), 'rows': t.get('rows')} for t in r.get('trace') or []],
            'model': r.get('model'), 'provider': r.get('provider'), 'ms': r.get('ms'), 'created_at': now, 'grading': grade(q, r)}
    keep = {q['id'] for q in json.loads((ROOT / 'demo-data/sim-mill/answers/answer_key.json').read_text())['questions']} if 'sim-mill' in str(path) else None
    if keep: snap['answers'] = {k: v for k, v in snap['answers'].items() if k in keep}
    path.write_text(json.dumps(snap, indent=1, ensure_ascii=False) + '\n')
    print(f'recorded {len(snap["answers"])} answers in {path.relative_to(ROOT)}')

if __name__ == '__main__':
    main()
