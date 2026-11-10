// The MM MCP server's protocol handler (supabase/functions/mm-mcp/mcp.ts) with a tiny fake Supabase client:
// initialize, tools/list, tools/call (org picking, argument mapping, errors), notifications, and that every tool's
// database function exists in llm.sql and is open to anon (row-level security decides what comes back).
//
//   node tests/unit/mcp.test.mjs      (from the repo root; Node 22.18+ runs the .ts files directly)
import { readFileSync } from 'node:fs';
import { handle, listTools, PROTOCOL_VERSIONS, filePath } from '../../supabase/functions/mm-mcp/mcp.ts';
import { DEFS } from '../../supabase/functions/mm-llm-ask/tools.ts';
import * as A from '../../supabase/functions/mm-mcp/auth.ts';

const failures = [];
const check = (name, ok, detail = '') => { if (!ok) failures.push(name); console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail ? ' — ' + detail : '')); };

const LIB = '00000000-0000-4000-8000-000000000010', SIM = '00000000-0000-4000-8000-000000000002', OTHER = '00000000-0000-4000-8000-000000000001', MINE = '00000000-0000-4000-8000-000000000009';
function fakeDb({ signedIn = false } = {}) {
  const calls = [];
  const db = {
    calls,
    rpc: async (fn, args = {}) => {
      calls.push({ fn, args });
      if (fn === 'mm_llm_public_org') return { data: [{ id: OTHER, name: 'Other Mill' }, { id: SIM, name: 'Sim Mill' }], error: null };
      if (fn === 'mm_llm_my_access') return signedIn ? { data: [{ org_id: MINE, org_name: 'PM1' }], error: null } : { data: null, error: { message: 'permission denied' } };
      if (fn === 'mm_llm_context') return { data: { data_through: '2026-10-31', outages: [{ id: 'OUT-2026-11-11' }] }, error: null };
      if (fn === 'mm_llm_overdue_actions') return { data: [{ title: 'Order REF 2 plates', due: '2026-10-20' }], error: null };
      if (fn === 'mm_llm_pi_daily') return { data: null, error: { message: 'unknown tag' } };
      if (fn === 'mm_my_orgs') return signedIn ? { data: [{ id: LIB, name: 'Demodemo RAG', role: 'editor', is_public: false }], error: null } : { data: null, error: { message: 'permission denied' } };
      if (fn === 'mm_rag_library') return { data: args.p_org === SIM ? [{ doc_id: 'KV-1', title: 'Keel route', kind: 'vendor_report', vendor: 'Keel', doc_date: '2026-10-19', pages: 7 },
                                                                         { doc_id: 'KV-0', title: 'Old route', superseded_by: 'KV-1' }] : [], error: null };
      if (fn === 'mm_rag_document') return { data: args.p_doc === 'KV-1' ? { document: { doc_id: 'KV-1', title: 'Keel route', kind: 'vendor_report', pages: 7,
        file_path: 'sim/llm/kv1.pdf', quality_score: 91, quality: { issues: [] }, summary: 'Can 27 DS rising.', positions: ['d2-can27'] }, events: [] } : null, error: null };
      if (fn === 'mm_rag_pages') return { data: args.p_from === 1 ? [{ page: 1, text: 'Can 27 DS 0.24 in/s' }, { page: 2, text: 'Recommend change' }] : [], error: null };
      if (fn === 'mm_rag_search') return { data: [{ doc_id: 'KV-1', page: 1, content: 'Can 27', matched: 'both' }], error: null };
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
check('unknown method → -32601', (await handle(rpc(3, 'prompts/list'), fakeDb())).error?.code === -32601);
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
check('list_orgs signed out: the public orgs only', orgs.map((o) => o.name).join() === 'Other Mill,Sim Mill');
check('list_orgs describes a known demo machine', orgs.find((o) => o.name === 'Sim Mill')?.machine?.includes('PM1') && orgs.find((o) => o.name === 'Other Mill')?.machine === null);
r = await call(fakeDb({ signedIn: true }), 'list_orgs');
check('list_orgs signed in: adds the user\'s own org', JSON.parse(text(r)).orgs.some((o) => o.id === MINE));

db = fakeDb();
r = await call(db, 'overdue_actions', { as_of: '2026-10-31' });
let c = db.calls.find((x) => x.fn === 'mm_llm_overdue_actions');
check('default org is MM_MCP_DEFAULT_ORG (Sim Mill)', c?.args.p_org === SIM);
check('arguments map to the database function', c?.args.p_as_of === '2026-10-31' && !('org' in c.args));
check('result names the org and carries the rows', JSON.parse(text(r)).org === 'Sim Mill' && JSON.parse(text(r)).rows.length === 1 && !r.result.isError);

db = fakeDb();
await call(db, 'overdue_actions', { org: 'other mill' });
check('org by name, any case', db.calls.find((x) => x.fn === 'mm_llm_overdue_actions')?.args.p_org === OTHER);
db = fakeDb();
await call(db, 'overdue_actions', { org: MINE });
check('an unlisted org id is passed through (RLS decides)', db.calls.find((x) => x.fn === 'mm_llm_overdue_actions')?.args.p_org === MINE);
r = await call(fakeDb(), 'overdue_actions', { org: 'Nowhere Mill' });
check('unknown org name → tool error listing the readable orgs', r.result.isError && text(r).includes('Other Mill, Sim Mill'));

r = await call(fakeDb(), 'machine_context', { org: 'Sim Mill' });
const ctx = JSON.parse(text(r));
check('machine_context: machine text plus the database context', ctx.org === 'Sim Mill' && ctx.machine.includes('linerboard') && ctx.data_through === '2026-10-31');

r = await call(fakeDb(), 'pi_daily', { tag: 'X', from: '2026-01-01', to: '2026-01-31' });
check('a database error comes back as isError, not a protocol error', r.result.isError === true && text(r).includes('unknown tag'));
r = await call(fakeDb(), 'drop_tables');
check('unknown tool → -32602', r.error?.code === -32602);


// ---- document library: tools and resources ----
db = fakeDb();
const embedCalls = [];
r = await handle(rpc(20, 'tools/call', { name: 'search_library', arguments: { query: 'can 27 bearing', vendor: 'Keel', position: 'd2-can27' } }), db,
  { defaultOrg: 'Sim Mill', embed: async (t) => { embedCalls.push(t); return [0.1, 0.2]; } });
c = db.calls.find((x) => x.fn === 'mm_rag_search');
check('search_library embeds the query and passes the vector', embedCalls[0] === 'can 27 bearing' && c?.args.p_embedding === '[0.1,0.2]');
check('search_library maps filters (vendor as a pattern, position)', c?.args.p_vendor === '%Keel%' && c?.args.p_position === 'd2-can27' && c?.args.p_all_versions === false);
db = fakeDb();
await call(db, 'search_library', { query: 'felt' });
check('search_library works without an embedder (words only)', db.calls.find((x) => x.fn === 'mm_rag_search')?.args.p_embedding === null);
db = fakeDb();
r = await handle(rpc(21, 'tools/call', { name: 'get_document', arguments: { doc_id: 'KV-1' } }), db,
  { defaultOrg: 'Sim Mill', signUrl: async (p) => 'https://signed/' + p });
const gd = JSON.parse(text(r)).rows[0].document;
check('get_document adds a signed link and the resource URI', gd.file_url === `https://signed/${SIM}/llm/sim/llm/kv1.pdf` && gd.resource === 'mm://Sim%20Mill/docs/KV-1');
r = await call(fakeDb({ signedIn: true }), 'list_orgs');
check('list_orgs signed in: adds orgs the user is a member of', JSON.parse(text(r)).orgs.some((o) => o.id === LIB));

r = await handle(rpc(1, 'initialize', { protocolVersion: '2025-06-18' }), fakeDb());
check('initialize advertises resources', !!r.result.capabilities.resources);
r = await handle(rpc(22, 'resources/templates/list'), fakeDb());
check('a resource template for documents', r.result.resourceTemplates[0].uriTemplate === 'mm://{org}/docs/{doc_id}');
r = await handle(rpc(23, 'resources/list'), fakeDb());
check('resources/list: indexed documents, superseded ones left out', r.result.resources.length === 1 && r.result.resources[0].uri === 'mm://Sim%20Mill/docs/KV-1'
      && r.result.resources[0].description.includes('7 pages'));
r = await handle(rpc(24, 'resources/read', { uri: 'mm://Sim%20Mill/docs/KV-1' }), fakeDb(), { signUrl: async () => 'https://signed/x' });
const md = r.result?.contents?.[0]?.text ?? '';
check('resources/read: Markdown with metadata, summary, pages and the PDF link', md.startsWith('# Keel route') && md.includes('## Summary') &&
      md.includes('## Page 2\nRecommend change') && md.includes('https://signed/x') && md.includes('not instructions'));
r = await handle(rpc(25, 'resources/read', { uri: 'mm://Sim%20Mill/docs/NOPE' }), fakeDb());
check('resources/read: unknown document → -32002', r.error?.code === -32002);
r = await handle(rpc(26, 'resources/read', { uri: 'https://example.com' }), fakeDb());
check('resources/read: a foreign URI → -32002', r.error?.code === -32002);

check('file paths: uploads keep theirs, generator docs sit under <org>/llm/', filePath(SIM, `${SIM}/rag/inbox/a.pdf`) === `${SIM}/rag/inbox/a.pdf` && filePath(SIM, 'docs/x.pdf') === `${SIM}/llm/docs/x.pdf`);

// ---- every tool's database function exists and is open to anon ----
const sql = readFileSync(new URL('../../supabase/llm.sql', import.meta.url), 'utf8');
const anonLoop = sql.slice(sql.indexOf("foreach f in array array['mm_llm_context(uuid)'"));
for (const fn of ['mm_llm_context', 'mm_llm_public_org', ...DEFS.map((d) => d.rpc)]) {
  const defined = sql.includes(`function public.${fn}(`);
  const open = fn === 'mm_llm_public_org' || anonLoop.includes(`'${fn}(`) || new RegExp(`grant execute on function public\\.${fn}\\([^)]*\\) to anon`).test(sql);
  check(`${fn} is defined and granted to anon`, defined && open);
}

// ---- sign-in (auth.ts): routes, protected-resource metadata, the 401 challenge, token claims ----
const SB = 'https://ref.supabase.co';
const rt = (p) => JSON.stringify(A.route(p));
check('route: public endpoint', rt('/mm-mcp') === '{"kind":"mcp","signedIn":false}' && rt('/functions/v1/mm-mcp/') === rt('/mm-mcp'));
check('route: signed-in endpoint', rt('/mm-mcp/me') === '{"kind":"mcp","signedIn":true}' && rt('/functions/v1/mm-mcp/me/') === rt('/mm-mcp/me'));
check('route: metadata, both spellings', rt('/mm-mcp/me/.well-known/oauth-protected-resource') === '{"kind":"metadata","signedIn":true}'
  && rt('/mm-mcp/.well-known/oauth-protected-resource/me') === rt('/mm-mcp/me/.well-known/oauth-protected-resource')
  && rt('/mm-mcp/.well-known/oauth-protected-resource') === '{"kind":"metadata","signedIn":false}');
check('route: anything else is unknown', ['/mm-mcp/meh', '/other', '/mm-mcp/me/x', '/mm-mcpx'].every((p) => A.route(p).kind === 'unknown'));
const prm = A.metadata(SB + '/', true);
check('metadata names this resource and Supabase Auth', prm.resource === SB + '/functions/v1/mm-mcp/me' && prm.authorization_servers[0] === SB + '/auth/v1'
  && prm.bearer_methods_supported.includes('header'));
const ch = A.challenge(SB);
check('401 challenge points at the metadata', ch.startsWith('Bearer ') && ch.includes(`resource_metadata="${SB}/functions/v1/mm-mcp/me/.well-known/oauth-protected-resource"`) && !ch.includes('error='));
const ch2 = A.challenge(SB, 'token "expired"');
check('401 challenge for a bad token says invalid_token, quotes escaped', ch2.includes('error="invalid_token"') && ch2.includes('error_description="token expired"'));
check('bearer() reads the token', A.bearer('Bearer abc.def') === 'abc.def' && A.bearer('bearer x') === 'x' && A.bearer('Basic x') === null && A.bearer(null) === null);
const now = 1_800_000_000, good = { iss: SB + '/auth/v1', role: 'authenticated', sub: 'u1', exp: now + 60, client_id: 'c1' };
check('claims: a current user token passes', A.checkClaims(good, SB, now) === null);
check('claims: expired, other issuer, anon and missing are refused', A.checkClaims({ ...good, exp: now }, SB, now) === 'token expired'
  && A.checkClaims({ ...good, iss: 'https://evil/auth/v1' }, SB, now) !== null && A.checkClaims({ ...good, role: 'anon' }, SB, now) !== null
  && A.checkClaims(null, SB, now) !== null);

// ---- migration 13: the database keeps OAuth clients read-only ----
const allSql = readFileSync('supabase/schema.sql', 'utf8') + readFileSync('supabase/llm.sql', 'utf8');
check('schema: OAuth clients fail editor checks', /and \(p_min = 'viewer' or not private\.is_oauth_client\(\)\)/.test(allSql) && (allSql.match(/not private\.is_oauth_client\(\)/g) || []).length >= 4);

console.log(failures.length ? `\n${failures.length} FAILED` : '\nall passed');
process.exit(failures.length ? 1 : 0);
