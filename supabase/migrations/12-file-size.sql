-- Step 12: the mm-files bucket takes files up to 30 MB, the limit the RAG page and llm.rag_settings already use
-- (it was 25 MB, so 25–30 MB PDFs were refused by storage). Safe to run again.
update storage.buckets set file_size_limit = 31457280 where id = 'mm-files';
