"""Use the three board tools in a headless browser (demo mode) and check what happens.

    python3 tests/browser/boards.py http://localhost:8000/

Exits non-zero on any failed check or page error.
"""
import sys, os, json, tempfile
from playwright.sync_api import sync_playwright

BASE = sys.argv[1]
failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def open_page(br, name):
    ctx = br.new_context(viewport={"width": 1400, "height": 860}, accept_downloads=True)
    pg = ctx.new_page()
    pg.errors = []
    pg.on("pageerror", lambda e: pg.errors.append(str(e)[:300]))
    pg.on("dialog", lambda d: d.accept())
    pg.goto(BASE + name, wait_until="networkidle"); pg.wait_for_timeout(700)
    if pg.locator("#tipsOk").is_visible(): pg.click("#tipsOk")
    return ctx, pg


notes = lambda pg: pg.locator("#world > .note").count()
menu_text = lambda pg: pg.locator("#menu").inner_text()


def menu_click(pg, text):
    pg.locator("#menu .mi").filter(has_text=text).first.click(); pg.wait_for_timeout(250)


def empty_spot(pg):
    b = pg.locator("#board").bounding_box()
    return b["x"] + 220, b["y"] + b["height"] - 140


with sync_playwright() as p:
    br = p.chromium.launch(channel=os.environ.get("PW_CHANNEL") or None, headless=True)

    # ───────── Whiteboard ─────────
    ctx, pg = open_page(br, "Whiteboard.html")
    x, y = empty_spot(pg)
    pg.mouse.dblclick(x, y); pg.wait_for_timeout(300)
    check("WB: double-click opens the editor", pg.locator("#modal").is_visible())
    pg.fill("#edText", "Hello outage\n- [ ] Shower nozzles\n- [ ] Felt run")
    pg.fill("#edOwner", "Matt") if pg.locator("#edOwner").count() else None
    if pg.locator("#edDue").count(): pg.fill("#edDue", "2026-11-11")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    n = pg.locator("#world > .note").first
    check("WB: note shows its title and checklist", "Hello outage" in n.inner_text() and "0/2" in n.inner_text(), n.inner_text()[:80])
    check("WB: due date chip", n.locator(".chip.due").count() == 1)
    pg.locator("#world > .note .cb").first.click(); pg.wait_for_timeout(200)
    check("WB: ticking a checkbox", "1/2" in pg.locator("#world > .note").first.inner_text())
    pg.keyboard.press("Control+z"); pg.wait_for_timeout(200)
    check("WB: undo", "0/2" in pg.locator("#world > .note").first.inner_text())
    pg.keyboard.press("Control+Shift+z"); pg.wait_for_timeout(200)
    check("WB: redo", "1/2" in pg.locator("#world > .note").first.inner_text())
    pg.mouse.click(x + 400, y - 300); pg.keyboard.press("n"); pg.wait_for_timeout(300); pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    check("WB: N adds a note", notes(pg) == 2, str(notes(pg)))
    b = pg.locator("#world > .note").first.bounding_box()
    pg.mouse.click(b["x"] + 40, b["y"] + 20, button="right"); pg.wait_for_timeout(200)
    check("WB: note menu has the status row", "In progress" in menu_text(pg))
    pg.keyboard.press("Escape")
    pg.locator("#tabs > .ib").last.click(); menu_click(pg, "Blank")
    check("WB: new blank tab", pg.locator("#tabs .tab").count() == 2 and notes(pg) == 0)
    pg.locator("#tabs > .ib").last.click(); menu_click(pg, "Outage plan template"); pg.wait_for_timeout(400)
    check("WB: outage template", pg.locator("#tabs .tab").count() == 3 and pg.locator("#world > .frame").count() == 6)
    pg.locator("#tabs .tab.active").dblclick(); pg.keyboard.type("Nov 11 outage"); pg.keyboard.press("Enter"); pg.wait_for_timeout(200)
    check("WB: rename a tab", "Nov 11 outage" in pg.locator("#tabs .tab.active").inner_text())
    pg.locator("#tabs .tab.active .tx").click(); pg.locator("#tabs .tab.active .tx").click(); pg.wait_for_timeout(300)
    check("WB: delete a tab", pg.locator("#tabs .tab").count() == 2)
    pg.keyboard.press("Control+z"); pg.wait_for_timeout(300)
    check("WB: undo brings the tab back", pg.locator("#tabs .tab").count() == 3 and "Nov 11 outage" in pg.locator("#tabs .tab.active").inner_text())
    pg.locator("#tabs .tab").first.click(); pg.wait_for_timeout(300)
    pg.keyboard.press("/"); pg.keyboard.type("nozzles"); pg.wait_for_timeout(300)
    dim = pg.locator("#world > .note.dim, #world > .note.faded, #world > .note.hit, #world > .note.match").count()
    check("WB: search marks notes", dim >= 1, f"{dim} marked")
    pg.keyboard.press("Escape"); pg.keyboard.press("Escape")
    with pg.expect_download() as d:
        pg.keyboard.press("Control+s")
    path = os.path.join(tempfile.mkdtemp(), d.value.suggested_filename); d.value.save_as(path)
    check("WB: export a .whiteboard file", path.endswith(".whiteboard") and json.load(open(path))["board"]["notes"])
    pg.wait_for_timeout(800)
    pg.reload(wait_until="networkidle"); pg.wait_for_timeout(700)
    check("WB: boards survive a reload", pg.locator("#tabs .tab").count() == 3, str(pg.locator("#tabs .tab").count()))
    pg.locator("#importFile").set_input_files(path); pg.wait_for_timeout(600)
    check("WB: import opens it in a new tab", pg.locator("#tabs .tab").count() == 4 and notes(pg) == 2)
    check("WB: no page errors", not pg.errors, "; ".join(pg.errors))
    ctx.close()

    # ───────── Ops Task Library ─────────
    ctx, pg = open_page(br, "TaskPackageLibrary.html")
    check("TPL: opens on the library with 5 examples", pg.locator("#library").is_visible() and pg.locator(".pkg:not(.pkg-new)").count() == 5)
    pg.get_by_text("Dryer Felt Change", exact=True).first.click(); pg.wait_for_timeout(500)
    check("TPL: opening a package shows its steps", not pg.locator("#library").is_visible() and notes(pg) > 10, str(notes(pg)))
    n = pg.locator("#world > .note").first; b = n.bounding_box()
    pg.mouse.click(b["x"] + 40, b["y"] + 12, button="right"); pg.wait_for_timeout(200)
    check("TPL: step menu has the status row", "In progress" in menu_text(pg))
    pg.locator("#menu .mrow .sp").filter(has_text="In progress").first.click(); pg.wait_for_timeout(250)
    check("TPL: setting a status", "In progress" in pg.locator("#world > .note").first.inner_text())
    pg.keyboard.press("Escape")
    pg.click("#infoBtn"); pg.wait_for_timeout(200)
    check("TPL: details sheet counts steps", "steps" in pg.locator("#pkgStats").inner_text(), pg.locator("#pkgStats").inner_text())
    pg.click("#pkgDone")
    pg.click("#libBtn"); pg.wait_for_timeout(300)
    pg.click("#libNew"); menu_click(pg, "Blank package"); pg.wait_for_timeout(300)
    check("TPL: new blank package opens with its details", pg.locator("#pkgDlg").is_visible() and pg.input_value("#pkgName").startswith("New task package"))
    pg.fill("#pkgName", "Uhle box covers"); pg.click("#pkgDone"); pg.wait_for_timeout(200)
    check("TPL: renamed in the top bar", "Uhle box covers" in pg.locator("#brandSub").inner_text())
    pg.click("#infoBtn"); pg.click("#pkgDelete"); pg.click("#pkgDelete"); pg.wait_for_timeout(300)
    check("TPL: delete goes back to the library", pg.locator("#library").is_visible() and pg.locator(".pkg:not(.pkg-new)").count() == 5)
    pg.locator("#toast button").click(); pg.wait_for_timeout(300)
    check("TPL: undo the delete", pg.locator("#brandSub").inner_text().strip() == "Uhle box covers")
    pg.click("#libBtn"); pg.wait_for_timeout(200)
    pg.locator(".pkg").filter(has_text="Stock Prep Cleaners").locator(".pkg-more").click(); menu_click(pg, "Delete package")
    pg.wait_for_timeout(300)
    pg.locator(".lib-link").filter(has_text="Restore").click(); pg.wait_for_timeout(300)
    check("TPL: restore a deleted example", pg.locator(".pkg").filter(has_text="Stock Prep Cleaners").count() == 1)
    check("TPL: no page errors", not pg.errors, "; ".join(pg.errors))
    ctx.close()

    # ───────── Consumables Tracker ─────────
    ctx, pg = open_page(br, "ConsumablesTracker.html")
    check("CT: opens on the demo board", notes(pg) >= 8, str(notes(pg)))
    card = pg.locator("#world > .note").filter(has_text="Dryer rope").first
    before = card.locator(".qn").first.inner_text()
    card.locator(".qb").nth(1).click(); pg.wait_for_timeout(200)
    after = pg.locator("#world > .note").filter(has_text="Dryer rope").first.locator(".qn").first.inner_text()
    check("CT: + adds one on hand", int(after) == int(before) + 1, f"{before} → {after}")
    pg.click("#newBtn"); pg.wait_for_timeout(200)
    check("CT: New opens the card type menu", "Doctor blade" in menu_text(pg) and "Blank info card" in menu_text(pg))
    menu_click(pg, "Doctor blade"); pg.wait_for_timeout(300)
    check("CT: a doctor blade card opens with its fields", pg.locator("#modal").is_visible() and pg.locator("#edCons input").count() >= 7)
    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    check("CT: the new card is on the board", pg.locator("#world > .note").filter(has_text="Doctor blade").count() >= 1)
    b = pg.locator("#world > .note").first.bounding_box()
    pg.mouse.click(b["x"] + 40, b["y"] + 12, button="right"); pg.wait_for_timeout(200)
    check("CT: card menu has no status row", "In progress" not in menu_text(pg))
    pg.keyboard.press("Escape")
    pg.keyboard.press("/"); pg.keyboard.type("RP-58B"); pg.wait_for_timeout(300)
    check("CT: search finds text inside inventory rows", pg.locator("#world > .note.dim").count() >= 1 or pg.locator("#world > .note.hit").count() >= 1)
    pg.keyboard.press("Escape"); pg.keyboard.press("Escape")
    pg.click("#libBtn"); pg.wait_for_timeout(300)
    check("CT: library card counts inventory", "inventory" in pg.locator(".pkg:not(.pkg-new)").first.inner_text())
    check("CT: no page errors", not pg.errors, "; ".join(pg.errors))
    ctx.close()
    br.close()

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
sys.exit(1 if failures else 0)
