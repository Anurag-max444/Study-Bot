"""State repository — reads and writes to the `bot_state` key-value table
only (currently used for tracking the last successful weekly-report run)."""
from database.client import supabase


def get_state(key: str):
    res = supabase.table("bot_state").select("value").eq("key", key).execute()
    return res.data[0]["value"] if res.data else None


def set_state(key: str, value: str):
    supabase.table("bot_state").upsert({"key": key, "value": value}).execute()
