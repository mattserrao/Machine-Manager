-- Step 09: reports and the report lifecycle (Shift Report, Production Report; more types by registry entry).
-- A report is ingested once into llm.reports, then processed: its body is extracted into the tables it feeds
-- (llm.downtime, llm.production_daily; every extracted row keeps report_id) and it is indexed for search. Pages and the
-- assistant keep reading tables; nobody parses report text. Lifecycle (tools/reports/lifecycle.py):
--   generated -> submitted (where it's written)  ->  ingested -> extracted -> indexed (here)   | failed + error, retry
-- Every status change is logged in llm.report_events (a trigger). The report types come from tools/reports/registry.yaml
-- (loaded per org as llm.report_types), so the required fields and extractors live in one place.
-- Only adds; the same statements are in ../llm.sql (end state). Safe to re-run.

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

-- The ingest accepts 'report_types' and 'reports'; resetting reports also clears the rows extracted from them.
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

-- mm_llm_summary counts the reports too
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

-- mm_llm_downtime also says which report each stop came from (so a page can open the shift lead's notes)
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
revoke execute on function public.mm_llm_downtime(uuid, date, date, text) from public;
grant execute on function public.mm_llm_downtime(uuid, date, date, text) to anon, authenticated, service_role;
