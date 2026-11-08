"""Bring The Paper Mill engine's historian run into Sim Mill (tools/sim-mill/engine/).

    # in the-paper-mill, branch sim-headless:
    python3 headless/build_headless.py --full && node headless/historian.js        # ~2.5 min: Sep 1 2025 + 426 days
    # here:
    python3 tools/sim-mill/engine_import.py ../the-paper-mill/headless/out/historian

Keeps the engine keys config/tags.yaml uses (plus time, grade and sheet_on), gzipped, and the event log. Only rerun when
the engine or the base year changes: the 6-week roll moves these times, it doesn't re-run the game.
"""
import csv, gzip, io, json, os, re, shutil, subprocess, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))

def main(src):
    tm = yaml.safe_load(open(os.path.join(HERE, 'config', 'tags.yaml')))
    keys = sorted({w for e in list(tm['engine'].values()) + list(tm['derived'].values()) for w in re.findall(r'[A-Za-z_]\w*', str(e))})
    rows = list(csv.DictReader(open(os.path.join(src, 'hourly.csv'))))
    miss = [k for k in keys if k not in rows[0]]
    if miss: sys.exit(f'engine run has no tag(s): {miss}')
    out = os.path.join(HERE, 'engine'); os.makedirs(out, exist_ok=True)
    cols = ['time', 'grade', 'sheet_on'] + keys
    buf = io.StringIO(); w = csv.DictWriter(buf, cols, extrasaction='ignore', lineterminator='\n'); w.writeheader(); w.writerows(rows)
    with gzip.GzipFile(os.path.join(out, 'hourly.csv.gz'), 'wb', mtime=0) as f: f.write(buf.getvalue().encode())
    shutil.copy(os.path.join(src, 'events.jsonl'), os.path.join(out, 'events.jsonl'))
    man = json.load(open(os.path.join(src, 'manifest.json')))
    repo = os.path.abspath(os.path.join(src, '..', '..', '..'))
    try: man['engine_commit'] = subprocess.run(['git', '-C', repo, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    except Exception: pass
    man['keys'] = keys; man.pop('checksum', None)
    json.dump(man, open(os.path.join(out, 'manifest.json'), 'w'), indent=1)
    print(f"engine: {len(rows)} hours x {len(keys)} keys, {sum(1 for _ in open(os.path.join(out, 'events.jsonl')))} events -> {out}")

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', '..', '..', 'the-paper-mill', 'headless', 'out', 'historian'))
