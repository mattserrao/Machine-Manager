// MM LLM orchestrator, DEV copy for autoresearch (branch autoresearch). Same as mm-llm-ask plus eval mode:
//   ingest token + { eval: true }  ->  not saved to llm.answers, no daily cap, response adds usage and tool-result previews.
//   Round 3 (playbooks.ts): get_playbook(kind) gives a checklist per kind of data question; the prompt says to call it first.
//   + { no_rag: true } (eval only): the document tools are withheld for that answer, to measure what the library adds.
// Experiments are deployed here first; the live mm-llm-ask changes only when a change is kept.
//
// MM LLM orchestrator (Supabase Edge Function): answers a question about one organization's PM1 data.
//
// Who can ask:
//   - a signed-in user listed in llm.query_access for the org (Authorization: Bearer <user session token>),
//     within their daily limit; the tools run with that user's session, so row-level security applies;
//   - a batch run of the demo questions with an ingest token (header x-mm-ingest-token), e.g. to refresh the
//     saved answers everyone sees.
// Every answer is saved to llm.answers with its tool trace. Model and provider come from MM_LLM_PROVIDER /
// MM_LLM_MODEL and the provider's key secret (see adapter.ts). Deployed with verify_jwt off: it checks callers itself.
//
//   POST { question, question_id?, org_id?, model? }  ->  { id, answer, trace, charts, model, provider, ms, remaining }
// model: 'sonnet' (default) or 'opus' (the larger model; see makeModel in adapter.ts).
// org_id picks which of the user's orgs on llm.query_access to ask about (default: the first).
// Charts (make_chart) are kept in the trace (tool 'make_chart', args = the chart), so saved answers can redraw them.
import { createClient } from 'npm:@supabase/supabase-js@2';
import { makeModel, setTools, ModelError } from './adapter.ts';
import { TOOLS, runTool, forModel, checkChart } from './tools.ts';
import { systemPrompt } from './prompt.ts';
import { PLAYBOOK_TOOL, getPlaybook } from './playbooks.ts';

const URL_ = Deno.env.get('SUPABASE_URL')!, ANON = Deno.env.get('SUPABASE_ANON_KEY')!, SERVICE = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const DAILY_CAP = Number(Deno.env.get('MM_LLM_DAILY_CAP') ?? 300);   // all askers together, protects the model bill
const MAX_STEPS = 10;
// search_library embeds the query with the same model as the document chunks (gte-small, Supabase.ai in the runtime)
let embedder: any = null;
const embed = async (text: string): Promise<number[]> => {
  // @ts-ignore Supabase.ai is provided by the Edge Runtime
  embedder ??= new Supabase.ai.Session('gte-small');
  return Array.from(await embedder.run(text, { mean_pool: true, normalize: true }) as number[]);
};
const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, apikey, content-type, x-client-info, x-mm-ingest-token',
               'Access-Control-Allow-Methods': 'POST, OPTIONS' };
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { ...cors, 'Content-Type': 'application/json' } });
const svc = createClient(URL_, SERVICE, { auth: { persistSession: false } });
const ALL_TOOLS = [...TOOLS, PLAYBOOK_TOOL];
setTools(ALL_TOOLS);
// The document library (RAG) and document search: withheld when an eval run asks for no_rag.
const DOC_TOOLS = new Set(['search_library', 'get_document', 'get_document_page', 'list_documents', 'library_status', 'search_documents']);
const NO_RAG_NOTE = '\n- The document library is unavailable for this answer: there are no document tools. Use the data tools; for technical knowledge say "The library has no source for this; from general engineering knowledge:" and give it uncited.';

// Eval only: is every [citation] in the answer backed by what the tools returned in this run?
//  [DOC <id> p.N] / p.N-M: the doc (id or its first 8+ characters) with that page in a returned row (search passage or page read);
//  any other [..]: every id-like token in it (has a digit, 4+ chars: WO numbers, RCFA ids, tags, dates, report ids) appears in the
//  tool output. Brackets with no such token (e.g. [Action: title]) are "unchecked".
function checkCitations(answer: string, seen: string[]) {
  const all = seen.join('\n').toLowerCase();
  const pages = new Map<string, Set<number>>();                     // doc id -> pages seen
  const walk = (o: any) => { if (!o || typeof o !== 'object') return; if (Array.isArray(o)) { o.forEach(walk); return; }
    if (typeof o.doc_id === 'string') { const s = pages.get(o.doc_id) ?? new Set<number>(); if (Number.isFinite(Number(o.page))) s.add(Number(o.page)); pages.set(o.doc_id, s); }
    for (const k in o) walk(o[k]); };
  for (const s of seen) { try { walk(JSON.parse(s)); } catch { /* ignore */ } }
  const out = { total: 0, supported: 0, unsupported: [] as string[], unchecked: 0 };
  for (const m of answer.matchAll(/\[([^\[\]]{2,200})\]/g)) {
    for (const part of m[1].split(/;\s*/)) {
      const p = part.trim(); if (!p) continue;
      const d = p.match(/^DOC\s+([0-9a-f][0-9a-f-]{7,35})(?:[,\s]+(?:pp?\.?\s*)?(\d+)(?:\s*[-–]\s*(\d+))?)?/i);
      if (d) {
        out.total++;
        const id = [...pages.keys()].find((k) => k.toLowerCase().startsWith(d[1].toLowerCase()));
        const want = d[2] ? Array.from({ length: Math.min(20, (Number(d[3] ?? d[2]) - Number(d[2])) + 1) }, (_, i) => Number(d[2]) + i) : [];
        const ok = !!id && want.every((n) => pages.get(id)!.has(n));
        if (ok) out.supported++; else out.unsupported.push(p.slice(0, 80));
        continue;
      }
      const toks = (p.match(/[A-Za-z0-9][A-Za-z0-9:_\-.\/]*\d[A-Za-z0-9:_\-.\/]*/g) ?? []).map((t) => t.replace(/[.\-:]+$/, ''))
        .filter((t) => t.length >= 4 && !/^pp?\.\d/i.test(t));
      if (!toks.length) { out.unchecked++; continue; }
      out.total++;
      if (toks.every((t) => all.includes(t.toLowerCase()))) out.supported++; else out.unsupported.push(p.slice(0, 80));
    }
  }
  return out;
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);
  let body: any;
  try { body = await req.json(); } catch { return json({ error: 'body must be JSON' }, 400); }
  const question = String(body.question ?? '').trim();
  if (!question || question.length > 1500) return json({ error: 'Ask a question (up to 1,500 characters).' }, 400);

  // ---- who is asking ----
  let db: any, org: string, orgName: string, userId: string | null = null, remaining: number | null = null;
  const token = req.headers.get('x-mm-ingest-token');
  if (token) {
    const { data: o } = await svc.rpc('mm_llm_token_org', { p_token: token });
    if (!o) return json({ error: 'invalid or expired ingest token' }, 401);
    db = svc; org = o;
    const { data: pub } = await svc.rpc('mm_llm_public_org'); orgName = pub?.find((p: any) => p.id === o)?.name ?? 'the mill';
  } else {
    const auth = req.headers.get('Authorization') ?? '';
    db = createClient(URL_, ANON, { global: { headers: { Authorization: auth } }, auth: { persistSession: false } });
    const { data: u } = await db.auth.getUser();
    if (!u?.user) return json({ error: 'Sign in to ask questions.' }, 401);
    userId = u.user.id;
    const { data: acc } = await db.rpc('mm_llm_my_access');
    const a = (acc ?? []).find((x: any) => x.org_id === body.org_id) ?? (acc ?? [])[0];
    if (!a) return json({ error: 'Live questions are open to the demo account only. Everyone signed in can read the saved answers.' }, 403);
    if (a.used_today >= a.daily_limit) return json({ error: `Daily limit reached (${a.daily_limit} questions). Try again tomorrow.` }, 429);
    org = a.org_id; orgName = a.org_name; remaining = a.daily_limit - a.used_today - 1;
  }
  const evalMode = !!token && body.eval === true;
  const { data: today } = evalMode ? { data: 0 } : await svc.rpc('mm_llm_answers_today');
  if ((today ?? 0) >= DAILY_CAP) return json({ error: 'The assistant has reached its daily limit for everyone. Try again tomorrow.' }, 429);

  // ---- answer ----
  const t0 = Date.now(), trace: any[] = [], charts: any[] = [], seen: string[] = [];   // seen = full tool output (eval mode)
  let answer = '', status = 'ok', inT = 0, outT = 0, cacheR = 0, cacheW = 0, steps = 0, model = '', provider = '';
  try {
    const m = makeModel(body.model === 'opus' ? 'opus' : 'default'); model = m.model; provider = m.provider;
    const noRag = evalMode && body.no_rag === true;
    if (noRag) (m as any).tools = ALL_TOOLS.filter((t) => !DOC_TOOLS.has(t.name));
    const { data: ctx, error: e } = await db.rpc('mm_llm_context', { p_org: org });
    if (e) throw new Error(e.message);
    m.start(systemPrompt(orgName, ctx ?? {}) + (noRag ? NO_RAG_NOTE : ''), question);
    for (let step = 0; step < MAX_STEPS; step++) {
      const final = step === MAX_STEPS - 1;              // last step: answer from what the tools have returned so far
      const turn = await m.next(final); inT += turn.inTokens; outT += turn.outTokens; cacheR += turn.cacheRead ?? 0; cacheW += turn.cacheWrite ?? 0; steps++;
      if (final || !turn.calls.length) { answer = turn.text.trim() || 'No answer came back. Try a narrower question.'; break; }
      const results = [];
      for (const c of turn.calls) {
        if (c.name === 'make_chart') {          // drawn by the page; nothing to query
          const { chart, error } = checkChart(c.args);
          const same = chart ? charts.findIndex((x) => x.title === chart.title) : -1;   // a redraw replaces the earlier version
          if (chart) { if (same >= 0) charts[same] = chart; else charts.push(chart); }
          trace.push({ tool: 'make_chart', args: chart ?? c.args, rows: chart ? 1 : 0, error, ...(same >= 0 ? { replaces: same } : {}) });
          results.push({ id: c.id, content: JSON.stringify(chart ? { ok: true, note: 'The page draws this chart under your answer and offers a PNG download. Do not redraw it in text. To fix it, call make_chart again with the same title: that replaces it, so don\'t mention the redraw.' } : { error }) });
          continue;
        }
        if (c.name === 'get_playbook') {        // a checklist, not a source: never counts as something to cite
          const pb = getPlaybook(String(c.args.kind ?? ''));
          trace.push({ tool: 'get_playbook', args: c.args, rows: (pb as any).error ? 0 : 1, error: (pb as any).error });
          results.push({ id: c.id, content: JSON.stringify(pb) });
          continue;
        }
        const r = (evalMode && body.no_rag === true && DOC_TOOLS.has(c.name)) ? { error: 'document tools are unavailable in this run' } : await runTool(db, org, c.name, c.args, { embed });
        const content = forModel(r);
        if (evalMode) seen.push(JSON.stringify(c.name === 'get_document_page' && Array.isArray((r as any).rows)   // page rows carry no doc id
          ? { rows: (r as any).rows.map((x: any) => ({ doc_id: String(c.args.doc_id ?? ''), ...x })) } : r));
        trace.push({ tool: c.name, args: c.args, rows: (r as any).total ?? 0, error: (r as any).error ?? undefined,
                     ...(evalMode ? { preview: content.slice(0, 700) } : {}) });
        results.push({ id: c.id, content });
      }
      m.results(results);
    }
  } catch (err) {
    status = 'error';
    answer = err instanceof ModelError ? err.message : `Something went wrong: ${(err as Error).message}`;
  }
  const ms = Date.now() - t0;
  if (evalMode) return json({ answer, status, trace, charts, model, provider, ms, citations: checkCitations(answer, seen),
    usage: { in: inT, out: outT, cache_read: cacheR, cache_write: cacheW, steps } }, status === 'ok' ? 200 : 502);
  const { data: id } = await svc.rpc('mm_llm_save_answer', { p_org: org, p_question_id: body.question_id ?? null, p_question: question,
    p_answer: answer, p_status: status, p_trace: trace, p_model: model, p_provider: provider, p_in: inT, p_out: outT, p_ms: ms, p_user: userId });
  return json({ id, answer, status, trace, charts, model, provider, ms, remaining }, status === 'ok' ? 200 : 502);
});
