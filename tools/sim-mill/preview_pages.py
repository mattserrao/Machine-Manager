"""Screenshots of the data pages against a LOCAL database (rpc calls answered from Postgres as anon), for review
before Sim Mill is loaded live. Needs the site served on :8799 and both orgs loaded and public in dbname=mm_full.
    python3 -m http.server 8799 &  python3 tools/sim-mill/preview_pages.py
"""
import json, psycopg
from playwright.sync_api import sync_playwright
c = psycopg.connect("host=localhost dbname=mm_full user=postgres", autocommit=True)
def rpc(fn, args):
    c.execute("reset role")
    rs = c.execute("select p.proretset from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname='public' and p.proname=%s", (fn,)).fetchone()
    c.execute("set role anon")
    named = ', '.join(f'{k} => %s' for k in args)
    vals = [json.dumps(v) if isinstance(v, (dict, list)) else v for v in args.values()]
    q = f"select coalesce(json_agg(t), '[]'::json) from public.{fn}({named}) t" if rs and rs[0] else f"select to_json(public.{fn}({named}))"
    try: return c.execute(q, vals).fetchone()[0]
    finally: c.execute("reset role")
BASE = "http://localhost:8799/"
shots = [("Downtime.html?org=Sim%20Mill", "downtime"), ("Daily.html?org=Sim%20Mill&day=2026-05-18", "daily-may18"),
         ("Daily.html?org=Sim%20Mill", "daily-oct31"), ("VendorReports.html?org=Sim%20Mill&pos=p2-felt-top", "vendor-p2felt"),
         ("VendorReports.html?org=Sim%20Mill", "vendor-all"), ("MMLLM.html?org=Sim%20Mill", "mmllm")]
with sync_playwright() as p:
    b = p.chromium.launch()
    for path, name in shots:
        pg = b.new_page(viewport={"width": 1360, "height": 900}); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        def route(r):
            u = r.request.url
            if "/rest/v1/rpc/" in u:
                fn = u.split("/rest/v1/rpc/")[1].split("?")[0]
                body = json.loads(r.request.post_data or "{}")
                try: data = rpc(fn, body); return r.fulfill(status=200, body=json.dumps(data), content_type="application/json")
                except Exception as e: return r.fulfill(status=400, body=json.dumps({"message": str(e)}), content_type="application/json")
            if "supabase.co" in u: return r.fulfill(status=200, body="{}", content_type="application/json")
            return r.continue_()
        pg.route("**/*", route)
        pg.goto(BASE + path); pg.wait_for_timeout(3500)
        pg.screenshot(path=f"demo-data/sim-mill/preview/{name}.png", full_page=True)
        print(name, "errors:", errs[:2])
        pg.close()
    b.close()
