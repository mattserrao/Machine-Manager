// Playbooks: how a superintendent works a kind of question, as a checklist of sources to pull before answering.
// The model calls get_playbook(kind) and runs every step. They are general to the job, not written from any test question:
// no asset, vendor, date or finding from the answer keys appears here.
import type { Tool } from './adapter.ts';

export const PLAYBOOKS: Record<string, { use: string; steps: string[]; answer: string }> = {
  outage_brief: {
    use: 'What to prioritise or prepare for an outage.',
    steps: [
      'outage_scope for the outage: every WO with its status and parts status. Note any WO whose parts are not reserved or on order.',
      'bonvoy_report (latest) and bonvoy_exceptions since the last outage: which assets are flagged or above an alarm or Danger limit, and since when. Check whether each one has a WO in the scope.',
      'position_life (all positions): fabrics, felts, plate sets and rolls at or past target life by the outage date, and any running short of target.',
      'repeat_stops over the last 12 months: recurring failures, and whether the outage scope addresses them.',
      'search_documents for vendor reports from the last 90 days (vibration routes, clothing surveys, plate reports, roll service, audits): recommendations for this outage.',
      'overdue_actions and rcfa_status: open actions tied to scope items or flagged assets.',
      'search_records for spares on hand for the big jobs (plates, felts, bearings): what is in stores and what is still on order.',
    ],
    answer: 'A ranked list. Rank by risk of failing before the next outage first (alarm-level trends, confirmed defects, work already deferred once), then wear items due, then vendor recommendations, then housekeeping. Each item: why, the evidence with citations, and what is missing (parts, spares, owner).',
  },
  why_event: {
    use: 'Why something happened or was changed (a felt pulled early, a break, a failure).',
    steps: [
      'position_history for the asset around the date: BUS issues, WOs, actions, RCFAs, Bonvoy flags, documents.',
      'pi_daily on the asset\'s process tags for the weeks before and after: when did it start drifting, and by how much?',
      'bonvoy_exceptions for the asset: the first day it was flagged.',
      'shift_reports in the weeks before: what the crews saw and wrote.',
      'search_documents for vendor reports on the asset near the date (surveys, post-mortems, lab results).',
      'position_life if it is a fabric, felt, plate set or roll: days run against target, removal reason.',
    ],
    answer: 'The cause first, then a short timeline (first sign, first flag, action taken, result) with a citation on each step, then what it cost (days short, downtime, speed or tons).',
  },
  trend_projection: {
    use: 'A trend over time, comparing two assets\' trends, or where a value will be by a date.',
    steps: [
      'pi_daily on the tag over the window asked (and the matching tag on any sister asset to compare).',
      'Find when the trend changed (an outage, a plate or felt change, an event) with position_life or position_history, and fit the rate on the current segment only.',
      'Check the limit that matters (alarm, Danger, target) and whether it is already crossed.',
      'Check what is planned for it: outage_scope WO and parts status, spares on hand (search_records), the vendor\'s view (search_documents).',
    ],
    answer: 'The value now and the comparison, the fitted rate, the projected value and date (said to be an extrapolation), and what is planned or missing to deal with it. Chart it if asked: both series, the limit as a line, events as marks, the projection dashed.',
  },
  compare_groups: {
    use: 'Comparing grades, crews, months, felts or shifts (who or what is worse).',
    steps: [
      'Use the whole period in the data unless a period is asked for.',
      'Get counts with downtime_summary or production grouped by the thing compared.',
      'Normalise: grade_hours for per-100-hours-run rates by grade; crews on a rotation work equal hours, so say so; per day or per ton for months.',
      'Judge the gap: compare it with what chance would give (a simple Poisson or proportion test is enough) before calling it real.',
    ],
    answer: 'Counts and normalised rates for every group, which leads, whether the gap is bigger than chance, and one line on what would explain it. No blame on counts alone.',
  },
  repeat_failures: {
    use: 'Repeat failures, recurring stops, or which failures lack an RCFA.',
    steps: [
      'repeat_stops over the last 12 months (min_events 2): equipment, count, hours, causes, RCFAs raised.',
      'rcfa_status: the RCFA trigger used at this mill (downtime threshold) and which events stayed under it; say why none was raised (each stop short, stops far apart).',
      'bonvoy_exceptions and pi_daily on the asset before each failure: was there a warning sign?',
      'search_documents for vendor reports or recommendations on the asset.',
    ],
    answer: 'Each repeat failure with dates, total hours and why no RCFA was triggered, any precursor seen, and the vendor\'s recommendation, each cited.',
  },
  write_update: {
    use: 'Writing a BUS line, email, handover or brief for someone.',
    steps: [
      'search_records for the current BUS item, WO or action on the subject: its wording, current owner and status.',
      'pi_daily or the relevant summary tool for the latest numbers, and the comparison that shows the problem (a sister asset, a target).',
      'search_documents for the latest vendor finding or suspected cause.',
      'outage_scope or search_records for parts and timing of the fix.',
    ],
    answer: 'In the requested format, with the real names, numbers, WOs and dates. Name the current owner from the records, and say who you would assign if it should change.',
  },
  totals_ranking: {
    use: 'What cost the most, totals by month or area, OME or production comparisons.',
    steps: [
      'Pick the exact window asked (dates inclusive).',
      'downtime_summary grouped by cause, area or equipment; production or efficiency by month for tons, breaks and OME.',
      'Report every metric the question names, plus breaks and tons when comparing production periods.',
      'downtime_events for the top item if a cause needs explaining.',
    ],
    answer: 'A ranked list or per-period figures with the number of events and hours (or tons, breaks, OME) for each, cited, then one line on what drove the top item.',
  },
  position_life: {
    use: 'How long fabrics, felts, plates or rolls ran, or where the current one is.',
    steps: [
      'position_life for the position: every run with installed, removed, days and target.',
      'Today\'s date from the context: days on the current one and days left to target.',
      'position_history for early removals: why.',
    ],
    answer: 'Each run with dates and days against target, the current one\'s age and days to target, and the reason for any early removal.',
  },
  premise_check: {
    use: 'A question that assumes an event, a piece of equipment or a limit that may not exist or may already have been passed.',
    steps: [
      'Check the assumption against the context (positions, outages) and position_history or the relevant data tool.',
      'If it is false, find the nearest real thing the person may mean.',
    ],
    answer: 'Say plainly that the premise does not hold and why, with a citation, then give the nearest useful facts.',
  },
};

export const PLAYBOOK_TOOL: Tool = { name: 'get_playbook',
  description: 'The checklist for a kind of data question: which tools to call and what the answer must cover. Call it first for: outage_brief, why_event, trend_projection, compare_groups, repeat_failures, write_update, totals_ranking, position_life, premise_check.',
  parameters: { type: 'object', properties: { kind: { type: 'string', enum: Object.keys(PLAYBOOKS) } }, required: ['kind'] } };

export function getPlaybook(kind: string) {
  const p = PLAYBOOKS[kind];
  if (!p) return { error: `unknown kind; use one of: ${Object.keys(PLAYBOOKS).join(', ')}` };
  return { kind, use: p.use, steps: p.steps.map((s, i) => `${i + 1}. ${s}`), answer: p.answer,
    note: 'Run every step before answering. A step that finds nothing relevant needs no mention. Cite the records each step returns, not this playbook.' };
}
