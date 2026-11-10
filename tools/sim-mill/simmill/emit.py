"""Sim Mill writers: the files exactly as they'd arrive from the mill, in the layouts `tools/ingest/importers.py` reads,
plus the three new feeds: downtime events, daily production and position runs.

    out/bus/BUS_PM1_<date>.xlsx            daily BUS sheet
    out/jde/WO_PM1_<monday>.csv            weekly JDE deltas, and WO_PM1_full_<today>.csv
    out/teams/Planner_PM1_<date>.csv       weekly Planner exports
    out/rcfa/RCFA_log_PM1.csv              RCFA log as of today
    out/pi/hourly/PM1_hourly_<YYYY-MM>.csv  Pi hourly (wide), out/pi/minute/<F#>_<from>_<to>.csv, out/pi/points.json
    out/bonvoy/Bonvoy_PM1_<date>.csv          daily Bonvoy exception report
    out/downtime/Downtime_PM1_<date>.csv    NEW: every stop, break and slowdown that started that day
    out/production/Production_PM1_<YYYY-MM>.csv  NEW: one row per mill day (6 AM to 6 AM)
    out/positions/Position_runs_PM1_<today>.csv  NEW: every fabric, felt, plate and roll run (My Machine history)
    out/_truth/                              what the checks and the answer key read (never imported)
"""
import datetime as dt, json, math, os
import numpy as np
from .base import (DAY, HOUR, MIN, Y0, TODAY, H, OUT_BY_ID, MACHINE, TAG, BY_NAME, POS_NAME, SECTION_NAME, GRADE_IDS, GLABEL, NAME, crews, next_outage,
                   us, hidx, ts, write_csv)
from .model import grade_at
from .records import STATUS, WO_TYPE, CRAFT_LEAD
from . import process as PR

JDE_COLS = ['Order Number', 'Order Type', 'Type of WO', 'Description', 'Asset Number', 'Asset Description', 'Location',
            'Priority', 'Status', 'Status Description', 'Requested Date', 'Planned Start', 'Completed Date', 'Originator',
            'Assigned To', 'Craft', 'Est Hours', 'Act Hours', 'Outage', 'Parts Status', 'Completion Notes']
PLANNER_COLS = ['Task ID', 'Task Name', 'Bucket Name', 'Progress', 'Priority', 'Assigned To', 'Created By', 'Created Date',
                'Start Date', 'Due Date', 'Late', 'Completed Date', 'Completed By', 'Labels', 'Description']
RCFA_COLS = ['RCFA ID', 'Event Date', 'Opened', 'Closed', 'Status', 'Title', 'Area', 'Asset Number', 'Asset', 'Downtime (h)',
             'Production Loss', 'Category', 'Root Cause', 'Contributing Factors', 'Lead', 'Action IDs (Planner)']
DOWNTIME_COLS = ['Event ID', 'Start', 'End', 'Minutes', 'Kind', 'Area', 'Equipment', 'Asset Number', 'Position', 'Cause', 'Grade', 'Crew',
                 'WO #', 'RCFA ID', 'Comment']
PRODUCTION_COLS = ['Mill Day', 'Tons', 'Uptime %', 'Sheet Breaks', 'Break Minutes', 'Unplanned Minutes', 'Planned Minutes',
                   'Slowdown Minutes', 'Avg Speed (fpm)', 'Grade Hours', 'Steam (t/t)', 'Refining (kWh/t)', 'Reel Moisture %', 'Crew Day', 'Crew Night']
POSITION_COLS = ['Position', 'Position Name', 'Installed', 'Removed', 'Days', 'Target Days', 'Reason', 'Condition', 'Vendor', 'Style',
                 'Serial', 'Comment']


def wo_row(w, d):
    st = w.status_at(d); out = w.outage_at(d)
    act = '' if st < 90 else f"{w.est * (0.8 + (int(w.no) % 7) / 10):.1f}"
    return {'Order Number': w.no, 'Order Type': 'WM', 'Type of WO': WO_TYPE[w.type], 'Description': w.desc,
            'Asset Number': w.asset['asset_no'], 'Asset Description': w.asset['name'], 'Location': f"{MACHINE} / {SECTION_NAME.get(w.asset['section'], '')}",
            'Priority': w.priority, 'Status': st, 'Status Description': STATUS[st], 'Requested Date': us(w.created),
            'Planned Start': us(OUT_BY_ID[out]['date'] if out else w.planned), 'Completed Date': us(w.completed) if st >= 90 else '',
            'Originator': NAME(w.originator), 'Assigned To': NAME(CRAFT_LEAD[w.craft]) if CRAFT_LEAD.get(w.craft) else 'Operations',
            'Craft': w.craft, 'Est Hours': f'{w.est:g}', 'Act Hours': act,
            'Outage': (out.replace('OUT-', '') if out else ''), 'Parts Status': w.parts if st < 90 else '',
            'Completion Notes': w.notes if st >= 90 or st in (35, 45) or w.resched else ''}

def action_row(a, d):
    p = a.progress_at(d)
    return {'Task ID': a.id, 'Task Name': a.title, 'Bucket Name': a.bucket, 'Progress': p, 'Priority': a.priority,
            'Assigned To': NAME(a.owner), 'Created By': NAME(a.creator), 'Created Date': us(a.created),
            'Start Date': us(a.started) if a.started and a.started <= d else '', 'Due Date': us(a.due),
            'Late': 'true' if p != 'Completed' and a.due < d else 'false', 'Completed Date': us(a.completed) if p == 'Completed' else '',
            'Completed By': NAME(a.owner) if p == 'Completed' else '',
            'Labels': ';'.join(x for x in [MACHINE, SECTION_NAME.get(a.asset['section'], '') if a.asset else ''] if x), 'Description': a.desc}


def bus_rows(rec, d):
    rows = []
    for i in rec['issues']:
        if not i.open_on(d): continue
        closing = i.end == d
        st = 'Closed' if closing else ('New' if i.start == d else (i.status or 'Open'))
        wo = i.wo.no if i.wo and i.wo.created <= d else ''
        rows.append(dict(area=SECTION_NAME.get(i.asset['section'], ''), equip=i.asset['name'], issue=i.issue, action=i.action_on(d),
                         owner=NAME(i.owner), status=st, days=(d - i.start).days + 1, wo=wo))
    order = {'New': 0, 'Open': 1, 'Waiting parts': 2, 'Closed': 3}
    return sorted(rows, key=lambda r: (order[r['status']], r['area'], r['equip']))

def write_bus(m, rec, out_dir):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    os.makedirs(out_dir, exist_ok=True)
    head = PatternFill('solid', fgColor='D9D9D9'); thin = Side(style='thin', color='BFBFBF')
    cols = ['#', 'Area', 'Equipment / Position', 'Issue', 'Action / Next step', 'Owner', 'Status', 'Days Open', 'WO #']
    widths = [4, 18, 30, 56, 46, 20, 13, 10, 11]
    counts = {}; d = Y0
    while d <= TODAY:
        rows = bus_rows(rec, d); counts[d] = len(rows)
        day_c, night_c = crews(d)
        y0, y1 = dt.datetime.combine(d - DAY, dt.time(6)), dt.datetime.combine(d, dt.time(6))
        brk = [x for x in m['events'] if x['kind'] == 'break' and y0 <= x['start'] < y1]
        down = sum(max(0, (min(x['end'], y1) - max(x['start'], y0)).total_seconds()) for x in m['events'] if x['kind'] in ('planned', 'unplanned')) / 3600
        gr = sorted({grade_at(m['sched'], y0 + HOUR * k) for k in range(24)}, key=GRADE_IDS.index)
        wb = Workbook(); ws = wb.active; ws.title = 'BUS'
        ws['A1'] = f'{MACHINE} BUS Daily Sheet (Sim Mill)'; ws['A1'].font = Font(bold=True, size=14)
        meta = [('Date', d.strftime('%a %m/%d/%Y')), ('Day crew', day_c), ('Night crew', night_c),
                ('Grades (last 24 h)', ', '.join(GLABEL[g] for g in gr)), ('Breaks (last 24 h)', len(brk)),
                ('Downtime (last 24 h, h)', round(down, 1)), ('Next outage', next_outage(d)['date'].strftime('%m/%d/%Y'))]
        for n, (k, v) in enumerate(meta):
            ws.cell(row=2 + n, column=1, value=k).font = Font(bold=True); ws.cell(row=2 + n, column=3, value=v)
        r0 = 10
        for c, (h, w) in enumerate(zip(cols, widths), 1):
            cell = ws.cell(row=r0, column=c, value=h); cell.font = Font(bold=True); cell.fill = head
            cell.border = Border(bottom=thin); ws.column_dimensions[cell.column_letter].width = w
        for n, r in enumerate(rows, 1):
            vals = [n, r['area'], r['equip'], r['issue'], r['action'], r['owner'], r['status'], r['days'], r['wo']]
            for c, v in enumerate(vals, 1):
                cell = ws.cell(row=r0 + n, column=c, value=v); cell.alignment = Alignment(wrap_text=c in (4, 5), vertical='top')
                cell.border = Border(bottom=thin)
        ws.freeze_panes = ws.cell(row=r0 + 1, column=1)
        wb.properties.creator = f'{MACHINE} BUS'; wb.properties.created = wb.properties.modified = dt.datetime.combine(d, dt.time(7, 45))
        wb.save(os.path.join(out_dir, f'BUS_{MACHINE}_{d.isoformat()}.xlsx'))
        d += DAY
    return counts


def write_structured(m, rec, out):
    mondays = [d for d in (Y0 + DAY * k for k in range((TODAY - Y0).days + 1)) if d.weekday() == 0]
    wos = rec['wos']
    for mo in mondays:
        rows = [wo_row(w, mo) for w in wos if w.created <= mo and any(mo - DAY * 7 < c <= mo for c in w.changes())]
        write_csv(os.path.join(out, 'jde', f'WO_{MACHINE}_{mo.isoformat()}.csv'), JDE_COLS, rows)
    write_csv(os.path.join(out, 'jde', f'WO_{MACHINE}_full_{TODAY.isoformat()}.csv'), JDE_COLS, [wo_row(w, TODAY) for w in wos if w.created <= TODAY])
    for mo in mondays + [TODAY]:
        write_csv(os.path.join(out, 'teams', f'Planner_{MACHINE}_{mo.isoformat()}.csv'), PLANNER_COLS,
                  [action_row(a, mo) for a in rec['actions'] if a.created <= mo])
    rows = []
    for r in rec['rcfas']:
        e = r['event']; a = BY_NAME[e['asset']]
        rows.append({'RCFA ID': r['id'], 'Event Date': us(e['start'].date()), 'Opened': us(r['opened']), 'Closed': us(r['closed']),
                     'Status': r['status'], 'Title': r['title'], 'Area': SECTION_NAME.get(a['section'], ''),
                     'Asset Number': a['asset_no'], 'Asset': a['name'], 'Downtime (h)': f"{r['downtime_h']:g}", 'Production Loss': r['loss'],
                     'Category': r['category'], 'Root Cause': r['root_cause'], 'Contributing Factors': r['contributing'], 'Lead': NAME(r['lead']),
                     'Action IDs (Planner)': '; '.join(r['action_ids'])})
    write_csv(os.path.join(out, 'rcfa', f'RCFA_log_{MACHINE}.csv'), RCFA_COLS, rows)


def fmt(v, t):
    if isinstance(v, float) and math.isnan(v): return ''
    return f"{v:.{TAG[t]['decimals']}f}"

def write_pi_bonvoy(m, p, out):
    tags = list(TAG)
    i0 = int(hidx(dt.datetime.combine(Y0, dt.time(0))))
    by_month = {}
    for h in range(i0, H): by_month.setdefault(ts(h).strftime('%Y-%m'), []).append(h)
    for mon, hs in by_month.items():
        rows = [dict({'Timestamp': ts(h).isoformat(timespec='minutes')}, **{t: fmt(float(p['OUT'][t][h]), t) for t in tags}) for h in hs]
        write_csv(os.path.join(out, 'pi', 'hourly', f'{MACHINE}_hourly_{mon}.csv'), ['Timestamp'] + tags, rows)
    rng = np.random.default_rng(3304)
    for story, a, b, short in PR.MINUTE_WINDOWS:
        wt = [f'{MACHINE}:{s}' for s in short]
        cols = {t: PR.minute_series(p, m, t, a, b, rng) for t in wt}
        n = len(next(iter(cols.values())))
        rows = [dict({'Timestamp': (a + MIN * i).isoformat(timespec='minutes')}, **{t: fmt(float(cols[t][i]), t) for t in wt}) for i in range(n)]
        write_csv(os.path.join(out, 'pi', 'minute', f'{story}_{a.date()}_{(b - MIN).date()}.csv'), ['Timestamp'] + wt, rows)
    pts = [{'Name': t, 'Descriptor': v['description'], 'EngineeringUnits': v['units'], 'PointClass': 'classic',
            'PointType': 'Int32' if v['short'] == 'BREAKS' else 'Float32', 'Step': v['short'] == 'BREAKS',
            'Area': SECTION_NAME.get(v['section'], ''), 'AssetNumber': v['asset_no'], 'Asset': v['asset'], 'PositionId': v['position_id']} for t, v in TAG.items()]
    json.dump({'server': 'SIMPI01', 'demo_now': f'{TODAY.isoformat()}T23:00:00', 'points': pts}, open(os.path.join(out, 'pi', 'points.json'), 'w'), indent=1)
    days = [Y0 + DAY * k for k in range((TODAY - Y0).days + 1)]
    ev = PR.bonvoy(p['OUT'], p['grade'], p['sheet'], p['on'], days)
    for d, rows in ev.items():
        write_csv(os.path.join(out, 'bonvoy', f'Bonvoy_{MACHINE}_{d.isoformat()}.csv'), PR.BONVOY_COLS, rows)
    return ev


def write_new_feeds(m, p, rec, out):
    """Event ids for the stops (the Shift Reports quote them) and position runs (as of today)."""
    rc_of = {}
    for r in rec['rcfas']: rc_of[id(r['event'])] = r['id']
    by_day = {}
    n = 0
    for e in m['events']:
        if e['start'].date() < Y0 or e['start'].date() > TODAY: continue
        n += 1; e['event_id'] = f"DT-{e['start']:%y%m%d}-{n:04d}"
        by_day.setdefault(e['start'].date(), []).append(e)
    # Downtime and daily production now reach Machine Manager as reports (simmill/reports.py: the Shift Report carries
    # every stop, the Production Report the mill day's numbers); the database extracts them into llm.downtime and
    # llm.production_daily. The event ids above are what the Shift Reports quote.
    months = None
    rows = []
    for pos, rr in m['runs'].items():
        for r in rr:
            if r['installed'] > dt.datetime.combine(TODAY, dt.time(23)): continue
            rem = r['removed'] if r['removed'] and r['removed'].date() <= TODAY else None
            rows.append({'Position': pos, 'Position Name': POS_NAME[pos], 'Installed': r['installed'].date().isoformat(),
                         'Removed': rem.date().isoformat() if rem else '', 'Days': ((rem or dt.datetime.combine(TODAY, dt.time(12))) - r['installed']).days,
                         'Target Days': r['target_days'], 'Reason': r['reason'] if rem else '', 'Condition': r['condition'] if rem else 'running',
                         'Vendor': r['vendor'], 'Style': r['style'], 'Serial': r['serial'], 'Comment': r['note'] if rem else ''})
    write_csv(os.path.join(out, 'positions', f'Position_runs_{MACHINE}_{TODAY.isoformat()}.csv'), POSITION_COLS, rows)
    return months


def write_truth(m, rec, ev, out):
    T = os.path.join(out, '_truth'); os.makedirs(T, exist_ok=True)
    write_csv(os.path.join(T, 'events.csv'), ['start', 'end', 'minutes', 'kind', 'cause', 'asset', 'story'],
              [dict(start=e['start'].isoformat(timespec='minutes'), end=e['end'].isoformat(timespec='minutes'), minutes=e['minutes'], kind=e['kind'],
                    cause=e['cause'], asset=e['asset'], story=e['story']) for e in m['events']])
    flags = {}
    for d, rows in ev.items():
        for r in rows: flags.setdefault(r['Tag'], []).append(d.isoformat())
    json.dump({'bonvoy_flags': flags, 'faults': [dict(asset=f['asset'], onset=f['onset'].isoformat(), found=f['found'] and f['found'].isoformat(),
                                                     fail=f['fail'] and f['fail'].isoformat(), fix_outage=f['fix_outage'], story=f['story'],
                                                     wo=f['wo'].no if f.get('wo') else None) for f in m['faults']],
               'rcfas': [dict(id=r['id'], story=r['story'], title=r['title'], actions=r['action_ids']) for r in rec['rcfas']],
               'wos': {w.story or w.key: w.no for w in rec['wos'] if w.story or w.key}}, open(os.path.join(T, 'truth.json'), 'w'), indent=1)
