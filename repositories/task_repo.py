"""Task repository — reads and writes to the `custom_tasks` table only
(user-defined study sessions created via /addtask)."""
from datetime import datetime, timedelta

from database.client import supabase
from exceptions.database import DatabaseError
from exceptions.validation import ValidationError


def add_custom_task(user_id: int, time_str: str, topic: str, duration_minutes: int):
    now = datetime.now()
    hh, mm = map(int, time_str.split(":"))
    try:
        candidate = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    except ValueError as e:
        # Defense-in-depth: bot.py's handle_task_flow_text already rejects
        # out-of-range times (this is the exact spot Bug 1 used to crash),
        # but this guard means a future caller that skips that check gets a
        # clear error instead of a raw, confusing ValueError.
        raise ValidationError("time", f"'{time_str}' is not a valid HH:MM time") from e
    if candidate <= now:
        candidate += timedelta(days=1)  # time already passed today, schedule for tomorrow

    try:
        res = supabase.table("custom_tasks").insert({
            "user_id": user_id, "time": time_str, "topic": topic, "duration_minutes": duration_minutes,
            "next_trigger_at": candidate.isoformat(),
        }).execute()
    except Exception as e:
        raise DatabaseError("add_custom_task", e) from e
    return res.data[0] if res.data else None


def get_custom_tasks(user_id: int):
    res = (
        supabase.table("custom_tasks")
        .select("*")
        .eq("user_id", user_id)
        .order("time")
        .execute()
    )
    return res.data


def remove_custom_task(user_id: int, time_str: str):
    res = (
        supabase.table("custom_tasks")
        .delete()
        .eq("user_id", user_id)
        .eq("time", time_str)
        .execute()
    )
    return bool(res.data)


def delete_custom_task_by_id(task_id: int):
    supabase.table("custom_tasks").delete().eq("id", task_id).execute()


def get_due_custom_tasks():
    """Catch-up safe: returns tasks whose trigger time has arrived or passed (not exact-minute match)."""
    now_iso = datetime.now().isoformat()
    res = (
        supabase.table("custom_tasks")
        .select("*, users(*)")
        .lte("next_trigger_at", now_iso)
        .execute()
    )
    return res.data
