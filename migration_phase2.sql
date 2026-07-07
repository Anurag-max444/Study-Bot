-- Ye Supabase SQL Editor me RUN karna (Phase 1 wale schema.sql ke baad)

alter table users add column if not exists evening_reminder_time text default '19:00';

-- Har user ke liye ek din me plan dobara na bane, isliye unique constraint
-- (Postgres me "ADD CONSTRAINT IF NOT EXISTS" valid nahi hai, isliye DO block use kiya)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'unique_user_syllabus_date'
    ) THEN
        ALTER TABLE daily_plan
            ADD CONSTRAINT unique_user_syllabus_date
            UNIQUE (user_id, syllabus_id, plan_date);
    END IF;
END $$;
