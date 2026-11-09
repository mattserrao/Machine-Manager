// MM MCP (Supabase Edge Function): Machine Manager's read-only MM LLM tools for any MCP client (Claude, MCP Inspector …).
//
//   Endpoint:  https://<project>.supabase.co/functions/v1/mm-mcp   (Streamable HTTP; POST JSON-RPC, JSON responses)
//   Deploy:    supabase functions deploy mm-mcp --no-verify-jwt     (it handles callers itself, like mm-llm-ask)
//
// Who can read what:
//   - no Authorization header: the anon key, so only the public demo orgs (Demo Mill, Sim Mill);
//   - Authorization: Bearer <user session token>: that user's session, so row-level security adds their own orgs.
// Nothing is written and no model is called, so there is no daily cap. Stateless: no sessions, no SSE stream (GET → 405).
// MM_MCP_DEFAULT_ORG (optional) names the org used when a tool call doesn't give one; otherwise the first public org.
import { createClient } from 'npm:@supabase/supabase-js@2';
import { handle } from './mcp.ts';

const URL_ = Deno.env.get('SUPABASE_URL')!, ANON = Deno.env.get('SUPABASE_ANON_KEY')!;
const DEFAULT_ORG = Deno.env.get('MM_MCP_DEFAULT_ORG') ?? 'Sim Mill';
const cors = { 'Access-Control-Allow-Origin': '*', 'Access-Control-Expose-Headers': 'mcp-session-id',
  'Access-Control-Allow-Headers': 'authorization, apikey, content-type, accept, mcp-protocol-version, mcp-session-id, last-event-id',
  'Access-Control-Allow-Methods': 'POST, GET, DELETE, OPTIONS' };
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { ...cors, 'Content-Type': 'application/json' } });

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return new Response('POST JSON-RPC messages to this endpoint (no SSE stream).', { status: 405, headers: { ...cors, Allow: 'POST' } });
  let msg: any;
  try { msg = await req.json(); } catch { return json({ jsonrpc: '2.0', id: null, error: { code: -32700, message: 'Parse error' } }, 400); }
  if (Array.isArray(msg)) return json({ jsonrpc: '2.0', id: null, error: { code: -32600, message: 'Batches are not supported' } }, 400);

  const auth = req.headers.get('Authorization');
  const db = createClient(URL_, ANON, { auth: { persistSession: false }, ...(auth?.startsWith('Bearer ') ? { global: { headers: { Authorization: auth } } } : {}) });
  const out = await handle(msg, db, { defaultOrg: DEFAULT_ORG });
  return out ? json(out) : new Response(null, { status: 202, headers: cors });
});
