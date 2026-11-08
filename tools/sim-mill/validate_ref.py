"""Check the Python port against the reference model (the-paper-mill `sim-headless`, reference/ in this folder).

    python3 tools/sim-mill/validate_ref.py

Process: for each mapped tag, the port's median running value per grade must be within tolerance of the reference
year's (reference/grade_stats.json: hourly means while the machine ran). Events: break rate, unplanned stops and
outages against reference/summary.json and the agreed targets. The two use different random generators, so events are
compared as rates, not one by one.
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simmill import base, model, process
from simmill.base import Y0, TODAY, GRADE_IDS

REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reference')
G = json.load(open(os.path.join(REF, 'grade_stats.json'))); S = json.load(open(os.path.join(REF, 'summary.json')))
# port tag -> (reference tag, relative tolerance)
MAP = {'SPEED': ('speed', .03), 'PROD': ('prod', .12), 'DRY4_STEAM_P': ('st3', .05), 'STEAM_FLOW': ('steam', .12), 'REEL_MOIST': ('moist', .03),
       'REEL_BW': ('bw', .02), 'PULPER_AMPS': ('amps', .03), 'FLATBOX_VAC': ('vac', .08), 'COUCH_SOLIDS': ('couchSol', .04),
       'PRESS_SOLIDS': ('pressSol', .03), 'HB_CONS': ('hbc', .03), 'DRY1_DP': ('dp1', .1), 'DRY2_DP': ('dp2', .1), 'DRY4_DP': ('dp3', .12),
       'REF_A_SE': ('kwh', .12)}

def main():
    m = model.build(); p = process.build(m)
    fails = 0
    run = (p['sheet'] > .99) & (p['on'] > .99)
    i0 = int(base.hidx(base.dt.datetime.combine(Y0, base.dt.time(0))))
    run[:i0] = False
    print(f"{'tag':14} {'grade':8} {'port':>9} {'ref':>9}  tol")
    for k, (rk, tol) in MAP.items():
        x = p['OUT'][base.T(k)]
        for gi, g in enumerate(GRADE_IDS):
            sel = run & (p['grade'] == gi) & ~np.isnan(x)
            if sel.sum() < 24 or rk not in G.get(g, {}): continue
            a, b = float(np.median(x[sel])), G[g][rk]['median']
            ok = abs(a - b) <= tol * abs(b)
            fails += not ok
            print(f"{k:14} {g:8} {a:9.3f} {b:9.3f}  {'ok' if ok else 'OUT'} ({tol:.0%})")
    yr = [e for e in m['events'] if Y0 <= e['start'].date() <= TODAY]
    bpd = sum(1 for e in yr if e['kind'] == 'break') / 365
    unp = sum(1 for e in yr if e['kind'] == 'unplanned' and e['minutes'] > 60)
    outs = sum(1 for e in yr if e['cause'] == 'outage')
    checks = [(f"breaks/day {bpd:.2f} vs reference {S['breaks_per_day']}", abs(bpd - S['breaks_per_day']) <= .25 * S['breaks_per_day']),
              (f"unplanned stops > 1 h: {unp} vs reference {S['unplanned_gt1h']} (target 15-25)", 15 <= unp <= 25),
              (f"outages {outs} vs reference {S['outages']}", outs == S['outages'])]
    for msg, ok in checks:
        print(('PASS ' if ok else 'FAIL ') + msg); fails += not ok
    print(f'{fails} outside tolerance' if fails else 'port matches the reference model')
    return fails

if __name__ == '__main__':
    sys.exit(1 if main() else 0)
