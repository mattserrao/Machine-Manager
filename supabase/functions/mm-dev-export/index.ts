// Dev only (branch wiki-memory): raw rows of one org's llm table, for building the wiki corpus. Read-only.
//   POST { org, table, offset?, limit? }  with  x-mm-ingest-token: <token of that org>   ->  { rows }
import { createClient } from 'npm:@supabase/supabase-js@2';
const svc = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!, { auth: { persistSession: false } });
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { 'Content-Type': 'application/json' } });
Deno.serve(async (req) => {
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);
  const token = req.headers.get('x-mm-ingest-token') ?? '';
  const { data: org } = token ? await svc.rpc('mm_llm_token_org', { p_token: token }) : { data: null };
  if (!org) return json({ error: 'invalid or expired ingest token' }, 401);
  let b: any; try { b = await req.json(); } catch { return json({ error: 'body must be JSON' }, 400); }
  const { data, error } = await svc.rpc('mm_dev_export', { p_org: org, p_table: String(b.table ?? ''), p_offset: Number(b.offset ?? 0), p_limit: Math.min(Number(b.limit ?? 500), 2000) });
  return error ? json({ error: error.message }, 400) : json({ rows: data ?? [] });
});
