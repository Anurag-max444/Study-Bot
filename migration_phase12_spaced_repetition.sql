-- Spaced Repetition: jab koi syllabus topic "done" mark hota hai, 4 revision
-- reminders automatically schedule ho jate hai (1/3/7/15 din baad) — forgetting
-- curve ke hisaab se, taaki topic long-term memory me chala jaye.

create table if not exists revisions (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    syllabus_id bigint references syllabus(id) on delete cascade,
    due_date date not null,
    interval_label text not null,   -- '1-day' / '3-day' / '7-day' / '15-day'
    notified boolean default false,
    completed boolean default false,
    created_at timestamp default now()
);

alter table revisions disable row level security;
