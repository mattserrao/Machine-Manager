// MM MCP: the MM LLM tools as a Model Context Protocol server (JSON-RPC over Streamable HTTP, stateless).
// No Deno or npm imports here, so the unit tests can run it in Node; index.ts wires it to Deno.serve and Supabase.
//
// The tools are the same read-only mm_llm_* functions mm-llm-ask uses (DEFS / runTool in ../mm-llm-ask/tools.ts),
// with an extra `org` argument, plus list_orgs and machine_context. They run with the caller's session (or the anon
// key when signed out), so row-level security decides what comes back: signed out, only the public demo orgs.
import { DEFS, runTool, forModel } from '../mm-llm-ask/tools.ts';
import { MACHINES } from '../mm-llm-ask/prompt.ts';

export const SERVER = { name: 'machine-manager', title: 'Machine Manager', version: '0.1.0' };
export const PROTOCOL_VERSIONS = ['2025-11-25', '2025-06-18', '2025-03-26', '2024-11-05'];   // newest first

export const INSTRUCTIONS = `Machine Manager holds a year of data for PM1, a paper machine, for each organization: Pi trends, \
Bonvoy exception reports (Pi tags outside 3-sigma), BUS daily sheets, JDE work orders, Teams/Planner actions, RCFAs, vendor \
reports, shift and production reports, downtime and position (fabric, felt, roll, plate) life.
- Start with list_orgs, then machine_context for the org you use: it gives today's date in the data, the outages, the \
My Machine position ids and the Pi tags the other tools take. Every tool takes an optional org (name or id); the default is \
the first listed org.
- Answer only from what the tools return; never invent numbers, dates, WO numbers or names. Check more than one source when \
it matters (trend, BUS, vendor report, WO and parts status, RCFA and actions).
- Cite sources in square brackets: [WO 2591919], [RCFA-2026-03], [Bonvoy PM1:TAG 2026-09-22], [BUS 2026-10-21], \
[Shift Report <id>], [Bonvoy Report <day>].
- For totals and trends use downtime_summary, downtime_events and production (exact), and normalise before ranking \
(grade_hours for per-100 h rates). Check the premise of a question against the data before answering it.
- All data is fictional demo data unless you are signed in to your own organization.`;

type Db = { rpc: (fn: string, args?: Record<string, unknown>) => PromiseLike<{ data: any; error: any }> };
type Org = { id: string; name: string };
type Msg = { jsonrpc?: string; id?: string | number | null; method?: string; params?: any };

const ORG_ARG = { type: 'string', description: 'Organization name or id from list_orgs (default: the first one).' };
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const READ_ONLY = { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false };

const EXTRA = [
  { name: 'list_orgs', title: 'List organizations',
    description: 'The organizations you can read: the public demo orgs (Demo Mill, Sim Mill), plus your own when signed in.',
    inputSchema: { type: 'object', properties: {} } },
  { name: 'machine_context', title: 'Machine context',
    description: 'What the machine is and what the other tools take: the last day of data ("today"), outages with their ids, My Machine position ids and names, and Pi tags with units. Call this first.',
    inputSchema: { type: 'object', properties: { org: ORG_ARG } } },
];

export function listTools() {
  const tools = DEFS.map((d) => ({ name: d.name, description: d.description,
    inputSchema: { ...d.parameters, properties: { ...(d.parameters as any).properties, org: ORG_ARG } } }));
  return [...EXTRA, ...tools].map((t) => ({ ...t, annotations: READ_ONLY }));
}

// Orgs the caller can read. Signed out, mm_llm_my_access is refused (anon), which just leaves the public orgs.
export async function readableOrgs(db: Db): Promise<Org[]> {
  const out: Org[] = [];
  const { data: pub } = await db.rpc('mm_llm_public_org');
  for (const p of pub ?? []) out.push({ id: p.id, name: p.name });
  try {
    const { data: mine } = await db.rpc('mm_llm_my_access');
    for (const m of mine ?? []) if (!out.some((o) => o.id === m.org_id)) out.push({ id: m.org_id, name: m.org_name });
  } catch { /* signed out */ }
  return out;
}

export function pickOrg(orgs: Org[], want: unknown, fallback?: string): Org | { error: string } {
  const w = String(want ?? '').trim();
  if (!w) {
    const d = (fallback && orgs.find((o) => o.name.toLowerCase() === fallback.toLowerCase())) || orgs[0];
    return d ?? { error: 'No organizations are readable. Sign in, or check that a demo org is public.' };
  }
  const hit = orgs.find((o) => o.id === w || o.name.toLowerCase() === w.toLowerCase());
  if (hit) return hit;
  if (UUID.test(w)) return { id: w, name: w };   // not listed, but row-level security decides
  return { error: `Unknown org "${w}". Readable: ${orgs.map((o) => o.name).join(', ') || 'none'}.` };
}

async function callTool(db: Db, name: string, args: Record<string, any>, defaultOrg?: string) {
  const orgs = await readableOrgs(db);
  if (name === 'list_orgs') return { orgs: orgs.map((o) => ({ ...o, machine: MACHINES[o.name] ?? null })) };
  const org = pickOrg(orgs, args.org, defaultOrg);
  if ('error' in org) return org;
  const { org: _drop, ...rest } = args;
  if (name === 'machine_context') {
    const { data, error } = await db.rpc('mm_llm_context', { p_org: org.id });
    if (error) return { error: error.message };
    return { org: org.name, machine: MACHINES[org.name] ?? null, ...(data ?? {}) };
  }
  const r: any = await runTool(db, org.id, name, rest);
  return r.error ? r : { org: org.name, ...r };
}

const ok = (id: Msg['id'], result: unknown) => ({ jsonrpc: '2.0', id, result });
const fail = (id: Msg['id'], code: number, message: string) => ({ jsonrpc: '2.0', id: id ?? null, error: { code, message } });

// One JSON-RPC message in, one response out (null for notifications and client responses: HTTP 202, no body).
export async function handle(msg: Msg, db: Db, opts: { defaultOrg?: string } = {}): Promise<object | null> {
  if (!msg || typeof msg !== 'object' || Array.isArray(msg) || msg.jsonrpc !== '2.0') return fail(null, -32600, 'Invalid Request');
  if (msg.method === undefined) return null;                    // a response to something we never send
  if (msg.id === undefined || msg.id === null) return null;     // notification (notifications/initialized, cancelled …)
  const { id, method, params } = msg;
  switch (method) {
    case 'initialize': {
      const asked = String(params?.protocolVersion ?? '');
      return ok(id, { protocolVersion: PROTOCOL_VERSIONS.includes(asked) ? asked : PROTOCOL_VERSIONS[0],
        capabilities: { tools: { listChanged: false } }, serverInfo: SERVER, instructions: INSTRUCTIONS });
    }
    case 'ping': return ok(id, {});
    case 'tools/list': return ok(id, { tools: listTools() });
    case 'tools/call': {
      const name = String(params?.name ?? '');
      const args = params?.arguments && typeof params.arguments === 'object' ? params.arguments : {};
      if (!listTools().some((t) => t.name === name)) return fail(id, -32602, `Unknown tool: ${name}`);
      try {
        const r: any = await callTool(db, name, args, opts.defaultOrg);
        return ok(id, { content: [{ type: 'text', text: r.error ? r.error : forModel(r) }], isError: !!r.error });
      } catch (e) {
        return ok(id, { content: [{ type: 'text', text: `Tool failed: ${(e as Error).message}` }], isError: true });
      }
    }
    default: return fail(id, -32601, `Method not found: ${method}`);
  }
}
