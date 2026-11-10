"""The Paper Mill engine's historian for Sim Mill: tools/sim-mill/engine/, written by engine_import.py from the-paper-mill
`node headless/historian.js` (sim-headless branch).

    hourly.csv.gz   per hour (base-year local mill time): grade, fraction of the hour with the sheet on, and the engine tag
                    keys config/tags.yaml uses (the mean of the 1-minute samples while the sheet was on)
    events.jsonl    sheet breaks, upsets, reliability failures, planned repairs, outages and grade changes
    manifest.json   the run: engine commit, seed, calendar, counts

The engine runs once for the base year; the 6-week roll moves its times with everything else (base.SHIFT).
"""
import csv, datetime as dt, gzip, json, os
import numpy as np
import yaml
from .base import HERE, SHIFT, H, hidx

DIR = os.path.join(HERE, 'engine')
TAGMAP = yaml.safe_load(open(os.path.join(HERE, 'config', 'tags.yaml')))
SOURCE = {**{k: 'engine' for k in TAGMAP['engine']}, **{k: 'derived' for k in TAGMAP['derived']},
          **{k: 'condition' for k in TAGMAP['condition']}, **{k: 'model' for k in TAGMAP['model']}}
EXPR = {**TAGMAP['engine'], **TAGMAP['derived']}
ON = os.path.exists(os.path.join(DIR, 'hourly.csv.gz')) and os.environ.get('SIM_ENGINE', '1') != '0'

def when(s):
    """An engine time (base-year local mill time) on Sim Mill's clock."""
    return dt.datetime.fromisoformat(s) + SHIFT

_cache = {}
def hourly():
    """{'sheet_on': array(H), 'grade': [str|None]*H, key: array(H) (nan where the engine has no running value)}"""
    if 'h' in _cache: return _cache['h']
    rows = list(csv.DictReader(gzip.open(os.path.join(DIR, 'hourly.csv.gz'), 'rt')))
    keys = [k for k in rows[0] if k not in ('time', 'grade', 'sheet_on')]
    out = {k: np.full(H, np.nan) for k in keys}; out['sheet_on'] = np.full(H, np.nan); out['grade'] = [None] * H
    for r in rows:
        h = int(round(hidx(when(r['time']))))
        if not 0 <= h < H: continue
        out['sheet_on'][h] = float(r['sheet_on']); out['grade'][h] = r['grade']
        for k in keys:
            if r[k] != '': out[k][h] = float(r[k])
    _cache['h'] = out
    return out

def events():
    if 'e' in _cache: return _cache['e']
    ev = []
    for line in open(os.path.join(DIR, 'events.jsonl')):
        e = json.loads(line)
        if 'start' in e: e['start'], e['end'] = when(e['start']), when(e['end'])
        if 't' in e: e['t'] = when(e['t'])
        ev.append(e)
    _cache['e'] = ev
    return ev

def series(tag_short):
    """The engine (or derived) level for a PM1 tag, hourly, or None if the tag isn't engine-driven."""
    expr = EXPR.get(tag_short)
    if not ON or expr is None: return None
    h = hourly()
    env = {k: v for k, v in h.items() if isinstance(v, np.ndarray)}
    with np.errstate(invalid='ignore'):
        return np.asarray(eval(str(expr), {'__builtins__': {}}, env), dtype=float)   # expressions come from config/tags.yaml
