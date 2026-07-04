import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_user(user_id: int):
    res = supabase.table("users").select("*").eq("id", user_id).execute()
    return res.data[0] if res.data else None


def create_user(user_id: int):
    supabase.table("users").insert({"id": user_id, "onboarding_step": "ask_language"}).execute()
    return get_user(user_id)


def update_user(user_id: int, **fields):
    supabase.table("users").update(fields).eq("id", user_id).execute()


def add_syllabus_topics(user_id: int, subject: str, topics: list[str]):
    rows = [{"user_id": user_id, "subject": subject, "topic": topic} for topic in topics]
    if rows:
        supabase.table("syllabus").insert(rows).execute()


def get_pending_topics(user_id: int, limit: int = 5):
    res = (
        supabase.table("syllabus")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "pending")
        .limit(limit)
        .execute()
    )
    return res.data


def mark_topic_status(topic_id: int, status: str):
    supabase.table("syllabus").update({"status": status}).eq("id", topic_id).execute()


def get_users_by_morning_time(time_str: str):
    res = (
        supabase.table("users")
        .select("*")
        .eq("reminder_time", time_str)
        .eq("onboarding_step", "done")
        .execute()
    )
    return res.data


def get_users_by_evening_time(time_str: str):
    res = (
        supabase.table("users")
        .select("*")
        .eq("evening_reminder_time", time_str)
        .eq("onboarding_step", "done")
        .execute()
    )
    return res.data


def create_today_plan(user_id: int, today_str: str, num_topics: int = 4):
    existing = (
        supabase.table("daily_plan")
        .select("*, syllabus(*)")
        .eq("user_id", user_id)
        .eq("plan_date", today_str)
        .execute()
    )
    if existing.data:
        return existing.data

    topics = get_pending_topics(user_id, limit=num_topics)
    if not topics:
        return []

    rows = [
        {"user_id": user_id, "plan_date": today_str, "syllabus_id": topic["id"]}
        for topic in topics
    ]
    supabase.table("daily_plan").insert(rows).execute()

    result = (
        supabase.table("daily_plan")
        .select("*, syllabus(*)")
        .eq("user_id", user_id)
        .eq("plan_date", today_str)
        .execute()
    )
    return result.data


def get_today_plan(user_id: int, today_str: str):
    res = (
        supabase.table("daily_plan")
        .select("*, syllabus(*)")
        .eq("user_id", user_id)
        .eq("plan_date", today_str)
        .execute()
    )
    return res.data


def get_streak(user_id: int):
    res = supabase.table("streaks").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None


def update_streak_on_completion(user_id: int, today_str: str):
    """Call this when user marks at least one topic done today."""
    from datetime import date, timedelta

    streak = get_streak(user_id)
    today = date.fromisoformat(today_str)
    yesterday_str = (today - timedelta(days=1)).isoformat()

    if not streak:
        supabase.table("streaks").insert({
            "user_id": user_id, "current_streak": 1,
            "longest_streak": 1, "last_active_date": today_str,
        }).execute()
        return

    if streak["last_active_date"] == today_str:
        return  # already counted today

    if streak["last_active_date"] == yesterday_str:
        new_current = streak["current_streak"] + 1
    else:
        new_current = 1  # streak broken, restart

    new_longest = max(new_current, streak["longest_streak"])
    supabase.table("streaks").update({
        "current_streak": new_current,
        "longest_streak": new_longest,
        "last_active_date": today_str,
    }).eq("user_id", user_id).execute()


def get_progress_stats(user_id: int):
    """Returns subject-wise done/total counts."""
    res = supabase.table("syllabus").select("subject, status").eq("user_id", user_id).execute()
    stats = {}
    for row in res.data:
        subj = row["subject"]
        stats.setdefault(subj, {"done": 0, "total": 0})
        stats[subj]["total"] += 1
        if row["status"] == "done":
            stats[subj]["done"] += 1
    return stats


def toggle_plan_item(plan_id: int, completed: bool, today_str: str = None):
    supabase.table("daily_plan").update({"completed": completed}).eq("id", plan_id).execute()
    if completed:
        plan = supabase.table("daily_plan").select("syllabus_id, user_id").eq("id", plan_id).execute()
        if plan.data:
            mark_topic_status(plan.data[0]["syllabus_id"], "done")
            if today_str:
                update_streak_on_completion(plan.data[0]["user_id"], today_str)


# ---- Per-task reminder slots (multiple reminders/day, one topic each) ----

def add_reminder_slot(user_id: int, time_str: str):
    supabase.table("reminder_slots").insert({"user_id": user_id, "time": time_str}).execute()


def remove_reminder_slot(user_id: int, time_str: str):
    res = (
        supabase.table("reminder_slots")
        .delete()
        .eq("user_id", user_id)
        .eq("time", time_str)
        .execute()
    )
    return bool(res.data)


def get_reminder_slots(user_id: int):
    res = (
        supabase.table("reminder_slots")
        .select("*")
        .eq("user_id", user_id)
        .order("time")
        .execute()
    )
    return res.data


def get_users_with_slot_at(time_str: str):
    res = (
        supabase.table("reminder_slots")
        .select("*, users(*)")
        .eq("time", time_str)
        .execute()
    )
    return res.data


def get_or_create_next_task(user_id: int, today_str: str):
    """Picks ONE pending topic not already assigned today, adds it to daily_plan, returns it joined."""
    existing = get_today_plan(user_id, today_str)
    used_syllabus_ids = {e["syllabus_id"] for e in existing}

    pending = (
        supabase.table("syllabus")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "pending")
        .execute()
    ).data

    next_topic = next((topic for topic in pending if topic["id"] not in used_syllabus_ids), None)
    if not next_topic:
        return None

    inserted = (
        supabase.table("daily_plan")
        .insert({"user_id": user_id, "plan_date": today_str, "syllabus_id": next_topic["id"]})
        .execute()
    )
    if not inserted.data:
        return None

    new_id = inserted.data[0]["id"]
    result = (
        supabase.table("daily_plan")
        .select("*, syllabus(*)")
        .eq("id", new_id)
        .execute()
    )
    return result.data[0] if result.data else None
