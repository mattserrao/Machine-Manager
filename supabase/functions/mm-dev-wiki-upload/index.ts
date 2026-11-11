// Dev only (branch wiki-memory): load a trained wiki + memory into llm.wiki_* / llm.memory for the token's org.
//   POST { action: 'build', checkpoint, lint, layout?, note? }                 -> { build_id }   (new candidate build)
//   POST { action: 'pages', build_id, pages: [{slug,path,type,title,description,aliases,body,bytes,source_bytes,citations,conflicts,open_q}] }
//   POST { action: 'links', build_id, links: [{from_slug,to_slug,weight,relation,is_redlink}] }
//   POST { action: 'memory', items: [{topic,title,body,kind,source}] }        (replaces the org's memory topics)
//   POST { action: 'live', build_id }                                          (marks it live, retires older builds)
import { createClient } from 'npm:@supabase/supabase-js@2';
const svc = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!, { auth: { persistSession: false } });
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { 'Content-Type': 'application/json' } });
Deno.serve(async (req) => {
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);
  const token = req.headers.get('x-mm-ingest-token') ?? '';
  const { data: org } = token ? await svc.rpc('mm_llm_token_org', { p_token: token }) : { data: null };
  if (!org) return json({ error: 'invalid or expired ingest token' }, 401);
  let b: any; try { b = await req.json(); } catch { return json({ error: 'body must be JSON' }, 400); }
  const { data, error } = await svc.rpc('mm_dev_wiki_load', { p_org: org, p: b });
  return error ? json({ error: error.message }, 400) : json(data ?? { ok: true });
});
