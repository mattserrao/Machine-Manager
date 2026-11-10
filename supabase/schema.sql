-- Machine Manager — Supabase schema
-- Run once in the Supabase dashboard: SQL Editor → New query → paste → Run.
-- Safe to re-run: every statement is idempotent.
--
-- Model
--   orgs          a mill / customer. Everything belongs to exactly one org.
--   memberships   who is in which org, as viewer | editor | admin.
--   mm_records    every tool's data (My Machine, Whiteboard, ...), one row per record.
--   storage       private bucket "mm-files" (<org_id>/<tool>/...).
--
-- Security
--   Row-level security on every table. A signed-in user only sees rows of orgs
--   they belong to; only editors and admins can write. Accounts and memberships
--   are managed from the dashboard (see SETUP.md), never from the web page.
--
-- Concurrency
--   Every record has a version number the database bumps on each write.
--   Pages save through mm_apply(), which only updates a row if the version it last saw
--   is still current. If someone else changed it first, the save is refused and the
--   page shows their version instead (no silent overwrites). Each change in a batch
--   succeeds or fails on its own, and rows are always locked in id order (no deadlocks).
--   Deletes are soft (deleted = true) so they sync live and can be undone; a nightly
--   job removes rows deleted more than 90 days ago.
--
-- Migrations for an existing project are in supabase/migrations/ (this file is the
-- end state and is safe to re-run).

-- ───────────────────────── Orgs & memberships ─────────────────────────

create table if not exists public.orgs (
  id         uuid primary key default gen_random_uuid(),
  name       text not null unique,
  created_at timestamptz not null default now()
);

do $$ begin
  create type public.org_role as enum ('viewer', 'editor', 'admin');   -- order matters: viewer < editor < admin
exception when duplicate_object then null; end $$;

create table if not exists public.memberships (
  org_id     uuid not null references public.orgs(id) on delete cascade,
  user_id    uuid not null references auth.users(id) on delete cascade,
  role       public.org_role not null default 'editor',
  created_at timestamptz not null default now(),
  primary key (org_id, user_id)
);
create index if not exists memberships_user_idx on public.memberships(user_id);

-- Helpers for the policies live in a schema the web API doesn't expose.
create schema if not exists private;
grant usage on schema private to authenticated;

-- True if the signed-in user has at least p_min role in p_org.
-- security definer so policies can call it without recursing into memberships' own policy.
create or replace function private.has_org_role(p_org uuid, p_min public.org_role default 'viewer')
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.memberships m
    where m.org_id = p_org and m.user_id = (select auth.uid()) and m.role >= p_min
  );
$$;

-- Same check for storage paths, whose first folder is the org id as text.
create or replace function private.has_org_role_path(p_org text, p_min public.org_role default 'viewer')
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.memberships m
    where m.org_id::text = p_org and m.user_id = (select auth.uid()) and m.role >= p_min
  );
$$;

alter table public.orgs        enable row level security;
alter table public.memberships enable row level security;

drop policy if exists orgs_read on public.orgs;
create policy orgs_read on public.orgs for select to authenticated
  using (private.has_org_role(id));

drop policy if exists memberships_read on public.memberships;
create policy memberships_read on public.memberships for select to authenticated
  using (user_id = (select auth.uid()) or private.has_org_role(org_id, 'admin'));

-- ───────────────────────── API access ─────────────────────────
-- Signed-out visitors (the demo) get nothing. Signed-in users go through RLS.

revoke all on public.orgs, public.memberships from anon;
grant select on public.orgs, public.memberships to authenticated;

revoke execute on function private.has_org_role(uuid, public.org_role) from public, anon;
grant  execute on function private.has_org_role(uuid, public.org_role) to authenticated;
revoke execute on function private.has_org_role_path(text, public.org_role) from public, anon;
grant  execute on function private.has_org_role_path(text, public.org_role) to authenticated;
-- Earlier versions kept these helpers in public; take them out of the API.
drop function if exists public.has_org_role(uuid, public.org_role);
drop function if exists public.has_org_role_path(text, public.org_role);

-- ───────────────────────── Records for every other tool ─────────────────────────
-- One generic table so new tools need no schema change: each tool stores its own
-- records (e.g. My Machine: 'machine', 'item:<position>') as JSON, with the same
-- version check and live updates as the Whiteboard.

create table if not exists public.mm_records (
  org_id      uuid not null references public.orgs(id) on delete cascade,
  tool        text not null check (tool ~ '^[a-z0-9-]{1,40}$'),
  id          text not null check (length(id) between 1 and 200),
  data        jsonb not null default '{}'::jsonb,
  deleted     boolean not null default false,
  version     integer not null default 1,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  updated_by  uuid default auth.uid(),
  primary key (org_id, tool, id)
);

-- Added later: who created each record (kept when the Whiteboard moved here), and an
-- index for "what changed since" refetches.
alter table public.mm_records add column if not exists created_by uuid default auth.uid();
create index if not exists mm_records_changed_idx on public.mm_records (org_id, tool, updated_at);

create or replace function public.mm_touch() returns trigger language plpgsql set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    new.version := 1;
  else
    new.version := old.version + 1;
    new.org_id := old.org_id; new.tool := old.tool; new.id := old.id;   -- records can't be moved
  end if;
  new.updated_at := now();
  new.updated_by := auth.uid();
  return new;
end $$;
drop trigger if exists mm_records_touch on public.mm_records;
create trigger mm_records_touch before insert or update on public.mm_records
  for each row execute function public.mm_touch();

alter table public.mm_records enable row level security;
drop policy if exists mm_records_read   on public.mm_records;
drop policy if exists mm_records_insert on public.mm_records;
drop policy if exists mm_records_update on public.mm_records;
create policy mm_records_read   on public.mm_records for select to authenticated using (private.has_org_role(org_id));
create policy mm_records_insert on public.mm_records for insert to authenticated with check (private.has_org_role(org_id, 'editor'));
create policy mm_records_update on public.mm_records for update to authenticated
  using (private.has_org_role(org_id, 'editor')) with check (private.has_org_role(org_id, 'editor'));

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

revoke all on public.mm_records from anon;
grant select, insert, update on public.mm_records to authenticated;
revoke execute on function public.mm_apply(uuid, text, jsonb) from public, anon;
grant  execute on function public.mm_apply(uuid, text, jsonb) to authenticated;
revoke execute on function public.mm_file_refs(uuid, text) from public, anon;
grant  execute on function public.mm_file_refs(uuid, text) to authenticated;


-- Files for every other tool: private bucket "mm-files", kept under <org_id>/<tool>/...
insert into storage.buckets (id, name, public, file_size_limit)
values ('mm-files', 'mm-files', false, 31457280)          -- private, 30 MB per file
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit;

drop policy if exists mm_files_read   on storage.objects;
drop policy if exists mm_files_insert on storage.objects;
drop policy if exists mm_files_update on storage.objects;
drop policy if exists mm_files_delete on storage.objects;
create policy mm_files_read on storage.objects for select to authenticated
  using (bucket_id = 'mm-files' and private.has_org_role_path((storage.foldername(name))[1]));
create policy mm_files_insert on storage.objects for insert to authenticated
  with check (bucket_id = 'mm-files' and private.has_org_role_path((storage.foldername(name))[1], 'editor'));
create policy mm_files_update on storage.objects for update to authenticated
  using (bucket_id = 'mm-files' and private.has_org_role_path((storage.foldername(name))[1], 'editor'));
create policy mm_files_delete on storage.objects for delete to authenticated
  using (bucket_id = 'mm-files' and private.has_org_role_path((storage.foldername(name))[1], 'editor'));

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

-- ───────────────────────── Live updates ─────────────────────────

do $$ begin
  alter publication supabase_realtime add table public.mm_records;
exception when duplicate_object then null; end $$;

-- ───────────────────────── Admin helper (SQL Editor only) ─────────────────────────
-- select public.mm_add_member('PM1', 'person@example.com', 'editor');
-- Creates the org if needed. The user must already exist (Authentication → Users → Add user).
create or replace function public.mm_add_member(p_org_name text, p_email text, p_role public.org_role default 'editor')
returns text language plpgsql security definer set search_path = '' as $$
declare o uuid; u uuid;
begin
  insert into public.orgs (name) values (p_org_name) on conflict (name) do nothing;
  select id into o from public.orgs where name = p_org_name;
  select id into u from auth.users where lower(email) = lower(p_email);
  if u is null then raise exception 'No user with email % — add them under Authentication → Users first', p_email; end if;
  insert into public.memberships (org_id, user_id, role) values (o, u, p_role)
  on conflict (org_id, user_id) do update set role = excluded.role;
  return format('%s is %s in %s', p_email, p_role, p_org_name);
end $$;
revoke execute on function public.mm_add_member(text, text, public.org_role) from public, anon, authenticated;
