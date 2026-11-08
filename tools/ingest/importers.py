"""MM LLM importers: turn the files that arrive from the mill into rows for the llm.* tables.

Each importer reads one kind of export and returns rows. Column names live in the MAP dicts below, so a real
export with different headers is a mapping change, not a code change. Every row is tagged to a PM1 position
by the Tagger (exact matches against the equipment register first; free text in documents by name matching).
Nothing here reads the demo answer key (_truth/).
"""
import csv, datetime as dt, hashlib, os, re, subprocess, tempfile
from zoneinfo import ZoneInfo

MILL_TZ = ZoneInfo('America/New_York')

def mdy(s):
    s = (s or '').strip()
    return dt.datetime.strptime(s, '%m/%d/%Y').date().isoformat() if s else None

def num(s):
    s = (s or '').strip()
    try: return float(s) if s else None
    except ValueError: return None


# ═════════════════════════ Position tagger ═════════════════════════
class Tagger:
    def __init__(self, equipment_rows):
        self.eq = equipment_rows
        self.by_name = {e['name'].lower(): e for e in equipment_rows}
        self.by_no = {e['asset_no']: e for e in equipment_rows}
        self.by_pos = {e['position_id']: e for e in equipment_rows if e.get('position_id')}
        names = sorted((e['name'] for e in equipment_rows if e['kind'] != 'section'), key=len, reverse=True)
        self.name_re = re.compile(r'\b(' + '|'.join(re.escape(n) for n in names) + r')\b', re.I)
        self.parent = {e['asset_no']: e.get('parent_asset') for e in equipment_rows}
        self.pos_re = re.compile(r'\b(' + '|'.join(re.escape(p) for p in sorted(self.by_pos, key=len, reverse=True)) + r')\b')

    def position_of(self, asset_no):
        """The asset's own position, or the nearest parent's (an HP shower belongs to its felt)."""
        seen = 0
        while asset_no and seen < 5:
            e = self.by_no.get(asset_no)
            if not e: return None
            if e.get('position_id'): return e['position_id']
            asset_no = self.parent.get(asset_no); seen += 1
        return None

    def asset(self, name=None, asset_no=None):
        e = self.by_no.get((asset_no or '').strip()) or self.by_name.get((name or '').strip().lower())
        return (e['asset_no'], self.position_of(e['asset_no']), e['section']) if e else (None, None, None)

    def in_text(self, text):
        """Positions and asset numbers mentioned in free text."""
        assets, positions = set(), set()
        for m in self.name_re.finditer(text):
            e = self.by_name[m.group(1).lower()]; assets.add(e['asset_no'])
            p = self.position_of(e['asset_no'])
            if p: positions.add(p)
        for m in self.pos_re.finditer(text):
            e = self.by_pos[m.group(1)]; positions.add(m.group(1)); assets.add(e['asset_no'])
        for m in re.finditer(r'\bcan (\d{1,2})\b', text, re.I):     # "can 27" in vibration notes
            e = self.by_name.get(f'dryer can {int(m.group(1))}')
            if e: assets.add(e['asset_no'])
        return sorted(positions), sorted(assets)


# ═════════════════════════ Backbone ═════════════════════════
def backbone(folder):
    rd = lambda n: list(csv.DictReader(open(os.path.join(folder, n))))
    eq = rd('equipment.csv')
    equipment = [dict(asset_no=e['asset_no'], name=e['name'], section=e['section'], kind=e['kind'],
                      position_id=e['position_id'] or None, parent_asset=e['parent_asset'] or None) for e in eq]
    tags = [dict(tag=t['tag'], description=t['description'], units=t['units'], asset_no=t['asset_no'],
                 position_id=t['position_id'] or None, section=t['section']) for t in rd('pi_tags.csv')]
    loc = lambda s: dt.datetime.fromisoformat(s).replace(tzinfo=MILL_TZ).isoformat()
    outages = [dict(outage_id=o['id'], kind=o['type'], starts_at=loc(o['start']), ends_at=loc(o['end']), note=o['note']) for o in rd('outages.csv')]
    return equipment, tags, outages


# ═════════════════════════ BUS daily sheet (.xlsx) ═════════════════════════
BUS_MAP = {'area': 'Area', 'equipment': 'Equipment / Position', 'issue': 'Issue', 'action': 'Action / Next step',
           'owner': 'Owner', 'status': 'Status', 'days_open': 'Days Open', 'wo_no': 'WO #'}

def bus_sheets(paths, tagger):
    """paths in any order; returns item rows. issue_key follows one issue across consecutive sheets."""
    from openpyxl import load_workbook
    rows, open_issues = [], {}      # (equipment, issue) -> (key, last date)
    for path in sorted(paths):
        ws = load_workbook(path, read_only=True).active
        cells = [list(r) for r in ws.iter_rows(values_only=True)]
        day = None
        for r in cells:
            if r and r[0] == 'Date' and r[2]: day = dt.datetime.strptime(str(r[2])[4:], '%m/%d/%Y').date()
        if day is None:
            day = dt.date.fromisoformat(re.search(r'(\d{4}-\d{2}-\d{2})', path).group(1))
        hi = next(i for i, r in enumerate(cells) if r and r[0] == '#')
        idx = {h: i for i, h in enumerate(cells[hi]) if h}
        for r in cells[hi + 1:]:
            if not r or r[0] is None: continue
            g = lambda k: r[idx[BUS_MAP[k]]]
            equip, issue = str(g('equipment') or ''), str(g('issue') or '')
            k = (equip.lower(), issue.lower())
            prev = open_issues.get(k)
            if prev and (day - prev[1]).days <= 1: key = prev[0]
            else: key = hashlib.sha1(f'{equip}|{issue}|{day}'.encode()).hexdigest()[:16]
            open_issues[k] = (key, day)
            asset_no, pos, _ = tagger.asset(name=equip)
            rows.append(dict(sheet_date=day.isoformat(), line=int(r[0]), issue_key=key, area=g('area'), equipment=equip,
                             asset_no=asset_no, position_id=pos, issue=issue, action=g('action'), owner=g('owner'),
                             status=g('status'), days_open=int(g('days_open') or 0), wo_no=str(g('wo_no') or '') or None,
                             source_file=os.path.basename(path)))
    return rows


# ═════════════════════════ JDE work orders (.csv) ═════════════════════════
JDE_MAP = {'wo_no': 'Order Number', 'wo_type': 'Type of WO', 'description': 'Description', 'asset_no': 'Asset Number',
           'asset': 'Asset Description', 'priority': 'Priority', 'status': 'Status', 'status_text': 'Status Description',
           'requested': 'Requested Date', 'planned_start': 'Planned Start', 'completed': 'Completed Date', 'originator': 'Originator',
           'assigned_to': 'Assigned To', 'craft': 'Craft', 'est_hours': 'Est Hours', 'act_hours': 'Act Hours', 'outage': 'Outage',
           'parts_status': 'Parts Status', 'notes': 'Completion Notes'}

def jde_exports(paths, tagger):
    """Weekly deltas and full exports, applied oldest first: the latest export wins for each WO."""
    latest = {}
    for path in sorted(paths, key=lambda p: (re.search(r'(\d{4}-\d{2}-\d{2})', p).group(1), 'full' in p)):
        as_of = re.search(r'(\d{4}-\d{2}-\d{2})', path).group(1)
        for r in csv.DictReader(open(path)):
            g = lambda k: r.get(JDE_MAP[k], '')
            asset_no, pos, sec = tagger.asset(name=g('asset'), asset_no=g('asset_no'))
            latest[g('wo_no')] = dict(wo_no=g('wo_no'), wo_type=g('wo_type'), description=g('description'), asset_no=asset_no or g('asset_no'),
                                      asset=g('asset'), position_id=pos, section=sec, priority=int(g('priority') or 0) or None,
                                      status=int(g('status') or 0) or None, status_text=g('status_text'), requested=mdy(g('requested')),
                                      planned_start=mdy(g('planned_start')), completed=mdy(g('completed')), originator=g('originator'),
                                      assigned_to=g('assigned_to'), craft=g('craft'), est_hours=num(g('est_hours')), act_hours=num(g('act_hours')),
                                      outage=g('outage') or None, parts_status=g('parts_status') or None, notes=g('notes') or None,
                                      as_of=as_of, source_file=os.path.basename(path))
    return list(latest.values())


# ═════════════════════════ Teams / Planner (.csv) ═════════════════════════
PLANNER_MAP = {'task_id': 'Task ID', 'title': 'Task Name', 'bucket': 'Bucket Name', 'progress': 'Progress', 'priority': 'Priority',
               'assigned_to': 'Assigned To', 'created_by': 'Created By', 'created': 'Created Date', 'started': 'Start Date',
               'due': 'Due Date', 'late': 'Late', 'completed': 'Completed Date', 'labels': 'Labels', 'description': 'Description'}

def planner_exports(paths, tagger):
    latest = {}
    for path in sorted(paths):
        as_of = re.search(r'(\d{4}-\d{2}-\d{2})', path).group(1)
        for r in csv.DictReader(open(path)):
            g = lambda k: r.get(PLANNER_MAP[k], '')
            pos, assets = tagger.in_text(g('title'))
            latest[g('task_id')] = dict(task_id=g('task_id'), title=g('title'), bucket=g('bucket'), progress=g('progress'),
                                        priority=g('priority'), assigned_to=g('assigned_to'), created_by=g('created_by'),
                                        created=mdy(g('created')), started=mdy(g('started')), due=mdy(g('due')),
                                        late=g('late').lower() == 'true', completed=mdy(g('completed')), labels=g('labels'),
                                        description=g('description') or None, asset_no=assets[0] if assets else None,
                                        position_id=pos[0] if pos else None, as_of=as_of, source_file=os.path.basename(path))
    return list(latest.values())


# ═════════════════════════ RCFA log (.csv) ═════════════════════════
def rcfa_log(path, tagger):
    out = []
    for r in csv.DictReader(open(path)):
        asset_no, pos, _ = tagger.asset(name=r['Asset'], asset_no=r['Asset Number'])
        out.append(dict(rcfa_id=r['RCFA ID'], event_date=mdy(r['Event Date']), opened=mdy(r['Opened']), closed=mdy(r['Closed']),
                        status=r['Status'], title=r['Title'], area=r['Area'], asset_no=asset_no, asset=r['Asset'], position_id=pos,
                        downtime_h=num(r['Downtime (h)']), production_loss=r['Production Loss'] or None, category=r['Category'],
                        root_cause=r['Root Cause'], contributing=r['Contributing Factors'], lead=r['Lead'],
                        action_ids=[x.strip() for x in r['Action IDs (Planner)'].split(';') if x.strip()],
                        source_file=os.path.basename(path)))
    return out


# ═════════════════════════ Envoy (.csv) ═════════════════════════
def envoy_reports(paths, tagger):
    out = []
    for path in sorted(paths):
        for r in csv.DictReader(open(path)):
            asset_no, pos, _ = tagger.asset(name=r['Asset'], asset_no=r['Asset Number'])
            out.append(dict(period=mdy(r['Period']), tag=r['Tag'], report_date=mdy(r['Report Date']), description=r['Description'],
                            area=r['Area'], asset_no=asset_no, asset=r['Asset'], position_id=pos, units=r['Units'], grade=r['Grade'] or None,
                            mean=num(r['Baseline Mean']), std=num(r['Baseline Std Dev']), low=num(r['Low Limit']), high=num(r['High Limit']),
                            min=num(r['Min']), max=num(r['Max']), hours_outside=int(r['Hours Outside']), first_outside=r['First Outside'],
                            last_outside=r['Last Outside'], direction=r['Direction'], source_file=os.path.basename(path)))
    return out


# ═════════════════════════ Pi series (.csv, wide) ═════════════════════════
def pi_series(folder):
    """Wide CSVs in mill local time -> packed series rows: hourly values one row per tag per UTC day (24 slots),
    minute values one row per tag per UTC hour (60 slots). Missing values are null. A local time that doesn't
    exist (spring-forward hour) lands on the same instant as the next hour; the first value is kept."""
    packs = {}   # (tag, res, t0) -> list
    for sub, res, step in (('hourly', 'h', 3600), ('minute', 'm', 60)):
        d = os.path.join(folder, sub); seen = set()
        for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            for r in csv.DictReader(open(os.path.join(d, fn))):
                t = dt.datetime.fromisoformat(r.pop('Timestamp')).replace(tzinfo=MILL_TZ).astimezone(dt.timezone.utc)
                if t in seen: continue
                seen.add(t)
                if res == 'h': t0 = t.replace(hour=0, minute=0); i = t.hour; n = 24
                else: t0 = t.replace(minute=0); i = t.minute; n = 60
                for tag, v in r.items():
                    arr = packs.setdefault((tag, res, t0), [None] * n)
                    arr[i] = float(v) if v != '' else None
    return [dict(tag=tag, resolution=res, t0=t0.isoformat(), step_s=3600 if res == 'h' else 60, vals=vals)
            for (tag, res, t0), vals in sorted(packs.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2]))]


# ═════════════════════════ Documents ═════════════════════════
DATE_RE = re.compile(r'\b(\d{2}/\d{2}/\d{4})\b')

def pdf_pages(path):
    from pypdf import PdfReader
    r = PdfReader(path)
    return [(p.extract_text() or '') for p in r.pages], (r.metadata.title if r.metadata and r.metadata.title else None)

def ocr_pages(path):
    """Scanned PDFs: rasterize and OCR (tesseract). In production this is the helper's job."""
    tmp = tempfile.mkdtemp()
    subprocess.run(['pdftoppm', '-r', '200', '-png', path, os.path.join(tmp, 'p')], check=True)
    pages = []
    for fn in sorted(os.listdir(tmp)):
        pages.append(subprocess.run(['tesseract', os.path.join(tmp, fn), '-', '--psm', '6'], capture_output=True, text=True).stdout)
    return pages

def docx_text(path):
    from docx import Document
    d = Document(path)
    parts = [p.text for p in d.paragraphs if p.text.strip()]
    for t in d.tables:
        for row in t.rows:
            cells = []
            for c in row.cells:
                if not cells or c.text != cells[-1]: cells.append(c.text)
            parts.append(' | '.join(cells))
    return '\n'.join(parts), d.core_properties.title

def chunks_of(text, size=1100, overlap=150):
    text = re.sub(r'[ \t]+', ' ', text).strip()
    if len(text) <= size: return [text] if text else []
    out, i = [], 0
    while i < len(text):
        j = min(len(text), i + size)
        if j < len(text):
            k = text.rfind('\n', i + size // 2, j)
            j = k if k > 0 else j
        out.append(text[i:j].strip()); i = max(j - overlap, i + 1) if j < len(text) else j
    return [c for c in out if c]

def documents(docs_root, tagger, rel_root):
    """Returns (documents, chunks). doc_id is the file name; kind from the folder it arrived in."""
    docs, chunks = [], []
    for dirpath, _, files in os.walk(docs_root):
        for fn in sorted(files):
            path = os.path.join(dirpath, fn); rel = os.path.relpath(path, rel_root)
            parts = os.path.relpath(path, docs_root).split(os.sep)
            folder = parts[0]
            if folder == 'reference' and parts[1] == 'tables':
                continue      # typed tables are attached to their reference document below
            doc_id, ext = os.path.splitext(fn)
            kind = {'vendor': 'vendor_report', 'rcfa': 'rcfa', 'drawings': 'drawing', 'reference': 'reference'}[folder]
            vendor = (lambda v: v + '.' if v.endswith(' Co') else v)(parts[1].replace('-', ' ').title()) if folder == 'vendor' else None
            if ext == '.docx':
                text, title = docx_text(path); pages, source = [text], 'docx'
            else:
                pages, title = pdf_pages(path); source = 'text'
                if sum(len(p.strip()) for p in pages) < 20:
                    pages = ocr_pages(path); source = 'ocr'; title = None
            full = '\n'.join(pages)
            if kind == 'reference':
                tbl = os.path.join(docs_root, 'reference', 'tables', doc_id + '.csv')
                if os.path.exists(tbl): pages.append('Table (CSV):\n' + open(tbl).read())
            if not title:
                title = next((l.strip() for l in full.splitlines() if len(l.strip()) > 12 and doc_id not in l), doc_id)
            dates = DATE_RE.findall(full)
            pos, assets = tagger.in_text(full)
            docs.append(dict(doc_id=doc_id, kind=kind, vendor=vendor, doc_date=mdy(dates[0]) if dates else None, title=title,
                             file_path=rel.replace(os.sep, '/'), mime='application/pdf' if ext == '.pdf' else
                             'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                             positions=pos, assets=assets, pages=len(pages), text_source=source))
            n = 0
            for pg, text in enumerate(pages, 1):
                for c in chunks_of(text):
                    cp, _ = tagger.in_text(c)
                    chunks.append(dict(doc_id=doc_id, chunk_no=n, page=pg, content=f'{title}\n{c}' if n else c, positions=cp)); n += 1
    return docs, chunks


# ═════════════════════════ Downtime events, daily production, position runs (.csv; step 05) ═════════════════════════
DOWNTIME_KIND = {'Planned': 'planned', 'Unplanned': 'unplanned', 'Sheet break': 'break', 'Slowdown': 'slowdown'}

def local_ts(s):
    return dt.datetime.fromisoformat(s).replace(tzinfo=MILL_TZ).isoformat()

def downtime_files(paths, tagger):
    out = []
    for path in sorted(paths):
        for r in csv.DictReader(open(path)):
            asset_no, pos, _ = tagger.asset(name=r['Equipment'], asset_no=r['Asset Number'])
            out.append(dict(event_id=r['Event ID'], starts_at=local_ts(r['Start']), ends_at=local_ts(r['End']), minutes=num(r['Minutes']),
                            kind=DOWNTIME_KIND.get(r['Kind'], r['Kind'].lower()), area=r['Area'] or None, equipment=r['Equipment'] or None,
                            asset_no=asset_no or (r['Asset Number'] or None), position_id=r['Position'] or pos, cause=r['Cause'] or None,
                            grade=r['Grade'] or None, crew=r['Crew'] or None, wo_no=r['WO #'] or None, rcfa_id=r['RCFA ID'] or None,
                            comment=r['Comment'] or None, source_file=os.path.basename(path)))
    return out

def production_files(paths):
    out = []
    for path in sorted(paths):
        for r in csv.DictReader(open(path)):
            out.append(dict(day=r['Mill Day'], tons=num(r['Tons']), uptime_pct=num(r['Uptime %']), breaks=int(r['Sheet Breaks'] or 0),
                            break_min=num(r['Break Minutes']), unplanned_min=num(r['Unplanned Minutes']), planned_min=num(r['Planned Minutes']),
                            slowdown_min=num(r['Slowdown Minutes']), avg_speed=num(r['Avg Speed (fpm)']), grade_hours=r['Grade Hours'] or None,
                            steam_per_t=num(r['Steam (t/t)']), kwh_per_t=num(r['Refining (kWh/t)']), reel_moist=num(r['Reel Moisture %']),
                            crew_day=r['Crew Day'] or None, crew_night=r['Crew Night'] or None, source_file=os.path.basename(path)))
    return out

def position_run_files(paths):
    """Latest export wins for each (position, installed)."""
    latest = {}
    for path in sorted(paths):
        for r in csv.DictReader(open(path)):
            latest[(r['Position'], r['Installed'])] = dict(
                position_id=r['Position'], installed=r['Installed'], position_name=r['Position Name'], removed=r['Removed'] or None,
                days=int(r['Days']) if r['Days'] else None, target_days=int(r['Target Days']) if r['Target Days'] else None,
                reason=r['Reason'] or None, condition=r['Condition'] or None, vendor=r['Vendor'] or None, style=r['Style'] or None,
                serial=r['Serial'] or None, comment=r['Comment'] or None, source_file=os.path.basename(path))
    return list(latest.values())


# ═════════════════════════ Machine Manager records (.json; step 05) ═════════════════════════
RECORD_TOOLS = ('mymachine', 'outages', 'consumables')

def record_files(folder):
    """records/<tool>.json = { record id: data } -> { tool: [{ id, data }] } for the tools the ingest accepts."""
    import json
    out = {}
    for tool in RECORD_TOOLS:
        p = os.path.join(folder, f'{tool}.json')
        if os.path.exists(p): out[tool] = [dict(id=k, data=v) for k, v in json.load(open(p)).items()]
    return out
