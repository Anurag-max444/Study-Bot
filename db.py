import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

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


def update_streak_on_completion(user_id: int, today_str: str) -> bool:
    """Call this when user marks at least one topic done today. Returns True if a shield was consumed."""
    from datetime import date, timedelta

    streak = get_streak(user_id)
    today = date.fromisoformat(today_str)
    yesterday_str = (today - timedelta(days=1)).isoformat()
    two_days_ago_str = (today - timedelta(days=2)).isoformat()

    if not streak:
        supabase.table("streaks").insert({
            "user_id": user_id, "current_streak": 1, "longest_streak": 1,
            "last_active_date": today_str, "shields_available": 0, "shields_used": 0,
        }).execute()
        return False

    if streak["last_active_date"] == today_str:
        return False  # already counted today

    shield_used = False
    shields_available = streak.get("shields_available") or 0

    if streak["last_active_date"] == yesterday_str:
        new_current = streak["current_streak"] + 1
    elif streak["last_active_date"] == two_days_ago_str and shields_available > 0:
        # Missed exactly one day, but a shield covers it — streak survives.
        new_current = streak["current_streak"] + 1
        shield_used = True
    else:
        new_current = 1  # streak broken, restart

    new_longest = max(new_current, streak["longest_streak"])
    updates = {
        "current_streak": new_current,
        "longest_streak": new_longest,
        "last_active_date": today_str,
    }

    if shield_used:
        updates["shields_available"] = shields_available - 1
        updates["shields_used"] = (streak.get("shields_used") or 0) + 1

    # Earn a fresh shield every 7-day streak milestone (capped at 3 so it stays meaningful)
    if new_current % 7 == 0:
        current_shields = updates.get("shields_available", shields_available)
        updates["shields_available"] = min(current_shields + 1, 3)

    supabase.table("streaks").update(updates).eq("user_id", user_id).execute()
    return shield_used


def process_completion(user_id: int, today_str: str):
    """Runs after ANY completion event: updates streak/shields, checks for new badges."""
    shield_used = update_streak_on_completion(user_id, today_str)
    newly_awarded_badges = check_and_award_badges(user_id)
    return shield_used, newly_awarded_badges


# ---- Achievement badges ----

BADGES = {
    "streak_7": {"name": "🔥 Week Warrior", "condition": lambda s: s["current_streak"] >= 7},
    "streak_30": {"name": "🌟 Monthly Master", "condition": lambda s: s["current_streak"] >= 30},
    "topics_10": {"name": "📘 Getting Started", "condition": lambda s: s["total_done_topics"] >= 10},
    "topics_50": {"name": "📚 Half Century", "condition": lambda s: s["total_done_topics"] >= 50},
    "topics_100": {"name": "🏅 Century Club", "condition": lambda s: s["total_done_topics"] >= 100},
    "night_owl": {"name": "🦉 Night Owl", "condition": lambda s: s["night_owl"]},
    "early_bird": {"name": "🐦 Early Bird", "condition": lambda s: s["early_bird"]},
    "shield_saver": {"name": "🛡️ Shield Saver", "condition": lambda s: s["shields_used"] >= 1},
}


def _gather_badge_stats(user_id: int):
    from datetime import datetime as _dt

    streak = get_streak(user_id) or {}
    total_done = len(
        supabase.table("syllabus").select("id").eq("user_id", user_id).eq("status", "done").execute().data
    )
    sessions = (
        supabase.table("task_sessions")
        .select("completed_at")
        .eq("user_id", user_id)
        .eq("completed", True)
        .execute()
    ).data

    night_owl = False
    early_bird = False
    for s in sessions:
        if not s.get("completed_at"):
            continue
        try:
            hour = _dt.fromisoformat(s["completed_at"]).hour
        except ValueError:
            continue
        if hour >= 22 or hour < 4:
            night_owl = True
        if hour < 7:
            early_bird = True

    return {
        "current_streak": streak.get("current_streak", 0),
        "total_done_topics": total_done,
        "night_owl": night_owl,
        "early_bird": early_bird,
        "shields_used": streak.get("shields_used", 0),
    }


def get_user_badges(user_id: int):
    res = supabase.table("user_badges").select("*").eq("user_id", user_id).execute()
    return res.data


def award_badge(user_id: int, code: str):
    try:
        supabase.table("user_badges").insert({"user_id": user_id, "badge_code": code}).execute()
    except Exception:
        pass  # already awarded (unique constraint) — safe to ignore


def check_and_award_badges(user_id: int):
    """Checks all badge conditions, awards new ones, returns list of newly-earned badge names."""
    existing_codes = {b["badge_code"] for b in get_user_badges(user_id)}
    stats = _gather_badge_stats(user_id)

    newly_awarded = []
    for code, meta in BADGES.items():
        if code not in existing_codes and meta["condition"](stats):
            award_badge(user_id, code)
            newly_awarded.append(meta["name"])
    return newly_awarded


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
    shield_used, newly_badges = False, []
    if completed:
        plan = supabase.table("daily_plan").select("syllabus_id, user_id").eq("id", plan_id).execute()
        if plan.data:
            mark_topic_status(plan.data[0]["syllabus_id"], "done")
            if today_str:
                shield_used, newly_badges = process_completion(plan.data[0]["user_id"], today_str)
    return shield_used, newly_badges


# ---- Custom scheduled tasks (user-defined topic + time + duration) ----

def add_custom_task(user_id: int, time_str: str, topic: str, duration_minutes: int):
    res = supabase.table("custom_tasks").insert({
        "user_id": user_id, "time": time_str, "topic": topic, "duration_minutes": duration_minutes,
    }).execute()
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


def get_users_with_custom_task_at(time_str: str):
    res = (
        supabase.table("custom_tasks")
        .select("*, users(*)")
        .eq("time", time_str)
        .execute()
    )
    return res.data


def create_task_session(user_id: int, custom_task_id: int, session_date: str, topic: str, duration_minutes: int):
    """Idempotent — won't duplicate if a session already exists today for this task."""
    from datetime import datetime as _dt, timedelta as _td

    existing = (
        supabase.table("task_sessions")
        .select("*")
        .eq("custom_task_id", custom_task_id)
        .eq("session_date", session_date)
        .execute()
    )
    if existing.data:
        return existing.data[0], False  # already existed

    follow_up_due_at = (_dt.now() + _td(minutes=duration_minutes)).isoformat()

    res = supabase.table("task_sessions").insert({
        "user_id": user_id, "custom_task_id": custom_task_id, "session_date": session_date,
        "topic_snapshot": topic, "duration_minutes": duration_minutes,
        "follow_up_due_at": follow_up_due_at, "followup_sent": False,
    }).execute()
    return (res.data[0] if res.data else None), True


def mark_session_completed(session_id: int):
    from datetime import datetime as _dt
    supabase.table("task_sessions").update({
        "completed": True, "completed_at": _dt.now().isoformat(),
    }).eq("id", session_id).execute()

    session = get_session(session_id)
    if not session:
        return False, []
    today_str = _dt.now().strftime("%Y-%m-%d")
    return process_completion(session["user_id"], today_str)


def get_session(session_id: int):
    res = supabase.table("task_sessions").select("*").eq("id", session_id).execute()
    return res.data[0] if res.data else None


def get_due_followups():
    """Sessions whose study duration has elapsed and haven't been followed up on yet."""
    from datetime import datetime as _dt

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
    from datetime import date, timedelta
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
