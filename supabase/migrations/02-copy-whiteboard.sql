-- Step 2 of 3 (see README.md): copy the Whiteboard into mm_records, tool 'whiteboard'.
-- Run right after the new Whiteboard page is live. Running it again only adds what's missing;
-- it never overwrites a board or item the new page has already saved.
--
-- Record ids follow the other board tools: p:<board> · n:<board>:<note> · l:<board>:<arrow> · f:<board>:<frame>.
-- Board order is kept through a sort key taken from when each board was made.

insert into public.mm_records as r (org_id, tool, id, data, deleted, created_by, created_at, updated_by)
select b.org_id, 'whiteboard', 'p:' || b.id,
       jsonb_build_object('name', b.name, 'meta', '{}'::jsonb, 'created', b.created_at,
                          'sort', (extract(epoch from b.created_at) * 1000)::bigint + b.sort),
       b.deleted, b.created_by, b.created_at, b.updated_by
from public.wb_boards b
on conflict (org_id, tool, id) do nothing;

insert into public.mm_records as r (org_id, tool, id, data, deleted, created_by, updated_by)
select i.org_id, 'whiteboard',
       (case i.kind when 'note' then 'n:' when 'link' then 'l:' else 'f:' end) || i.board_id || ':' || i.id,
       i.data - 'id', i.deleted, i.updated_by, i.updated_by
from public.wb_items i
on conflict (org_id, tool, id) do nothing;

-- Check: the counts per organization should match.
select o.name,
       (select count(*) from public.wb_boards b where b.org_id = o.id and not b.deleted) as old_boards,
       (select count(*) from public.mm_records r where r.org_id = o.id and r.tool = 'whiteboard' and r.id like 'p:%' and not r.deleted) as new_boards,
       (select count(*) from public.wb_items i where i.org_id = o.id and not i.deleted) as old_items,
       (select count(*) from public.mm_records r where r.org_id = o.id and r.tool = 'whiteboard' and r.id not like 'p:%' and not r.deleted) as new_items
from public.orgs o order by o.name;
