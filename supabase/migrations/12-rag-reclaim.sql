-- Step 12: a worker call killed by the runtime (CPU or wall-clock limit) leaves its job 'running' for ever.
-- mm_rag_claim now also takes back jobs that have been running for more than 5 minutes (the attempt still counts,
-- so a job that keeps dying fails after 3 tries). Safe to run again; also appended to ../llm.sql.
create or replace function public.mm_rag_claim(p_limit int default 3)
returns setof llm.rag_jobs language sql security definer set search_path = '' as $$
  update llm.rag_jobs j set state = 'running', attempts = j.attempts + 1, started_at = now()
  where j.id in (select id from llm.rag_jobs
                 where (state = 'queued' and run_after <= now())
                    or (state = 'running' and started_at < now() - interval '5 minutes' and attempts < 3)
                 order by run_after, id limit least(p_limit, 10) for update skip locked)
  returning j.*;
$$;
revoke execute on function public.mm_rag_claim(int) from public, anon, authenticated;
grant execute on function public.mm_rag_claim(int) to service_role;
