"""Sim Mill's report producer: the Shift Report (each 12 h shift, written by the crew's shift lead) and the Production
Report (Quality / Uptime / Tonnage / OME, each mill day) for tools/reports (registry.yaml, lifecycle.py, daemon.py).

Everything a report says comes from the year as modelled: the stops and breaks (model events, with their WO numbers),
the hourly Pi values (tons, speed, basis weight, moisture, steam, refining), the developing failures (degrade.py) the
crew could see, and the BUS issues open that day. The shift notes are templated, with each shift lead's own way of
writing, and seeded by the report id: the same year always writes the same notes.

Definitions (the Production Report):
  reel tons         tons made at the reel (Pi PM1:PROD), net of the broke made while a grade change settles
  cull              tons made in off-spec hours (basis weight more than 3% off target, or reel moisture outside
                    target -1.2 / +0.8 points) plus the winder's trim and cull
  saleable tons     reel tons - cull
  time efficiency   hours with the sheet on / 24
  prod. efficiency  (reel tons + grade-change broke) / full-rate tons for the sheet-on hours at each grade's target speed
  qual. efficiency  saleable tons / (reel tons + grade-change broke)
  OME               time x production x quality efficiency (Overall Machine Efficiency)
"""
import datetime as dt, math, random, sys, os
from zoneinfo import ZoneInfo
import numpy as np
from .base import (MACHINE, DAY, HOUR, MIN, H, Y0, TODAY, GRADES, GRADE_IDS, GLABEL, full_tph, hidx, ts, crews, LEAD_OF, NAME, PEOPLE,
                   BY_NAME, BY_NO, SECTION_NAME, OUTAGES, NEXT_OUTAGE)
from .model import CAUSE_TEXT
from . import degrade

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'reports'))
import lifecycle as L

TZ = ZoneInfo('America/New_York')
MOIST_TARGET, MOIST_LO, MOIST_HI, BW_TOL = 8.0, 1.2, 0.8, 0.03
KIND = {'planned': 'Planned', 'unplanned': 'Unplanned', 'break': 'Sheet break', 'slowdown': 'Slowdown'}
iso = lambda t: t.replace(tzinfo=TZ).isoformat(timespec='minutes')
lc = lambda t: t[:1].lower() + t[1:] if len(t) > 1 and not t[1].isupper() else t   # lower-case a sentence start, not an acronym
r1 = lambda x: None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), 1)


def position_of(asset):
    a = BY_NAME.get(asset)
    if not a: return '', '', ''
    pos, q = a['position_id'], a['parent_asset']
    while q and not pos:
        pos = BY_NO[q]['position_id']; q = BY_NO[q]['parent_asset']
    return a['asset_no'], pos or '', SECTION_NAME.get(a['section'], '')


class Producer:
    machine = MACHINE

    def __init__(self, m, p, rec):
        self.m, self.p, self.rec = m, p, rec
        O = p['OUT']; T = lambda k: O[f'{MACHINE}:{k}']
        self.prod, self.speed, self.bw, self.moist = T('PROD'), T('SPEED'), T('REEL_BW'), T('REEL_MOIST')
        self.kw = T('REF_A_KW') + T('REF_B_KW'); self.steam = T('STEAM_FLOW')
        self.grade, self.sheet = p['grade'], p['sheet']
        self.full = np.array([full_tph(GRADE_IDS[g]) for g in self.grade])
        self.target_bw = np.array([GRADES[GRADE_IDS[g]]['bw'] for g in self.grade])
        # grade-change broke, by hour: the same rule the process model takes it off PM1:PROD with (18% for two hours,
        # or the whole of a campaign under 5 h)
        chg = np.zeros(H)
        for a, b, g in m['sched']:
            n = int(hidx(b)) - int(hidx(a)) + 1 if (b - a).total_seconds() < 5 * 3600 else 2
            for k in range(n):
                h = int(hidx(a)) + k
                if 0 <= h < H: chg[h] = 1
        self.broke = np.where(chg > 0, self.prod * 0.18 / 0.82, 0.0)
        off_bw = np.abs(self.bw - self.target_bw) > BW_TOL * self.target_bw
        off_m = (self.moist > MOIST_TARGET + MOIST_HI) | (self.moist < MOIST_TARGET - MOIST_LO)
        self.off_bw, self.off_m = np.nan_to_num(off_bw) > 0, np.nan_to_num(off_m) > 0
        self.issues = rec['issues']
        self.dev = m.get('developing', [])
        self.year_events = [e for e in m['events'] if Y0 <= e['start'].date() <= TODAY]

    # ─────────────── shared numbers for a span of hours ───────────────
    def span(self, a, b):
        hs = range(max(0, int(hidx(a))), min(H, int(hidx(b))))
        tons = float(np.nansum(self.prod[hs.start:hs.stop])); broke = float(np.nansum(self.broke[hs.start:hs.stop]))
        sheet_h = float(np.sum(self.sheet[hs.start:hs.stop]))
        full = float(np.sum(self.full[hs.start:hs.stop] * self.sheet[hs.start:hs.stop]))
        off = [h for h in hs if self.off_bw[h] or self.off_m[h]]
        off_t = float(np.nansum([self.prod[h] for h in off]))
        rnd = random.Random(f'cull:{a.isoformat()}')
        cull = off_t + tons * rnd.uniform(.006, .014)
        mins = {k: 0.0 for k in KIND}; nb = 0
        for e in self.m['events']:
            ov = max(0, (min(e['end'], b) - max(e['start'], a)).total_seconds()) / 60
            if ov: mins[e['kind']] += ov
            if e['kind'] == 'break' and a <= e['start'] < b: nb += 1
        gh = {}
        for h in hs: g = GLABEL[GRADE_IDS[self.grade[h]]]; gh[g] = gh.get(g, 0) + 1
        run = [h for h in hs if self.sheet[h] > .95]
        avg = lambda x: float(np.nanmean([x[h] for h in run])) if run else float('nan')
        gross = tons + broke
        te, pe = sheet_h / len(hs), gross / full if full > 1 else 0.0
        qe = (tons - cull) / gross if gross > 1 else 0.0
        return dict(hours=len(hs), tons=tons, broke=broke, cull=cull, saleable=tons - cull, off_hours=len(off), off_bw=sum(1 for h in hs if self.off_bw[h]),
                    off_m=sum(1 for h in hs if self.off_m[h]), sheet_h=sheet_h, mins=mins, breaks=nb, gh=gh, speed=avg(self.speed),
                    moist=avg(self.moist), bw={g: (float(np.nanmean([self.bw[h] for h in run if GLABEL[GRADE_IDS[self.grade[h]]] == g])) if any(GLABEL[GRADE_IDS[self.grade[h]]] == g for h in run) else None) for g in gh},
                    kwh=float(np.nansum(self.kw[hs.start:hs.stop])) / tons if tons > 1 else float('nan'),
                    steam=float(np.nansum(self.steam[hs.start:hs.stop])) / tons if tons > 1 else float('nan'),
                    te=te, pe=min(pe, 1.0), qe=max(0.0, qe), ome=te * min(pe, 1.0) * max(0.0, qe))

    def stop_item(self, e):
        asset_no, pos, area = position_of(e['asset']) if e['asset'] else ('', '', '')
        return dict(event_id=e['event_id'], start=iso(e['start']), end=iso(e['end']), minutes=e['minutes'], kind=e['kind'],
                    area=area or ('All' if e['cause'] == 'outage' else ''), equipment=e['asset'] or ('Machine' if e['cause'] == 'outage' else ''),
                    asset_no=asset_no, position_id=pos, cause=CAUSE_TEXT[e['cause']] + (f" ({e['where']})" if e.get('where') else ''),
                    grade=GLABEL[e['grade']], crew=e['crew'], wo_no=e['wo'].no if e.get('wo') and e['wo'].no else '',
                    comment=((e.get('outage', '') + ' ') if e.get('outage') else '') + e['note'])

    # ─────────────── the producer interface ───────────────
    def generate(self, rtype, day, shift=None):
        return self.shift_report(day, shift) if rtype == 'shift' else self.production_report(day)

    def envelope(self, rtype, day, shift, a, b, crew, author, body, text):
        who = PEOPLE.get(author)
        return dict(report_id=L.report_id(rtype, MACHINE, day.isoformat(), shift), type=rtype, schema=L.SCHEMA, machine=MACHINE,
                    period_start=iso(a), period_end=iso(b), mill_day=day.isoformat(), shift=shift, crew=crew,
                    author=dict(id=author, name=who['name'], role=who['role']) if who else dict(id=author, name=author, role=''),
                    source='sim-mill', body=body, text=text)

    # ═════════════════════════ Shift Report ═════════════════════════
    def shift_report(self, day, shift):
        a = dt.datetime.combine(day, dt.time(6)) + (HOUR * 12 if shift == 'Night' else dt.timedelta())
        b = a + HOUR * 12
        dc, nc = crews(day); crew = dc if shift == 'Day' else nc; lead = LEAD_OF[crew]
        s = self.span(a, b)
        evs = [e for e in self.year_events if a <= e['start'] < b]
        stops = [self.stop_item(e) for e in evs]
        changes = [(t, g) for t, _, g in self.m['sched'] if a < t < b]
        watch = self.watch_items(a, b)
        handover = self.handover(day, b, watch)
        rnd = random.Random(f'notes:{day}:{shift}')
        stories = [i for i in self.issues if i.story and i.open_on(day)]
        notes = Notes(lead, rnd).write(s, evs, changes, watch, shift, b, stories, day)
        body = dict(grades=[dict(grade=g, hours=h) for g, h in s['gh'].items()],
                    grade_changes=[dict(at=iso(t), to=GLABEL[g]) for t, g in changes],
                    tons=round(s['tons']), sheet_on_pct=round(100 * s['sheet_h'] / s['hours'], 1), breaks=s['breaks'],
                    break_min=round(s['mins']['break']), unplanned_min=round(s['mins']['unplanned']), planned_min=round(s['mins']['planned']),
                    avg_speed=None if math.isnan(s['speed']) else round(s['speed']), stops=stops, notes=notes,
                    watch=[dict(equipment=w['asset'], tags=[f'{MACHINE}:{k}' for k in w['tags']], note=w['note'], wo_no=w['wo']) for w in watch],
                    handover=handover)
        text = self.shift_text(day, shift, crew, lead, body)
        return self.envelope('shift', day, shift, a, b, crew, lead, body, text)

    def watch_items(self, a, b):
        """Developing failures the crew could see this shift: known ones (found, with a WO) and ones nobody has called
        yet (only some leads write those down)."""
        out, mid = [], a + HOUR * 6
        for f in self.dev:
            if not (f['onset'] < b and f['end'] > a): continue
            x = degrade.signature(f, [mid])[0]
            if x < .3: continue
            known = f['found'] is not None and f['found'] < b
            mode = next(m for m in degrade.MODES if m['id'] == f['mode'])
            wo = f['wo'].no if known and f.get('wo') and f['wo'].no else ''
            note = mode['finding'] if known else mode['sign']
            out.append(dict(asset=f['asset'], tags=list(f['tags']), note=note, known=known, wo=wo, x=x, mode=f['mode']))
        return out

    def handover(self, day, b, watch):
        out = [f"{w['asset']}: {lc(w['note'].split(':')[0])}" + (f" (WO {w['wo']})" if w['wo'] else '') for w in watch if w['known']]
        for i in sorted((i for i in self.issues if i.open_on(day) and (i.story or (day - i.start).days <= 2)), key=lambda i: (not i.story, i.start), reverse=False):
            issue = i.issue if not i.issue.startswith(i.asset['name']) else i.issue[len(i.asset['name']):].lstrip(' :')
            line = f"{i.asset['name']}: {lc(issue)} → {lc(i.action_on(day))}"
            if line not in out: out.append(line)
            if len(out) >= 4: break
        nx = next((o for o in OUTAGES if o['start'] >= b), None)
        if nx and (nx['start'] - b).days <= 3: out.append(f"Outage {nx['date']:%b %d}: shutdown at {nx['start']:%H:%M}")
        return out[:5]

    def shift_text(self, day, shift, crew, lead, body):
        L_ = [f"# Shift Report · {MACHINE} · {day:%a %b %d, %Y} · {shift} shift ({'06:00–18:00' if shift == 'Day' else '18:00–06:00'})",
              f"Crew {crew} · {NAME(lead)}, shift lead", '',
              f"**{body['tons']:,} t** · sheet on {body['sheet_on_pct']}% · {body['breaks']} break{'s' if body['breaks'] != 1 else ''} ({body['break_min']} min)"
              + (f" · unplanned {body['unplanned_min']} min" if body['unplanned_min'] else '') + (f" · planned {body['planned_min']} min" if body['planned_min'] else ''),
              'Grades: ' + ', '.join(f"{g['grade']} {g['hours']} h" for g in body['grades']), '', '## Notes', body['notes'], '']
        if body['stops']:
            L_ += ['## Stops and breaks'] + [f"- {x['start'][11:16]} {KIND[x['kind']]} {x['minutes']:g} min · {x['equipment'] or '—'} · {x['cause']}"
                                              + (f" · WO {x['wo_no']}" if x['wo_no'] else '') for x in body['stops']] + ['']
        if body['handover']: L_ += ['## Handover'] + [f'- {h}' for h in body['handover']]
        return '\n'.join(L_).strip() + '\n'

    # ═════════════════════════ Production Report ═════════════════════════
    def production_report(self, day):
        a = dt.datetime.combine(day, dt.time(6)); b = a + DAY
        s = self.span(a, b); dc, nc = crews(day)
        sh = [dict(shift=n, crew=c, **self.shift_numbers(self.span(a + HOUR * k, a + HOUR * (k + 12)))) for n, c, k in (('Day', dc, 0), ('Night', nc, 12))]
        q_bw = [dict(grade=g, target=GRADES[next(k for k in GRADE_IDS if GLABEL[k] == g)]['bw'], avg=None if v is None else round(v, 2)) for g, v in s['bw'].items()]
        body = dict(tons=round(s['tons']), saleable_tons=round(s['saleable']), broke_tons=round(s['broke']), cull_tons=round(s['cull'], 1),
                    uptime_pct=round(100 * (1 - (s['mins']['planned'] + s['mins']['unplanned']) / 1440), 1),
                    minutes={k: round(v) for k, v in s['mins'].items()}, breaks=s['breaks'],
                    avg_speed=None if math.isnan(s['speed']) else round(s['speed']),
                    grade_hours='; '.join(f'{k} {v}' for k, v in s['gh'].items()),
                    quality=dict(basis_weight=q_bw, moisture=dict(target=MOIST_TARGET, avg=None if math.isnan(s['moist']) else round(s['moist'], 2)),
                                 off_spec_hours=s['off_hours'], off_bw_hours=s['off_bw'], off_moisture_hours=s['off_m']),
                    efficiency=dict(time_pct=round(100 * s['te'], 1), production_pct=round(100 * s['pe'], 1), quality_pct=round(100 * s['qe'], 1), ome_pct=round(100 * s['ome'], 1)),
                    energy=dict(steam_per_t=None if math.isnan(s['steam']) else round(s['steam'], 2), kwh_per_t=None if math.isnan(s['kwh']) else round(s['kwh'], 1)),
                    reel_moist=None if math.isnan(s['moist']) else round(s['moist'], 2), crews=dict(day=dc, night=nc), shifts=sh)
        text = self.production_text(day, body)
        return self.envelope('production', day, None, a, b, None, 'P18', body, text)

    def shift_numbers(self, s):
        return dict(tons=round(s['tons']), saleable_tons=round(s['saleable']), breaks=s['breaks'], sheet_on_pct=round(100 * s['sheet_h'] / s['hours'], 1),
                    ome_pct=round(100 * s['ome'], 1))

    def production_text(self, day, b):
        e, q = b['efficiency'], b['quality']
        L_ = [f"# Production Report · {MACHINE} · mill day {day:%a %b %d, %Y} (06:00 to 06:00)",
              'Quality / Uptime / Tonnage / OME · from the MES, reviewed by the production manager', '',
              f"**OME {e['ome_pct']}%** = time {e['time_pct']}% × production {e['production_pct']}% × quality {e['quality_pct']}%", '',
              '## Tonnage', f"Reel {b['tons']:,} t · saleable {b['saleable_tons']:,} t · grade-change broke {b['broke_tons']} t · cull {b['cull_tons']} t",
              f"Grades: {b['grade_hours']}", '',
              '## Uptime', f"Uptime {b['uptime_pct']}% · breaks {b['breaks']} ({b['minutes']['break']} min) · unplanned {b['minutes']['unplanned']} min · "
              f"planned {b['minutes']['planned']} min · slowdowns {b['minutes']['slowdown']} min" + (f" · average speed {b['avg_speed']:,} fpm" if b['avg_speed'] else ''), '',
              '## Quality', 'Basis weight: ' + ', '.join(f"{x['grade']} {x['avg']} (target {x['target']})" for x in q['basis_weight'] if x['avg'] is not None),
              f"Reel moisture {q['moisture']['avg']}% (target {q['moisture']['target']}%) · off-spec hours {q['off_spec_hours']}"
              + (f" (basis weight {q['off_bw_hours']}, moisture {q['off_moisture_hours']})" if q['off_spec_hours'] else ''), '',
              '## Energy', f"Steam {b['energy']['steam_per_t']} t/t · refining {b['energy']['kwh_per_t']} kWh/t", '',
              '## By shift'] + [f"- {x['shift']} (crew {x['crew']}): {x['tons']:,} t, saleable {x['saleable_tons']:,} t, {x['breaks']} break{'' if x['breaks'] == 1 else 's'}, sheet on {x['sheet_on_pct']}%, OME {x['ome_pct']}%" for x in b['shifts']]
        return '\n'.join(L_) + '\n'


# ═════════════════════════ The shift lead's notes ═════════════════════════
# Each lead writes the same facts their own way. 'notice': how likely they are to write down a trend nobody has called yet.
STYLE = {
    'P08': dict(name='terse', notice=.35),        # Harlan Mbeki, crew A: short lines, abbreviations
    'P09': dict(name='thorough', notice=.75),     # Lucille Brandt, crew B: full sentences, the why
    'P10': dict(name='numbers', notice=.45),      # Rafael Okonkwo, crew C: tons and rates first
    'P11': dict(name='safety', notice=.55),       # Wynn Castellano, crew D: safety and housekeeping first
}

class Notes:
    def __init__(self, lead, rnd):
        self.st = STYLE[lead]['name']; self.notice = STYLE[lead]['notice']; self.r = rnd
    def pick(self, *opts): return self.r.choice(opts)

    def write(self, s, evs, changes, watch, shift, end, stories=(), day=None):
        st, out = self.st, []
        down = [e for e in evs if e['kind'] in ('unplanned', 'planned')]
        brk = [e for e in evs if e['kind'] == 'break']; slow = [e for e in evs if e['kind'] == 'slowdown']
        outage = next((e for e in down if e['cause'] == 'outage'), None)
        tons = round(s['tons'])
        # opening line
        if outage:
            out.append(self.pick(f"Outage shift. {'Shutdown' if outage['start'] >= end - HOUR * 12 else 'Start-up'} went to plan.",
                                 "Outage work most of the shift; machine down on the outage plan."))
        elif not down and len(brk) <= 1 and not slow:
            out.append({'terse': self.pick(f'Good shift. {tons} t.', f'Steady. {tons} t, {len(brk)} break.' if brk else f'Clean shift, {tons} t.'),
                        'thorough': self.pick(f'A steady shift with {tons} t made and nothing major to report.', f'Quiet shift: {tons} t and the machine ran well throughout.'),
                        'numbers': self.pick(f'{tons} t, sheet on {100 * s["sheet_h"] / s["hours"]:.0f}% of the shift.', f'Good rate all shift: {tons} t at {s["speed"]:.0f} fpm average.' if not math.isnan(s['speed']) else f'{tons} t.'),
                        'safety': self.pick(f'No injuries or near misses. Ran well: {tons} t.', f'Safe shift, housekeeping done on the wet end. {tons} t.')}[st])
        else:
            out.append({'terse': f'Rough one. {tons} t.' if len(down) + len(brk) >= 3 else f'{tons} t.',
                        'thorough': f'Not the smoothest shift: {tons} t made.' if len(down) + len(brk) >= 3 else f'Mostly a good shift, {tons} t made.',
                        'numbers': f'{tons} t; lost {round(s["mins"]["unplanned"] + s["mins"]["break"])} min to stops and breaks.',
                        'safety': self.pick('No injuries.', 'No injuries; one near miss reported at the wet end (slippery floor at the couch pit).' if self.r.random() < .2 else 'No injuries.') + f' {tons} t.'}[st])
        # stops
        for e in down:
            if e['cause'] == 'outage': continue
            h = e['minutes'] / 60; c = lc(CAUSE_TEXT[e['cause']]); wo = f" WO {e['wo'].no}." if e.get('wo') and e['wo'].no else ''
            if e['kind'] == 'planned':
                out.append({'terse': f"Planned stop {h:.1f} h: {c}.{wo}", 'thorough': f"We took a planned {h:.1f} h stop at {e['start']:%H:%M} for {c} on the {e['asset']}.{wo}",
                            'numbers': f"Planned stop {e['start']:%H:%M}, {h:.1f} h ({c}).{wo}", 'safety': f"Planned {h:.1f} h stop for {c}; lockouts verified before work started.{wo}"}[st])
            else:
                out.append({'terse': f"Down {h:.1f} h at {e['start']:%H:%M}, {e['asset']}: {c}.{wo}",
                            'thorough': f"Unplanned stop at {e['start']:%H:%M}: {c} on the {e['asset']}, {h:.1f} h down. {e['note']}{wo}",
                            'numbers': f"Lost {h:.1f} h ({round(h * 31)} t) to {c} on the {e['asset']} at {e['start']:%H:%M}.{wo}",
                            'safety': f"{e['asset']}: {c} at {e['start']:%H:%M}, {h:.1f} h down. Area barricaded while maintenance worked.{wo}"}[st])
        for e in slow:
            out.append(f"Slowed for {e['minutes'] / 60:.1f} h: {lc(CAUSE_TEXT[e['cause']])} ({e['asset']}).")
        # breaks
        if len(brk) >= 2:
            where = max(sorted({e['where'] for e in brk}), key=lambda w: sum(1 for e in brk if e['where'] == w))
            out.append({'terse': f"{len(brk)} breaks, mostly {where}.", 'thorough': f"{len(brk)} sheet breaks, most of them at the {where}; tail threading went OK.",
                        'numbers': f"{len(brk)} breaks, {round(s['mins']['break'])} min sheet off.", 'safety': f"{len(brk)} breaks ({where}); reminded the crew about rope threading guards."}[st])
        elif len(brk) == 1 and st == 'thorough':
            out.append(f"One break at the {brk[0]['where']} ({brk[0]['minutes']:.0f} min).")
        # grade changes
        if changes:
            gs = ', '.join(GLABEL[g] for _, g in changes)
            out.append({'terse': f"GC to {gs}.", 'thorough': f"Grade change to {gs}; on weight within the hour.", 'numbers': f"Grade change to {gs}.",
                        'safety': f"Grade change to {gs}."}[st])
        # what they saw developing
        for w in watch:
            if w['known']:
                if self.r.random() < .6:
                    out.append({'terse': f"{w['asset']} still trending ({lc(w['note'].split(':')[0])}).", 'thorough': f"Still watching the {w['asset']}: {lc(w['note'])}." + (f" WO {w['wo']} is in." if w['wo'] else ''),
                                'numbers': f"{w['asset']}: trend still moving; WO {w['wo'] or 'raised'}.", 'safety': f"Keeping an eye on the {w['asset']} ({lc(w['note'].split(':')[0])})."}[st])
            elif self.r.random() < self.notice * min(1.0, w['x'] + .2):
                out.append({'terse': f"{w['asset']}: {lc(w['note'])}?", 'thorough': f"Something to look at on the {w['asset']}: {lc(w['note'])}. Not sure yet; flagging it.",
                            'numbers': f"{w['asset']}: {lc(w['note'])} ({', '.join(w['tags'])}).", 'safety': f"Operators mentioned the {w['asset']}: {lc(w['note'])}."}[st])
        # the long-running problems on the BUS sheet (the planted stories): most leads say where they stand
        for i in stories[:2]:
            if self.r.random() < {'terse': .35, 'thorough': .85, 'numbers': .5, 'safety': .55}[st]:
                act = i.action_on(day)
                out.append({'terse': f"{i.asset['name']}: {lc(act)}.", 'thorough': f"On the {i.asset['name']}: {lc(i.issue)}. Latest: {lc(act)}.",
                            'numbers': f"{i.asset['name']} still on the list ({lc(act)}).", 'safety': f"{i.asset['name']}: {lc(act)}; crew briefed."}[st])
        if st == 'safety' and self.r.random() < .3: out.append(self.pick('Housekeeping: dry end swept, broke conveyor cleared.', 'Eyewash stations checked.', 'Hood doors cleaned and closed.'))
        return ' '.join(out)
