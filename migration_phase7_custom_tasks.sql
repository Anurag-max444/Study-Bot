-- Naya feature: khud ka topic + time + duration set karo, bot padhna shuru/khatam karne ka reminder dega
-- aur ek study log rakhega (kitna padha, kab padha)

create table if not exists custom_tasks (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    time text not null,              -- HH:MM 24hr format, jab study start karna hai
    topic text not null,             -- khud likha hua topic naam
    duration_minutes int not null,   -- kitni der padhna hai
    created_at timestamp default now()
);

create table if not exists task_sessions (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    custom_task_id bigint references custom_tasks(id) on delete cascade,
    session_date date not null,
    topic_snapshot text not null,     -- topic naam is din ke liye (agar baad me task edit ho jaye)
    duration_minutes int not null,
    completed boolean default false,
    completed_at timestamp,
    created_at timestamp default now(),
    unique (custom_task_id, session_date)  -- ek din me ek task ka ek hi session
);

alter table custom_tasks disable row level security;
alter table task_sessions disable row level security;
