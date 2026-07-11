import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_user(user_id: int):
    res = supabase.table("users").select("*").eq("id", user_id).execute()
    return res.data[0] if res.data else None


def get_all_onboarded_users():
    """Every user who has completed onboarding — used for the weekly report broadcast."""
    res = supabase.table("users").select("*").eq("onboarding_step", "done").execute()
    return res.data


def create_user(user_id: int):
    supabase.table("users").insert({"id": user_id, "onboarding_step": "ask_language"}).execute()
    return get_user(user_id)


def update_user(user_id: int, **fields):
    supabase.table("users").update(fields).eq("id", user_id).execute()


def add_syllabus_topics(user_id: int, subject: str, topics: list[str]):
    rows = [{"user_id": user_id, "subject": subject, "topic": topic} for topic in topics]
    if rows:
        supabase.table("syllabus").insert(rows).execute()


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


# ---- Custom scheduled tasks (user-defined topic + time + duration) ----

def add_custom_task(user_id: int, time_str: str, topic: str, duration_minutes: int):
    from datetime import datetime, timedelta

    now = datetime.now()
    hh, mm = map(int, time_str.split(":"))
    candidate = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if candidate <= now:
        candidate += timedelta(days=1)  # time already passed today, schedule for tomorrow

    res = supabase.table("custom_tasks").insert({
        "user_id": user_id, "time": time_str, "topic": topic, "duration_minutes": duration_minutes,
        "next_trigger_at": candidate.isoformat(),
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


def get_due_custom_tasks():
    """Catch-up safe: returns tasks whose trigger time has arrived or passed (not exact-minute match)."""
    from datetime import datetime

    now_iso = datetime.now().isoformat()
    res = (
        supabase.table("custom_tasks")
        .select("*, users(*)")
        .lte("next_trigger_at", now_iso)
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

    # Sirf /addtask (custom_tasks) se complete hue topics ke liye revision schedule hoti hai.
    create_revisions_for_topic(session["user_id"], today_str, topic_text=session["topic_snapshot"])

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


def get_tree_growth_score(user_id: int):
    """Total completed activities (syllabus topics + custom task sessions) — never decreases."""
    total_done_topics = len(
        supabase.table("syllabus").select("id").eq("user_id", user_id).eq("status", "done").execute().data
    )
    total_sessions = len(
        supabase.table("task_sessions").select("id").eq("user_id", user_id).eq("completed", True).execute().data
    )
    return total_done_topics + total_sessions


def get_days_since_active(user_id: int):
    """Returns days since last completed activity, or None if never active."""
    from datetime import date

    streak = get_streak(user_id)
    if not streak or not streak.get("last_active_date"):
        return None
    last_active = date.fromisoformat(streak["last_active_date"])
    return (date.today() - last_active).days


# ---- Spaced Repetition Revisions ----

REVISION_INTERVALS = [(1, "1-day"), (3, "3-day"), (7, "7-day"), (15, "15-day")]


def create_revisions_for_topic(user_id: int, today_str: str, syllabus_id: int = None, topic_text: str = None):
    """Schedules 4 future revision reminders (1/3/7/15 days). Use syllabus_id OR topic_text."""
    from datetime import date, timedelta

    base = date.fromisoformat(today_str)
    rows = [
        {
            "user_id": user_id,
            "syllabus_id": syllabus_id,
            "topic_text": topic_text,
            "due_date": (base + timedelta(days=offset)).isoformat(),
            "interval_label": label,
        }
        for offset, label in REVISION_INTERVALS
    ]
    supabase.table("revisions").insert(rows).execute()


def get_due_revisions():
    """Revisions due today (or earlier) that haven't been notified about yet."""
    from datetime import date

    today_str = date.today().isoformat()
    res = (
        supabase.table("revisions")
        .select("*, users(*), syllabus(*)")
        .eq("notified", False)
        .eq("completed", False)
        .lte("due_date", today_str)
        .execute()
    )
    return res.data


def mark_revision_notified(revision_id: int):
    supabase.table("revisions").update({"notified": True}).eq("id", revision_id).execute()


def mark_revision_completed(revision_id: int):
    supabase.table("revisions").update({"completed": True}).eq("id", revision_id).execute()


def get_pending_revisions(user_id: int):
    res = (
        supabase.table("revisions")
        .select("*, syllabus(*)")
        .eq("user_id", user_id)
        .eq("completed", False)
        .order("due_date")
        .execute()
    )
    return res.data


# ---- Mock test logging ----

def add_mock_test(user_id: int, **fields):
    fields["user_id"] = user_id
    fields["test_date"] = fields["test_date"].isoformat()
    res = supabase.table("mock_tests").insert(fields).execute()
    return res.data[0] if res.data else None


def get_mock_tests(user_id: int):
    res = (
        supabase.table("mock_tests")
        .select("*")
        .eq("user_id", user_id)
        .order("test_date", desc=True)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data


def get_mock_test(test_id: int, user_id: int):
    res = (
        supabase.table("mock_tests")
        .select("*")
        .eq("id", test_id)
        .eq("user_id", user_id)
        .execute()
    )
    return res.data[0] if res.data else None


# ---- Personal vault (multiple images) ----
# Only each image's Telegram file_id is stored — Telegram hosts the actual
# file, so this survives bot restarts/redeploys without needing persistent disk.

def add_vault_image(file_id: str):
    res = supabase.table("vault_images").insert({"file_id": file_id}).execute()
    return res.data[0] if res.data else None


def get_vault_images():
    res = supabase.table("vault_images").select("*").order("created_at").execute()
    return res.data


def delete_vault_image(image_id: int):
    supabase.table("vault_images").delete().eq("id", image_id).execute()
