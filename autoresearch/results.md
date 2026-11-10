# Autoresearch results

Ledger: `llm.eval_runs` / `llm.eval_results` (Supabase), per-answer detail in `autoresearch/runs/` (local, not committed).
Answer model Sonnet 5.5 via `mm-llm-ask-dev` v1 (= live `mm-llm-ask`); judge Opus 5.5 `judge-v1.1` via `mm-llm-eval` v3.

## Spend
| Run | What | Cost |
|---|---|---|
| 1 | smoke test (2 questions) | $0.15 |
| 1 | ledger: 4 baseline answers re-run after the judge JSON fix | $0.49 |
| 2 | **baseline, all 54** | **$4.94** (answers $3.88, judge $1.06) |
| 3 | judge v2 check (3 questions) | $0.33 |
| 4 | **baseline v2, all 54** (paused for API credit at 31, then finished; incl. $0.06 re-run overlap in run 1 ledger) | **$5.10** |
| 5 | **round 1, train (36)**: prompt change | **$3.60** |
| | **Total so far** | **$14.68 of $50** |

## Judge v2 (Nov 10, user direction)
Technical answers: wrong or missing citations are penalised heavily; short, fully cited, accurate answers score highest.
- Weights: correct 35%, **cited 35%**, complete 15%, **concise 15%**.
- `mm-llm-ask-dev` v2 checks every `[...]` citation against the full tool output of that run (DOC id + page must have been returned
  or read; WO / RCFA / tag / date / report ids must appear in a tool result). **Any unsupported citation: cited = 0, score capped at 50.**
- Uncited technical claims: cited at most 1-2. Gap questions: must say the library has no source and label general knowledge.
- Concise: about 150 words for knowledge/calc, 220 for data/briefs; padding scores 0-1.
- Question ids hidden from the judge; the runner keeps full responses so answers can be re-judged without paying for them again.
- Check run 3 (3 questions, $0.33): pm02 90 (all 5 citations supported, docked for 323 words), pm04 78.3, sm13 48.3 (contradicted itself on action counts).
- The v1 baseline below is **not comparable** with v2.

## Round 1 — prompt: citations + length (run 5, train only, Nov 10)
Change (`mm-llm-ask-dev` v3, prompt.ts only): cite every number / setting / step / id inline right after it; cite only records,
tags, dates or pages a tool returned; never cite a tool call; label gap answers "The library has no source for this; from general
engineering knowledge"; search and cite the formula before a calculation; lead with the answer, ~150 / ~220 words, no extra sections.

| Train (12 each) | Baseline | Round 1 | Change |
|---|---|---|---|
| Papermaking | 81.1 | 88.1 | +7.0 |
| Industrial / chem eng | 78.7 | 89.8 | +11.1 |
| Sim Mill | 58.5 | 68.5 | +10.0 |
| **All train** | **72.8** | **82.1** | **+9.3** |

By criterion (0-3), baseline → round 1: correct 2.72 → 2.83, **cited 1.97 → 2.61**, complete 2.38 → 2.20, concise 1.28 → 1.58.
25 questions up, 5 level, 6 down. Biggest gains: sm03 +40, ce07 +40, sm10 +38, sm01 +23, ce10 +23 (now looks up and cites the formula).
Cost $3.60; average input tokens unchanged (33k).

Still losing points:
1. **Tool-call citations** still happen despite the rule: sm04 `[outage_scope OUT-2026-11-11]` (-35, capped at 50) and sm09 `[downtime_summary, 2025-11-01 to 2026-10-31]`. Both are the only "fabricated" flags, and both are real queries the model ran.
2. **Still long**: most answers 200-400 words against 150/220.
3. **Sim Mill completeness fell** (1.50 → 1.25): shorter briefs drop the second and third sources (sm01 rotary joint and reel bearing history, sm03 plate sets on hand, sm05 REF 1 comparison).
4. One-run noise not measured; the +9.3 with 25 up / 6 down is very unlikely to be chance (sign test p < 0.001).

Recommendation: **keep** (promote to live after a held-out check).

## Round 0 — baseline, judge v2 (run 4, complete Nov 10)
Paused at 31/54 when the API credit ran out; finished after credit was added (the 23 re-run into run 4).
Score 0-100: correct 35%, cited 35%, complete 15%, concise 15%; any unsupported citation caps at 50.

| Section | Train (12) | Held-out (6) | All (18) |
|---|---|---|---|
| Papermaking | 81.1 | 80.1 | 80.8 |
| Industrial / chem eng | 78.7 | 68.6 | 75.4 |
| Sim Mill | 58.5 | 70.8 | 62.6 |
| **All** | **72.8** | **73.2** | **72.9** |

By criterion (0-3): correct 2.72, **cited 1.91**, complete 2.41, **concise 1.41**. By kind: data 61.1, premise 70.0, gap 73.9, calc 78.6, library 79.0.
Average answer 287 words (target 150 / 220). Run cost $5.10.

### What lost points
1. **Uncited claims** (cited 1.91): one citation at the top or end covering a whole list or table; Sim Mill answers cite few records (sm06, sm10, sm14, sm17: no checkable citations). 7 of 54 answers had no checkable citation at all.
2. **Length** (concise 1.41): 280-500 words with unrequested sections (worked examples, "checks on PM1", watch-outs, background).
3. **Sim Mill briefs miss the second and third sources** (sm01 outage brief 28.3, sm03 REF projection 16.7, sm06 45, sm10 crews 45): wrong lead item, missing scope/parts status, Brightwater, RCFA threshold logic; sm10 used only May-Oct and named the wrong crew.
4. **Calc without lookup** (ce10 60, ce15 60): right number, no tool call, no source.
5. **Two unsupported citations**: sm03 cited a Pi tag it never queried ([Pi PM1:REF_A_SE]); sm09 cited a tool call as a source ([grade_hours 2025-11-01 to 2026-10-31]) — the dates were its query, not in the output. Checker edge case to decide: should citing a query you ran count?
6. Content errors: ce17 (laminar limit 2,000, plug-flow friction direction wrong), sm18 ("nine outages", lists eight).

## Round 0 — baseline, judge v1.1 (Nov 10 2026, superseded)
Score 0-100 (correct 40%, complete 25%, grounded 20%, useful 15%).

| Section | Train (12) | Held-out (6) | All (18) |
|---|---|---|---|
| Papermaking | 87.3 | 79.8 | 84.8 |
| Industrial / chem eng | 88.6 | 91.1 | 89.4 |
| Sim Mill | 73.1 | 84.5 | 76.9 |
| **All** | **83.0** | **85.1** | **83.7** |

By criterion (0-3): correct 2.54, complete 2.56, grounded 2.33, useful 2.59. By kind: calc 90.5, library 86.6, gap 85.3, premise 80.0, data 76.2.
Average answer: 30k input tokens, 10.4 s.

### What lost points
1. **Citations to pages never read** (pm02, pm06, ce05, ce07, ce14): the answer cites a page number or a second document that isn't in its trace. Biggest grounded loss.
2. **Sim Mill multi-source answers stop short** (sm01 outage brief 56.7, sm03 REF projection 45, sm06 repeat failures 50, sm07 bearing chart 50): right core fact, but it skips the second and third sources (Brightwater report, scope status, Danger line, RCFA threshold logic).
3. **Calc questions skip the library** (grounded 1.86): right numbers from memory, no source.
4. **Partial coverage when one tool would do** (sm15 never queried breaks; pm05 didn't read page 2).

### Grader issues found (fix before round 1)
- 4 judge replies weren't valid JSON (fixed in v3, those 4 re-run).
- The judge saw question ids like "pm12" and twice mistook them for a machine name ("says PM1 instead of PM12"). Fix: don't show ids to the judge.
- Re-judging needs the full answer + trace saved locally; the runner should store the whole response.
- Only one baseline pass, so run-to-run noise is not yet known.
