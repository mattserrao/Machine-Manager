-- Step 3 of 3 (see README.md): remove the old Whiteboard tables once step 2's copy looks right.
-- This deletes the old copy of the data and can't be undone.

do $$ begin
  if exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'wb_items') then
    alter publication supabase_realtime drop table public.wb_items;
  end if;
  if exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'wb_boards') then
    alter publication supabase_realtime drop table public.wb_boards;
  end if;
end $$;

drop function if exists public.wb_apply(jsonb);
drop table if exists public.wb_items;
drop table if exists public.wb_boards;
drop function if exists public.wb_touch();
drop function if exists public.wb_item_org();

drop policy if exists wb_files_read   on storage.objects;
drop policy if exists wb_files_insert on storage.objects;
drop policy if exists wb_files_update on storage.objects;
-- Then delete the empty wb-files bucket under Storage in the dashboard.
