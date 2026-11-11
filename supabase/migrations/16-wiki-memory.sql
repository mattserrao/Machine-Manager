-- 16: Wiki layer + memory (branch wiki-memory). See "MM LLM - Wiki Layer Plan" v0.3 in the Machine Manager Claude project.
--   llm.mcp_calls      every tool call made through mm-mcp-dev with a run id (full output, for the citation check)
--   llm.wiki_builds    one row per uploaded wiki build (checkpoint), with its lint and graph layout
--   llm.wiki_pages     the wiki's pages (Markdown + frontmatter fields), per org and build
--   llm.wiki_links     [[links]] between pages (is_redlink = the target page doesn't exist yet)
--   llm.memory         short process lessons for answering (not facts), per org
-- Pages and memory are read by org members and, for public demo orgs, by anyone (same rules as the other llm tables).
-- Writes: service role only (the upload script); OAuth connected apps stay read-only.

create table if not exists llm.mcp_calls (
  id         bigint generated always as identity primary key,
  run_id     text not null,
  org_id     uuid,
  tool       text not null,
  args       jsonb,
  output     text,          -- the JSON the model saw (full, before the 20k cut)
  rows       int,
  error      text,
  ms         int,
  created_at timestamptz not null default now()
);
create index if not exists mcp_calls_run on llm.mcp_calls (run_id, id);
alter table llm.mcp_calls enable row level security;   -- service role only

create table if not exists llm.wiki_builds (
  id          bigint generated always as identity primary key,
  org_id      uuid not null,
  checkpoint  text not null,             -- e.g. ck3
  status      text not null default 'candidate' check (status in ('candidate', 'live', 'retired')),
  pages       int, links int, redlinks int, bytes int, source_bytes bigint,
  lint        jsonb,
  layout      jsonb,                     -- cached graph positions {slug: [x, y]}
  note        text,
  created_at  timestamptz not null default now()
);
create table if not exists llm.wiki_pages (
  build_id     bigint not null references llm.wiki_builds(id) on delete cascade,
  org_id       uuid not null,
  slug         text not null,
  path         text not null,
  type         text,                     -- position, equipment, outage, failure-mode, document, topic, ... ; root for _index etc.
  title        text,
  description  text,
  aliases      text[] not null default '{}',
  body         text not null,
  bytes        int not null,
  source_bytes int,                      -- size of the sources the page cites (for the size-ratio view)
  citations    int not null default 0,
  conflicts    int not null default 0,
  open_q       int not null default 0,
  use_count    int not null default 0,
  fts          tsvector generated always as (to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '') || ' ' || body)) stored,
  primary key (build_id, slug)
);
create index if not exists wiki_pages_fts on llm.wiki_pages using gin (fts);
create table if not exists llm.wiki_links (
  build_id   bigint not null references llm.wiki_builds(id) on delete cascade,
  org_id     uuid not null,
  from_slug  text not null,
  to_slug    text not null,
  weight     int not null default 1,
  relation   text,
  is_redlink boolean not null default false,
  primary key (build_id, from_slug, to_slug)
);
create table if not exists llm.memory (
  id          bigint generated always as identity primary key,
  org_id      uuid not null,
  scope       text not null default 'org' check (scope in ('org', 'user', 'position')),
  kind        text not null default 'lesson' check (kind in ('fact', 'decision', 'preference', 'glossary', 'lesson')),
  topic       text not null,             -- file stem, e.g. tool-ids
  title       text,
  body        text not null,
  status      text not null default 'approved' check (status in ('proposed', 'approved', 'retired')),
  source      text,                      -- e.g. training checkpoint ck3
  created_at  timestamptz not null default now(),
  unique (org_id, topic)
);

do $$ declare t text; begin
  foreach t in array array['wiki_builds', 'wiki_pages', 'wiki_links', 'memory'] loop
    execute format('alter table llm.%I enable row level security', t);
    execute format('drop policy if exists %I on llm.%I', t || '_read', t);
    execute format('drop policy if exists %I on llm.%I', t || '_public_read', t);
    execute format('create policy %I on llm.%I for select to authenticated using (private.has_org_role(org_id) or private.llm_is_public(org_id))', t || '_read', t);
    execute format('create policy %I on llm.%I for select to anon using (private.llm_is_public(org_id))', t || '_public_read', t);
    execute format('grant select on llm.%I to authenticated, anon', t);
  end loop;
end $$;

-- The live build for an org (the newest 'live', else the newest candidate).
create or replace function private.wiki_build(p_org uuid) returns bigint
language sql stable security definer set search_path = '' as $$
  select id from llm.wiki_builds where org_id = p_org and status in ('live', 'candidate')
  order by (status = 'live') desc, id desc limit 1 $$;
revoke execute on function private.wiki_build(uuid) from public;

-- ---------- read tools (same names as the mm-mcp-dev / mm-llm-ask-dev tools) ----------
create or replace function public.mm_wiki_index(p_org uuid, p_kind text default null) returns table (slug text, type text, title text, description text, body text)
language sql stable security invoker set search_path = '' as $$
  select p.slug, p.type, p.title, p.description, case when p.slug = '_index' then p.body else null end
  from llm.wiki_pages p where p.build_id = private.wiki_build(p_org) and p.org_id = p_org
    and (p.slug = '_index' or (p_kind is not null and p.type = p_kind))
  order by (p.slug = '_index') desc, p.slug $$;

create or replace function public.mm_wiki_read(p_org uuid, p_slug text, p_section text default null) returns table (slug text, type text, title text, text text, bytes int)
language sql stable security invoker set search_path = '' as $$
  with pg as (select * from llm.wiki_pages p where p.build_id = private.wiki_build(p_org) and p.org_id = p_org
                and (p.slug = lower(p_slug) or lower(p_slug) = any (select lower(a) from unnest(p.aliases) a)) limit 1)
  select pg.slug, pg.type, pg.title,
    case when p_section is null or p_section = '' then pg.body
         else coalesce((select string_agg(s, E'\n## ') from regexp_split_to_table(pg.body, E'\n## ') s
                        where lower(split_part(s, E'\n', 1)) like '%' || lower(p_section) || '%'), '(no section "' || p_section || '"; sections: '
                        || (select string_agg(split_part(s, E'\n', 1), ' | ') from regexp_split_to_table(pg.body, E'\n## ') s offset 1) || ')') end,
    pg.bytes
  from pg $$;

create or replace function public.mm_wiki_search(p_org uuid, p_query text, p_limit int default 8) returns table (slug text, type text, title text, description text, lines text)
language sql stable security invoker set search_path = '' as $$
  with q as (select websearch_to_tsquery('english', p_query) tq, regexp_split_to_array(lower(p_query), '\W+') words),
  hits as (
    select p.*, ts_rank(p.fts, q.tq) r from llm.wiki_pages p, q
    where p.build_id = private.wiki_build(p_org) and p.org_id = p_org and (p.fts @@ q.tq
       or exists (select 1 from unnest(q.words) w where length(w) > 3 and lower(p.title || ' ' || coalesce(p.description, '')) like '%' || w || '%'))
    order by r desc limit greatest(1, least(p_limit, 15)))
  select h.slug, h.type, h.title, h.description,
    (select string_agg(l, E'\n') from (select l from regexp_split_to_table(h.body, E'\n') l, q
       where exists (select 1 from unnest(q.words) w where length(w) > 3 and lower(l) like '%' || w || '%') limit 4) x)
  from hits h order by h.r desc $$;

create or replace function public.mm_wiki_neighbors(p_org uuid, p_slug text) returns table (direction text, slug text, title text, weight int, relation text, redlink boolean)
language sql stable security invoker set search_path = '' as $$
  select 'out', l.to_slug, p.title, l.weight, l.relation, l.is_redlink from llm.wiki_links l
    left join llm.wiki_pages p on p.build_id = l.build_id and p.slug = l.to_slug
    where l.build_id = private.wiki_build(p_org) and l.org_id = p_org and l.from_slug = lower(p_slug)
  union all
  select 'in', l.from_slug, p.title, l.weight, l.relation, false from llm.wiki_links l
    join llm.wiki_pages p on p.build_id = l.build_id and p.slug = l.from_slug
    where l.build_id = private.wiki_build(p_org) and l.org_id = p_org and l.to_slug = lower(p_slug)
  order by 1, 4 desc $$;

create or replace function public.mm_memory_index(p_org uuid) returns table (topic text, title text, lines int)
language sql stable security invoker set search_path = '' as $$
  select m.topic, m.title, array_length(regexp_split_to_array(m.body, E'\n'), 1) from llm.memory m
  where m.org_id = p_org and m.status = 'approved' order by m.topic $$;

create or replace function public.mm_memory_read(p_org uuid, p_topic text) returns table (topic text, title text, body text)
language sql stable security invoker set search_path = '' as $$
  select m.topic, m.title, m.body from llm.memory m where m.org_id = p_org and m.status = 'approved' and m.topic = lower(p_topic) $$;

-- The graph for the Wiki page: nodes and edges of the build (default: the live one).
create or replace function public.mm_wiki_graph(p_org uuid, p_build bigint default null) returns jsonb
language sql stable security invoker set search_path = '' as $$
  with b as (select coalesce(p_build, private.wiki_build(p_org)) id)
  select jsonb_build_object(
    'build', (select to_jsonb(w) - 'layout' from llm.wiki_builds w, b where w.id = b.id),
    'builds', (select jsonb_agg(jsonb_build_object('id', id, 'checkpoint', checkpoint, 'status', status, 'pages', pages, 'links', links) order by id) from llm.wiki_builds where org_id = p_org),
    'layout', (select w.layout from llm.wiki_builds w, b where w.id = b.id),
    'nodes', coalesce((select jsonb_agg(jsonb_build_object('slug', p.slug, 'type', p.type, 'title', p.title, 'description', p.description,
       'bytes', p.bytes, 'source_bytes', p.source_bytes, 'citations', p.citations, 'conflicts', p.conflicts, 'open_q', p.open_q,
       'use_count', p.use_count)) from llm.wiki_pages p, b where p.build_id = b.id and p.org_id = p_org), '[]'),
    'edges', coalesce((select jsonb_agg(jsonb_build_object('from', l.from_slug, 'to', l.to_slug, 'weight', l.weight, 'relation', l.relation,
       'redlink', l.is_redlink)) from llm.wiki_links l, b where l.build_id = b.id and l.org_id = p_org), '[]')) $$;

create or replace function public.mm_wiki_page(p_org uuid, p_slug text, p_build bigint default null) returns jsonb
language sql stable security invoker set search_path = '' as $$
  select to_jsonb(p) - 'fts' from llm.wiki_pages p
  where p.build_id = coalesce(p_build, private.wiki_build(p_org)) and p.org_id = p_org and p.slug = p_slug $$;

grant execute on function public.mm_wiki_index(uuid, text), public.mm_wiki_read(uuid, text, text), public.mm_wiki_search(uuid, text, int),
  public.mm_wiki_neighbors(uuid, text), public.mm_memory_index(uuid), public.mm_memory_read(uuid, text),
  public.mm_wiki_graph(uuid, bigint), public.mm_wiki_page(uuid, text, bigint) to authenticated, anon;
grant execute on function private.wiki_build(uuid) to authenticated, anon;

-- Call log access for mm-mcp-dev (service role only; llm is not exposed over the REST API).
create or replace function public.mm_mcp_log(p jsonb) returns void
language sql security definer set search_path = '' as $$
  insert into llm.mcp_calls (run_id, org_id, tool, args, output, rows, error, ms)
  values (p->>'run_id', nullif(p->>'org_id','')::uuid, p->>'tool', p->'args', p->>'output', (p->>'rows')::int, p->>'error', (p->>'ms')::int) $$;
create or replace function public.mm_mcp_calls(p_run text) returns table (tool text, args jsonb, output text, rows int, error text, ms int)
language sql stable security definer set search_path = '' as $$
  select tool, args, output, rows, error, ms from llm.mcp_calls where run_id = p_run order by id $$;
revoke execute on function public.mm_mcp_log(jsonb), public.mm_mcp_calls(text) from public, anon, authenticated;
grant execute on function public.mm_mcp_log(jsonb), public.mm_mcp_calls(text) to service_role;

-- mm-mcp-dev /export: raw rows of one org's table, for building the wiki corpus. Service role only.
create or replace function public.mm_dev_export(p_org uuid, p_table text, p_offset int default 0, p_limit int default 500) returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare r jsonb; cols text;
begin
  if p_table not in ('documents','doc_pages','doc_chunks','reports','work_orders','bus_items','rcfa','actions','downtime',
                     'position_runs','outages','equipment','bonvoy','bonvoy_reports','pi_tags','production_daily') then
    raise exception 'table not allowed';
  end if;
  select string_agg(quote_ident(column_name), ', ' order by ordinal_position) into cols from information_schema.columns
   where table_schema = 'llm' and table_name = p_table and data_type not in ('USER-DEFINED', 'tsvector') and column_name not in ('embedding', 'fts');
  execute format('select coalesce(jsonb_agg(to_jsonb(t)), ''[]'') from (select %s from llm.%I where org_id = $1 order by ctid offset $2 limit $3) t', cols, p_table)
    into r using p_org, p_offset, p_limit;
  return r;
end $$;
revoke execute on function public.mm_dev_export(uuid, text, int, int) from public, anon, authenticated;
grant execute on function public.mm_dev_export(uuid, text, int, int) to service_role;

-- 16e. Loader for the dev upload function (mm-dev-wiki-upload): one call per action. service_role only.
create or replace function public.mm_dev_wiki_load(p_org uuid, p jsonb)
returns jsonb language plpgsql security definer set search_path to '' as $function$
declare bid bigint; n int;
begin
  if p->>'action' = 'build' then
    insert into llm.wiki_builds (org_id, checkpoint, lint, layout, note, pages, links, redlinks, bytes, source_bytes)
    values (p_org, p->>'checkpoint', p->'lint', p->'layout', p->>'note', (p->'lint'->>'pages')::int, (p->'lint'->>'links')::int,
            (p->'lint'->>'redlinks')::int, (p->'lint'->>'wiki_bytes')::int, (p->'lint'->>'source_bytes')::bigint) returning id into bid;
    return jsonb_build_object('build_id', bid);
  elsif p->>'action' = 'pages' then
    bid := (p->>'build_id')::bigint;
    if not exists (select 1 from llm.wiki_builds where id = bid and org_id = p_org) then raise exception 'build not in this org'; end if;
    insert into llm.wiki_pages (build_id, org_id, slug, path, type, title, description, aliases, body, bytes, source_bytes, citations, conflicts, open_q)
    select bid, p_org, x->>'slug', x->>'path', x->>'type', x->>'title', x->>'description',
           coalesce((select array_agg(a) from jsonb_array_elements_text(x->'aliases') a), '{}'), x->>'body', (x->>'bytes')::int,
           nullif(x->>'source_bytes','')::int, coalesce((x->>'citations')::int,0), coalesce((x->>'conflicts')::int,0), coalesce((x->>'open_q')::int,0)
    from jsonb_array_elements(p->'pages') x
    on conflict (build_id, slug) do update set body = excluded.body, bytes = excluded.bytes, title = excluded.title, description = excluded.description,
      type = excluded.type, aliases = excluded.aliases, citations = excluded.citations, conflicts = excluded.conflicts;
    get diagnostics n = row_count; return jsonb_build_object('pages', n);
  elsif p->>'action' = 'links' then
    bid := (p->>'build_id')::bigint;
    if not exists (select 1 from llm.wiki_builds where id = bid and org_id = p_org) then raise exception 'build not in this org'; end if;
    insert into llm.wiki_links (build_id, org_id, from_slug, to_slug, weight, relation, is_redlink)
    select bid, p_org, x->>'from_slug', x->>'to_slug', coalesce((x->>'weight')::int,1), x->>'relation', coalesce((x->>'is_redlink')::boolean,false)
    from jsonb_array_elements(p->'links') x on conflict do nothing;
    get diagnostics n = row_count; return jsonb_build_object('links', n);
  elsif p->>'action' = 'memory' then
    delete from llm.memory where org_id = p_org;
    insert into llm.memory (org_id, scope, kind, topic, title, body, status, source)
    select p_org, 'org', coalesce(x->>'kind','lesson'), x->>'topic', x->>'title', x->>'body', 'approved', x->>'source' from jsonb_array_elements(p->'items') x;
    get diagnostics n = row_count; return jsonb_build_object('memory', n);
  elsif p->>'action' = 'live' then
    bid := (p->>'build_id')::bigint;
    update llm.wiki_builds set status = case when id = bid then 'live' else 'retired' end where org_id = p_org and status <> 'retired' or id = bid;
    return jsonb_build_object('live', bid);
  end if;
  raise exception 'unknown action';
end $function$;
revoke all on function public.mm_dev_wiki_load(uuid, jsonb) from public, anon, authenticated;
grant execute on function public.mm_dev_wiki_load(uuid, jsonb) to service_role;
