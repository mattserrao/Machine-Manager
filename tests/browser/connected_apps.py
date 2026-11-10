"""ConnectedApps.html, the OAuth consent page for MCP apps, against tests/browser/fake-supabase.js (no network).

Signed out it asks to sign in; signed in it shows the app, the account and what the app can read, and Approve / Deny
call Supabase's OAuth server and return to the app; an already-approved request goes straight back; connected apps
are listed with Disconnect; the menu links here.

    python3 tests/browser/connected_apps.py http://localhost:8000/
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


DETAILS = {"authorization_id": "auth-1", "redirect_uri": "https://claude.ai/api/mcp/auth_callback", "scope": "email",
           "client": {"client_id": "cl-1", "name": "Claude", "client_uri": "https://claude.ai"}}
GRANTS = [{"client": {"client_id": "cl-1", "name": "Claude"}, "scopes": ["email"], "granted_at": "2026-11-10T11:00:00Z"}]

with sync_playwright() as p:
    browser = p.chromium.launch()

    def open_page(query="", oauth=None, signed_out=False, width=1280):
        ctx = browser.new_context(viewport={"width": width, "height": 900})
        ctx.route(re.compile(r".*/vendor/supabase-[^/]*\.js(\?.*)?$"), lambda route: route.fulfill(content_type="application/javascript", body=FAKE))
        ctx.add_init_script(f"window.__oauth = {json.dumps(oauth or {})};" + ("window.__signedOut = true;" if signed_out else ""))
        pg = ctx.new_page(); errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(BASE + "ConnectedApps.html" + query); pg.wait_for_timeout(600)
        return ctx, pg, errs

    # Signed out, with a request: sign in first, nothing shared yet.
    ctx, pg, errs = open_page("?authorization_id=auth-1", {"details": DETAILS}, signed_out=True)
    ask = pg.locator("#ask")
    check("signed out: asks to sign in", ask.is_visible() and "Sign in" in ask.inner_text() and pg.locator("[data-signin]").count() == 1)
    check("signed out: nothing was asked of the OAuth server", pg.evaluate("(window.__oauthLog || []).length") == 0)
    check("the connector address is shown", pg.locator("#me").inner_text().endswith("/functions/v1/mm-mcp/me"))
    check("no page errors (signed out)", not errs, "; ".join(errs))
    ctx.close()

    # Signed in: the request, the account and what it can read.
    ctx, pg, errs = open_page("?authorization_id=auth-1", {"details": DETAILS, "grants": []})
    text = pg.locator("#ask").inner_text()
    check("shows the app", "Connect Claude?" in text and "claude.ai" in text, text[:200])
    check("shows the signed-in account", "matt@example.com" in text)
    check("lists what it can read: own orgs and the public demo", "PM1" in text and "Sim Mill" in text and "public demo" in text)
    check("says it's read-only", "can’t change, upload or delete" in text)
    pg.locator("#ok").click(); pg.wait_for_timeout(500)
    check("Approve returns to the app with the code", pg.url.startswith("about:blank") and "code=abc" in pg.url, pg.url)
    ctx.close()

    ctx, pg, errs = open_page("?authorization_id=auth-1", {"details": DETAILS})
    pg.locator("#no").click(); pg.wait_for_timeout(500)
    check("Deny returns to the app with access_denied", "error=access_denied" in pg.url, pg.url)
    ctx.close()

    # Approve calls the server with the request id and handles the redirect itself.
    ctx, pg, errs = open_page("?authorization_id=auth-1", {"details": DETAILS, "approveTo": BASE + "favicon.svg#code=abc"})
    pg.locator("#ok").click(); pg.wait_for_timeout(500)
    log = json.loads(pg.evaluate("sessionStorage.getItem('__oauthLog')") or "[]")
    check("Approve: one approve call for this request, no automatic redirect", [e for e in log if e["op"] == "approve"] == [{"op": "approve", "id": "auth-1", "opt": {"skipBrowserRedirect": True}}], json.dumps(log))
    check("Approve: the page sends the user back", pg.url.endswith("favicon.svg#code=abc"), pg.url)
    check("no page errors (consent)", not errs, "; ".join(errs))
    ctx.close()

    # Approved before: straight back without asking.
    ctx, pg, errs = open_page("?authorization_id=auth-2", {"details": {"redirect_url": "about:blank#code=again"}})
    check("an already-approved request goes straight back", "code=again" in pg.url, pg.url)
    ctx.close()

    # A bad request id.
    ctx, pg, errs = open_page("?authorization_id=nope", {})
    check("an unknown request says so", "can’t be used" in pg.locator("#ask").inner_text())
    ctx.close()

    # No request: the connected apps, with Disconnect (two clicks).
    ctx, pg, errs = open_page("", {"grants": GRANTS})
    check("no request: the consent panel stays hidden", not pg.locator("#ask").is_visible())
    check("lists the connected app", "Claude" in pg.locator("#apps").inner_text())
    b = pg.locator("[data-rm]")
    b.click(); pg.wait_for_timeout(100)
    check("Disconnect asks to confirm first", b.inner_text() == "Confirm" and not any(e["op"] == "revoke" for e in pg.evaluate("window.__oauthLog || []")))
    b.click(); pg.wait_for_timeout(300)
    check("Disconnect revokes that app", {"op": "revoke", "clientId": "cl-1"} in pg.evaluate("window.__oauthLog") and "No apps are connected" in pg.locator("#apps").inner_text())
    check("no page errors (list)", not errs, "; ".join(errs))
    ctx.close()

    # Phone width, and the menu link from another page.
    ctx, pg, errs = open_page("?authorization_id=auth-1", {"details": DETAILS}, width=390)
    over = pg.evaluate("document.documentElement.scrollWidth > window.innerWidth + 1")
    check("phone: no sideways scrolling", not over)
    ctx.close()
    ctx = browser.new_context(); ctx.route(re.compile(r".*/vendor/supabase-[^/]*\.js(\?.*)?$"), lambda route: route.fulfill(content_type="application/javascript", body=FAKE))
    pg = ctx.new_page(); pg.goto(BASE + "MyMachine.html"); pg.wait_for_timeout(500)
    pg.locator(".mmnav").first.click(); pg.wait_for_timeout(200)
    check("the menu links to Connected apps", pg.locator('#mmnavMenu a[href="ConnectedApps.html"]').count() == 1)
    ctx.close()
    browser.close()

print(f"\n{len(failures)} FAILED" if failures else "\nall passed")
sys.exit(1 if failures else 0)
