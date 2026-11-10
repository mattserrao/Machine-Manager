// MM RAG worker (Supabase Edge Function): takes uploaded PDFs from the queue (llm.rag_jobs) through
//   parse  → page text from the PDF's text layer; pages that are scans or garbled are read by Claude (in batches)
//   assess → quality signals + one Claude check (kind, vendor, date, positions, summary, relevance …) → score → gate:
//            accepted (indexed next), needs_review (an editor decides on the RAG page) or rejected
//   index  → chunks with a context header, tagged with machine positions; embeddings follow a few at a time
// Each call does one job step (a parse step is at most PAGE_BATCH pages) so it stays inside the CPU limit, then, if
// it did nothing else, embeds a few waiting chunks (EMBED_BATCH). pg_cron calls it every 15 s (migration 11); the RAG page also calls
// it right after an upload so work starts at once. Calls are safe to overlap: jobs are claimed with skip-locked.
//
//   POST {}  ->  { job?: { id, step, doc_id, result }, embedded }
// Deployed with verify_jwt on (the anon key is enough): a call only drains the queue, and only members can add to it.
// Secrets: ANTHROPIC_API_KEY (shared with mm-llm-ask). Model per org in llm.rag_settings (default claude-haiku-5-5).
import { createClient } from 'npm:@supabase/supabase-js@2';
import { PAGE_BATCH, MODEL_PAGE_CAP, PARSE_PROMPT, NOTES_PROMPT, isRefusal, needsModel, garbleRate, splitModelPages, assessPrompt, parseJson,
         cleanAssessment, score, contextHeader, chunkPages, tagPositions, isPdf, type Page } from './rag.ts';

const sb = createClient(Deno.env.get('SUPABASE_URL')!, Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!, { auth: { persistSession: false } });
const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, apikey, content-type, x-client-info',
               'Access-Control-Allow-Methods': 'POST, OPTIONS' };
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { ...cors, 'Content-Type': 'application/json' } });
const EMBED_MODEL = 'gte-small', EMBED_BATCH = 3;   // 6 per call ran out of compute
let embedder: any = null;
const embed = async (text: string): Promise<number[]> => {
  // @ts-ignore Supabase.ai is provided by the Edge Runtime
  embedder ??= new Supabase.ai.Session(EMBED_MODEL);
  return Array.from(await embedder.run(text, { mean_pool: true, normalize: true }) as number[]);
};

function apiKey(): string {   // pasted secrets can carry quotes or invisible characters (same clean-up as mm-llm-ask)
  return (Deno.env.get('ANTHROPIC_API_KEY') ?? '').replace(/[^\x21-\x7e]/g, '').replace(/^['"]+|['"]+$/g, '');
}
class Permanent extends Error {}   // no point retrying (not a PDF, encrypted, file gone)

async function rpc(fn: string, args: Record<string, unknown>) {
  const { data, error } = await sb.rpc(fn, args);
  if (error) throw new Error(`${fn}: ${error.message}`);
  return data;
}

// One Claude call with a couple of retries on overload / rate limits.
async function claude(model: string, content: unknown[], maxTokens: number) {
  const key = apiKey();
  if (!key) throw new Error('ANTHROPIC_API_KEY is not set');
  for (let attempt = 0; ; attempt++) {
    const r = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json' },
      body: JSON.stringify({ model, max_tokens: maxTokens, messages: [{ role: 'user', content }] }),
    });
    const j = await r.json().catch(() => ({}));
    if (r.ok) return { text: (j.content ?? []).filter((b: any) => b.type === 'text').map((b: any) => b.text).join('\n'),
                       inT: j.usage?.input_tokens ?? 0, outT: j.usage?.output_tokens ?? 0 };
    if ((r.status === 429 || r.status >= 500) && attempt < 2) { await new Promise((ok) => setTimeout(ok, 2000 * (attempt + 1))); continue; }
    throw new Error(`Claude ${r.status}: ${j?.error?.message ?? 'no detail'}`);
  }
}
const b64 = (bytes: Uint8Array) => { let s = ''; for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode(...bytes.subarray(i, i + 0x8000)); return btoa(s); };

// ---------- parse: one batch of pages ----------
async function parse(job: any, ctx: any) {
  const doc = ctx.doc, set = ctx.settings, prog = job.usage?.next_page ? job.usage : null;
  const { data: file, error } = await sb.storage.from('mm-files').download(doc.file_path);
  if (error || !file) throw new Permanent(`The uploaded file is missing (${doc.file_path}).`);
  const bytes = new Uint8Array(await file.arrayBuffer());
  if (!isPdf(bytes)) throw new Permanent('This file is not a PDF.');
  // The PDF libraries load only for a parse step, so embedding calls stay small (the runtime's memory and CPU limits).
  const { getDocumentProxy } = await import('npm:unpdf@1');
  let pdf: any;
  try { pdf = await getDocumentProxy(bytes.slice()); }   // a copy: PDF.js takes over the buffer it is given
  catch (e) { const m = String((e as Error)?.message ?? e); throw new Permanent(/password/i.test(m) ? 'The PDF is password-protected.' : `The PDF can't be read: ${m.slice(0, 160)}`); }
  const n = pdf.numPages;
  if (!prog) await rpc('mm_rag_save_pages', { p_org: job.org_id, p_doc: job.doc_id, p_pages: [] });   // a fresh parse
  const start = prog?.next_page ?? 1, end = Math.min(n, start + PAGE_BATCH - 1);
  let modelPages = prog?.model_pages ?? 0, notesPages = prog?.notes_pages ?? 0, inT = prog?.in ?? 0, outT = prog?.out ?? 0;

  const pages: Page[] = [];
  for (let i = start; i <= end; i++) {
    const page = await pdf.getPage(i);
    const tc = await page.getTextContent();
    const text = tc.items.map((it: any) => (it.str ?? '') + (it.hasEOL ? '\n' : ' ')).join('').replace(/[ \t]+\n/g, '\n').trim();
    pages.push({ page: i, text, text_source: 'layer', rotation: page.rotate ?? 0 });
  }
  const hard = pages.filter((p) => needsModel(p.text)).slice(0, Math.max(0, MODEL_PAGE_CAP - modelPages));
  if (hard.length && apiKey()) {
    const { PDFDocument } = await import('npm:pdf-lib@1.17.1');
    const src = await PDFDocument.load(bytes, { ignoreEncryption: true });
    const sub = await PDFDocument.create();
    for (const p of await sub.copyPages(src, hard.map((h) => h.page - 1))) sub.addPage(p);
    const docBlock = { type: 'document', source: { type: 'base64', media_type: 'application/pdf', data: b64(await sub.save()) } };
    const max = Math.min(16000, 1500 * hard.length + 500);
    let r;
    try { r = await claude(set.model, [docBlock, { type: 'text', text: PARSE_PROMPT }], max); }
    catch (e) {
      if (!isRefusal((e as Error).message)) throw e;
      r = await claude(set.model, [docBlock, { type: 'text', text: NOTES_PROMPT }], max);   // a published text: notes, not a copy
      notesPages += hard.length;
    }
    inT += r.inT; outT += r.outT; modelPages += hard.length;
    const got = splitModelPages(r.text, hard.map((h) => h.page));
    for (const p of pages) {
      const t = got.get(p.page);
      if (t && t.replace(/\s/g, '').length > p.text.replace(/\s/g, '').length * 0.6) { p.text = t; p.text_source = 'model'; }
    }
  }
  for (const p of pages) p.garble = Number(garbleRate(p.text).toFixed(3));
  await rpc('mm_rag_add_pages', { p_org: job.org_id, p_doc: job.doc_id, p_pages: pages });

  const usage = { next_page: end + 1, pages: n, model_pages: modelPages, notes_pages: notesPages, in: inT, out: outT };
  if (end < n) { await rpc('mm_rag_requeue', { p_job: job.id, p_progress: usage }); return `pages ${start}-${end} of ${n}`; }
  const src = modelPages === 0 ? 'text' : modelPages >= n ? 'model' : 'mixed';
  return await rpc('mm_rag_finish', { p_job: job.id, p_ok: true, p_to: 'parsed', p_doc_patch: { text_source: src }, p_usage: usage });
}

// ---------- assess: signals + Claude check → score → gate ----------
async function assess(job: any, ctx: any) {
  const doc = ctx.doc, set = ctx.settings, pages: Page[] = ctx.pages ?? [];
  const { data: mctx } = await sb.rpc('mm_llm_context', { p_org: job.org_id });
  const positions: { id: string; name: string }[] = (mctx?.positions ?? []).map((p: any) => ({ id: p.id, name: p.name }));
  const chars = pages.map((p) => p.text.replace(/\s+/g, ' ').trim().length);
  const text = pages.map((p) => `--- page ${p.page} ---\n${p.text}`).join('\n').slice(0, 60000);

  let m = null, modelOk = false, inT = 0, outT = 0;
  try {
    const r = await claude(set.model, [{ type: 'text', text: assessPrompt(text, positions, doc.file_name ?? doc.title) }], 1500);
    inT = r.inT; outT = r.outT; m = parseJson(r.text); modelOk = !!m;
  } catch (e) { console.warn('assess model:', (e as Error).message); }
  const a = cleanAssessment(m, new Set(positions.map((p) => p.id)));

  let near = null;
  try {
    const sample = pages.map((p) => p.text).join('\n').slice(0, 1500);
    if (sample.trim()) {
      const v = await embed(sample);
      const { data: hits } = await sb.rpc('mm_llm_search_docs_vec', { p_org: job.org_id, p_embedding: `[${v.join(',')}]`, p_limit: 3 });
      const h = (hits ?? []).find((x: any) => x.doc_id !== job.doc_id && x.distance < 0.05);
      if (h) near = { doc_id: h.doc_id, title: h.title, distance: Number(h.distance.toFixed(3)) };
    }
  } catch (e) { console.warn('near-duplicate check:', (e as Error).message); }

  const sig = { pages: pages.length, empty_pages: chars.filter((c) => c < 40).length, model_pages: pages.filter((p) => p.text_source === 'model').length,
    avg_chars: Math.round(chars.reduce((s, c) => s + c, 0) / Math.max(1, chars.length)),
    avg_garble: Number((pages.reduce((s, p) => s + (p.garble ?? 0), 0) / Math.max(1, pages.length)).toFixed(3)),
    near_duplicate: near, has_positions_list: positions.length > 0, model_ok: modelOk };
  const g = score(sig, a, set);
  const fileTitle = String(doc.file_name ?? '').replace(/\.pdf$/i, '');
  const patch = {
    kind: doc.kind || a.kind, vendor: doc.vendor || a.vendor, doc_date: doc.doc_date || a.doc_date,
    title: (!doc.title || doc.title === fileTitle) && a.title ? a.title : doc.title,
    positions: [...new Set([...(doc.positions ?? []), ...(a.positions ?? [])])], assets: a.assets, summary: a.summary,
    quality_score: g.score,
    quality: { signals: sig, model: a, reasons: g.reasons, review: g.review, issues: [...g.review, ...g.reasons, ...(a.issues ?? [])].slice(0, 12),
               decision: g.decision, thresholds: { accept: set.accept_min, review: set.review_min } },
  };
  return await rpc('mm_rag_finish', { p_job: job.id, p_ok: true, p_to: g.decision, p_doc_patch: patch, p_usage: { in: inT, out: outT, model: set.model } });
}

// ---------- index: chunks with a context header (embeddings follow) ----------
async function index(job: any, ctx: any) {
  const doc = ctx.doc, pages: Page[] = ctx.pages ?? [];
  const { data: mctx } = await sb.rpc('mm_llm_context', { p_org: job.org_id });
  const positions: { id: string; name: string }[] = (mctx?.positions ?? []).map((p: any) => ({ id: p.id, name: p.name }));
  const names = (doc.positions ?? []).map((id: string) => positions.find((p) => p.id === id)?.name ?? id);
  const header = contextHeader({ vendor: doc.vendor, kind: doc.kind, doc_date: doc.doc_date, title: doc.title, positionNames: names });
  const chunks = chunkPages(pages, header).map((c) => ({ ...c, positions: tagPositions(c.content, positions, doc.positions ?? []) }));
  if (!chunks.length) throw new Permanent('No text to index.');
  await rpc('mm_rag_save_chunks', { p_org: job.org_id, p_doc: job.doc_id, p_chunks: chunks });
  return await rpc('mm_rag_finish', { p_job: job.id, p_ok: true, p_to: 'indexed', p_usage: { chunks: chunks.length } });
}

async function runJob(job: any) {
  try {
    const ctx = await rpc('mm_rag_job_context', { p_org: job.org_id, p_doc: job.doc_id, p_pages: job.step !== 'parse' });
    if (!ctx) throw new Permanent('The document was deleted.');
    return job.step === 'parse' ? await parse(job, ctx) : job.step === 'assess' ? await assess(job, ctx) : await index(job, ctx);
  } catch (e) {
    const msg = (e as Error).message ?? String(e);
    console.error(`job ${job.id} ${job.step} ${job.doc_id}:`, msg);
    if (e instanceof Permanent) await sb.rpc('mm_rag_give_up', { p_job: job.id });
    const { data } = await sb.rpc('mm_rag_finish', { p_job: job.id, p_ok: false, p_error: msg.slice(0, 500) });
    return `${data ?? 'error'}: ${msg}`;
  }
}

async function embedPending(limit: number) {
  const { data: rows, error } = await sb.rpc('mm_rag_chunks_to_embed', { p_limit: limit });
  if (error || !rows?.length) return 0;
  const byOrg = new Map<string, any[]>();
  for (const r of rows) {
    const v = await embed(r.content);
    if (!byOrg.has(r.org_id)) byOrg.set(r.org_id, []);
    byOrg.get(r.org_id)!.push({ doc_id: r.doc_id, chunk_no: r.chunk_no, embedding: `[${v.join(',')}]` });
  }
  let n = 0;
  for (const [org, out] of byOrg) {
    const { data, error: e } = await sb.rpc('mm_llm_set_embeddings', { p_org: org, p_model: EMBED_MODEL, p_rows: out });
    if (e) console.error('set embeddings:', e.message); else n += Number(data) || 0;
  }
  return n;
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);
  const { data: jobs, error } = await sb.rpc('mm_rag_claim', { p_limit: 1 });
  if (error) return json({ error: error.message }, 500);
  const job = jobs?.[0];
  const result = job ? await runJob(job) : null;
  const embedded = job ? 0 : await embedPending(EMBED_BATCH);   // embeddings only when there was no job, to stay inside the CPU limit
  return json({ ...(job ? { job: { id: job.id, step: job.step, doc_id: job.doc_id, result } } : {}), embedded });
});
