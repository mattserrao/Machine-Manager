-- Step 11: what the RAG worker (mm-rag-process), the RAG page and the MCP server need on top of step 10.
--   - mm_my_orgs(): the signed-in user's own organizations with their role and whether they're public, so the RAG
--     page can pick the user's private org and the MCP server can read orgs the user belongs to.
--   - mm_rag_add_pages / mm_rag_requeue: large PDFs are parsed in page batches, one batch per worker call.
--   - mm_rag_chunks_to_embed: chunks of indexed documents still waiting for an embedding, across orgs.
--   - pg_net, so pg_cron can call the worker (the schedule itself is set up once in the SQL editor, see below).
-- Only adds. Safe to run again. The same statements are appended to ../llm.sql (end state).
--
-- Admin (SQL editor), once, after deploying mm-rag-process. <anon key> is the project's publishable key:
--   select cron.schedule('mm-rag-process', '15 seconds', $$select net.http_post(
--     url := 'https://<project>.supabase.co/functions/v1/mm-rag-process',
--     headers := '{"Content-Type": "application/json", "Authorization": "Bearer <anon key>"}'::jsonb,
--     body := '{"source": "cron"}'::jsonb, timeout_milliseconds := 5000)$$);

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
