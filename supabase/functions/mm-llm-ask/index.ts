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

const URL_ = Deno.env.get('SUPABASE_URL')!, ANON = Deno.env.get('SUPABASE_ANON_KEY')!, SERVICE = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const DAILY_CAP = Number(Deno.env.get('MM_LLM_DAILY_CAP') ?? 300);   // all askers together, protects the model bill
const MAX_STEPS = 10;
const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, apikey, content-type, x-client-info, x-mm-ingest-token',
               'Access-Control-Allow-Methods': 'POST, OPTIONS' };
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { ...cors, 'Content-Type': 'application/json' } });
const svc = createClient(URL_, SERVICE, { auth: { persistSession: false } });
setTools(TOOLS);

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
  const { data: today } = await svc.rpc('mm_llm_answers_today');
  if ((today ?? 0) >= DAILY_CAP) return json({ error: 'The assistant has reached its daily limit for everyone. Try again tomorrow.' }, 429);

  // ---- answer ----
  const t0 = Date.now(), trace: any[] = [], charts: any[] = [];
  let answer = '', status = 'ok', inT = 0, outT = 0, model = '', provider = '';
  try {
    const m = makeModel(body.model === 'opus' ? 'opus' : 'default'); model = m.model; provider = m.provider;
    const { data: ctx, error: e } = await db.rpc('mm_llm_context', { p_org: org });
    if (e) throw new Error(e.message);
    m.start(systemPrompt(orgName, ctx ?? {}), question);
    for (let step = 0; step < MAX_STEPS; step++) {
      const final = step === MAX_STEPS - 1;              // last step: answer from what the tools have returned so far
      const turn = await m.next(final); inT += turn.inTokens; outT += turn.outTokens;
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
        const r = await runTool(db, org, c.name, c.args);
        trace.push({ tool: c.name, args: c.args, rows: (r as any).total ?? 0, error: (r as any).error ?? undefined });
        results.push({ id: c.id, content: forModel(r) });
      }
      m.results(results);
    }
  } catch (err) {
    status = 'error';
    answer = err instanceof ModelError ? err.message : `Something went wrong: ${(err as Error).message}`;
  }
  const ms = Date.now() - t0;
  const { data: id } = await svc.rpc('mm_llm_save_answer', { p_org: org, p_question_id: body.question_id ?? null, p_question: question,
    p_answer: answer, p_status: status, p_trace: trace, p_model: model, p_provider: provider, p_in: inT, p_out: outT, p_ms: ms, p_user: userId });
  return json({ id, answer, status, trace, charts, model, provider, ms, remaining }, status === 'ok' ? 200 : 502);
});
