"""Screenshot the board tools in a fixed set of states (demo mode), for before/after comparison.

    python3 tests/browser/visual.py http://localhost:8765/ out_dir
"""
import sys, os, json
from playwright.sync_api import sync_playwright

BASE, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
FREEZE = "Date.now = () => 1794096000000; const _D = Date; window.Date = class extends _D { constructor(...a){ super(...(a.length ? a : [1794096000000])); } static now(){ return 1794096000000; } };"
STATES = {
    "Whiteboard.html": [
        ("main", []),
        ("template", [("click", "#tabs > .ib >> nth=-1"), ("menu", "Outage plan template"), ("wait", 600)]),
        ("editor", [("click", "#tabs > .ib >> nth=-1"), ("menu", "Outage plan template"), ("wait", 600), ("dbl-note", 0)]),
        ("help", [("key", "?")]),
    ],
    "TaskPackageLibrary.html": [
        ("library", []), ("board", [("text", "BP Wire Change"), ("wait", 600)]),
        ("editor", [("text", "BP Wire Change"), ("wait", 600), ("dbl-note", 0)]),
        ("help", [("text", "BP Wire Change"), ("wait", 400), ("key", "?")]), ("info", [("text", "BP Wire Change"), ("wait", 400), ("click", "#infoBtn")]),
    ],
    "ConsumablesTracker.html": [
        ("main", []), ("library", [("click", "#libBtn")]), ("editor", [("dbl-note", 0)]), ("help", [("key", "?")]), ("info", [("click", "#infoBtn")]),
        ("typemenu", [("click", "#newBtn")]),
    ],
}
errors = {}
with sync_playwright() as p:
    br = p.chromium.launch(channel="chrome", headless=True)
    for page_name, states in STATES.items():
        for state, steps in states:
            ctx = br.new_context(viewport={"width": 1400, "height": 860}, device_scale_factor=1)
            ctx.add_init_script(FREEZE + "Math.random = (() => { let s = 42; return () => (s = (s * 16807) % 2147483647) / 2147483647; })();")
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
            pg.goto(BASE + page_name, wait_until="networkidle"); pg.wait_for_timeout(900)
            if pg.locator("#tipsOk").is_visible(): pg.click("#tipsOk")
            for kind, arg in steps:
                if kind == "click": pg.locator(arg).first.click()
                elif kind == "menu": pg.locator("#menu .mi").filter(has_text=arg).first.click()
                elif kind == "key": pg.keyboard.press(arg)
                elif kind == "text": pg.get_by_text(arg, exact=True).first.click()
                elif kind == "wait": pg.wait_for_timeout(arg)
                elif kind == "dbl-note":
                    n = pg.locator("#world > .note").nth(arg); n.wait_for(timeout=3000)
                    b = n.bounding_box(); pg.mouse.dblclick(b["x"] + 30, b["y"] + 20)
                pg.wait_for_timeout(350)
            pg.wait_for_timeout(500)
            pg.screenshot(path=f"{OUT}/{page_name[:-5]}-{state}.png")
            if errs: errors[f"{page_name}:{state}"] = errs
            ctx.close()
    br.close()
json.dump(errors, open(f"{OUT}/errors.json", "w"), indent=1)
print("errors:", json.dumps(errors, indent=1) if errors else "none")
