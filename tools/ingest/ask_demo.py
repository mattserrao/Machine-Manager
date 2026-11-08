"""Run the demo questions (demo-data/answers/answer_key.json) through the live mm-llm-ask function.

The answers are saved in llm.answers under each question id, and signed-in users see them on the MM LLM page.
Needs a short-lived ingest token for the org (see supabase/SETUP.md). Delete the token afterwards.

    python3 tools/ingest/ask_demo.py --token <token> [--only S01-Q1 S04-Q1] [--out /tmp/answers]
"""
import argparse, concurrent.futures as cf, json, os, sys, urllib.error, urllib.request
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
    ap.add_argument('--only', nargs='*', default=[])
    ap.add_argument('--out', default=None, help='also write each response as JSON here')
    ap.add_argument('--workers', type=int, default=3)
    a = ap.parse_args()
    url, key = config()
    qs = json.loads((ROOT / 'demo-data/answers/answer_key.json').read_text())['questions']
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
        return r.get('status') == 'ok'

    with cf.ThreadPoolExecutor(a.workers) as ex: ok = list(ex.map(run, qs))
    print(f'{sum(ok)}/{len(ok)} answered'); sys.exit(0 if all(ok) else 1)

if __name__ == '__main__':
    main()
