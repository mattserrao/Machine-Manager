"""Tests for supabase/llm.sql: ingest tokens decide the org, readers only see their org, tools respect RLS.

    PGDSN="host=localhost dbname=mm_test user=postgres password=pg" python3 tests/db/test_llm.py
(load tests/db/supabase-shim.sql, supabase/schema.sql and supabase/llm.sql first)
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

admin = psycopg.connect(DSN, autocommit=True)
def as_user(c, uid):
    c.execute("reset role"); c.execute("select set_config('request.jwt.sub', %s, false)", (str(uid) if uid else "",))
    c.execute("set role authenticated" if uid else "set role anon")
def ingest(c, tok, table, rows, mode="upsert"):
    return c.execute("select public.mm_llm_ingest(%s, %s, %s::jsonb, %s)", (tok, table, json.dumps(rows), mode)).fetchone()[0]

name_a, name_b = f"LLM-A-{uuid.uuid4().hex[:6]}", f"LLM-B-{uuid.uuid4().hex[:6]}"
tok_a = admin.execute("select public.mm_llm_new_ingest_token(%s, 1)", (name_a,)).fetchone()[0]
tok_b = admin.execute("select public.mm_llm_new_ingest_token(%s, 1)", (name_b,)).fetchone()[0]
A = admin.execute("select id from orgs where name = %s", (name_a,)).fetchone()[0]
B = admin.execute("select id from orgs where name = %s", (name_b,)).fetchone()[0]
check("tokens are stored hashed, not in clear", admin.execute("select count(*) from private.llm_ingest_tokens where token_hash = %s", (tok_a,)).fetchone()[0] == 0)

anon = psycopg.connect(DSN, autocommit=True); as_user(anon, None)
check("anon can't call mm_llm_ingest directly", raises(lambda: ingest(anon, tok_a, "equipment", [])) is not None)
anon.execute("reset role"); anon.execute("set role service_role")   # the edge function's role
svc = anon
check("the service role can ingest with a valid token", ingest(svc, tok_a, "equipment", [{"asset_no": "1", "name": "Dryer can 1", "section": "s"}]) == 1)
check("org comes from the token, not the row", ingest(svc, tok_a, "equipment", [{"asset_no": "2", "name": "x", "org_id": str(B)}]) == 1
      and admin.execute("select org_id from llm.equipment where asset_no = '2'").fetchone()[0] == A)
check("a bad token is refused", raises(lambda: ingest(svc, "nope", "equipment", [])) is not None)
check("an unknown table is refused", raises(lambda: ingest(svc, tok_a, "orgs", [])) is not None)
check("more than 5000 rows is refused", raises(lambda: ingest(svc, tok_a, "equipment", [{"asset_no": str(i), "name": "n"} for i in range(5001)])) is not None)
admin.execute("update private.llm_ingest_tokens set expires_at = now() - interval '1 minute' where org_id = %s", (B,))
check("an expired token is refused", raises(lambda: ingest(svc, tok_b, "equipment", [])) is not None)
check("re-ingesting a row updates it", ingest(svc, tok_a, "equipment", [{"asset_no": "1", "name": "Dryer can 1 renamed", "section": "s"}]) == 1
      and admin.execute("select name from llm.equipment where org_id = %s and asset_no = '1'", (A,)).fetchone()[0] == "Dryer can 1 renamed")
check("defaults apply to columns the rows leave out", ingest(svc, tok_a, "ingest_files", [{"source_file": "a.csv", "kind": "x"}]) == 1
      and admin.execute("select imported_at is not null from llm.ingest_files where org_id = %s", (A,)).fetchone()[0])
svc = anon; anon = psycopg.connect(DSN, autocommit=True); as_user(anon, None)
check("anon sees no rows of a private org", anon.execute("select count(*) from llm.equipment").fetchone()[0] == 0)
check("anon gets nothing from the tools for a private org", len(anon.execute("select * from public.mm_llm_overdue_actions(%s, '2026-03-01')", (A,)).fetchall()) == 0)
check("no public demo org yet", anon.execute("select count(*) from public.mm_llm_public_org()").fetchone()[0] == 0)
check("anon can't make an org public", raises(lambda: anon.execute("select public.mm_llm_set_public(%s, true)", (name_a,)).fetchone()) is not None)
check("anon can't create tokens", raises(lambda: anon.execute("select public.mm_llm_new_ingest_token('x', 1)").fetchone()) is not None)

u_a, u_b = uuid.uuid4(), uuid.uuid4()
admin.execute("insert into auth.users (id, email) values (%s, 'a@t'), (%s, 'b@t')", (u_a, u_b))
admin.execute("insert into memberships (org_id, user_id, role) values (%s, %s, 'viewer'), (%s, %s, 'viewer')", (A, u_a, B, u_b))
c = psycopg.connect(DSN, autocommit=True)
as_user(c, u_a); check("a member reads their org's rows", c.execute("select count(*) from llm.equipment").fetchone()[0] == 2)
check("a member can't write directly", raises(lambda: c.execute("insert into llm.equipment (org_id, asset_no, name) values (%s, '9', 'x')", (A,))) is not None)
as_user(c, u_b); check("another org's member sees none of them", c.execute("select count(*) from llm.equipment").fetchone()[0] == 0)
ingest(svc, tok_a, "actions", [{"task_id": "t1", "title": "Fix guard", "progress": "Not started", "due": "2026-01-01", "as_of": "2026-02-01", "late": True}])
as_user(c, u_a); check("tools work for a member", len(c.execute("select * from public.mm_llm_overdue_actions(%s)", (A,)).fetchall()) == 1)
as_user(c, u_b); check("tools return nothing for another org's member", len(c.execute("select * from public.mm_llm_overdue_actions(%s)", (A,)).fetchall()) == 0)
# a public demo org: anyone can read it, signed in or not
admin.execute("select public.mm_llm_set_public(%s, true)", (name_a,))
check("the public demo org is advertised", anon.execute("select id from public.mm_llm_public_org()").fetchone()[0] == A)
check("anon reads the public org", anon.execute("select count(*) from llm.equipment where org_id = %s", (A,)).fetchone()[0] == 2)
check("anon's tools work on the public org", len(anon.execute("select * from public.mm_llm_overdue_actions(%s)", (A,)).fetchall()) == 1)
as_user(c, u_b); check("a signed-in non-member reads the public org too", c.execute("select count(*) from llm.equipment where org_id = %s", (A,)).fetchone()[0] == 2)
check("…but still not the other private org", anon.execute("select count(*) from llm.equipment where org_id = %s", (B,)).fetchone()[0] == 0)
admin.execute("insert into storage.objects (bucket_id, name) values ('mm-files', %s), ('mm-files', %s), ('mm-files', %s)",
              (f"{A}/llm/docs/x.pdf", f"{A}/whiteboard/y.png", f"{B}/llm/docs/z.pdf"))
check("anon can read the public org's llm files only", [r[0] for r in anon.execute("select name from storage.objects order by name").fetchall()] == [f"{A}/llm/docs/x.pdf"])
admin.execute("select public.mm_llm_set_public(%s, false)", (name_a,))
check("making it private again hides it", anon.execute("select count(*) from llm.equipment").fetchone()[0] == 0)
check("reset clears the org's rows", ingest(svc, tok_a, "actions", [], "reset") == 0 and admin.execute("select count(*) from llm.actions where org_id = %s", (A,)).fetchone()[0] == 0)

# ── Asking: allowlist and saved answers ──
admin.execute("select public.mm_llm_set_public(%s, true)", (name_a,))
admin.execute("insert into auth.users (id, email) values (%s, 'asker@t')", (str(u_q := uuid.uuid4()),))
check("only the SQL editor can grant asking", raises(lambda: anon.execute("select public.mm_llm_grant_query('asker@t', %s, 5)", (name_a,)).fetchone()) is not None)
admin.execute("select public.mm_llm_grant_query('asker@t', %s, 5)", (name_a,))
admin.execute("insert into llm.answers (org_id, question_id, question, answer, asked_by) values (%s, 'S01-Q1', 'q?', 'a.', %s)", (A, u_q))
as_user(c, u_q); r = c.execute("select org_id, daily_limit, used_today, can_ask from public.mm_llm_my_access()").fetchall()
check("an allowed user sees their access and today's count", r == [(A, 5, 1, True)], str(r))
as_user(c, u_b); check("a user without access gets no row", c.execute("select count(*) from public.mm_llm_my_access()").fetchone()[0] == 0)
check("any signed-in user reads the public org's answers", c.execute("select count(*) from llm.answers where org_id = %s", (A,)).fetchone()[0] == 1)
check("anon can't read answers", raises(lambda: anon.execute("select count(*) from llm.answers").fetchone()) is not None)
check("signed-in users can't write answers", raises(lambda: c.execute("insert into llm.answers (org_id, question) values (%s, 'x')", (A,))) is not None)
check("users only see their own access row", c.execute("select count(*) from llm.query_access").fetchone()[0] == 0)
admin.execute("insert into llm.answers (org_id, question_id, question, answer, status) values (%s, 'S01-Q1', 'q?', 'newer, failed', 'error')", (A,))
r = c.execute("select answer from public.mm_llm_saved_answers(%s)", (A,)).fetchall()
check("saved answers: latest good answer per demo question", r == [('a.',)], str(r))
check("anon can't call the saved-answers reader", raises(lambda: anon.execute("select * from public.mm_llm_saved_answers(%s)", (A,)).fetchall()) is not None)
check("my answers: only the caller's own", c.execute("select count(*) from public.mm_llm_my_answers(%s)", (A,)).fetchone()[0] == 0)
as_user(c, u_q); check("my answers: the asker sees theirs", c.execute("select count(*) from public.mm_llm_my_answers(%s)", (A,)).fetchone()[0] == 1)
as_user(c, u_b)
admin.execute("select public.mm_llm_set_public(%s, false)", (name_a,))
as_user(c, u_b); check("answers of a private org are hidden from non-members", c.execute("select count(*) from llm.answers where org_id = %s", (A,)).fetchone()[0] == 0)

print(f"\n{len(failures)} failing" if failures else "\nall passed"); sys.exit(1 if failures else 0)
