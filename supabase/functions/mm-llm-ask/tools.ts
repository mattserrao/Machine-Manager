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
    description: 'Everything known about one position or asset, newest first: BUS issues, work orders, actions, RCFAs, Bonvoy exceptions and documents. term = a My Machine position id (e.g. p2-felt-top, form-bottom, ref-bp2, cal-bottom), a JDE asset number, or an exact asset name (e.g. "Dryer can 27", "3rd section pocket ventilation"). Optionally filter by sources.',
    parameters: { type: 'object', properties: { term: { type: 'string' }, from: date, to: date,
      sources: { type: 'array', items: { type: 'string', enum: ['BUS', 'WO', 'Action', 'RCFA', 'Bonvoy', 'Document'] } } }, required: ['term'] },
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
  { name: 'bonvoy_exceptions', rpc: 'mm_llm_bonvoy', maxRows: 80,
    description: 'Bonvoy exception reports (Pi tags outside their 3-sigma limits for 3+ hours in a day). term = a Pi tag, asset name, asset number or position id; omit for all. Each row is one tag-day (period = the day covered; the report arrives the next morning).',
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
  { name: 'bonvoy_report', rpc: 'mm_llm_bonvoy_report', maxRows: 1,
    description: 'The daily Bonvoy Report for a day (the latest when day is omitted; the last 7 days are kept): a summary, the flagged Pi trends ranked by severity (tag, position, hours outside the band, days in a row, likely cause, suggested check, related WOs, RCFAs and vendor reports) and a watch list of bearings above their fixed vibration alarm limits. Use it for "what is Bonvoy flagging", "what should I look at today" and trend questions; use bonvoy_exceptions for older days.',
    parameters: { type: 'object', properties: { day: date } },
    map: (a) => ({ p_day: a.day ?? null }) },
  // ---- step 05: batched downtime, production, RCFA status and position life (empty for orgs without those feeds) ----
  { name: 'downtime_summary', rpc: 'mm_llm_downtime_summary', maxRows: 120,
    description: 'Downtime totals from the downtime feed, one row per group and kind (planned / unplanned / break / slowdown): events, minutes, hours, share of that kind, MTBF and MTTR. group: area, equipment, cause, crew, grade, month, week or kind. Use this for any "downtime by month / area / cause" or Pareto question; it is exact, unlike adding up BUS text.',
    parameters: { type: 'object', properties: { from: date, to: date, group: { type: 'string', enum: ['area', 'equipment', 'cause', 'crew', 'grade', 'month', 'week', 'kind'] } }, required: ['from', 'to'] },
    map: (a) => ({ p_from: a.from, p_to: a.to, p_group: a.group ?? 'area' }) },
  { name: 'downtime_events', rpc: 'mm_llm_downtime', maxRows: 120,
    description: 'Individual stops from the downtime feed in a date range (start, minutes, kind, equipment, cause, WO, RCFA). kind optional: planned, unplanned, break, slowdown.',
    parameters: { type: 'object', properties: { from: date, to: date, kind: { type: 'string', enum: ['planned', 'unplanned', 'break', 'slowdown'] } }, required: ['from', 'to'] },
    map: (a) => ({ p_from: a.from, p_to: a.to, p_kind: a.kind ?? null }) },
  { name: 'repeat_stops', rpc: 'mm_llm_repeat_stops',
    description: 'Equipment with 2+ unplanned stops in a date range, with hours, causes and the RCFAs raised (rcfas = "none" when nobody analysed it).',
    parameters: { type: 'object', properties: { from: date, to: date, min_events: { type: 'integer', minimum: 2 } }, required: ['from', 'to'] },
    map: (a) => ({ p_from: a.from, p_to: a.to, p_min_events: a.min_events ?? 2 }) },
  { name: 'rcfa_status', rpc: 'mm_llm_rcfa_status',
    description: 'Every RCFA with downtime hours, status and its actions: total, done, overdue, next due.',
    parameters: { type: 'object', properties: { as_of: date } },
    map: (a) => ({ p_as_of: a.as_of ?? null }) },
  { name: 'position_life', rpc: 'mm_llm_position_life', maxRows: 80,
    description: 'Runs of a fabric, felt, refiner plate set or roll position (or all positions when omitted): installed, removed, days vs target, early removals and why. position = a My Machine position id or name.',
    parameters: { type: 'object', properties: { position: { type: 'string' }, as_of: date } },
    map: (a) => ({ p_position: a.position ?? null, p_as_of: a.as_of ?? null }) },
  { name: 'production', rpc: 'mm_llm_production', maxRows: 120,
    description: 'Production by day, week or month: tons, uptime %, sheet breaks, break / unplanned / planned / slowdown minutes, kWh/t, steam t/t.',
    parameters: { type: 'object', properties: { from: date, to: date, by: { type: 'string', enum: ['day', 'week', 'month'] } }, required: ['from', 'to'] },
    map: (a) => ({ p_from: a.from, p_to: a.to, p_by: a.by ?? 'day' }) },
];

// Not a database tool: the model hands over the numbers and the page draws the chart (with a PNG download).
export const CHART: Tool = { name: 'make_chart',
  description: 'Show a chart under the answer. Use it whenever the user asks for a graph, chart, plot or image (PNG): the page draws it from these numbers and offers a PNG download. Pass only numbers the other tools returned. One measure per chart (one unit); up to 4 series of equal length; labels = the x values in order (e.g. months).',
  parameters: { type: 'object', properties: {
    title: { type: 'string' }, type: { type: 'string', enum: ['bar', 'line'] }, unit: { type: 'string', description: 'e.g. min, h, t' },
    labels: { type: 'array', items: { type: 'string' } },
    series: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, values: { type: 'array', items: { type: 'number' } } }, required: ['name', 'values'] } },
    source: { type: 'string', description: 'where the numbers came from, e.g. "downtime_summary by month"' } },
    required: ['title', 'type', 'labels', 'series'] } };
export function checkChart(a: any): { chart?: any; error?: string } {
  const labels = Array.isArray(a?.labels) ? a.labels.slice(0, 60).map(String) : [];
  const series = (Array.isArray(a?.series) ? a.series : []).slice(0, 4).map((x: any) => ({ name: String(x?.name ?? ''), values: (Array.isArray(x?.values) ? x.values : []).slice(0, labels.length).map((v: any) => Number(v)) }));
  if (!labels.length || !series.length) return { error: 'make_chart needs labels and at least one series' };
  if (series.some((x: any) => x.values.length !== labels.length || x.values.some((v: number) => !Number.isFinite(v)))) return { error: 'each series needs one number per label' };
  return { chart: { title: String(a.title ?? '').slice(0, 120), type: a.type === 'line' ? 'line' : 'bar', unit: String(a.unit ?? '').slice(0, 20), labels, series, source: String(a.source ?? '').slice(0, 160) } };
}
export const TOOLS: Tool[] = [...DEFS.map(({ name, description, parameters }) => ({ name, description, parameters })), CHART];

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
