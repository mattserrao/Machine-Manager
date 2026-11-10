"""The RAG page against tests/browser/fake-supabase.js (no network): uploads into a private org, the library list,
review by an editor, read-only public libraries, and that document text from the server can't run script.

    python3 tests/browser/rag.py http://localhost:8000/
"""
import sys, os, re, json
from playwright.sync_api import sync_playwright

BASE = sys.argv[1]
FAKE = open(os.path.join(os.path.dirname(__file__), 'fake-supabase.js')).read()
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok: failures.append(name)

LIB, SIM = "11111111-2222-4333-8444-555555555555", "org-sim"
DOCS = [
    {"doc_id": "d-review", "title": "Keel route <img src=x onerror=\"window.__xss=1\">", "kind": "vendor_report", "vendor": "Keel", "doc_date": "2026-10-19",
     "pages": 7, "source": "upload", "status": "needs_review", "quality_score": 68, "issues": ["no date found"], "file_name": "route.pdf",
     "file_path": f"{LIB}/rag/inbox/d-review.pdf", "imported_at": "2026-11-09T20:00:00Z"},
    {"doc_id": "d-ok", "title": "Felt survey", "kind": "vendor_report", "vendor": "Halden", "doc_date": "2026-09-30", "pages": 4,
     "source": "upload", "status": "indexed", "quality_score": 92, "issues": [], "file_name": "survey.pdf", "file_path": f"{LIB}/rag/inbox/d-ok.pdf",
     "imported_at": "2026-11-08T20:00:00Z"},
]
HOOK = """
window.__rpcHook = (name, a) => {
  const LIB = %s, DOCS = %s, ROLE = %s;
  if (name === 'mm_my_orgs') return { data: [{ id: 'org-sim', name: 'Sim Mill', role: 'viewer', is_public: true }, { id: LIB, name: 'Demodemo RAG', role: ROLE, is_public: false }], error: null };
  if (name === 'mm_rag_library') return { data: a.p_org === LIB ? DOCS : [{ doc_id: 'KV-1', title: 'Sim route', kind: 'vendor_report', status: 'indexed', quality_score: null, source: 'generator', file_path: 'docs/kv1.pdf', imported_at: '2026-11-01T00:00:00Z' }], error: null };
  if (name === 'mm_rag_status') return { data: a.p_org === LIB ? [{ status: 'indexed', docs: 1 }, { status: 'needs_review', docs: 1 }] : [{ status: 'indexed', docs: 1 }], error: null };
  if (name === 'mm_rag_register') return { data: { doc_id: 'new', status: 'uploaded', duplicate: a.p_sha256 === window.__dupSha }, error: null };
  if (name === 'mm_rag_review') return { data: 'accepted', error: null };
  if (name === 'mm_rag_document') { const d = DOCS.find(x => x.doc_id === a.p_doc) || {}; return { data: { document: { ...d, summary: 'Can 27 DS rising <b onmouseover=x>.',
      quality: { reasons: [], review: ['no date found'], signals: { pages: 7, model_pages: 2, avg_chars: 1500, avg_garble: 0.01 } } },
      events: [{ at: '2026-11-09T20:00:00Z', to: 'uploaded', detail: {} }, { at: '2026-11-09T20:01:00Z', to: 'needs_review', detail: {} }], chunks: 0 }, error: null }; }
  return undefined;
};"""

PDF = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R 4 0 R]/Count 2>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R>>endobj\n4 0 obj<</Type/Page/Parent 2 0 R>>endobj\ntrailer<</Root 1 0 R>>\n%%EOF\n"

with sync_playwright() as p:
    br = p.chromium.launch(channel=os.environ.get("PW_CHANNEL") or None, headless=True)

    def open_rag(role="editor", url="RAG.html"):
        ctx = br.new_context(viewport={"width": 1300, "height": 900})
        ctx.route(re.compile(r".*/vendor/supabase-[^/]*\.js(\?.*)?$"), lambda route: route.fulfill(content_type="application/javascript", body=FAKE))
        ctx.add_init_script("window.__seedRows = []; window.__orgId = 'org-sim'; window.__orgName = 'Sim Mill';" + HOOK % (json.dumps(LIB), json.dumps(DOCS), json.dumps(role)))
        pg = ctx.new_page(); pg.errors = []
        pg.on("pageerror", lambda e: pg.errors.append(str(e)[:300]))
        pg.goto(BASE + url, wait_until="networkidle"); pg.wait_for_timeout(900)
        return ctx, pg

    ctx, pg = open_rag()
    check("RAG: opens on the user's private org, not the public demo", pg.locator("#org select").input_value() == LIB)
    check("RAG: drop zone is on for a private org", pg.locator("#pick").is_enabled() and "Demodemo RAG" in pg.locator("#dropT").inner_text())
    check("RAG: library rows and status counts", pg.locator("tr.doc").count() == 2 and "Needs review 1" in pg.locator("#counts").inner_text())
    check("RAG: quality score is coloured by band", pg.locator("tr.doc .q.mid").count() == 1 and pg.locator("tr.doc .q.hi").count() == 1)
    check("RAG: a document title can't run script", pg.evaluate("window.__xss") is None and pg.locator("tr.doc img").count() == 0)

    pg.set_input_files("#file", files=[{"name": "Nozzle audit.pdf", "mimeType": "application/pdf", "buffer": PDF},
                                       {"name": "notes.pdf", "mimeType": "application/pdf", "buffer": b"MZ not a pdf"}])
    pg.wait_for_timeout(1200)
    st = pg.evaluate("window.__storage || []")
    reg = [c for c in pg.evaluate("window.__llmCalls") if c["name"] == "mm_rag_register"]
    up = [s for s in st if s["op"] == "upload"]
    check("RAG: a PDF is uploaded to <org>/rag/inbox/<uuid>.pdf", len(up) == 1 and re.fullmatch(LIB + r"/rag/inbox/[0-9a-f-]{36}\.pdf", up[0]["path"]) is not None, json.dumps(st)[:300])
    check("RAG: registered with a SHA-256, the real size and the page count", len(reg) == 1 and re.fullmatch(r"[0-9a-f]{64}", reg[0]["args"]["p_sha256"]) is not None
          and reg[0]["args"]["p_size"] == len(PDF) and reg[0]["args"]["p_pages"] == 2 and reg[0]["args"]["p_path"] == up[0]["path"], json.dumps(reg)[:300])
    check("RAG: a file that isn't a PDF is refused before upload", "not a PDF" in pg.locator("#ups").inner_text())
    check("RAG: the worker is nudged after upload", any(i["name"] == "mm-rag-process" for i in pg.evaluate("window.__invokes || []")))

    pg.locator("tr.doc", has_text="Keel route").click(); pg.wait_for_timeout(600)
    det = pg.locator("tr.det")
    check("RAG: details show summary, review reasons and history", det.count() == 1 and "Can 27 DS rising" in det.inner_text() and "no date found" in det.inner_text()
          and "Needs review" in det.inner_text() and pg.locator("tr.det b").count() == 0)
    det.locator("[data-f=doc_date]").fill("2026-10-19"); det.locator("[data-f=note]").fill("date from the cover")
    det.locator("button[data-a=accept]").click(); pg.wait_for_timeout(600)
    rv = [c for c in pg.evaluate("window.__llmCalls") if c["name"] == "mm_rag_review"]
    check("RAG: an editor accepts with corrected details", rv and rv[0]["args"]["p_action"] == "accept" and rv[0]["args"]["p_meta"]["doc_date"] == "2026-10-19"
          and rv[0]["args"]["p_note"] == "date from the cover" and rv[0]["args"]["p_doc"] == "d-review", json.dumps(rv)[:300])
    check("RAG: no script errors", not pg.errors, "; ".join(pg.errors))
    ctx.close()

    ctx, pg = open_rag(role="viewer")
    pg.locator("tr.doc", has_text="Keel route").click(); pg.wait_for_timeout(600)
    check("RAG: a viewer can upload but not review", pg.locator("#pick").is_enabled() and pg.locator("tr.det button[data-a]").count() == 0
          and "An editor" in pg.locator("tr.det").inner_text())
    ctx.close()

    ctx, pg = open_rag(url="RAG.html?org=Sim%20Mill")
    check("RAG: a public demo library is read-only", not pg.locator("#pick").is_enabled() and "public demo library" in pg.locator("#types").inner_text()
          and pg.locator("tr.doc").count() == 1)
    check("RAG: no script errors (public)", not pg.errors, "; ".join(pg.errors))
    ctx.close()
    br.close()

print(f"\n{len(failures)} failed" if failures else "\nall passed")
sys.exit(1 if failures else 0)
