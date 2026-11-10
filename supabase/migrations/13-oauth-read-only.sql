-- Step 13: OAuth for MM MCP. Connected apps (Claude's custom connector, other MCP clients) sign users in through
-- Supabase's OAuth 2.1 server; their access tokens carry a client_id claim. This step makes those tokens read-only:
--   - private.is_oauth_client(): true for an OAuth client's token;
--   - has_org_role / has_org_role_path: only 'viewer' checks pass for one, so every editor write (mm_apply, files,
--     reviews) is refused;
--   - RAG uploads (storage policy and mm_rag_register) refuse them;
--   - mm_llm_my_access returns nothing for them, so a connected app can't spend live MM LLM questions.
-- The user's own sessions (no client_id) are unchanged. Same statements as ../schema.sql and ../llm.sql. Safe to run again.

create or replace function private.is_oauth_client()
returns boolean language sql stable set search_path = '' as $$
  select coalesce((select auth.jwt()) ->> 'client_id', '') <> '';
$$;

revoke execute on function private.is_oauth_client() from public;
grant  execute on function private.is_oauth_client() to authenticated, anon;

create or replace function private.has_org_role(p_org uuid, p_min public.org_role default 'viewer')
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.memberships m
    where m.org_id = p_org and m.user_id = (select auth.uid()) and m.role >= p_min
  ) and (p_min = 'viewer' or not private.is_oauth_client());
$$;

create or replace function private.has_org_role_path(p_org text, p_min public.org_role default 'viewer')
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.memberships m
    where m.org_id::text = p_org and m.user_id = (select auth.uid()) and m.role >= p_min
  ) and (p_min = 'viewer' or not private.is_oauth_client());
$$;

create or replace function private.rag_can_upload_path(p_org text)
returns boolean language sql stable security definer set search_path = '' as $$
  select private.has_org_role_path(p_org) and not private.llm_is_public_path(p_org) and not private.is_oauth_client();
$$;

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
  where q.user_id = (select auth.uid()) and not private.is_oauth_client();   -- connected apps can't spend live questions
$$;

create or replace function public.mm_rag_register(p_org uuid, p_path text, p_file_name text, p_sha256 text,
  p_size bigint, p_pages int, p_kind text default null, p_vendor text default null, p_doc_date date default null,
  p_positions text[] default '{}')
returns jsonb language plpgsql security definer set search_path = '' as $$
declare v_uid uuid := (select auth.uid()); v_set llm.rag_settings; v_doc text; v_dup record; v_today bigint;
begin
  if v_uid is null or not private.has_org_role(p_org) then raise exception 'Sign in as a member of this organization to upload.'; end if;
  if private.is_oauth_client() then raise exception 'Connected apps (OAuth) have read-only access; upload from the RAG page.'; end if;
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
