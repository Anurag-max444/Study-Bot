-- ============================================================
-- STUDY SYNC — COMPLETE DATABASE SCHEMA (clean, single-file)
-- ============================================================
-- Run this once in the Supabase SQL Editor. Safe to re-run at any time —
-- everything is guarded with IF NOT EXISTS / DO blocks, so re-running
-- won't break or duplicate anything.
-- ============================================================

-- ---- Core: users, syllabus, streaks ----

create table if not exists users (
    id bigint primary key,
    name text,
    language text default 'hinglish',
    exam text,
    daily_hours numeric default 4,
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

create table if not exists streaks (
    user_id bigint primary key references users(id) on delete cascade,
    current_streak int default 0,
    longest_streak int default 0,
    last_active_date date,
    shields_available int default 0,
    shields_used int default 0
);

-- ---- Custom study sessions (/addtask) ----

create table if not exists custom_tasks (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    time text not null,
    topic text not null,
    duration_minutes int not null,
    next_trigger_at timestamp,
    created_at timestamp default now()
);

create table if not exists task_sessions (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    custom_task_id bigint references custom_tasks(id) on delete set null,
    session_date date not null,
    topic_snapshot text not null,
    duration_minutes int not null,
    completed boolean default false,
    completed_at timestamp,
    follow_up_due_at timestamp,
    followup_sent boolean default false,
    created_at timestamp default now(),
    unique (custom_task_id, session_date)
);

-- ---- Gamification: achievement badges ----

create table if not exists user_badges (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    badge_code text not null,
    earned_at timestamp default now(),
    unique (user_id, badge_code)
);

-- ---- Spaced repetition revisions ----

create table if not exists revisions (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    syllabus_id bigint references syllabus(id) on delete cascade,
    topic_text text,
    due_date date not null,
    interval_label text not null,
    notified boolean default false,
    completed boolean default false,
    created_at timestamp default now()
);

-- ---- Cleanup: drop the old reminder system (morning/evening plan, per-topic
-- reminder slots) if it exists from an earlier version of the bot ----

drop table if exists daily_plan;
drop table if exists reminder_slots;
alter table users drop column if exists reminder_time;
alter table users drop column if exists evening_reminder_time;

-- ---- Row Level Security: disabled everywhere, since only the bot's own
-- server accesses this database (no public client-side access) ----

alter table users disable row level security;
alter table syllabus disable row level security;
alter table streaks disable row level security;
alter table custom_tasks disable row level security;
alter table task_sessions disable row level security;
alter table user_badges disable row level security;
alter table revisions disable row level security;

-- ============================================================
-- Done. The database is ready for every feature: onboarding, custom study
-- sessions, gamification, and spaced-repetition revisions.
-- ============================================================

-- ---- Bot state (small key-value store) ----
-- Currently used to remember when the weekly report broadcast last ran
-- successfully, so a missed Sunday (e.g. the host was down) can be caught
-- up automatically on the next startup instead of silently skipping a week.

create table if not exists bot_state (
    key text primary key,
    value text,
    updated_at timestamp default now()
);

alter table bot_state disable row level security;

-- ---- Mock test logging ----
-- Every field the user asked for, stored as entered — no derived/guessed
-- scoring, since negative-marking schemes vary too much across exams to
-- safely auto-calculate a score from raw attempted/wrong/marks numbers.

create table if not exists mock_tests (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    test_date date not null,
    platform text,
    scope text,
    duration_minutes int,
    total_questions int,
    total_marks numeric,
    negative_marking text,
    attempted int,
    wrong int,
    skipped int,
    percentile numeric,
    rank int,
    weak_topics text,
    average_topics text,
    strong_topics text,
    created_at timestamp default now()
);

alter table mock_tests disable row level security;

-- Stores only each image's Telegram file_id, not the image bytes itself —
-- Telegram keeps the actual file, so this survives bot restarts and
-- redeploys on any host without needing persistent disk.

drop table if exists admin_vault;

create table if not exists vault_images (
    id bigserial primary key,
    file_id text not null,
    created_at timestamp default now()
);

alter table vault_images disable row level security;

