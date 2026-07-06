-- ============================================================
-- STUDY SYNC — COMPLETE DATABASE SETUP (all-in-one, safe to re-run)
-- ============================================================
-- Ye ek hi file poore schema aur saari migrations ko cover karti hai.
-- Naya Supabase project ho ya purana, bas ye pura file ek baar chala do —
-- har cheez "IF NOT EXISTS" / safe-guarded hai, dobara chalane se bhi kuch nahi tootega.
-- ============================================================

-- ---- Phase 1: Core tables ----

create table if not exists users (
    id bigint primary key,
    name text,
    language text default 'hinglish',
    exam text,
    daily_hours numeric default 4,
    reminder_time text default '07:00',
    onboarding_step text default 'ask_name',
    created_at timestamp default now()
);

create table if not exists syllabus (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    subject text not null,
    topic text not null,
    status text default 'pending',
    created_at timestamp default now()
);

create table if not exists daily_plan (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    plan_date date not null,
    syllabus_id bigint references syllabus(id) on delete cascade,
    completed boolean default false,
    created_at timestamp default now()
);

create table if not exists streaks (
    user_id bigint primary key references users(id) on delete cascade,
    current_streak int default 0,
    longest_streak int default 0,
    last_active_date date
);

-- ---- Phase 2: Evening reminder + unique daily_plan constraint ----

alter table users add column if not exists evening_reminder_time text default '19:00';

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

-- ---- Phase 6: Multiple per-task reminder slots ----

create table if not exists reminder_slots (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    time text not null,
    created_at timestamp default now()
);

-- ---- Phase 7: Custom scheduled tasks + study log ----

create table if not exists custom_tasks (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    time text not null,
    topic text not null,
    duration_minutes int not null,
    created_at timestamp default now()
);

create table if not exists task_sessions (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    custom_task_id bigint references custom_tasks(id) on delete cascade,
    session_date date not null,
    topic_snapshot text not null,
    duration_minutes int not null,
    completed boolean default false,
    completed_at timestamp,
    created_at timestamp default now(),
    unique (custom_task_id, session_date)
);

-- ---- Phase 8: Gamification (streak shields + achievement badges) ----

alter table streaks add column if not exists shields_available int default 0;
alter table streaks add column if not exists shields_used int default 0;

create table if not exists user_badges (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    badge_code text not null,
    earned_at timestamp default now(),
    unique (user_id, badge_code)
);

-- ---- Phase 9: Reliable (DB-backed) follow-up reminders ----

alter table task_sessions add column if not exists follow_up_due_at timestamp;
alter table task_sessions add column if not exists followup_sent boolean default false;

-- ---- RLS: sirf server hi in tables ko access karta hai, isliye sabme disable ----

alter table users disable row level security;
alter table syllabus disable row level security;
alter table daily_plan disable row level security;
alter table streaks disable row level security;
alter table reminder_slots disable row level security;
alter table custom_tasks disable row level security;
alter table task_sessions disable row level security;
alter table user_badges disable row level security;

-- ============================================================
-- Ho gaya! Ab bot ke saare features (onboarding, reminders, gamification,
-- custom tasks, badges) ke liye database poora taiyaar hai.
-- ============================================================
