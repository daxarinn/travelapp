-- Run in Supabase SQL Editor, after 001_planned_time.sql and before deploying v2.4.
-- Existing categories remain unchanged (flight uses flug, other travel uses annað).
-- Departure/check-in date and time use items.planned_date / planned_time.
-- Arrival/check-out and booking information are stored in travel_details.
BEGIN;
ALTER TABLE public.items ADD COLUMN IF NOT EXISTS travel_details jsonb;
COMMENT ON COLUMN public.items.travel_details IS 'Travel booking: kind (flight/transport/stay), from, to, address, company, service, reference, end_date, end_time. Times are local at each location.';
NOTIFY pgrst, 'reload schema';
COMMIT;
