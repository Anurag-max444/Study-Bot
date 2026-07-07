-- Naya feature: Streak Shield (miss hue din se streak bachana) + Achievement Badges

alter table streaks add column if not exists shields_available int default 0;
alter table streaks add column if not exists shields_used int default 0;

create table if not exists user_badges (
    id bigserial primary key,
    user_id bigint references users(id) on delete cascade,
    badge_code text not null,
    earned_at timestamp default now(),
    unique (user_id, badge_code)
);

alter table user_badges disable row level security;
