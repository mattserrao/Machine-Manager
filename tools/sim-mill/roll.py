"""Roll the Sim Mill demo forward: regenerate the year so it ends just before today (whole 6-week cycles) and reload it.

    MM_INGEST_TOKEN=<Sim Mill ingest token> python3 tools/sim-mill/roll.py [--force] [--no-answers]

Run by the scheduled task every week; it only does work when a new 6-week cycle has started (or with --force):
  1. tools/sim-mill/run.py --auto      the year moved by whole outage cycles; answer key re-rendered
  2. run.py --check + validate_ref.py   the generator's own checks, on the moved year
  3. tools/ingest/load.py --files --embed   replaces Sim Mill's rows, records (My Machine, Outage Planning, Consumables,
                                            task packages), original files (old ones pruned) and embeddings
  4. tools/ingest/ask_demo.py          re-asks the demo questions so the saved answers match the new dates, and
                                            records them (with charts) in answers/saved_answers.json
Afterwards commit demo-data/sim-mill/backbone, answers/answer_key.json and answers/saved_answers.json: the MM LLM page reads the
questions from that file, and its "roll" block is how the next run knows which cycle is live.

The ingest token comes from  select public.mm_llm_new_ingest_token('Sim Mill', 2);  (SQL editor, or the Supabase
tool in a scheduled session). It expires on its own.
"""
import argparse, datetime as dt, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
KEY = os.path.join(ROOT, 'demo-data', 'sim-mill', 'answers', 'answer_key.json')
sys.path.insert(0, HERE)
from run import cycles_for          # noqa: E402  (no simmill import: that reads the roll on import)

def sh(*args):
    print('$', ' '.join(args), flush=True)
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--force', action='store_true'); ap.add_argument('--no-answers', action='store_true')
    a = ap.parse_args()
    want = cycles_for(dt.date.today())
    try: live = json.load(open(KEY)).get('roll', {}).get('cycles')
    except FileNotFoundError: live = None
    if live == want and not a.force:
        print(f'Sim Mill is on cycle {want} already (year ends {json.load(open(KEY))["roll"]["today"]}); nothing to do.'); return 0
    token = os.environ.get('MM_INGEST_TOKEN') or sys.exit('set MM_INGEST_TOKEN to a Sim Mill ingest token')
    cfg = open(os.path.join(ROOT, 'mm-config.js')).read()
    url = re.search(r'https://[a-z0-9]+\.supabase\.co', cfg).group(0); key = re.search(r'sb_publishable_[A-Za-z0-9_-]+', cfg).group(0)
    print(f'rolling Sim Mill from cycle {live} to {want}')
    sh('tools/sim-mill/run.py', '--check', '--cycles', str(want))
    sh('tools/sim-mill/validate_ref.py')
    sh('tools/sim-mill/run.py', '--cycles', str(want))
    sh('tools/ingest/load.py', '--source', 'demo-data/sim-mill/out', '--backbone', 'demo-data/sim-mill/backbone',
       '--url', url, '--key', key, '--token', token, '--files', '--embed')
    if not a.no_answers: sh('tools/ingest/ask_demo.py', '--token', token, '--key', 'demo-data/sim-mill/answers/answer_key.json', '--snapshot', 'demo-data/sim-mill/answers/saved_answers.json')
    r = json.load(open(KEY))['roll']
    print(f"done: Sim Mill is on cycle {r['cycles']}, {r['start']} to {r['today']}. Commit demo-data/sim-mill/backbone and the answer key.")
    return 0

if __name__ == '__main__':
    sys.exit(main())
