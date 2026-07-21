"""User repository — reads and writes to the `users` table only."""
from database.client import supabase


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
