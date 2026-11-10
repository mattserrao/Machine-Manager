"""Tests for supabase/migrations/10-rag.sql: drop-in documents, the lifecycle, review and search.

    PGDSN="host=localhost dbname=mm_test user=postgres password=pg" python3 tests/db/test_rag.py
(load tests/db/supabase-shim.sql, supabase/schema.sql and supabase/llm.sql first; llm.sql includes step 10)
"""
import json, os, sys, uuid
import psycopg

DSN = os.environ.get("PGDSN", "host=localhost dbname=mm_test user=postgres password=pg")
failures = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok: failures.append(name)
def raises(fn):
    try: fn(); return None
    except Exception as e: return e
def conn(uid=None, role=None):
    c = psycopg.connect(DSN, autocommit=True)
    c.execute("select set_config('request.jwt.sub', %s, false)", (str(uid) if uid else "",))
    c.execute(f"set role {role or ('authenticated' if uid else 'anon')}")
    return c

admin = psycopg.connect(DSN, autocommit=True)
priv, pub = f"RAG-{uuid.uuid4().hex[:6]}", f"RAG-PUB-{uuid.uuid4().hex[:6]}"
admin.execute("insert into orgs (name) values (%s), (%s)", (priv, pub))
P = admin.execute("select id from orgs where name = %s", (priv,)).fetchone()[0]
Q = admin.execute("select id from orgs where name = %s", (pub,)).fetchone()[0]
admin.execute("select public.mm_llm_set_public(%s, true)", (pub,))
viewer, editor, outsider = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
admin.execute("insert into auth.users (id, email) values (%s, %s), (%s, %s), (%s, %s)",
              (viewer, f"v{viewer.hex[:6]}@t", editor, f"e{editor.hex[:6]}@t", outsider, f"o{outsider.hex[:6]}@t"))
admin.execute("insert into memberships (org_id, user_id, role) values (%s, %s, 'viewer'), (%s, %s, 'editor'), (%s, %s, 'viewer')",
              (P, viewer, P, editor, Q, viewer))

sha = lambda n: f"{n:064x}"
def path(org, d=None): return f"{org}/rag/inbox/{d or uuid.uuid4()}.pdf"
def register(c, org, p, s, size=1000, pages=3, **kw):
    r = c.execute("select public.mm_rag_register(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                  (org, p, kw.get("name", "Keel vibration route.pdf"), s, size, pages, kw.get("kind"), kw.get("vendor"), kw.get("date"), kw.get("positions", []))).fetchone()[0]
    return r

# ---- storage policy ----
v = conn(viewer)
upload = lambda c, name: c.execute("insert into storage.objects (bucket_id, name) values ('mm-files', %s)", (name,))
admin.execute("grant insert on storage.objects to authenticated")
check("a viewer can upload a PDF to their private org's inbox", raises(lambda: upload(v, path(P))) is None)
check("not outside rag/inbox", raises(lambda: upload(v, f"{P}/llm/x.pdf")) is not None)
check("not a non-PDF", raises(lambda: upload(v, f"{P}/rag/inbox/{uuid.uuid4()}.exe")) is not None)
check("not into a public demo org", raises(lambda: upload(v, path(Q))) is not None)
o = conn(outsider)
check("not into someone else's org", raises(lambda: upload(o, path(P))) is not None)

# ---- register ----
d1 = str(uuid.uuid4())
r = register(v, P, path(P, d1), sha(1))
check("a viewer registers an upload", r["doc_id"] == d1 and r["status"] == "uploaded" and not r["duplicate"], r)
check("a parse job is queued", admin.execute("select count(*) from llm.rag_jobs where doc_id = %s and step = 'parse' and state = 'queued'", (d1,)).fetchone()[0] == 1)
check("the upload is logged", admin.execute("select to_status from llm.document_events where doc_id = %s", (d1,)).fetchone()[0] == "uploaded")
r2 = register(v, P, path(P), sha(1))
check("the same file again returns the existing document", r2["duplicate"] and r2["doc_id"] == d1, r2)
check("registering in a public org is refused", raises(lambda: register(v, Q, path(Q), sha(2))) is not None)
check("a non-member can't register", raises(lambda: register(o, P, path(P), sha(3))) is not None)
check("anon can't register", raises(lambda: register(conn(), P, path(P), sha(4))) is not None)
check("a path in another org is refused", raises(lambda: register(v, P, path(Q), sha(5))) is not None)
check("a bad hash is refused", raises(lambda: register(v, P, path(P), "abc")) is not None)
check("an oversized file is refused", raises(lambda: register(v, P, path(P), sha(6), size=31 * 1048576)) is not None)
check("the daily page limit holds", raises(lambda: register(v, P, path(P), sha(7), pages=600)) is not None)
check("the library shows it to members", [x[0] for x in v.execute("select doc_id from public.mm_rag_library(%s)", (P,)).fetchall()] == [d1])
check("anon can't see a private org's library", conn().execute("select count(*) from public.mm_rag_library(%s)", (P,)).fetchone()[0] == 0)
check("a member can't write documents directly", raises(lambda: v.execute("update llm.documents set status = 'indexed' where doc_id = %s", (d1,))) is not None
      or admin.execute("select status from llm.documents where doc_id = %s", (d1,)).fetchone()[0] == "uploaded")

# ---- worker (service role) ----
svc = conn(role="service_role")
check("members can't claim jobs", raises(lambda: v.execute("select * from public.mm_rag_claim(1)").fetchall()) is not None)
job = svc.execute("select id, step from public.mm_rag_claim(5) where doc_id = %s", (d1,)).fetchone()
check("the worker claims the parse job", job is not None and job[1] == "parse")
svc.execute("select public.mm_rag_save_pages(%s, %s, %s::jsonb)", (P, d1, json.dumps([
    {"page": 1, "text": "Keel Vibration Services route 2026-10-19. Dryer can 27 drive side 0.24 in/s.", "text_source": "layer"},
    {"page": 2, "text": "Recommend bearing change at next outage.", "text_source": "model"}])))
svc.execute("select public.mm_rag_finish(%s, true, 'parsed', %s::jsonb)", (job[0], json.dumps({"text_source": "mixed"})))
check("parse moves it to parsed and queues assess", admin.execute("select status, text_source from llm.documents where doc_id = %s", (d1,)).fetchone() == ("parsed", "mixed")
      and admin.execute("select count(*) from llm.rag_jobs where doc_id = %s and step = 'assess' and state = 'queued'", (d1,)).fetchone()[0] == 1)
check("page text is readable by members", [p[0] for p in v.execute("select page from public.mm_rag_pages(%s, %s, 1, 9)", (P, d1)).fetchall()] == [1, 2])

job = svc.execute("select id from public.mm_rag_claim(5) where doc_id = %s", (d1,)).fetchone()
for i in range(3):
    if i: admin.execute("update llm.rag_jobs set run_after = now() where id = %s", (job[0],)); svc.execute("select public.mm_rag_claim(5)")
    res = svc.execute("select public.mm_rag_finish(%s, false, null, '{}', 'model timeout')", (job[0],)).fetchone()[0]
check("a step that fails 3 times fails the document", res == "failed" and admin.execute("select status, error from llm.documents where doc_id = %s", (d1,)).fetchone() == ("failed", "model timeout"))
e = conn(editor)
check("a viewer can't retry", raises(lambda: v.execute("select public.mm_rag_review(%s, %s, 'retry')", (P, d1))) is not None)
check("an editor can retry a failed document", e.execute("select public.mm_rag_review(%s, %s, 'retry')", (P, d1)).fetchone()[0] == "uploaded")

# walk it to needs_review
for step, to, patch in [("parse", "parsed", {}), ("assess", "needs_review",
        {"kind": "vibration_route", "vendor": "Keel Vibration Services", "doc_date": "2026-10-19", "positions": ["d2-can27"],
         "quality_score": 62, "summary": "Route; can 27 DS rising.", "quality": {"issues": ["no position tag found"]}})]:
    j = svc.execute("select id from public.mm_rag_claim(5) where doc_id = %s and step = %s", (d1, step)).fetchone()
    svc.execute("select public.mm_rag_finish(%s, true, %s, %s::jsonb)", (j[0], to, json.dumps(patch)))
row = admin.execute("select status, quality_score, vendor, positions from llm.documents where doc_id = %s", (d1,)).fetchone()
check("assess stores quality and metadata", row == ("needs_review", 62, "Keel Vibration Services", ["d2-can27"]), row)
check("needs_review is hidden from mm_llm_documents", v.execute("select count(*) from public.mm_llm_documents(%s)", (P,)).fetchone()[0] == 0)
check("a viewer can't accept", raises(lambda: v.execute("select public.mm_rag_review(%s, %s, 'accept')", (P, d1))) is not None)
check("an editor accepts with corrected metadata", e.execute("select public.mm_rag_review(%s, %s, 'accept', %s::jsonb, 'ok')",
      (P, d1, json.dumps({"positions": ["d2-can27", "d2"]}))).fetchone()[0] == "accepted")
j = svc.execute("select id from public.mm_rag_claim(5) where doc_id = %s and step = 'index'", (d1,)).fetchone()
check("accept queues the index step", j is not None)
svc.execute("select public.mm_rag_save_chunks(%s, %s, %s::jsonb)", (P, d1, json.dumps([
    {"chunk_no": 0, "page": 1, "content": "Keel Vibration Services · Vibration route · 2026-10-19 · Dryer can 27 · p.1\nDryer can 27 drive side 0.24 in/s.", "positions": ["d2-can27"]}])))
svc.execute("select public.mm_rag_finish(%s, true, 'indexed')", (j[0],))
check("indexed documents show in mm_llm_documents", v.execute("select count(*) from public.mm_llm_documents(%s)", (P,)).fetchone()[0] == 1)
hits = v.execute("select doc_id, page, matched from public.mm_rag_search(%s, 'can 27 drive side')", (P,)).fetchall()
check("search finds the indexed chunk", hits and hits[0][0] == d1 and hits[0][2] == "text", hits)
check("search filters by position", len(v.execute("select 1 from public.mm_rag_search(%s, 'can 27', null, 8, null, null, 'ref-1')", (P,)).fetchall()) == 0)
check("the document history has every step", [x[0] for x in admin.execute("select to_status from llm.document_events where doc_id = %s order by id", (d1,)).fetchall()]
      == ["uploaded", "parsed", "failed", "uploaded", "parsed", "needs_review", "accepted", "indexed"])
info = v.execute("select public.mm_rag_document(%s, %s)", (P, d1)).fetchone()[0]
check("mm_rag_document returns metadata, events and counts", info["chunks"] == 1 and info["pages_stored"] == 2 and len(info["events"]) == 8 and "uploaded_by" not in info["document"])

# versions and rejection
d2 = str(uuid.uuid4()); register(v, P, path(P, d2), sha(8), name="Keel vibration route v2.pdf")
admin.execute("update llm.documents set status = 'needs_review' where doc_id = %s", (d2,))
e.execute("select public.mm_rag_review(%s, %s, 'accept', %s::jsonb)", (P, d2, json.dumps({"supersedes": d1})))
admin.execute("update llm.documents set status = 'indexed' where doc_id = %s", (d2,))
check("a new version marks the old one superseded", admin.execute("select superseded_by from llm.documents where doc_id = %s", (d1,)).fetchone()[0] == d2)
check("search hides superseded versions by default", len(v.execute("select 1 from public.mm_rag_search(%s, 'can 27')", (P,)).fetchall()) == 0
      and len(v.execute("select 1 from public.mm_rag_search(%s, 'can 27', null, 8, null, null, null, null, null, null, true)", (P,)).fetchall()) == 1)
check("rejecting removes the chunks", e.execute("select public.mm_rag_review(%s, %s, 'reject', '{}', 'wrong mill')", (P, d1)).fetchone()[0] == "rejected"
      and admin.execute("select count(*) from llm.doc_chunks where doc_id = %s", (d1,)).fetchone()[0] == 0)
r3 = register(v, P, path(P), sha(1))
check("a rejected file can be uploaded again", not r3["duplicate"])
check("status counts", dict(v.execute("select status, docs from public.mm_rag_status(%s)", (P,)).fetchall()).get("rejected") == 1)

print(f"\n{len(failures)} failed" if failures else "\nall passed")
sys.exit(1 if failures else 0)
