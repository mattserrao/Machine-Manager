// The assistant's tools: thin wrappers over the read-only mm_llm_* database functions. They run with the asking
// user's own session, so row-level security decides what comes back. Results are trimmed before the model sees them.
import type { Tool } from './adapter.ts';

const date = { type: 'string', description: 'YYYY-MM-DD' };
type Def = Tool & { rpc: string; map: (a: any) => Record<string, unknown>; maxRows?: number; filter?: (rows: any[], a: any) => any[] };

export const DEFS: Def[] = [
  { name: 'search_documents', rpc: 'mm_llm_search_docs',
    description: 'Full-text search over documents: vendor reports (clothing surveys, vibration routes, roll service, shower audits, refiner plate reports, trial reports), RCFA write-ups, drawings and reference charts. Returns doc ids, titles, dates and matching snippets. Use specific words (equipment names, findings).',
    parameters: { type: 'object', properties: { query: { type: 'string' }, positions: { type: 'array', items: { type: 'string' }, description: 'optional My Machine position ids to narrow to' }, limit: { type: 'integer', minimum: 1, maximum: 15 } }, required: ['query'] },
    map: (a) => ({ p_query: a.query, p_limit: a.limit ?? 8, p_positions: a.positions?.length ? a.positions : null }) },
  { name: 'search_records', rpc: 'mm_llm_search_records',
    description: 'Full-text search across BUS daily sheet issues, JDE work orders, Teams/Planner actions and RCFAs. Use when you only know words (e.g. "Ridgeway plates order", "steam limited").',
    parameters: { type: 'object', properties: { query: { type: 'string' }, limit: { type: 'integer', minimum: 1, maximum: 40 } }, required: ['query'] },
    map: (a) => ({ p_query: a.query, p_limit: a.limit ?? 20 }) },
  { name: 'position_history', rpc: 'mm_llm_position_history', maxRows: 60,
    description: 'Everything known about one position or asset, newest first: BUS issues, work orders, actions, RCFAs, Envoy exceptions and documents. term = a My Machine position id (e.g. p2-felt-top, form-bottom, ref-bp2, cal-bottom), a JDE asset number, or an exact asset name (e.g. "Dryer can 27", "3rd section pocket ventilation"). Optionally filter by sources.',
    parameters: { type: 'object', properties: { term: { type: 'string' }, from: date, to: date,
      sources: { type: 'array', items: { type: 'string', enum: ['BUS', 'WO', 'Action', 'RCFA', 'Envoy', 'Document'] } } }, required: ['term'] },
    map: (a) => ({ p_term: a.term, p_from: a.from ?? null, p_to: a.to ?? null }),
    filter: (rows, a) => a.sources?.length ? rows.filter((r) => a.sources.includes(r.source)) : rows },
  { name: 'outage_scope', rpc: 'mm_llm_outage_scope', maxRows: 150,
    description: 'Work orders planned for an outage, with status, parts status (Reserved / Not reserved) and notes. Outage ids look like OUT-2026-11-11 or OUT-2026-ANNUAL.',
    parameters: { type: 'object', properties: { outage: { type: 'string' } }, required: ['outage'] },
    map: (a) => ({ p_outage: a.outage }) },
  { name: 'overdue_actions', rpc: 'mm_llm_overdue_actions',
    description: 'Teams/Planner actions not completed and past due as of a date (default: the latest export).',
    parameters: { type: 'object', properties: { as_of: date } },
    map: (a) => ({ p_as_of: a.as_of ?? null }) },
  { name: 'envoy_exceptions', rpc: 'mm_llm_envoy', maxRows: 80,
    description: 'Envoy exception reports (Pi tags outside their 3-sigma limits for 3+ hours in a day). term = a Pi tag, asset name, asset number or position id; omit for all. Each row is one tag-day (period = the day covered; the report arrives the next morning).',
    parameters: { type: 'object', properties: { term: { type: 'string' }, from: date, to: date } },
    map: (a) => ({ p_term: a.term ?? null, p_from: a.from ?? null, p_to: a.to ?? null }) },
  { name: 'pi_daily', rpc: 'mm_llm_pi_daily', maxRows: 120,
    description: 'Daily average / min / max of a Pi tag (mill-local days), from hourly data.',
    parameters: { type: 'object', properties: { tag: { type: 'string' }, from: date, to: date }, required: ['tag', 'from', 'to'] },
    map: (a) => ({ p_tag: a.tag, p_from: a.from, p_to: a.to }) },
  { name: 'pi_values', rpc: 'mm_llm_pi_values', maxRows: 200,
    description: 'Raw Pi values for a tag between two times (ISO 8601 with offset, e.g. 2026-02-18T00:00-05:00): hourly, or 1-minute where stored. Keep windows short.',
    parameters: { type: 'object', properties: { tag: { type: 'string' }, from: { type: 'string' }, to: { type: 'string' } }, required: ['tag', 'from', 'to'] },
    map: (a) => ({ p_tag: a.tag, p_from: a.from, p_to: a.to }) },
];
export const TOOLS: Tool[] = DEFS.map(({ name, description, parameters }) => ({ name, description, parameters }));

export async function runTool(db: any, org: string, name: string, args: Record<string, unknown>) {
  const d = DEFS.find((x) => x.name === name);
  if (!d) return { error: `unknown tool ${name}` };
  const { data, error } = await db.rpc(d.rpc, { p_org: org, ...d.map(args) });
  if (error) return { error: error.message };
  let rows = Array.isArray(data) ? data : [data];
  if (d.filter) rows = d.filter(rows, args);
  const total = rows.length, max = d.maxRows ?? 40;
  rows = rows.slice(0, max);
  return { rows, total, truncated: total > max };
}

export function forModel(result: unknown): string {
  let s = JSON.stringify(result);
  if (s.length > 14000) s = s.slice(0, 14000) + ' …(cut; narrow the query)';
  return s;
}
