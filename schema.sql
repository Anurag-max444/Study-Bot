-- Ye pura SQL Supabase dashboard > SQL Editor me paste karke RUN kar dena

create table if not exists users (
    id bigint primary key,              -- telegram user id
    name text,
    language text default 'hinglish',   -- 'hindi' / 'english' / 'hinglish'
    exam text,                          -- 'ssc_cgl' / 'jee_mains' / 'custom'
    daily_hours numeric default 4,
    reminder_time text default '07:00', -- HH:MM 24hr format
    onboarding_step text default 'ask_name', -- tracks where user is in setup
    created_at timestamp default now()
);

create table if not exists syllabus (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    subject text not null,
    topic text not null,
    status text default 'pending',      -- pending / in_progress / done
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
