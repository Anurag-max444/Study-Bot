-- Ye Supabase SQL Editor me RUN karna (Phase 1 wale schema.sql ke baad)

alter table users add column if not exists evening_reminder_time text default '19:00';

-- Har user ke liye ek din me plan dobara na bane, isliye unique constraint
alter table daily_plan add constraint if not exists unique_user_syllabus_date
    unique (user_id, syllabus_id, plan_date);
