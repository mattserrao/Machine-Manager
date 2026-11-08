"""Operations Outage Planning works signed out: demo outages load, edits stay in this browser, Reset demo
restores them, and on a phone the outage cards are one per swipe with a pager.

    python3 tests/browser/outages_demo.py http://localhost:8000/
"""
import sys, os
from playwright.sync_api import sync_playwright

BASE = sys.argv[1]
URL = BASE + "OperationsOutagePlanning.html"
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok: failures.append(name)

with sync_playwright() as p:
    br = p.chromium.launch(channel=os.environ.get("PW_CHANNEL") or None, headless=True)

    # ---- Desktop: demo data, saving, reset ----
    ctx = br.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(1200)
    cards = pg.locator(".lane > .card:not(.ghost)")
    check("demo: upcoming outages shown", cards.count() >= 5, f"{cards.count()} cards")
    w = pg.evaluate("Math.max(...[...document.querySelectorAll('.lane > .card.small')].map(c => c.offsetWidth))")
    check("compact cards keep their width", w <= 330, f"{w}px")
    first = pg.locator(".lane > .card").first.inner_text()
    check("next outage has packages, tasks and manning", "2 packages" in first and "2/6 tasks" in first and "Manning 37/40" in first, first.replace("\n", " | ")[:200])
    check("annual outage in the demo", pg.locator(".lane > .card.annual").count() == 1)
    check("past outage kept", "Past (1)" in pg.locator("#pastBtn").inner_text())
    pg.locator(".lane > .card").first.click(); pg.wait_for_timeout(500)
    check("opened card lists package steps", pg.locator(".card.big .pk").count() == 2)
    pg.locator(".card.big .addtask input").fill("Demo test task"); pg.keyboard.press("Enter"); pg.wait_for_timeout(400)
    pg.reload(wait_until="networkidle"); pg.wait_for_timeout(1000)
    check("demo edits survive a reload", pg.locator(".card.big").get_by_text("Demo test task").count() == 1)
    pg.locator("#resetDemoBtn").click(); pg.wait_for_timeout(500)
    check("Reset demo restores the sample outages", pg.get_by_text("Demo test task").count() == 0)
    check("no script errors (desktop)", not errs, "; ".join(errs))
    ctx.close()

    # ---- Phone: one card per swipe, pager, previous / next on an opened card ----
    ctx = br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(1200)
    lane = pg.locator(".lane").first
    cw = pg.evaluate("document.querySelector('.lane > .card').offsetWidth")
    check("phone: one card fills the row, the next peeks in", 310 <= cw <= 370, f"{cw}px")
    check("phone: pager shown", pg.locator(".pager").first.is_visible())
    pg.locator(".pager .ib").nth(1).click(); pg.wait_for_timeout(900)
    at = pg.locator(".pager .at").first.inner_text()
    check("phone: next arrow moves one outage", "2 of" in at, at)
    pg.locator(".pager .dot").first.click(); pg.wait_for_timeout(900)
    check("phone: dot jumps back", "1 of" in pg.locator(".pager .at").first.inner_text())
    pg.locator(".lane > .card").first.click(); pg.wait_for_timeout(500)
    d0 = pg.locator(".card.big .date").inner_text()
    pg.locator(".card.big .nav .ib").nth(1).click(); pg.wait_for_timeout(500)
    d1 = pg.locator(".card.big .date").inner_text()
    check("phone: opened card steps to the next outage", d0 != d1, f"{d0} → {d1}")
    check("no script errors (phone)", not errs, "; ".join(errs))
    ctx.close(); br.close()

if failures: print(f"\n{len(failures)} failed"); sys.exit(1)
print("\nall passed")
