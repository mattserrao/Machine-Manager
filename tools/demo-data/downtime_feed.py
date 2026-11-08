"""Demo Mill downtime feed: demo-data/out/downtime/Downtime_PM1_<date>.csv, the same layout as Sim Mill's.

Built from what the Demo Mill generator already decided (no new randomness):
  demo-data/out/_truth/downtime.csv   sheet breaks and equipment stops
  demo-data/backbone/outages.csv      planned outages (up to the demo's "today")
  backbone grade and crew schedules   grade and crew on at the start of each event
  demo-data/out/rcfa/RCFA_log_PM1.csv  RCFA ID where an RCFA was opened on that asset that day

Run:  python3 tools/demo-data/downtime_feed.py
"""
import csv, datetime as dt, os
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DD = os.path.join(ROOT, 'demo-data')
TODAY = dt.date(2026, 10, 31)   # backbone.DEMO_TODAY
HEAD = ['Event ID', 'Start', 'End', 'Minutes', 'Kind', 'Area', 'Equipment', 'Asset Number', 'Position', 'Cause',
        'Grade', 'Crew', 'WO #', 'RCFA ID', 'Comment']


def rows(path):
    return list(csv.DictReader(open(path, newline='')))


def main():
    eq = {r['asset_no']: r for r in rows(os.path.join(DD, 'backbone', 'equipment.csv'))}
    sec = {r['section']: r['name'].replace('PM1 ', '') for r in eq.values() if r['kind'] == 'section'}
    grades = [(dt.datetime.fromisoformat(r['start']), dt.datetime.fromisoformat(r['end']), r['grade'])
              for r in rows(os.path.join(DD, 'backbone', 'grade_schedule.csv'))]
    crews = {r['date']: r for r in rows(os.path.join(DD, 'backbone', 'crew_schedule.csv'))}
    rcfa = {}
    for r in rows(os.path.join(DD, 'out', 'rcfa', 'RCFA_log_PM1.csv')):
        d = dt.datetime.strptime(r['Event Date'], '%m/%d/%Y').date()
        rcfa[(r['Asset Number'], d)] = r['RCFA ID']

    def grade_at(t):
        g = next((g for a, b, g in grades if a <= t < b), '')
        return '' if g == 'DOWN' else g

    def crew_at(t):
        day = t.date() if t.hour >= 6 else t.date() - dt.timedelta(days=1)   # night shift belongs to the day it started
        c = crews.get(day.isoformat(), {})
        return c.get('day_crew' if 6 <= t.hour < 18 else 'night_crew', '')

    ev = []
    for r in rows(os.path.join(DD, 'out', '_truth', 'downtime.csv')):
        t = dt.datetime.fromisoformat(r['start']); m = round(float(r['hours']) * 60)
        a = eq.get(r['asset_no'], {}); area = sec.get(a.get('section', ''), '')
        brk = r['kind'] == 'break'
        ev.append(dict(t=t, m=m, kind='Sheet break' if brk else 'Unplanned', area=area, equip=r['asset'], asset=r['asset_no'],
                       pos=a.get('position_id', ''), cause=('Sheet break (' + r['note'] + ')') if brk else r['note'],
                       rcfa='' if brk else rcfa.get((r['asset_no'], t.date()), ''),
                       comment=(r['note'].capitalize() if brk else r['note']) + '.'))
    for o in rows(os.path.join(DD, 'backbone', 'outages.csv')):
        a, b = dt.datetime.fromisoformat(o['start']), dt.datetime.fromisoformat(o['end'])
        if a.date() > TODAY:
            continue
        ev.append(dict(t=a, m=round((b - a).total_seconds() / 60), kind='Planned', area='All', equip='Machine', asset='', pos='',
                       cause='Annual outage' if o['type'] == 'annual' else 'Planned outage', rcfa='', comment=f"{o['id']} {o['note']}"))
    ev = [e for e in ev if e['t'].date() <= TODAY]
    ev.sort(key=lambda e: e['t'])

    out = os.path.join(DD, 'out', 'downtime'); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.startswith('Downtime_PM1_'):
            os.remove(os.path.join(out, f))
    by_day = defaultdict(list)
    for i, e in enumerate(ev, 1):
        end = e['t'] + dt.timedelta(minutes=e['m'])
        by_day[e['t'].date()].append([f"DT-{e['t']:%y%m%d}-{i:04d}", e['t'].strftime('%Y-%m-%dT%H:%M'), end.strftime('%Y-%m-%dT%H:%M'),
                                      e['m'], e['kind'], e['area'], e['equip'], e['asset'], e['pos'], e['cause'],
                                      grade_at(e['t']), crew_at(e['t']), '', e['rcfa'], e['comment']])
    for d, rs in sorted(by_day.items()):
        with open(os.path.join(out, f'Downtime_PM1_{d.isoformat()}.csv'), 'w', newline='') as fh:
            w = csv.writer(fh); w.writerow(HEAD); w.writerows(rs)
    kinds = defaultdict(int)
    for e in ev:
        kinds[e['kind']] += 1
    print(f'{len(ev)} events in {len(by_day)} files -> {os.path.relpath(out, ROOT)}  ' + ', '.join(f'{k}: {n}' for k, n in sorted(kinds.items())))
    print('with RCFA ID:', sum(1 for e in ev if e['rcfa']))


if __name__ == '__main__':
    main()
