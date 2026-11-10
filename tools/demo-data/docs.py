"""MM LLM demo data, phase 4: the documents — vendor reports, RCFA write-ups, drawings and reference charts.

    demo-data/out/docs/vendor/<vendor>/<report>.pdf   clothing surveys, trial reports, vibration routes, roll service,
                                                      shower audits, refiner plate reports
    demo-data/out/docs/rcfa/<RCFA id>.docx            one write-up per RCFA in the log
    demo-data/out/docs/drawings/<DWG no>.pdf          schematic machine drawings (machine direction right to left)
    demo-data/out/docs/reference/<REF id>.pdf (+ tables/<REF id>.csv)  reference charts, as a document and a typed table
    demo-data/out/_truth/documents.json               answer key: every document's fields an extractor should find

    python3 tools/demo-data/docs.py            # generate (after structured.py and pi_bonvoy.py)
    python3 tools/demo-data/docs.py --check    # generate to a temp folder and check text extraction against the answer key

Measured values come from the generated data, so documents agree with everything else: vibration route readings
and refiner specific energy are read from the Pi series; RCFA timelines, WO numbers and actions come from the
phase 2 exports. A few documents are deliberately messy for the ingest path: scanned pages with no text layer
(they need OCR) and one rotated page.
"""
import csv, io, json, os, random, shutil, sys, tempfile, datetime as dt
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, 'demo-data')
SEED = 4404
D = dt.date.fromisoformat
DAY = dt.timedelta(days=1)

def read(path):
    with open(path) as f: return list(csv.DictReader(f))

EQUIP = read(os.path.join(DATA, 'backbone', 'equipment.csv'))
BY_NAME = {e['name']: e for e in EQUIP}
BY_POS = {e['position_id']: e for e in EQUIP if e['position_id']}
SECTION_NAME = {e['section']: e['name'][4:] for e in EQUIP if e['kind'] == 'section'}
VENDORS = {v['id']: v for v in read(os.path.join(DATA, 'backbone', 'vendors.csv'))}
PEOPLE = {p['id']: p for p in read(os.path.join(DATA, 'backbone', 'roster.csv'))}
NAME = lambda pid: PEOPLE[pid]['name']
OUTAGES = read(os.path.join(DATA, 'backbone', 'outages.csv'))
IN_YEAR = [o for o in OUTAGES if D(o['start'][:10]) <= D('2026-10-31')]
odate = lambda o: D(o['start'][:10])

# Clothing / plate changes (the same schedule as structured.py and pi_bonvoy.py)
CHANGES = {
    'p2-felt-top': ['2025-09-17', '2025-12-10', '2026-03-04', '2026-04-15', '2026-07-08', '2026-10-05'],
    'form-bottom': ['2025-09-17', '2025-12-10', '2026-01-21', '2026-02-18', '2026-03-04', '2026-05-27', '2026-08-19'],
    'form-top': ['2025-09-17', '2025-12-10', '2026-03-04', '2026-05-27', '2026-08-19'],
    'ref-bp1': ['2025-09-17', '2025-12-10', '2026-03-04', '2026-05-27', '2026-08-19'],
    'ref-bp2': ['2025-09-17', '2025-12-10', '2026-03-04', '2026-05-27', '2026-08-19'],
    'ref-tp1': ['2025-10-29', '2026-01-21', '2026-04-15', '2026-07-08', '2026-10-05'],
    'ref-tp2': ['2025-10-29', '2026-01-21', '2026-04-15', '2026-07-08', '2026-10-05'],
    'd1-felt': ['2025-04-16', '2026-04-15'], 'd2-felt-bottom': ['2025-07-09', '2026-07-08'],
    'd2-felt-top': ['2025-10-06', '2026-10-05'], 'd3-felt-bottom': ['2025-10-06', '2026-10-05'], 'd3-felt-top': ['2025-10-06'],
}
EVERY = ['p1-felt-top', 'p-tandem-felt']
LIFE = {'p1-felt-top': 6, 'p-tandem-felt': 6, 'p2-felt-top': 12, 'form-bottom': 12, 'form-top': 14, 'd1-felt': 52, 'd2-felt-top': 52,
        'd2-felt-bottom': 52, 'd3-felt-top': 65, 'd3-felt-bottom': 78, 'ref-bp1': 12, 'ref-bp2': 12, 'ref-tp1': 12, 'ref-tp2': 12}
STYLE = {'form-top': 'NX-2160 triple layer', 'form-bottom': 'NX-2740 triple layer', 'p1-felt-top': 'Seamed felt, 1350 gsm',
         'p2-felt-top': 'Seamed felt, 1450 gsm', 'p-tandem-felt': 'Bottom felt, 1600 gsm', 'd1-felt': 'Dryer fabric, spiral seam',
         'd2-felt-top': 'Dryer fabric, pin seam', 'd2-felt-bottom': 'Dryer fabric, pin seam', 'd3-felt-top': 'Dryer fabric, spiral seam',
         'd3-felt-bottom': 'Dryer fabric, spiral seam'}

def changes(pos):
    if pos in EVERY: return ['2025-09-17', '2025-10-29'] + [o['start'][:10] for o in OUTAGES]
    return CHANGES[pos]

def installed_before(pos, d):
    """Date the clothing/plates in `pos` on day d were installed (changes on d itself are the new set)."""
    return max(D(x) for x in changes(pos) if D(x) < d)

def changed_on(pos, d):
    return any(D(x) == d for x in changes(pos))


# ═════════════════════════ Generated data the documents read ═════════════════════════
class Pi:
    def __init__(self, folder):
        self.v = {}
        for fn in sorted(os.listdir(os.path.join(folder, 'hourly'))):
            for r in csv.DictReader(open(os.path.join(folder, 'hourly', fn))):
                t = dt.datetime.fromisoformat(r.pop('Timestamp'))
                for k, x in r.items():
                    if x != '': self.v.setdefault(k, {})[t] = float(x)
    def avg(self, tag, d, h0=0, h1=24):
        xs = [self.v[tag].get(dt.datetime.combine(d, dt.time(h))) for h in range(h0, h1)]
        xs = [x for x in xs if x is not None and x > 0]
        return sum(xs) / len(xs) if xs else None
    def last_running_avg(self, tag, before):
        d = before - DAY
        while self.avg(tag, d) is None: d -= DAY
        return self.avg(tag, d), d


# ═════════════════════════ Rendering ═════════════════════════
# A document is a list of blocks: ('h', text) | ('p', text) | ('kv', [(k, v), ...]) | ('table', header, rows) | ('break',)
def render_pdf(path, head, title, blocks, doc_id, rotate_page=None):
    from reportlab import rl_config
    rl_config.invariant = 1
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    ss = getSampleStyleSheet()
    body = ParagraphStyle('b', parent=ss['BodyText'], fontSize=9.5, leading=13)
    h2 = ParagraphStyle('h', parent=ss['Heading2'], fontSize=11.5, spaceBefore=10, spaceAfter=4)
    cell = ParagraphStyle('c', parent=body, fontSize=8, leading=10)
    flow = [Paragraph(escape(title), ParagraphStyle('t', parent=ss['Title'], fontSize=15, alignment=0, spaceAfter=8))]
    for b in blocks:
        if b[0] == 'h': flow.append(Paragraph(escape(b[1]), h2))
        elif b[0] == 'p': flow.append(Paragraph(escape(b[1]), body))
        elif b[0] == 'break': flow.append(PageBreak())
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
    data = buf.getvalue()
    if rotate_page is not None:
        from pypdf import PdfReader, PdfWriter
        r, w = PdfReader(io.BytesIO(data)), PdfWriter()
        for i, p in enumerate(r.pages):
            if i == rotate_page: p.rotate(90)
            w.add_page(p)
        out = io.BytesIO(); w.write(out); data = out.getvalue()
    open(path, 'wb').write(data)

def _font(size, bold=False, mono=False):
    from PIL import ImageFont
    base = '/usr/share/fonts/truetype/dejavu/DejaVuSans' + ('Mono' if mono else '') + ('-Bold' if bold else '') + '.ttf'
    try: return ImageFont.truetype(base, size)
    except OSError: return ImageFont.load_default(size=size)

def render_scanned(path, head, title, blocks, doc_id, seed):
    """Image-only PDF that looks like a photocopy: no text layer, slightly skewed, speckled."""
    from PIL import Image, ImageDraw
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    rng = random.Random(seed)
    W, H = 1275, 1650
    pages, img, y = [], None, 0
    def new():
        nonlocal img, y
        img = Image.new('L', (W, H), 250); y = 150; dr = ImageDraw.Draw(img)
        dr.text((110, 70), head, font=_font(26, True), fill=20); dr.text((W - 110, 70), doc_id, font=_font(20), fill=40, anchor='ra')
        dr.line((110, 112, W - 110, 112), fill=60, width=2); pages.append(img)
    def line(text, f, gap=8):
        nonlocal y
        if y > H - 160: new()
        ImageDraw.Draw(img).text((110, y), text, font=f, fill=25); y += f.size + gap
    def wrap(text, f, width=W - 220):
        words, cur = text.split(), ''
        for w in words:
            if ImageDraw.Draw(Image.new('L', (1, 1))).textlength(cur + ' ' + w, font=f) > width and cur: line(cur, f); cur = w
            else: cur = (cur + ' ' + w).strip()
        if cur: line(cur, f)
    new(); wrap(title, _font(34, True)); y += 10
    for b in blocks:
        if b[0] == 'h': y += 12; line(b[1], _font(26, True))
        elif b[0] == 'p': wrap(b[1], _font(21))
        elif b[0] == 'kv':
            for k, v in b[1]: wrap(f'{k}: {v}', _font(21))
        elif b[0] == 'table':
            cols = [b[1]] + [list(map(str, r)) for r in b[2]]
            wd = [max(len(str(r[i])) for r in cols) for i in range(len(b[1]))]
            for n, r in enumerate(cols):
                line('  '.join(str(x).ljust(wd[i]) for i, x in enumerate(r)), _font(17, n == 0, mono=True), 5)
            y += 8
        elif b[0] == 'break': new()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = canvas.Canvas(path, pagesize=letter, invariant=1)
    for p in pages:
        dr = ImageDraw.Draw(p)
        for _ in range(900): x, yy = rng.randrange(W), rng.randrange(H); dr.point((x, yy), fill=rng.choice([80, 120, 160]))
        p = p.rotate(rng.uniform(-.9, .9), fillcolor=235, resample=Image.BICUBIC)
        c.drawImage(ImageReader(p), 0, 0, width=letter[0], height=letter[1]); c.showPage()
    c.save()


# ═════════════════════════ Vendor reports ═════════════════════════
def us(d): return d.strftime('%m/%d/%Y')

def vendor_reports(pi, rnd, add):
    # ---- Clothing surveys at every outage in the year ----
    SURVEY = {'V-NB': ['form-top', 'form-bottom', 'd1-felt', 'd2-felt-top', 'd2-felt-bottom'], 'V-HF': ['p1-felt-top', 'p2-felt-top'],
              'V-MP': ['p-tandem-felt']}
    plan = [(o, v) for o in IN_YEAR for v in SURVEY] + [(o, 'V-CT') for o in IN_YEAR if o['start'][:10] in ('2026-07-08', '2026-10-05')]
    for o, vid in plan:
        d = odate(o); v = VENDORS[vid]; poss = SURVEY.get(vid, ['d3-felt-top', 'd3-felt-bottom'])
        rid = f"{vid[2:]}-SV-{d.strftime('%y%m%d')}"
        rows, notes, fields = [], [], {'report_no': rid, 'vendor': v['name'], 'survey_date': us(d)}
        for pos in poss:
            if pos == 'form-bottom' and D('2025-12-10') < d <= D('2026-01-21'):
                rows.append([BY_POS[pos]['name'], 'Halden PF-3315 (trial)', '-', '-', '-', '-', 'Not surveyed - Halden trial fabric', 'See Halden trial report'])
                continue
            inst = installed_before(pos, d); age = (d - inst).days / 7; f = age / LIFE[pos]
            chg = changed_on(pos, d) or (pos == 'form-bottom' and d == D('2026-03-04'))
            felt = pos.startswith('p'); dryer = pos.startswith('d')
            cal = (3.2 - .6 * f if felt else 1.8 - .2 * f if dryer else .95 - .1 * f) + rnd.uniform(-.03, .03)
            perm = (30 - 14 * f if felt else 90 - 30 * f if dryer else 480 - 60 * f) * rnd.uniform(.97, 1.03)
            third = f'{650 + 250 * f + rnd.uniform(-25, 25):.0f} gsm water' if felt else (f'{20 + 70 * f + rnd.uniform(-3, 3):.0f}% wear layer' if not dryer else 'Seam OK')
            cond = 'Good' if f < .5 else ('Normal wear' if f < .95 else 'End of life')
            rec = 'Change at this outage as planned' if chg else 'Continue'
            if pos == 'p2-felt-top' and d == D('2026-04-15'):
                third = '1,150 gsm water'; cond = 'High fill - heavy contamination (68% fill vs ~45% typical at 6 weeks)'
                rec = 'Pull felt now. Check 2nd press HP shower nozzles and shower water quality before the next felt goes on.'
                notes.append('2nd press top felt: fill level and water content far above normal for 6 weeks of running. Uhle box vacuum '
                             'trend (Pi) has been climbing since mid-March. Pattern points to shower cleaning, not felt design.')
                fields.update(p2_condition='High fill', fill='68%')
            rows.append([BY_POS[pos]['name'], STYLE.get(pos, ''), us(inst), f'{age:.1f}', f'{cal:.2f}', f'{perm:.0f}', third, f'{cond}. {rec}'])
        if not notes: notes.append('No unusual wear. Clothing running as expected for its age.')
        blocks = [('kv', [('Customer', 'PM1 (two-ply linerboard)'), ('Survey date', us(d)), ('Issued', us(d + 2 * DAY)),
                          ('Surveyed by', v['rep']), ('Distribution', f"{NAME('P01')}, {NAME('P04')}")]),
                  ('h', 'Measurements'),
                  ('table', ['Position', 'Style', 'Installed', 'Age (wk)', 'Caliper (mm)', 'Air perm (cfm)', 'Fill / wear', 'Condition and recommendation'], rows),
                  ('h', 'Comments')] + [('p', n) for n in notes]
        story = 'S02' if 'p2_condition' in fields else ''
        add(kind='clothing_survey', id=rid, vendor=vid, date=d, title=f'{v["name"]} - Clothing survey, PM1 outage {us(d)}', blocks=blocks,
            fields=fields, positions=poss, story=story)

    # ---- Halden trial: start-up and end-of-trial (S06) ----
    v = VENDORS['V-HF']
    trial = sum(pi.avg('PM1:FORM_BASE_COUCH_VAC', D('2025-12-18') + k * DAY) for k in range(7)) / 7
    nxt = sum(pi.avg('PM1:FORM_BASE_COUCH_VAC', D('2026-01-29') + k * DAY) for k in range(7)) / 7
    add(kind='trial_report', id='HF-TR-251210', vendor='V-HF', date=D('2025-12-10'), story='S06',
        title='Halden Felt Co. - Trial start-up report: PF-3315 on PM1 base ply', positions=['form-bottom'],
        blocks=[('kv', [('Trial', 'PF-3315 forming fabric, base ply'), ('Installed', '12/10/2025'), ('Halden contact', v['rep']),
                        ('Mill contact', NAME('P04')), ('Incumbent', 'Northbank NX-2740 triple layer')]),
                ('h', 'Targets'), ('table', ['Measure', 'Target', 'Basis'], [['Formation index', 'equal or better', 'QCS'],
                 ['Couch vacuum', 'within 0.3 inHg of incumbent', 'Pi PM1:FORM_BASE_COUCH_VAC'], ['Speed on 33#', 'no loss', 'Pi PM1:SPEED'],
                 ['Run life', '12 weeks', 'outage cycle']]),
                ('p', 'Start-up normal. Break-in showers at reduced pressure for the first 8 hours.')],
        fields={'report_no': 'HF-TR-251210', 'trial': 'PF-3315', 'installed': '12/10/2025'})
    add(kind='trial_report', id='HF-TR-260121', vendor='V-HF', date=D('2026-01-21'), story='S06',
        title='Halden Felt Co. - End of trial report: PF-3315 on PM1 base ply', positions=['form-bottom'],
        blocks=[('kv', [('Trial', 'PF-3315 forming fabric, base ply'), ('Ran', '12/10/2025 to 01/21/2026 (6 weeks)'), ('Halden contact', v['rep'])]),
                ('h', 'Results'), ('table', ['Measure', 'Target', 'Result'], [['Formation index', 'equal or better', 'Equal (no change on QCS)'],
                 ['Couch vacuum (days 8-14)', 'within 0.3 inHg', f'{trial:.1f} inHg vs {nxt:.1f} inHg on the NX-2740 at the same age (+{trial - nxt:.1f})'],
                 ['Speed on 33#', 'no loss', 'About 15 fpm lower on 33# (drainage limited)']]),
                ('h', 'Conclusion'), ('p', 'Formation was good but drainage was slower than the incumbent. The mill decided to return to '
                                          'the Northbank NX-2740 at the 01/21/2026 outage. Halden suggests a more open bottom layer for any future trial.')],
        fields={'report_no': 'HF-TR-260121', 'result': 'About 15 fpm lower on 33#', 'decision': 'return to the Northbank NX-2740'})

    # ---- Keel monthly vibration route ----
    v = VENDORS['V-KV']
    PI_POINTS = [(t, a, side) for t, a, side in [
        ('PM1:DRY1_C05_DS_VIB', 'Dryer can 5', 'DS'), ('PM1:DRY2_C15_DS_VIB', 'Dryer can 15', 'DS'), ('PM1:DRY2_C21_DS_VIB', 'Dryer can 21', 'DS'),
        ('PM1:DRY2_C27_DS_VIB', 'Dryer can 27', 'DS'), ('PM1:DRY2_C27_TS_VIB', 'Dryer can 27', 'TS'), ('PM1:DRY2_C33_DS_VIB', 'Dryer can 33', 'DS'),
        ('PM1:DRY3_C49_DS_VIB', 'Dryer can 49', 'DS'), ('PM1:DRY3_C61_DS_VIB', 'Dryer can 61', 'DS'),
        ('PM1:PRESS2_BOT_DS_VIB', '2nd press bottom roll', 'DS'), ('PM1:CAL_BOT_DS_VIB', 'Calender bottom roll', 'DS')]]
    OTHER = ['Top ply fan pump', 'Base ply fan pump', 'Vacuum pump 1', 'Vacuum pump 2', 'Vacuum pump 3', 'Vacuum pump 4', 'BP 1 refiner motor',
             'BP 2 refiner motor', 'TP 1 refiner motor', 'TP 2 refiner motor', '1st section drive group', '2nd section drive group',
             '3rd section drive group', 'Reel drum', 'Lumpbreaker roll', '1st press top roll', '1st press bottom roll', '2nd press top roll',
             'Calender top roll', 'Dryer can 40']
    base = {a: rnd.uniform(.04, .09) for a in OTHER}
    routes = [D(f'2025-{m}-14') for m in (11, 12)] + [D(f'2026-{m:02d}-14') for m in range(1, 10)] + [D('2026-10-19')]
    for n, d in enumerate(routes):
        rid = f"KV-VR-{d.strftime('%y%m%d')}"; rows = []; findings = []; fields = {'report_no': rid, 'route_date': us(d)}
        for tag, a, side in PI_POINTS:
            x = pi.avg(tag, d); status, note = ('OK', '')   # route reading = that day's average level
            if x >= .30: status = 'Danger'
            elif x >= .15: status = 'Alert'
            if tag == 'PM1:DRY2_C27_DS_VIB' and d == D('2026-09-14'):
                status, note = 'Watch', 'BPFO tone at low amplitude (early outer-race defect). Re-check next route.'
                findings.append('Dryer can 27 DS: overall level normal (0.07 in/s) but the spectrum shows an outer-race defect '
                                'frequency (BPFO) at low amplitude. Watch; re-check on the next route.')
                fields['c27_ds'] = f'{x:.2f}'
            if tag == 'PM1:DRY2_C27_DS_VIB' and d == D('2026-10-19'):
                status, note = 'Alert', 'BPFO with harmonics and sidebands - outer race defect confirmed. Replace at next opportunity.'
                findings.append(f'Dryer can 27 DS: {x:.2f} in/s and rising, BPFO with harmonics and sidebands. Outer race defect confirmed. '
                                'Bearing temperature also up about 8 °F since the annual outage restart (Pi). Recommend replacement at the next '
                                'opportunity (11/11 outage) and monitoring twice per shift until then.')
                fields['c27_ds'] = f'{x:.2f}'; fields['c27_status'] = 'Alert'
            rows.append([a, side, f'{x:.2f}', status, note])
        for a in OTHER:
            x = base[a] * rnd.uniform(.9, 1.1)
            if a == 'Vacuum pump 2' and d >= D('2026-08-14'):
                x = {D('2026-08-14'): .11, D('2026-09-14'): .13, D('2026-10-19'): .16}[d]
            status = 'Alert' if x >= .15 else 'OK'
            note = 'Misalignment pattern (2x running speed); check coupling alignment' if (a == 'Vacuum pump 2' and x >= .13) else ''
            if note and d == D('2026-10-19'): findings.append('Vacuum pump 2: 0.16 in/s, 2x running-speed peak - check coupling alignment; packing leak reported on BUS.')
            rows.append([a, 'DS' if 'pump' not in a else 'Motor OB', f'{x:.2f}', status, note])
        if not findings: findings.append('All points within limits. No new findings.')
        blocks = [('kv', [('Route date', us(d)), ('Analyst', v['rep']), ('Machine', 'PM1, running' + ('' if d.month != 10 else ' (post-annual)')),
                          ('Limits', 'Overall velocity, in/s peak: Alert 0.15, Danger 0.30 (see REF-08)')]),
                  ('h', 'Findings')] + [('p', f) for f in findings] + [
                  ('h', 'Readings'), ('table', ['Point', 'Side', 'Overall (in/s)', 'Status', 'Notes'], rows)]
        story = 'S01' if 'c27_ds' in fields else ''
        add(kind='vibration_route', id=rid, vendor='V-KV', date=d, title=f'Keel Vibration Services - PM1 monthly route, {us(d)}', blocks=blocks,
            fields=fields, story=story, positions=[], rotate=1 if d == D('2026-07-14') else None)

    # ---- Roll service ----
    add(kind='roll_service', id='PR-RS-260304', vendor='V-PR', date=D('2026-03-04'), story='S03', positions=['lumpbreaker'],
        title='Pellham Roll Service - Lumpbreaker roll inspection', fields={'report_no': 'PR-RS-260304', 'hardness': '35 P&J'},
        blocks=[('kv', [('Roll', 'Lumpbreaker roll (base ply)'), ('Inspected', '03/04/2026, in place'), ('Inspector', VENDORS['V-PR']['rep'])]),
                ('table', ['Check', 'Spec', 'Found'], [['Cover hardness', '35 ±3 P&J', '35 P&J'], ['Cover surface', 'no damage', 'Light marking at TS from the 02/18 wad'],
                                                        ['Doctor contact', 'even', 'Even after new blade']]),
                ('p', 'Cover is serviceable. No regrind needed. Marking at TS is cosmetic. Recommend the new doctor blade PM every outage.')])
    add(kind='roll_service', id='TR-RS-260527', vendor='V-TR', date=D('2026-05-27'), story='S07', positions=['cal-bottom'], scanned=True,
        title='Teague Roll Works - Calender bottom roll inspection', fields={'report_no': 'TR-RS-260527', 'hardness': '87.5', 'crown': '0.017'},
        blocks=[('kv', [('Roll', 'Calender bottom roll (soft cover)'), ('Inspected', '05/27/2026'), ('Inspector', VENDORS['V-TR']['rep'])]),
                ('table', ['Check', 'Spec', 'Found'], [['Cover hardness (Shore D)', '85 ±2', '87.5'], ['Crown (in)', '0.020 ±0.003', '0.017'],
                                                        ['Cover thickness (in)', '>= 0.35', '0.42']]),
                ('p', 'Cover hardness has drifted high and crown is at the low edge of tolerance. Recommend changing the roll at the '
                      'October annual outage and regrinding. Book a shop slot by end of August.')])
    add(kind='roll_service', id='PR-RS-261009', vendor='V-PR', date=D('2026-10-09'), story='S09', positions=['p1-roll-bottom'],
        title='Pellham Roll Service - 1st press bottom roll recover', fields={'report_no': 'PR-RS-261009', 'new_cover': '10 P&J'},
        blocks=[('kv', [('Roll', '1st press bottom roll (suction)'), ('Work', 'Recover, drill and grind'), ('Shipped', '10/09/2026')]),
                ('table', ['Check', 'Spec', 'Found'], [['Cover hardness', '10 ±2 P&J', '10 P&J'], ['Open area', '22 ±1%', '22%'], ['Crown (in)', '0.000', '0.000']]),
                ('p', 'Roll recovered and installed during the annual outage.')])
    add(kind='roll_service', id='TR-RS-261020', vendor='V-TR', date=D('2026-10-20'), story='S07', positions=['cal-bottom'],
        title='Teague Roll Works - Calender bottom roll regrind (post-grind report)', fields={'report_no': 'TR-RS-261020', 'hardness': '85.2', 'crown': '0.020'},
        blocks=[('kv', [('Roll', 'Calender bottom roll (soft cover)'), ('Removed', '10/06/2026 (annual outage)'), ('Ground', '10/16/2026')]),
                ('table', ['Check', 'Spec', 'As received', 'As shipped'], [['Cover hardness (Shore D)', '85 ±2', '87.9', '85.2'],
                 ['Crown (in)', '0.020 ±0.003', '0.016', '0.020'], ['Cover thickness (in)', '>= 0.35', '0.42', '0.39']]),
                ('p', 'Ground to spec. Roughly two more regrinds left on this cover.')])

    # ---- Spraywell shower audits ----
    SHOWERS = [('Top ply HP shower', 48, 250), ('Base ply HP shower', 48, 250), ('1st press top felt HP shower', 50, 250),
               ('2nd press top felt HP shower', 50, 250), ('Tandem felt HP shower', 50, 250), ('Top ply LP lube shower', 60, 40),
               ('Base ply LP lube shower', 60, 40), ('Calender doctor shower', 30, 60)]
    for d, scanned in [(D('2026-01-21'), True), (D('2026-04-15'), False), (D('2026-07-08'), False), (D('2026-10-07'), False)]:
        rid = f"SN-SA-{d.strftime('%y%m%d')}"; rows = []; fields = {'report_no': rid, 'audit_date': us(d)}; notes = []
        for name, n, psi in SHOWERS:
            plugged = rnd.choice([0, 0, 1, 1, 2])
            if name.startswith('2nd press') and d == D('2026-04-15'): plugged = 9
            if name.startswith('2nd press') and d == D('2026-01-21'): plugged = 2
            pct = round(100 * plugged / n)
            rows.append([name, n, plugged, f'{pct}%', f'{psi * rnd.uniform(.96, 1.02):.0f}', 'OK', 'All plugged nozzles replaced' if plugged else ''])
            if pct >= 10:
                notes.append(f'{name}: {plugged} of {n} nozzles plugged ({pct}%). Debris in the header points to the shower water. '
                             'Recommend a finer strainer on the HP header and a monthly nozzle check.')
                fields['p2_plugged'] = f'{pct}%'
        if not notes: notes.append('No significant plugging. Pressures normal.')
        add(kind='shower_audit', id=rid, vendor='V-SN', date=d, title=f'Spraywell Nozzle Supply - PM1 shower audit, {us(d)}',
            story='S02' if 'p2_plugged' in fields else '', scanned=scanned, positions=[], fields=fields,
            blocks=[('kv', [('Audit date', us(d)), ('Technician', VENDORS['V-SN']['rep'])]), ('h', 'Findings')] + [('p', x) for x in notes] +
                   [('h', 'Shower detail'), ('table', ['Shower', 'Nozzles', 'Plugged', 'Plugged %', 'Pressure (psi)', 'Oscillator', 'Action'], rows)])

    # ---- Refiner plate reports ----
    for pos, vid, ref in [('ref-bp1', 'V-RR', 'BP 1'), ('ref-bp2', 'V-RR', 'BP 2'), ('ref-tp1', 'V-BP', 'TP 1'), ('ref-tp2', 'V-BP', 'TP 2')]:
        tag = f"PM1:REF_{ref.replace(' ', '')}_SE"
        for x in changes(pos):
            d = D(x)
            if not D('2025-11-01') <= d <= D('2026-10-31'): continue
            inst = installed_before(pos, d); wk = (d - inst).days / 7; se, sd = pi.last_running_avg(tag, d)
            loss = .9 + .5 * wk / 12 + rnd.uniform(-.1, .1)
            rid = f"{vid[2:]}-PR-{d.strftime('%y%m%d')}-{ref.replace(' ', '')}"
            add(kind='plate_report', id=rid, vendor=vid, date=d, positions=[pos], story='S04' if pos == 'ref-bp2' and d == D('2026-08-19') else '',
                title=f'{VENDORS[vid]["name"]} - Refiner plate change report, {ref} refiner, {us(d)}',
                fields={'report_no': rid, 'refiner': f'{ref} refiner', 'run_weeks': f'{wk:.1f}', 'se_at_removal': f'{se:.1f}'},
                blocks=[('kv', [('Refiner', f'{ref} refiner'), ('Plates removed', f'Installed {us(inst)}, removed {us(d)} ({wk:.1f} weeks)'),
                                ('Specific energy before removal', f'{se:.1f} kWh/t (Pi daily average, {us(sd)})'), ('Representative', VENDORS[vid]['rep'])]),
                        ('table', ['Measure', 'Value', 'Comment'], [['Bar height loss', f'{loss:.1f} mm', 'Normal for run time'],
                                                                   ['Edge rounding', 'Normal', ''], ['Plate damage', 'None', '']]),
                        ('p', 'New plates installed, same pattern. Gap set and loaded to the normal curve after start-up.')])
    se1, _ = pi.last_running_avg('PM1:REF_BP1_SE', D('2026-10-05')); se2, _ = pi.last_running_avg('PM1:REF_BP2_SE', D('2026-10-05'))
    add(kind='plate_report', id='RR-PI-261007', vendor='V-RR', date=D('2026-10-07'), story='S04', positions=['ref-bp1', 'ref-bp2'],
        title='Ridgeway Refining - Base ply refiner plate inspection (annual outage)',
        fields={'report_no': 'RR-PI-261007', 'bp2_edge': 'Elevated', 'bp2_loss': '1.6 mm'},
        blocks=[('kv', [('Inspected', '10/07/2026, plates in place (installed 08/19/2026, 7 weeks)'), ('Representative', VENDORS['V-RR']['rep'])]),
                ('table', ['Refiner', 'Bar height loss', 'Edge rounding', 'SE before outage (kWh/t)', 'Recommendation'],
                 [['BP 1 refiner', '0.8 mm', 'Normal', f'{se1:.1f}', 'Change at 11/11 outage as planned'],
                  ['BP 2 refiner', '1.6 mm', 'Elevated', f'{se2:.1f}', 'Change at the next opportunity; check stock for grit']]),
                ('p', 'BP 2 shows about twice the expected bar edge rounding for 7 weeks of running. With both base ply refiners due '
                      'at the 11/11 outage, two sets of plates are needed.')])


# ═════════════════════════ RCFA write-ups ═════════════════════════
RCFA_DETAIL = {
    'RCFA-2026-02': dict(event='At 02:40 on 02/18/2026 the base ply forming fabric was found with a 4-inch hole at the tending side. '
                               'A wad of stock had passed under the lumpbreaker doctor and through the couch nip. The machine was down '
                               '10 hours to change the fabric using the floor spare.',
                         whys=[('Why was there a hole in the base ply fabric?', 'A wad passed through the couch nip.'),
                               ('Why did a wad reach the couch nip?', 'The lumpbreaker doctor blade was worn and let stock build up and release.'),
                               ('Why was the blade worn?', 'The blade had no change interval and had not been changed in over a year.'),
                               ('Why was there no change interval?', 'The lumpbreaker doctor was never set up as a PM when the roll was installed.')]),
    'RCFA-2026-03': dict(event='From mid-March the 2nd press top felt filled faster than normal. Uhle box vacuum and press moisture '
                               'climbed, and on 33# the 3rd dryer section reached its 135 psig steam limit, so the crews slowed '
                               'about 40 fpm. The felt was pulled at 6 of its 12 weeks at the 04/15/2026 outage.',
                         whys=[('Why was PM1 steam limited on 33#?', 'More water reached the dryers from the press.'),
                               ('Why was the press removing less water?', 'The 2nd press top felt was filled with contaminants.'),
                               ('Why did the felt fill?', '18% of the 2nd press HP shower nozzles were plugged, so the felt was not being cleaned.'),
                               ('Why were the nozzles plugged?', 'Debris in the shower water, and the nozzle check interval was too long to catch it.')]),
}

def rcfa_docs(add, out_root):
    log = read(os.path.join(DATA_OUT, 'rcfa', 'RCFA_log_PM1.csv'))
    plan = {r['Task ID']: r for r in read(os.path.join(DATA_OUT, 'teams', 'Planner_PM1_2026-10-31.csv'))}
    wo = {r['key']: r['wo_no'] for r in read(os.path.join(DATA_OUT, '_truth', 'wo_keys.csv')) if r['key']}
    down = read(os.path.join(DATA_OUT, '_truth', 'downtime.csv'))
    for r in log:
        rid = r['RCFA ID']; ev = dt.datetime.strptime(r['Event Date'], '%m/%d/%Y').date()
        det = RCFA_DETAIL.get(rid, {})
        dt_row = next((x for x in down if x['kind'] == 'equipment' and x['start'][:10] == ev.isoformat()), None)
        wo_no = wo.get(rid + '-WO') or wo.get({'RCFA-2026-02': 'S03-WO1', 'RCFA-2026-03': 'S02-WO1'}.get(rid, ''), '')
        acts = [plan[i.strip()] for i in r['Action IDs (Planner)'].split(';') if i.strip()]
        team = [r['Lead']] + [x for x in [NAME('P05'), NAME('P04'), NAME('P03')] if x != r['Lead']][:2]
        timeline = []
        if dt_row: timeline.append(f"{dt.datetime.fromisoformat(dt_row['start']).strftime('%m/%d/%Y %H:%M')} - {r['Title']}; machine down {float(dt_row['hours']):g} h")
        else: timeline.append(f"{us(ev)} - {r['Title']}")
        if wo_no: timeline.append(f'{us(ev)} - WO {wo_no} raised')
        timeline.append(f"{r['Opened']} - RCFA opened, lead {r['Lead']}")
        if r['Closed']: timeline.append(f"{r['Closed']} - Last action completed; RCFA closed")
        whys = det.get('whys') or [(f"Why did the {r['Title'].lower()} happen?", r['Root Cause'] + '.'),
                                   ("Why did that happen?", r['Contributing Factors'] + '.'),
                                   ('Why was it not caught earlier?', 'No check or alarm in the PM program or shift rounds covered it.')]
        add(kind='rcfa', id=rid, vendor='', date=ev, story={'RCFA-2026-02': 'S03', 'RCFA-2026-03': 'S02'}.get(rid, ''),
            positions=[BY_NAME[r['Asset']]['position_id']] if BY_NAME[r['Asset']]['position_id'] else [], docx=True,
            title=f"{rid} - {r['Title']}",
            fields={'rcfa_id': rid, 'event_date': r['Event Date'], 'downtime_h': r['Downtime (h)'], 'root_cause': r['Root Cause'],
                    'lead': r['Lead'], **({'wo': wo_no} if wo_no else {}), **{f'action_{n + 1}': a['Task ID'] for n, a in enumerate(acts)}},
            blocks=[('kv', [('RCFA', rid), ('Event date', r['Event Date']), ('Area / asset', f"{r['Area']} / {r['Asset']} ({r['Asset Number']})"),
                            ('Downtime', f"{r['Downtime (h)']} h"), ('Production loss', r['Production Loss'] or '-'), ('Category', r['Category']),
                            ('Lead', r['Lead']), ('Team', ', '.join(team)), ('Status', r['Status'])]),
                    ('h', '1. Event'), ('p', det.get('event') or f"{r['Title']} on {r['Event Date']}." + (f" WO {wo_no}." if wo_no else '')),
                    ('h', '2. Timeline')] + [('p', t) for t in timeline] + [
                    ('h', '3. Why analysis'), ('table', ['Question', 'Answer'], [[q, a] for q, a in whys]),
                    ('h', '4. Root cause'), ('p', r['Root Cause'] + '.'), ('p', 'Contributing: ' + r['Contributing Factors'] + '.'),
                    ('h', '5. Actions'), ('table', ['Planner ID', 'Action', 'Owner', 'Due', 'Status (10/31/2026)'],
                                          [[a['Task ID'], a['Task Name'], a['Assigned To'], a['Due Date'], a['Progress'] + (' (late)' if a['Late'] == 'true' else '')] for a in acts]),
                    ('h', '6. Sign-off'), ('p', f"RCFA closed {r['Closed']}." if r['Closed'] else 'Open - actions pending.')])

def render_docx(path, title, blocks, doc_id):
    from docx import Document
    from docx.shared import Pt
    doc = Document()
    doc.core_properties.author = 'PM1 Reliability'; doc.core_properties.title = title
    doc.core_properties.created = doc.core_properties.modified = dt.datetime(2026, 10, 31, 12)
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


# ═════════════════════════ Drawings ═════════════════════════
def drawings(add, rnd):
    from reportlab import rl_config
    rl_config.invariant = 1
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import TABLOID, landscape
    W, H = landscape(TABLOID)

    def sheet(dwg, title, fn, rev='C', date='03/12/2019', drawn='P19', story='', positions=(), fields=None, scanned=False):
        if scanned:
            add(kind='drawing', id=dwg, vendor='', date=D('2014-06-02'), title=f'{dwg} {title}', story=story, positions=list(positions),
                fields=fields or {'dwg_no': dwg}, scanned_drawing=fn); return
        path = os.path.join(OUT_DOCS, 'drawings', f'{dwg}.pdf'); os.makedirs(os.path.dirname(path), exist_ok=True)
        c = canvas.Canvas(path, pagesize=(W, H), invariant=1); c.setTitle(f'{dwg} {title}')
        c.setLineWidth(1.5); c.rect(20, 20, W - 40, H - 40); c.setLineWidth(.8)
        # title block
        x0, y0 = W - 380, 20
        c.rect(x0, y0, 360, 90)
        c.setFont('Helvetica-Bold', 12); c.drawString(x0 + 10, y0 + 66, f'PM1 - {title}')
        c.setFont('Helvetica', 9)
        for i, (k, v) in enumerate([('DWG NO', dwg), ('REV', rev), ('DATE', date), ('DRAWN', NAME(drawn)), ('MILL', 'Demo Mill - fictional')]):
            c.drawString(x0 + 10 + (i % 3) * 120, y0 + 42 - (i // 3) * 18, f'{k}: {v}')
        c.setFont('Helvetica-Bold', 10); c.drawString(40, H - 45, '<-- MACHINE DIRECTION (headbox right, reel left)')
        c.setFont('Helvetica', 9)
        fn(c, W, H)
        c.showPage(); c.save()
        add(kind='drawing', id=dwg, vendor='', date=D('2019-03-12'), title=f'{dwg} {title}', story=story, positions=list(positions),
            fields=fields or {'dwg_no': dwg}, prebuilt=path)

    def roll(c, x, y, r, label, below=False, fill=False):
        c.circle(x, y, r, fill=1 if fill else 0)
        if label: c.drawCentredString(x, y - r - 11 if below else y + r + 4, label)
    def loop(c, pts):
        p = c.beginPath(); p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        p.close(); c.setDash(4, 2); c.drawPath(p); c.setDash()
    def table(c, x, y, header, rows, widths):
        c.setFont('Helvetica-Bold', 9)
        for i, h in enumerate(header): c.drawString(x + sum(widths[:i]), y, h)
        c.setFont('Helvetica', 9)
        for n, r in enumerate(rows):
            for i, v in enumerate(r): c.drawString(x + sum(widths[:i]), y - 16 * (n + 1), str(v))
            c.line(x, y - 16 * (n + 1) - 4, x + sum(widths), y - 16 * (n + 1) - 4)

    def overview(c, W, H):
        secs = [('Refiners', 'sec-refiners'), ('Formers', 'sec-topply / sec-baseply'), ('Press', 'sec-press'), ('1st dryer', 'sec-dryer-1 (cans 1-10)'),
                ('2nd dryer', 'sec-dryer-2 (cans 11-44)'), ('3rd dryer', 'sec-dryer-3 (cans 45-74)'), ('Calender', 'sec-calender'), ('Reel', 'sec-reel')]
        w = (W - 120) / len(secs)
        for i, (n, ids) in enumerate(secs):
            x = W - 60 - (i + 1) * w
            c.rect(x + 6, H / 2 - 50, w - 12, 100); c.setFont('Helvetica-Bold', 11); c.drawCentredString(x + w / 2, H / 2 + 10, n)
            c.setFont('Helvetica', 8); c.drawCentredString(x + w / 2, H / 2 - 10, ids)
            if i: c.line(x + w + 6, H / 2, x + w - 6, H / 2)
        c.drawString(60, H / 2 - 90, 'Two-ply linerboard: top ply and base ply formers, 2-nip press with tandem felt, three dryer sections, calender, reel.')
    sheet('DWG-PM1-100', 'Machine overview', overview, fields={'dwg_no': 'DWG-PM1-100', 'label': '2nd dryer'})

    def former(base):
        def f(c, W, H):
            y = H / 2; xs = [W - 120, W - 380, W - 640, W - 900]
            roll(c, xs[0], y, 28, 'Breast roll'); roll(c, xs[3], y, 34, 'Couch roll')
            for i, x in enumerate([W - 460, W - 540, W - 620]): c.rect(x - 25, y - 34, 50, 10); c.drawCentredString(x, y - 46, f'Flat box {i + 1}')
            c.rect(xs[0] - 90, y - 34, 60, 8); c.drawCentredString(xs[0] - 60, y - 46, 'Forming board')
            for i, x in enumerate([W - 300, W - 700]): roll(c, x, y - 160, 18, f'Return roll {i + 1}', below=True)
            roll(c, W - 820, y - 220, 18, 'Stretch roll', below=True)
            loop(c, [(xs[0], y + 28), (xs[3], y + 34), (W - 820, y - 238), (W - 700, y - 178), (W - 300, y - 178), (xs[0], y - 28)])
            c.drawString(W - 520, y + 50, ('Base' if base else 'Top') + ' ply forming fabric (' + ('form-bottom' if base else 'form-top') + ')')
            c.drawString(W - 120, y + 120, 'HP shower (inside return run)')
            if base:
                roll(c, xs[3] - 10, y + 80, 22, ''); c.drawString(xs[3] - 160, y + 112, 'Lumpbreaker roll (lumpbreaker)')
                c.line(xs[3] + 12, y + 80, xs[3] + 40, y + 96); c.drawString(xs[3] + 44, y + 96, 'Lumpbreaker doctor')
        return f
    sheet('DWG-PM1-110', 'Top ply former - clothing run', former(False), positions=['form-top'], fields={'dwg_no': 'DWG-PM1-110', 'label': 'form-top'})
    sheet('DWG-PM1-111', 'Base ply former - clothing run', former(True), positions=['form-bottom', 'lumpbreaker'], story='S03',
          fields={'dwg_no': 'DWG-PM1-111', 'label': 'Lumpbreaker roll'})

    def press(c, W, H):
        y = H / 2 + 20
        roll(c, W - 420, y + 32, 30, '1st press top roll'); roll(c, W - 420, y - 32, 30, '1st press bottom roll', below=True)
        roll(c, W - 760, y + 32, 30, '2nd press top roll'); roll(c, W - 760, y - 32, 30, '2nd press bottom roll', below=True)
        loop(c, [(W - 420, y + 62), (W - 300, y + 200), (W - 520, y + 230)]); c.drawString(W - 330, y + 230, '1st press top felt (p1-felt-top)')
        loop(c, [(W - 760, y + 62), (W - 640, y + 210), (W - 880, y + 230)]); c.drawString(W - 900, y + 245, '2nd press top felt (p2-felt-top)')
        loop(c, [(W - 420, y - 62), (W - 760, y - 62), (W - 860, y - 230), (W - 320, y - 230)]); c.drawString(W - 640, y - 250, 'Tandem felt (p-tandem-felt) - both nips')
        for x, yy, l in [(W - 330, y + 160, 'Uhle box P1'), (W - 650, y + 170, 'Uhle box P2'), (W - 560, y - 225, 'Uhle box TAN')]:
            c.rect(x - 22, yy - 6, 44, 12); c.drawString(x + 26, yy - 3, l)
        for x, yy, l in [(W - 300, y + 120, 'HP shower P1'), (W - 620, y + 130, 'HP shower P2'), (W - 400, y - 200, 'HP shower TAN')]:
            c.line(x - 8, yy, x + 8, yy); c.line(x, yy, x, yy - 10); c.drawString(x + 12, yy - 4, l)
    sheet('DWG-PM1-120', 'Press section - clothing runs, Uhle boxes and showers', press, positions=['p1-felt-top', 'p2-felt-top', 'p-tandem-felt'],
          story='S02', fields={'dwg_no': 'DWG-PM1-120', 'label': 'Uhle box P2'})

    def dryer(sec, first, last, uno=False, pv=False):
        def f(c, W, H):
            cans = list(range(first, last + 1)); n = len(cans); step = (W - 160) / ((n + 1) // 2 + 1)
            for i, can in enumerate(cans):
                top = i % 2 == 0; x = W - 90 - (i // 2 + 1) * step - (step / 2 if not top else 0); y = H / 2 + (55 if top else -55)
                roll(c, x, y, 22, str(can), below=not top, fill=False)
            if uno: c.drawString(W - 400, H / 2 + 120, f'{sec} unorun felt (d1-felt) weaves over top cans and under bottom vacuum rolls')
            else:
                c.drawString(W - 400, H / 2 + 120, f'{sec} top felt (d{sec[0]}-felt-top) - runs around the bottom of the top cans')
                c.drawString(W - 400, H / 2 - 130, f'{sec} bottom felt (d{sec[0]}-felt-bottom) - runs around the top of the bottom cans')
            c.drawString(60, 140, f'Cans {first}-{last}, numbered from the wet end. Top cans odd positions, bottom cans even. DS = drive side, TS = tending side.')
            if pv: c.drawString(60, 120, 'Pocket ventilation PV-3 supplies the 3rd section pockets - see DWG-PM1-180.')
        return f
    sheet('DWG-PM1-130', '1st dryer section - can numbering and felt run', dryer('1st', 1, 10, uno=True), positions=['d1-felt'],
          fields={'dwg_no': 'DWG-PM1-130', 'label': 'unorun'})
    sheet('DWG-PM1-131', '2nd dryer section - can numbering and felt runs', dryer('2nd', 11, 44), positions=['d2-felt-top', 'd2-felt-bottom'],
          story='S01', fields={'dwg_no': 'DWG-PM1-131', 'label': '27'})
    sheet('DWG-PM1-132', '3rd dryer section - can numbering and felt runs', dryer('3rd', 45, 74, pv=True), positions=['d3-felt-top', 'd3-felt-bottom'],
          story='S05', fields={'dwg_no': 'DWG-PM1-132', 'label': 'PV-3'})

    def rope(c, W, H):
        c.drawString(60, H - 90, 'Tail threading rope run - front (tending) side, 2nd and 3rd dryer sections')
        for k, (sec, x0, x1) in enumerate([('2nd section', W - 120, W / 2 + 40), ('3rd section', W / 2 - 40, 140)]):
            y = H / 2 + 40 - k * 0
            c.line(x0, y + 30, x1, y + 30); c.line(x0, y - 30, x1, y - 30)
            for i in range(6): roll(c, x0 - i * (x0 - x1) / 5, y + 30 if i % 2 else y - 30, 9, f'S{k + 1}-{i + 1}')
            c.drawString(min(x0, x1) + 20, y - 70, f'{sec}: red rope (outer) and blue rope (inner); sheaves S{k + 1}-1 to S{k + 1}-6')
    sheet('DWG-PM1-135', 'Dryer tail threading rope run', rope, fields={'dwg_no': 'DWG-PM1-135', 'label': 'blue rope'})

    def cal(c, W, H):
        roll(c, W - 500, H / 2 + 45, 42, 'Calender top roll (cal-top) - chilled iron')
        roll(c, W - 500, H / 2 - 45, 42, 'Calender bottom roll (cal-bottom) - soft cover', below=True)
        roll(c, W - 900, H / 2, 50, 'Reel drum'); roll(c, W - 900, H / 2 + 95, 40, 'Spool')
        c.drawString(W - 640, H / 2 - 160, 'Loading cylinders: calender loading hydraulics (DS and TS)')
    sheet('DWG-PM1-140', 'Calender and reel', cal, positions=['cal-top', 'cal-bottom'], story='S07', fields={'dwg_no': 'DWG-PM1-140', 'label': 'soft cover'})

    def showers(c, W, H):
        table(c, 60, H - 100, ['Shower ID', 'Location', 'Type', 'Nozzle', 'Pressure', 'Oscillating'],
              [['SH-101', 'Top ply fabric return run', 'HP cleaning', '1.0 mm needle', '250 psi', 'Yes'],
               ['SH-102', 'Base ply fabric return run', 'HP cleaning', '1.0 mm needle', '250 psi', 'Yes'],
               ['SH-103', 'Top ply breast roll', 'LP lube', 'Fan 40°', '40 psi', 'No'],
               ['SH-104', 'Base ply breast roll', 'LP lube', 'Fan 40°', '40 psi', 'No'],
               ['SH-201', '1st press top felt', 'HP cleaning', '1.0 mm needle', '250 psi', 'Yes'],
               ['SH-202', '2nd press top felt', 'HP cleaning', '1.0 mm needle', '250 psi', 'Yes'],
               ['SH-203', 'Tandem felt', 'HP cleaning', '1.0 mm needle', '250 psi', 'Yes'],
               ['SH-401', 'Calender doctor', 'LP', 'Fan 15°', '60 psi', 'No']], [90, 230, 110, 110, 90, 90])
    sheet('DWG-PM1-150', 'Shower schedule and locations', showers, story='S02', fields={'dwg_no': 'DWG-PM1-150', 'label': 'SH-202'})

    def clothing(c, W, H):
        table(c, 60, H - 100, ['Position', 'My Machine id', 'Length (m)', 'Width (m)', 'Supplier', 'Style', 'Target life'],
              [[BY_POS[p]['name'], p, ln, wd, sup, STYLE[p], f'{LIFE[p]} wk'] for p, ln, wd, sup in [
                  ('form-top', 31.2, 6.10, 'Northbank Fabrics'), ('form-bottom', 33.8, 6.10, 'Northbank Fabrics'),
                  ('p1-felt-top', 18.5, 5.95, 'Halden Felt Co.'), ('p2-felt-top', 19.0, 5.95, 'Halden Felt Co.'),
                  ('p-tandem-felt', 24.4, 5.95, 'Marlow Press Fabrics'), ('d1-felt', 61.0, 5.80, 'Northbank Fabrics'),
                  ('d2-felt-top', 88.0, 5.80, 'Northbank Fabrics'), ('d2-felt-bottom', 86.5, 5.80, 'Northbank Fabrics'),
                  ('d3-felt-top', 80.0, 5.80, 'Corrie Textiles'), ('d3-felt-bottom', 79.0, 5.80, 'Corrie Textiles')]],
              [170, 110, 80, 75, 150, 190, 80])
    sheet('DWG-PM1-102', 'Clothing list', clothing, rev='F', date='01/15/2026', fields={'dwg_no': 'DWG-PM1-102', 'label': 'p-tandem-felt'})

    def rolls(c, W, H):
        table(c, 60, H - 100, ['Roll', 'My Machine id', 'Cover', 'Diameter (in)', 'Face (in)', 'Service'],
              [['Lumpbreaker roll', 'lumpbreaker', 'Rubber 35 P&J', 24, 250, 'Pellham Roll Service'],
               ['1st press top roll', 'p1-roll-top', 'Granite-style composite', 42, 248, 'Pellham Roll Service'],
               ['1st press bottom roll', 'p1-roll-bottom', 'Rubber 10 P&J, suction', 44, 248, 'Pellham Roll Service'],
               ['2nd press top roll', 'p2-roll-top', 'Composite', 42, 248, 'Pellham Roll Service'],
               ['2nd press bottom roll', 'p2-roll-bottom', 'Blind-drilled rubber 12 P&J', 44, 248, 'Pellham Roll Service'],
               ['Calender top roll', 'cal-top', 'Chilled iron', 36, 244, 'Teague Roll Works'],
               ['Calender bottom roll', 'cal-bottom', 'Soft cover 85 Shore D', 36, 244, 'Teague Roll Works']], [150, 110, 190, 90, 80, 160])
    sheet('DWG-PM1-160', 'Roll list', rolls, rev='D', date='06/30/2025', fields={'dwg_no': 'DWG-PM1-160', 'label': 'Blind-drilled'})

    def steam(c, W, H):
        for i, (s, p) in enumerate([('1st section', '20-28 psig'), ('2nd section', '65-85 psig'), ('3rd section', '100-135 psig (limit 135)')]):
            x = W - 200 - i * 330
            c.rect(x - 120, H / 2 - 40, 240, 80); c.drawCentredString(x, H / 2 + 10, f'{s} steam header'); c.drawCentredString(x, H / 2 - 10, p)
            c.rect(x - 60, H / 2 - 180, 120, 50); c.drawCentredString(x, H / 2 - 160, 'Condensate tank'); c.line(x, H / 2 - 40, x, H / 2 - 130)
        c.drawString(60, 140, 'Cascade steam system: 3rd section blow-through feeds 2nd section, 2nd feeds 1st. DP control on each section.')
    sheet('DWG-PM1-170', 'Steam and condensate schematic', steam, story='S02', fields={'dwg_no': 'DWG-PM1-170', 'label': 'limit 135'})

    def refiners(c, W, H):
        for i, r in enumerate(['BP 1', 'BP 2', 'TP 1', 'TP 2']):
            x = W - 200 - i * 230; c.circle(x, H / 2, 45); c.drawCentredString(x, H / 2 - 4, f'{r} refiner')
            c.drawCentredString(x, H / 2 - 70, ('Base ply - Ridgeway plates' if r.startswith('BP') else 'Top ply - Brennock plates'))
        c.drawString(60, 140, 'Base ply refiners BP 1 / BP 2 in series to the base ply machine chest; top ply TP 1 / TP 2 to the top ply chest.')
    sheet('DWG-PM1-190', 'Refiner layout', refiners, positions=['ref-bp1', 'ref-bp2', 'ref-tp1', 'ref-tp2'], story='S04',
          fields={'dwg_no': 'DWG-PM1-190', 'label': 'Ridgeway plates'})

    def uhle(c, W, H):
        table(c, 60, H - 100, ['Uhle box', 'Felt', 'Cover', 'Slot (mm)', 'Normal vacuum', 'Separator'],
              [['UB-P1', '1st press top felt', 'Ceramic', '2 x 15', '10.5-12 inHg', 'VS-2'], ['UB-P2', '2nd press top felt', 'Ceramic', '2 x 15', '11.5-13 inHg', 'VS-2'],
               ['UB-TAN', 'Tandem felt', 'Ceramic', '2 x 18', '12-13.5 inHg', 'VS-3']], [90, 170, 90, 90, 130, 90])
    sheet('DWG-PM1-125', 'Press Uhle box details', uhle, story='S02', fields={'dwg_no': 'DWG-PM1-125', 'label': 'UB-P2'})

    def pv3():   # an old scanned drawing
        return [('kv', [('Drawing', 'DWG-PM1-180 Rev A'), ('Title', '3rd section pocket ventilation PV-3'), ('Date', '06/02/2014')]),
                ('p', 'Fan PV-3 (75 hp) supplies hot air to the 3rd section pockets through dampers D1-D4 on the drive side header.'),
                ('table', ['Damper', 'Serves pockets', 'Actuator', 'Normal position'],
                 [['D1', 'cans 45-52', 'Pneumatic', '70% open'], ['D2', 'cans 53-60', 'Pneumatic', '70% open'],
                  ['D3', 'cans 61-68', 'Pneumatic', '65% open'], ['D4', 'cans 69-74', 'Pneumatic', '60% open']]),
                ('p', 'Fan motor current about 62 A at normal load. Low current means low airflow (closed damper, slipping belt or blocked filter).')]
    sheet('DWG-PM1-180', '3rd section pocket ventilation PV-3', pv3(), scanned=True, story='S05', fields={'dwg_no': 'DWG-PM1-180', 'label': '62 A'})


# ═════════════════════════ Reference charts ═════════════════════════
REFS = [
    ('REF-01', 'Grade sheet - PM1 linerboard', ['Grade', 'Basis weight (lb/MSF)', 'Speed (fpm)', 'Reel moisture (%)', '1st sect steam (psig)',
                                                '2nd sect steam (psig)', '3rd sect steam (psig)', '1st press (pli)', '2nd press (pli)'],
     [['26#', 26, 2450, 7.5, 20, 65, 100, 1450, 2150], ['30#', 30, 2250, 7.5, 25, 75, 110, 1500, 2200], ['33#', 33, 2050, 7.5, 28, 85, 120, 1550, 2250]]),
    ('REF-02', 'Felt and fabric tension chart', ['Position', 'Target (pli)', 'Min (pli)', 'Max (pli)'],
     [['Top ply forming fabric', 32, 28, 36], ['Base ply forming fabric', 32, 28, 36], ['1st press top felt', 22, 18, 26], ['2nd press top felt', 22, 18, 26],
      ['Tandem felt', 24, 20, 28], ['Dryer fabrics (all)', 12, 10, 14]]),
    ('REF-03', 'Shower and nozzle chart', ['Shower', 'Type', 'Orifice (mm)', 'Spacing (mm)', 'Pressure (psi)', 'Check interval'],
     [['Forming HP (SH-101/102)', 'Needle', 1.0, 150, 250, 'Monthly'], ['Press HP (SH-201/202/203)', 'Needle', 1.0, 150, 250, 'Monthly (since 05/2026)'],
      ['Breast roll LP (SH-103/104)', 'Fan 40°', 2.0, 100, 40, 'Quarterly'], ['Calender doctor (SH-401)', 'Fan 15°', 1.5, 150, 60, 'Quarterly']]),
    ('REF-04', 'Refiner plate specifications', ['Refiner', 'Plate supplier', 'Diameter (in)', 'Bar / groove (mm)', 'Target life (wk)', 'Normal SE (kWh/t)'],
     [['BP 1', 'Ridgeway Refining', 36, '3.0 / 4.0', 12, '95-98'], ['BP 2', 'Ridgeway Refining', 36, '3.0 / 4.0', 12, '95-98'],
      ['TP 1', 'Brennock Plates', 34, '2.5 / 3.5', 12, '95-98'], ['TP 2', 'Brennock Plates', 34, '2.5 / 3.5', 12, '95-98']]),
    ('REF-05', 'Steam curve by grade', ['Grade', '1st section (psig)', '2nd section (psig)', '3rd section (psig)', '3rd section limit (psig)'],
     [['26#', 20, 65, 100, 135], ['30#', 25, 75, 110, 135], ['33#', 28, 85, 120, 135]]),
    ('REF-06', 'Vacuum targets by clothing age', ['Measure', 'New', '25% life', '50% life', '75% life', 'End of life'],
     [['Uhle box P1 (inHg)', 11.0, 11.25, 11.5, 11.75, 12.0], ['Uhle box P2 (inHg)', 12.0, 12.25, 12.5, 12.75, 13.0],
      ['Uhle box tandem (inHg)', 12.5, 12.75, 13.0, 13.25, 13.5], ['Base ply couch (inHg)', 18.0, 18.4, 18.8, 19.1, 19.5],
      ['Top ply flat boxes (inHg)', 8.5, 8.65, 8.8, 8.95, 9.1]]),
    ('REF-07', 'Doctor blade chart', ['Location', 'Blade type', 'Material', 'Thickness (mm)', 'Bevel', 'Change interval'],
     [['Lumpbreaker roll', 'Cleaning', 'Composite', 1.5, '30°', 'Every outage (since 03/2026)'], ['1st press top roll', 'Cleaning', 'Composite', 1.5, '30°', 'Every outage'],
      ['2nd press bottom roll', 'Cleaning', 'Steel', 1.2, '25°', 'Every outage'], ['Dryer cans', 'Cleaning', 'Composite', 1.5, '30°', 'Annual'],
      ['Calender rolls', 'Cleaning', 'Composite', 1.5, '30°', 'Every outage']]),
    ('REF-08', 'Vibration severity limits', ['Machine type', 'Good (in/s)', 'Alert (in/s)', 'Danger (in/s)'],
     [['Dryer can bearings', '< 0.10', 0.15, 0.30], ['Press and calender rolls', '< 0.10', 0.15, 0.30], ['Pumps and fans', '< 0.12', 0.15, 0.30],
      ['Refiner and drive motors', '< 0.10', 0.15, 0.30]]),
]

def reference(add):
    for rid, title, hdr, rows in REFS:
        path = os.path.join(OUT_DOCS, 'reference', 'tables', f'{rid}.csv'); os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', newline='') as f:
            w = csv.writer(f, lineterminator='\n'); w.writerow(hdr); w.writerows(rows)
        add(kind='reference', id=rid, vendor='', date=D('2026-01-15'), title=f'{rid} {title}', positions=[],
            story={'REF-03': 'S02', 'REF-04': 'S04', 'REF-05': 'S02', 'REF-08': 'S01'}.get(rid, ''),
            fields={'ref_id': rid, 'cell': str(rows[-1][-1])},
            blocks=[('kv', [('Owner', NAME('P04') if rid not in ('REF-07', 'REF-08') else NAME('P03')), ('Issued', '01/15/2026'),
                            ('Table', f'tables/{rid}.csv (same values, typed)')]), ('table', hdr, rows)])


# ═════════════════════════ Build + check ═════════════════════════
def slug(s): return ''.join(ch if ch.isalnum() else '-' for ch in s.lower()).strip('-')

def build(out):
    global OUT_DOCS, DATA_OUT
    OUT_DOCS = os.path.join(out, 'docs'); DATA_OUT = os.path.join(DATA, 'out')
    if os.path.exists(OUT_DOCS): shutil.rmtree(OUT_DOCS)
    pi = Pi(os.path.join(DATA_OUT, 'pi')); rnd = random.Random(SEED); manifest = []
    def add(kind, id, vendor, date, title, fields, story='', positions=(), blocks=None, scanned=False, rotate=None, docx=False,
            prebuilt=None, scanned_drawing=None):
        if prebuilt: path = prebuilt
        elif docx:
            path = os.path.join(OUT_DOCS, 'rcfa', f'{id}.docx'); render_docx(path, title, blocks, id)
        elif scanned_drawing is not None:
            path = os.path.join(OUT_DOCS, 'drawings', f'{id}.pdf'); render_scanned(path, 'PM1 drawing', title, scanned_drawing, id, SEED + len(manifest)); scanned = True
        else:
            folder = os.path.join(OUT_DOCS, 'vendor', slug(VENDORS[vendor]['name'])) if vendor else os.path.join(OUT_DOCS, 'reference')
            path = os.path.join(folder, f'{id}.pdf')
            head = VENDORS[vendor]['name'] if vendor else 'PM1 reference'
            if scanned: render_scanned(path, head, title, blocks, id, SEED + len(manifest))
            else: render_pdf(path, head, title, blocks, id, rotate_page=rotate)
        manifest.append(dict(id=id, kind=kind, vendor=VENDORS[vendor]['name'] if vendor else '', date=date.isoformat(), title=title,
                             path=os.path.relpath(path, out), story=story, positions=list(positions), needs_ocr=bool(scanned),
                             rotated_page=rotate, fields=fields))
    vendor_reports(pi, rnd, add)
    rcfa_docs(add, out)
    drawings(add, rnd)
    reference(add)
    os.makedirs(os.path.join(out, '_truth'), exist_ok=True)
    json.dump(sorted(manifest, key=lambda m: (m['kind'], m['id'])), open(os.path.join(out, '_truth', 'documents.json'), 'w'), indent=1)
    return manifest

def text_of(path):
    if path.endswith('.docx'):
        from docx import Document
        d = Document(path)
        parts = [p.text for p in d.paragraphs] + [c.text for t in d.tables for r in t.rows for c in r.cells]
        return '\n'.join(parts)
    from pypdf import PdfReader
    return '\n'.join((p.extract_text() or '') for p in PdfReader(path).pages)

REAL_NAMES = ['AstenJohnson', 'Albany', 'Andritz', 'Valmet', 'Voith', 'Xerium', 'Stowe', 'Kadant', 'Spraying Systems', 'SKF']

def check(manifest, out):
    import shutil as sh
    errs = []
    def need(ok, msg):
        if not ok: errs.append(msg)
    kinds = {}
    for m in manifest: kinds[m['kind']] = kinds.get(m['kind'], 0) + 1
    vendor_n = sum(v for k, v in kinds.items() if k not in ('rcfa', 'drawing', 'reference'))
    need(60 <= vendor_n <= 80, f'{vendor_n} vendor reports, want 60–80')
    need(kinds.get('rcfa') == 13, f"{kinds.get('rcfa')} RCFA write-ups, want 13 (one per log row)")
    need(kinds.get('drawing', 0) >= 15, f"{kinds.get('drawing')} drawings, want >= 15")
    need(kinds.get('reference') == 8 and len(os.listdir(os.path.join(out, 'docs', 'reference', 'tables'))) == 8, 'want 8 reference charts with 8 tables')
    need(len({m['id'] for m in manifest}) == len(manifest), 'duplicate document ids')
    norm = lambda s: ' '.join(s.replace(' ', ' ').split())
    tess = sh.which('tesseract')
    for m in manifest:
        p = os.path.join(out, m['path']); need(os.path.exists(p), f"{m['id']}: file missing")
        txt = norm(text_of(p))
        if m['needs_ocr']:
            need(len(txt) < 20, f"{m['id']}: scanned document should have no text layer")
            if tess and m['kind'] != 'drawing':
                import subprocess
                tmp = tempfile.mkdtemp()
                subprocess.run(['pdftoppm', '-r', '150', '-png', '-f', '1', '-l', '1', p, os.path.join(tmp, 'pg')], check=True)
                img = os.path.join(tmp, sorted(os.listdir(tmp))[0])
                ocr = norm(subprocess.run(['tesseract', img, '-', '--psm', '6'], capture_output=True, text=True).stdout)
                need(m['id'] in ocr.replace(' ', '') or m['id'] in ocr, f"{m['id']}: OCR did not find the report number")
                sh.rmtree(tmp)
            continue
        for k, v in m['fields'].items():
            need(norm(str(v)) in txt, f"{m['id']}: field {k}={v!r} not found in the extracted text")
        for n in REAL_NAMES:
            need(n not in txt, f"{m['id']}: real company name {n}")
    # storyline anchors
    get = {m['id']: m for m in manifest}
    need(get['KV-VR-260914']['fields'].get('c27_ds') == '0.07', f"S01: Sep route can 27 = {get['KV-VR-260914']['fields'].get('c27_ds')}, want 0.07")
    oct19 = float(get['KV-VR-261019']['fields'].get('c27_ds', 0)); need(.22 <= oct19 <= .27, f'S01: Oct route can 27 = {oct19}, want ~0.25')
    need(get['SN-SA-260415']['fields'].get('p2_plugged') == '18%', 'S02: Apr 15 shower audit should show 18% plugged on the 2nd press HP shower')
    need(get['HF-SV-260415']['fields'].get('p2_condition') == 'High fill', 'S02: Apr 15 Halden survey should report high fill')
    need(get['RR-PI-261007']['fields'].get('bp2_edge') == 'Elevated', 'S04: Ridgeway annual inspection should flag BP 2')
    need(get['TR-RS-260527']['needs_ocr'], 'S07: the May Teague report is the scanned one')
    need(get['KV-VR-260714']['rotated_page'] == 1, 'one vibration report has a rotated page')
    from pypdf import PdfReader
    need(PdfReader(os.path.join(out, get['KV-VR-260714']['path'])).pages[1].get('/Rotate') == 90, 'rotated page not rotated')
    return errs

if __name__ == '__main__':
    checking = '--check' in sys.argv
    for need_file in ('_truth/downtime.csv', 'pi/points.json', 'rcfa/RCFA_log_PM1.csv'):
        if not os.path.exists(os.path.join(DATA, 'out', need_file)):
            sys.exit(f'Missing demo-data/out/{need_file}: run structured.py and pi_bonvoy.py first.')
    out = os.path.join(tempfile.mkdtemp(), 'out') if checking else os.path.join(DATA, 'out')
    manifest = build(out)
    kinds = {}
    for m in manifest: kinds[m['kind']] = kinds.get(m['kind'], 0) + 1
    summary = ' · '.join(f'{v} {k}' for k, v in sorted(kinds.items())) + f" · {sum(m['needs_ocr'] for m in manifest)} need OCR"
    if checking:
        errs = check(manifest, out)
        shutil.rmtree(os.path.dirname(out))
        for e in errs: print('FAIL', e)
        if errs: sys.exit(1)
        print('docs ok —', summary)
    else:
        print('wrote demo-data/out/docs —', summary)
