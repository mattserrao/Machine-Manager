"""Operations Outage Planning works signed out: demo outages load, edits stay in this browser, Reset demo
restores them; outage times, task assignment, crews, accept / decline and the Word export work, and on a phone the outage cards are one per swipe with a pager.

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

# Signed out, the demo tools read Sim Mill read-only (tests/browser/demo_sim_mill.py). This test is about the
# browser-only demo the pages fall back to when the server can't be reached, so it blocks the server.
def offline(ctx): ctx.route("**/*.supabase.co/**", lambda r: r.abort())

with sync_playwright() as p:
    br = p.chromium.launch(channel=os.environ.get("PW_CHANNEL") or None, headless=True)

    # ---- Desktop: demo data, saving, reset ----
    ctx = br.new_context(viewport={"width": 1400, "height": 900}, accept_downloads=True); offline(ctx); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(1200)
    cards = pg.locator(".lane > .card:not(.ghost)")
    check("demo: upcoming outages shown", cards.count() >= 5, f"{cards.count()} cards")
    w = pg.evaluate("Math.max(...[...document.querySelectorAll('.lane > .card.small')].map(c => c.offsetWidth))")
    check("compact cards keep their width", w <= 330, f"{w}px")
    first = pg.locator(".lane > .card").first.inner_text()
    check("next outage has packages, tasks and manning", "2 packages" in first and "2/10 tasks" in first and "Manning 37/40" in first, first.replace("\n", " | ")[:200])
    check("card shows planned shutdown → on reel and hours", "04:00 → " in first and "· 16 h" in first, first.replace("\n", " | ")[:200])
    check("annual outage in the demo", pg.locator(".lane > .card.annual").count() == 1)
    check("past outage kept", "Past (1)" in pg.locator("#pastBtn").inner_text())
    pg.locator(".lane > .card").first.click(); pg.wait_for_timeout(500)
    check("opened card lists package steps", pg.locator(".card.big .pk").count() == 2)
    check("tasks grouped by phase", pg.locator(".card.big .tg-h").count() >= 4, str(pg.locator(".card.big .tg-h").all_inner_texts()))
    check("task shows area, crew and person", pg.locator(".card.big .tmeta", has_text="Crew A · K. Lavoie").count() >= 1)
    # Decline the first suggested fabric/roll: it stays here struck through and moves to the next outage
    row = pg.locator(".card.big .due:has(.acts)").first; nm = row.locator(".nm a").inner_text()
    row.locator("button", has_text="Decline").click(); pg.wait_for_timeout(400)
    check("declined item marked and moved", pg.locator(".card.big .due.declined", has_text=nm).count() == 1
      and "moved to" in pg.locator(".card.big .due.declined", has_text=nm).inner_text())
    pg.locator(".card.big .shrink").click(); pg.wait_for_timeout(300)
    pg.locator(".lane > .card").nth(1).click(); pg.wait_for_timeout(500)
    check("declined item shows on the next outage as deferred", pg.locator(".card.big .due", has_text=nm).filter(has_text="Deferred from").count() == 1)
    pg.locator(".card.big .shrink").click(); pg.wait_for_timeout(300)
    pg.locator(".lane > .card").first.click(); pg.wait_for_timeout(500)
    pg.locator(".card.big .due:has(.acts)").first.locator("button", has_text="Accept").click(); pg.wait_for_timeout(300)
    check("accept marks it and offers a package", pg.locator(".card.big .due .chg", has_text="Accepted").count() >= 1 and "Add " in pg.locator("#toast").inner_text(), pg.locator("#toast").inner_text())
    # Assign a task to a crew and a person
    pg.locator(".card.big .tmeta.empty").first.click(); pg.wait_for_timeout(200)
    pg.locator("#picker select").nth(1).select_option("DE"); pg.locator("#picker select").nth(2).select_option("C")
    pg.locator("#picker input").fill("A. Plante"); pg.locator("#picker input").press("Enter"); pg.wait_for_timeout(300)
    check("task assigned to crew C and a person", pg.locator(".card.big .tmeta", has_text="DE · Crew C · A. Plante").count() == 1)
    # Manning: every shift at once on desktop; click a name to change it
    check("manning grid: 4 shifts side by side", pg.locator(".card.big .mtab thead th").count() == 5 and pg.locator(".card.big .tabs").count() == 0)
    cell = pg.locator(".card.big .mtab tbody tr").nth(1).locator("td").nth(2)
    cell.locator(".nm").click(); cell.locator("input").fill("Q. Tester"); cell.locator("input").press("Enter"); pg.wait_for_timeout(300)
    check("manning grid: name changed in place", pg.locator(".card.big .mtab .nm", has_text="Q. Tester").count() == 1)
    cell = pg.locator(".card.big .mtab tbody tr").nth(1).locator("td").nth(3)
    was = cell.locator(".nm").inner_text()
    cell.locator(".nm").click(); cell.locator("input").fill("Nobody"); cell.locator("input").press("Escape"); pg.wait_for_timeout(300)
    check("manning grid: Escape cancels", cell.locator(".nm").inner_text() == was and pg.locator(".card.big").count() == 1)
    # Crews editor
    pg.locator("#crewBtn").click(); pg.wait_for_timeout(200)
    check("crews editor lists the four crews", pg.locator("#crCols textarea").count() == 4 and "E. Thibault" in pg.locator("#cr-C").input_value())
    pg.locator("#crCancel").click()
    # Word export
    with pg.expect_download() as dl: pg.locator(".card.big .wordbtn").click()
    f = dl.value; data = open(f.path(), "rb").read()
    check("Word export downloads a .docx", f.suggested_filename.endswith(".docx") and data[:2] == b"PK" and len(data) > 8000, f"{f.suggested_filename} {len(data)} bytes")
    pg.locator(".card.big .addtask input").fill("Demo test task"); pg.keyboard.press("Enter"); pg.wait_for_timeout(400)
    pg.reload(wait_until="networkidle"); pg.wait_for_timeout(1000)
    check("demo edits survive a reload", pg.locator(".card.big").get_by_text("Demo test task").count() == 1)
    pg.locator("#resetDemoBtn").click(); pg.wait_for_timeout(500)
    check("Reset demo restores the sample outages", pg.get_by_text("Demo test task").count() == 0)
    check("no script errors (desktop)", not errs, "; ".join(errs))
    ctx.close()

    # ---- Phone: one card per swipe, pager, previous / next on an opened card ----
    ctx = br.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True); offline(ctx); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(1200)
    lane = pg.locator(".lane").first
    cw = pg.evaluate("document.querySelector('.lane > .card').offsetWidth")
    check("phone: one card fills the row, the next peeks in", 310 <= cw <= 370, f"{cw}px")
    check("phone: pager shown", pg.locator(".pager").first.is_visible())
    pg.locator(".lane > .card").first.click(); pg.wait_for_timeout(400)
    check("phone: manning keeps the shift tabs", pg.locator(".card.big .tabs").count() == 1 and pg.locator(".card.big .mtab").count() == 0)
    pg.locator(".card.big .shrink").click(); pg.wait_for_timeout(300)
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
