"""Mock PI Web API for the MM LLM demo: serves the generated Pi series (Sim Mill: demo-data/sim-mill/out/pi) with the same request
and response shapes as AVEVA PI Web API, so the orchestrator's Pi tool can later point at the real server by
changing only the base URL (plus mill network / VPN access and credentials).

    python3 tools/ingest/mock_piwebapi.py                 # http://localhost:8811/piwebapi
    python3 tools/ingest/mock_piwebapi.py --port 9000 --data demo-data/sim-mill/out/pi
    python3 tools/ingest/mock_piwebapi.py --selftest      # run the self-test against the generated data

Endpoints (GET):
    /piwebapi                                         links
    /piwebapi/dataservers                             the one data server (MILLPI01)
    /piwebapi/dataservers/{webId}/points?nameFilter=PM1:*&maxCount=1000
    /piwebapi/points?path=\\\\MILLPI01\\PM1:SPEED
    /piwebapi/points/{webId}
    /piwebapi/streams/{webId}/value?time=*
    /piwebapi/streams/{webId}/recorded?startTime=*-1d&endTime=*&maxCount=1000
    /piwebapi/streams/{webId}/interpolated?startTime=...&endTime=...&interval=1h
    /piwebapi/streams/{webId}/summary?startTime=...&endTime=...&summaryType=Average&summaryType=Maximum&summaryDuration=1d
    /piwebapi/streamsets/recorded?webId=...&webId=...&startTime=...&endTime=...

Times accept ISO 8601 (with Z/offset, or local mill time without one) and PI relative times: * (the data's "now",
its last hour, from points.json), t (today 00:00), y (yesterday 00:00), with offsets like *-7d, t-12h, *-30m. Responses use
UTC timestamps, like the real API. Data is hourly averages, with 1-minute data where the generator wrote it.
"""
import base64, csv, hashlib, json, math, os, re, sys, threading, datetime as dt
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MILL_TZ = ZoneInfo('America/New_York')
SERVER = 'MILLPI01'

def webid(prefix, s):
    return prefix + base64.urlsafe_b64encode(hashlib.sha1(s.encode()).digest()[:15]).decode().rstrip('=')


class Archive:
    """All series in memory: per tag a sorted list of (local naive datetime, value or None)."""
    def __init__(self, folder):
        meta = json.load(open(os.path.join(folder, 'points.json')))
        self.now = dt.datetime.fromisoformat(meta['demo_now'])
        self.points = {p['Name']: p for p in meta['points']}
        self.ds_webid = webid('F1DS', SERVER)
        for p in self.points.values():
            p['WebId'] = webid('F1DP', f'\\\\{SERVER}\\{p["Name"]}')
        self.by_webid = {p['WebId']: p for p in self.points.values()}
        series = {n: {} for n in self.points}
        hourly = os.path.join(folder, 'hourly')
        for fn in sorted(os.listdir(hourly)):
            for r in csv.DictReader(open(os.path.join(hourly, fn))):
                t = dt.datetime.fromisoformat(r.pop('Timestamp'))
                for k, v in r.items(): series[k][t] = float(v) if v != '' else None
        minute = os.path.join(folder, 'minute')
        for fn in sorted(os.listdir(minute)) if os.path.isdir(minute) else []:
            rows = list(csv.DictReader(open(os.path.join(minute, fn))))
            a, b = dt.datetime.fromisoformat(rows[0]['Timestamp']), dt.datetime.fromisoformat(rows[-1]['Timestamp'])
            for k in rows[0]:
                if k == 'Timestamp': continue
                for t in [t for t in series[k] if a <= t <= b]: del series[k][t]     # minute data replaces those hours
                for r in rows: series[k][dt.datetime.fromisoformat(r['Timestamp'])] = float(r[k]) if r[k] != '' else None
        self.series = {k: sorted(v.items()) for k, v in series.items()}

    # ---- time handling ----
    def parse_time(self, s, default=None):
        if s is None or s == '': s = default
        s = s.strip()
        m = re.fullmatch(r'(\*|t|today|y|yesterday)?\s*([+-]\s*\d+(?:\.\d+)?\s*(?:s|m|h|d|w))?', s, re.I)
        if m and (m.group(1) or m.group(2)):
            base = {'*': self.now, 't': self.now.replace(hour=0, minute=0), 'today': self.now.replace(hour=0, minute=0),
                    'y': self.now.replace(hour=0, minute=0) - dt.timedelta(days=1), 'yesterday': self.now.replace(hour=0, minute=0) - dt.timedelta(days=1)}[(m.group(1) or '*').lower()]
            return base + (parse_interval(m.group(2).replace(' ', '')) if m.group(2) else dt.timedelta(0))
        t = dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
        if t.tzinfo: t = t.astimezone(MILL_TZ).replace(tzinfo=None)
        return t

    @staticmethod
    def iso(t):
        return t.replace(tzinfo=MILL_TZ).astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    def tvq(self, t, v, units):
        if v is None:
            return {'Timestamp': self.iso(t), 'Value': {'Name': 'No Data', 'Value': 248, 'IsSystem': True}, 'UnitsAbbreviation': '',
                    'Good': False, 'Questionable': False, 'Substituted': False, 'Annotated': False}
        return {'Timestamp': self.iso(t), 'Value': v, 'UnitsAbbreviation': units, 'Good': True, 'Questionable': False,
                'Substituted': False, 'Annotated': False}

    # ---- data ----
    def recorded(self, name, a, b, max_count=1000):
        out = [(t, v) for t, v in self.series[name] if a <= t <= b]
        return out[:max_count]

    def at(self, name, t):
        s = self.series[name]
        lo, hi = 0, len(s)
        while lo < hi:
            mid = (lo + hi) // 2
            if s[mid][0] <= t: lo = mid + 1
            else: hi = mid
        if lo == 0: return None
        t0, v0 = s[lo - 1]
        if self.points[name]['Step'] or lo == len(s) or t0 == t: return v0
        t1, v1 = s[lo]
        if v0 is None or v1 is None: return None
        return v0 + (v1 - v0) * (t - t0).total_seconds() / (t1 - t0).total_seconds()


def parse_interval(s):
    m = re.fullmatch(r'([+-]?)(\d+(?:\.\d+)?)(s|m|h|d|w)', s.strip())
    if not m: raise ValueError(f'bad interval {s}')
    sign = -1 if m.group(1) == '-' else 1
    return sign * dt.timedelta(**{{'s': 'seconds', 'm': 'minutes', 'h': 'hours', 'd': 'days', 'w': 'weeks'}[m.group(3)]: float(m.group(2))})


class Api:
    def __init__(self, archive, base='http://localhost:8811/piwebapi'):
        self.a = archive; self.base = base

    def point(self, p):
        w = p['WebId']; L = f'{self.base}/streams/{w}'
        return {'WebId': w, 'Id': int(hashlib.sha1(p['Name'].encode()).hexdigest()[:6], 16), 'Name': p['Name'],
                'Path': f'\\\\{SERVER}\\{p["Name"]}', 'Descriptor': p['Descriptor'], 'PointClass': p['PointClass'],
                'PointType': p['PointType'], 'DigitalSetName': '', 'EngineeringUnits': p['EngineeringUnits'], 'Span': 100.0,
                'Zero': 0.0, 'Step': p['Step'], 'Future': False, 'DisplayDigits': -5,
                'Links': {'Self': f'{self.base}/points/{w}', 'DataServer': f'{self.base}/dataservers/{self.a.ds_webid}',
                          'InterpolatedData': f'{L}/interpolated', 'RecordedData': f'{L}/recorded', 'SummaryData': f'{L}/summary',
                          'Value': f'{L}/value', 'EndValue': f'{L}/end'}}

    def handle(self, path, q):
        """Returns (status, body). q: dict of lists (as from parse_qs)."""
        one = lambda k, d=None: (q.get(k) or q.get(k[0].upper() + k[1:]) or [d])[0]
        parts = [p for p in path.split('/') if p]
        if not parts or parts[0].lower() != 'piwebapi': return 404, err('Not found')
        parts = parts[1:]
        try:
            if not parts:
                return 200, {'Links': {'Self': self.base, 'DataServers': f'{self.base}/dataservers', 'Points': f'{self.base}/points'}}
            if parts == ['dataservers']:
                return 200, {'Links': {}, 'Items': [{'WebId': self.a.ds_webid, 'Id': '00000000-0000-0000-0000-00000000mm01', 'Name': SERVER,
                                                      'Path': f'\\\\PIServers[{SERVER}]', 'IsConnected': True, 'ServerVersion': '3.4.445.688',
                                                      'Links': {'Points': f'{self.base}/dataservers/{self.a.ds_webid}/points'}}]}
            if len(parts) == 3 and parts[0] == 'dataservers' and parts[2] == 'points':
                if parts[1] != self.a.ds_webid: return 404, err('Data server not found')
                pat = re.compile('^' + re.escape(one('nameFilter', '*')).replace('\\*', '.*').replace('\\?', '.') + '$', re.I)
                items = [self.point(p) for n, p in self.a.points.items() if pat.match(n)][:int(one('maxCount', 1000))]
                return 200, {'Links': {}, 'Items': items}
            if parts == ['points']:
                path_ = one('path', '')
                name = path_.split('\\')[-1]
                if name not in self.a.points: return 404, err(f'PI Point not found: {path_}')
                return 200, self.point(self.a.points[name])
            if len(parts) == 2 and parts[0] == 'points':
                p = self.a.by_webid.get(parts[1])
                return (200, self.point(p)) if p else (404, err('Point not found'))
            if parts[0] == 'streams' and len(parts) == 3:
                p = self.a.by_webid.get(parts[1])
                if not p: return 404, err('Stream not found')
                return 200, self.stream(p, parts[2], q, one)
            if parts == ['streamsets', 'recorded']:
                items = []
                for w in q.get('webId', []) + q.get('WebId', []):
                    p = self.a.by_webid.get(w)
                    if not p: return 404, err(f'Stream not found: {w}')
                    items.append({'WebId': w, 'Name': p['Name'], 'Path': f'\\\\{SERVER}\\{p["Name"]}', 'Items': self.stream(p, 'recorded', q, one)['Items'],
                                  'UnitsAbbreviation': p['EngineeringUnits']})
                return 200, {'Links': {}, 'Items': items}
            return 404, err('Not found')
        except ValueError as e:
            return 400, err(str(e))

    def stream(self, p, kind, q, one):
        a, n, u = self.a, p['Name'], p['EngineeringUnits']
        if kind in ('value', 'end'):
            t = a.parse_time(one('time', '*')) if kind == 'value' else a.now
            return a.tvq(t, a.at(n, t), u)
        t0, t1 = a.parse_time(one('startTime'), '*-1d'), a.parse_time(one('endTime'), '*')
        if t1 < t0: raise ValueError('endTime is before startTime')
        if kind == 'recorded':
            return {'Links': {}, 'Items': [a.tvq(t, v, u) for t, v in a.recorded(n, t0, t1, int(one('maxCount', 1000)))]}
        if kind == 'interpolated':
            step = parse_interval(one('interval', '1h')); out, t = [], t0
            if step.total_seconds() <= 0: raise ValueError('interval must be positive')
            while t <= t1 and len(out) < 150000:
                out.append(a.tvq(t, a.at(n, t), u)); t += step
            return {'Links': {}, 'Items': out}
        if kind == 'summary':
            types = q.get('summaryType') or q.get('SummaryType') or ['Total']
            types = [x for s in types for x in s.split(',')]
            dur = parse_interval(one('summaryDuration')) if one('summaryDuration') else (t1 - t0)
            items, s = [], t0
            while s < t1:
                e = min(s + dur, t1)
                vals = [v for t, v in a.recorded(n, s, e, 10 ** 9) if v is not None and t < e]
                for ty in types:
                    v = summarize(ty, vals, (e - s))
                    items.append({'Type': ty, 'Value': a.tvq(s, v, u) if v is not None else a.tvq(s, None, u)})
                s = e
            return {'Links': {}, 'Items': items}
        raise ValueError(f'unknown stream call {kind}')


def summarize(kind, vals, span):
    if not vals: return None
    n = len(vals); mean = sum(vals) / n
    return {'Average': mean, 'Minimum': min(vals), 'Maximum': max(vals), 'Range': max(vals) - min(vals), 'Count': float(n),
            'StdDev': math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1)) if n > 1 else 0.0,
            'Total': mean * span.total_seconds() / 86400,   # time-weighted total per day, like PI's default
            }.get(kind)

def err(msg): return {'Errors': [msg]}


def serve(folder, port):
    api = Api(Archive(folder), f'http://localhost:{port}/piwebapi')
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            u = urlparse(self.path); status, body = api.handle(u.path, parse_qs(u.query))
            b = json.dumps(body).encode()
            self.send_response(status); self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*'); self.send_header('Content-Length', str(len(b))); self.end_headers()
            self.wfile.write(b)
        def log_message(self, *a): pass
    srv = ThreadingHTTPServer(('127.0.0.1', port), H)
    return srv, api


def selftest(folder):
    """Round-trips the API against the CSVs (any generated year: it reads the tags from the data). Returns problems."""
    import glob, urllib.request, urllib.error
    errs = []
    def need(ok, msg):
        if not ok: errs.append('mock PI Web API: ' + msg)
    srv, api = serve(folder, 0); port = srv.server_address[1]
    api.base = f'http://localhost:{port}/piwebapi'
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    get = lambda p: json.loads(urllib.request.urlopen(f'http://localhost:{port}{p}', timeout=10).read())
    try:
        f = sorted(glob.glob(os.path.join(folder, 'hourly', '*.csv')))[-1]
        rows = list(csv.DictReader(open(f))); tags = [c for c in rows[0] if c != 'Timestamp']
        ds = get('/piwebapi/dataservers')['Items']; need(ds and ds[0]['Name'] == SERVER, 'dataservers')
        pts = get(f"/piwebapi/dataservers/{ds[0]['WebId']}/points?nameFilter=*")['Items']
        need({p['Name'] for p in pts} >= set(tags), f'{len(pts)} points for {len(tags)} tags in the CSV')
        tag = tags[0]; w = get('/piwebapi/points?path=' + urllib.request.quote(f'\\\\{SERVER}\\{tag}'))['WebId']
        r0 = rows[len(rows) // 2]; t0 = r0['Timestamp']
        rec = get(f'/piwebapi/streams/{w}/recorded?startTime={t0}&endTime={t0}')['Items']
        need(rec and abs(rec[0]['Value'] - float(r0[tag])) < 1e-9, f'{tag} at {t0}: recorded value differs from the CSV')
        need(rec and rec[0]['Timestamp'].endswith('Z'), 'UTC timestamps')
        it = get(f'/piwebapi/streams/{w}/interpolated?startTime=*-6h&endTime=*&interval=1h')['Items']
        need(len(it) == 7, f'{len(it)} interpolated items for *-6h..*')
        sm = get(f'/piwebapi/streams/{w}/summary?startTime=*-7d&endTime=*&summaryType=Average&summaryDuration=1d')['Items']
        need(len(sm) == 7, f'{len(sm)} daily summaries for *-7d')
        try:
            urllib.request.urlopen(f'http://localhost:{port}/piwebapi/points?path=%5C%5CMILLPI01%5CNOPE', timeout=5); need(False, 'unknown point should 404')
        except urllib.error.HTTPError as e:
            need(e.code == 404, f'unknown point gave {e.code}')
    finally:
        srv.shutdown()
    return errs

if __name__ == '__main__':
    args = sys.argv[1:]
    folder = args[args.index('--data') + 1] if '--data' in args else os.path.join(ROOT, 'demo-data', 'sim-mill', 'out', 'pi')
    if '--selftest' in args:
        e = selftest(folder)
        for x in e: print('FAIL', x)
        sys.exit(1 if e else print('mock PI Web API ok'))
    port = int(args[args.index('--port') + 1]) if '--port' in args else 8811
    srv, _ = serve(folder, port)
    print(f'Mock PI Web API on http://localhost:{port}/piwebapi  (data: {folder}, now: {_.a.now:%b %d %Y %H:%M})')
    srv.serve_forever()
