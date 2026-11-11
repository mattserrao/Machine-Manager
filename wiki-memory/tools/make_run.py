"""Prepare one answering pass: a folder per question with an `mm` wrapper (org, run id, stage baked in) and the question.
    python3 tools/make_run.py CK REP [--stage STAGE] [--questions eval/train.json]
Prints one line per question: <qid> <folder>."""
import argparse, json, os, stat
from pathlib import Path
H = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(); ap.add_argument('ck'); ap.add_argument('rep')
ap.add_argument('--stage', default=None); ap.add_argument('--questions', default='eval/train.json')
a = ap.parse_args()
stage = a.stage or a.ck
for q in json.loads((H / a.questions).read_text())['questions']:
    d = H / 'runs' / a.ck / a.rep / q['id']; d.mkdir(parents=True, exist_ok=True)
    run = f"{a.ck}-{a.rep}-{q['id']}"
    w = d / 'mm'
    w.write_text(f"#!/bin/sh\nMM_ORG='{q['org']}' MM_RUN='{run}' MM_STAGE='{stage}' exec {H}/bin/mm \"$@\"\n")
    w.chmod(w.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    (d / 'question.txt').write_text(q['question'] + '\n')
    (d / 'meta.json').write_text(json.dumps({'id': q['id'], 'org': q['org'], 'run_id': run, 'stage': stage}))
    print(q['id'], d)
