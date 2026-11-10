-- MM LLM — the data the assistant reads, and the tools it reads it through.
-- Applied after schema.sql: the tests load both, and on the live project this file is migration step 04
-- (see migrations/README.md). Safe to re-run.
--
-- Model (schema llm; not exposed to the web API directly)
--   equipment, pi_tags, outages      the backbone: positions every other row is tagged to
--   bus_items                        one row per BUS sheet line (sheet date × issue); issue_key groups an issue across days
--   work_orders, actions             latest state from the JDE / Planner exports (re-imports update in place)
--   rcfa                             the RCFA log
--   bonvoy                            Bonvoy exceptions (one row per tag per day)
--   pi_series                        Pi series packed as arrays: hourly averages one row per tag per UTC day ('h'),
--                                    1-minute data one row per tag per hour around events ('m')
--   documents, doc_chunks            every document (vendor report, RCFA write-up, drawing, reference chart) and its
--                                    searchable chunks (full text always; embedding when the embedder has run)
--   ingest_files                     what was imported, when, from which file
--   downtime                         every stop, sheet break and slowdown (one row per event)          (step 05)
--   production_daily                 one row per mill day: tons, uptime, breaks, minutes lost, energy  (step 05)
--   position_runs                    every fabric, felt, plate and roll run on a position (life history) (step 05)
--   report_types, reports,           every report (Shift, Production, ...) as ingested, with its lifecycle: ingested ->
--   report_events                    extracted -> indexed | failed; downtime and production_daily rows keep report_id (step 09)
--
-- Access: members of an org can read its rows (RLS, same rule as mm_records), and anyone can read a public demo
-- org's rows (mm_llm_set_public; the Demo Mill is one). Nobody writes from the web page:
-- imports go through the mm-llm-ingest edge function and mm_llm_ingest(), guarded by an ingest token an admin creates in the SQL editor
-- (select public.mm_llm_new_ingest_token('Demo Mill', 6);). Tokens are stored hashed and expire.
--
-- Tools (what the orchestrator calls; security invoker, so RLS applies to the signed-in user):
--   mm_llm_search_docs, mm_llm_search_docs_vec, mm_llm_search_records, mm_llm_position_history, mm_llm_outage_scope,
--   mm_llm_overdue_actions, mm_llm_bonvoy, mm_llm_pi_daily, mm_llm_pi_values,
--   mm_llm_downtime, mm_llm_downtime_summary, mm_llm_repeat_stops, mm_llm_rcfa_status, mm_llm_position_life, mm_llm_production,
--   mm_llm_documents, mm_llm_bus_day (step 05; the last two feed the Vendor Reports and Daily pages)
--
-- Asking: llm.query_access (who may ask, per org, with a daily limit) and llm.answers (every answer with its tool
-- trace; readable by signed-in users who can see the org). Questions go through the mm-llm-ask edge function.

create schema if not exists llm;
grant usage on schema llm to authenticated, service_role;

do $$ begin
  if exists (select 1 from pg_available_extensions where name = 'vector') then
    create extension if not exists vector with schema extensions;
  end if;
end $$;

create table if not exists llm.equipment (
  org_id uuid not null references public.orgs(id) on delete cascade,
  asset_no text not null, name text not null, section text, kind text, position_id text, parent_asset text,
  primary key (org_id, asset_no));
create index if not exists equipment_name_idx on llm.equipment (org_id, lower(name));

create table if not exists llm.pi_tags (
  org_id uuid not null references public.orgs(id) on delete cascade,
  tag text not null, description text, units text, asset_no text, position_id text, section text,
  primary key (org_id, tag));

create table if not exists llm.outages (
  org_id uuid not null references public.orgs(id) on delete cascade,
  outage_id text not null, kind text, starts_at timestamptz, ends_at timestamptz, note text,
  primary key (org_id, outage_id));

create table if not exists llm.bus_items (
  org_id uuid not null references public.orgs(id) on delete cascade,
  sheet_date date not null, line int not null, issue_key text not null,
  area text, equipment text, asset_no text, position_id text, issue text, action text, owner text, status text,
  days_open int, wo_no text, source_file text,
  primary key (org_id, sheet_date, line));
create index if not exists bus_items_issue_idx on llm.bus_items (org_id, issue_key);
create index if not exists bus_items_asset_idx on llm.bus_items (org_id, asset_no);

create table if not exists llm.work_orders (
  org_id uuid not null references public.orgs(id) on delete cascade,
  wo_no text not null, wo_type text, description text, asset_no text, asset text, position_id text, section text,
  priority int, status int, status_text text, requested date, planned_start date, completed date,
  originator text, assigned_to text, craft text, est_hours numeric, act_hours numeric, outage text, parts_status text,
  notes text, as_of date, source_file text,
  primary key (org_id, wo_no));
create index if not exists work_orders_asset_idx on llm.work_orders (org_id, asset_no);
create index if not exists work_orders_outage_idx on llm.work_orders (org_id, outage);

create table if not exists llm.actions (
  org_id uuid not null references public.orgs(id) on delete cascade,
  task_id text not null, title text, bucket text, progress text, priority text, assigned_to text, created_by text,
  created date, started date, due date, completed date, late boolean, labels text, description text,
  asset_no text, position_id text, as_of date, source_file text,
  primary key (org_id, task_id));

create table if not exists llm.rcfa (
  org_id uuid not null references public.orgs(id) on delete cascade,
  rcfa_id text not null, event_date date, opened date, closed date, status text, title text, area text,
  asset_no text, asset text, position_id text, downtime_h numeric, production_loss text, category text,
  root_cause text, contributing text, lead text, action_ids text[], source_file text,
  primary key (org_id, rcfa_id));

create table if not exists llm.bonvoy (
  org_id uuid not null references public.orgs(id) on delete cascade,
  period date not null, tag text not null, report_date date, description text, area text, asset_no text, asset text,
  position_id text, units text, grade text, mean double precision, std double precision, low double precision,
  high double precision, min double precision, max double precision, hours_outside int, first_outside text,
  last_outside text, direction text, source_file text,
  primary key (org_id, period, tag));
create index if not exists bonvoy_asset_idx on llm.bonvoy (org_id, asset_no, period);
-- The daily Bonvoy Report (step 07): flagged trends from the Pi historian, written by MM LLM (mocked for the demo).
create table if not exists llm.bonvoy_reports (
  org_id uuid not null references public.orgs(id) on delete cascade,
  day date not null, report_date date, headline text, summary text, flagged int, items jsonb, watch jsonb,
  generated_by text, model text, source_file text,
  primary key (org_id, day));
-- Where a Pi tag's values come from (step 07)
alter table llm.pi_tags add column if not exists source text;          -- engine | derived | condition (Sim Mill), null for others

create table if not exists llm.pi_series (
  org_id uuid not null references public.orgs(id) on delete cascade,
  tag text not null, resolution char(1) not null check (resolution in ('h', 'm')),
  t0 timestamptz not null,                 -- first value's time; value i is at t0 + (i-1) * step_s
  step_s int not null, vals double precision[] not null,
  primary key (org_id, tag, resolution, t0));

create table if not exists llm.documents (
  org_id uuid not null references public.orgs(id) on delete cascade,
  doc_id text not null, kind text, vendor text, doc_date date, title text, file_path text, mime text,
  positions text[] not null default '{}', assets text[] not null default '{}', pages int,
  text_source text check (text_source in ('text', 'ocr', 'docx', 'csv')), imported_at timestamptz default now(),
  primary key (org_id, doc_id));

create table if not exists llm.doc_chunks (
  org_id uuid not null, doc_id text not null, chunk_no int not null, page int, content text not null,
  positions text[] not null default '{}',
  fts tsvector generated always as (to_tsvector('english', content)) stored,
  embed_model text,
  primary key (org_id, doc_id, chunk_no),
  foreign key (org_id, doc_id) references llm.documents (org_id, doc_id) on delete cascade);
create index if not exists doc_chunks_fts_idx on llm.doc_chunks using gin (fts);
do $$ begin
  if exists (select 1 from pg_extension where extname = 'vector') then
    execute 'alter table llm.doc_chunks add column if not exists embedding extensions.vector(384)';
  end if;
end $$;

create table if not exists llm.ingest_files (
  org_id uuid not null references public.orgs(id) on delete cascade,
  source_file text not null, kind text, rows int, imported_at timestamptz not null default now(),
  primary key (org_id, source_file));

-- Step 05 (Sim Mill): downtime events, daily production and position life, batched so summaries are one query away.
create table if not exists llm.downtime (
  org_id uuid not null references public.orgs(id) on delete cascade,
  event_id text not null, starts_at timestamptz not null, ends_at timestamptz not null, minutes numeric not null,
  kind text not null check (kind in ('planned', 'unplanned', 'break', 'slowdown')),
  area text, equipment text, asset_no text, position_id text, cause text, grade text, crew text, wo_no text, rcfa_id text,
  comment text, source_file text,
  primary key (org_id, event_id));
alter table llm.downtime add column if not exists report_id text;   -- step 09: the Shift Report it came from
create index if not exists downtime_time_idx on llm.downtime (org_id, starts_at);
create index if not exists downtime_asset_idx on llm.downtime (org_id, asset_no);

create table if not exists llm.production_daily (
  org_id uuid not null references public.orgs(id) on delete cascade,
  day date not null, tons numeric, uptime_pct numeric, breaks int, break_min numeric, unplanned_min numeric, planned_min numeric,
  slowdown_min numeric, avg_speed numeric, grade_hours text, steam_per_t numeric, kwh_per_t numeric, reel_moist numeric,
  crew_day text, crew_night text, source_file text,
  primary key (org_id, day));

create table if not exists llm.position_runs (
  org_id uuid not null references public.orgs(id) on delete cascade,
  position_id text not null, installed date not null, position_name text, removed date, days int, target_days int,
  reason text, condition text, vendor text, style text, serial text, comment text, source_file text,
  primary key (org_id, position_id, installed));

-- Public demo organizations (llm.public_orgs; e.g. Demo Mill, all fictional data): anyone, signed in or not, can read their MM LLM
-- rows and files. Set with  select public.mm_llm_set_public('Demo Mill', true);  in the SQL editor.
-- The list itself is public (it only names the demo orgs), so the lookup below needs no elevated rights.
create table if not exists llm.public_orgs (
  org_id uuid primary key references public.orgs(id) on delete cascade, name text not null,
  created_at timestamptz not null default now());
alter table llm.public_orgs enable row level security;
drop policy if exists public_orgs_read on llm.public_orgs;
create policy public_orgs_read on llm.public_orgs for select to anon, authenticated using (true);
revoke all on llm.public_orgs from anon, authenticated;
grant select on llm.public_orgs to anon, authenticated;
grant all on llm.public_orgs to service_role;
grant usage on schema llm to anon;
grant usage on schema private to anon;

create or replace function private.llm_is_public(p_org uuid) returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from llm.public_orgs where org_id = p_org);
$$;
create or replace function private.llm_is_public_path(p_org text) returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from llm.public_orgs where org_id::text = p_org);
$$;
revoke execute on function private.llm_is_public(uuid) from public;
revoke execute on function private.llm_is_public_path(text) from public;
grant execute on function private.llm_is_public(uuid) to anon, authenticated;
grant execute on function private.llm_is_public_path(text) to anon, authenticated;

-- Read access: members of the org, or anyone for a public demo org. No writes from the API.
do $$ declare t text; begin
  foreach t in array array['equipment','pi_tags','outages','bus_items','work_orders','actions','rcfa','bonvoy','pi_series',
                           'documents','doc_chunks','ingest_files','downtime','production_daily','position_runs','bonvoy_reports'] loop
    execute format('alter table llm.%I enable row level security', t);
    execute format('drop policy if exists %I on llm.%I', t || '_read', t);
    execute format('drop policy if exists %I on llm.%I', t || '_public_read', t);
    execute format('create policy %I on llm.%I for select to authenticated using (private.has_org_role(org_id) or private.llm_is_public(org_id))', t || '_read', t);
    execute format('create policy %I on llm.%I for select to anon using (private.llm_is_public(org_id))', t || '_public_read', t);
    execute format('revoke all on llm.%I from anon, authenticated', t);
    execute format('grant select on llm.%I to anon, authenticated', t);
    execute format('grant all on llm.%I to service_role', t);
  end loop;
end $$;
grant usage on schema llm to anon;

-- SQL editor only: make an org's MM LLM data public (or private again).
create or replace function public.mm_llm_set_public(p_org_name text, p_public boolean default true)
returns text language plpgsql security definer set search_path = '' as $$
declare o uuid;
begin
  select id into o from public.orgs where name = p_org_name;
  if o is null then raise exception 'No organization named %', p_org_name; end if;
  if p_public then insert into llm.public_orgs (org_id, name) values (o, p_org_name) on conflict (org_id) do update set name = excluded.name;
  else delete from llm.public_orgs where org_id = o; end if;
  return format('%s MM LLM data is now %s', p_org_name, case when p_public then 'public' else 'members only' end);
end $$;
revoke execute on function public.mm_llm_set_public(text, boolean) from public, anon, authenticated;

-- The public demo org the MM LLM page loads when nobody is signed in (or the signed-in org has no data yet).
create or replace function public.mm_llm_public_org() returns table (id uuid, name text)
language sql stable security invoker set search_path = '' as $$
  select p.org_id, p.name from llm.public_orgs p order by p.created_at;   -- every public demo org, the first published first (step 05: was limit 1)
$$;
revoke execute on function public.mm_llm_public_org() from public;
grant execute on function public.mm_llm_public_org() to anon, authenticated;

-- Original files of a public demo org: readable by anyone (bucket mm-files, folder <org>/llm/).
drop policy if exists mm_llm_files_public_read on storage.objects;
create policy mm_llm_files_public_read on storage.objects for select to anon, authenticated
  using (bucket_id = 'mm-files' and (storage.foldername(name))[2] = 'llm' and private.llm_is_public_path((storage.foldername(name))[1]));


-- ───────────────────────── Ingest (token-guarded) ─────────────────────────

create table if not exists private.llm_ingest_tokens (
  token_hash text primary key, org_id uuid not null references public.orgs(id) on delete cascade,
  expires_at timestamptz not null, created_at timestamptz not null default now());
revoke all on private.llm_ingest_tokens from public, anon, authenticated;
create index if not exists llm_ingest_tokens_org_idx on private.llm_ingest_tokens (org_id);

-- SQL editor only. Returns the token once; only its hash is kept.
create or replace function public.mm_llm_new_ingest_token(p_org_name text, p_hours int default 6)
returns text language plpgsql security definer set search_path = '' as $$
declare o uuid; tok text;
begin
  insert into public.orgs (name) values (p_org_name) on conflict (name) do nothing;
  select id into o from public.orgs where name = p_org_name;
  tok := encode(extensions.gen_random_bytes(32), 'hex');
  insert into private.llm_ingest_tokens (token_hash, org_id, expires_at)
  values (encode(extensions.digest(tok, 'sha256'), 'hex'), o, now() + make_interval(hours => p_hours));
  return tok;
end $$;
revoke execute on function public.mm_llm_new_ingest_token(text, int) from public, anon, authenticated;

create or replace function private.llm_token_org(p_token text) returns uuid
language sql stable security definer set search_path = '' as $$
  select org_id from private.llm_ingest_tokens
  where token_hash = encode(extensions.digest(coalesce(p_token, ''), 'sha256'), 'hex') and expires_at > now();
$$;
revoke execute on function private.llm_token_org(text) from public, anon, authenticated;

-- For the ingest edge function (service role only): which org a token belongs to.
create or replace function public.mm_llm_token_org(p_token text) returns uuid
language sql stable security definer set search_path = '' as $$ select private.llm_token_org(p_token) $$;
revoke execute on function public.mm_llm_token_org(text) from public, anon, authenticated;
grant execute on function public.mm_llm_token_org(text) to service_role;

-- p_mode 'upsert' (default) inserts or replaces rows by primary key; 'reset' first deletes the org's rows in
-- p_table (p_rows may then be '[]'). org_id always comes from the token, never from the rows.
-- Step 05: p_table 'records:<tool>' loads Machine Manager records (mm_records) for a demo org from the same token:
-- rows are [{ id, data }]; only the tools in the list below; 'reset' first removes that tool's records for the org.
create or replace function public.mm_llm_ingest(p_token text, p_table text, p_rows jsonb, p_mode text default 'upsert')
returns int language plpgsql security definer set search_path = '' as $$
declare o uuid; n int; cols text; keys text; upd text; v_tool text;
begin
  o := private.llm_token_org(p_token);
  if o is null then raise exception 'invalid or expired ingest token' using errcode = '28000'; end if;
  if jsonb_typeof(p_rows) <> 'array' then raise exception 'p_rows must be an array' using errcode = '22023'; end if;
  if jsonb_array_length(p_rows) > 5000 then raise exception 'at most 5000 rows per call' using errcode = '22023'; end if;
  if p_table like 'records:%' then
    v_tool := substr(p_table, 9);
    if v_tool not in ('mymachine', 'outages', 'consumables', 'task-packages') then raise exception 'records for % can''t be loaded', v_tool using errcode = '22023'; end if;
    if p_mode = 'reset' then delete from public.mm_records r where r.org_id = o and r.tool = v_tool; end if;
    insert into public.mm_records as r (org_id, tool, id, data, deleted)
    select o, v_tool, x->>'id', coalesce(x->'data', '{}'::jsonb), false from jsonb_array_elements(p_rows) x
    where jsonb_typeof(x->'id') = 'string'
    on conflict (org_id, tool, id) do update set data = excluded.data, deleted = false;
    get diagnostics n = row_count;
    return n;
  end if;
  if p_table not in ('equipment','pi_tags','outages','bus_items','work_orders','actions','rcfa','bonvoy','pi_series',
                     'documents','doc_chunks','ingest_files','downtime','production_daily','position_runs','bonvoy_reports',
                     'report_types','reports') then
    raise exception 'unknown table %', p_table using errcode = '22023';
  end if;
  if p_mode = 'reset' then
    execute format('delete from llm.%I where org_id = $1', p_table) using o;
    if p_table = 'reports' then   -- step 09: what was extracted from the reports goes with them
      delete from llm.downtime d where d.org_id = o and d.report_id is not null;
      delete from llm.production_daily p where p.org_id = o and p.report_id is not null;
    end if;
  end if;
  if jsonb_array_length(p_rows) = 0 then return 0; end if;
  select string_agg(quote_ident(a.attname), ', ' order by a.attnum),
         string_agg(case when a.attname <> 'org_id' and not k.is_key then format('%1$I = excluded.%1$I', a.attname) end, ', ' order by a.attnum)
    into cols, upd
  from pg_attribute a
  join lateral (select exists (select 1 from pg_index i where i.indrelid = a.attrelid and i.indisprimary and a.attnum = any(i.indkey)) as is_key) k on true
  where a.attrelid = format('llm.%I', p_table)::regclass and a.attnum > 0 and not a.attisdropped and a.attgenerated = ''
    and (a.attname = 'org_id' or (jsonb_array_length(p_rows) > 0 and p_rows->0 ? a.attname));   -- only columns the rows carry (defaults apply to the rest)
  select string_agg(quote_ident(a.attname), ', ') into keys
  from pg_index i join pg_attribute a on a.attrelid = i.indrelid and a.attnum = any(i.indkey)
  where i.indrelid = format('llm.%I', p_table)::regclass and i.indisprimary;
  execute format(
    'insert into llm.%1$I (%2$s) select %2$s from jsonb_populate_recordset(null::llm.%1$I, (select jsonb_agg(r || jsonb_build_object(''org_id'', $1)) from jsonb_array_elements($2) r)) ' ||
    'on conflict (%3$s) do %4$s', p_table, cols, keys, case when upd is null then 'nothing' else 'update set ' || upd end)
  using o, p_rows;
  get diagnostics n = row_count;
  return n;
end $$;
-- Not callable from the web API: imports reach it through the mm-llm-ingest edge function (service role),
-- which checks the token first. The token is still checked here too.
revoke execute on function public.mm_llm_ingest(text, text, jsonb, text) from public, anon, authenticated;
grant execute on function public.mm_llm_ingest(text, text, jsonb, text) to service_role;

-- For the embed step of the ingest edge function (service role only).
create or replace function public.mm_llm_chunks_to_embed(p_org uuid, p_limit int default 50)
returns table (doc_id text, chunk_no int, content text) language sql stable security definer set search_path = '' as $$
  select c.doc_id, c.chunk_no, c.content from llm.doc_chunks c
  where c.org_id = p_org and c.embed_model is null order by c.doc_id, c.chunk_no limit p_limit;
$$;
revoke execute on function public.mm_llm_chunks_to_embed(uuid, int) from public, anon, authenticated;
grant execute on function public.mm_llm_chunks_to_embed(uuid, int) to service_role;

do $$ begin
  if exists (select 1 from pg_extension where extname = 'vector') then
    execute $f$
      create or replace function public.mm_llm_set_embeddings(p_org uuid, p_model text, p_rows jsonb)
      returns int language plpgsql security definer set search_path = '' as $b$
      declare n int;
      begin
        update llm.doc_chunks c set embedding = (r->>'embedding')::extensions.vector, embed_model = p_model
        from jsonb_array_elements(p_rows) r
        where c.org_id = p_org and c.doc_id = r->>'doc_id' and c.chunk_no = (r->>'chunk_no')::int;
        get diagnostics n = row_count; return n;
      end $b$;
      revoke execute on function public.mm_llm_set_embeddings(uuid, text, jsonb) from public, anon, authenticated;
      grant execute on function public.mm_llm_set_embeddings(uuid, text, jsonb) to service_role;
    $f$;
  end if;
end $$;


-- ───────────────────────── Tools ─────────────────────────
-- Read-only, security invoker: RLS decides what they return (members' orgs, plus public demo orgs for anyone).

-- Full-text search over documents. Positions narrow it to chunks tagged with any of them.
create or replace function public.mm_llm_search_docs(p_org uuid, p_query text, p_limit int default 8, p_positions text[] default null)
returns table (doc_id text, title text, kind text, vendor text, doc_date date, page int, chunk_no int, snippet text, rank real)
language sql stable security invoker set search_path = '' as $$
  -- All words first; if nothing has all of them, any of them (best matches first), so long questions still find something.
  with q as (select pg_catalog.websearch_to_tsquery('english', p_query) qa),
  q2 as (select qa, coalesce(pg_catalog.to_tsquery('english', nullif(pg_catalog.replace(qa::text, ' & ', ' | '), '')), qa) qo from q),
  hits as (
    select c.org_id, c.doc_id, c.page, c.chunk_no, c.content, c.fts, q2.qa as q from llm.doc_chunks c, q2
    where c.org_id = p_org and c.fts @@ q2.qa and (p_positions is null or c.positions && p_positions)),
  anyhits as (
    select c.org_id, c.doc_id, c.page, c.chunk_no, c.content, c.fts, q2.qo as q from llm.doc_chunks c, q2
    where not exists (select 1 from hits) and c.org_id = p_org and c.fts @@ q2.qo and (p_positions is null or c.positions && p_positions)),
  m as (select * from hits union all select * from anyhits)
  select d.doc_id, d.title, d.kind, d.vendor, d.doc_date, m.page, m.chunk_no,
         pg_catalog.ts_headline('english', m.content, m.q, 'MaxWords=45, MinWords=20'), pg_catalog.ts_rank(m.fts, m.q)
  from m join llm.documents d on d.org_id = m.org_id and d.doc_id = m.doc_id
  order by pg_catalog.ts_rank(m.fts, m.q) desc, d.doc_date desc limit least(p_limit, 50);
$$;

do $$ begin
  if exists (select 1 from pg_extension where extname = 'vector') then
    execute $f$
      create or replace function public.mm_llm_search_docs_vec(p_org uuid, p_embedding extensions.vector, p_limit int default 8)
      returns table (doc_id text, title text, kind text, doc_date date, page int, chunk_no int, content text, distance double precision)
      language sql stable security invoker set search_path = '' as $b$
        select d.doc_id, d.title, d.kind, d.doc_date, c.page, c.chunk_no, c.content,
               extensions.cosine_distance(c.embedding, p_embedding)
        from llm.doc_chunks c join llm.documents d using (org_id, doc_id)
        where c.org_id = p_org and c.embedding is not null
        order by extensions.cosine_distance(c.embedding, p_embedding) limit least(p_limit, 50);
      $b$;
      grant execute on function public.mm_llm_search_docs_vec(uuid, extensions.vector, int) to anon, authenticated;
    $f$;
  end if;
end $$;

-- Everything known about a position or asset, newest first. p_term matches a My Machine position id,
-- a JDE asset number, or an asset name (exact, case-insensitive), e.g. 'p2-felt-top', 'Dryer can 27'.
create or replace function public.mm_llm_position_history(p_org uuid, p_term text, p_from date default null, p_to date default null)
returns table (source text, day date, ref text, summary text, status text)
language sql stable security invoker set search_path = '' as $$
  with a as (
    select e.asset_no, e.position_id from llm.equipment e
    where e.org_id = p_org and (lower(e.name) = lower(p_term) or e.asset_no = p_term or e.position_id = p_term)
  ), ev as (
    select 'BUS'::text, min(b.sheet_date), max(b.issue_key), max(b.issue) || ' — ' || (array_agg(b.action order by b.sheet_date desc))[1],
           (array_agg(b.status order by b.sheet_date desc))[1] || ' (' || count(*) || ' days on sheet)'
      from llm.bus_items b where b.org_id = p_org and b.asset_no in (select asset_no from a) group by b.issue_key
    union all
    select 'WO', w.requested, w.wo_no, w.description || coalesce(' [' || nullif(w.outage, '') || ']', '') || coalesce(' — ' || w.notes, ''), w.status || ' ' || w.status_text
      from llm.work_orders w where w.org_id = p_org and w.asset_no in (select asset_no from a)
    union all
    select 'Action', t.created, t.task_id, t.title, t.progress || case when t.late then ' (late)' else '' end || ', due ' || t.due
      from llm.actions t where t.org_id = p_org and t.asset_no in (select asset_no from a)
    union all
    select 'RCFA', r.event_date, r.rcfa_id, r.title || ' — ' || r.root_cause, r.status
      from llm.rcfa r where r.org_id = p_org and r.asset_no in (select asset_no from a)
    union all
    select 'Bonvoy', v.period, v.tag, v.description || ': ' || v.direction || ', max ' || v.max || ' ' || v.units || ' vs limit ' ||
           case when v.direction = 'High' then v.high else v.low end || ' (' || v.hours_outside || ' h)', null
      from llm.bonvoy v where v.org_id = p_org and v.asset_no in (select asset_no from a)
    union all
    select 'Document', d.doc_date, d.doc_id, d.title, d.kind
      from llm.documents d where d.org_id = p_org
        and (d.positions && array(select position_id from a where position_id is not null) or d.assets && array(select asset_no from a))
    union all
    select 'Downtime', (x.starts_at at time zone 'America/New_York')::date, x.event_id,
           x.cause || ': ' || x.minutes || ' min' || coalesce(' — ' || x.comment, ''), x.kind || coalesce(' / ' || x.rcfa_id, '')
      from llm.downtime x where x.org_id = p_org and x.kind <> 'break'
        and (x.asset_no in (select asset_no from a) or x.position_id in (select position_id from a where position_id is not null))
    union all
    select 'Run', r.installed, r.serial, r.vendor || ' ' || coalesce(r.style, '') || ': ' || coalesce(r.days, 0) || ' days (target ' ||
           coalesce(r.target_days, 0) || ')' || coalesce(' — ' || nullif(r.comment, ''), ''),
           case when r.removed is null then 'running' else r.reason || ', ' || r.condition end
      from llm.position_runs r where r.org_id = p_org and r.position_id in (select position_id from a where position_id is not null)
  )
  select * from ev e(source, day, ref, summary, status)
  where (p_from is null or e.day >= p_from) and (p_to is null or e.day <= p_to)
  order by e.day desc nulls last limit 400;
$$;

-- Full-text search across the structured records (BUS lines, WOs, actions, RCFAs), for things that aren't
-- tagged to a position or when only words are known ("Ridgeway plates order").
create or replace function public.mm_llm_search_records(p_org uuid, p_query text, p_limit int default 20)
returns table (source text, day date, ref text, summary text, status text, rank real)
language sql stable security invoker set search_path = '' as $$
  with q as (select pg_catalog.websearch_to_tsquery('english', p_query) q),
  r as (
    select 'BUS'::text as source, max(b.sheet_date) as day, b.issue_key as ref,
           max(b.equipment) || ': ' || max(b.issue) || ' — ' || (array_agg(b.action order by b.sheet_date desc))[1] as summary,
           (array_agg(b.status order by b.sheet_date desc))[1] as status
      from llm.bus_items b where b.org_id = p_org group by b.issue_key
    union all
    select 'WO', w.requested, w.wo_no, w.asset || ': ' || w.description || coalesce(' — ' || w.notes, ''), w.status || ' ' || w.status_text
      from llm.work_orders w where w.org_id = p_org
    union all
    select 'Action', t.created, t.task_id, t.title || coalesce(' (' || t.description || ')', ''),
           t.progress || case when t.late then ' (late)' else '' end || ', due ' || t.due
      from llm.actions t where t.org_id = p_org
    union all
    select 'RCFA', x.event_date, x.rcfa_id, x.title || ' — ' || x.root_cause || ' / ' || x.contributing, x.status
      from llm.rcfa x where x.org_id = p_org
  )
  select r.source, r.day, r.ref, r.summary, r.status, pg_catalog.ts_rank(pg_catalog.to_tsvector('english', r.summary), q.q)
  from r, q where pg_catalog.to_tsvector('english', r.summary) @@ q.q
  order by 6 desc, r.day desc limit least(p_limit, 100);
$$;

-- What an org has loaded: row counts per source and the data's date range.
create or replace function public.mm_llm_summary(p_org uuid)
returns table (source text, n bigint, first_day date, last_day date)
language sql stable security invoker set search_path = '' as $$
  select 'BUS lines', count(*), min(sheet_date), max(sheet_date) from llm.bus_items where org_id = p_org
  union all select 'Work orders', count(*), min(requested), max(requested) from llm.work_orders where org_id = p_org
  union all select 'Actions', count(*), min(created), max(created) from llm.actions where org_id = p_org
  union all select 'RCFAs', count(*), min(event_date), max(event_date) from llm.rcfa where org_id = p_org
  union all select 'Bonvoy exceptions', count(*), min(period), max(period) from llm.bonvoy where org_id = p_org
  union all select 'Bonvoy reports', count(*), min(day), max(day) from llm.bonvoy_reports where org_id = p_org
  union all select 'Pi tags', count(distinct tag), min((t0 at time zone 'America/New_York')::date), max((t0 at time zone 'America/New_York')::date) from llm.pi_series where org_id = p_org
  union all select 'Documents', count(*), min(doc_date), max(doc_date) from llm.documents where org_id = p_org
  union all select 'Downtime events', count(*), min((starts_at at time zone 'America/New_York')::date), max((starts_at at time zone 'America/New_York')::date) from llm.downtime where org_id = p_org
  union all select 'Production days', count(*), min(day), max(day) from llm.production_daily where org_id = p_org
  union all select 'Position runs', count(*), min(installed), max(coalesce(removed, installed)) from llm.position_runs where org_id = p_org;
$$;

-- What is planned for an outage: its WOs (with parts status) and when it is.
create or replace function public.mm_llm_outage_scope(p_org uuid, p_outage text)
returns table (wo_no text, description text, asset text, position_id text, wo_type text, priority int, status int,
               status_text text, parts_status text, est_hours numeric, notes text)
language sql stable security invoker set search_path = '' as $$
  select w.wo_no, w.description, w.asset, w.position_id, w.wo_type, w.priority, w.status, w.status_text, w.parts_status,
         w.est_hours, w.notes
  from llm.work_orders w
  where w.org_id = p_org and (w.outage = p_outage or 'OUT-' || w.outage = p_outage)
  order by (w.parts_status = 'Not reserved') desc, w.priority, w.wo_no;
$$;

-- Actions not completed and past due as of a date (default: the latest export).
create or replace function public.mm_llm_overdue_actions(p_org uuid, p_as_of date default null)
returns table (task_id text, title text, bucket text, assigned_to text, due date, days_late int, progress text, description text)
language sql stable security invoker set search_path = '' as $$
  select t.task_id, t.title, t.bucket, t.assigned_to, t.due,
         (coalesce(p_as_of, t.as_of) - t.due), t.progress, t.description
  from llm.actions t
  where t.org_id = p_org and t.progress <> 'Completed' and t.due < coalesce(p_as_of, t.as_of)
  order by t.due;
$$;

-- Bonvoy exceptions for a tag, asset or position (or everything when p_term is null) in a date range.
create or replace function public.mm_llm_bonvoy(p_org uuid, p_term text default null, p_from date default null, p_to date default null)
returns table (period date, tag text, asset text, direction text, max double precision, high double precision,
               low double precision, hours_outside int, grade text)
language sql stable security invoker set search_path = '' as $$
  select v.period, v.tag, v.asset, v.direction, v.max, v.high, v.low, v.hours_outside, v.grade
  from llm.bonvoy v
  where v.org_id = p_org and (p_from is null or v.period >= p_from) and (p_to is null or v.period <= p_to)
    and (p_term is null or v.tag = p_term or v.asset_no = p_term or lower(v.asset) = lower(p_term) or v.position_id = p_term)
  order by v.period, v.tag limit 1000;
$$;

-- Stored Pi values for a tag between two times (minute data where it exists, else hourly). The live (or mock)
-- PI Web API is the full source; this is the cheap copy the orchestrator can always reach.
create or replace function public.mm_llm_pi_values(p_org uuid, p_tag text, p_from timestamptz, p_to timestamptz)
returns table (ts timestamptz, value double precision, resolution char(1))
language sql stable security invoker set search_path = '' as $$
  with v as (
    select s.t0 + make_interval(secs => (u.i - 1) * s.step_s) as ts, u.val, s.resolution
    from llm.pi_series s, unnest(s.vals) with ordinality u(val, i)
    where s.org_id = p_org and s.tag = p_tag and s.t0 <= p_to and s.t0 + make_interval(secs => 86400) >= p_from
  )
  select v.ts, v.val, v.resolution from v
  where v.ts between p_from and p_to
    and (v.resolution = 'm' or not exists (select 1 from v m where m.resolution = 'm'
                                           and m.ts >= v.ts and m.ts < v.ts + interval '1 hour'))
  order by v.ts limit 20000;
$$;

-- Daily summary of a Pi tag by mill-local day (hourly values).
create or replace function public.mm_llm_pi_daily(p_org uuid, p_tag text, p_from date, p_to date)
returns table (day date, avg double precision, min double precision, max double precision, hours int)
language sql stable security invoker set search_path = '' as $$
  select (x.ts at time zone 'America/New_York')::date, avg(x.val), min(x.val), max(x.val), count(*)::int
  from (select s.t0 + make_interval(secs => (u.i - 1) * s.step_s) as ts, u.val
        from llm.pi_series s, unnest(s.vals) with ordinality u(val, i)
        where s.org_id = p_org and s.tag = p_tag and s.resolution = 'h'
          and s.t0 between (p_from - 1)::timestamptz and (p_to + 2)::timestamptz) x
  where x.val is not null and (x.ts at time zone 'America/New_York')::date between p_from and p_to
  group by 1 order by 1;
$$;

-- ───────────────────────── Step 05: downtime, RCFA status, position life, production ─────────────────────────
-- Downtime events in a date range (mill-local days), optionally one kind ('planned', 'unplanned', 'break', 'slowdown').
-- (step 09 added report_id: drop first, since the return type changed)
drop function if exists public.mm_llm_downtime(uuid, date, date, text);
create or replace function public.mm_llm_downtime(p_org uuid, p_from date, p_to date, p_kind text default null)
returns table (event_id text, starts_at timestamptz, minutes numeric, kind text, area text, equipment text, position_id text,
               cause text, grade text, crew text, wo_no text, rcfa_id text, comment text, report_id text)
language sql stable security invoker set search_path = '' as $$
  select d.event_id, d.starts_at, d.minutes, d.kind, d.area, d.equipment, d.position_id, d.cause, d.grade, d.crew, d.wo_no, d.rcfa_id, d.comment, d.report_id
  from llm.downtime d
  where d.org_id = p_org and (d.starts_at at time zone 'America/New_York')::date between p_from and p_to
    and (p_kind is null or d.kind = p_kind)
  order by d.starts_at limit 2000;
$$;

-- Downtime batched: minutes and events per group, a Pareto share of the group's kind, and MTBF / MTTR for failures.
-- p_group: 'area' (default), 'equipment', 'cause', 'crew', 'grade', 'month', 'week', 'kind'. Breaks and slowdowns count
-- as their own kinds; MTBF is the period's running hours / unplanned events.
create or replace function public.mm_llm_downtime_summary(p_org uuid, p_from date, p_to date, p_group text default 'area')
returns table (grp text, kind text, events bigint, minutes numeric, hours numeric, share_pct numeric, mtbf_h numeric, mttr_h numeric)
language sql stable security invoker set search_path = '' as $$
  with d as (
    select x.*, case p_group when 'equipment' then x.equipment when 'cause' then x.cause when 'crew' then x.crew when 'grade' then x.grade
                  when 'month' then to_char(x.starts_at at time zone 'America/New_York', 'YYYY-MM')
                  when 'week' then to_char(date_trunc('week', x.starts_at at time zone 'America/New_York'), 'YYYY-MM-DD')
                  when 'kind' then x.kind else x.area end as g
    from llm.downtime x
    where x.org_id = p_org and (x.starts_at at time zone 'America/New_York')::date between p_from and p_to
  ), span as (
    select greatest(1, (p_to - p_from + 1) * 24 - coalesce((select sum(minutes) from d where kind = 'planned'), 0) / 60.0) as run_h
  )
  select coalesce(d.g, '(none)'), d.kind, count(*), round(sum(d.minutes), 1), round(sum(d.minutes) / 60, 1),
         round(100 * sum(d.minutes) / nullif(sum(sum(d.minutes)) over (partition by d.kind), 0), 1),
         case when d.kind = 'unplanned' then round((select run_h from span) / count(*), 0) end,
         case when d.kind in ('unplanned', 'break') then round(avg(d.minutes) / 60, 2) end
  from d group by d.g, d.kind
  order by d.kind = 'unplanned' desc, d.kind, sum(d.minutes) desc;
$$;

-- Repeat unplanned stops on the same equipment in a period, and whether any of them has an RCFA: the failures that keep
-- coming back without anyone analysing them.
create or replace function public.mm_llm_repeat_stops(p_org uuid, p_from date, p_to date, p_min_events int default 2)
returns table (equipment text, position_id text, events bigint, hours numeric, first_day date, last_day date, causes text, rcfas text, wo_nos text)
language sql stable security invoker set search_path = '' as $$
  select d.equipment, max(d.position_id), count(*), round(sum(d.minutes) / 60, 1),
         min((d.starts_at at time zone 'America/New_York')::date), max((d.starts_at at time zone 'America/New_York')::date),
         string_agg(distinct d.cause, '; '), coalesce(string_agg(distinct d.rcfa_id, ', '), 'none'), string_agg(distinct d.wo_no, ', ')
  from llm.downtime d
  where d.org_id = p_org and d.kind = 'unplanned' and (d.starts_at at time zone 'America/New_York')::date between p_from and p_to
  group by d.equipment having count(*) >= p_min_events
  order by (count(d.rcfa_id) = 0) desc, sum(d.minutes) desc;
$$;

-- Every RCFA with its downtime and the state of its actions as of a date (default: the actions' latest export).
create or replace function public.mm_llm_rcfa_status(p_org uuid, p_as_of date default null)
returns table (rcfa_id text, event_date date, title text, equipment text, category text, downtime_h numeric, status text,
               actions int, done int, overdue int, next_due date, root_cause text)
language sql stable security invoker set search_path = '' as $$
  select r.rcfa_id, r.event_date, r.title, r.asset, r.category, r.downtime_h, r.status,
         count(a.task_id)::int, count(a.task_id) filter (where a.progress = 'Completed')::int,
         count(a.task_id) filter (where a.progress <> 'Completed' and a.due < coalesce(p_as_of, a.as_of))::int,
         min(a.due) filter (where a.progress <> 'Completed'), r.root_cause
  from llm.rcfa r left join llm.actions a on a.org_id = r.org_id and a.task_id = any(r.action_ids)
  where r.org_id = p_org
  group by r.rcfa_id, r.event_date, r.title, r.asset, r.category, r.downtime_h, r.status, r.root_cause
  order by r.event_date desc;
$$;

-- Position life: every run of a position (or of all positions when p_position is null) with its age against target,
-- the current run's age as of p_as_of, and early removals flagged (not a planned change, or under 75% of target). Covers fabric, felt, plate and roll aging.
create or replace function public.mm_llm_position_life(p_org uuid, p_position text default null, p_as_of date default null)
returns table (position_id text, position_name text, installed date, removed date, days int, target_days int, pct_of_target numeric,
               early boolean, reason text, condition text, vendor text, style text, comment text)
language sql stable security invoker set search_path = '' as $$
  select r.position_id, r.position_name, r.installed, r.removed,
         coalesce(r.days, (coalesce(p_as_of, (select max(x.installed) from llm.position_runs x where x.org_id = p_org), current_date) - r.installed)),
         r.target_days,
         round(100.0 * coalesce(r.days, coalesce(p_as_of, current_date) - r.installed) / nullif(r.target_days, 0), 0),
         r.removed is not null and (r.reason not in ('planned', '') or r.days < 0.75 * r.target_days), r.reason, r.condition, r.vendor, r.style, r.comment
  from llm.position_runs r
  where r.org_id = p_org and (p_position is null or r.position_id = p_position or lower(r.position_name) = lower(p_position))
  order by r.position_id, r.installed desc;
$$;

-- Production by day, week or month: tons, uptime, breaks and minutes lost (p_by: 'day', 'week', 'month').
create or replace function public.mm_llm_production(p_org uuid, p_from date, p_to date, p_by text default 'day')
returns table (period text, days int, tons numeric, tons_per_day numeric, uptime_pct numeric, breaks bigint,
               break_min numeric, unplanned_min numeric, planned_min numeric, slowdown_min numeric, kwh_per_t numeric, steam_per_t numeric)
language sql stable security invoker set search_path = '' as $$
  select case p_by when 'month' then to_char(p.day, 'YYYY-MM') when 'week' then to_char(date_trunc('week', p.day), 'YYYY-MM-DD') else p.day::text end,
         count(*)::int, round(sum(p.tons), 0), round(avg(p.tons), 0), round(avg(p.uptime_pct), 1), sum(p.breaks),
         round(sum(p.break_min), 0), round(sum(p.unplanned_min), 0), round(sum(p.planned_min), 0), round(sum(p.slowdown_min), 0),
         round(avg(p.kwh_per_t), 1), round(avg(p.steam_per_t), 2)
  from llm.production_daily p
  where p.org_id = p_org and p.day between p_from and p_to
  group by 1 order by 1;
$$;

-- Hours run on each grade (step 08), for fair comparisons between grades.
create or replace function public.mm_llm_grade_hours(p_org uuid, p_from date, p_to date)
returns table (grade text, hours numeric, days int, share_pct numeric)
language sql stable security invoker set search_path = '' as $$
  with parts as (
    select p.day, trim(x) as part
    from llm.production_daily p, unnest(string_to_array(coalesce(p.grade_hours, ''), ';')) as x
    where p.org_id = p_org and p.day between p_from and p_to and trim(x) <> ''
  ), g as (
    select regexp_replace(part, '\s+[0-9.]+$', '') as grade, substring(part from '([0-9.]+)$')::numeric as h, day from parts
  )
  select g.grade, round(sum(g.h), 1), count(distinct g.day)::int, round(100 * sum(g.h) / nullif(sum(sum(g.h)) over (), 0), 1)
  from g group by g.grade order by sum(g.h) desc;
$$;

-- Documents of an org (newest first), optionally one kind ('vendor_report', 'rcfa', 'drawing', 'reference'), for the Vendor Reports page.
create or replace function public.mm_llm_documents(p_org uuid, p_kind text default null)
returns table (doc_id text, kind text, vendor text, doc_date date, title text, file_path text, mime text, positions text[], assets text[], pages int)
language sql stable security invoker set search_path = '' as $$
  select d.doc_id, d.kind, d.vendor, d.doc_date, d.title, d.file_path, d.mime, d.positions, d.assets, d.pages
  from llm.documents d where d.org_id = p_org and (p_kind is null or d.kind = p_kind)
  order by d.doc_date desc nulls last, d.doc_id limit 1000;
$$;

-- One BUS sheet: its lines on a day, in sheet order (the Daily page).
create or replace function public.mm_llm_bus_day(p_org uuid, p_day date)
returns table (line int, area text, equipment text, position_id text, issue text, action text, owner text, status text, days_open int, wo_no text)
language sql stable security invoker set search_path = '' as $$
  select b.line, b.area, b.equipment, b.position_id, b.issue, b.action, b.owner, b.status, b.days_open, b.wo_no
  from llm.bus_items b where b.org_id = p_org and b.sheet_date = p_day order by b.line;
$$;

do $$ declare f text; begin
  foreach f in array array['mm_llm_summary(uuid)', 'mm_llm_search_docs(uuid, text, int, text[])', 'mm_llm_search_records(uuid, text, int)', 'mm_llm_position_history(uuid, text, date, date)',
                           'mm_llm_outage_scope(uuid, text)', 'mm_llm_overdue_actions(uuid, date)',
                           'mm_llm_bonvoy(uuid, text, date, date)', 'mm_llm_pi_daily(uuid, text, date, date)',
                           'mm_llm_downtime(uuid, date, date, text)', 'mm_llm_downtime_summary(uuid, date, date, text)', 'mm_llm_repeat_stops(uuid, date, date, int)', 'mm_llm_rcfa_status(uuid, date)', 'mm_llm_position_life(uuid, text, date)', 'mm_llm_production(uuid, date, date, text)', 'mm_llm_grade_hours(uuid, date, date)', 'mm_llm_documents(uuid, text)', 'mm_llm_bus_day(uuid, date)',
                           'mm_llm_pi_values(uuid, text, timestamptz, timestamptz)'] loop
    execute format('revoke execute on function public.%s from public', f);
    execute format('grant execute on function public.%s to anon, authenticated', f);   -- RLS decides what comes back
  end loop;
end $$;


-- ───────────────────────── Asking the assistant ─────────────────────────
-- Two tiers: every signed-in user can read the assistant's saved answers for orgs they can see (members, or a
-- public demo org); only users on llm.query_access can ask new questions (through the mm-llm-ask edge function,
-- which runs the tools as that user and saves the answer). Grant in the SQL editor:
--   select public.mm_llm_grant_query('demodemo@gmail.com', 'Sim Mill', 40);    -- questions per day

create table if not exists llm.query_access (
  user_id uuid not null references auth.users(id) on delete cascade,
  org_id uuid not null references public.orgs(id) on delete cascade,
  daily_limit int not null default 40 check (daily_limit between 0 and 1000),
  created_at timestamptz not null default now(),
  primary key (user_id, org_id));
alter table llm.query_access enable row level security;
drop policy if exists query_access_own on llm.query_access;
create policy query_access_own on llm.query_access for select to authenticated using (user_id = (select auth.uid()));
revoke all on llm.query_access from anon, authenticated;
grant select on llm.query_access to authenticated;
grant all on llm.query_access to service_role;

create table if not exists llm.answers (
  id bigint generated always as identity primary key,
  org_id uuid not null references public.orgs(id) on delete cascade,
  question_id text,                      -- answer-key id (S01-Q1 …) when it was a demo question
  question text not null, answer text, status text not null default 'ok' check (status in ('ok', 'error')),
  tool_trace jsonb not null default '[]'::jsonb, model text, provider text,
  input_tokens int, output_tokens int, ms int,
  asked_by uuid references auth.users(id) on delete set null, created_at timestamptz not null default now());
create index if not exists answers_org_idx on llm.answers (org_id, created_at desc);
create index if not exists answers_q_idx on llm.answers (org_id, question_id, created_at desc);
create index if not exists answers_user_idx on llm.answers (asked_by, created_at);
alter table llm.answers enable row level security;
drop policy if exists answers_read on llm.answers;
create policy answers_read on llm.answers for select to authenticated
  using (private.has_org_role(org_id) or private.llm_is_public(org_id));   -- signed-in only: not anon
revoke all on llm.answers from anon, authenticated;
grant select on llm.answers to authenticated;
grant all on llm.answers to service_role;

-- What the signed-in user may do: ask (and how many questions are left today) for which org.
create or replace function public.mm_llm_my_access()
returns table (org_id uuid, org_name text, daily_limit int, used_today int, can_ask boolean)
language sql stable security invoker set search_path = '' as $$
  select q.org_id, coalesce(p.name, o.name), q.daily_limit,
         (select count(*)::int from llm.answers a where a.asked_by = (select auth.uid()) and a.org_id = q.org_id
            and a.created_at >= date_trunc('day', now() at time zone 'America/New_York') at time zone 'America/New_York'),
         true
  from llm.query_access q
  left join llm.public_orgs p on p.org_id = q.org_id
  left join public.orgs o on o.id = q.org_id
  where q.user_id = (select auth.uid());
$$;
revoke execute on function public.mm_llm_my_access() from public, anon;
grant execute on function public.mm_llm_my_access() to authenticated;

-- SQL editor only.
create or replace function public.mm_llm_grant_query(p_email text, p_org_name text, p_daily_limit int default 40)
returns text language plpgsql security definer set search_path = '' as $$
declare u uuid; o uuid;
begin
  select id into u from auth.users where lower(email) = lower(p_email);
  if u is null then raise exception 'No user with email %', p_email; end if;
  select id into o from public.orgs where name = p_org_name;
  if o is null then raise exception 'No organization named %', p_org_name; end if;
  if p_daily_limit <= 0 then delete from llm.query_access where user_id = u and org_id = o;
    return format('%s can no longer ask about %s', p_email, p_org_name); end if;
  insert into llm.query_access (user_id, org_id, daily_limit) values (u, o, p_daily_limit)
  on conflict (user_id, org_id) do update set daily_limit = excluded.daily_limit;
  return format('%s can ask about %s (%s questions a day)', p_email, p_org_name, p_daily_limit);
end $$;
revoke execute on function public.mm_llm_grant_query(text, text, int) from public, anon, authenticated;

-- Grounding for the orchestrator's prompt: the org's outages, positions and Pi tags.
create or replace function public.mm_llm_context(p_org uuid) returns jsonb
language sql stable security invoker set search_path = '' as $$
  select jsonb_build_object(
    'outages', (select coalesce(jsonb_agg(jsonb_build_object('id', o.outage_id, 'kind', o.kind,
                 'starts', (o.starts_at at time zone 'America/New_York')::date, 'ends', (o.ends_at at time zone 'America/New_York')::date) order by o.starts_at), '[]')
                from llm.outages o where o.org_id = p_org),
    'positions', (select coalesce(jsonb_agg(jsonb_build_object('id', e.position_id, 'name', e.name, 'section', e.section) order by e.section, e.name), '[]')
                  from llm.equipment e where e.org_id = p_org and e.position_id is not null),
    'pi_tags', (select coalesce(jsonb_agg(jsonb_build_object('tag', t.tag, 'description', t.description, 'units', t.units) order by t.tag), '[]')
                from llm.pi_tags t where t.org_id = p_org),
    'data_through', (select max(sheet_date) from llm.bus_items b where b.org_id = p_org));
$$;

-- For the mm-llm-ask edge function only (service role).
create or replace function public.mm_llm_save_answer(p_org uuid, p_question_id text, p_question text, p_answer text, p_status text,
  p_trace jsonb, p_model text, p_provider text, p_in int, p_out int, p_ms int, p_user uuid)
returns bigint language sql security definer set search_path = '' as $$
  insert into llm.answers (org_id, question_id, question, answer, status, tool_trace, model, provider, input_tokens, output_tokens, ms, asked_by)
  values (p_org, p_question_id, p_question, p_answer, p_status, coalesce(p_trace, '[]'::jsonb), p_model, p_provider, p_in, p_out, p_ms, p_user)
  returning id;
$$;
create or replace function public.mm_llm_answers_today() returns int
language sql stable security definer set search_path = '' as $$
  select count(*)::int from llm.answers
  where created_at >= date_trunc('day', now() at time zone 'America/New_York') at time zone 'America/New_York';
$$;
revoke execute on function public.mm_llm_save_answer(uuid, text, text, text, text, jsonb, text, text, int, int, int, uuid) from public, anon, authenticated;
grant execute on function public.mm_llm_save_answer(uuid, text, text, text, text, jsonb, text, text, int, int, int, uuid) to service_role;
revoke execute on function public.mm_llm_answers_today() from public, anon, authenticated;
grant execute on function public.mm_llm_answers_today() to service_role;

-- Reading answers (signed-in only; row-level security on llm.answers applies).
-- Saved answers to the demo questions: the latest good answer per question id.
create or replace function public.mm_llm_saved_answers(p_org uuid)
returns table (id bigint, question_id text, question text, answer text, tool_trace jsonb, model text, provider text, ms int, created_at timestamptz)
language sql stable security invoker set search_path = '' as $$
  select distinct on (a.question_id) a.id, a.question_id, a.question, a.answer, a.tool_trace, a.model, a.provider, a.ms, a.created_at
  from llm.answers a
  where a.org_id = p_org and a.question_id is not null and a.status = 'ok'
  order by a.question_id, a.created_at desc;
$$;
-- The signed-in user's own recent questions.
create or replace function public.mm_llm_my_answers(p_org uuid, p_limit int default 20)
returns table (id bigint, question text, answer text, status text, tool_trace jsonb, model text, ms int, created_at timestamptz)
language sql stable security invoker set search_path = '' as $$
  select a.id, a.question, a.answer, a.status, a.tool_trace, a.model, a.ms, a.created_at
  from llm.answers a
  where a.org_id = p_org and a.asked_by = (select auth.uid())
  order by a.created_at desc limit least(greatest(coalesce(p_limit, 20), 1), 100);
$$;
revoke execute on function public.mm_llm_saved_answers(uuid) from public, anon;
grant execute on function public.mm_llm_saved_answers(uuid) to authenticated, service_role;
revoke execute on function public.mm_llm_my_answers(uuid, int) from public, anon;
grant execute on function public.mm_llm_my_answers(uuid, int) to authenticated;

-- The tools are also run by the edge function's service role (batch runs of the demo questions).
do $$ declare f text; begin
  foreach f in array array['mm_llm_context(uuid)', 'mm_llm_summary(uuid)', 'mm_llm_search_docs(uuid, text, int, text[])', 'mm_llm_search_records(uuid, text, int)',
                           'mm_llm_position_history(uuid, text, date, date)', 'mm_llm_outage_scope(uuid, text)', 'mm_llm_overdue_actions(uuid, date)',
                           'mm_llm_bonvoy(uuid, text, date, date)', 'mm_llm_pi_daily(uuid, text, date, date)',
                           'mm_llm_downtime(uuid, date, date, text)', 'mm_llm_downtime_summary(uuid, date, date, text)', 'mm_llm_repeat_stops(uuid, date, date, int)', 'mm_llm_rcfa_status(uuid, date)', 'mm_llm_position_life(uuid, text, date)', 'mm_llm_production(uuid, date, date, text)', 'mm_llm_grade_hours(uuid, date, date)', 'mm_llm_documents(uuid, text)', 'mm_llm_bus_day(uuid, date)',
                           'mm_llm_pi_values(uuid, text, timestamptz, timestamptz)'] loop
    execute format('revoke execute on function public.%s from public', f);
    execute format('grant execute on function public.%s to anon, authenticated, service_role', f);
  end loop;
end $$;

-- Step 06 (Sim Mill is the demo): signed-out visitors see the public demo org's Machine Manager records, read-only.
-- Only the demo tools, only orgs on llm.public_orgs (the first published, if there are several), and only id / data /
-- version / updated_at: who edited a record stays private. Members still read their own org through mm_records.
create or replace function public.mm_demo_org()
returns table (id uuid, name text)
language sql stable security definer set search_path = '' as $$
  select p.org_id, p.name from llm.public_orgs p order by p.created_at limit 1;
$$;
create or replace function public.mm_demo_records(p_tool text)
returns table (id text, data jsonb, version int, updated_at timestamptz)
language sql stable security definer set search_path = '' as $$
  select r.id, r.data, r.version, r.updated_at
  from public.mm_records r
  where r.org_id = (select p.org_id from llm.public_orgs p order by p.created_at limit 1)
    and r.tool = p_tool and p_tool in ('mymachine', 'outages', 'consumables', 'task-packages')
    and not r.deleted
  order by r.id;
$$;
revoke execute on function public.mm_demo_org() from public;
revoke execute on function public.mm_demo_records(text) from public;
grant execute on function public.mm_demo_org() to anon, authenticated, service_role;
grant execute on function public.mm_demo_records(text) to anon, authenticated, service_role;

-- Step 07 (Bonvoy): the daily Bonvoy Report (flagged trends from the Pi historian, written by MM LLM; mocked for the
-- demo by the generator), and Pi tags linked to My Machine positions with where their values come from.

-- The Bonvoy Reports of an org, newest first (a list for the page's day picker).
create or replace function public.mm_llm_bonvoy_reports(p_org uuid, p_from date default null, p_to date default null)
returns table (day date, report_date date, flagged int, headline text, watch int, generated_by text)
language sql stable security invoker set search_path = '' as $$
  select r.day, r.report_date, r.flagged, r.headline, coalesce(jsonb_array_length(r.watch), 0), r.generated_by
  from llm.bonvoy_reports r
  where r.org_id = p_org and (p_from is null or r.day >= p_from) and (p_to is null or r.day <= p_to)
  order by r.day desc;
$$;
-- One day's Bonvoy Report (the latest when p_day is null).
create or replace function public.mm_llm_bonvoy_report(p_org uuid, p_day date default null)
returns table (day date, report_date date, headline text, summary text, flagged int, items jsonb, watch jsonb, generated_by text, model text)
language sql stable security invoker set search_path = '' as $$
  select r.day, r.report_date, r.headline, r.summary, r.flagged, r.items, r.watch, r.generated_by, r.model
  from llm.bonvoy_reports r
  where r.org_id = p_org and (p_day is null or r.day = p_day)
  order by r.day desc limit 1;
$$;
-- The Pi tags on a My Machine position: latest daily average, Bonvoy flags in the last 14 days, the latest report flagging it.
create or replace function public.mm_llm_position_tags(p_org uuid, p_position text)
returns table (tag text, description text, units text, source text, last_day date, last_avg double precision,
               flags_14d int, last_flag date, last_report date)
language sql stable security invoker set search_path = '' as $$
  with t as (select * from llm.pi_tags where org_id = p_org and position_id = p_position),
       d as (select coalesce((select max(period) from llm.bonvoy where org_id = p_org), current_date) as today)
  select t.tag, t.description, t.units, t.source, d.today,
         (select x.avg from public.mm_llm_pi_daily(p_org, t.tag, d.today, d.today) x),
         (select count(*)::int from llm.bonvoy b where b.org_id = p_org and b.tag = t.tag and b.period > d.today - 14),
         (select max(b.period) from llm.bonvoy b where b.org_id = p_org and b.tag = t.tag),
         (select max(r.day) from llm.bonvoy_reports r where r.org_id = p_org and r.items @> jsonb_build_array(jsonb_build_object('tag', t.tag)))
  from t, d order by t.tag;
$$;
do $$ declare f text; begin
  foreach f in array array['mm_llm_bonvoy_reports(uuid, date, date)', 'mm_llm_bonvoy_report(uuid, date)', 'mm_llm_position_tags(uuid, text)'] loop
    execute format('revoke execute on function public.%s from public', f);
    execute format('grant execute on function public.%s to anon, authenticated, service_role', f);
  end loop;
end $$;

-- ───────────────────────── Step 09: reports and the report lifecycle ─────────────────────────
-- (migrations/09-reports.sql has the why; these are the same statements)
create table if not exists llm.report_types (
  org_id uuid not null references public.orgs(id) on delete cascade,
  type text not null, title text, cadence text check (cadence in ('shift', 'day', 'week', 'outage')),
  required text[] not null default '{}', extract text[] not null default '{}', index_kind text,
  primary key (org_id, type));

create table if not exists llm.reports (
  org_id uuid not null references public.orgs(id) on delete cascade,
  report_id text not null, type text not null, schema_version int not null default 1, machine text,
  period_start timestamptz not null, period_end timestamptz not null, mill_day date not null, shift text, crew text,
  author text, author_role text, source text,
  status text not null default 'ingested' check (status in ('ingested', 'extracted', 'indexed', 'failed')),
  error text, body jsonb not null, text text not null, history jsonb not null default '[]', file_path text,
  positions text[] not null default '{}',
  fts tsvector generated always as (to_tsvector('english', text)) stored,
  ingested_at timestamptz not null default now(), processed_at timestamptz,
  primary key (org_id, report_id));
create index if not exists reports_day_idx on llm.reports (org_id, mill_day, type);
create index if not exists reports_status_idx on llm.reports (org_id, status);
create index if not exists reports_fts_idx on llm.reports using gin (fts);

create table if not exists llm.report_events (
  id bigint generated always as identity primary key,
  org_id uuid not null, report_id text not null, at timestamptz not null default clock_timestamp(),
  from_status text, to_status text not null, detail text,
  foreign key (org_id, report_id) references llm.reports (org_id, report_id) on delete cascade);
alter table llm.report_events add column if not exists id bigint generated always as identity;   -- (early drafts had none)
create index if not exists report_events_idx on llm.report_events (org_id, report_id, id);

alter table llm.downtime add column if not exists report_id text;
alter table llm.production_daily add column if not exists report_id text;
alter table llm.production_daily add column if not exists saleable_tons numeric;
alter table llm.production_daily add column if not exists broke_tons numeric;
alter table llm.production_daily add column if not exists cull_tons numeric;
alter table llm.production_daily add column if not exists off_spec_hours int;
alter table llm.production_daily add column if not exists time_eff numeric;
alter table llm.production_daily add column if not exists prod_eff numeric;
alter table llm.production_daily add column if not exists quality_eff numeric;
alter table llm.production_daily add column if not exists ome_pct numeric;
create index if not exists downtime_report_idx on llm.downtime (org_id, report_id);

-- Every status change, logged (insert = ingested; a re-ingest of the same report logs ingested again).
create or replace function private.llm_report_log() returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if tg_op = 'INSERT' or new.status is distinct from old.status or new.ingested_at is distinct from old.ingested_at then
    insert into llm.report_events (org_id, report_id, from_status, to_status, detail)
    values (new.org_id, new.report_id, case when tg_op = 'UPDATE' then old.status end, new.status, new.error);
  end if;
  return new;
end $$;
drop trigger if exists reports_log on llm.reports;
create trigger reports_log after insert or update on llm.reports for each row execute function private.llm_report_log();

-- Read access: same rule as every other llm table (members, or anyone for a public demo org). No writes from the API.
do $$ declare t text; begin
  foreach t in array array['report_types', 'reports', 'report_events'] loop
    execute format('alter table llm.%I enable row level security', t);
    execute format('drop policy if exists %I on llm.%I', t || '_read', t);
    execute format('drop policy if exists %I on llm.%I', t || '_public_read', t);
    execute format('create policy %I on llm.%I for select to authenticated using (private.has_org_role(org_id) or private.llm_is_public(org_id))', t || '_read', t);
    execute format('create policy %I on llm.%I for select to anon using (private.llm_is_public(org_id))', t || '_public_read', t);
    execute format('revoke all on llm.%I from anon, authenticated', t);
    execute format('grant select on llm.%I to anon, authenticated', t);
    execute format('grant all on llm.%I to service_role', t);
  end loop;
end $$;

-- ───────────── Extractors (one per name in a type's `extract` list) ─────────────
-- downtime: every stop and break in a Shift Report. The RCFA, if one was opened, is found by equipment and day (the
-- shift lead doesn't know it when writing; the RCFA log does).
create or replace function private.llm_extract_downtime(p_org uuid, p_rep llm.reports) returns int
language plpgsql security definer set search_path = '' as $$
declare n int;
begin
  if jsonb_typeof(p_rep.body->'stops') <> 'array' then raise exception 'stops must be a list'; end if;
  delete from llm.downtime d where d.org_id = p_org and d.report_id = p_rep.report_id;
  insert into llm.downtime as d (org_id, event_id, starts_at, ends_at, minutes, kind, area, equipment, asset_no, position_id, cause, grade,
                                 crew, wo_no, rcfa_id, comment, source_file, report_id)
  select p_org, s->>'event_id', (s->>'start')::timestamptz, (s->>'end')::timestamptz, (s->>'minutes')::numeric, s->>'kind',
         nullif(s->>'area', ''), nullif(s->>'equipment', ''), nullif(s->>'asset_no', ''), nullif(s->>'position_id', ''), s->>'cause',
         nullif(s->>'grade', ''), coalesce(nullif(s->>'crew', ''), p_rep.crew), nullif(s->>'wo_no', ''),
         case when s->>'kind' = 'unplanned' then
           (select r.rcfa_id from llm.rcfa r where r.org_id = p_org and r.asset_no = s->>'asset_no'
              and r.event_date = ((s->>'start')::timestamptz at time zone 'America/New_York')::date order by r.rcfa_id limit 1) end,
         nullif(s->>'comment', ''), p_rep.file_path, p_rep.report_id
  from jsonb_array_elements(p_rep.body->'stops') s
  on conflict (org_id, event_id) do update set starts_at = excluded.starts_at, ends_at = excluded.ends_at, minutes = excluded.minutes,
    kind = excluded.kind, area = excluded.area, equipment = excluded.equipment, asset_no = excluded.asset_no, position_id = excluded.position_id,
    cause = excluded.cause, grade = excluded.grade, crew = excluded.crew, wo_no = excluded.wo_no, rcfa_id = excluded.rcfa_id,
    comment = excluded.comment, source_file = excluded.source_file, report_id = excluded.report_id;
  get diagnostics n = row_count;
  return n;
end $$;

-- production_daily: the mill day's row from a Production Report.
create or replace function private.llm_extract_production_daily(p_org uuid, p_rep llm.reports) returns int
language plpgsql security definer set search_path = '' as $$
declare b jsonb := p_rep.body;
begin
  insert into llm.production_daily as p (org_id, day, tons, uptime_pct, breaks, break_min, unplanned_min, planned_min, slowdown_min, avg_speed,
                                         grade_hours, steam_per_t, kwh_per_t, reel_moist, crew_day, crew_night, source_file, report_id,
                                         saleable_tons, broke_tons, cull_tons, off_spec_hours, time_eff, prod_eff, quality_eff, ome_pct)
  values (p_org, p_rep.mill_day, (b->>'tons')::numeric, (b->>'uptime_pct')::numeric, (b->>'breaks')::int, (b->'minutes'->>'break')::numeric,
          (b->'minutes'->>'unplanned')::numeric, (b->'minutes'->>'planned')::numeric, (b->'minutes'->>'slowdown')::numeric, (b->>'avg_speed')::numeric,
          b->>'grade_hours', (b->'energy'->>'steam_per_t')::numeric, (b->'energy'->>'kwh_per_t')::numeric, (b->>'reel_moist')::numeric,
          b->'crews'->>'day', b->'crews'->>'night', p_rep.file_path, p_rep.report_id,
          (b->>'saleable_tons')::numeric, (b->>'broke_tons')::numeric, (b->>'cull_tons')::numeric, (b->'quality'->>'off_spec_hours')::int,
          (b->'efficiency'->>'time_pct')::numeric, (b->'efficiency'->>'production_pct')::numeric, (b->'efficiency'->>'quality_pct')::numeric,
          (b->'efficiency'->>'ome_pct')::numeric)
  on conflict (org_id, day) do update set tons = excluded.tons, uptime_pct = excluded.uptime_pct, breaks = excluded.breaks, break_min = excluded.break_min,
    unplanned_min = excluded.unplanned_min, planned_min = excluded.planned_min, slowdown_min = excluded.slowdown_min, avg_speed = excluded.avg_speed,
    grade_hours = excluded.grade_hours, steam_per_t = excluded.steam_per_t, kwh_per_t = excluded.kwh_per_t, reel_moist = excluded.reel_moist,
    crew_day = excluded.crew_day, crew_night = excluded.crew_night, source_file = excluded.source_file, report_id = excluded.report_id,
    saleable_tons = excluded.saleable_tons, broke_tons = excluded.broke_tons, cull_tons = excluded.cull_tons, off_spec_hours = excluded.off_spec_hours,
    time_eff = excluded.time_eff, prod_eff = excluded.prod_eff, quality_eff = excluded.quality_eff, ome_pct = excluded.ome_pct;
  return 1;
end $$;

-- Process what's been ingested: check the type's required fields, run its extractors, index it (searchable text and
-- the positions it mentions). A report that fails is marked failed with the error and doesn't stop the others; fix it
-- and ingest it again to retry. Returns {picked, extracted, failed}.
create or replace function public.mm_llm_process_reports(p_token text, p_limit int default 500)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare o uuid; r llm.reports; t llm.report_types; x text; miss text[]; n int := 0; ok int := 0; bad int := 0;
begin
  o := private.llm_token_org(p_token);
  if o is null then raise exception 'invalid or expired ingest token' using errcode = '28000'; end if;
  for r in select * from llm.reports where org_id = o and status = 'ingested' order by mill_day, period_start limit least(p_limit, 2000) loop
    n := n + 1;
    begin
      select * into t from llm.report_types where org_id = o and type = r.type;
      if t.type is null then raise exception 'unknown report type % (load the registry)', r.type; end if;
      select array_agg(k) into miss from unnest(t.required) k where not (r.body ? k);
      if miss is not null then raise exception 'body is missing %', array_to_string(miss, ', '); end if;
      foreach x in array t.extract loop
        case x
          when 'downtime' then perform private.llm_extract_downtime(o, r);
          when 'production_daily' then perform private.llm_extract_production_daily(o, r);
          else raise exception 'no extractor %', x;
        end case;
      end loop;
      update llm.reports set status = 'extracted', error = null, processed_at = now() where org_id = o and report_id = r.report_id;
      update llm.reports set status = 'indexed',
        positions = coalesce((select array_agg(distinct p) from (
            select s->>'position_id' as p from jsonb_array_elements(case when jsonb_typeof(r.body->'stops') = 'array' then r.body->'stops' else '[]' end) s
          ) z where p is not null and p <> ''), '{}')
      where org_id = o and report_id = r.report_id;
      ok := ok + 1;
    exception when others then
      update llm.reports set status = 'failed', error = sqlerrm, processed_at = now() where org_id = o and report_id = r.report_id;
      bad := bad + 1;
    end;
  end loop;
  return jsonb_build_object('picked', n, 'extracted', ok, 'failed', bad);
end $$;
revoke execute on function public.mm_llm_process_reports(text, int) from public, anon, authenticated;
grant execute on function public.mm_llm_process_reports(text, int) to service_role;
revoke execute on function private.llm_extract_downtime(uuid, llm.reports) from public;
revoke execute on function private.llm_extract_production_daily(uuid, llm.reports) from public;
revoke execute on function private.llm_report_log() from public;

-- ───────────── Reading (security invoker: RLS decides) ─────────────
-- Reports in a date range (mill days), optionally one type, optionally matching words (full text, all words).
create or replace function public.mm_llm_reports(p_org uuid, p_from date, p_to date, p_type text default null, p_term text default null, p_limit int default 60)
returns table (report_id text, type text, mill_day date, shift text, crew text, author text, author_role text, period_start timestamptz,
               period_end timestamptz, status text, body jsonb, text text)
language sql stable security invoker set search_path = '' as $$
  select r.report_id, r.type, r.mill_day, r.shift, r.crew, r.author, r.author_role, r.period_start, r.period_end, r.status, r.body, r.text
  from llm.reports r
  where r.org_id = p_org and r.mill_day between p_from and p_to and (p_type is null or r.type = p_type)
    and (p_term is null or r.fts @@ pg_catalog.websearch_to_tsquery('english', p_term))
  order by r.period_start desc limit least(p_limit, 400);
$$;

-- One report, with its lifecycle (every status change).
create or replace function public.mm_llm_report(p_org uuid, p_report_id text)
returns table (report_id text, type text, mill_day date, shift text, crew text, author text, author_role text, status text, error text,
               body jsonb, text text, file_path text, history jsonb, events jsonb)
language sql stable security invoker set search_path = '' as $$
  select r.report_id, r.type, r.mill_day, r.shift, r.crew, r.author, r.author_role, r.status, r.error, r.body, r.text, r.file_path, r.history,
         (select coalesce(jsonb_agg(jsonb_build_object('at', e.at, 'from', e.from_status, 'to', e.to_status, 'detail', e.detail) order by e.id), '[]')
          from llm.report_events e where e.org_id = r.org_id and e.report_id = r.report_id)
  from llm.reports r where r.org_id = p_org and r.report_id = p_report_id;
$$;

-- The pipeline at a glance: reports by type and status, the latest day, and the failures.
create or replace function public.mm_llm_report_status(p_org uuid)
returns table (type text, title text, cadence text, status text, reports bigint, first_day date, last_day date, last_error text)
language sql stable security invoker set search_path = '' as $$
  select r.type, t.title, t.cadence, r.status, count(*), min(r.mill_day), max(r.mill_day), max(r.error)
  from llm.reports r left join llm.report_types t on t.org_id = r.org_id and t.type = r.type
  where r.org_id = p_org group by r.type, t.title, t.cadence, r.status order by r.type, r.status;
$$;

-- Efficiency by day, week or month (the Production Reports): tons, saleable tons and the OME parts (averages of the days).
create or replace function public.mm_llm_efficiency(p_org uuid, p_from date, p_to date, p_by text default 'month')
returns table (period text, days int, tons numeric, saleable_tons numeric, cull_tons numeric, off_spec_hours bigint,
               time_pct numeric, prod_pct numeric, quality_pct numeric, ome_pct numeric)
language sql stable security invoker set search_path = '' as $$
  select case p_by when 'month' then to_char(p.day, 'YYYY-MM') when 'week' then to_char(date_trunc('week', p.day), 'YYYY-MM-DD') else p.day::text end,
         count(*)::int, round(sum(p.tons), 0), round(sum(p.saleable_tons), 0), round(sum(p.cull_tons), 1), sum(p.off_spec_hours),
         round(avg(p.time_eff), 1), round(avg(p.prod_eff), 1), round(avg(p.quality_eff), 1), round(avg(p.ome_pct), 1)
  from llm.production_daily p
  where p.org_id = p_org and p.day between p_from and p_to and p.ome_pct is not null
  group by 1 order by 1;
$$;

do $$ declare f text; begin
  foreach f in array array['mm_llm_reports(uuid, date, date, text, text, int)', 'mm_llm_report(uuid, text)', 'mm_llm_report_status(uuid)',
                           'mm_llm_efficiency(uuid, date, date, text)'] loop
    execute format('revoke execute on function public.%s from public', f);
    execute format('grant execute on function public.%s to anon, authenticated, service_role', f);
  end loop;
end $$;

-- mm_llm_summary counts the reports too (redefined here, after llm.reports exists)
create or replace function public.mm_llm_summary(p_org uuid)
returns table (source text, n bigint, first_day date, last_day date)
language sql stable security invoker set search_path = '' as $$
  select 'BUS lines', count(*), min(sheet_date), max(sheet_date) from llm.bus_items where org_id = p_org
  union all select 'Work orders', count(*), min(requested), max(requested) from llm.work_orders where org_id = p_org
  union all select 'Actions', count(*), min(created), max(created) from llm.actions where org_id = p_org
  union all select 'RCFAs', count(*), min(event_date), max(event_date) from llm.rcfa where org_id = p_org
  union all select 'Bonvoy exceptions', count(*), min(period), max(period) from llm.bonvoy where org_id = p_org
  union all select 'Bonvoy reports', count(*), min(day), max(day) from llm.bonvoy_reports where org_id = p_org
  union all select 'Pi tags', count(distinct tag), min((t0 at time zone 'America/New_York')::date), max((t0 at time zone 'America/New_York')::date) from llm.pi_series where org_id = p_org
  union all select 'Documents', count(*), min(doc_date), max(doc_date) from llm.documents where org_id = p_org
  union all select 'Downtime events', count(*), min((starts_at at time zone 'America/New_York')::date), max((starts_at at time zone 'America/New_York')::date) from llm.downtime where org_id = p_org
  union all select 'Production days', count(*), min(day), max(day) from llm.production_daily where org_id = p_org
  union all select 'Position runs', count(*), min(installed), max(coalesce(removed, installed)) from llm.position_runs where org_id = p_org
  union all select 'Shift reports', count(*), min(mill_day), max(mill_day) from llm.reports where org_id = p_org and type = 'shift'
  union all select 'Production reports', count(*), min(mill_day), max(mill_day) from llm.reports where org_id = p_org and type = 'production';
$$;


-- ═════════════════════════ Step 10: drop-in documents for the RAG (migrations/10-rag.sql) ═════════════════════════
-- ───────────────────────── Documents: lifecycle, quality, versions ─────────────────────────
alter table llm.documents add column if not exists source text not null default 'generator';
alter table llm.documents add column if not exists status text not null default 'indexed';
alter table llm.documents add column if not exists sha256 text;
alter table llm.documents add column if not exists file_name text;
alter table llm.documents add column if not exists file_size bigint;
alter table llm.documents add column if not exists uploaded_by uuid references auth.users(id) on delete set null;
alter table llm.documents add column if not exists quality jsonb;
alter table llm.documents add column if not exists quality_score int;
alter table llm.documents add column if not exists summary text;
alter table llm.documents add column if not exists supersedes text;
alter table llm.documents add column if not exists superseded_by text;
alter table llm.documents add column if not exists error text;
alter table llm.documents add column if not exists review_note text;
alter table llm.documents add column if not exists reviewed_by uuid references auth.users(id) on delete set null;
alter table llm.documents add column if not exists reviewed_at timestamptz;
alter table llm.documents add column if not exists updated_at timestamptz default now();

do $$ begin
  alter table llm.documents drop constraint if exists documents_text_source_check;
  alter table llm.documents add constraint documents_text_source_check
    check (text_source in ('text', 'ocr', 'docx', 'csv', 'model', 'mixed'));
  alter table llm.documents drop constraint if exists documents_source_check;
  alter table llm.documents add constraint documents_source_check check (source in ('generator', 'upload'));
  alter table llm.documents drop constraint if exists documents_status_check;
  alter table llm.documents add constraint documents_status_check
    check (status in ('uploaded', 'parsed', 'assessed', 'needs_review', 'accepted', 'indexed', 'rejected', 'failed'));
end $$;

-- One live copy of a file per org (a rejected copy doesn't block a fresh upload).
create unique index if not exists documents_sha_idx on llm.documents (org_id, sha256)
  where sha256 is not null and status not in ('rejected', 'failed');
create index if not exists documents_status_idx on llm.documents (org_id, status, imported_at desc);

-- Page text, kept so chunks can be rebuilt without parsing again and agents can read a whole page.
create table if not exists llm.doc_pages (
  org_id uuid not null, doc_id text not null, page int not null,
  text text not null default '',
  text_source text not null check (text_source in ('layer', 'model', 'ocr')),
  chars int generated always as (length(text)) stored,
  garble real, rotation int,
  primary key (org_id, doc_id, page),
  foreign key (org_id, doc_id) references llm.documents (org_id, doc_id) on delete cascade);

-- Every status change, who made it and why.
create table if not exists llm.document_events (
  id bigint generated always as identity primary key,
  org_id uuid not null, doc_id text not null, at timestamptz not null default now(),
  from_status text, to_status text not null, actor uuid, detail jsonb,
  foreign key (org_id, doc_id) references llm.documents (org_id, doc_id) on delete cascade);
create index if not exists document_events_doc_idx on llm.document_events (org_id, doc_id, at);

-- Work queue for mm-rag-process: one row per document step.
create table if not exists llm.rag_jobs (
  id bigint generated always as identity primary key,
  org_id uuid not null, doc_id text not null,
  step text not null check (step in ('parse', 'assess', 'index')),
  state text not null default 'queued' check (state in ('queued', 'running', 'done', 'failed')),
  attempts int not null default 0, run_after timestamptz not null default now(),
  started_at timestamptz, finished_at timestamptz, error text, usage jsonb,
  foreign key (org_id, doc_id) references llm.documents (org_id, doc_id) on delete cascade);
create index if not exists rag_jobs_ready_idx on llm.rag_jobs (state, run_after) where state = 'queued';

-- Per-org knobs, tunable without a deploy. A missing row means the defaults.
create table if not exists llm.rag_settings (
  org_id uuid primary key references public.orgs(id) on delete cascade,
  accept_min int not null default 75,       -- score at or above: indexed without review
  review_min int not null default 40,       -- below this: rejected
  max_mb int not null default 30,
  daily_mb int not null default 100,        -- MB uploaded per org per day
  model text not null default 'claude-haiku-5-5');

-- Vector index (when pgvector is installed): semantic search stops scanning every chunk.
do $$ begin
  if exists (select 1 from pg_extension where extname = 'vector') then
    execute 'create index if not exists doc_chunks_embedding_idx on llm.doc_chunks
             using hnsw (embedding extensions.vector_cosine_ops)';
  end if;
end $$;

-- Read access: members of the org, or anyone for a public demo org. No direct writes.
do $$ declare t text; begin
  foreach t in array array['doc_pages', 'document_events', 'rag_jobs', 'rag_settings'] loop
    execute format('alter table llm.%I enable row level security', t);
    execute format('drop policy if exists %I on llm.%I', t || '_read', t);
    execute format('drop policy if exists %I on llm.%I', t || '_public_read', t);
    execute format('create policy %I on llm.%I for select to authenticated using (private.has_org_role(org_id) or private.llm_is_public(org_id))', t || '_read', t);
    execute format('create policy %I on llm.%I for select to anon using (private.llm_is_public(org_id))', t || '_public_read', t);
    execute format('revoke all on llm.%I from anon, authenticated', t);
    execute format('grant select on llm.%I to anon, authenticated', t);
    execute format('grant all on llm.%I to service_role', t);
  end loop;
end $$;

-- ───────────────────────── Storage: uploads into <org>/rag/inbox/ ─────────────────────────
-- Any member may upload a PDF to their own private org's inbox. Public demo orgs can't take uploads.
create or replace function private.rag_can_upload_path(p_org text)
returns boolean language sql stable security definer set search_path = '' as $$
  select private.has_org_role_path(p_org) and not private.llm_is_public_path(p_org);
$$;
revoke execute on function private.rag_can_upload_path(text) from public;
grant execute on function private.rag_can_upload_path(text) to authenticated;

drop policy if exists mm_rag_upload on storage.objects;
create policy mm_rag_upload on storage.objects for insert to authenticated
  with check (bucket_id = 'mm-files' and (storage.foldername(name))[2] = 'rag' and (storage.foldername(name))[3] = 'inbox'
              and lower(name) like '%.pdf' and private.rag_can_upload_path((storage.foldername(name))[1]));

-- ───────────────────────── Internal helpers ─────────────────────────
create or replace function private.rag_settings(p_org uuid) returns llm.rag_settings
language sql stable security definer set search_path = '' as $$
  select coalesce((select s from llm.rag_settings s where s.org_id = p_org),
                  row(p_org, 75, 40, 30, 100, 'claude-haiku-5-5')::llm.rag_settings);
$$;
revoke execute on function private.rag_settings(uuid) from public;

-- Move a document to a new status, log it, and queue the next step if there is one.
create or replace function private.rag_move(p_org uuid, p_doc text, p_to text, p_actor uuid, p_detail jsonb default null)
returns void language plpgsql security definer set search_path = '' as $$
declare v_from text;
begin
  select status into v_from from llm.documents where org_id = p_org and doc_id = p_doc for update;
  update llm.documents set status = p_to, updated_at = now() where org_id = p_org and doc_id = p_doc;
  insert into llm.document_events (org_id, doc_id, from_status, to_status, actor, detail) values (p_org, p_doc, v_from, p_to, p_actor, p_detail);
  if p_to in ('uploaded', 'parsed', 'accepted') then
    insert into llm.rag_jobs (org_id, doc_id, step)
    values (p_org, p_doc, case p_to when 'uploaded' then 'parse' when 'parsed' then 'assess' else 'index' end);
  end if;
end $$;
revoke execute on function private.rag_move(uuid, text, text, uuid, jsonb) from public;

-- ───────────────────────── For the page (signed in) ─────────────────────────
-- Register a file the user has just uploaded to <org>/rag/inbox/<doc_id>.pdf. Returns the document's id and
-- status. An identical file (same SHA-256) already in the library is returned instead, with duplicate = true.
create or replace function public.mm_rag_register(p_org uuid, p_path text, p_file_name text, p_sha256 text,
  p_size bigint, p_pages int, p_kind text default null, p_vendor text default null, p_doc_date date default null,
  p_positions text[] default '{}')
returns jsonb language plpgsql security definer set search_path = '' as $$
declare v_uid uuid := (select auth.uid()); v_set llm.rag_settings; v_doc text; v_dup record; v_today bigint;
begin
  if v_uid is null or not private.has_org_role(p_org) then raise exception 'Sign in as a member of this organization to upload.'; end if;
  if private.llm_is_public(p_org) then raise exception 'This is a public demo organization; uploads are turned off here.'; end if;
  if p_path !~ ('^' || p_org::text || '/rag/inbox/[0-9a-f-]{36}\.pdf$') then raise exception 'Upload path must be <org>/rag/inbox/<uuid>.pdf'; end if;
  if p_sha256 !~ '^[0-9a-f]{64}$' then raise exception 'sha256 must be 64 hex characters'; end if;
  v_set := private.rag_settings(p_org);
  if p_size is null or p_size <= 0 or p_size > v_set.max_mb::bigint * 1048576 then raise exception 'File must be under % MB.', v_set.max_mb; end if;
  if p_pages is null or p_pages < 1 then raise exception 'The PDF has no pages.'; end if;

  select d.doc_id, d.status, d.title into v_dup from llm.documents d
    where d.org_id = p_org and d.sha256 = p_sha256 and d.status not in ('rejected', 'failed');
  if found then return jsonb_build_object('doc_id', v_dup.doc_id, 'status', v_dup.status, 'title', v_dup.title, 'duplicate', true); end if;

  select coalesce(sum(d.file_size), 0) into v_today from llm.documents d
    where d.org_id = p_org and d.source = 'upload' and d.imported_at > now() - interval '1 day';
  if v_today + p_size > v_set.daily_mb::bigint * 1048576 then
    raise exception 'Daily upload limit reached (% MB a day). Try again tomorrow.', v_set.daily_mb; end if;

  v_doc := substring(p_path from '([0-9a-f-]{36})\.pdf$');
  insert into llm.documents (org_id, doc_id, kind, vendor, doc_date, title, file_path, mime, positions, pages,
                             source, status, sha256, file_name, file_size, uploaded_by)
  values (p_org, v_doc, nullif(p_kind, ''), nullif(p_vendor, ''), p_doc_date, regexp_replace(left(p_file_name, 200), '\.pdf$', '', 'i'),
          p_path, 'application/pdf', coalesce(p_positions, '{}'), p_pages, 'upload', 'uploaded', p_sha256, left(p_file_name, 200), p_size, v_uid);
  insert into llm.document_events (org_id, doc_id, to_status, actor, detail)
    values (p_org, v_doc, 'uploaded', v_uid, jsonb_build_object('file_name', p_file_name, 'pages', p_pages, 'bytes', p_size));
  insert into llm.rag_jobs (org_id, doc_id, step) values (p_org, v_doc, 'parse');
  return jsonb_build_object('doc_id', v_doc, 'status', 'uploaded', 'duplicate', false);
end $$;
revoke execute on function public.mm_rag_register(uuid, text, text, text, bigint, int, text, text, date, text[]) from public, anon;
grant execute on function public.mm_rag_register(uuid, text, text, text, bigint, int, text, text, date, text[]) to authenticated;

-- Editor review of a document that needs it: accept (indexes it), reject, or retry a failed one.
-- p_meta may correct kind, vendor, doc_date, title, positions and supersedes (doc_id of the older version).
create or replace function public.mm_rag_review(p_org uuid, p_doc text, p_action text, p_meta jsonb default '{}', p_note text default null)
returns text language plpgsql security definer set search_path = '' as $$
declare v_uid uuid := (select auth.uid()); v_status text; v_old text;
begin
  if v_uid is null or not private.has_org_role(p_org, 'editor') then raise exception 'Only editors can review documents.'; end if;
  select status into v_status from llm.documents where org_id = p_org and doc_id = p_doc;
  if v_status is null then raise exception 'No document %', p_doc; end if;
  if p_action = 'retry' then
    if v_status <> 'failed' then raise exception 'Only a failed document can be retried.'; end if;
    perform private.rag_move(p_org, p_doc, 'uploaded', v_uid, jsonb_build_object('action', 'retry'));
    return 'uploaded';
  end if;
  if v_status not in ('needs_review', 'assessed', 'indexed', 'rejected') then raise exception 'Document is % — wait for processing to finish.', v_status; end if;
  update llm.documents d set
    kind = coalesce(p_meta->>'kind', d.kind), vendor = coalesce(p_meta->>'vendor', d.vendor),
    doc_date = coalesce((p_meta->>'doc_date')::date, d.doc_date), title = coalesce(p_meta->>'title', d.title),
    positions = coalesce((select array_agg(x) from jsonb_array_elements_text(p_meta->'positions') x), d.positions),
    review_note = p_note, reviewed_by = v_uid, reviewed_at = now()
  where d.org_id = p_org and d.doc_id = p_doc;
  v_old := p_meta->>'supersedes';
  if v_old is not null then
    if not exists (select 1 from llm.documents where org_id = p_org and doc_id = v_old) then raise exception 'No document % to supersede', v_old; end if;
    update llm.documents set supersedes = v_old where org_id = p_org and doc_id = p_doc;
    update llm.documents set superseded_by = p_doc where org_id = p_org and doc_id = v_old;
  end if;
  if p_action = 'accept' then
    if v_status = 'indexed' then return 'indexed'; end if;           -- metadata edit on an indexed document
    perform private.rag_move(p_org, p_doc, 'accepted', v_uid, jsonb_build_object('action', 'accept', 'note', p_note));
    return 'accepted';
  elsif p_action = 'reject' then
    delete from llm.doc_chunks where org_id = p_org and doc_id = p_doc;
    perform private.rag_move(p_org, p_doc, 'rejected', v_uid, jsonb_build_object('action', 'reject', 'note', p_note));
    return 'rejected';
  end if;
  raise exception 'action must be accept, reject or retry';
end $$;
revoke execute on function public.mm_rag_review(uuid, text, text, jsonb, text) from public, anon;
grant execute on function public.mm_rag_review(uuid, text, text, jsonb, text) to authenticated;

-- ───────────────────────── Read tools (page, assistant, MCP) ─────────────────────────
-- The library: every document with its status and quality. Filters are optional.
create or replace function public.mm_rag_library(p_org uuid, p_status text default null, p_kind text default null,
  p_position text default null, p_query text default null, p_limit int default 200)
returns table (doc_id text, title text, kind text, vendor text, doc_date date, positions text[], pages int, source text,
  status text, quality_score int, summary text, issues jsonb, file_name text, file_path text, uploaded_by uuid,
  imported_at timestamptz, updated_at timestamptz, supersedes text, superseded_by text, error text)
language sql stable security invoker set search_path = '' as $$
  select d.doc_id, d.title, d.kind, d.vendor, d.doc_date, d.positions, d.pages, d.source, d.status, d.quality_score,
         d.summary, d.quality->'issues', d.file_name, d.file_path, d.uploaded_by, d.imported_at, d.updated_at,
         d.supersedes, d.superseded_by, d.error
  from llm.documents d
  where d.org_id = p_org and (p_status is null or d.status = p_status) and (p_kind is null or d.kind = p_kind)
    and (p_position is null or p_position = any(d.positions))
    and (p_query is null or d.title ilike '%' || p_query || '%' or d.vendor ilike '%' || p_query || '%' or d.file_name ilike '%' || p_query || '%')
  order by d.imported_at desc, d.doc_id limit least(coalesce(p_limit, 200), 1000);
$$;
grant execute on function public.mm_rag_library(uuid, text, text, text, text, int) to anon, authenticated;

-- Counts by status, plus what needs a person (review, failed). For the page header and an agent's morning watch.
create or replace function public.mm_rag_status(p_org uuid)
returns table (status text, docs bigint, pages bigint, oldest timestamptz)
language sql stable security invoker set search_path = '' as $$
  select d.status, count(*), coalesce(sum(d.pages), 0), min(d.imported_at)
  from llm.documents d where d.org_id = p_org group by d.status order by d.status;
$$;
grant execute on function public.mm_rag_status(uuid) to anon, authenticated;

-- One document's metadata, quality and history.
create or replace function public.mm_rag_document(p_org uuid, p_doc text)
returns jsonb language sql stable security invoker set search_path = '' as $$
  select jsonb_build_object('document', to_jsonb(d) - 'org_id' - 'uploaded_by' - 'reviewed_by',
    'events', coalesce((select jsonb_agg(jsonb_build_object('at', e.at, 'from', e.from_status, 'to', e.to_status, 'detail', e.detail) order by e.at)
                        from llm.document_events e where e.org_id = d.org_id and e.doc_id = d.doc_id), '[]'),
    'chunks', (select count(*) from llm.doc_chunks c where c.org_id = d.org_id and c.doc_id = d.doc_id),
    'pages_stored', (select count(*) from llm.doc_pages p where p.org_id = d.org_id and p.doc_id = d.doc_id))
  from llm.documents d where d.org_id = p_org and d.doc_id = p_doc;
$$;
grant execute on function public.mm_rag_document(uuid, text) to anon, authenticated;

-- Full text of up to 5 pages, for close reading. Falls back to the indexed chunks for documents loaded before
-- page text was kept (the generator's documents).
create or replace function public.mm_rag_pages(p_org uuid, p_doc text, p_from int default 1, p_to int default null)
returns table (page int, text text, text_source text)
language sql stable security invoker set search_path = '' as $$
  with r as (select greatest(coalesce(p_from, 1), 1) a, least(coalesce(p_to, p_from, 1), greatest(coalesce(p_from, 1), 1) + 4) b)
  select p.page, p.text, p.text_source from llm.doc_pages p, r
    where p.org_id = p_org and p.doc_id = p_doc and p.page between r.a and r.b
  union all
  select c.page, string_agg(c.content, E'\n' order by c.chunk_no), 'chunks'
    from llm.doc_chunks c, r
    where c.org_id = p_org and c.doc_id = p_doc and coalesce(c.page, 1) between r.a and r.b
      and not exists (select 1 from llm.doc_pages p where p.org_id = p_org and p.doc_id = p_doc)
    group by c.page
  order by 1;
$$;
grant execute on function public.mm_rag_pages(uuid, text, int, int) to anon, authenticated;

-- Hybrid search: full text and (when given an embedding) vector, merged by reciprocal rank fusion.
-- Only indexed documents, newest version unless p_all_versions. Filters are optional.
create or replace function public.mm_rag_search(p_org uuid, p_query text, p_embedding text default null, p_limit int default 8,
  p_kind text default null, p_vendor text default null, p_position text default null, p_from date default null, p_to date default null,
  p_min_quality int default null, p_all_versions boolean default false)
returns table (doc_id text, title text, kind text, vendor text, doc_date date, page int, chunk_no int, content text,
  quality_score int, score double precision, matched text)
language plpgsql stable security invoker set search_path = '' as $$
declare v_vec boolean := p_embedding is not null and exists (select 1 from pg_extension where extname = 'vector');
begin
  return query execute format($q$
    with docs as (
      select d.* from llm.documents d
      where d.org_id = $1 and d.status = 'indexed' and ($5::text is null or d.kind = $5) and ($6::text is null or d.vendor ilike $6)
        and ($7::text is null or $7 = any(d.positions)) and ($8::date is null or d.doc_date >= $8) and ($9::date is null or d.doc_date <= $9)
        and ($10::int is null or coalesce(d.quality_score, 100) >= $10) and ($11 or d.superseded_by is null)),
    ft as (
      select c.doc_id, c.chunk_no, row_number() over (order by ts_rank_cd(c.fts, q) desc) rk
      from llm.doc_chunks c join docs d using (doc_id), websearch_to_tsquery('english', $2) q
      where c.org_id = $1 and c.fts @@ q limit 50),
    ve as (%s),
    fused as (
      select coalesce(ft.doc_id, ve.doc_id) doc_id, coalesce(ft.chunk_no, ve.chunk_no) chunk_no,
             coalesce(1.0 / (60 + ft.rk), 0) + coalesce(1.0 / (60 + ve.rk), 0) score,
             case when ft.rk is not null and ve.rk is not null then 'both' when ft.rk is not null then 'text' else 'meaning' end matched
      from ft full join ve on ft.doc_id = ve.doc_id and ft.chunk_no = ve.chunk_no)
    select d.doc_id, d.title, d.kind, d.vendor, d.doc_date, c.page, c.chunk_no, c.content, d.quality_score, f.score::double precision, f.matched
    from fused f join llm.doc_chunks c on c.org_id = $1 and c.doc_id = f.doc_id and c.chunk_no = f.chunk_no
    join docs d on d.doc_id = f.doc_id
    order by f.score desc limit least(coalesce($4, 8), 30)$q$,
    case when v_vec then
      $v$select c.doc_id, c.chunk_no, row_number() over (order by extensions.cosine_distance(c.embedding, $3::extensions.vector)) rk
         from llm.doc_chunks c join docs d using (doc_id)
         where c.org_id = $1 and c.embedding is not null
         order by extensions.cosine_distance(c.embedding, $3::extensions.vector) limit 50$v$
    else 'select null::text doc_id, null::int chunk_no, null::bigint rk where false' end)
  using p_org, p_query, p_embedding, p_limit, p_kind, p_vendor, p_position, p_from, p_to, p_min_quality, p_all_versions;
end $$;
grant execute on function public.mm_rag_search(uuid, text, text, int, text, text, text, date, date, int, boolean) to anon, authenticated;

-- The Vendor Reports page and the assistant only see documents that made it into the library.
create or replace function public.mm_llm_documents(p_org uuid, p_kind text default null)
returns table (doc_id text, kind text, vendor text, doc_date date, title text, file_path text, mime text, positions text[], assets text[], pages int)
language sql stable security invoker set search_path = '' as $$
  select d.doc_id, d.kind, d.vendor, d.doc_date, d.title, d.file_path, d.mime, d.positions, d.assets, d.pages
  from llm.documents d where d.org_id = p_org and d.status = 'indexed' and (p_kind is null or d.kind = p_kind)
  order by d.doc_date desc nulls last, d.doc_id limit 1000;
$$;

-- ───────────────────────── For mm-rag-process (service role only) ─────────────────────────
-- Claim up to p_limit ready jobs (skips rows another worker holds).
create or replace function public.mm_rag_claim(p_limit int default 3)
returns setof llm.rag_jobs language sql security definer set search_path = '' as $$
  update llm.rag_jobs j set state = 'running', attempts = j.attempts + 1, started_at = now()
  where j.id in (select id from llm.rag_jobs where state = 'queued' and run_after <= now()
                 order by run_after, id limit least(p_limit, 10) for update skip locked)
  returning j.*;
$$;

-- Finish a job: done (and move the document on), retry later, or fail the document after 3 attempts.
-- p_doc_patch sets document fields the step produced (title, kind, vendor, doc_date, positions, assets, summary,
-- quality, quality_score, text_source); p_to is the document's next status.
create or replace function public.mm_rag_finish(p_job bigint, p_ok boolean, p_to text default null, p_doc_patch jsonb default '{}',
  p_error text default null, p_usage jsonb default null)
returns text language plpgsql security definer set search_path = '' as $$
declare j llm.rag_jobs;
begin
  select * into j from llm.rag_jobs where id = p_job and state = 'running' for update;
  if not found then raise exception 'job % is not running', p_job; end if;
  update llm.rag_jobs set usage = p_usage, finished_at = now(), error = p_error,
    state = case when p_ok then 'done' when j.attempts >= 3 then 'failed' else 'queued' end,
    run_after = case when p_ok or j.attempts >= 3 then run_after else now() + (j.attempts * interval '2 minutes') end
  where id = p_job;
  if not p_ok then
    if j.attempts >= 3 then
      update llm.documents set error = p_error where org_id = j.org_id and doc_id = j.doc_id;
      perform private.rag_move(j.org_id, j.doc_id, 'failed', null, jsonb_build_object('step', j.step, 'error', p_error));
      return 'failed';
    end if;
    return 'retry';
  end if;
  update llm.documents d set
    title = coalesce(p_doc_patch->>'title', d.title), kind = coalesce(p_doc_patch->>'kind', d.kind),
    vendor = coalesce(p_doc_patch->>'vendor', d.vendor), doc_date = coalesce((p_doc_patch->>'doc_date')::date, d.doc_date),
    positions = coalesce((select array_agg(x) from jsonb_array_elements_text(p_doc_patch->'positions') x), d.positions),
    assets = coalesce((select array_agg(x) from jsonb_array_elements_text(p_doc_patch->'assets') x), d.assets),
    summary = coalesce(p_doc_patch->>'summary', d.summary), quality = coalesce(p_doc_patch->'quality', d.quality),
    quality_score = coalesce((p_doc_patch->>'quality_score')::int, d.quality_score),
    text_source = coalesce(p_doc_patch->>'text_source', d.text_source), error = null
  where d.org_id = j.org_id and d.doc_id = j.doc_id;
  if p_to is not null then
    perform private.rag_move(j.org_id, j.doc_id, p_to, null, jsonb_build_object('step', j.step) || coalesce(p_usage, '{}'));
  end if;
  return coalesce(p_to, 'done');
end $$;

-- Replace a document's page text (parse step) or chunks (index step) in one call.
create or replace function public.mm_rag_save_pages(p_org uuid, p_doc text, p_pages jsonb)
returns int language plpgsql security definer set search_path = '' as $$
declare n int;
begin
  delete from llm.doc_pages where org_id = p_org and doc_id = p_doc;
  insert into llm.doc_pages (org_id, doc_id, page, text, text_source, garble, rotation)
  select p_org, p_doc, (r->>'page')::int, coalesce(r->>'text', ''), r->>'text_source', (r->>'garble')::real, (r->>'rotation')::int
  from jsonb_array_elements(p_pages) r;
  get diagnostics n = row_count; return n;
end $$;

create or replace function public.mm_rag_save_chunks(p_org uuid, p_doc text, p_chunks jsonb)
returns int language plpgsql security definer set search_path = '' as $$
declare n int;
begin
  delete from llm.doc_chunks where org_id = p_org and doc_id = p_doc;
  insert into llm.doc_chunks (org_id, doc_id, chunk_no, page, content, positions)
  select p_org, p_doc, (r->>'chunk_no')::int, (r->>'page')::int, r->>'content',
         coalesce((select array_agg(x) from jsonb_array_elements_text(r->'positions') x), '{}')
  from jsonb_array_elements(p_chunks) r;
  get diagnostics n = row_count; return n;
end $$;

do $$ declare f text; begin
  foreach f in array array['public.mm_rag_claim(int)', 'public.mm_rag_finish(bigint, boolean, text, jsonb, text, jsonb)',
                           'public.mm_rag_save_pages(uuid, text, jsonb)', 'public.mm_rag_save_chunks(uuid, text, jsonb)'] loop
    execute format('revoke execute on function %s from public, anon, authenticated', f);
    execute format('grant execute on function %s to service_role', f);
  end loop;
end $$;

-- ═════════════════════════ Step 11: RAG worker, the RAG page and the MCP server (migrations/11-rag-worker.sql) ═════════════════════════
do $$ begin
  if exists (select 1 from pg_available_extensions where name = 'pg_net') then
    execute 'create extension if not exists pg_net with schema extensions';
  end if;
end $$;

-- The signed-in user's organizations (memberships are readable by their own user only).
create or replace function public.mm_my_orgs()
returns table (id uuid, name text, role public.org_role, is_public boolean, since timestamptz)
language sql stable security definer set search_path = '' as $$
  select o.id, o.name, m.role, exists (select 1 from llm.public_orgs p where p.org_id = o.id), m.created_at
  from public.memberships m join public.orgs o on o.id = m.org_id
  where m.user_id = (select auth.uid())
  order by m.created_at;
$$;
revoke execute on function public.mm_my_orgs() from public, anon;
grant execute on function public.mm_my_orgs() to authenticated;

-- Add or replace some pages (one parse batch); mm_rag_save_pages replaces all of a document's pages.
create or replace function public.mm_rag_add_pages(p_org uuid, p_doc text, p_pages jsonb)
returns int language plpgsql security definer set search_path = '' as $$
declare n int;
begin
  insert into llm.doc_pages (org_id, doc_id, page, text, text_source, garble, rotation)
  select p_org, p_doc, (r->>'page')::int, coalesce(r->>'text', ''), r->>'text_source', (r->>'garble')::real, (r->>'rotation')::int
  from jsonb_array_elements(p_pages) r
  on conflict (org_id, doc_id, page) do update set text = excluded.text, text_source = excluded.text_source,
    garble = excluded.garble, rotation = excluded.rotation;
  get diagnostics n = row_count; return n;
end $$;

-- Put a running job back in the queue with its progress (a batch done, more to go). Doesn't count as an attempt.
create or replace function public.mm_rag_requeue(p_job bigint, p_progress jsonb)
returns void language sql security definer set search_path = '' as $$
  update llm.rag_jobs set state = 'queued', attempts = greatest(attempts - 1, 0), usage = p_progress, run_after = now(), error = null
  where id = p_job and state = 'running';
$$;

-- Stop retrying: the next failure fails the document (encrypted PDF, not a PDF, file missing).
create or replace function public.mm_rag_give_up(p_job bigint)
returns void language sql security definer set search_path = '' as $$
  update llm.rag_jobs set attempts = 3 where id = p_job and state = 'running';
$$;

-- Everything a worker step needs about one document: the row, the org's settings and (optionally) its pages.
create or replace function public.mm_rag_job_context(p_org uuid, p_doc text, p_pages boolean default false)
returns jsonb language sql stable security definer set search_path = '' as $$
  select jsonb_build_object(
    'doc', to_jsonb(d) - 'org_id',
    'settings', to_jsonb(private.rag_settings(p_org)) - 'org_id',
    'pages', case when p_pages then coalesce((select jsonb_agg(jsonb_build_object('page', p.page, 'text', p.text, 'text_source', p.text_source,
                                                       'garble', p.garble, 'rotation', p.rotation) order by p.page)
                                               from llm.doc_pages p where p.org_id = p_org and p.doc_id = p_doc), '[]') end)
  from llm.documents d where d.org_id = p_org and d.doc_id = p_doc;
$$;

-- Chunks of indexed documents with no embedding yet, newest documents first, any org (needs pgvector).
do $$ begin
  if exists (select 1 from pg_extension where extname = 'vector') then
    execute $f$
      create or replace function public.mm_rag_chunks_to_embed(p_limit int default 6)
      returns table (org_id uuid, doc_id text, chunk_no int, content text)
      language sql stable security definer set search_path = '' as $b$
        select c.org_id, c.doc_id, c.chunk_no, c.content
        from llm.doc_chunks c join llm.documents d using (org_id, doc_id)
        where c.embedding is null and d.status = 'indexed' and d.source = 'upload'
        order by d.updated_at desc, c.chunk_no limit least(p_limit, 50);
      $b$;
      revoke execute on function public.mm_rag_chunks_to_embed(int) from public, anon, authenticated;
      grant execute on function public.mm_rag_chunks_to_embed(int) to service_role;
    $f$;
  end if;
end $$;

do $$ declare f text; begin
  foreach f in array array['public.mm_rag_add_pages(uuid, text, jsonb)', 'public.mm_rag_requeue(bigint, jsonb)',
                           'public.mm_rag_give_up(bigint)', 'public.mm_rag_job_context(uuid, text, boolean)'] loop
    execute format('revoke execute on function %s from public, anon, authenticated', f);
    execute format('grant execute on function %s to service_role', f);
  end loop;
end $$;
