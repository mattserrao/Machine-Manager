// The MM MCP edge function (supabase/functions/mm-mcp/index.ts) as HTTP, in Node: Deno.serve and the Supabase client
// are stand-ins (a fake getClaims and rpc), so this checks the routes, the OAuth 401 challenge, the protected-resource
// metadata and that a valid token reaches the tools as that user.
//
//   node tests/unit/mcp_http.test.mjs      (from the repo root; Node 22.18+)
import { register } from 'node:module';

const failures = [];
const check = (name, ok, detail = '') => { if (!ok) failures.push(name); console.log((ok ? 'PASS ' : 'FAIL ') + name + (detail ? ' — ' + detail : '')); };

// npm:@supabase/supabase-js@2 → a fake client. Tokens: 'good' (a current user token), 'expired', anything else invalid.
const FAKE = `
const SB = 'https://ref.supabase.co';
export const calls = globalThis.__calls = [];
export function createClient(url, key, opts = {}) {
  const auth = opts.global?.headers?.Authorization ?? null;
  return {
    auth: { getClaims: async (t) => {
      const now = Math.floor(Date.now() / 1000);
      if (t === 'good') return { data: { claims: { iss: SB + '/auth/v1', role: 'authenticated', sub: 'u1', exp: now + 600, client_id: 'c1' } }, error: null };
      if (t === 'expired') return { data: { claims: { iss: SB + '/auth/v1', role: 'authenticated', sub: 'u1', exp: now - 5 } }, error: null };
      return { data: null, error: { message: 'invalid JWT' } };
    } },
    rpc: async (fn, args) => { calls.push({ fn, auth });
      if (fn === 'mm_llm_public_org') return { data: [{ id: 'sim', name: 'Sim Mill' }], error: null };
      if (fn === 'mm_my_orgs') return auth ? { data: [{ id: 'lib', name: 'Demodemo RAG' }], error: null } : { data: null, error: { message: 'denied' } };
      if (fn === 'mm_llm_my_access') return { data: [], error: null };
      return { data: [], error: null };
    },
    storage: { from: () => ({ createSignedUrl: async () => ({ data: null }) }) },
  };
}`;
register('data:text/javascript,' + encodeURIComponent(`
export async function resolve(spec, ctx, next) {
  if (spec === 'npm:@supabase/supabase-js@2') return { url: 'data:text/javascript,' + ${JSON.stringify(encodeURIComponent(FAKE))}, shortCircuit: true };
  return next(spec, ctx);
}`));

let handler = null;
globalThis.Deno = { env: { get: (k) => ({ SUPABASE_URL: 'https://ref.supabase.co', SUPABASE_ANON_KEY: 'anon' })[k] }, serve: (fn) => { handler = fn; } };
await import('../../supabase/functions/mm-mcp/index.ts');
check('index.ts registers a handler', typeof handler === 'function');

const BASE = 'https://ref.supabase.co/functions/v1';
const rpc = (method, params = {}) => JSON.stringify({ jsonrpc: '2.0', id: 1, method, params });
const send = (path, { method = 'POST', token, body = rpc('tools/call', { name: 'list_orgs', arguments: {} }) } = {}) =>
  handler(new Request(BASE + path, { method, body: method === 'POST' ? body : undefined,
    headers: { 'content-type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) } }));

let r = await send('/mm-mcp/me');
const www = r.headers.get('www-authenticate') ?? '';
check('/me without a token: 401', r.status === 401);
check('/me 401 points at the protected-resource metadata', www.includes(`resource_metadata="${BASE}/mm-mcp/me/.well-known/oauth-protected-resource"`), www);
check('the challenge header is readable from browsers (CORS)', (r.headers.get('access-control-expose-headers') ?? '').includes('www-authenticate'));

r = await send('/mm-mcp/me/.well-known/oauth-protected-resource', { method: 'GET' });
const prm = await r.json();
check('metadata: 200 JSON naming Supabase Auth', r.status === 200 && prm.resource === `${BASE}/mm-mcp/me` && prm.authorization_servers?.[0] === 'https://ref.supabase.co/auth/v1');

r = await send('/mm-mcp/me', { token: 'expired' });
check('/me with an expired token: 401 invalid_token', r.status === 401 && (r.headers.get('www-authenticate') ?? '').includes('invalid_token'));
r = await send('/mm-mcp/me', { token: 'forged' });
check('/me with an invalid token: 401', r.status === 401);

globalThis.__calls.length = 0;
r = await send('/mm-mcp/me', { token: 'good' });
let out = await r.json();
const orgs = JSON.parse(out.result?.content?.[0]?.text ?? '{}').orgs ?? [];
check('/me with a valid token: tools run', r.status === 200 && !out.result?.isError);
check('…as that user (their private org is listed)', orgs.some((o) => o.name === 'Demodemo RAG') && orgs.some((o) => o.name === 'Sim Mill'), JSON.stringify(orgs));
check('…with the token passed to the database', globalThis.__calls.every((c) => c.auth === 'Bearer good'));

r = await send('/mm-mcp');
out = await r.json();
check('public endpoint without a token: works as before (public orgs only)', r.status === 200 && JSON.parse(out.result.content[0].text).orgs.map((o) => o.name).join() === 'Sim Mill');
r = await send('/mm-mcp', { token: 'anon-key-or-anything' });
check('public endpoint passes a token through unchecked, as before', r.status === 200);
r = await send('/mm-mcp/me', { method: 'GET', token: 'good' });
check('/me GET (no SSE stream): 405 after sign-in', r.status === 405);
r = await send('/mm-mcp/nope');
check('unknown path: 404', r.status === 404);
r = await send('/mm-mcp/me', { method: 'OPTIONS' });
check('CORS preflight needs no token', r.status === 200);

console.log(failures.length ? `\n${failures.length} FAILED` : '\nall passed');
process.exit(failures.length ? 1 : 0);
