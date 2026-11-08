-- Step 1 of 3 (see README.md). Safe to run any time and more than once.
-- Same statements as the matching parts of ../schema.sql.

-- Added later: who created each record (kept when the Whiteboard moved here), and an
-- index for "what changed since" refetches.
alter table public.mm_records add column if not exists created_by uuid default auth.uid();
create index if not exists mm_records_changed_idx on public.mm_records (org_id, tool, updated_at);

-- p_changes: [{ id, data, deleted, base }] — base = version last seen, null for new.
-- Returns one result per change, in the order sent:
--   { id, ok:true, version }                 saved
--   { id, ok:false, row }                    someone changed it first (row = theirs, or null if gone / no access)
--   { id, ok:false, row:null, error }        this change is invalid or not allowed; the rest still go through
-- Changes are applied in id order so two people saving overlapping batches never deadlock.
-- A new record (base null) whose id belongs to a deleted record brings that record back.
create or replace function public.mm_apply(p_org uuid, p_tool text, p_changes jsonb)
returns jsonb language plpgsql security invoker set search_path = '' as $$
declare
  c jsonb; pos bigint; res jsonb[]; v integer; cur jsonb; base integer; cid text; err text; n integer;
begin
  if p_changes is null or jsonb_typeof(p_changes) <> 'array' then
    raise exception 'mm_apply: p_changes must be a JSON array' using errcode = '22023';
  end if;
  n := jsonb_array_length(p_changes);
  if n > 500 then raise exception 'mm_apply: at most 500 changes per call (got %)', n using errcode = '22023'; end if;
  res := array_fill(null::jsonb, array[n]);
  for c, pos in select e.value, e.ord from jsonb_array_elements(p_changes) with ordinality e(value, ord)
                order by e.value->>'id' nulls first, e.ord loop
    v := null; cur := null; err := null; cid := c->>'id';
    begin
      if jsonb_typeof(c) <> 'object' or jsonb_typeof(c->'id') is distinct from 'string' then
        raise exception 'each change needs a string id' using errcode = '22023';
      end if;
      if c ? 'base' and jsonb_typeof(c->'base') not in ('number', 'null') then
        raise exception 'base must be a version number or null' using errcode = '22023';
      end if;
      if c ? 'deleted' and jsonb_typeof(c->'deleted') not in ('boolean', 'null') then
        raise exception 'deleted must be true or false' using errcode = '22023';
      end if;
      base := (c->>'base')::integer;
      if base is null then
        insert into public.mm_records as r (org_id, tool, id, data, deleted)
        values (p_org, p_tool, cid, coalesce(c->'data', '{}'::jsonb), coalesce((c->>'deleted')::boolean, false))
        on conflict (org_id, tool, id) do update set data = excluded.data, deleted = excluded.deleted
          where r.deleted                                    -- only revives a deleted record
        returning version into v;
      else
        update public.mm_records set data = coalesce(c->'data', data), deleted = coalesce((c->>'deleted')::boolean, deleted)
        where org_id = p_org and tool = p_tool and id = cid and version = base returning version into v;
      end if;
      if v is null then
        select to_jsonb(r) into cur from public.mm_records r where r.org_id = p_org and r.tool = p_tool and r.id = cid;
      end if;
    exception
      when data_exception or integrity_constraint_violation or insufficient_privilege then
        err := sqlerrm;                                     -- this change only; deadlocks and outages still fail the call
    end;
    res[pos] := case when err is not null then jsonb_build_object('id', cid, 'ok', false, 'row', null, 'error', err)
                     else jsonb_build_object('id', cid, 'ok', v is not null, 'version', v, 'row', cur) end;
  end loop;
  return coalesce(to_jsonb(res), '[]'::jsonb);
end $$;

-- Paths of every file a tool's records point to (deleted records included, until they are purged).
-- Pages use this to remove stored files nothing refers to any more.
create or replace function public.mm_file_refs(p_org uuid, p_tool text)
returns setof text language sql stable security invoker set search_path = '' as $$
  select distinct p #>> '{}' from public.mm_records r,
    lateral jsonb_path_query(r.data, 'strict $.**.path') p
  where r.org_id = p_org and r.tool = p_tool and jsonb_typeof(p) = 'string';
$$;

revoke execute on function public.mm_apply(uuid, text, jsonb) from public, anon;
grant  execute on function public.mm_apply(uuid, text, jsonb) to authenticated;
revoke execute on function public.mm_file_refs(uuid, text) from public, anon;
grant  execute on function public.mm_file_refs(uuid, text) to authenticated;



-- ───────────────────────── Housekeeping ─────────────────────────
-- Nightly: remove records deleted more than 90 days ago (soft deletes otherwise stay forever
-- and are sent to every page that loads the tool). Needs pg_cron, which Supabase provides.
do $$ begin
  if exists (select 1 from pg_available_extensions where name = 'pg_cron') then
    execute 'create extension if not exists pg_cron';
    perform cron.schedule('mm-purge-deleted', '17 7 * * *',
      $q$delete from public.mm_records where deleted and updated_at < now() - interval '90 days'$q$);
  end if;
end $$;

