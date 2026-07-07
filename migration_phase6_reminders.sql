-- Naya feature: din bhar mein kayi reminders, har ek pe ek naya topic bhejne ke liye

create table if not exists reminder_slots (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    time text not null,          -- HH:MM 24hr format
    created_at timestamp default now()
);

-- Isi bot ke baaki tables ki tarah RLS disable rakh rahe hain
-- (sirf server hi is table ko access karta hai)
alter table reminder_slots disable row level security;
