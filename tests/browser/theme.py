"""Appearance setting (bottom of the app menu): System / Light / Dark, remembered in this browser when signed
out and saved on the account when signed in.

    python3 tests/browser/theme.py http://localhost:8000/
"""
import os, re, sys
from playwright.sync_api import sync_playwright
B=sys.argv[1]
FAKE=open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fake-supabase.js')).read()
ok=True
def check(n,c):
    global ok; print(('PASS ' if c else 'FAIL ')+n); ok = ok and c
with sync_playwright() as p:
    br=p.chromium.launch(channel=os.environ.get("PW_CHANNEL") or None, headless=True)
    # signed out: default system follows the OS; picking one sticks in this browser
    ctx=br.new_context(color_scheme='light'); pg=ctx.new_page(); pg.goto(B+'MyMachine.html', wait_until='networkidle')
    check('system follows OS light', pg.evaluate("document.documentElement.dataset.theme")=='light')
    pg.click('button.mmnav'); pg.click('.mmnav-seg button[data-theme=dark]')
    check('dark applied', pg.evaluate("document.documentElement.dataset.theme")=='dark')
    check('menu radio checked', pg.get_attribute('.mmnav-seg button[data-theme=dark]','aria-checked')=='true')
    check('bg is warm charcoal', pg.evaluate("getComputedStyle(document.body).backgroundColor")=='rgb(38, 38, 36)')
    pg.goto(B+'index.html', wait_until='networkidle')
    check('remembered across pages', pg.evaluate("document.documentElement.dataset.theme")=='dark')
    ctx.close()
    # signed in: the account's saved choice wins, and changes are saved to the account
    ctx=br.new_context(color_scheme='dark')
    ctx.route(re.compile(r".*/vendor/supabase-[^/]*\.js(\?.*)?$"), lambda r: r.fulfill(content_type="application/javascript", body=FAKE))
    ctx.add_init_script("window.__seedRows = []; window.__userMeta = { mm_theme: 'light' };")
    pg=ctx.new_page(); pg.goto(B+'index.html', wait_until='networkidle'); pg.wait_for_timeout(500)
    check('account choice applied', pg.evaluate("document.documentElement.dataset.theme")=='light')
    pg.click('button.mmnav'); pg.click('.mmnav-seg button[data-theme=system]'); pg.wait_for_timeout(300)
    check('saved to account', pg.evaluate("window.__metaSaved && window.__metaSaved.mm_theme")=='system')
    check('system -> OS dark', pg.evaluate("document.documentElement.dataset.theme")=='dark')
    ctx.close(); br.close()
sys.exit(0 if ok else 1)
