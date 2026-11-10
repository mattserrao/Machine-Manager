-- 14: Autoresearch eval records (branch autoresearch). Service role only; the results page reads through
-- mm_eval_summary (public, read-only aggregates, no answers or traces).
create table if not exists llm.eval_runs (
  id            bigint generated always as identity primary key,
  round         int not null,                 -- 0 = baseline
  label         text not null,
  change        text,                         -- what this round changed
  git_sha       text,
  split         text not null,                -- train | heldout | all
  answer_model  text,
  judge_model   text,
  kept          boolean,                      -- keep / revert decision, set after review
  status        text not null default 'running',
  cost_usd      numeric(10,4) not null default 0,
  started_at    timestamptz not null default now(),
  finished_at   timestamptz
);
create table if not exists llm.eval_results (
  id            bigint generated always as identity primary key,
  run_id        bigint not null references llm.eval_runs(id) on delete cascade,
  question_id   text not null,
  section       text not null,
  split         text not null,
  kind          text,
  score         numeric(5,1),                 -- 0-100
  criteria      jsonb,                        -- {correct, complete, grounded, useful} 0-3
  must_hits     jsonb,                        -- [true,false,...] per must point
  judge_notes   text,
  answer        text,
  status        text,
  trace         jsonb,
  in_tokens     int, out_tokens int, cache_read int, cache_write int,
  judge_in      int, judge_out int,
  answer_cost   numeric(10,4), judge_cost numeric(10,4),
  ms            int,
  created_at    timestamptz not null default now(),
  unique (run_id, question_id)
);
alter table llm.eval_runs enable row level security;
alter table llm.eval_results enable row level security;

create or replace function public.mm_eval_spent() returns numeric
language sql stable security definer set search_path = '' as $$
  select coalesce(sum(coalesce(answer_cost,0) + coalesce(judge_cost,0)), 0) from llm.eval_results $$;

create or replace function public.mm_eval_start(p_round int, p_label text, p_change text, p_sha text, p_split text,
  p_answer_model text, p_judge_model text) returns bigint
language sql security definer set search_path = '' as $$
  insert into llm.eval_runs (round, label, change, git_sha, split, answer_model, judge_model)
  values (p_round, p_label, p_change, p_sha, p_split, p_answer_model, p_judge_model) returning id $$;

create or replace function public.mm_eval_save(p jsonb) returns void
language sql security definer set search_path = '' as $$
  insert into llm.eval_results (run_id, question_id, section, split, kind, score, criteria, must_hits, judge_notes, answer, status,
    trace, in_tokens, out_tokens, cache_read, cache_write, judge_in, judge_out, answer_cost, judge_cost, ms)
  values ((p->>'run_id')::bigint, p->>'question_id', p->>'section', p->>'split', p->>'kind', (p->>'score')::numeric,
    p->'criteria', p->'must_hits', p->>'judge_notes', p->>'answer', p->>'status', p->'trace',
    (p->>'in_tokens')::int, (p->>'out_tokens')::int, (p->>'cache_read')::int, (p->>'cache_write')::int,
    (p->>'judge_in')::int, (p->>'judge_out')::int, (p->>'answer_cost')::numeric, (p->>'judge_cost')::numeric, (p->>'ms')::int)
  on conflict (run_id, question_id) do update set score = excluded.score, criteria = excluded.criteria, must_hits = excluded.must_hits,
    judge_notes = excluded.judge_notes, answer = excluded.answer, status = excluded.status, trace = excluded.trace,
    in_tokens = excluded.in_tokens, out_tokens = excluded.out_tokens, cache_read = excluded.cache_read, cache_write = excluded.cache_write,
    judge_in = excluded.judge_in, judge_out = excluded.judge_out, answer_cost = excluded.answer_cost, judge_cost = excluded.judge_cost, ms = excluded.ms $$;

create or replace function public.mm_eval_finish(p_run bigint) returns void
language sql security definer set search_path = '' as $$
  update llm.eval_runs r set status = 'done', finished_at = now(),
    cost_usd = (select coalesce(sum(coalesce(answer_cost,0) + coalesce(judge_cost,0)), 0) from llm.eval_results where run_id = p_run)
  where r.id = p_run $$;

-- read-only aggregates for the results page
create or replace function public.mm_eval_summary() returns jsonb
language sql stable security definer set search_path = '' as $$
  select coalesce(jsonb_agg(x order by x->>'round', x->>'id'), '[]'::jsonb) from (
    select jsonb_build_object('id', r.id, 'round', r.round, 'label', r.label, 'change', r.change, 'split', r.split, 'kept', r.kept,
      'cost', r.cost_usd, 'started', r.started_at, 'n', count(e.*), 'score', round(avg(e.score), 1),
      'by_section', (select jsonb_object_agg(k, v) from (select section || '/' || split k, round(avg(score), 1) v
                      from llm.eval_results where run_id = r.id group by 1) s)) x
    from llm.eval_runs r left join llm.eval_results e on e.run_id = r.id group by r.id) t $$;

revoke execute on function public.mm_eval_spent(), public.mm_eval_start(int, text, text, text, text, text, text),
  public.mm_eval_save(jsonb), public.mm_eval_finish(bigint) from public, anon, authenticated;
grant execute on function public.mm_eval_spent(), public.mm_eval_start(int, text, text, text, text, text, text),
  public.mm_eval_save(jsonb), public.mm_eval_finish(bigint) to service_role;
grant execute on function public.mm_eval_summary() to anon, authenticated;
