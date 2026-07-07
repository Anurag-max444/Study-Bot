-- RLS (Row Level Security) Supabase me default on hoti hai naye projects me,
-- jo humare server-side inserts/updates ko block kar rahi thi.
-- Ye bot sirf server se hi DB access karta hai (koi public client nahi), isliye safe hai disable karna.

alter table users disable row level security;
alter table syllabus disable row level security;
alter table daily_plan disable row level security;
alter table streaks disable row level security;
