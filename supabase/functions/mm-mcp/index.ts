// MM MCP (Supabase Edge Function): Machine Manager's read-only MM LLM tools for any MCP client (Claude, MCP Inspector …).
//
//   Endpoint:  https://<project>.supabase.co/functions/v1/mm-mcp      (Streamable HTTP; POST JSON-RPC, JSON responses)
//              https://<project>.supabase.co/functions/v1/mm-mcp/me   the same, signed in with OAuth (see auth.ts)
//   Deploy:    supabase functions deploy mm-mcp --no-verify-jwt     (it handles callers itself, like mm-llm-ask)
//
// Who can read what:
//   - no Authorization header (only on /mm-mcp): the anon key, so only the public demo orgs (today: Sim Mill);
//   - Authorization: Bearer <token>: a user session token, or on /mm-mcp/me the OAuth access token from its sign-in
//     (checked first there: 401 when it isn't valid); used as that user, so row-level security adds their own orgs.
// Nothing is written and no model is called, so there is no daily cap. Stateless: no sessions, no SSE stream (GET → 405).
// MM_MCP_DEFAULT_ORG (optional) names the org used when a tool call doesn't give one; default Sim Mill.
import { createClient } from 'npm:@supabase/supabase-js@2';
import { handle } from './mcp.ts';
import { route, metadata, challenge, bearer, checkClaims } from './auth.ts';

const URL_ = Deno.env.get('SUPABASE_URL')!, ANON = Deno.env.get('SUPABASE_ANON_KEY')!;
const DEFAULT_ORG = Deno.env.get('MM_MCP_DEFAULT_ORG') ?? 'Sim Mill';
let embedder: any = null;   // search_library: gte-small query embeddings, the same model as the document chunks
const embed = async (text: string): Promise<number[]> => {
  // @ts-ignore Supabase.ai is provided by the Edge Runtime
  embedder ??= new Supabase.ai.Session('gte-small');
  return Array.from(await embedder.run(text, { mean_pool: true, normalize: true }) as number[]);
};
const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Expose-Headers': 'mcp-session-id, www-authenticate',
  'Access-Control-Allow-Headers': 'authorization, apikey, content-type, accept, mcp-protocol-version, mcp-session-id, last-event-id',
  'Access-Control-Allow-Methods': 'POST, GET, DELETE, OPTIONS' };
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { ...cors, 'Content-Type': 'application/json' } });

const unauthorized = (error?: string) => new Response(JSON.stringify({ error: error ? 'invalid_token' : 'unauthorized',
  error_description: error ?? 'Sign in to use this endpoint (OAuth). Use /functions/v1/mm-mcp for the public demo.' }),
  { status: 401, headers: { ...cors, 'Content-Type': 'application/json', 'WWW-Authenticate': challenge(URL_, error) } });
const verifier = createClient(URL_, ANON, { auth: { persistSession: false, autoRefreshToken: false } });

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  // Any path that isn't /me or metadata is the public endpoint, as before (so the existing connector never breaks).
  const found = route(new URL(req.url).pathname);
  const r = found.kind === 'unknown' ? { kind: 'mcp' as const, signedIn: false } : found;
  if (r.kind === 'metadata') return json(metadata(URL_, r.signedIn));

  // /me: a valid Supabase token for a signed-in user, or 401 (which starts the client's OAuth sign-in). The public
  // endpoint passes whatever it gets straight to Supabase, as before (some clients send the anon key).
  const token = bearer(req.headers.get('Authorization'));
  if (r.signedIn) {
    if (!token) return unauthorized();
    const { data, error } = await verifier.auth.getClaims(token);
    const bad = error ? error.message : checkClaims(data?.claims, URL_);
    if (bad) return unauthorized(bad);
  }
  if (req.method !== 'POST') return new Response('POST JSON-RPC messages to this endpoint (no SSE stream).', { status: 405, headers: { ...cors, Allow: 'POST' } });
  let msg: any;
  try { msg = await req.json(); } catch { return json({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } }, 400); }
  if (Array.isArray(msg)) return json({ jsonrpc: '2.0', id: null, error: { code: -32600, message: 'Batches are not supported' } }, 400);

  const db = createClient(URL_, ANON, { auth: { persistSession: false }, ...(token ? { global: { headers: { Authorization: `Bearer ${token}` } } } : {}) });
  // Links to a document's original PDF: a short-lived signed URL, under the caller's own storage access.
  const signUrl = async (path: string) => {
    const { data } = await db.storage.from('mm-files').createSignedUrl(path, 3600);
    return data?.signedUrl ?? null;
  };
  const out = await handle(msg, db, { defaultOrg: DEFAULT_ORG, embed, signUrl });
  return out ? json(out) : new Response(null, { status: 202, headers: cors });
});
