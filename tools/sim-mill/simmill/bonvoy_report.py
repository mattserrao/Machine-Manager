"""The Bonvoy Report: one daily report of flagged trends from the Pi historian, written as MM LLM would write it.

For the demo the text is generated here (mocked), not by a model, for the last REPORT_DAYS days up to "today" (the
historian behind it covers the whole year, so streaks and week trends still look back as far as they need):
    out/bonvoy/reports/Bonvoy_Report_PM1_<day>.json   {day, report_date, headline, summary, flagged, items: [...]}
built from that day's Bonvoy exceptions, ranked by sigma x hours x days in a row, with the context a superintendent would
look for: what the tag belongs to (and how old that clothing is), the trend over the week, open work orders and RCFAs on
the asset, the latest vendor report, and the known story behind the planted faults. Loaded into llm.bonvoy_reports; the
Bonvoy Report page and the assistant's bonvoy_report tool read it.
"""
import datetime as dt, json, os
import numpy as np
from .base import (PLANTS, D, DAY, HOUR, Y0, TODAY, TAG, BY_NAME, POS_NAME, MACHINE, OUTAGES, hidx, md, us)
from .model import piece_at, VIB_ALERT, VIB_DANGER

REPORT_DAYS = 7          # one report per day for the most recent week

FAMILY = [   # (test on the short tag, family)
    (lambda s: s.endswith('_VIB'), 'bearing'), (lambda s: s.endswith('_TEMP'), 'bearing_temp'),
    (lambda s: s.startswith('UHLE'), 'felt'), (lambda s: s == 'PRESS_SOLIDS' or s.startswith('PRESS') and s.endswith('LOAD'), 'press'),
    (lambda s: s in ('FLATBOX_VAC', 'COUCH_VAC', 'COUCH_SOLIDS'), 'forming'),
    (lambda s: s.startswith('REF_') or s == 'FREENESS', 'refining'),
    (lambda s: s.startswith('DRY') and s.endswith('_DP'), 'syphon'), (lambda s: s.startswith('DRY') or s in ('STEAM_FLOW', 'HOOD_EXH_TEMP'), 'steam'),
    (lambda s: s.startswith('REEL_'), 'quality'), (lambda s: s in ('SPEED', 'PROD', 'BREAKS'), 'production'),
]
def family(short): return next((f for test, f in FAMILY if test(short)), 'stock')

CAUSE = {   # (family, direction) -> (likely cause, what to check)
    ('bearing', 'High'): ('Overall vibration above its normal band: a developing bearing defect or looseness.',
                          'Ask Keel for an off-route reading with a spectrum (BPFO / BPFI, 1x running speed); check lubrication and the bearing temperature.'),
    ('bearing_temp', 'High'): ('Bearing running hotter than usual: lubrication or a bearing defect.',
                               'Check the grease line and auto-lube; compare with the vibration trend on the same bearing.'),
    ('felt', 'High'): ('Uhle vacuum climbing: the felt is filling and compacting.',
                       'Check the HP shower: nozzles plugged, pressure, oscillator, supply strainer. Watch press solids.'),
    ('felt', 'Low'): ('Uhle vacuum low: an air leak at the cover or an open, new felt.', 'Check the Uhle cover, deckles and seals; normal for a felt in its first days.'),
    ('press', 'Low'): ('Less water out in the press.', 'Check the press felts (Uhle vacuum trend, age), nip loading and shower conditioning.'),
    ('press', 'High'): ('Press running harder than usual.', 'Check nip loading setpoints and felt condition.'),
    ('forming', 'High'): ('Drainage load rising on the forming table: the fabric is filling or the stock drains slower.',
                          'Check fabric condition and showers, freeness and headbox consistency.'),
    ('forming', 'Low'): ('Lower vacuum on the table: a seal strip, vacuum pump or a leak.', 'Check the vacuum pump, couch seal strips and box covers.'),
    ('refining', 'High'): ('More energy per ton for the same work: refiner plates wearing.',
                           'Check the plate gap and bar wear; look at LC cleaner reject rates (sand wears plates fast).'),
    ('refining', 'Low'): ('Refining load low against its normal band.', 'Check the refiner load setpoint, plate gap control and stock flow.'),
    ('syphon', 'High'): ('Syphon differential up: condensate removal struggling in this section.',
                         'Walk the section for steam at the rotary joint; check the syphon and the joint seal.'),
    ('syphon', 'Low'): ('Syphon differential low: blow-through or a control change.', 'Check the differential controller and the joint.'),
    ('steam', 'High'): ('Dryers working harder: more steam for the same sheet.', 'Check press solids and felt condition upstream; check hood balance.'),
    ('steam', 'Low'): ('Less steam demand than usual.', 'Usually a lighter grade or lower speed; confirm against the grade schedule.'),
    ('quality', 'High'): ('Sheet property above its band.', 'Check the moisture / basis weight profile and the steam and stock controls.'),
    ('quality', 'Low'): ('Sheet property below its band.', 'Check the moisture / basis weight profile and the steam and stock controls.'),
    ('production', 'Low'): ('Machine held back: speed or rate below its band.', 'Find the limit: steam, drainage, breaks, or a slowdown on the BUS sheet.'),
    ('production', 'High'): ('Rate above its normal band.', 'Normal after a grade change; confirm quality held.'),
    ('stock', 'High'): ('Stock system running above its band.', 'Check consistency control, chest levels and the pulper.'),
    ('stock', 'Low'): ('Stock system running below its band.', 'Check consistency control, chest levels and the pulper.'),
}

def story_for(short, day, m):
    """The planted-fault story behind a flag, if there is one (what an engineer who knew the history would add)."""
    P = PLANTS
    if short == 'UHLE_P2T_VAC' and D(P['F1']['fill_from']) <= day <= D(str(P['F1']['change'])[:10]):
        return ('F1', f"The 2nd press top felt is filling early. Spraywell's audit on {md(P['F1']['audit'])} found "
                      f"{P['F1']['shower_plugged_pct']}% of its HP shower nozzles plugged.")
    if short in ('REF_B_SE', 'REF_B_KW') and day >= D(P['F3']['rise_from']):
        return ('F3', f"REF 2's plates (on since {md(P['F3']['installed'])}) are wearing fast: energy per ton climbing since "
                      f"{md(P['F3']['rise_from'])}. Only one Ridgeway set on hand for two refiners.")
    if short in ('DRY3_DP', 'DRY3_STEAM_P'):
        nxt = [D(e['start']) for e in P['F5']['events'] if D(e['start']) >= day]
        if nxt and (nxt[0] - day).days <= 6:
            return ('F5', 'Same pattern as before the earlier 3rd section DS rotary joint leaks; Brightwater says the joint is misaligned on its bracket.')
    if short in ('COUCH_VAC', 'FLATBOX_VAC') and abs((day - D(str(P['F4']['event'])[:10])).days) <= 1:
        return ('F4', 'Forming fabric hole from a wad off the headbox approach.')
    for f in m['faults']:
        if f['asset'] == TAG[f'{MACHINE}:{short}']['asset'] and f['onset'].date() <= day and (not f['fixed'] or day < f['fixed'].date()):
            found = f.get('found')
            return (f['story'], f"Known bearing defect on the {f['asset']}" + (f", found on the {md(found)} vibration route." if found and found.date() <= day else '.'))
    return ('', '')

def build(m, p, rec, ev, docs, out):
    runs = m['runs']; vals = p['OUT']
    year = sorted(d for d in ev if Y0 <= d <= TODAY)
    days = [d for d in year if d > TODAY - DAY * REPORT_DAYS]
    flagged_days = {t: set() for t in TAG}
    for d in year:
        for r in ev[d]: flagged_days[r['Tag']].add(d)
    outage_on = {o['date']: o for o in OUTAGES}
    folder = os.path.join(out, 'bonvoy', 'reports'); os.makedirs(folder, exist_ok=True)
    def daily(tag, d):
        i = int(hidx(dt.datetime.combine(d, dt.time(0)))); x = vals[tag][i:i + 24]
        x = x[~np.isnan(x)]; return float(x.mean()) if len(x) else None
    n_written = 0
    for d in days:
        items = []
        for r in ev[d]:
            tag = r['Tag']; short = tag.split(':', 1)[1]; meta = TAG[tag]; fam = family(short)
            streak = 1
            while d - DAY * streak in flagged_days[tag]: streak += 1
            mu, sd = float(r['Baseline Mean']), float(r['Baseline Std Dev']) or 1e-9
            worst = float(r['Max'] if r['Direction'] == 'High' else r['Min'])
            sigma = abs(worst - mu) / sd
            week = [v for v in (daily(tag, d - DAY * k) for k in range(6, -1, -1)) if v is not None]
            slope = (week[-1] - week[0]) / max(1, len(week) - 1) if len(week) >= 3 else 0.0
            pct = 100 * slope / abs(mu) if mu else 0.0
            cause, check = CAUSE.get((fam, r['Direction']), ('Outside its normal band.', 'Check the trend and the BUS sheet for what changed.'))
            story, known = story_for(short, d, m)
            pos = meta['position_id'] or None
            ctx = []
            if pos and pos in runs:
                cur = piece_at(runs, pos, dt.datetime.combine(d, dt.time(12)))
                age = (dt.datetime.combine(d, dt.time(12)) - cur['installed']).days
                ctx.append(f"{POS_NAME[pos]} is {age} days into a {cur['target_days']}-day target life.")
            asset = meta['asset']
            parent = BY_NAME[asset]['parent_asset']
            wos = [w for w in rec['wos'] if (w.asset['name'] == asset or w.asset['asset_no'] == parent) and w.created <= d
                   and (w.status_at(d) or 0) not in (90, 99) and w.type != 'PM']
            rcfas = [x['id'] for x in rec['rcfas'] if x['event']['asset'] == asset and x['opened'] <= d and (not x['closed'] or x['closed'] > d)]
            related = [x for x in docs if x['kind'] not in ('drawing', 'reference') and x.get('date') and D(x['date']) <= d and (d - D(x['date'])).days <= 120
                       and ((pos and pos in x.get('positions', [])) or asset.lower() in x['title'].lower())]
            doc = max(related, key=lambda x: x['date']) if related else None
            items.append(dict(
                tag=tag, short=short, description=meta['description'], units=meta['units'], asset=asset, area=r['Area'],
                position_id=pos, position=POS_NAME.get(pos) if pos else None, family=fam, direction=r['Direction'],
                hours=int(r['Hours Outside']), first=r['First Outside'], last=r['Last Outside'], min=float(r['Min']), max=float(r['Max']),
                mean=mu, std=sd, low=float(r['Low Limit']), high=float(r['High Limit']), sigma=round(sigma, 1), grade=r['Grade'] or None,
                streak=streak, trend_pct_per_day=round(pct, 2),
                cause=known or cause, check=check, context=' '.join(ctx) or None, story=story or None,
                wos=[dict(no=w.no, desc=w.desc, status=w.status_at(d)) for w in wos[:3]], rcfas=rcfas[:2],
                doc=dict(id=doc['doc_id'], title=doc['title'], date=doc['date']) if doc else None,
                score=round(sigma * int(r['Hours Outside']) * (1 + .25 * (streak - 1)), 1)))
        items.sort(key=lambda x: -x['score'])
        for i, x in enumerate(items, 1): x['rank'] = i
        new = [x for x in items if x['streak'] == 1]; cont = [x for x in items if x['streak'] > 1]
        o = outage_on.get(d)
        if not items:
            headline = 'Quiet day: every tag stayed inside its normal band.'
            summary = headline + (' PM1 was down for the scheduled outage; restart hours are left out.' if o else '')
        else:
            t = items[0]
            headline = f"{t['asset']}: {t['description']} {t['direction'].lower()} for {t['hours']} h" + \
                       (f", {t['streak']} days running" if t['streak'] > 1 else ' (new)')
            parts = [f"{len(items)} tag{'s' if len(items) != 1 else ''} outside the normal band on {md(d, '%b %-d')}" +
                     (f" ({len(new)} new, {len(cont)} continuing)." if new and cont else ' (all new).' if new else ' (all continuing).')]
            lead = t['cause'] if t['story'] else t['cause'].split(':')[0].rstrip('.') + '.'
            parts.append(f"Look first at the {t['asset']}: {t['description']} {t['direction'].lower()}, {t['sigma']}σ at worst. {lead}")
            if t['trend_pct_per_day'] and abs(t['trend_pct_per_day']) >= .3:
                parts.append(f"It has moved about {abs(t['trend_pct_per_day']):.1f}% a day over the week.")
            more = [x for x in items[1:4]]
            if more: parts.append('Also flagged: ' + '; '.join(f"{x['description']} ({x['direction'].lower()}, {x['hours']} h"
                                                               + (f", {x['streak']} days" if x['streak'] > 1 else '') + ')' for x in more) + '.')
            if o: parts.append('PM1 was down for the scheduled outage; restart hours are left out.')
            summary = ' '.join(parts)
        # Above alarm limits: Bonvoy compares a tag with its own recent past, so a defect that has been climbing for weeks drops
        # out of it. The fixed vibration limits catch what the moving baseline no longer does.
        watch = []
        for tag, meta in TAG.items():
            if not meta['short'].endswith('_VIB'): continue
            v = daily(tag, d)
            if v is None or v < VIB_ALERT: continue
            level = 'Danger' if v >= VIB_DANGER else 'Alert'
            story, known = story_for(meta['short'], d, m)
            watch.append(dict(tag=tag, short=meta['short'], description=meta['description'], asset=meta['asset'], units=meta['units'],
                              value=round(v, 3), level=level, limit=VIB_DANGER if level == 'Danger' else VIB_ALERT,
                              flagged=any(x['tag'] == tag for x in items), story=story or None,
                              note=(known + ' ' if known else '') + (f"Above the {level} limit ({VIB_DANGER if level == 'Danger' else VIB_ALERT} in/s)"
                                    + ('' if any(x['tag'] == tag for x in items) else ', but not flagged by Bonvoy: its baseline has moved up with it') + '.')))
        watch.sort(key=lambda x: -x['value'])
        if watch and items: summary += f" Above alarm limits: {', '.join(f'{w['asset']} {w['value']:.2f} in/s ({w['level']})' for w in watch)}."
        elif watch: summary += f" Still above alarm limits: {', '.join(f'{w['asset']} {w['value']:.2f} in/s ({w['level']})' for w in watch)}."
        rep = dict(day=d.isoformat(), report_date=(d + DAY).isoformat(), headline=headline, summary=summary, flagged=len(items), items=items, watch=watch,
                   generated_by='mock', model='MM LLM (mocked for the demo)')
        json.dump(rep, open(os.path.join(folder, f'Bonvoy_Report_{MACHINE}_{d.isoformat()}.json'), 'w'), indent=1)
        n_written += 1
    return n_written
