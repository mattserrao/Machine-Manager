"""The tools signed in, against tests/browser/fake-supabase.js (no network).

Checks that the Whiteboard reads its stored records, saves through mm_apply with the
board tools' record ids, and that My Machine and Outage Planning load and save cleanly.

    python3 tests/browser/signed_in.py http://localhost:8000/
"""
import sys, os, json, re
from playwright.sync_api import sync_playwright

BASE = sys.argv[1]
FAKE = open(os.path.join(os.path.dirname(__file__), 'fake-supabase.js')).read()
failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


# Two Whiteboard boards as they're stored in mm_records.
WB_ROWS = [
    {"tool": "whiteboard", "id": "p:b-old", "data": {"name": "Outage plan", "meta": {}, "created": "2026-11-01T10:00:00Z", "sort": 1793527200000}},
    {"tool": "whiteboard", "id": "p:b-new", "data": {"name": "Test Board 1 (2)", "meta": {}, "created": "2026-11-05T10:00:00Z", "sort": 1793872800000}},
    {"tool": "whiteboard", "id": "n:b-old:n1", "data": {"text": "Shower nozzles\n- [ ] 2nd press", "x": 40, "y": 60, "z": 1, "color": "#fff4b8", "status": "planned", "attachments": [], "children": [], "parent": None}},
    {"tool": "whiteboard", "id": "n:b-old:n2", "data": {"text": "Felt run", "x": 340, "y": 60, "z": 2, "color": "#ffffff", "attachments": [], "children": [], "parent": None}},
    {"tool": "whiteboard", "id": "l:b-old:l1", "data": {"from": "n1", "to": "n2", "label": "then"}},
    {"tool": "whiteboard", "id": "f:b-old:f1", "data": {"title": "Wet end", "x": 0, "y": 0, "w": 640, "h": 300, "color": "#2563eb"}},
    {"tool": "whiteboard", "id": "n:b-new:m1", "data": {"text": "Hello", "x": 0, "y": 0, "z": 1, "color": "#ffffff", "attachments": [], "children": [], "parent": None}},
]
MM_ROWS = [
    {"tool": "mymachine", "id": "machine", "data": {"name": "PM1", "press": {"nips": 2, "tandem": True}, "dryers": [{"type": "uno"}, {"type": "double"}, {"type": "double"}],
                                                  "former": {"type": "twin", "lumpbreaker": True}, "calender": True,
                                                  "refiners": [{"id": "bp1", "name": "BP 1"}, {"id": "bp2", "name": "BP 2"}, {"id": "tp1", "name": "TP 1"}, {"id": "tp2", "name": "TP 2"}]}},
    {"tool": "mymachine", "id": "item:p1-felt-top", "data": {"note": "", "target": 6, "history": [], "installed": "2026-09-30", "targetUnit": "weeks"}},
    {"tool": "mymachine", "id": "item:form-top", "data": {"note": "", "target": 26, "history": [], "installed": "2026-11-07", "targetUnit": "weeks"}},
    {"tool": "outages", "id": "outage:o1", "data": {"date": "2026-11-11", "type": "normal"}},
    {"tool": "outages", "id": "settings", "data": {"anchor": "2026-11-11", "cadenceDays": 42, "setUp": True}},
]

with sync_playwright() as p:
    br = p.chromium.launch(channel=os.environ.get("PW_CHANNEL") or None, headless=True)

    def open_page(name, rows, org=None):
        ctx = br.new_context(viewport={"width": 1400, "height": 860})
        ctx.route(re.compile(r".*/vendor/supabase-[^/]*\.js(\?.*)?$"), lambda route: route.fulfill(content_type="application/javascript", body=FAKE))
        ctx.add_init_script(f"window.__seedRows = {json.dumps(rows)};" + (f"window.__orgId = {json.dumps(org[0])}; window.__orgName = {json.dumps(org[1])};" if org else ""))
        pg = ctx.new_page(); pg.errors = []
        pg.on("pageerror", lambda e: pg.errors.append(str(e)[:300]))
        pg.on("dialog", lambda d: d.dismiss())
        pg.goto(BASE + name, wait_until="networkidle"); pg.wait_for_timeout(1200)
        if pg.locator("#tipsOk").is_visible(): pg.click("#tipsOk")
        return ctx, pg

    # ───────── Whiteboard on mm_records ─────────
    ctx, pg = open_page("Whiteboard.html", WB_ROWS)
    tabs = pg.locator("#tabs .tab").all_inner_texts()
    check("WB: migrated boards load as tabs, oldest first", [t.strip().rstrip("✕").strip() for t in tabs] == ["Outage plan", "Test Board 1 (2)"], str(tabs))
    pg.locator("#tabs .tab").filter(has_text="Outage plan").click(); pg.wait_for_timeout(400)
    check("WB: notes, frame and arrow come through", pg.locator("#world > .note").count() == 2 and pg.locator("#world > .frame").count() == 1
          and pg.locator("#lg path.lk").count() == 1, f"{pg.locator('#world > .note').count()} notes")
    check("WB: no save on load (nothing changed)", pg.evaluate("window.__rpcLog.length") == 0, json.dumps(pg.evaluate("window.__rpcLog"))[:300])
    pg.locator("#world > .note .cb").first.click(); pg.wait_for_timeout(1200)
    log = pg.evaluate("window.__rpcLog")
    sent = [c for call in log for c in call["p_changes"]]
    check("WB: ticking a box saves just that note as n:<board>:<note>", log and log[-1]["p_tool"] == "whiteboard" and [c["id"] for c in sent] == ["n:b-old:n1"]
          and sent[0]["base"] == 1 and "[x]" in sent[0]["data"]["text"], json.dumps(sent)[:300])
    pg.locator("#tabs > .ib").last.click(); pg.locator("#menu .mi").filter(has_text="Blank").first.click(); pg.wait_for_timeout(1200)
    rows = pg.evaluate("window.__rows()")
    newb = [r for r in rows if r["id"].startswith("p:") and r["id"] not in ("p:b-old", "p:b-new")]
    check("WB: a new tab is saved as p:<board> with a sort key", len(newb) == 1 and newb[0]["data"].get("sort", 0) > 1793872800000, json.dumps(newb)[:200])
    pg.reload(wait_until="networkidle"); pg.wait_for_timeout(1200)
    check("WB: tab order survives a reload", [t.strip().rstrip("✕").strip() for t in pg.locator("#tabs .tab").all_inner_texts()][:2] == ["Outage plan", "Test Board 1 (2)"]
          and pg.locator("#tabs .tab").count() == 3)
    check("WB: no page errors", not pg.errors, "; ".join(pg.errors))
    ctx.close()

    # ───────── Ops Task Library and Consumables signed in ─────────
    for name, tool in [("TaskPackageLibrary.html", "task-packages"), ("ConsumablesTracker.html", "consumables")]:
        ctx, pg = open_page(name, [])
        pg.wait_for_timeout(800)
        rows = pg.evaluate("window.__rows()")
        mine = [r for r in rows if r["tool"] == tool]
        if tool == "task-packages":
            check("TPL: a real org starts empty (no example packages written)", not mine, json.dumps([r["id"] for r in mine])[:200])
            check("TPL: the examples can be added on request", pg.locator(".lib-link").filter(has_text="Add the example packages").count() == 1)
        else:
            check("CT: first editor gets one empty PM1 board with category frames", len([r for r in mine if r["id"].startswith("p:")]) == 1
                  and len([r for r in mine if r["id"].startswith("f:")]) == 6 and not any(r["id"].startswith("n:") for r in mine))
        check(f"{name}: no page errors", not pg.errors, "; ".join(pg.errors))
        ctx.close()

    # ───────── My Machine and Outage Planning ─────────
    ctx, pg = open_page("MyMachine.html", MM_ROWS)
    check("MM: loads the shared machine", pg.locator("#fabRows tr").count() >= 10, str(pg.locator("#fabRows tr").count()))
    check("MM: no save on load", pg.evaluate("window.__rpcLog.length") == 0, json.dumps(pg.evaluate("window.__rpcLog"))[:300])
    pg.locator("#fabRows tr[data-id='p1-felt-top']").click(); pg.wait_for_timeout(300)
    pg.locator("#drawer [data-act='cond'][data-c='worn']").click(); pg.wait_for_timeout(1200)
    sent = [c for call in pg.evaluate("window.__rpcLog") for c in call["p_changes"]]
    check("MM: flagging a felt saves only that position", [c["id"] for c in sent] == ["item:p1-felt-top"] and sent[0]["data"]["condition"] == "worn", json.dumps(sent)[:300])
    check("MM: no page errors", not pg.errors, "; ".join(pg.errors))
    ctx.close()

    ctx, pg = open_page("OperationsOutagePlanning.html", MM_ROWS)
    check("OOP: shows the outage", "Nov" in pg.locator("body").inner_text() and pg.locator("#gate").is_hidden() if pg.locator("#gate").count() else True)
    check("OOP: no save on load", pg.evaluate("window.__rpcLog.length") == 0, json.dumps(pg.evaluate("window.__rpcLog"))[:300])
    check("OOP: no page errors", not pg.errors, "; ".join(pg.errors))
    ctx.close()

    # ───────── Refiner plates: a plate change takes a set from the Consumables Tracker ─────────
    PL_ROWS = MM_ROWS + [
        {"tool": "mymachine", "id": "item:ref-bp1", "data": {"installed": "2026-08-20", "target": 12, "targetUnit": "weeks", "vendor": "Vendor A", "style": "LC pattern · RP-2210", "history": []}},
        {"tool": "mymachine", "id": "item:ref-bp2", "data": {"installed": "2026-08-01", "target": 12, "targetUnit": "weeks", "vendor": "Vendor A", "style": "LC pattern", "history": []}},
        {"tool": "outages", "id": "outage:o2", "data": {"date": "2027-01-06", "type": "normal"}},
        {"tool": "consumables", "id": "p:cs1", "data": {"name": "PM1 Consumables", "meta": {}, "created": "2026-11-01T10:00:00Z"}},
        {"tool": "consumables", "id": "n:cs1:c1", "data": {"text": "Refiner plates", "x": 0, "y": 0, "z": 1, "color": "#e9e0ff", "w": 268, "attachments": [], "children": [], "parent": None,
            "cons": {"type": "plates", "kind": "inv", "unit": "sets", "cols": ["Manufacturer", "Pattern / part #"], "fits": {"mode": "all", "list": ""},
                     "rows": [{"id": "r1", "a": "Vendor A", "b": "LC pattern", "c": "RP-2210", "q": 1}, {"id": "r2", "a": "Vendor B", "b": "HC pattern", "q": 0}]}}},
    ]
    def sent_of(pg, tool=None):
        return [c for call in pg.evaluate("window.__rpcLog") for c in call["p_changes"] if tool is None or call.get("p_tool") == tool]
    ctx, pg = open_page("MyMachine.html", PL_ROWS)
    pg.locator("#refRows tr[data-id='ref-bp1']").click(); pg.wait_for_timeout(300)
    pg.locator("#drawer [data-act='replace']").click(); pg.wait_for_timeout(300)
    opts = pg.locator("#chPlate option").all_inner_texts()
    check("MM plates: plate change lists the plate types with sets on hand", len(opts) == 3 and "Vendor A — LC pattern · RP-2210 (1 on hand)" in opts[1], str(opts))
    check("MM plates: the plates in now are picked, Vendor and Style filled and locked",
          pg.input_value("#chPlate") == "cs1:c1:r1" and pg.input_value("#chVendor") == "Vendor A" and pg.locator("#chStyle").get_attribute("readonly") is not None)
    pg.locator("#drawer [data-act='chsave']").click(); pg.wait_for_timeout(1500)
    cs = [c for c in sent_of(pg) if c["id"] == "n:cs1:c1"]; it = [c for c in sent_of(pg) if c["id"] == "item:ref-bp1"]
    check("MM plates: logging it takes one set", cs and cs[-1]["data"]["cons"]["rows"][0]["q"] == 0 and cs[-1]["data"]["cons"]["rows"][1]["q"] == 0, json.dumps(cs)[:300])
    check("MM plates: the run records the plates taken", it and it[-1]["data"].get("plate", {}).get("key") == "cs1:c1:r1", json.dumps(it)[-300:])
    pg.locator("#toast button", has_text="Undo").click(); pg.wait_for_timeout(1500)
    cs = [c for c in sent_of(pg) if c["id"] == "n:cs1:c1"]
    check("MM plates: undo gives the set back", cs[-1]["data"]["cons"]["rows"][0]["q"] == 1, json.dumps(cs[-1])[:200])
    # Not from inventory: nothing taken
    pg.locator("#drawer [data-act='replace']").click(); pg.wait_for_timeout(300)
    pg.select_option("#chPlate", ""); pg.fill("#chVendor", "Other Co"); n0 = len(sent_of(pg))
    pg.locator("#drawer [data-act='chsave']").click(); pg.wait_for_timeout(1500)
    check("MM plates: Not from inventory takes nothing", not [c for c in sent_of(pg)[n0:] if c["id"].startswith("n:")] and not [c for c in sent_of(pg)[n0:] if c["id"] == "item:ref-bp1"][-1]["data"].get("plate"))
    check("MM plates: no page errors", not pg.errors, "; ".join(pg.errors))
    ctx.close()

    ctx, pg = open_page("OperationsOutagePlanning.html", PL_ROWS)
    pg.locator(".lane > .card").first.click(); pg.wait_for_timeout(500)
    row = pg.locator(".card.big .due").filter(has_text="BP 2 refiner")
    check("OOP plates: refiner row shows sets on hand", row.count() == 1 and "1 set on hand" in row.inner_text(), row.inner_text() if row.count() else "")
    row.locator("button", has_text="Changed").first.click(); pg.wait_for_timeout(300)
    items = pg.locator("#picker button").all_inner_texts()
    check("OOP plates: Changed asks which plates went in", len(items) == 3 and "Not from inventory" in items[-1], str(items))
    pg.locator("#picker button", has_text="Vendor B").click(); pg.wait_for_timeout(1500)
    cs = [c for c in sent_of(pg) if c["id"] == "n:cs1:c1"]; it = [c for c in sent_of(pg) if c["id"] == "item:ref-bp2"]
    check("OOP plates: picking plates takes a set (none on hand: goes negative)", cs and cs[-1]["data"]["cons"]["rows"][1]["q"] == -1, json.dumps(cs)[:300])
    check("OOP plates: the new run records the plates", it and it[-1]["data"]["plate"]["key"] == "cs1:c1:r2" and it[-1]["data"]["vendor"] == "Vendor B", json.dumps(it)[-300:])
    check("OOP plates: no page errors", not pg.errors, "; ".join(pg.errors))
    ctx.close()

    ctx, pg = open_page("ConsumablesTracker.html", PL_ROWS)
    pg.wait_for_timeout(500)
    if pg.locator(".pkg").filter(has_text="PM1 Consumables").count(): pg.locator(".pkg").filter(has_text="PM1 Consumables").first.click(); pg.wait_for_timeout(600)
    txt = pg.locator("body").inner_text()
    check("CT plates: old two-column plate card shows vendor, model and part #", "Vendor A" in txt and "LC pattern · Part # RP-2210" in txt, txt[:300].replace("\n", " | "))
    check("CT plates: no page errors", not pg.errors, "; ".join(pg.errors))
    ctx.close()
    # ───────── Mill data pages for a real org with no data of its own: placeholders, never the demo org ─────────
    for name in ["DailyJournal.html", "Downtime.html", "VendorReports.html", "BonvoyReport.html", "MMLLM.html"]:
        ctx, pg = open_page(name, [])
        pg.wait_for_timeout(600)
        calls = pg.evaluate("window.__llmCalls || []")
        demo = [c for c in calls if c["args"].get("p_org") == "org-sim"]
        text = pg.locator("main").inner_text()
        ph = pg.locator(".ph").count() == 1
        check(f"{name}: PM1 sees a placeholder", ph and "Sim Mill" not in text, text[:160].replace("\n", " "))
        check(f"{name}: no demo-org data is requested", not demo, json.dumps(demo)[:200])
        check(f"{name}: no page errors", not pg.errors, "; ".join(pg.errors))
        ctx.close()
    # ───────── The demo account (a viewer of Sim Mill): still sees the demo data, and can pick Sonnet or Opus ─────────
    ctx, pg = open_page("MMLLM.html", [], org=("org-sim", "Sim Mill"))
    pg.wait_for_timeout(600)
    calls = pg.evaluate("window.__llmCalls || []")
    check("Demo account: MM LLM loads Sim Mill, no placeholder", pg.locator(".ph").count() == 0 and any(c["args"].get("p_org") == "org-sim" for c in calls))
    picks = pg.locator(".mpick button").all_inner_texts()
    check("Demo account: model picker offers Sonnet and Opus", picks == ["Sonnet", "Opus"], str(picks))
    pg.locator(".mpick button").filter(has_text="Opus").click()
    check("Demo account: the choice sticks", pg.evaluate("localStorage.getItem('mm-llm-model')") == "opus"
          and pg.locator(".mpick button[aria-checked='true']").inner_text() == "Opus")
    check("Examples start collapsed", not pg.evaluate("document.getElementById('examples').open"))
    pg.fill("#askQ", "What actions are overdue?"); pg.locator(".ask .btn.primary").click(); pg.wait_for_timeout(800)
    live = pg.locator("#liveAns")
    check("Live answer shows under the Ask box with the examples still collapsed", live.is_visible() and "Six actions are overdue" in live.inner_text()
          and live.locator(".mchart").count() == 1 and not pg.evaluate("document.getElementById('examples').open"), live.inner_text()[:120])
    check("Live answer sits between the Ask box and the examples", pg.evaluate(
          "(() => { const a = document.querySelector('.ask'), l = document.getElementById('liveAns'), e = document.getElementById('examples');"
          " return !!(a.compareDocumentPosition(l) & 4) && !!(l.compareDocumentPosition(e) & 4); })()"))
    check("The question went to Opus", pg.evaluate("window.__invokes[0].body.model") == "opus")
    ctx.close()
    ctx, pg = open_page("DailyJournal.html", [], org=("org-sim", "Sim Mill"))
    calls = pg.evaluate("window.__llmCalls || []")
    check("Demo account: the Daily Journal asks for Sim Mill's data, no placeholder", pg.locator(".ph").count() == 0 and any(c["args"].get("p_org") == "org-sim" for c in calls))
    ctx.close()
    ctx, pg = open_page("MMLLM.html", [])
    check("PM1: no model picker (no live asking)", pg.locator(".mpick").count() == 0)
    ctx.close()
    br.close()

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
sys.exit(1 if failures else 0)
