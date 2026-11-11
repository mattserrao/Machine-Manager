# MM LLM — Wiki + Memory Results

Status: **done** (Nov 10 2026). Branch `wiki-memory`, PR #55. Deployed: migration 16, `mm-mcp-dev`, `mm-llm-ask-dev` v8 (v3: memory in prompt, wiki tools; `no_wiki` eval flag). Live `mm-llm-ask` and `mm-mcp` unchanged. Eval spend $44.89 of the $50 cap.

## Where things are
- **Supabase** (live build per org, readable by org members incl. demodemo and serrao.matt): `llm.wiki_pages` / `wiki_links` / `wiki_builds`, `llm.memory`. Sim Mill build 1: 137 pages, 1,947 links. Demodemo RAG build 2: 190 pages, 1,194 links.
- **Repo** `wiki-memory/`: wiki markdown, memory, agent prompts (answer, build, organizer), scripts (`bin/mm`, `judge.py`, `final_run.py`, `upload.py`, `wikigraph.py`), results.
- **Page**: MMLLM.html → "Memory and wiki" tab: results table and the wiki connections graph (circle area = page size; dashed = linked but not written; ring = conflict).

## Results (judge v2, 0–100)
| Run | Papermaking | Chem / industrial | Sim Mill data | New (12) | All |
|---|---|---|---|---|---|
| Training set, no wiki (mean of 2) | 90.5 | 92.0 | 68.5 | — | 83.7 |
| Training set, test agents with wiki + memory (ck1 B) | 91.2 | 81.6 | 75.1 | — | 82.7 |
| Final API, unseen, no wiki | 81.6 | 86.7 | 67.2 | 83.0 | 80.3 |
| Final API, unseen, wiki + memory (v2: memory as a tool) | 89.4 | 90.3 | 54.7 | 78.0 | 78.1 |
| Final API, unseen, v3: memory in the prompt, wiki as a tool (Sim Mill + new only) | — | — | 62.5 | 85.9 | — |

Noise: about ±4 overall, ±10 on Sim Mill.

## Findings
1. The wiki helps knowledge questions on the API (pm +7.8, ce +3.6): topic pages point to the right document page.
2. It hurts Sim Mill data questions on the API (−12.5 held-out, −5 new). The API model called `memory_index` and one wiki page, then made fewer data calls; two answers cited a tool call or an unreturned fact (capped at 50).
3. The test agents (Sonnet subagents over MCP) gained on Sim Mill (+6.6) with the same wiki, because they followed the rules and read the memory topics.

## v3 (done, `mm-llm-ask-dev` v8)
Memory lessons go straight into the system prompt (~5 KB Sim Mill, ~2.4 KB library); memory tools removed; wiki stays a tool with rules that say data questions still need the data tools. Sim Mill held-out 54.7 → 62.5 (no wiki 67.2, within ±10 noise); new set 78.0 → 85.9 (no wiki 83.0). Run cost $2.15; eval spend now $44.89 of $50.

**Recommendation:** v3 is ready to promote to the live `mm-llm-ask` after one papermaking/chem rerun confirms the v2 knowledge gains hold (~$1.50).

## App
MMLLM.html → About → "Memory and wiki": graph of both wikis; click a page, "Read page" shows its text, [[links]] jump to the linked page, Enter in "Find a page" opens the best match. Page text comes from `mm_wiki_page` under RLS: Sim Mill is public; the library wiki needs Demodemo RAG membership (demodemo and serrao.matt both have it). The page is on branch `wiki-memory` (PR #55) until merged.

## Memory (as uploaded)

### sim-mill

#### _index

#### answer-shape
- First sentence = the answer. About 220 words for data questions and briefs, about 150 for knowledge questions. Over ~250 words loses points.
- No unrequested sections (no "also", tips, background, unrequested comparisons). Every number, date, id gets its own inline citation.
- If the question's premise is wrong (wrong date, equipment the machine doesn't have, a limit already crossed), say so first, then answer what is useful.

#### briefs
- Rank by severity and evidence: anything already past a Danger limit or failing now comes before Alert-level items; then items due by life; then routine scope.
- For each item: why (data + vendor finding), its WO and parts status, what is missing (parts, second set, owner), and the decision needed.
- Include items that are due or recommended but NOT in the outage scope.
- A BUS line: one line in the sheet's style with the issue, the number that matters (and its comparison, e.g. vs the other refiner or vs normal), the action, the WO, and the named owner from the records.

#### citations
- A citation passes only if every id-like token in it (tag, date, WO no., report id, RCFA id) appears in a row a tool returned in THIS conversation. One unsupported citation caps the whole answer at 50.
- pi_daily and pi_values rows do NOT contain the tag name, only day/avg/min/max. So a citation like [Pi PM1:TAG 2026-10-31] fails unless the tag also came back in another tool result. For trend numbers, also call bonvoy_exceptions with term=<tag> (its rows carry tag + period) and cite [Bonvoy PM1:TAG <period>] only for days that came back there; otherwise cite the trend without the tag, e.g. "(pi_daily, Oct 1-31)" in words, not in brackets.
- Never cite a date range or a tool call ([downtime_summary ...], [grade_hours ...]); cite record ids or say the numbers come from the tool in plain words.
- [BUS <date>] needs that exact sheet date in a returned row (search_records / position_history rows carry the day). Don't cite a BUS date you inferred.
- downtime_summary and grade_hours rows have no record ids: give their numbers uncited in words ("from the downtime summary"), or cite individual events from downtime_events.
- Vendor report ids (e.g. KV-VR-..., RR-FV-..., MP-FA-...) are citable as [DOC <id> p.N] only after search_documents/search_library/get_document returned them.

#### data-tools
- Owners: BUS issue owners and action owners come back in search_records (owner/assigned_to fields) and overdue_actions. Look them up before saying "no owner".
- Parts readiness for any planned change: outage_scope (parts status) AND open actions / BUS lines about ordering or spares (search_records "order", "set on hand", "spare"). A change can be scoped with parts reserved and still be short of a second set.
- Position life: position_life gives installed date, days vs target; compute when it reaches target and compare with the outage dates in the rules (outages every 42 days). If a due position has no WO in outage_scope, say so.
- Trends: read the whole series before describing it — say when it started rising (flat until X, then rising), not "since <start of window>". Give the fitted rate and the projection, and say it is an extrapolation. Show alarm/Danger limits on charts as reference lines.
- Vendor findings (vibration routes, steam surveys, felt analysis, plate reports) live in search_documents (Sim Mill documents). Check them for every equipment item in a brief; they often hold the recommendation (replace, re-align, change early).
- Repeat failures: repeat_stops shows rcfas="none"; then check search_documents for vendor findings and overdue_actions/search_records for a root-cause review.
- Crews: shift_reports and downtime_summary group=crew give counts; normalise before ranking and say whether the gap is beyond normal variation.

#### wiki
- Start at `wiki index` (Where to start), then `wiki read` the position / equipment / outage / failure-mode page for the question. It lists the related records, ids, vendor reports and which tool returns each.
- The wiki is a map: re-fetch every fact you use with the data/document tools in this conversation and cite those results. Never cite a wiki page. If the wiki and a tool disagree, the tool wins.
- Use the wiki's links to find the 2nd and 3rd sources a question needs (vendor report, open action, outage WO) — that is what most weak answers miss.

### demodemo-rag

#### _index

#### answer-shape
- First sentence = the answer. About 220 words for data questions and briefs, about 150 for knowledge questions. Over ~250 words loses points.
- No unrequested sections (no "also", tips, background, unrequested comparisons). Every number, date, id gets its own inline citation.
- If the question's premise is wrong (wrong date, equipment the machine doesn't have, a limit already crossed), say so first, then answer what is useful.
- Before writing "the library has no source": check the wiki page for the topic (it lists which documents cover it), then run search_library twice more with other terms (synonyms, units, the equipment name). Many misses were a source that existed under different words.
- Answer exactly what was asked, including the distinctions the question implies (cause vs look-alike, range vs single value); state the range when the source gives one.

#### citations
- Cite [DOC <doc_id> p.N] only for a page that came back in search_library or that you read with get_document_page in this conversation. Read the page before quoting a value or procedure step.
- Every specific claim needs its own citation, including the first summary sentence. An uncited lead sentence costs points.
- If the library has no source for the question's core point, start that part with "The library has no source for this; from general engineering knowledge:" and give it uncited. Don't dress general knowledge with citations to loosely related pages.
- Calculations: search for the formula, cite the page it is on, then show the one-line calculation.

#### wiki
- `wiki search <words>` finds the topic page; topic pages list which documents and pages hold each value. Then read those pages with get_document_page and cite them.
- Never cite a wiki page. If the wiki and the document disagree, the document wins.
- When several documents cover a topic, the topic page says where they differ: give both values with their sources only if the question needs it.
