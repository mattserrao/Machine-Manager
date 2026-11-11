// MM MCP, DEV copy for the wiki + memory training run (branch wiki-memory). Live mm-mcp is untouched.
//
// Same tools as mm-llm-ask-dev (one module: ../mm-llm-ask-dev/tools.ts, incl. make_chart), plus list_orgs, machine_context
// and the answering rules as an MCP prompt (mm_answer_rules = the API harness's system prompt, word for word).
//
// Callers: test and build agents, with ingest tokens instead of OAuth:
//   x-mm-ingest-token: <token>[,<token>...]   one per org (Sim Mill, Demodemo RAG); the tools run as service role on that org only
//   x-mm-run-id: <id>                         optional; every tools/call is logged to llm.mcp_calls under it (full output)
// Routes:
//   POST /mm-mcp-dev          MCP JSON-RPC (initialize, tools/list, tools/call, prompts/list, prompts/get, ping)
//   POST /mm-mcp-dev/check    { run_id, answer } -> { citations, trace, charts } built from the run's logged calls:
//                             the same citation check and trace previews mm-llm-ask-dev returns in eval mode, for the judge.
import { createClient } from 'npm:@supabase/supabase-js@2';
import { handle, checkRun } from './mcp.ts';

const URL_ = Deno.env.get('SUPABASE_URL')!, SERVICE = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
const svc = createClient(URL_, SERVICE, { auth: { persistSession: false } });
let embedder: any = null;
const embed = async (text: string): Promise<number[]> => {
  // @ts-ignore Supabase.ai is provided by the Edge Runtime
  embedder ??= new Supabase.ai.Session('gte-small');
  return Array.from(await embedder.run(text, { mean_pool: true, normalize: true }) as number[]);
};
const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'apikey, content-type, accept, mcp-protocol-version, x-mm-ingest-token, x-mm-run-id',
  'Access-Control-Allow-Methods': 'POST, OPTIONS' };
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { ...cors, 'Content-Type': 'application/json' } });

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return new Response('POST only', { status: 405, headers: cors });
  const tokens = (req.headers.get('x-mm-ingest-token') ?? '').split(',').map((s) => s.trim()).filter(Boolean);
  if (!tokens.length) return json({ error: 'x-mm-ingest-token required' }, 401);
  const { data: pub } = await svc.rpc('mm_llm_public_org');
  const { data: allOrgs } = await svc.from('orgs').select('id, name');
  const orgs: { id: string; name: string; promptName: string }[] = [];
  for (const t of tokens) {
    const { data: o } = await svc.rpc('mm_llm_token_org', { p_token: t });
    if (!o) return json({ error: 'invalid or expired ingest token' }, 401);
    const name = (allOrgs ?? []).find((x: any) => x.id === o)?.name ?? (pub ?? []).find((x: any) => x.id === o)?.name ?? o;
    // the API harness names a non-public org "the mill" in its prompt (mm-llm-ask-dev): keep that for parity
    const promptName = (pub ?? []).find((x: any) => x.id === o)?.name ?? 'the mill';
    if (!orgs.some((x) => x.id === o)) orgs.push({ id: o, name, promptName });
  }
  let body: any;
  try { body = await req.json(); } catch { return json({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } }, 400); }
  if (new URL(req.url).pathname.endsWith('/check')) return json(await checkRun(svc, String(body.run_id ?? ''), String(body.answer ?? '')));
  const runId = req.headers.get('x-mm-run-id') || null;
  const out = await handle(body, svc, { orgs, embed, runId });
  return out ? json(out) : new Response(null, { status: 202, headers: cors });
});
