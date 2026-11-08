"""Every page loads in demo mode without script errors or missing files, and stored XSS in My Machine stays blocked.

    python3 tests/browser/smoke.py http://localhost:8000/
"""
import sys, os, json, tempfile
from playwright.sync_api import sync_playwright

BASE = sys.argv[1]
PAGES = ["index.html", "MyMachine.html", "OperationsOutagePlanning.html", "Whiteboard.html", "TaskPackageLibrary.html",
         "ConsumablesTracker.html", "VendorReports.html", "MMLLM.html", "Daily.html", "DailyNotes.html", "Downtime.html"]
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok: failures.append(name)

with sync_playwright() as p:
    br = p.chromium.launch(channel=os.environ.get("PW_CHANNEL") or None, headless=True)
    for name in PAGES:
        ctx = br.new_context(); pg = ctx.new_page(); errs, missing = [], []
        pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
        pg.on("response", lambda r: r.status >= 400 and r.url.startswith(BASE) and missing.append(r.url[len(BASE):]))
        pg.goto(BASE + name, wait_until="networkidle"); pg.wait_for_timeout(800)
        check(f"{name} loads cleanly", not errs and not missing, "; ".join(errs + [f"missing {m}" for m in missing]))
        ctx.close()

    # A tampered export (or record) must not run script in My Machine.
    payload = {"machine": {"name": "PM1", "press": {"nips": 2, "tandem": True}, "dryers": [{"type": "uno"}],
                           "refiners": [{"id": 'x"><img src=x onerror="window.__xss1=1">', "name": "BP1"}]},
               "items": {"form-top": {"installed": "2026-10-01", "target": 12,
                                      "condition": 'worn" onmouseover="x" ><img src=x onerror="window.__xss2=1"><b "',
                                      "vendor": "<img src=x onerror=window.__xss3=1>", "conditionNote": "<img src=x onerror=window.__xss4=1>"}}}
    f = os.path.join(tempfile.mkdtemp(), "evil.json"); json.dump(payload, open(f, "w"))
    ctx = br.new_context(); pg = ctx.new_page()
    pg.goto(BASE + "MyMachine.html", wait_until="networkidle")
    pg.locator("input[type=file]").first.set_input_files(f); pg.wait_for_timeout(1000)
    pg.locator("tr[data-id='form-top']").first.click(); pg.wait_for_timeout(500)
    ran = pg.evaluate("[window.__xss1, window.__xss2, window.__xss3, window.__xss4].filter(Boolean).length")
    check("My Machine: tampered import runs no script", ran == 0, f"{ran} payloads ran")
    ctx.close(); br.close()

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
sys.exit(1 if failures else 0)
