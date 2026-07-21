"""Progress repository — cross-cutting queries and orchestration that don't
belong to a single table: completing an activity updates the streak AND
checks for new badges (process_completion), and the tree's growth score /
inactivity check both combine syllabus + task_sessions + streak data.

process_completion's orchestration (streak_repo + badge_repo together) will
move to a services/ layer in a later phase; kept as-is here for now."""
from datetime import date

from database.client import supabase
from repositories.streak_repo import update_streak_on_completion, get_streak
from repositories.badge_repo import check_and_award_badges


def process_completion(user_id: int, today_str: str):
    """Runs after ANY completion event: updates streak/shields, checks for new badges."""
    shield_used = update_streak_on_completion(user_id, today_str)
    newly_awarded_badges = check_and_award_badges(user_id)
    return shield_used, newly_awarded_badges


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
    streak = get_streak(user_id)
    if not streak or not streak.get("last_active_date"):
        return None
    last_active = date.fromisoformat(streak["last_active_date"])
    return (date.today() - last_active).days
