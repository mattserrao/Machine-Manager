"""Signed out, the demo tools show Sim Mill (the public demo org) read-only, from the live project.

    python3 tests/browser/demo_sim_mill.py http://localhost:8000/
"""
import sys, os
from playwright.sync_api import sync_playwright

BASE = sys.argv[1]
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok: failures.append(name)

with sync_playwright() as p:
    br = p.chromium.launch(channel=os.environ.get("PW_CHANNEL") or None, headless=True)
    ctx = br.new_context(viewport={"width": 1400, "height": 900}); errs = []
    def page(name):
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(f"{name}: {str(e)[:160]}"))
        pg.goto(BASE + name, wait_until="networkidle"); pg.wait_for_timeout(2500); return pg

    pg = page("MyMachine.html")
    chip = pg.locator("#acct").inner_text()
    check("My Machine: demo chip says view only", "view only" in chip, chip.replace("\n", " "))
    rows = pg.locator("tr[data-id]").count()
    check("My Machine: Sim Mill's positions are shown", rows >= 30, f"{rows} rows")
    check("My Machine: the dryer felt rolls are there", pg.locator("tr[data-id='d3-froll-1']").count() == 1)

    pg = page("OperationsOutagePlanning.html")
    sub = pg.locator("#brandSub").inner_text()
    check("Outage Planning: shows the Sim Mill demo, view only", "Sim Mill" in sub and "view only" in sub, sub)
    cards = pg.locator(".lane > .card:not(.ghost)").count()
    check("Outage Planning: upcoming outages shown", cards >= 3, f"{cards} cards")

    pg = page("ConsumablesTracker.html")
    check("Consumables: the Sim Mill board loads", "PM1 Consumables" in pg.content())

    pg = page("index.html")
    check("Home: the outage tile is marked as the Sim Mill demo", "Demo · Sim Mill" in pg.locator("#tOutage").inner_text())

    check("no script errors", not errs, "; ".join(errs))
    br.close()

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
sys.exit(1 if failures else 0)
