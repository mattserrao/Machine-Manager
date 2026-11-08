"""Sim Mill documents: vendor reports (PDF), RCFA write-ups (Word), drawings and reference charts (PDF + CSV table).
Measured values come from the model (Pi series, position runs, faults), so the documents agree with every other source.

    out/docs/vendor/<vendor>/<report>.pdf    clothing surveys, felt analysis, vibration routes, shower audits,
                                             refiner plate reports, roll service, steam surveys
    out/docs/rcfa/<RCFA id>.docx             one write-up per RCFA in the log
    out/docs/drawings/<DWG no>.pdf           machine layout tables (dryer cans and felt rolls, press, roll list)
    out/docs/reference/<REF id>.pdf (+ tables/<REF id>.csv)
"""
import datetime as dt, io, os, random
from xml.sax.saxutils import escape
import numpy as np
from .base import B, BT, md, tx, SHIFT
from .base import (CFG, PLANTS, D, DAY, HOUR, Y0, TODAY, OUTAGES, IN_YEAR, NEXT_OUTAGE, MACHINE, TAG, BY_NAME, BY_POS, POS_NAME,
                   SECTION_NAME, GRADES, GRADE_IDS, GLABEL, NAME, VENDORS, hidx, us, ORD, write_csv)
from .base import full_tph
from .model import piece_at, ROUTES, CRITICAL, VIB_ALERT, VIB_DANGER, CAUSE_TEXT
from .process import BY_G

HEAD = f'Sim Mill {MACHINE}'


def render_pdf(path, head, title, blocks, doc_id):
    from reportlab import rl_config
    rl_config.invariant = 1
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    ss = getSampleStyleSheet()
    body = ParagraphStyle('b', parent=ss['BodyText'], fontSize=9.5, leading=13)
    h2 = ParagraphStyle('h', parent=ss['Heading2'], fontSize=11.5, spaceBefore=10, spaceAfter=4)
    cell = ParagraphStyle('c', parent=body, fontSize=8, leading=10)
    flow = [Paragraph(escape(title), ParagraphStyle('t', parent=ss['Title'], fontSize=15, alignment=0, spaceAfter=8))]
    for b in blocks:
        if b[0] == 'h': flow.append(Paragraph(escape(b[1]), h2))
        elif b[0] == 'p': flow.append(Paragraph(escape(b[1]), body))
        elif b[0] == 'kv':
            t = Table([[Paragraph(f'<b>{escape(k)}</b>', cell), Paragraph(escape(str(v)), cell)] for k, v in b[1]], colWidths=[1.7 * inch, 4.9 * inch])
            t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LINEBELOW', (0, 0), (-1, -1), .25, colors.lightgrey)]))
            flow += [t, Spacer(1, 6)]
        elif b[0] == 'table':
            data = [[Paragraph(f'<b>{escape(str(x))}</b>', cell) for x in b[1]]] + [[Paragraph(escape(str(x)), cell) for x in r] for r in b[2]]
            t = Table(data, repeatRows=1, hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e6e6e6')), ('GRID', (0, 0), (-1, -1), .25, colors.grey),
                                   ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
            flow += [t, Spacer(1, 8)]
    def deco(c, d):
        c.saveState(); c.setFont('Helvetica-Bold', 10); c.drawString(.75 * inch, 10.5 * inch, head)
        c.setFont('Helvetica', 8); c.drawRightString(7.75 * inch, 10.5 * inch, doc_id)
        c.line(.75 * inch, 10.42 * inch, 7.75 * inch, 10.42 * inch)
        c.drawString(.75 * inch, .5 * inch, f'{head} · {doc_id}'); c.drawRightString(7.75 * inch, .5 * inch, f'Page {d.page}')
        c.restoreState()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=letter, topMargin=1.0 * inch, bottomMargin=.8 * inch, leftMargin=.75 * inch, rightMargin=.75 * inch,
                      title=title, author=head).build(flow, onFirstPage=deco, onLaterPages=deco)
    open(path, 'wb').write(buf.getvalue())

def render_docx(path, title, blocks, doc_id):
    from docx import Document
    from docx.shared import Pt
    doc = Document()
    doc.core_properties.author = f'{HEAD} Reliability'; doc.core_properties.title = title
    doc.core_properties.created = doc.core_properties.modified = BT('2026-10-31T12:00')
    doc.add_heading(title, 1)
    for b in blocks:
        if b[0] == 'h': doc.add_heading(b[1], 2)
        elif b[0] == 'p': doc.add_paragraph(b[1])
        elif b[0] in ('kv', 'table'):
            hdr, rows = (None, b[1]) if b[0] == 'kv' else (b[1], b[2])
            t = doc.add_table(rows=0, cols=len(rows[0]) if rows else len(hdr)); t.style = 'Table Grid'
            if hdr:
                cells = t.add_row().cells
                for i, h in enumerate(hdr): cells[i].text = str(h); cells[i].paragraphs[0].runs[0].bold = True
            for r in rows:
                cells = t.add_row().cells
                for i, x in enumerate(r): cells[i].text = str(x)
            doc.add_paragraph()
    doc.add_paragraph(doc_id).runs[0].font.size = Pt(8)
    os.makedirs(os.path.dirname(path), exist_ok=True); doc.save(path)

slug = lambda s: ''.join(ch if ch.isalnum() else '-' for ch in s.lower()).strip('-').replace('--', '-')


def build(m, p, rec, out):
    rnd = random.Random(4405); runs = m['runs']; O = p['OUT']
    manifest = []
    def pi_at(tag, t):
        h = int(hidx(t)); return float(O[f'{MACHINE}:{tag}'][h])
    def pi_day(tag, d):
        a = int(hidx(dt.datetime.combine(d, dt.time(0)))); x = O[f'{MACHINE}:{tag}'][a:a + 24]; return float(np.nanmean(x))
    def add(kind, rid, vendor, d, title, blocks, positions, story='', fields=None):
        path = os.path.join(out, 'docs', 'vendor', slug(vendor), f'{rid}.pdf')
        render_pdf(path, vendor, title, blocks, rid)
        manifest.append(dict(doc_id=rid, kind=kind, vendor=vendor, date=d.isoformat(), title=title, positions=positions, story=story, fields=fields or {}))

    # ─── clothing surveys at every outage in the year ───
    SURVEY = {'Northbank Fabrics': ['form-bottom', 'd1-felt', 'd2-felt'], 'Halden Felt Co.': ['p1-felt-top', 'p1-felt-bottom'],
              'Marlow Press Fabrics': ['p2-felt-top', 'p2-felt-bottom'], 'Corrie Textiles': ['d3-felt', 'd4-felt']}
    for o in IN_YEAR:
        d = o['date']
        for vendor, poss in SURVEY.items():
            v = VENDORS[vendor]; rid = f"{''.join(w[0] for w in vendor.split())[:2].upper()}-SV-{d:%y%m%d}"
            rows, notes = [], []
            for pos in poss:
                r = piece_at(runs, pos, o['start'] - HOUR); age = (o['start'] - r['installed']).days; f = age / r['target_days']
                felt = pos.startswith('p'); dryer = pos.startswith('d')
                chg = r['removed'] is not None and o['start'] <= r['removed'] <= o['end'] + HOUR * 3
                cal = (3.1 - .6 * f if felt else 1.8 - .2 * f if dryer else .9 - .1 * f) + rnd.uniform(-.03, .03)
                perm = (32 - 14 * f if felt else 95 - 30 * f if dryer else 520 - 70 * f) * rnd.uniform(.97, 1.03)
                third = f'{620 + 260 * f + rnd.uniform(-25, 25):.0f} gsm water' if felt else (f'{20 + 70 * f:.0f}% wear layer' if not dryer else 'Seam OK')
                cond = 'Good' if f < .5 else ('Normal wear' if f < .95 else 'End of life')
                rows.append([POS_NAME[pos], r['style'], us(r['installed'].date()), f'{age / 7:.1f}', f'{cal:.2f}', f'{perm:.0f}', third,
                             f"{cond}. {'Change at this outage as planned' if chg else 'Continue'}"])
            if not notes: notes.append('No unusual wear. Clothing running as expected for its age.')
            if vendor == 'Marlow Press Fabrics' and d == B('2026-05-27'):
                notes = [tx('The 2nd press top felt changed early on 05/19/2026 (34 days) was analysed separately: see MP-FA-260526. '
                            'The replacement is running normally; Uhle vacuum back to 9.8 inHg.')]
            blocks = [('kv', [('Customer', f'{HEAD} (recycled linerboard, fourdrinier)'), ('Survey date', us(d)), ('Issued', us(d + 2 * DAY)),
                              ('Surveyed by', v['rep']), ('Distribution', f"{NAME('P01')}, {NAME('P16')}")]),
                      ('h', 'Measurements'),
                      ('table', ['Position', 'Style', 'Installed', 'Age (wk)', 'Caliper (mm)', 'Air perm (cfm)', 'Fill / wear', 'Condition and recommendation'], rows),
                      ('h', 'Comments')] + [('p', n) for n in notes]
            add('clothing_survey', rid, vendor, d, f'{vendor} - Clothing survey, {MACHINE} outage {us(d)}', blocks, poss,
                fields={'report_no': rid, 'vendor': vendor, 'survey_date': us(d)})
    # F1: the felt analysis of the felt that filled
    F1 = PLANTS['F1']; uh = pi_day('UHLE_P2T_VAC', B('2026-05-18')); ps = pi_day('PRESS_SOLIDS', B('2026-05-18'))
    add('felt_analysis', tx('MP-FA-260526'), 'Marlow Press Fabrics', B('2026-05-26'),
        tx('Marlow Press Fabrics - Used felt analysis: 2nd press top felt removed 05/19/2026'),
        [('kv', [('Felt', f"Seamed felt, 1400 gsm, serial {piece_at(runs, 'p2-felt-top', BT('2026-05-01T00:00')).get('serial')}"),
                 ('Installed / removed', tx('04/15/2026 to 05/19/2026 (34 days, target 42)')), ('Analysed by', VENDORS['Marlow Press Fabrics']['rep'])]),
         ('h', 'Findings'),
         ('table', ['Measure', 'This felt', 'Typical at 5 weeks'], [['Fill (contaminants)', '71%', '40-45%'], ['Water content', '1,180 gsm', '780 gsm'],
                                                                      ['Air permeability', '9 cfm', '19 cfm'], ['Contaminant', 'Stickies, filler and fines', '']]),
         ('p', f"Uhle box vacuum (Pi) was {uh:.1f} inHg on {md(B('2026-05-18'), '%m/%d')} against ~10 inHg for a felt this age; press exit solids {ps:.1f}%. "
               + tx('The felt was not being cleaned: the Spraywell audit of 05/13/2026 found 22% of the 2nd press top HP shower nozzles plugged.')),
         ('h', 'Recommendation'), ('p', 'Check the HP shower nozzles weekly and clean the shower supply strainer at every outage. '
                                         'Watch the Uhle vacuum rate of rise: more than 0.1 inHg a day before week 4 means the felt is filling.')],
        ['p2-felt-top'], 'F1', {'fill': '71%', 'days': '34'})

    # ─── Keel monthly vibration route ───
    v = VENDORS['Keel Vibration Services']
    extra = [('2nd section felt roll 3', .05), ('4th section felt roll 1', .055), ('Hood supply fan', .07), ('Hood exhaust fan', .065), ('Vacuum pump', .08)]
    for r in ROUTES:
        if r < Y0: continue
        t = dt.datetime.combine(r, dt.time(10)); rid = f'KV-VR-{r:%y%m%d}'
        rows = []; recs = []; story = ''
        for aid, asset, tag in CRITICAL:
            x = pi_at(tag, t)
            if x < .03:   # machine down at 10:00: take the day's running average
                x = pi_day(tag, r)
            st = 'Danger' if x >= VIB_DANGER else 'Alert' if x >= VIB_ALERT else 'Good'
            note = ''
            f = next((f for f in m['faults'] if f['asset'] == asset and f['onset'] <= t and (not f['fixed'] or t < f['fixed'])), None)
            if st != 'Good' and f:
                note = 'Outer race defect frequency (BPFO) with harmonics' if asset.startswith('Reel') else 'Bearing defect frequencies present'
                if f['story'] == 'F2':
                    story = 'F2'
                    recs.append(f"{asset}: outer race defect, {x:.2f} in/s ({st}). " +
                                (tx('Change at the next outage (Aug 19). Plan the bearing now.') if r <= B('2026-08-19') else
                                 tx('Deferred from Aug 19 (no bearing in stores). Rate of rise is accelerating: change no later than the Nov 11 outage; '
                                    'consider a planned stop if it passes 0.50 in/s.')))
                else:
                    recs.append(f'{asset}: {x:.2f} in/s ({st}). Plan a bearing change.')
            rows.append([asset, TAG[f'{MACHINE}:{tag}']['tag'], f'{x:.3f}', st, note])
        for asset, base in extra:
            x = base + rnd.uniform(-.01, .01); rows.append([asset, '(portable)', f'{x:.3f}', 'Good', ''])
        if not recs: recs.append('No new findings. All points within limits.')
        add('vibration_route', rid, v['name'], r, f'Keel Vibration Services - {MACHINE} monthly vibration route {us(r)}',
            [('kv', [('Route date', us(r)), ('Analyst', v['rep']), ('Limits', 'Alert 0.15 in/s, Danger 0.40 in/s (overall velocity)'),
                     ('Distribution', f"{NAME('P03')}, {NAME('P05')}, {NAME('P02')}")]),
             ('h', 'Readings'), ('table', ['Asset', 'Point', 'Overall (in/s)', 'Status', 'Note'], rows),
             ('h', 'Findings and recommendations')] + [('p', x) for x in recs],
            [BY_NAME[a]['position_id'] for a, _ in extra if BY_NAME[a]['position_id']], story,
            {'report_no': rid, 'reel_vib': f"{pi_at('REEL_DRUM_DS_VIB', t):.2f}"})

    # ─── Spraywell shower audits ───
    for d, f1 in ((B('2026-02-04'), False), (D(str(F1['audit'])), True), (B('2026-08-05'), False), (B('2026-10-21'), False)):
        rid = f'SW-SA-{d:%y%m%d}'; rows = []
        for sh in ('Forming HP shower', '1st press top felt HP shower', '1st press bottom felt HP shower', '2nd press top felt HP shower',
                   '2nd press bottom felt HP shower'):
            pl = F1['shower_plugged_pct'] if f1 and sh.startswith('2nd press top') else rnd.choice([0, 2, 3, 4, 5])
            psi = 280 if sh.startswith('Forming') else 220
            rows.append([sh, f'{psi + rnd.randint(-8, 8)} psi', f'{pl}%', 'Clean nozzles; check strainer' if pl > 10 else 'OK'])
        notes = ['Shower coverage good.'] if not f1 else [
            f"2nd press top felt HP shower: {F1['shower_plugged_pct']}% of nozzles plugged (fibre and stickies). The supply strainer was "
            'packed solid. This felt is not being conditioned: expect it to fill. Nozzles cleaned during the audit; strainer to be cleaned at the next stop.']
        add('shower_audit', rid, 'Spraywell Nozzle Supply', d, f'Spraywell Nozzle Supply - {MACHINE} shower audit {us(d)}',
            [('kv', [('Audit date', us(d)), ('Auditor', VENDORS['Spraywell Nozzle Supply']['rep'])]), ('h', 'Showers'),
             ('table', ['Shower', 'Pressure', 'Nozzles plugged', 'Action'], rows), ('h', 'Comments')] + [('p', n) for n in notes],
            ['form-bottom', 'p1-felt-top', 'p1-felt-bottom', 'p2-felt-top', 'p2-felt-bottom'], 'F1' if f1 else '',
            {'plugged': f"{F1['shower_plugged_pct']}%" if f1 else ''})

    # ─── Ridgeway plate reports at every plate change in the year (+ the F3 field visit) ───
    F3 = PLANTS['F3']
    for pos in ('ref-refa', 'ref-refb'):
        for r in runs[pos]:
            if not r['removed'] or not (Y0 <= r['removed'].date() <= TODAY): continue
            d = r['removed'].date(); rid = f"RR-PL-{d:%y%m%d}-{'A' if pos.endswith('a') else 'B'}"; nm = POS_NAME[pos].replace(' refiner', '')
            wear = 85 if r['story'] == 'F3' else rnd.randint(52, 64)
            se_end = pi_day('REF_B_SE' if pos.endswith('b') else 'REF_A_SE', d - DAY * 2)
            add('plate_report', rid, 'Ridgeway Refining', d, f'Ridgeway Refining - Plate report, {nm} refiner ({us(d)})',
                [('kv', [('Refiner', f'{nm} refiner'), ('Plates', r['style']), ('Installed', us(r['installed'].date())), ('Removed', us(d)),
                         ('Days', (r['removed'] - r['installed']).days)]),
                 ('h', 'Condition'), ('table', ['Measure', 'Result'], [['Bar wear (height)', f'{wear}%'], ['Specific energy at removal', f'{se_end:.1f} kWh/t'],
                                                                      ['Pattern', 'Leading edges rounded' if wear > 70 else 'Even wear']]),
                 ('h', 'Comments'), ('p', 'Wear well above normal for 12 weeks (typical 55-62%). Check stock cleanliness (sand from the cleaners) '
                                          'and the plate gap control.' if wear > 70 else 'Normal wear for the run length.')],
                [pos], r['story'], {'wear': f'{wear}%'})
    se_b = pi_day('REF_B_SE', B('2026-10-25')); se_a = pi_day('REF_A_SE', B('2026-10-25'))
    add('plate_report', tx('RR-FV-261026'), 'Ridgeway Refining', B('2026-10-26'), 'Ridgeway Refining - Field visit: REF 2 plates wearing fast',
        [('kv', [('Visit', tx('10/26/2026')), ('Rep', VENDORS['Ridgeway Refining']['rep']), ('Plates', tx('Set installed 09/30/2026'))]),
         ('h', 'Findings'),
         ('p', f"REF 2 specific energy {se_b:.1f} kWh/t on {md(B('2026-10-25'), '%m/%d')} against {se_a:.1f} on REF 1 at a similar stage; climbing about 1.4% a day since {md(F3['rise_from'], '%m/%d')}. "
               'The previous REF 2 set came out at 85% bar wear. Probable cause: sand carry-over from the LC cleaners into the REF 2 line.'),
         ('h', 'Recommendation'),
         ('p', tx('Change REF 2 plates at the 11/11/2026 outage (6 weeks early) together with REF 1 (due). The mill has one set on hand: '
                  'order a second set now (lead time 10 days). Check the LC cleaner reject rates.'))],
        ['ref-refb', 'ref-refa'], 'F3', {'sets_on_hand': '1'})

    # ─── Pellham roll service for every roll that came out in the year ───
    for pos, rr in runs.items():
        for r in rr:
            if r['kind'] != 'roll' or not r['removed'] or not (Y0 <= r['removed'].date() <= TODAY): continue
            d = r['removed'].date() + DAY * 9; rid = f"PR-RS-{d:%y%m%d}-{pos.split('-')[0]}{pos.split('-')[-1]}"
            add('roll_service', rid, 'Pellham Roll Service', d, f'Pellham Roll Service - Roll service report: {POS_NAME[pos]}',
                [('kv', [('Roll', POS_NAME[pos]), ('Received', us(r['removed'].date() + DAY * 2)), ('Serial', r['serial']),
                         ('In service', f"{(r['removed'] - r['installed']).days} days")]),
                 ('h', 'Work done'), ('table', ['Item', 'As received', 'As shipped'],
                                       [['Cover hardness', f'{rnd.randint(11, 14)} P&J', '10 P&J'], ['Crown', f'{rnd.uniform(.003, .009):.3f} in', '0.000 in (straight)'],
                                        ['Bearings', 'Replaced', 'New, sealed'], ['TIR', f'{rnd.uniform(.002, .006):.3f} in', '0.001 in']])],
                [pos], '', {})

    # ─── Brightwater steam surveys ───
    for d, f5 in ((B('2026-03-18'), False), (B('2026-10-14'), True)):
        rid = f'BS-SS-{d:%y%m%d}'; rows = []
        for s in range(1, 5):
            rows.append([f'{ORD(s)} section rotary joint (DS)', f"{pi_day(f'DRY{s}_STEAM_P', d):.0f} psig", f"{pi_day(f'DRY{s}_DP', d):.2f} psi",
                         'Seal worn: replace joint' if (f5 and s == 3) else 'OK'])
        notes = ['All joints and syphons within spec.'] if not f5 else [
            f"The 3rd section DS rotary joint has had three seal failures this year ({', '.join(md(D(e['start']), '%m/%d') for e in PLANTS['F5']['events'])}), each a 2-3 h stop. The carbon ring "
            'wears unevenly: the joint body is misaligned on its support bracket. Replace the joint and re-align the bracket at the next outage. '
            'Seal kits alone will keep failing.']
        add('steam_survey', rid, 'Brightwater Steam Systems', d, f'Brightwater Steam Systems - {MACHINE} steam and condensate survey {us(d)}',
            [('kv', [('Survey date', us(d)), ('Engineer', VENDORS['Brightwater Steam Systems']['rep'])]), ('h', 'Rotary joints and syphons'),
             ('table', ['Joint', 'Steam', 'Syphon ΔP', 'Condition'], rows), ('h', 'Comments')] + [('p', n) for n in notes],
            [], 'F5' if f5 else '', {})

    # ─── RCFA write-ups ───
    for r in rec['rcfas']:
        e = r['event']; rid = r['id']
        acts = [[a.id, a.title.replace(f' ({rid})', ''), NAME(a.owner), us(a.due), a.progress_at(TODAY)] for a in r['actions']]
        timeline = [[e['start'].strftime('%m/%d/%Y %H:%M'), f"{CAUSE_TEXT[e['cause']]}: {e['asset']}. {e['note']}"],
                    [e['end'].strftime('%m/%d/%Y %H:%M'), f"Running again ({r['downtime_h']} h)."]]
        if e.get('wo'): timeline.append([us(e['start'].date()), f"Emergency WO {e['wo'].no}"])
        blocks = [('kv', [('RCFA', rid), ('Event', f"{e['start']:%m/%d/%Y %H:%M}"), ('Equipment', e['asset']), ('Area', SECTION_NAME.get(BY_NAME[e['asset']]['section'], '')),
                          ('Downtime', f"{r['downtime_h']} h"), ('Production loss', r['loss']), ('Lead', NAME(r['lead'])), ('Status', r['status'])]),
                  ('h', 'Timeline'), ('table', ['When', 'What'], timeline),
                  ('h', 'Root cause'), ('p', r['root_cause']), ('h', 'Contributing factors'), ('p', r['contributing']),
                  ('h', f'Actions (as of {us(TODAY)})'), ('table', ['Planner ID', 'Action', 'Owner', 'Due', 'Status'], acts)]
        render_docx(os.path.join(out, 'docs', 'rcfa', f'{rid}.docx'), f"{rid}: {r['title']}", blocks, rid)
        manifest.append(dict(doc_id=rid, kind='rcfa', vendor='', date=e['start'].date().isoformat(), title=r['title'], positions=[], story=r['story'], fields={}))

    # ─── drawings and reference charts ───
    def drawing(did, title, cols, rows):
        render_pdf(os.path.join(out, 'docs', 'drawings', f'{did}.pdf'), f'{HEAD} drawings', title,
                   [('p', 'Machine direction right to left. Tending side (TS) at the bottom of the drawing.'), ('table', cols, rows)], did)
        manifest.append(dict(doc_id=did, kind='drawing', vendor='', date='', title=title, positions=[], story='', fields={}))
    rows = []
    for s in range(1, 5):
        cans = ', '.join(str(c) for c in range((s - 1) * 5 + 1, s * 5 + 1))
        rows.append([f'{ORD(s)} dryer section', 'Uno-run', cans, ', '.join(f'{ORD(s)} section felt roll {k}' for k in range(1, 6)), f'{ORD(s)} section rotary joint (DS)'])
    drawing('SM-DWG-301', f'{MACHINE} dryer sections: cans, felt rolls and rotary joints', ['Section', 'Felt run', 'Cans', 'Felt rolls', 'Steam joint'], rows)
    drawing('SM-DWG-201', f'{MACHINE} press section layout', ['Nip', 'Top', 'Bottom', 'Felts', 'Uhle boxes'],
            [[f'{ORD(n)} press', f'{ORD(n)} press top roll', f'{ORD(n)} press bottom roll', f'{ORD(n)} press top felt, {ORD(n)} press bottom felt',
              f'{ORD(n)} press top felt Uhle box, {ORD(n)} press bottom felt Uhle box'] for n in (1, 2)])
    drawing('SM-DWG-101', f'{MACHINE} roll list', ['Roll', 'Position id', 'Vendor', 'Target life (wk)'],
            [[POS_NAME[p_], p_, runs[p_][-1]['vendor'], runs[p_][-1]['target_days'] // 7] for p_ in runs if runs[p_][-1]['kind'] == 'roll'])
    REF = [('SM-REF-01', 'Steam pressure by grade (4 sections)', ['Grade', '1st (psig)', '2nd (psig)', '3rd (psig)', '4th (psig)', 'Limit (psig)'],
            [[GLABEL[g], *[f"{BY_G[f'DRY{s}_STEAM_P'][i]:.0f}" for s in range(1, 5)], '140']
             for i, g in enumerate(GRADE_IDS)]),
           ('SM-REF-02', 'Clothing and plate life targets', ['Position', 'Target (weeks)', 'Vendor', 'Style'],
            [[POS_NAME[k], v['life_w'], v['vendor'], v['style']] for k, v in CFG['positions'].items()]),
           ('SM-REF-03', 'Grade speeds and production', ['Grade', 'Speed (fpm)', 'Basis weight (lb/1000 ft2)', 'Full rate (t/h)'],
            [[GLABEL[g], GRADES[g]['sp'], GRADES[g]['bw'], f"{full_tph(g):.1f}"] for g in GRADE_IDS])]
    for rid, title, cols, rows in REF:
        render_pdf(os.path.join(out, 'docs', 'reference', f'{rid}.pdf'), f'{HEAD} reference', title, [('table', cols, rows)], rid)
        write_csv(os.path.join(out, 'docs', 'reference', 'tables', f'{rid}.csv'), cols, [dict(zip(cols, r)) for r in rows])
        manifest.append(dict(doc_id=rid, kind='reference', vendor='', date='', title=title, positions=[], story='', fields={}))
    return manifest
