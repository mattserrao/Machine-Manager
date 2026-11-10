// MM MCP sign-in (OAuth 2.1, per the MCP authorization spec). No Deno or npm imports, so the unit tests run it in Node.
//
// Two endpoints, one server:
//   .../functions/v1/mm-mcp      public: no sign-in needed, the public demo orgs (Sim Mill). A Bearer token still works
//                                (Claude Code, MCP Inspector) and adds that user's orgs.
//   .../functions/v1/mm-mcp/me   signed in: a request without a valid token gets 401 and a WWW-Authenticate header that
//                                points at this server's protected-resource metadata, which names Supabase Auth
//                                (<project>/auth/v1) as the authorization server. The MCP client (Claude's custom
//                                connector) then registers itself, sends the user to the consent page
//                                (ConnectedApps.html on the site), and comes back with a Supabase access token.
// Access tokens are Supabase JWTs for that user with a client_id claim. Row-level security decides what they read, and the
// database makes them read-only (private.is_oauth_client, migration 13).

export const SCOPES = ['email'];   // only identity scopes exist; data access is decided by RLS, not scopes

export type Route = { kind: 'metadata' | 'mcp'; signedIn: boolean } | { kind: 'unknown' };

// pathname as the function sees it: /mm-mcp, /mm-mcp/me, /mm-mcp/.well-known/oauth-protected-resource[/me],
// /mm-mcp/me/.well-known/oauth-protected-resource (with or without /functions/v1 in front, and a trailing slash).
export function route(pathname: string): Route {
  const p = pathname.replace(/^\/functions\/v1/, '').replace(/\/+$/, '');
  const m = /^\/mm-mcp(\/.*)?$/.exec(p);
  if (!m) return { kind: 'unknown' };
  const rest = m[1] ?? '';
  const WK = '/.well-known/oauth-protected-resource';
  if (rest === WK) return { kind: 'metadata', signedIn: false };
  if (rest === WK + '/me' || rest === '/me' + WK) return { kind: 'metadata', signedIn: true };
  if (rest === '') return { kind: 'mcp', signedIn: false };
  if (rest === '/me') return { kind: 'mcp', signedIn: true };
  return { kind: 'unknown' };
}

const trim = (u: string) => u.replace(/\/+$/, '');
export const base = (supabaseUrl: string) => `${trim(supabaseUrl)}/functions/v1/mm-mcp`;
export const issuer = (supabaseUrl: string) => `${trim(supabaseUrl)}/auth/v1`;
export const metadataUrl = (supabaseUrl: string, signedIn = true) =>
  `${base(supabaseUrl)}${signedIn ? '/me' : ''}/.well-known/oauth-protected-resource`;

// RFC 9728 protected-resource metadata.
export function metadata(supabaseUrl: string, signedIn = true) {
  return {
    resource: base(supabaseUrl) + (signedIn ? '/me' : ''),
    authorization_servers: [issuer(supabaseUrl)],
    scopes_supported: SCOPES,
    bearer_methods_supported: ['header'],
    resource_name: signedIn ? 'Machine Manager (signed in)' : 'Machine Manager',
  };
}

// The 401 challenge (RFC 6750 + RFC 9728). error is set when a token was sent but isn't valid.
export function challenge(supabaseUrl: string, error?: string) {
  const parts = [`resource_metadata="${metadataUrl(supabaseUrl, true)}"`, `scope="${SCOPES.join(' ')}"`];
  if (error) parts.push('error="invalid_token"', `error_description="${error.replace(/["\\]/g, '')}"`);
  return 'Bearer ' + parts.join(', ');
}

export const bearer = (header: string | null) => {
  const m = /^Bearer\s+(\S+)\s*$/i.exec(header ?? '');
  return m ? m[1] : null;
};

// After the signature check (supabase.auth.getClaims): is this a token this server accepts? Supabase Auth must have
// issued it for a signed-in user, and it must not have expired. Returns an error message, or null when it's fine.
export function checkClaims(claims: any, supabaseUrl: string, nowSec = Math.floor(Date.now() / 1000)): string | null {
  if (!claims || typeof claims !== 'object') return 'no claims';
  if (claims.iss !== issuer(supabaseUrl)) return 'token from another issuer';
  if (claims.role !== 'authenticated' || !claims.sub) return 'not a signed-in user';
  if (typeof claims.exp !== 'number' || claims.exp <= nowSec) return 'token expired';
  return null;
}
