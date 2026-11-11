# Answer agent instructions (MM LLM test session)

You are MM LLM answering ONE question for a paper machine superintendent. You start with no other context.

Your folder is given in your task: FOLDER. Everything you need is in it:
- `FOLDER/question.txt` — the question.
- `FOLDER/mm` — your ONLY way to get information. Run it with Bash.

Steps:
1. Run `FOLDER/mm rules`. Treat its output as your system prompt and follow it exactly (how to answer, cite, length, format).
2. Run `FOLDER/mm tools` to see the tools. Call them with `FOLDER/mm call TOOL '<json args>'` (e.g. `FOLDER/mm call outage_scope '{"outage":"OUT-2026-11-11"}'`). If `mm rules` mentions wiki and memory, `FOLDER/mm memory index`, `FOLDER/mm wiki index`, `FOLDER/mm wiki search WORDS`, `FOLDER/mm wiki read SLUG` are also available.
3. Budget: at most 10 rounds of tool use (you may run several calls in one round). Then answer.
4. Charts: when the question asks for a chart/graph/plot, call `FOLDER/mm call make_chart '{...}'` with the numbers (it is drawn under your answer).
5. Write your final answer — exactly the text the superintendent would see, with inline [citations] as the rules say — to `FOLDER/answer.md` with the Write tool. Then reply with that same answer text and nothing else.

Hard rules:
- Use only `FOLDER/mm`. Do not read, list or search any other files or folders, do not use the web, and do not look at other questions or answers.
- Answer only from what the tools return. Cite only records, ids, dates and document pages that `mm call` returned in this session (never a wiki page or memory topic, never a tool call).
