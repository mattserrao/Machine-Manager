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

# ─── step 05: downtime / production / position runs, records ingest, several public orgs ───
check("downtime rows load through the token", ingest(svc, tok_a, "downtime", [
    {"event_id": "DT-1", "starts_at": "2026-01-06T09:40:00-05:00", "ends_at": "2026-01-06T12:22:00-05:00", "minutes": 162, "kind": "unplanned",
     "area": "3rd dryer section", "equipment": "3rd section rotary joint (DS)", "asset_no": "1", "cause": "Rotary joint leak"},
    {"event_id": "DT-2", "starts_at": "2026-06-23T15:10:00-05:00", "ends_at": "2026-06-23T18:04:00-05:00", "minutes": 174, "kind": "unplanned",
     "area": "3rd dryer section", "equipment": "3rd section rotary joint (DS)", "asset_no": "1", "cause": "Rotary joint leak"},
    {"event_id": "DT-3", "starts_at": "2026-06-24T01:00:00-05:00", "ends_at": "2026-06-24T01:30:00-05:00", "minutes": 30, "kind": "break", "area": "Reel"}]) == 3)
check("a bad downtime kind is refused", raises(lambda: ingest(svc, tok_a, "downtime", [{"event_id": "DT-X", "starts_at": "2026-01-01T00:00:00Z",
      "ends_at": "2026-01-01T01:00:00Z", "minutes": 60, "kind": "nap"}])) is not None)
ingest(svc, tok_a, "production_daily", [{"day": "2026-06-23", "tons": 640, "uptime_pct": 87.9, "breaks": 1}])
ingest(svc, tok_a, "position_runs", [{"position_id": "p2-felt-top", "installed": "2026-04-15", "removed": "2026-05-19", "days": 34, "target_days": 42,
                                     "reason": "performance", "condition": "worn", "position_name": "2nd press top felt"}])
check("records load for an allowed tool, into the token's org", ingest(svc, tok_a, "records:mymachine", [{"id": "machine", "data": {"name": "PM1"}},
      {"id": "item:p2-felt-top", "data": {"installed": "2026-05-19"}}]) == 2
      and admin.execute("select count(*) from mm_records where org_id = %s and tool = 'mymachine'", (A,)).fetchone()[0] == 2)
check("records for other tools are refused", raises(lambda: ingest(svc, tok_a, "records:whiteboard", [{"id": "p:x", "data": {}}])) is not None)
check("records reset replaces that tool's records only", ingest(svc, tok_a, "records:mymachine", [{"id": "machine", "data": {"name": "PM1"}}], "reset") == 1
      and admin.execute("select count(*) from mm_records where org_id = %s and tool = 'mymachine'", (A,)).fetchone()[0] == 1)
as_user(c, u_b)
check("new tables: a non-member sees no downtime", c.execute("select count(*) from llm.downtime").fetchone()[0] == 0)
check("new tools: a non-member gets nothing", c.execute("select count(*) from public.mm_llm_downtime_summary(%s, '2026-01-01', '2026-12-31')", (A,)).fetchone()[0] == 0)
admin.execute("select public.mm_llm_set_public(%s, true)", (name_a,)); admin.execute("select public.mm_llm_set_public(%s, true)", (name_b,))
as_user(anon, None)
pubs = [r[0] for r in anon.execute("select id from public.mm_llm_public_org()").fetchall()]
check("every public org is listed, the first published first", pubs == [A, B], str(pubs))
r = anon.execute("select equipment, events, rcfas from public.mm_llm_repeat_stops(%s, '2026-01-01', '2026-12-31')", (A,)).fetchall()
check("repeat stops without an RCFA (anon on a public org)", r == [("3rd section rotary joint (DS)", 2, "none")], str(r))
r = anon.execute("select kind, events, minutes from public.mm_llm_downtime_summary(%s, '2026-01-01', '2026-12-31', 'kind')", (A,)).fetchall()
check("downtime summary by kind", sorted((k, n) for k, n, _ in r) == [("break", 1), ("unplanned", 2)], str(r))
r = anon.execute("select early, pct_of_target from public.mm_llm_position_life(%s, 'p2-felt-top')", (A,)).fetchall()
check("position life flags an early removal", r == [(True, 81)], str(r))
check("production summary", anon.execute("select tons from public.mm_llm_production(%s, '2026-06-01', '2026-06-30', 'month')", (A,)).fetchone()[0] == 640)
check("anon can't read the demo org's mm_records", raises(lambda: anon.execute("select count(*) from mm_records").fetchone()) is not None
      or anon.execute("select count(*) from mm_records").fetchone()[0] == 0)
admin.execute("select public.mm_llm_set_public(%s, false)", (name_a,)); admin.execute("select public.mm_llm_set_public(%s, false)", (name_b,))

# ─── step 09: reports and their lifecycle ───
ingest(svc, tok_a, "report_types", [{"type": "shift", "title": "Shift Report", "cadence": "shift", "required": ["stops", "notes"], "extract": ["downtime"]},
                                     {"type": "production", "title": "Production Report", "cadence": "day", "required": ["tons", "efficiency"], "extract": ["production_daily"]}])
stop = {"event_id": "R-1", "start": "2026-07-01T08:00-04:00", "end": "2026-07-01T10:30-04:00", "minutes": 150, "kind": "unplanned", "area": "Press",
        "equipment": "Vacuum pump", "asset_no": "77", "position_id": "", "cause": "Vacuum pump failure", "wo_no": "W1", "comment": "vanes"}
rep = lambda rid, rtype, body, day="2026-07-01": {"report_id": rid, "type": rtype, "machine": "PM1", "period_start": day + "T06:00-04:00",
      "period_end": day + "T18:00-04:00", "mill_day": day, "shift": "Day", "crew": "B", "author": "Lead", "body": body, "text": "Vacuum pump down 2.5 h; couch vacuum fell off all week.", "status": "ingested"}
ingest(svc, tok_a, "rcfa", [{"rcfa_id": "RC-9", "event_date": "2026-07-01", "asset_no": "77", "title": "Vacuum pump"}])
ingest(svc, tok_a, "reports", [rep("S-1", "shift", {"stops": [stop], "notes": "x"}), rep("S-2", "shift", {"notes": "no stops field"}),
                               rep("P-1", "production", {"tons": 700, "minutes": {"break": 30}, "efficiency": {"ome_pct": 81.5, "time_pct": 97}})])
check("reports can't be processed without a token", raises(lambda: c.execute("select public.mm_llm_process_reports('nope', 10)").fetchone()) is not None)
r = svc.execute("select public.mm_llm_process_reports(%s, 100)", (tok_a,)).fetchone()[0]
check("processing: two extracted, one failed", r == {"picked": 3, "extracted": 2, "failed": 1}, str(r))
st = dict(admin.execute("select report_id, status from llm.reports where org_id = %s", (A,)).fetchall())
check("statuses after processing", st == {"S-1": "indexed", "S-2": "failed", "P-1": "indexed"}, str(st))
check("a failed report says why", "stops" in admin.execute("select error from llm.reports where report_id = 'S-2'").fetchone()[0])
d = admin.execute("select minutes, rcfa_id, report_id from llm.downtime where org_id = %s and event_id = 'R-1'", (A,)).fetchone()
check("a shift report's stops land in downtime, with the RCFA found by equipment and day", d == (150, "RC-9", "S-1"), str(d))
p = admin.execute("select tons, ome_pct, time_eff, report_id from llm.production_daily where org_id = %s and day = '2026-07-01'", (A,)).fetchone()
check("a production report lands in production_daily", p == (700, 81.5, 97, "P-1"), str(p))
ev = [r[0] for r in admin.execute("select to_status from llm.report_events where report_id = 'S-1' order by id").fetchall()]
check("every status change is logged", ev == ["ingested", "extracted", "indexed"], str(ev))
check("processing again picks nothing", svc.execute("select public.mm_llm_process_reports(%s, 100)", (tok_a,)).fetchone()[0]["picked"] == 0)
ingest(svc, tok_a, "reports", [rep("S-1", "shift", {"stops": [dict(stop, minutes=160)], "notes": "x"})])
svc.execute("select public.mm_llm_process_reports(%s, 100)", (tok_a,))
check("a re-ingested report is extracted again (idempotent, no duplicates)",
      admin.execute("select count(*), max(minutes) from llm.downtime where org_id = %s and report_id = 'S-1'", (A,)).fetchone() == (1, 160))
as_user(c, u_a)
check("a member reads their reports", c.execute("select count(*) from public.mm_llm_reports(%s, '2026-07-01', '2026-07-01')", (A,)).fetchone()[0] == 3)
check("report search finds words in the text", c.execute("select count(*) from public.mm_llm_reports(%s, '2026-01-01', '2026-12-31', null, 'couch vacuum')", (A,)).fetchone()[0] == 3)
check("a report with its lifecycle", len(c.execute("select events from public.mm_llm_report(%s, 'S-1')", (A,)).fetchone()[0]) >= 3)
check("the pipeline status", ("shift", "failed") in [(r[0], r[3]) for r in c.execute("select * from public.mm_llm_report_status(%s)", (A,)).fetchall()])
as_user(c, u_b)
check("a non-member reads no reports", c.execute("select count(*) from public.mm_llm_reports(%s, '2026-01-01', '2026-12-31')", (A,)).fetchone()[0] == 0
      and c.execute("select count(*) from llm.report_events").fetchone()[0] == 0)
ingest(svc, tok_a, "reports", [], "reset")
check("resetting reports clears what was extracted from them",
      admin.execute("select count(*) from llm.downtime where org_id = %s and report_id is not null", (A,)).fetchone()[0] == 0
      and admin.execute("select count(*) from llm.production_daily where org_id = %s and report_id is not null", (A,)).fetchone()[0] == 0)

print(f"\n{len(failures)} failing" if failures else "\nall passed"); sys.exit(1 if failures else 0)
