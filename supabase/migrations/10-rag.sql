-- Step 10: drop-in documents for the RAG (see project doc "MM RAG - PDF Drop-in Plan").
-- Any member of a private org (viewer and up) can upload a PDF to <org>/rag/inbox/ and register it; the
-- mm-rag-process edge function (service role) parses, assesses, gates and indexes it; editors review.
-- Public demo orgs are read-only: nothing can be uploaded there, because everything in them is public.
-- Only adds. Safe to run again. The same statements are appended to ../llm.sql (end state).
--
-- Admin (SQL editor), the private test org for the demo account:
--   select public.mm_add_member('Demodemo RAG', 'demodemo@gmail.com', 'editor');
--   select public.mm_llm_grant_query('demodemo@gmail.com', 'Demodemo RAG', 40);   -- optional: live questions

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
