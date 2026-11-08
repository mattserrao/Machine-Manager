-- Step 07 (Bonvoy), for a project that already has step 06. Run this file, then apply ../llm.sql (the end state: it
-- re-creates every function under its new name and adds the Bonvoy reports table, its functions and the Pi tag links).
-- Safe to run again.

-- Envoy is renamed Bonvoy: the table, its index and its read policies move in place, keeping every row.
do $$ begin
  if to_regclass('llm.envoy') is not null and to_regclass('llm.bonvoy') is null then
    alter table llm.envoy rename to bonvoy;
  end if;
  if to_regclass('llm.envoy_asset_idx') is not null then alter index llm.envoy_asset_idx rename to bonvoy_asset_idx; end if;
end $$;
drop policy if exists envoy_read on llm.bonvoy;
drop policy if exists envoy_public_read on llm.bonvoy;
drop function if exists public.mm_llm_envoy(uuid, text, date, date);

-- Saved tool traces and answers keep the old word in their text; the demo questions are re-asked after the reload.
