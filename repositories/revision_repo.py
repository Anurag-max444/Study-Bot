"""Revision repository — reads and writes to the `revisions` table only
(spaced-repetition reminders)."""
from datetime import date, timedelta

from database.client import supabase

REVISION_INTERVALS = [(1, "1-day"), (3, "3-day"), (7, "7-day"), (15, "15-day")]


def create_revisions_for_topic(user_id: int, today_str: str, syllabus_id: int = None, topic_text: str = None):
    """Schedules 4 future revision reminders (1/3/7/15 days). Use syllabus_id OR topic_text."""
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
