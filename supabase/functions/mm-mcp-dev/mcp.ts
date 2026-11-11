// MM MCP dev: JSON-RPC handling, tool calls with a run log, the answering-rules prompt and the citation check.
// Tools, prompt and citation check are the ones mm-llm-ask-dev uses, so a test agent here sees what the API harness sees.
import { DEFS, TOOLS, runTool, forModel, checkChart } from '../mm-llm-ask-dev/tools.ts';
import { systemPrompt, MACHINES } from '../mm-llm-ask-dev/prompt.ts';

export const SERVER = { name: 'machine-manager-dev', title: 'Machine Manager (dev)', version: '0.4.0-dev' };
const PROTOCOL_VERSIONS = ['2025-11-25', '2025-06-18', '2025-03-26', '2024-11-05'];
type Org = { id: string; name: string; promptName?: string };
export type Opts = { orgs: Org[]; embed?: (t: string) => Promise<number[]>; runId?: string | null };

const ORG_ARG = { type: 'string', description: 'Organization name (Sim Mill or Demodemo RAG). Default: the first one your token allows.' };
const EXTRA = [
  { name: 'list_orgs', description: 'The organizations this connection can read.', parameters: { type: 'object', properties: {} } },
  { name: 'machine_context', description: 'What the machine is and what the other tools take: the last day of data ("today"), outages with their ids, My Machine position ids and names, and Pi tags with units.',
    parameters: { type: 'object', properties: {} } },
];
export function listTools() {
  return [...EXTRA, ...TOOLS].map((t: any) => ({ name: t.name, description: t.description,
    inputSchema: { ...t.parameters, properties: { ...(t.parameters?.properties ?? {}), org: ORG_ARG } },
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false } }));
}
const pick = (orgs: Org[], want: unknown): Org | null => {
  const w = String(want ?? '').trim().toLowerCase();
  if (!w) return orgs[0] ?? null;
  return orgs.find((o) => o.id === w || o.name.toLowerCase() === w) ?? null;
};

async function callTool(db: any, name: string, args: Record<string, any>, o: Opts) {
  if (name === 'list_orgs') return { orgs: o.orgs.map((x) => ({ ...x, machine: MACHINES[x.name] ?? null })) };
  const org = pick(o.orgs, args.org);
  if (!org) return { error: `Unknown org "${args.org}". Readable: ${o.orgs.map((x) => x.name).join(', ')}.` };
  const { org: _drop, ...rest } = args;
  if (name === 'machine_context') {
    const { data, error } = await db.rpc('mm_llm_context', { p_org: org.id });
    return error ? { error: error.message } : { org: org.name, machine: MACHINES[org.name] ?? null, ...(data ?? {}) };
  }
  if (name === 'make_chart') {
    const { chart, error } = checkChart(rest);
    return chart ? { ok: true, chart, note: 'The page draws this chart under your answer. Do not redraw it in text. To fix it, call make_chart again with the same title.' } : { error };
  }
  const r: any = await runTool(db, org.id, name, rest, { embed: o.embed });
  // page rows carry no doc id: add it, as mm-llm-ask-dev does for its citation check
  if (name === 'get_document_page' && Array.isArray(r.rows)) r.rows = r.rows.map((x: any) => ({ doc_id: String(rest.doc_id ?? ''), ...x }));
  return r;
}

const ok = (id: any, result: unknown) => ({ jsonrpc: '2.0', id, result });
const fail = (id: any, code: number, message: string) => ({ jsonrpc: '2.0', id: id ?? null, error: { code, message } });

export async function handle(msg: any, db: any, o: Opts): Promise<object | null> {
  if (!msg || typeof msg !== 'object' || Array.isArray(msg) || msg.jsonrpc !== '2.0') return fail(null, -32600, 'Invalid Request');
  if (msg.method === undefined || msg.id === undefined || msg.id === null) return null;
  const { id, method, params } = msg;
  switch (method) {
    case 'initialize': {
      const asked = String(params?.protocolVersion ?? '');
      return ok(id, { protocolVersion: PROTOCOL_VERSIONS.includes(asked) ? asked : PROTOCOL_VERSIONS[0],
        capabilities: { tools: { listChanged: false }, prompts: { listChanged: false } }, serverInfo: SERVER,
        instructions: 'Load the prompt mm_answer_rules first and follow it. Every tool takes an optional org.' });
    }
    case 'ping': return ok(id, {});
    case 'tools/list': return ok(id, { tools: listTools() });
    case 'prompts/list': return ok(id, { prompts: [{ name: 'mm_answer_rules', title: 'MM LLM answering rules',
      description: 'The system prompt the MM LLM API harness uses for this org: machine, today, outages, positions, Pi tags and how to answer and cite.',
      arguments: [{ name: 'org', description: 'Organization name', required: false }] }] });
    case 'prompts/get': {
      if (params?.name !== 'mm_answer_rules') return fail(id, -32602, `Unknown prompt: ${params?.name}`);
      const org = pick(o.orgs, params?.arguments?.org);
      if (!org) return fail(id, -32602, 'Unknown org');
      const { data, error } = await db.rpc('mm_llm_context', { p_org: org.id });
      if (error) return fail(id, -32603, error.message);
      return ok(id, { description: `MM LLM rules for ${org.name}`, messages: [{ role: 'user', content: { type: 'text', text: systemPrompt(org.promptName ?? org.name, data ?? {}) } }] });
    }
    case 'tools/call': {
      const name = String(params?.name ?? '');
      const args = params?.arguments && typeof params.arguments === 'object' ? params.arguments : {};
      if (!listTools().some((t) => t.name === name)) return fail(id, -32602, `Unknown tool: ${name}`);
      const t0 = Date.now();
      let r: any;
      try { r = await callTool(db, name, args, o); } catch (e) { r = { error: `Tool failed: ${(e as Error).message}` }; }
      const text = r.error ? String(r.error) : forModel(r);
      if (o.runId) {
        const org = pick(o.orgs, args.org);
        await db.rpc('mm_mcp_log', { p: { run_id: o.runId, org_id: org?.id ?? null, tool: name, args,
          output: name === 'make_chart' ? JSON.stringify(r.chart ?? r) : JSON.stringify(r), rows: r.total ?? (r.chart ? 1 : 0),
          error: r.error ?? null, ms: Date.now() - t0 } });
      }
      return ok(id, { content: [{ type: 'text', text }], isError: !!r.error });
    }
    default: return fail(id, -32601, `Method not found: ${method}`);
  }
}

// ---------- the citation check (same as mm-llm-ask-dev's eval mode) ----------
export function checkCitations(answer: string, seen: string[]) {
  const all = seen.join('\n').toLowerCase();
  const pages = new Map<string, Set<number>>();
  const walk = (x: any) => { if (!x || typeof x !== 'object') return; if (Array.isArray(x)) { x.forEach(walk); return; }
    if (typeof x.doc_id === 'string') { const s = pages.get(x.doc_id) ?? new Set<number>(); if (Number.isFinite(Number(x.page))) s.add(Number(x.page)); pages.set(x.doc_id, s); }
    for (const k in x) walk(x[k]); };
  for (const s of seen) { try { walk(JSON.parse(s)); } catch { /* ignore */ } }
  const out = { total: 0, supported: 0, unsupported: [] as string[], unchecked: 0 };
  for (const m of answer.matchAll(/\[([^\[\]]{2,200})\]/g)) {
    for (const part of m[1].split(/;\s*/)) {
      const p = part.trim(); if (!p) continue;
      const d = p.match(/^DOC\s+([0-9a-f][0-9a-f-]{7,35})(?:[,\s]+(?:pp?\.?\s*)?(\d+)(?:\s*[-–]\s*(\d+))?)?/i);
      if (d) {
        out.total++;
        const docId = [...pages.keys()].find((k) => k.toLowerCase().startsWith(d[1].toLowerCase()));
        const want = d[2] ? Array.from({ length: Math.min(20, (Number(d[3] ?? d[2]) - Number(d[2])) + 1) }, (_, i) => Number(d[2]) + i) : [];
        const good = !!docId && want.every((n) => pages.get(docId)!.has(n));
        if (good) out.supported++; else out.unsupported.push(p.slice(0, 80));
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

export async function checkRun(db: any, runId: string, answer: string) {
  if (!runId) return { error: 'run_id required' };
  const { data, error } = await db.rpc('mm_mcp_calls', { p_run: runId });
  if (error) return { error: error.message };
  const calls = data ?? [];
  const seen = calls.filter((c: any) => c.tool !== 'make_chart' && !c.error).map((c: any) => c.output ?? '');
  const charts: any[] = [];
  for (const c of calls) if (c.tool === 'make_chart' && !c.error) {
    try { const ch = JSON.parse(c.output); const i = charts.findIndex((x) => x.title === ch.title); if (i >= 0) charts[i] = ch; else charts.push(ch); } catch { /* ignore */ }
  }
  const trace = calls.map((c: any) => ({ tool: c.tool, args: c.args, rows: c.rows ?? 0, error: c.error ?? undefined,
    preview: c.tool === 'make_chart' ? undefined : forModel(JSON.parse(c.output || 'null')).slice(0, 700) }));
  return { citations: checkCitations(answer, seen), trace, charts, calls: calls.length, ms: calls.reduce((s: number, c: any) => s + (c.ms ?? 0), 0) };
}
