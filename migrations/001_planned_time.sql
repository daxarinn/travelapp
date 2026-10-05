-- Run once in the existing project's Supabase SQL Editor before deploying v2.3.
-- Safe to run again. Existing items, policies and memberships are unchanged.
-- Ideas use the existing nullable planned_date; no new table/status is needed.
BEGIN;
ALTER TABLE public.items ADD COLUMN IF NOT EXISTS planned_time time without time zone;
COMMENT ON COLUMN public.items.planned_time IS 'Optional event time in Europe/Istanbul. A null planned_date denotes an idea.';
NOTIFY pgrst, 'reload schema';
COMMIT;
