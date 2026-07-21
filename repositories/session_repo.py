"""Session repository — reads and writes to the `task_sessions` table only.

mark_session_completed also triggers revision scheduling (revision_repo) and
streak/badge processing (progress_repo) — this cross-repository
orchestration will move to a services/ layer in a later phase; kept exactly
as it worked before for now."""
from datetime import datetime as _dt, date, timedelta

from database.client import supabase
from repositories.revision_repo import create_revisions_for_topic
from repositories.progress_repo import process_completion


def create_task_session(user_id: int, custom_task_id: int, session_date: str, topic: str, duration_minutes: int):
    """Idempotent — won't duplicate if a session already exists today for this task."""
    existing = (
        supabase.table("task_sessions")
        .select("*")
        .eq("custom_task_id", custom_task_id)
        .eq("session_date", session_date)
        .execute()
    )
    if existing.data:
        return existing.data[0], False  # already existed

    follow_up_due_at = (_dt.now() + timedelta(minutes=duration_minutes)).isoformat()

    res = supabase.table("task_sessions").insert({
        "user_id": user_id, "custom_task_id": custom_task_id, "session_date": session_date,
        "topic_snapshot": topic, "duration_minutes": duration_minutes,
        "follow_up_due_at": follow_up_due_at, "followup_sent": False,
    }).execute()
    return (res.data[0] if res.data else None), True


def mark_session_completed(session_id: int):
    supabase.table("task_sessions").update({
        "completed": True, "completed_at": _dt.now().isoformat(),
    }).eq("id", session_id).execute()

    session = get_session(session_id)
    if not session:
        return False, []
    today_str = _dt.now().strftime("%Y-%m-%d")

    # Sirf /addtask (custom_tasks) se complete hue topics ke liye revision schedule hoti hai.
    create_revisions_for_topic(session["user_id"], today_str, topic_text=session["topic_snapshot"])

    return process_completion(session["user_id"], today_str)


def get_session(session_id: int):
    res = supabase.table("task_sessions").select("*").eq("id", session_id).execute()
    return res.data[0] if res.data else None


def get_due_followups():
    """Sessions whose study duration has elapsed and haven't been followed up on yet."""
    now_iso = _dt.now().isoformat()
    res = (
        supabase.table("task_sessions")
        .select("*, users(*)")
        .eq("followup_sent", False)
        .eq("completed", False)
        .lte("follow_up_due_at", now_iso)
        .execute()
    )
    return res.data


def mark_followup_sent(session_id: int):
    supabase.table("task_sessions").update({"followup_sent": True}).eq("id", session_id).execute()


def get_study_log(user_id: int, days: int = 7):
    """Returns sessions from the last `days` days, most recent first."""
    since = (date.today() - timedelta(days=days)).isoformat()
    res = (
        supabase.table("task_sessions")
        .select("*")
        .eq("user_id", user_id)
        .gte("session_date", since)
        .order("session_date", desc=True)
        .execute()
    )
    return res.data
