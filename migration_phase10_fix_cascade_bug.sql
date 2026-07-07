-- BUG FIX: task_sessions ka custom_task_id column "ON DELETE CASCADE" tha,
-- isliye jab hum ek-baar-chalne-wale custom_task ko turant delete karte the
-- (one-time design ke liye), wahi task_session row bhi automatically delete
-- ho jati thi -- follow-up ("kya poora kiya?") kabhi milta hi nahi tha.
--
-- Fix: FK ko "ON DELETE SET NULL" kar diya, taaki custom_task delete hone par
-- session apni jagah surakshit rahe (bas custom_task_id NULL ho jayega, baaki
-- sab data -- topic, duration, completed status -- waisa hi rahega).

DO $$
DECLARE
    con_name text;
BEGIN
    SELECT conname INTO con_name
    FROM pg_constraint
    WHERE conrelid = 'task_sessions'::regclass
      AND confrelid = 'custom_tasks'::regclass
      AND contype = 'f';

    IF con_name IS NOT NULL THEN
        EXECUTE format('ALTER TABLE task_sessions DROP CONSTRAINT %I', con_name);
    END IF;
END $$;

ALTER TABLE task_sessions ALTER COLUMN custom_task_id DROP NOT NULL;

ALTER TABLE task_sessions
    ADD CONSTRAINT task_sessions_custom_task_id_fkey
    FOREIGN KEY (custom_task_id) REFERENCES custom_tasks(id) ON DELETE SET NULL;
