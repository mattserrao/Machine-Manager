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
| 4 | baseline v2 — **partial**: 31 of 54 scored, then the Anthropic API credit ran out | $2.61 |
| | **Total so far** | **$8.52 of $50** |

## Judge v2 (Nov 10, user direction)
Technical answers: wrong or missing citations are penalised heavily; short, fully cited, accurate answers score highest.
- Weights: correct 35%, **cited 35%**, complete 15%, **concise 15%**.
- `mm-llm-ask-dev` v2 checks every `[...]` citation against the full tool output of that run (DOC id + page must have been returned
  or read; WO / RCFA / tag / date / report ids must appear in a tool result). **Any unsupported citation: cited = 0, score capped at 50.**
- Uncited technical claims: cited at most 1-2. Gap questions: must say the library has no source and label general knowledge.
- Concise: about 150 words for knowledge/calc, 220 for data/briefs; padding scores 0-1.
- Question ids hidden from the judge; the runner keeps full responses so answers can be re-judged without paying for them again.
- Check run 3 (3 questions, $0.33): pm02 90 (all 5 citations supported, docked for 323 words), pm04 78.3, sm13 48.3 (contradicted itself on action counts).
- The v1 baseline below is **not comparable**; a v2 baseline is next.

## Round 0 — baseline, judge v2 (run 4, PARTIAL)
Stopped at 12:40 Nov 10: "credit balance is too low" on the Anthropic API. Papermaking and chem eng are complete except
ce13 and ce15-18; **no Sim Mill questions scored yet**. The 23 unscored rows have score = null.
Finish after credit is added: fresh tokens, then `eval_run.py --round 0 --label baseline-v2 --run-id 4 --only sm01 ... sm18 ce13 ce15 ce16 ce17 ce18` (~$2.5).

| Section | Train | Held-out | All | n |
|---|---|---|---|---|
| Papermaking | 81.1 | 80.1 | 80.8 | 18 |
| Industrial / chem eng | 78.7 | 90.0 (1 q) | 79.6 | 13 |
| **Scored so far** | | | **80.3** | 31 |

By criterion (0-3): **correct 2.90, cited 2.29, complete 2.72, concise 1.23**.
- **No fabricated citations**: every checked citation in the 31 answers was supported by the tool output. The v1 judge's "never retrieved" flags were mostly its 700-character preview limit.
- **Length is now the biggest loss**: answers run 280-500 words against 150; unrequested sections (worked examples, "checks on PM1", caveats).
- **Uncited sub-claims**: one citation up top covering a whole list; extra advice with no source.
- **Calc without lookup**: ce10 called no tools, so no citation (60).
- Content misses: ce07 (scoops; condensate moving with the shell), pm15 (starch / calender sizing), pm17 (pumping and viscous shear).

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
