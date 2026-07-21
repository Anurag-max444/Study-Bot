"""Syllabus repository — reads and writes to the `syllabus` table only."""
from database.client import supabase


def add_syllabus_topics(user_id: int, subject: str, topics: list[str]):
    rows = [{"user_id": user_id, "subject": subject, "topic": topic} for topic in topics]
    if rows:
        supabase.table("syllabus").insert(rows).execute()
