"""Consumables Tracker as an organizer: category sections, cards sorted by name, no canvas.
Cards work as before (counts, editor), and the menu does what dragging used to (move, tuck).

    python3 tests/browser/consumables_organizer.py http://localhost:8000/
"""
import sys, os
from playwright.sync_api import sync_playwright

BASE = sys.argv[1]
URL = BASE + "ConsumablesTracker.html"
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok: failures.append(name)

def titles(pg, sec):
    return pg.locator(f".org-sec:has(.ft:text-is('{sec}')) .org-grid > .note .title").all_text_contents()

with sync_playwright() as p:
    br = p.chromium.launch(channel=os.environ.get("PW_CHANNEL") or None, headless=True)
    ctx = br.new_context(viewport={"width": 1400, "height": 900}); pg = ctx.new_page(); errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)[:200]))
    pg.goto(URL, wait_until="networkidle"); pg.wait_for_timeout(1200)
    if pg.locator("#tipsOk").is_visible(): pg.click("#tipsOk")

    secs = pg.locator(".org-sec .ft").all_text_contents()
    check("category sections in board order", secs[:3] == ["Refiner plates", "Doctor blades", "Shower nozzles"], str(secs))
    check("no library, zoom or arrows", not pg.locator("#library").is_visible() and not pg.locator("#zoombar").is_visible() and not pg.locator("#libBtn").is_visible())
    t = titles(pg, "Doctor blades")
    check("cards sorted by name", t == sorted(t, key=str.lower), str(t))
    pos = pg.evaluate("[...document.querySelectorAll('.org-grid > .note')].map(n => getComputedStyle(n).position)")
    check("cards are in the page flow", set(pos) == {"relative"}, str(set(pos)))

    q = pg.locator(".org-grid .qn").first; before = int(q.text_content())
    pg.locator(".org-grid .qb[data-d='1']").first.click(); pg.wait_for_timeout(200)
    check("+ adds one on hand", int(pg.locator(".org-grid .qn").first.text_content()) == before + 1)

    pg.locator(".org-sec:has(.ft:text-is('Doctor blades')) .org-grid > .note").first.click(); pg.wait_for_timeout(600)
    check("clicking a card opens its editor", pg.locator("#edCons").is_visible())
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300)

    # Move to another category through the menu
    card = pg.locator(".org-sec:has(.ft:text-is('Doctor blades')) .org-grid > .note").first
    name = card.locator(".title").text_content()
    card.click(button="right"); pg.wait_for_timeout(200)
    pg.locator("#menu .mi", has_text="Shower nozzles").first.click(); pg.wait_for_timeout(400)
    check("Move to puts the card in the other category", name in titles(pg, "Shower nozzles") and name not in titles(pg, "Doctor blades"))
    check("…and keeps it sorted", titles(pg, "Shower nozzles") == sorted(titles(pg, "Shower nozzles"), key=str.lower))

    # Tuck under another card in the same category
    sn = pg.locator(".org-sec:has(.ft:text-is('Shower nozzles')) .org-grid > .note")
    n0 = sn.count()
    sn.nth(1).click(button="right"); pg.wait_for_timeout(200)
    pg.locator("#menu .mi").filter(has_text=titles(pg, "Shower nozzles")[0]).last.click(); pg.wait_for_timeout(500)
    check("Tuck under makes it a sub-card", sn.count() == n0 - 1 and pg.locator(".org-sec:has(.ft:text-is('Shower nozzles')) .mini").count() >= 1)

    pg.keyboard.press("Control+z"); pg.wait_for_timeout(300)
    check("undo works", sn.count() == n0)

    # New card from a category's +
    pg.locator(".org-sec:has(.ft:text-is('Deckle strips')) .org-h .ib").first.click(); pg.wait_for_timeout(200)
    pg.locator("#menu .mi", has_text="Blank info card").click(); pg.wait_for_timeout(400)
    pg.locator("#edText").fill("AAA test strip"); pg.keyboard.press("Escape"); pg.wait_for_timeout(400)
    check("+ on a category adds the card there", "AAA test strip" in titles(pg, "Deckle strips"))

    # New category
    pg.locator("#frameBtn").click(); pg.wait_for_timeout(300)
    pg.keyboard.type("Felts"); pg.keyboard.press("Enter"); pg.wait_for_timeout(300)
    check("Category adds a section at the end", pg.locator(".org-sec .ft").all_text_contents()[-1] == "Felts")

    pg.wait_for_timeout(800)                 # saves are debounced
    pg.reload(wait_until="networkidle"); pg.wait_for_timeout(1200)
    check("changes survive a reload", "AAA test strip" in titles(pg, "Deckle strips") and "Felts" in pg.locator(".org-sec .ft").all_text_contents())

    pg.fill("#search", "RP-58"); pg.wait_for_timeout(300)
    check("search highlights matching cards", pg.locator(".org-grid > .note.hit").count() >= 1)
    check("no script errors", not errs, "; ".join(errs))
    ctx.close(); br.close()

if failures: print(f"\n{len(failures)} failed"); sys.exit(1)
print("\nall passed")
