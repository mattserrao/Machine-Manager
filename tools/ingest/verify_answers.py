"""Check that the loaded data can answer every demo question: runs each answer-key check through the tool functions.

    # local Postgres: runs as a signed-in viewer of the org, so row-level security applies
    python3 tools/ingest/verify_answers.py --dsn "host=... dbname=..." --org "Demo Mill"

    # live project: print one SQL query (paste in the SQL editor or run with the Supabase MCP); one row per check
    python3 tools/ingest/verify_answers.py --emit-sql --org "Demo Mill"
"""
import argparse, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KEYS = {'Demo Mill': os.path.join(ROOT, 'demo-data', 'answers', 'answer_key.json'),
        'Sim Mill': os.path.join(ROOT, 'demo-data', 'sim-mill', 'answers', 'answer_key.json')}
KEY = KEYS['Demo Mill']

def checks():
    for q in json.load(open(KEY))['questions']:
        for c in q['checks']: yield q['id'], c['desc'], c['sql']

def emit_sql(org_name):
    org = f"(select id from public.orgs where name = '{org_name}')"
    lit = lambda x: "'" + x.replace("'", "''") + "'"
    parts = [f"select {lit(qid)} as question, {lit(d)} as check, ({s.replace(':org', org)}) as ok" for qid, d, s in checks()]
    return '\nunion all\n'.join(parts) + ';'

def run_local(dsn, org_name):
    import psycopg, uuid
    c = psycopg.connect(dsn, autocommit=True)
    org = c.execute('select id from public.orgs where name = %s', (org_name,)).fetchone()[0]
    uid = c.execute("insert into auth.users (id, email) values (%s, 'verify@demo.invalid') on conflict do nothing returning id", (str(uuid.uuid4()),)).fetchone()
    uid = uid[0] if uid else c.execute("select id from auth.users where email = 'verify@demo.invalid'").fetchone()[0]
    c.execute("insert into public.memberships (org_id, user_id, role) values (%s, %s, 'viewer') on conflict do nothing", (org, uid))
    c.execute("select set_config('request.jwt.sub', %s, false)", (str(uid),)); c.execute('set role authenticated')
    fails = 0
    for qid, d, s in checks():
        try: ok = c.execute('select ' + s.replace(':org', f"'{org}'::uuid")).fetchone()[0]   # no params: LIKE patterns keep their %
        except Exception as e: ok = False; d += f' — ERROR {str(e).splitlines()[0]}'
        print(('PASS ' if ok else 'FAIL ') + f'{qid}: {d}'); fails += not ok
    c.execute('reset role')
    # and a non-member sees nothing through the same tools
    c.execute("select set_config('request.jwt.sub', %s, false)", (str(uuid.uuid4()),)); c.execute('set role authenticated')
    pub = c.execute("select exists (select 1 from llm.public_orgs where org_id = %s)", (org,)).fetchone()[0]
    n = c.execute("select count(*) from public.mm_llm_overdue_actions(%s, '2026-10-31')", (org,)).fetchone()[0]
    if pub: print('SKIP a non-member gets nothing from the tools (the org is public)')
    else: print(('PASS ' if n == 0 else 'FAIL ') + 'a non-member gets nothing from the tools'); fails += n != 0
    c.execute('reset role')
    return fails

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--dsn'); ap.add_argument('--org', default='Demo Mill'); ap.add_argument('--emit-sql', action='store_true')
    ap.add_argument('--key', help='answer key (default: the org\'s own, demo-data/... )')
    a = ap.parse_args()
    KEY = a.key or KEYS.get(a.org, KEY)
    if a.emit_sql: print(emit_sql(a.org)); sys.exit(0)
    f = run_local(a.dsn, a.org)
    print(f'{f} failing' if f else 'all answer-key checks pass'); sys.exit(1 if f else 0)
