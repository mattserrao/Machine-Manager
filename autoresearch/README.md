# MM LLM — Autoresearch (self-improvement loop)

Status: **baseline done** (Nov 10 2026), $5.58 of $50 spent. Branch `autoresearch`. Live: migration 14 (eval tables), `mm-llm-ask-dev` v1, `mm-llm-eval` v3. Sim Mill weekly roll paused. Results: `results.md`.

## Goal
Make MM LLM answer better, measurably, by improving tools, the RAG library, a memory file and the harness one change at a time. Every change is scored the same way, and the results are charted at the end.

## Decisions so far
| Topic | Decision |
|---|---|
| Who runs what | Hybrid: scripts answer and grade; the user + Claude make the improvements |
| Answer model | Sonnet 5.5 (`claude-sonnet-5-5`), through the API |
| Judge | Scripted Opus 5.5 judge with a fixed rubric, plus the deterministic checks |
| Questions | 3 sections × 18 = 54 (12 train + 6 held-out each): papermaking, industrial/chem eng, Sim Mill |
| Budget | **$50 total, hard cap**, enforced in the judge function |

## The loop
```
 ┌────────────────────────────────────────────────────────────────────────────────┐
 │ 1. Improve (one change)  Claude Code on the autoresearch branch / you on the RAG page │
 │ 2. Deploy to mm-llm-ask-dev      (live mm-llm-ask and the demo page untouched)       │
 │ 3. eval_run.py --split train     Sonnet answers 36 train questions                   │
 │ 4. mm-llm-eval judges            Opus scores each answer, writes llm.eval_results    │
 │ 5. Keep or revert                keep only if the train score beats the noise band    │
 │ 6. Every 3rd round + final       also run the 18 held-out questions                  │
 └────────────────────────────────────────────────────────────────────────────────┘
```

## What each improvement lever means in practice
**Tools.** Written in Claude Code on this branch: a SQL function (migration) and its entry in a shared `_shared/tools.ts`, which both `mm-llm-ask-dev` and `mm-mcp` read (Harness Review H10). New tools first go to the dev function only. You can try them in Claude desktop through the MM MCP connector before a scored round. Candidates come from the Harness Review: `resolve`, `analyze`, `compare_runs`, charts by reference.

**RAG.** You choose and upload real documents (vendor manuals, TAPPI TIPs, textbook sections) to **Demodemo RAG** through the RAG page or the bulk loader. Claude's part: after each round, a *gap report* lists questions that failed for lack of a source, the topic to look for, and whether a passage was missed even though it exists (a retrieval problem, not a library problem). Rules: only real documents, never notes written to answer a test question; no uploads aimed at held-out questions (you won't see them, the report only covers train).

**Memory file.** One org memory doc (`llm.memory`, or a markdown file to start) whose index goes into the system prompt: glossary, how this mill names things, answer-format preferences. Claude proposes edits; you approve each one. Never facts copied from the answer keys.

**Harness.** Harness Review items: prompt caching (H1), parallel tools (H2), retries (H3), error hints (H6), row-safe truncation (H7), thinking for Opus (H8), per-step trace (H9), step budget by type (H11), router/checker later.

## Grading
Per answer, the judge gets: question, key (`must` points, `nice` points, sources, tolerance), the answer, and the tool trace (tool, args, row counts, doc ids/pages read). Scores 0-3 each:

| Criterion | Weight | 3 means |
|---|---|---|
| Correct | 40% | every claim matches the key / data; numbers within tolerance |
| Complete | 25% | all `must` points |
| Grounded | 20% | claims trace to tool results; library questions cite a real [DOC id p.] that was read |
| Useful | 15% | leads with the answer, right format, premise checked, brief |

Score = weighted mean scaled to 0-100. Also recorded: the existing deterministic chart/regex checks for Sim Mill, pass/fail per `must` point, tokens, cache reads, latency, cost. The judge model and prompt are pinned; changing either restarts the baseline.

## Records
`llm.eval_runs` (round, label, git sha, change description, kept?, models, cost) and `llm.eval_results` (per question: score, criteria, must hits, judge notes, answer, trace, tokens, cost). A results page (`Evals.html`, or a dashboard artifact) charts score by round, split by section and train/held-out, with cost per round.

## Cost (from real `llm.answers`: Sonnet averages ~42k in / 1.7k out per answer)
| Item | Each | Train round (36) | Full round (54) |
|---|---|---|---|
| Sonnet answer | ~$0.10 (Sim Mill), ~$0.05 (knowledge) | ~$2.5 | ~$4 |
| Opus judge | ~$0.05 | ~$1.8 | ~$2.7 |
| **Total** | | **~$4.3** | **~$6.7** |

Plan within $50: baseline full + a second train pass for noise (~$11), ~6 train rounds (~$26), a full round at rounds 3 and final (~$13). Prompt caching (likely round 1) should cut answer cost by about half and buy more rounds.

## Files
- `build_questions.py` → `questions.json` (54 questions with keys).
- To build after approval: `supabase/migrations/14-evals.sql`, `supabase/functions/mm-llm-eval/`, `mm-llm-ask-dev` (eval mode: no save to `llm.answers`, returns usage), `autoresearch/eval_run.py`, `Evals.html`.
