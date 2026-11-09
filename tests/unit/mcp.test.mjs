// The MM MCP server's protocol handler (supabase/functions/mm-mcp/mcp.ts) with a tiny fake Supabase client:
// initialize, tools/list, tools/call (org picking, argument mapping, errors), notifications, and that every tool's
// database function exists in llm.sql and is open to anon (row-level security decides what comes back).
//
//   node tests/unit/mcp.test.mjs      (from the repo root; Node 22.18+ runs the .ts files directly)
import { readFileSync } from 'node:fs';
import { handle, listTools, PROTOCOL_VERSIONS } from '../../supabase/functions/mm-mcp/mcp.ts';
import { DEFS } from '../../supabase/functions/mm-llm-ask/tools.ts';

const failures = [];
const check = (name, ok, detail = '') => { if (!ok) failures.push(name); console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail ? ' — ' + detail : '')); };

const SIM = '00000000-0000-4000-8000-000000000002', DEMO = '00000000-0000-4000-8000-000000000001', MINE = '00000000-0000-4000-8000-000000000009';
function fakeDb({ signedIn = false } = {}) {
  const calls = [];
  const db = {
    calls,
    rpc: async (fn, args = {}) => {
      calls.push({ fn, args });
      if (fn === 'mm_llm_public_org') return { data: [{ id: DEMO, name: 'Demo Mill' }, { id: SIM, name: 'Sim Mill' }], error: null };
      if (fn === 'mm_llm_my_access') return signedIn ? { data: [{ org_id: MINE, org_name: 'PM1' }], error: null } : { data: null, error: { message: 'permission denied' } };
      if (fn === 'mm_llm_context') return { data: { data_through: '2026-10-31', outages: [{ id: 'OUT-2026-11-11' }] }, error: null };
      if (fn === 'mm_llm_overdue_actions') return { data: [{ title: 'Order REF 2 plates', due: '2026-10-20' }], error: null };
      if (fn === 'mm_llm_pi_daily') return { data: null, error: { message: 'unknown tag' } };
      return { data: [], error: null };
    },
  };
  return db;
}
const rpc = (id, method, params) => ({ jsonrpc: '2.0', id, method, ...(params ? { params } : {}) });
const call = (db, name, args = {}) => handle(rpc(9, 'tools/call', { name, arguments: args }), db, { defaultOrg: 'Sim Mill' });
const text = (r) => r.result.content[0].text;

// ---- protocol ----
let r = await handle(rpc(1, 'initialize', { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 't', version: '0' } }), fakeDb());
check('initialize echoes a supported protocol version', r.result.protocolVersion === '2025-06-18');
check('initialize advertises tools and instructions', !!r.result.capabilities.tools && r.result.instructions.includes('machine_context'));
r = await handle(rpc(1, 'initialize', { protocolVersion: '1999-01-01' }), fakeDb());
check('unknown protocol version → the newest supported', r.result.protocolVersion === PROTOCOL_VERSIONS[0]);
check('notifications get no response', (await handle({ jsonrpc: '2.0', method: 'notifications/initialized' }, fakeDb())) === null);
check('ping', JSON.stringify((await handle(rpc(2, 'ping'), fakeDb())).result) === '{}');
check('unknown method → -32601', (await handle(rpc(3, 'resources/list'), fakeDb())).error?.code === -32601);
check('not JSON-RPC 2.0 → -32600', (await handle({ id: 1, method: 'ping' }, fakeDb())).error?.code === -32600);

// ---- tools/list ----
const tools = (await handle(rpc(4, 'tools/list'), fakeDb())).result.tools;
check('lists every MM LLM tool plus list_orgs and machine_context', tools.length === DEFS.length + 2, `${tools.length} tools`);
check('make_chart is not exposed (the page draws charts)', !tools.some((t) => t.name === 'make_chart'));
check('every tool is read-only', tools.every((t) => t.annotations.readOnlyHint));
check('every tool but list_orgs takes org', tools.every((t) => t.name === 'list_orgs' || t.inputSchema.properties.org));
check('listTools() does not change the shared DEFS schemas', DEFS.every((d) => !d.parameters.properties.org));
check('tool input schemas are objects', tools.every((t) => t.inputSchema.type === 'object'));

// ---- tools/call ----
let db = fakeDb();
r = await call(db, 'list_orgs');
const orgs = JSON.parse(text(r)).orgs;
check('list_orgs signed out: the public orgs only', orgs.map((o) => o.name).join() === 'Demo Mill,Sim Mill');
check('list_orgs describes each demo machine', orgs.every((o) => o.machine && o.machine.includes('PM1')));
r = await call(fakeDb({ signedIn: true }), 'list_orgs');
check('list_orgs signed in: adds the user\'s own org', JSON.parse(text(r)).orgs.some((o) => o.id === MINE));

db = fakeDb();
r = await call(db, 'overdue_actions', { as_of: '2026-10-31' });
let c = db.calls.find((x) => x.fn === 'mm_llm_overdue_actions');
check('default org is MM_MCP_DEFAULT_ORG (Sim Mill)', c?.args.p_org === SIM);
check('arguments map to the database function', c?.args.p_as_of === '2026-10-31' && !('org' in c.args));
check('result names the org and carries the rows', JSON.parse(text(r)).org === 'Sim Mill' && JSON.parse(text(r)).rows.length === 1 && !r.result.isError);

db = fakeDb();
await call(db, 'overdue_actions', { org: 'demo mill' });
check('org by name, any case', db.calls.find((x) => x.fn === 'mm_llm_overdue_actions')?.args.p_org === DEMO);
db = fakeDb();
await call(db, 'overdue_actions', { org: MINE });
check('an unlisted org id is passed through (RLS decides)', db.calls.find((x) => x.fn === 'mm_llm_overdue_actions')?.args.p_org === MINE);
r = await call(fakeDb(), 'overdue_actions', { org: 'Nowhere Mill' });
check('unknown org name → tool error listing the readable orgs', r.result.isError && text(r).includes('Demo Mill, Sim Mill'));

r = await call(fakeDb(), 'machine_context', { org: 'Demo Mill' });
const ctx = JSON.parse(text(r));
check('machine_context: machine text plus the database context', ctx.org === 'Demo Mill' && ctx.machine.includes('linerboard') && ctx.data_through === '2026-10-31');

r = await call(fakeDb(), 'pi_daily', { tag: 'X', from: '2026-01-01', to: '2026-01-31' });
check('a database error comes back as isError, not a protocol error', r.result.isError === true && text(r).includes('unknown tag'));
r = await call(fakeDb(), 'drop_tables');
check('unknown tool → -32602', r.error?.code === -32602);

// ---- every tool's database function exists and is open to anon ----
const sql = readFileSync(new URL('../../supabase/llm.sql', import.meta.url), 'utf8');
const anonLoop = sql.slice(sql.indexOf("foreach f in array array['mm_llm_context(uuid)'"));
for (const fn of ['mm_llm_context', 'mm_llm_public_org', ...DEFS.map((d) => d.rpc)]) {
  const defined = sql.includes(`function public.${fn}(`);
  const open = fn === 'mm_llm_public_org' || anonLoop.includes(`'${fn}(`) || new RegExp(`grant execute on function public\\.${fn}\\([^)]*\\) to anon`).test(sql);
  check(`${fn} is defined and granted to anon`, defined && open);
}

console.log(failures.length ? `\n${failures.length} FAILED` : '\nall passed');
process.exit(failures.length ? 1 : 0);
