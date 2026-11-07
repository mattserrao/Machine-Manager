-- Machine Manager — Supabase schema
-- Run once in the Supabase dashboard: SQL Editor → New query → paste → Run.
-- Safe to re-run: every statement is idempotent.
--
-- Model
--   orgs          a mill / customer. Everything belongs to exactly one org.
--   memberships   who is in which org, as viewer | editor | admin.
--   wb_boards     Whiteboard boards (one row per board).
--   wb_items      Whiteboard notes, links and frames (one row per item).
--   storage       private bucket "wb-files", files kept under <org_id>/<board_id>/...
--
-- Security
--   Row-level security on every table. A signed-in user only sees rows of orgs
--   they belong to; only editors and admins can write. Accounts and memberships
--   are managed from the dashboard (see SETUP.md), never from the web page.
--
-- Concurrency
--   Every board and item has a version number the database bumps on each write.
--   The page saves through wb_apply(), which only updates a row if the version
--   it last saw is still current. If someone else changed it first, the save is
--   refused and the page shows their version instead (no silent overwrites).
--   Deletes are soft (deleted = true) so they sync live and can be undone.

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

-- ───────────────────────── Whiteboard ─────────────────────────

create table if not exists public.wb_boards (
  id          text primary key,
  org_id      uuid not null references public.orgs(id) on delete cascade,
  name        text not null default 'Board',
  sort        double precision not null default 0,
  deleted     boolean not null default false,
  version     integer not null default 1,
  created_at  timestamptz not null default now(),
  created_by  uuid default auth.uid(),
  updated_at  timestamptz not null default now(),
  updated_by  uuid default auth.uid()
);
create index if not exists wb_boards_org_idx on public.wb_boards(org_id);

create table if not exists public.wb_items (
  board_id    text not null references public.wb_boards(id) on delete cascade,
  id          text not null,
  org_id      uuid not null references public.orgs(id) on delete cascade,
  kind        text not null check (kind in ('note', 'link', 'frame')),
  data        jsonb not null,
  deleted     boolean not null default false,
  version     integer not null default 1,
  updated_at  timestamptz not null default now(),
  updated_by  uuid default auth.uid(),
  primary key (board_id, id)
);
create index if not exists wb_items_org_idx on public.wb_items(org_id);

-- Versions, timestamps and authorship are set by the database, not the page.
create or replace function public.wb_touch() returns trigger language plpgsql set search_path = '' as $$
begin
  if tg_op = 'INSERT' then
    new.version := 1;
  else
    new.version := old.version + 1;
    new.org_id  := old.org_id;                       -- rows can't be moved between orgs
    if tg_table_name = 'wb_items' then
      new.board_id := old.board_id; new.kind := old.kind;
    end if;
  end if;
  new.updated_at := now();
  new.updated_by := auth.uid();
  return new;
end $$;

-- An item always belongs to its board's org (taken from the board, not the page).
create or replace function public.wb_item_org() returns trigger language plpgsql set search_path = '' as $$
begin
  select b.org_id into new.org_id from public.wb_boards b where b.id = new.board_id;
  if new.org_id is null then raise exception 'board % not found', new.board_id using errcode = '23503'; end if;
  return new;
end $$;

drop trigger if exists wb_boards_touch on public.wb_boards;
create trigger wb_boards_touch before insert or update on public.wb_boards
  for each row execute function public.wb_touch();
drop trigger if exists wb_items_org on public.wb_items;
create trigger wb_items_org before insert on public.wb_items
  for each row execute function public.wb_item_org();
drop trigger if exists wb_items_touch on public.wb_items;
create trigger wb_items_touch before insert or update on public.wb_items
  for each row execute function public.wb_touch();

alter table public.wb_boards enable row level security;
alter table public.wb_items  enable row level security;

drop policy if exists wb_boards_read   on public.wb_boards;
drop policy if exists wb_boards_insert on public.wb_boards;
drop policy if exists wb_boards_update on public.wb_boards;
create policy wb_boards_read   on public.wb_boards for select to authenticated using (private.has_org_role(org_id));
create policy wb_boards_insert on public.wb_boards for insert to authenticated with check (private.has_org_role(org_id, 'editor'));
create policy wb_boards_update on public.wb_boards for update to authenticated
  using (private.has_org_role(org_id, 'editor')) with check (private.has_org_role(org_id, 'editor'));

drop policy if exists wb_items_read   on public.wb_items;
drop policy if exists wb_items_insert on public.wb_items;
drop policy if exists wb_items_update on public.wb_items;
create policy wb_items_read   on public.wb_items for select to authenticated using (private.has_org_role(org_id));
create policy wb_items_insert on public.wb_items for insert to authenticated with check (private.has_org_role(org_id, 'editor'));
create policy wb_items_update on public.wb_items for update to authenticated
  using (private.has_org_role(org_id, 'editor')) with check (private.has_org_role(org_id, 'editor'));
-- No delete policies: the page soft-deletes. Hard deletes happen only from the dashboard.

-- Save a batch of changes with version checks. Runs as the caller, so RLS applies.
-- p_changes: [{ kind:'board'|'note'|'link'|'frame', id, board_id?, org_id?, data, deleted, base }]
--   base = version the page last saw, or null for a new row.
-- Returns one result per change: { kind, id, board_id, ok, version } or, on conflict,
-- { ..., ok:false, row: <current row or null if gone / no access> }.
create or replace function public.wb_apply(p_changes jsonb)
returns jsonb language plpgsql security invoker set search_path = '' as $$
declare
  c jsonb; res jsonb := '[]'::jsonb; v integer; cur jsonb; base integer; is_board boolean;
begin
  for c in select * from jsonb_array_elements(p_changes) loop
    v := null; cur := null;
    base := (c->>'base')::integer;
    is_board := c->>'kind' = 'board';
    if is_board then
      if base is null then
        insert into public.wb_boards (id, org_id, name, sort, deleted)
        values (c->>'id', (c->>'org_id')::uuid, coalesce(c->'data'->>'name', 'Board'),
                coalesce((c->'data'->>'sort')::double precision, 0), coalesce((c->>'deleted')::boolean, false))
        on conflict (id) do nothing returning version into v;
      else
        update public.wb_boards set
          name = coalesce(c->'data'->>'name', name),
          sort = coalesce((c->'data'->>'sort')::double precision, sort),
          deleted = coalesce((c->>'deleted')::boolean, deleted)
        where id = c->>'id' and version = base returning version into v;
      end if;
      if v is null then select to_jsonb(b) into cur from public.wb_boards b where b.id = c->>'id'; end if;
    else
      if base is null then
        insert into public.wb_items (board_id, id, kind, data, deleted)
        values (c->>'board_id', c->>'id', c->>'kind', c->'data', coalesce((c->>'deleted')::boolean, false))
        on conflict (board_id, id) do nothing returning version into v;
      else
        update public.wb_items set
          data = coalesce(c->'data', data),
          deleted = coalesce((c->>'deleted')::boolean, deleted)
        where board_id = c->>'board_id' and id = c->>'id' and version = base returning version into v;
      end if;
      if v is null then select to_jsonb(i) into cur from public.wb_items i where i.board_id = c->>'board_id' and i.id = c->>'id'; end if;
    end if;
    res := res || jsonb_build_array(jsonb_build_object(
      'kind', c->>'kind', 'id', c->>'id', 'board_id', c->>'board_id',
      'ok', v is not null, 'version', v, 'row', cur));
  end loop;
  return res;
end $$;

-- ───────────────────────── API access ─────────────────────────
-- Signed-out visitors (the demo) get nothing. Signed-in users go through RLS.

revoke all on public.orgs, public.memberships, public.wb_boards, public.wb_items from anon;
grant select on public.orgs, public.memberships to authenticated;
grant select, insert, update on public.wb_boards, public.wb_items to authenticated;

revoke execute on function public.wb_apply(jsonb) from public, anon;
grant  execute on function public.wb_apply(jsonb) to authenticated;
revoke execute on function private.has_org_role(uuid, public.org_role) from public, anon;
grant  execute on function private.has_org_role(uuid, public.org_role) to authenticated;
revoke execute on function private.has_org_role_path(text, public.org_role) from public, anon;
grant  execute on function private.has_org_role_path(text, public.org_role) to authenticated;
-- Earlier versions kept these helpers in public; take them out of the API.
drop function if exists public.has_org_role(uuid, public.org_role);
drop function if exists public.has_org_role_path(text, public.org_role);

-- ───────────────────────── Live updates ─────────────────────────

do $$ begin
  alter publication supabase_realtime add table public.wb_boards;
exception when duplicate_object then null; end $$;
do $$ begin
  alter publication supabase_realtime add table public.wb_items;
exception when duplicate_object then null; end $$;

-- ───────────────────────── File attachments ─────────────────────────

insert into storage.buckets (id, name, public, file_size_limit)
values ('wb-files', 'wb-files', false, 26214400)          -- private, 25 MB per file
on conflict (id) do update set public = false, file_size_limit = excluded.file_size_limit;

drop policy if exists wb_files_read   on storage.objects;
drop policy if exists wb_files_insert on storage.objects;
drop policy if exists wb_files_update on storage.objects;
create policy wb_files_read on storage.objects for select to authenticated
  using (bucket_id = 'wb-files' and private.has_org_role_path((storage.foldername(name))[1]));
create policy wb_files_insert on storage.objects for insert to authenticated
  with check (bucket_id = 'wb-files' and private.has_org_role_path((storage.foldername(name))[1], 'editor'));
create policy wb_files_update on storage.objects for update to authenticated
  using (bucket_id = 'wb-files' and private.has_org_role_path((storage.foldername(name))[1], 'editor'));

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
