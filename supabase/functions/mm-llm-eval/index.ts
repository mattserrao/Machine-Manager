// Autoresearch judge and recorder (branch autoresearch). Ingest-token callers only; deployed with verify_jwt off.
//   POST { action: 'start', round, label, change?, sha?, split }                  -> { run_id, spent, budget }
//   POST { action: 'judge', run_id, q, result, auto? }                           -> { score, criteria, must_hits, notes, cost, spent }
//   POST { action: 'finish', run_id }                                            -> { ok, spent }
// q = one question from autoresearch/questions.json; result = the mm-llm-ask-dev eval response; auto = deterministic misses.
// The judge model and prompt are pinned (JUDGE_VERSION). Changing either means a new baseline.
// Hard budget: MM_EVAL_BUDGET (default $50) over everything recorded in llm.eval_results; checked before every call.
import { createClient } from 'npm:@supabase/supabase-js@2';

const URL_ = Deno.env.get('SUPABASE_URL')!, SERVICE = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const BUDGET = Number(Deno.env.get('MM_EVAL_BUDGET') ?? 50);
const JUDGE_MODEL = 'claude-opus-5-5', JUDGE_VERSION = 'judge-v1.1';
// USD per million tokens (platform.claude.com pricing, Nov 2026). Cache reads 0.05x, 5-minute cache writes 1.25x.
const PRICE: Record<string, { in: number; out: number }> = {
  'claude-sonnet-5-5': { in: 2, out: 10 }, 'claude-opus-5-5': { in: 4, out: 20 }, 'claude-haiku-5-5': { in: 0.1, out: 0.5 } };
const cost = (model: string, u: { in?: number; out?: number; cache_read?: number; cache_write?: number }) => {
  const p = PRICE[model] ?? PRICE['claude-sonnet-5-5'];
  return ((u.in ?? 0) * p.in + (u.out ?? 0) * p.out + (u.cache_read ?? 0) * p.in * 0.05 + (u.cache_write ?? 0) * p.in * 1.25) / 1e6;
};
const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'apikey, content-type, x-mm-ingest-token', 'Access-Control-Allow-Methods': 'POST, OPTIONS' };
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { ...cors, 'Content-Type': 'application/json' } });
const svc = createClient(URL_, SERVICE, { auth: { persistSession: false } });
const key = () => (Deno.env.get('MM-LLM-OP') ?? '').replace(/[^\x21-\x7e]/g, '').replace(/^['"]+|['"]+$/g, '');

const SYSTEM = `You grade answers from MM LLM, an assistant for a paper machine superintendent. You are strict, consistent and brief.
You get: the question, its kind, an answer key (MUST points, NICE points, source documents, numeric tolerance), the assistant's answer,
the charts it drew, a trace of the tools it called (with a preview of what each returned) and any automatic-check misses.

Judge only against the key and the trace. The key is the truth for this question; the trace is what the assistant actually saw.
- must_hits: one true/false per MUST point, in order. True only if the answer states that point (wording may differ; numbers within
  the tolerance, or within about 5% when none is given). A point the answer contradicts is false.
- correct (0-3): 3 = nothing wrong; 2 = a minor slip; 1 = a material error; 0 = mostly wrong or invented. Penalise invented
  numbers, dates, ids or names, and claims that contradict the key. For premise questions, missing the false premise caps this at 1.
- grounded (0-3): are the answer's specific claims supported by the trace? For library and calc questions, did it find and cite a
  real document ([DOC id p.N]) that it read? For gap questions (no library source exists), sound general knowledge stated plainly
  as such is fine: 2 if correct and not dressed up with fake citations, 3 only if it also says the library lacked a source.
  Citations to documents or records not in the trace score 0. Tool previews are cut to the first 700 characters: a claim you
  can't see in a preview still counts as supported if the assistant called a tool that would return it (e.g. read that document
  page); penalise only claims that contradict the trace or cite ids/pages it never retrieved.
- useful (0-3): leads with the answer, right format and length, charts when asked, checks the premise, no padding.
- notes: at most 40 words: the main thing it got wrong or missed, or "clean".
Return only JSON: {"must_hits":[...], "correct":n, "grounded":n, "useful":n, "notes":"..."}`;

function userMsg(q: any, r: any, auto: string[]) {
  const trace = (r.trace ?? []).map((t: any, i: number) => {
    const head = `${i + 1}. ${t.tool}(${JSON.stringify(t.args).slice(0, 300)}) rows=${t.rows ?? ''}${t.error ? ' ERROR ' + t.error : ''}`;
    return t.preview ? `${head}\n   -> ${t.preview.replace(/\s+/g, ' ')}` : head;
  }).join('\n') || '(no tools called)';
  const charts = (r.charts ?? []).map((c: any) => `- "${c.title}": ${(c.series ?? []).length} series${(c.series ?? []).some((s: any) => s.axis === 'right') ? ', right axis' : ''}`).join('\n') || '(none)';
  return `QUESTION (${q.id}, section ${q.section}, kind ${q.kind}): ${q.question}

KEY
MUST:
${q.must.map((m: string, i: number) => `${i + 1}. ${m}`).join('\n')}
NICE: ${q.nice?.length ? q.nice.join('; ') : '(none)'}
Sources: ${q.sources?.length ? q.sources.join('; ') : '(none in the library: gap question)'}
Tolerance: ${q.tolerance ?? '(none)'}

ANSWER (status ${r.status}):
${r.answer ?? ''}

CHARTS:
${charts}

TRACE:
${trace}

AUTOMATIC CHECK MISSES: ${auto.length ? auto.join('; ') : '(none)'}`;
}

async function judge(q: any, r: any, auto: string[]) {
  const body: any = { model: JUDGE_MODEL, max_tokens: 1200, temperature: 0, system: SYSTEM, messages: [{ role: 'user', content: userMsg(q, r, auto) }] };
  let res = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST',
    headers: { 'x-api-key': key(), 'anthropic-version': '2023-06-01', 'content-type': 'application/json' }, body: JSON.stringify(body) });
  let j = await res.json();
  if (res.status === 400 && /temperature/i.test(JSON.stringify(j))) {      // model doesn't take temperature: run without it
    delete body.temperature;
    res = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST',
      headers: { 'x-api-key': key(), 'anthropic-version': '2023-06-01', 'content-type': 'application/json' }, body: JSON.stringify(body) });
    j = await res.json();
  }
  if (!res.ok) throw new Error(`judge ${res.status}: ${j?.error?.message ?? JSON.stringify(j).slice(0, 200)}`);
  const text = (j.content ?? []).filter((b: any) => b.type === 'text').map((b: any) => b.text).join('');
  const m = text.match(/\{[\s\S]*\}/);
  let g: any;
  try { g = JSON.parse(m ? m[0] : text); } catch {        // unescaped quotes in notes, or cut short: read the fields one by one
    const num = (k: string) => { const x = text.match(new RegExp(`"${k}"\\s*:\\s*(\\d)`)); return x ? Number(x[1]) : null; };
    const hits = text.match(/"must_hits"\s*:\s*\[([^\]]*)\]/);
    g = { must_hits: hits ? hits[1].split(',').map((s) => /true/i.test(s)) : null, correct: num('correct'), grounded: num('grounded'),
          useful: num('useful'), notes: (text.match(/"notes"\s*:\s*"([\s\S]*)/)?.[1] ?? '').replace(/"\s*\}?\s*$/, '').slice(0, 400) };
    if (!g.must_hits || g.correct === null || g.grounded === null) throw new Error('judge reply not JSON: ' + text.slice(0, 200));
    if (g.useful === null) g.useful = 2;      // cut before "useful": neutral
  }
  return { g, usage: { in: j.usage?.input_tokens ?? 0, out: j.usage?.output_tokens ?? 0 } };
}

const clamp = (n: any) => Math.max(0, Math.min(3, Number(n) || 0));

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);
  const token = req.headers.get('x-mm-ingest-token');
  const { data: org } = token ? await svc.rpc('mm_llm_token_org', { p_token: token }) : { data: null };
  if (!org) return json({ error: 'invalid or expired ingest token' }, 401);
  let b: any; try { b = await req.json(); } catch { return json({ error: 'body must be JSON' }, 400); }
  const { data: spent0 } = await svc.rpc('mm_eval_spent'); const spent = Number(spent0 ?? 0);

  if (b.action === 'start') {
    if (spent >= BUDGET) return json({ error: `budget reached: $${spent.toFixed(2)} of $${BUDGET}` }, 402);
    const { data: id, error } = await svc.rpc('mm_eval_start', { p_round: b.round ?? 0, p_label: b.label ?? 'run', p_change: b.change ?? null,
      p_sha: b.sha ?? null, p_split: b.split ?? 'all', p_answer_model: b.answer_model ?? 'claude-sonnet-5-5', p_judge_model: `${JUDGE_MODEL} ${JUDGE_VERSION}` });
    if (error) return json({ error: error.message }, 500);
    return json({ run_id: id, spent, budget: BUDGET });
  }
  if (b.action === 'finish') {
    await svc.rpc('mm_eval_finish', { p_run: b.run_id });
    return json({ ok: true, spent });
  }
  if (b.action !== 'judge') return json({ error: 'action must be start, judge or finish' }, 400);

  const q = b.q, r = b.result ?? {}, auto: string[] = b.auto ?? [];
  const answerCost = cost(r.model ?? 'claude-sonnet-5-5', r.usage ?? {});
  if (spent + answerCost >= BUDGET) return json({ error: `budget reached: $${spent.toFixed(2)} of $${BUDGET}` }, 402);
  let g: any = null, usage = { in: 0, out: 0 }, note = '';
  if (r.status === 'ok' && r.answer) {
    try { ({ g, usage } = await judge(q, r, auto)); } catch (e) { note = (e as Error).message; }
  } else note = 'no answer: ' + String(r.answer ?? r.error ?? '').slice(0, 200);
  const hits: boolean[] = (g?.must_hits ?? []).slice(0, q.must.length).map(Boolean);
  while (hits.length < q.must.length) hits.push(false);
  const crit = g ? { correct: clamp(g.correct), complete: Math.round(30 * hits.filter(Boolean).length / q.must.length) / 10,
                     grounded: clamp(g.grounded), useful: clamp(g.useful) } : { correct: 0, complete: 0, grounded: 0, useful: 0 };
  const score = Math.round(1000 * (0.40 * crit.correct + 0.25 * crit.complete + 0.20 * crit.grounded + 0.15 * crit.useful) / 3) / 10;
  const judgeCost = cost(JUDGE_MODEL, usage);
  const { error } = await svc.rpc('mm_eval_save', { p: {
    run_id: b.run_id, question_id: q.id, section: q.section, split: q.split, kind: q.kind, score, criteria: crit, must_hits: hits,
    judge_notes: g ? String(g.notes ?? '').slice(0, 500) : note, answer: r.answer ?? null, status: r.status ?? 'error',
    trace: (r.trace ?? []).map((t: any) => ({ tool: t.tool, args: t.args, rows: t.rows, error: t.error })),
    in_tokens: r.usage?.in ?? 0, out_tokens: r.usage?.out ?? 0, cache_read: r.usage?.cache_read ?? 0, cache_write: r.usage?.cache_write ?? 0,
    judge_in: usage.in, judge_out: usage.out, answer_cost: answerCost.toFixed(4), judge_cost: judgeCost.toFixed(4), ms: r.ms ?? 0 } });
  if (error) return json({ error: error.message }, 500);
  return json({ score, criteria: crit, must_hits: hits, notes: g?.notes ?? note, answer_cost: answerCost, judge_cost: judgeCost,
                spent: spent + answerCost + judgeCost });
});
