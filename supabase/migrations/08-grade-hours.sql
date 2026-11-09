-- Step 08: hours run on each grade, from the production feed (llm.production_daily.grade_hours, "24# 18; 34 Super 6").
-- Lets the assistant compare grades fairly (breaks or downtime per 100 h run, not raw counts). Read-only, only adds.
create or replace function public.mm_llm_grade_hours(p_org uuid, p_from date, p_to date)
returns table (grade text, hours numeric, days int, share_pct numeric)
language sql stable security invoker set search_path = '' as $$
  with parts as (
    select p.day, trim(x) as part
    from llm.production_daily p, unnest(string_to_array(coalesce(p.grade_hours, ''), ';')) as x
    where p.org_id = p_org and p.day between p_from and p_to and trim(x) <> ''
  ), g as (
    select regexp_replace(part, '\s+[0-9.]+$', '') as grade, substring(part from '([0-9.]+)$')::numeric as h, day from parts
  )
  select g.grade, round(sum(g.h), 1), count(distinct g.day)::int, round(100 * sum(g.h) / nullif(sum(sum(g.h)) over (), 0), 1)
  from g group by g.grade order by sum(g.h) desc;
$$;

revoke execute on function public.mm_llm_grade_hours(uuid, date, date) from public;
grant execute on function public.mm_llm_grade_hours(uuid, date, date) to anon, authenticated, service_role;   -- RLS decides what comes back
