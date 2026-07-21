"""Streak repository — reads and writes to the `streaks` table only.
(Shield/badge award orchestration lives in progress_repo.py, not here.)"""
from datetime import date, timedelta

from database.client import supabase


def get_streak(user_id: int):
    res = supabase.table("streaks").select("*").eq("user_id", user_id).execute()
    return res.data[0] if res.data else None


def update_streak_on_completion(user_id: int, today_str: str) -> bool:
    """Call this when user marks at least one topic done today. Returns True if a shield was consumed."""
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
