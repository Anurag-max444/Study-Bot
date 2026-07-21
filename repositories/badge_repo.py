"""Badge repository — reads and writes to the `user_badges` table, plus the
badge-condition definitions and the stats-gathering needed to check them.
_gather_badge_stats queries syllabus/task_sessions/streaks because that's
what the badge conditions need, but its purpose is entirely "am I eligible
for a badge", so it lives here rather than being split further."""
from datetime import datetime as _dt

from database.client import supabase
from repositories.streak_repo import get_streak

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
