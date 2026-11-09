// MM LLM ingest helper (Supabase Edge Function).
// The only way in for imports: loads rows (through public.mm_llm_ingest), stores original files in the private
// mm-files bucket, and embeds document chunks. Every call needs an ingest token (header x-mm-ingest-token);
// the token decides the organization. Runs with the service role inside Supabase.
//
//   POST { action: 'rows', table, rows: [...], mode: 'upsert' | 'reset' }   -> public.mm_llm_ingest
//   POST { action: 'upload', path: 'docs/vendor/x/y.pdf', contentType, data: <base64> }   -> <org>/llm/<path>
//   POST { action: 'process', limit: 500 }   extracts and indexes ingested reports (public.mm_llm_process_reports):
//                                             { picked, extracted, failed }; call until picked is 0
//   POST { action: 'embed', limit: 6 }        embeds chunks that have no embedding yet (gte-small, 384 dims;
//                                             keep batches small, larger ones hit the function's compute limit)
//   POST { action: 'prune', keep: [paths] }   removes the org's stored files under <org>/llm/ that aren't in keep
//                                             (paths as uploaded): after a reload, the files the new load didn't send
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

  if (body.action === 'process') {
    const { data, error } = await sb.rpc('mm_llm_process_reports', { p_token: token, p_limit: Math.min(Number(body.limit) || 500, 2000) });
    return error ? json({ error: error.message }, 400) : json(data);
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

  if (body.action === 'prune') {
    if (!Array.isArray(body.keep) || !body.keep.length) return json({ error: 'keep must list the files to keep' }, 400);
    const keep = new Set(body.keep.map((p: unknown) => `${org}/llm/${String(p)}`));
    const all: string[] = [];
    const walk = async (prefix: string): Promise<void> => {
      for (let offset = 0; ; offset += 1000) {
        const { data, error } = await sb.storage.from('mm-files').list(prefix, { limit: 1000, offset });
        if (error) throw error;
        for (const o of data ?? []) {
          const p = `${prefix}/${o.name}`;
          if (o.id == null) await walk(p); else all.push(p);
        }
        if (!data || data.length < 1000) return;
      }
    };
    try { await walk(`${org}/llm`); } catch (e) { return json({ error: (e as Error).message }, 500); }
    const gone = all.filter((p) => !keep.has(p));
    for (let i = 0; i < gone.length; i += 100) {
      const { error } = await sb.storage.from('mm-files').remove(gone.slice(i, i + 100));
      if (error) return json({ error: error.message, removed: i }, 500);
    }
    return json({ removed: gone.length, kept: all.length - gone.length });
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
