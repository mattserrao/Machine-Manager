-- MM LLM — the data the assistant reads, and the tools it reads it through.
-- Applied after schema.sql: the tests load both, and on the live project this file is migration step 04
-- (see migrations/README.md). Safe to re-run.
--
-- Model (schema llm; not exposed to the web API directly)
--   equipment, pi_tags, outages      the backbone: positions every other row is tagged to
--   bus_items                        one row per BUS sheet line (sheet date × issue); issue_key groups an issue across days
--   work_orders, actions             latest state from the JDE / Planner exports (re-imports update in place)
--   rcfa                             the RCFA log
--   envoy                            Envoy exceptions (one row per tag per day)
--   pi_series                        Pi series packed as arrays: hourly averages one row per tag per UTC day ('h'),
--                                    1-minute data one row per tag per hour around events ('m')
--   documents, doc_chunks            every document (vendor report, RCFA write-up, drawing, reference chart) and its
--                                    searchable chunks (full text always; embedding when the embedder has run)
--   ingest_files                     what was imported, when, from which file
--   downtime                         every stop, sheet break and slowdown (one row per event)          (step 05)
--   production_daily                 one row per mill day: tons, uptime, breaks, minutes lost, energy  (step 05)
--   position_runs                    every fabric, felt, plate and roll run on a position (life history) (step 05)
--
-- Access: members of an org can read its rows (RLS, same rule as mm_records), and anyone can read a public demo
-- org's rows (mm_llm_set_public; the Demo Mill is one). Nobody writes from the web page:
-- imports go through the mm-llm-ingest edge function and mm_llm_ingest(), guarded by an ingest token an admin creates in the SQL editor
-- (select public.mm_llm_new_ingest_token('Demo Mill', 6);). Tokens are stored hashed and expire.
--
-- Tools (what the orchestrator calls; security invoker, so RLS applies to the signed-in user):
--   mm_llm_search_docs, mm_llm_search_docs_vec, mm_llm_search_records, mm_llm_position_history, mm_llm_outage_scope,
--   mm_llm_overdue_actions, mm_llm_envoy, mm_llm_pi_daily, mm_llm_pi_values,
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

create table if not exists llm.envoy (
  org_id uuid not null references public.orgs(id) on delete cascade,
  period date not null, tag text not null, report_date date, description text, area text, asset_no text, asset text,
  position_id text, units text, grade text, mean double precision, std double precision, low double precision,
  high double precision, min double precision, max double precision, hours_outside int, first_outside text,
  last_outside text, direction text, source_file text,
  primary key (org_id, period, tag));
create index if not exists envoy_asset_idx on llm.envoy (org_id, asset_no, period);

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
  foreach t in array array['equipment','pi_tags','outages','bus_items','work_orders','actions','rcfa','envoy','pi_series',
                           'documents','doc_chunks','ingest_files','downtime','production_daily','position_runs'] loop
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
    if v_tool not in ('mymachine', 'outages', 'consumables') then raise exception 'records for % can''t be loaded', v_tool using errcode = '22023'; end if;
    if p_mode = 'reset' then delete from public.mm_records r where r.org_id = o and r.tool = v_tool; end if;
    insert into public.mm_records as r (org_id, tool, id, data, deleted)
    select o, v_tool, x->>'id', coalesce(x->'data', '{}'::jsonb), false from jsonb_array_elements(p_rows) x
    where jsonb_typeof(x->'id') = 'string'
    on conflict (org_id, tool, id) do update set data = excluded.data, deleted = false;
    get diagnostics n = row_count;
    return n;
  end if;
  if p_table not in ('equipment','pi_tags','outages','bus_items','work_orders','actions','rcfa','envoy','pi_series',
                     'documents','doc_chunks','ingest_files','downtime','production_daily','position_runs') then
    raise exception 'unknown table %', p_table using errcode = '22023';
  end if;
  if p_mode = 'reset' then
    execute format('delete from llm.%I where org_id = $1', p_table) using o;
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
    select 'Envoy', v.period, v.tag, v.description || ': ' || v.direction || ', max ' || v.max || ' ' || v.units || ' vs limit ' ||
           case when v.direction = 'High' then v.high else v.low end || ' (' || v.hours_outside || ' h)', null
      from llm.envoy v where v.org_id = p_org and v.asset_no in (select asset_no from a)
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
  union all select 'Envoy exceptions', count(*), min(period), max(period) from llm.envoy where org_id = p_org
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

-- Envoy exceptions for a tag, asset or position (or everything when p_term is null) in a date range.
create or replace function public.mm_llm_envoy(p_org uuid, p_term text default null, p_from date default null, p_to date default null)
returns table (period date, tag text, asset text, direction text, max double precision, high double precision,
               low double precision, hours_outside int, grade text)
language sql stable security invoker set search_path = '' as $$
  select v.period, v.tag, v.asset, v.direction, v.max, v.high, v.low, v.hours_outside, v.grade
  from llm.envoy v
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
create or replace function public.mm_llm_downtime(p_org uuid, p_from date, p_to date, p_kind text default null)
returns table (event_id text, starts_at timestamptz, minutes numeric, kind text, area text, equipment text, position_id text,
               cause text, grade text, crew text, wo_no text, rcfa_id text, comment text)
language sql stable security invoker set search_path = '' as $$
  select d.event_id, d.starts_at, d.minutes, d.kind, d.area, d.equipment, d.position_id, d.cause, d.grade, d.crew, d.wo_no, d.rcfa_id, d.comment
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
                           'mm_llm_envoy(uuid, text, date, date)', 'mm_llm_pi_daily(uuid, text, date, date)',
                           'mm_llm_downtime(uuid, date, date, text)', 'mm_llm_downtime_summary(uuid, date, date, text)', 'mm_llm_repeat_stops(uuid, date, date, int)', 'mm_llm_rcfa_status(uuid, date)', 'mm_llm_position_life(uuid, text, date)', 'mm_llm_production(uuid, date, date, text)', 'mm_llm_documents(uuid, text)', 'mm_llm_bus_day(uuid, date)',
                           'mm_llm_pi_values(uuid, text, timestamptz, timestamptz)'] loop
    execute format('revoke execute on function public.%s from public', f);
    execute format('grant execute on function public.%s to anon, authenticated', f);   -- RLS decides what comes back
  end loop;
end $$;


-- ───────────────────────── Asking the assistant ─────────────────────────
-- Two tiers: every signed-in user can read the assistant's saved answers for orgs they can see (members, or a
-- public demo org); only users on llm.query_access can ask new questions (through the mm-llm-ask edge function,
-- which runs the tools as that user and saves the answer). Grant in the SQL editor:
--   select public.mm_llm_grant_query('demodemo@gmail.com', 'Demo Mill', 40);   -- questions per day

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
                           'mm_llm_envoy(uuid, text, date, date)', 'mm_llm_pi_daily(uuid, text, date, date)',
                           'mm_llm_downtime(uuid, date, date, text)', 'mm_llm_downtime_summary(uuid, date, date, text)', 'mm_llm_repeat_stops(uuid, date, date, int)', 'mm_llm_rcfa_status(uuid, date)', 'mm_llm_position_life(uuid, text, date)', 'mm_llm_production(uuid, date, date, text)', 'mm_llm_documents(uuid, text)', 'mm_llm_bus_day(uuid, date)',
                           'mm_llm_pi_values(uuid, text, timestamptz, timestamptz)'] loop
    execute format('revoke execute on function public.%s from public', f);
    execute format('grant execute on function public.%s to anon, authenticated, service_role', f);
  end loop;
end $$;
