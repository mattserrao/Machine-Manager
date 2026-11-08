-- Step 05 (Sim Mill), for a project that already has step 04 (llm.sql as of 2026-11-08 18:00). The same statements are in
-- llm.sql (the end state); this file is just the delta, safe to run again.

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

create or replace function public.mm_llm_public_org() returns table (id uuid, name text)
language sql stable security invoker set search_path = '' as $$
  select p.org_id, p.name from llm.public_orgs p order by p.created_at;   -- every public demo org, the first published first (step 05: was limit 1)
$$;

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
  foreach f in array array['mm_llm_downtime(uuid, date, date, text)', 'mm_llm_downtime_summary(uuid, date, date, text)', 'mm_llm_repeat_stops(uuid, date, date, int)', 'mm_llm_rcfa_status(uuid, date)', 'mm_llm_position_life(uuid, text, date)', 'mm_llm_production(uuid, date, date, text)', 'mm_llm_documents(uuid, text)', 'mm_llm_bus_day(uuid, date)'] loop
    execute format('revoke execute on function public.%s from public', f);
    execute format('grant execute on function public.%s to anon, authenticated, service_role', f);   -- RLS decides what comes back
  end loop;
end $$;
