"""Tests for supabase/schema.sql: access rules, version checks, batch isolation, concurrency.

Runs against a plain Postgres with tests/db/supabase-shim.sql loaded first (it stands in for the
parts of Supabase the schema uses: auth.uid(), roles, storage tables, the realtime publication).

    PGDSN="host=localhost dbname=mm_test user=postgres password=pg" python3 tests/db/test_schema.py

Exits non-zero if any test fails.
"""
import json, os, sys, threading, time
import psycopg

DSN = os.environ.get("PGDSN", "host=localhost dbname=mm_test user=postgres password=pg")
failures = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok:
        failures.append(name)


def connect():
    return psycopg.connect(DSN, autocommit=True)


def as_user(c, uid):
    c.execute("reset role")
    c.execute("select set_config('request.jwt.sub', %s, false)", (str(uid) if uid else "",))
    c.execute("set role authenticated" if uid else "set role anon")


def apply(c, org, tool, changes):
    return c.execute("select public.mm_apply(%s, %s, %s::jsonb)", (org, tool, json.dumps(changes))).fetchone()[0]


def raises(fn):
    try:
        fn()
        return None
    except psycopg.Error as e:
        return e


admin = connect()
admin.execute("truncate public.mm_records, public.memberships, public.orgs cascade")
admin.execute("truncate auth.users cascade")
users = {e: admin.execute("insert into auth.users(email) values (%s) returning id", (e,)).fetchone()[0]
         for e in ["ed@a", "vw@a", "ad@a", "out@x", "ed@b"]}
for email, role, org in [("ed@a", "editor", "PM1"), ("vw@a", "viewer", "PM1"), ("ad@a", "admin", "PM1"), ("ed@b", "editor", "OTHER")]:
    admin.execute("select public.mm_add_member(%s, %s, %s)", (org, email, role))
A = admin.execute("select id from orgs where name = 'PM1'").fetchone()[0]
B = admin.execute("select id from orgs where name = 'OTHER'").fetchone()[0]
ed, vw, out, ed_b = users["ed@a"], users["vw@a"], users["out@x"], users["ed@b"]
c = connect()

# ───────── access ─────────
as_user(c, ed)
r = apply(c, A, "mymachine", [{"id": "machine", "data": {"name": "PM1"}, "base": None}])
check("editor creates a record (version 1)", r[0]["ok"] and r[0]["version"] == 1)
r = apply(c, A, "mymachine", [{"id": "machine", "data": {"name": "PM1b"}, "base": 1}])
check("update with the current version bumps it", r[0]["ok"] and r[0]["version"] == 2)
r = apply(c, A, "mymachine", [{"id": "machine", "data": {"name": "stale"}, "base": 1}])
check("stale version is refused and returns the current row", not r[0]["ok"] and r[0]["row"]["data"]["name"] == "PM1b" and "error" not in r[0])
row = admin.execute("select created_by from mm_records where id = 'machine'").fetchone()
check("created_by is recorded", row[0] == ed)

as_user(c, vw)
r = apply(c, A, "mymachine", [{"id": "viewer-new", "data": {}, "base": None}])
check("viewer insert is refused per change", not r[0]["ok"] and "error" in r[0], json.dumps(r[0])[:120])
r = apply(c, A, "mymachine", [{"id": "machine", "data": {"name": "viewer"}, "base": 2}])
check("viewer update changes nothing", not r[0]["ok"])
check("viewer can read", c.execute("select count(*) from mm_records").fetchone()[0] >= 1)

as_user(c, out)
check("non-member sees nothing", c.execute("select count(*) from mm_records").fetchone()[0] == 0)
as_user(c, ed_b)
check("another org's editor can't read PM1", c.execute("select count(*) from mm_records where org_id = %s", (A,)).fetchone()[0] == 0)
r = apply(c, A, "mymachine", [{"id": "evil", "data": {}, "base": None}])
check("another org's editor can't write PM1", not r[0]["ok"] and "error" in r[0])
check("…and nothing was written", admin.execute("select count(*) from mm_records where id = 'evil'").fetchone()[0] == 0)
as_user(c, None)
check("anon can't read tables", raises(lambda: c.execute("select count(*) from mm_records").fetchone()) is not None)
check("anon can't call mm_apply", raises(lambda: apply(c, A, "x", [])) is not None)

# ───────── one bad change never blocks the rest ─────────
as_user(c, ed)
bad = {
    "id over 200 characters": {"id": "x" * 201, "data": {}, "base": None},
    "base not a number": {"id": "b1", "data": {}, "base": "abc"},
    "missing id": {"data": {}, "base": None},
    "deleted not a boolean": {"id": "b2", "deleted": "yes", "base": None},
    "change not an object": 42,
}
for name, change in bad.items():
    good = [{"id": f"good-{abs(hash(name))}-{i}", "data": {"i": i}, "base": None} for i in range(4)]
    batch = good[:2] + [change] + good[2:]
    e = raises(lambda: apply(c, A, "consumables", batch))
    if e:
        check(f"bad change ({name}) is isolated", False, f"whole call failed: {e}")
        continue
    r = apply(c, A, "consumables", [{"id": g["id"], "data": {}, "base": 1} for g in good])  # all 4 exist at v1?
    saved = sum(x["ok"] for x in r)
    check(f"bad change ({name}) is isolated", saved == 4, f"{saved}/4 good changes saved")
r = apply(c, A, "consumables", [{"id": "o3", "data": {}, "base": None}, {"id": "o1", "data": {}, "base": None}, {"id": "o2", "data": {}, "base": "nope"}])
check("results come back in the order sent", [x["id"] for x in r] == ["o3", "o1", "o2"] and [x["ok"] for x in r] == [True, True, False])
check("non-array input is refused", raises(lambda: apply(c, A, "consumables", {"id": "x"})) is not None)
check("more than 500 changes is refused", raises(lambda: apply(c, A, "consumables", [{"id": f"m{i}", "base": None} for i in range(501)])) is not None)
check("bad tool name is refused", not apply(c, A, "Bad Tool!", [{"id": "a", "data": {}, "base": None}])[0]["ok"])
check("null data becomes {}", apply(c, A, "consumables", [{"id": "nulldata", "data": None, "base": None}])[0]["ok"])

# ───────── deleted records ─────────
apply(c, A, "mymachine", [{"id": "item:x", "data": {"installed": "2026-01-01"}, "base": None}])
apply(c, A, "mymachine", [{"id": "item:x", "deleted": True, "base": 1}])
r = apply(c, A, "mymachine", [{"id": "item:x", "data": {"installed": "2026-02-02"}, "base": None}])
row = admin.execute("select deleted, data->>'installed', version from mm_records where id = 'item:x'").fetchone()
check("creating a record over a deleted one brings it back", r[0]["ok"] and row == (False, "2026-02-02", 3), str(row))
r = apply(c, A, "mymachine", [{"id": "item:x", "data": {"installed": "1999-01-01"}, "base": None}])
check("…but never overwrites a live record", not r[0]["ok"] and r[0]["row"]["data"]["installed"] == "2026-02-02")

# ───────── file references ─────────
apply(c, A, "whiteboard", [
    {"id": "n:b1:n1", "data": {"text": "a", "attachments": [{"id": "a1", "path": f"{A}/whiteboard/b1/a1-x.png"}]}, "base": None},
    {"id": "n:b1:n2", "data": {"text": "b", "attachments": [{"id": "a2", "path": None}]}, "base": None},
])
refs = [r[0] for r in c.execute("select * from public.mm_file_refs(%s, 'whiteboard')", (A,)).fetchall()]
check("mm_file_refs lists attachment paths", refs == [f"{A}/whiteboard/b1/a1-x.png"], str(refs))
as_user(c, ed_b)
check("mm_file_refs respects access", c.execute("select count(*) from public.mm_file_refs(%s, 'whiteboard')", (A,)).fetchone()[0] == 0)
as_user(c, ed)

# ───────── concurrency ─────────
apply(c, A, "outages", [{"id": "race", "data": {"n": 0}, "base": None}])
wins, errs = [], []


def racer(i):
    cc = connect(); as_user(cc, ed)
    try:
        wins.append(apply(cc, A, "outages", [{"id": "race", "data": {"n": i}, "base": 1}])[0]["ok"])
    except Exception as e:
        errs.append(str(e))
    cc.close()


ts = [threading.Thread(target=racer, args=(i,)) for i in range(20)]
[t.start() for t in ts]; [t.join() for t in ts]
check("20 saves of the same version: exactly one wins", sum(wins) == 1 and not errs, f"wins={sum(wins)} errors={len(errs)}")

wins = []


def seeder(i):
    cc = connect(); as_user(cc, ed)
    wins.append(sum(x["ok"] for x in apply(cc, A, "task-packages", [{"id": f"seed-{k}", "data": {"by": i}, "base": None} for k in range(5)])))
    cc.close()


ts = [threading.Thread(target=seeder, args=(i,)) for i in range(8)]
[t.start() for t in ts]; [t.join() for t in ts]
check("8 editors creating the same 5 records at once: one copy each", sum(wins) == 5, f"created={sum(wins)}")

apply(c, A, "dl", [{"id": k, "data": {}, "base": None} for k in "abcdef"])
dl_errors = []


def opposite(order):
    cc = connect(); as_user(cc, ed)
    for _ in range(40):
        try:
            cur = dict(cc.execute("select id, version from mm_records where org_id = %s and tool = 'dl'", (A,)).fetchall())
            apply(cc, A, "dl", [{"id": k, "data": {"t": time.time()}, "base": cur[k]} for k in order])
        except Exception as e:
            dl_errors.append(type(e).__name__)
    cc.close()


ts = [threading.Thread(target=opposite, args=(o,)) for o in (list("abcdef"), list("fedcba"), list("cafebd"))]
[t.start() for t in ts]; [t.join() for t in ts]
check("overlapping batches in different orders never deadlock", not dl_errors, f"errors: {sorted(set(dl_errors)) or 'none'}")

# ───────── load ─────────
note = {"text": "Check shower nozzles on 2nd press; replace any plugged. " * 4, "x": 100, "y": 200, "attachments": [], "children": []}
t = time.perf_counter()
apply(c, A, "load", [{"id": f"n{i:03}", "data": note, "base": None} for i in range(500)])
ms = (time.perf_counter() - t) * 1000
check("500-change batch", ms < 3000, f"{ms:.0f} ms")

print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all passed'}")
sys.exit(1 if failures else 0)
