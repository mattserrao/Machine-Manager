// Autoresearch judge and recorder (branch autoresearch). Ingest-token callers only; deployed with verify_jwt off.
//   POST { action: 'start', round, label, change?, sha?, split }                  -> { run_id, spent, budget }
//   POST { action: 'judge', run_id, q, result, auto? }                           -> { score, criteria, must_hits, notes, cost, spent }
//   POST { action: 'finish', run_id }                                            -> { ok, spent }
// q = one question from autoresearch/questions.json; result = the mm-llm-ask-dev eval response; auto = deterministic misses.
// The judge model and prompt are pinned (JUDGE_VERSION). Changing either means a new baseline.
// v2 (Nov 10): citation-weighted rubric; the dev function's citation check is binding (any unsupported citation caps at 50).
// Hard budget: MM_EVAL_BUDGET (default $50) over everything recorded in llm.eval_results; checked before every call.
import { createClient } from 'npm:@supabase/supabase-js@2';

const URL_ = Deno.env.get('SUPABASE_URL')!, SERVICE = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const BUDGET = Number(Deno.env.get('MM_EVAL_BUDGET') ?? 50);
const JUDGE_MODEL = 'claude-opus-5-5', JUDGE_VERSION = 'judge-v2';
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

const SYSTEM = `You grade answers from MM LLM, an assistant for a paper machine superintendent. These are technical answers: accuracy and
citations matter most. A short, fully cited, accurate answer is the best answer. Be strict and consistent.
You get: the question, an answer key (MUST points, NICE points, library sources, numeric tolerance), the answer and its word count,
the charts it drew, the tools it called (with a preview of each result), a CITATION CHECK computed from the full tool outputs, and any
automatic-check misses. The key is the truth; the trace is what the assistant actually saw.

- must_hits: one true/false per MUST point, in order. True only if the answer states it (wording may differ; numbers within the
  tolerance, or about 5% when none is given). A point the answer contradicts is false.
- correct (0-3): 3 = nothing wrong. Any wrong technical value, setting, formula, procedure step, date, id or name: at most 1.
  Invented facts: 0. A false premise the answer misses: at most 1.
- cited (0-3): every specific technical claim (a number, setting, spec, formula, procedure step, finding, date, id) needs an inline
  citation to a source the assistant retrieved in this run. 3 = all of them cited; 2 = one minor claim uncited; 1 = several uncited,
  or only a general citation at the end; 0 = no citations, or ANY citation the CITATION CHECK lists as unsupported (treat those as
  fabricated). Citations the check marks unchecked: judge them against the trace.
  Gap questions (the key lists no library source): 3 only if the answer says the library has no source for it and gives the answer
  as general engineering knowledge, clearly labelled, with no invented citations; correct but unlabelled and uncited = 1.
  Calc questions with a listed source: the formula must be cited to that source; otherwise at most 1.
- concise (0-3): 3 = the answer comes first and covers only what was asked, within about 150 words for knowledge and calc questions
  or about 220 words for data questions and briefs (charts don't count); 2 = somewhat long or one unrequested section; 1 = padded
  (extra tables, tips, background; about twice the length needed); 0 = rambling.
- notes: at most 40 words: the main error, uncited or fabricated citation, or missing point; or "clean".
Return only JSON: {"must_hits":[...], "correct":n, "cited":n, "concise":n, "notes":"..."}`;

function userMsg(q: any, r: any, auto: string[]) {
  const trace = (r.trace ?? []).map((t: any, i: number) => {
    const head = `${i + 1}. ${t.tool}(${JSON.stringify(t.args).slice(0, 300)}) rows=${t.rows ?? ''}${t.error ? ' ERROR ' + t.error : ''}`;
    return t.preview ? `${head}\n   -> ${t.preview.replace(/\s+/g, ' ')}` : head;
  }).join('\n') || '(no tools called)';
  const charts = (r.charts ?? []).map((c: any) => `- "${c.title}": ${(c.series ?? []).length} series${(c.series ?? []).some((s: any) => s.axis === 'right') ? ', right axis' : ''}`).join('\n') || '(none)';
  const c = r.citations ?? { total: 0, supported: 0, unsupported: [], unchecked: 0 };
  const words = String(r.answer ?? '').split(/\s+/).filter(Boolean).length;
  return `QUESTION (kind: ${q.kind}${q.kind === 'gap' ? ', no library source' : ''}): ${q.question}

KEY
MUST:
${q.must.map((m: string, i: number) => `${i + 1}. ${m}`).join('\n')}
NICE: ${q.nice?.length ? q.nice.join('; ') : '(none)'}
Sources: ${q.sources?.length ? q.sources.join('; ') : '(none in the library: gap question)'}
Tolerance: ${q.tolerance ?? '(none)'}

ANSWER (status ${r.status}, ${words} words):
${r.answer ?? ''}

CHARTS:
${charts}

TRACE:
${trace}

CITATION CHECK: ${c.total} checked, ${c.supported} supported, ${c.unchecked} unchecked; UNSUPPORTED: ${c.unsupported.length ? c.unsupported.join(' | ') : '(none)'}

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
    g = { must_hits: hits ? hits[1].split(',').map((s) => /true/i.test(s)) : null, correct: num('correct'), cited: num('cited'),
          concise: num('concise'), notes: (text.match(/"notes"\s*:\s*"([\s\S]*)/)?.[1] ?? '').replace(/"\s*\}?\s*$/, '').slice(0, 400) };
    if (!g.must_hits || g.correct === null || g.cited === null) throw new Error('judge reply not JSON: ' + text.slice(0, 200));
    if (g.concise === null) g.concise = 2;    // cut before "concise": neutral
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
  // v2: correct 35%, cited 35%, complete 15%, concise 15%. Any unsupported citation: cited = 0 and the score is capped at 50.
  const cit = r.citations ?? { total: 0, supported: 0, unsupported: [], unchecked: 0 };
  const fabricated = (cit.unsupported ?? []).length > 0;
  const crit = g ? { correct: clamp(g.correct), cited: fabricated ? 0 : clamp(g.cited),
                     complete: Math.round(30 * hits.filter(Boolean).length / q.must.length) / 10, concise: clamp(g.concise) }
                 : { correct: 0, cited: 0, complete: 0, concise: 0 };
  let score = Math.round(1000 * (0.35 * crit.correct + 0.35 * crit.cited + 0.15 * crit.complete + 0.15 * crit.concise) / 3) / 10;
  if (fabricated) score = Math.min(score, 50);
  (crit as any).citations = { total: cit.total, supported: cit.supported, unsupported: (cit.unsupported ?? []).length, unchecked: cit.unchecked,
    list: (cit.unsupported ?? []).slice(0, 10) };
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
