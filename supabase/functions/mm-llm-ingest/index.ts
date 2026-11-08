// MM LLM ingest helper (Supabase Edge Function).
// The only way in for imports: loads rows (through public.mm_llm_ingest), stores original files in the private
// mm-files bucket, and embeds document chunks. Every call needs an ingest token (header x-mm-ingest-token);
// the token decides the organization. Runs with the service role inside Supabase.
//
//   POST { action: 'rows', table, rows: [...], mode: 'upsert' | 'reset' }   -> public.mm_llm_ingest
//   POST { action: 'upload', path: 'docs/vendor/x/y.pdf', contentType, data: <base64> }   -> <org>/llm/<path>
//   POST { action: 'embed', limit: 6 }        embeds chunks that have no embedding yet (gte-small, 384 dims;
//                                             keep batches small, larger ones hit the function's compute limit)
//
// Deployed with verify_jwt off: the ingest token is the credential.
import { createClient } from 'npm:@supabase/supabase-js@2';

const sb = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!, { auth: { persistSession: false } });
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
const MODEL = 'gte-small';
let session: any = null;

Deno.serve(async (req) => {
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);
  const token = req.headers.get('x-mm-ingest-token') ?? '';
  const { data: org, error: e1 } = await sb.rpc('mm_llm_token_org', { p_token: token });
  if (e1 || !org) return json({ error: 'invalid or expired ingest token' }, 401);
  let body: any;
  try { body = await req.json(); } catch { return json({ error: 'body must be JSON' }, 400); }

  if (body.action === 'rows') {
    const { data: n, error } = await sb.rpc('mm_llm_ingest', { p_token: token, p_table: String(body.table ?? ''),
      p_rows: body.rows ?? [], p_mode: body.mode === 'reset' ? 'reset' : 'upsert' });
    return error ? json({ error: error.message }, 400) : json({ rows: n });
  }

  if (body.action === 'upload') {
    const path = String(body.path ?? '');
    if (!path || path.includes('..') || path.startsWith('/') || path.length > 300) return json({ error: 'bad path' }, 400);
    const bytes = Uint8Array.from(atob(String(body.data ?? '')), (c) => c.charCodeAt(0));
    if (bytes.length > 25 * 1024 * 1024) return json({ error: 'file over 25 MB' }, 413);
    const { error } = await sb.storage.from('mm-files').upload(`${org}/llm/${path}`, bytes,
      { contentType: String(body.contentType ?? 'application/octet-stream'), upsert: true });
    return error ? json({ error: error.message }, 500) : json({ ok: true, path: `${org}/llm/${path}` });
  }

  if (body.action === 'embed') {
    const limit = Math.min(Number(body.limit) || 6, 20);
    const { data: rows, error } = await sb.rpc('mm_llm_chunks_to_embed', { p_org: org, p_limit: limit });
    if (error) return json({ error: error.message }, 500);
    if (!rows?.length) return json({ embedded: 0 });
    // @ts-ignore Supabase.ai is provided by the Edge Runtime
    session ??= new Supabase.ai.Session(MODEL);
    const out = [];
    for (const r of rows) {
      const v = await session.run(r.content, { mean_pool: true, normalize: true });
      out.push({ doc_id: r.doc_id, chunk_no: r.chunk_no, embedding: `[${Array.from(v as number[]).join(',')}]` });
    }
    const { data: n, error: e2 } = await sb.rpc('mm_llm_set_embeddings', { p_org: org, p_model: MODEL, p_rows: out });
    return e2 ? json({ error: e2.message }, 500) : json({ embedded: n });
  }

  return json({ error: 'unknown action' }, 400);
});
