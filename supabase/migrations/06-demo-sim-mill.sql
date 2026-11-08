-- Step 06 (Sim Mill is the demo), for a project that already has step 05. The same statements are in llm.sql (the end state);
-- this file is just the delta, safe to run again. Access was switched with the admin functions (see migrations/README.md).

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

-- The ingest also loads Sim Mill's task-package library (records:task-packages).
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
