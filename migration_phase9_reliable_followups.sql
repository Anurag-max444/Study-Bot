-- Follow-up reminder ab database me track hoga, memory me nahi.
-- Isse agar Render restart/sleep ho jaye bhi, follow-up reminder kabhi miss nahi hoga.

alter table task_sessions add column if not exists follow_up_due_at timestamp;
alter table task_sessions add column if not exists followup_sent boolean default false;
