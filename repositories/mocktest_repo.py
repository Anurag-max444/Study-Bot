"""Mock test repository — reads and writes to the `mock_tests` table only."""
from database.client import supabase
from exceptions.database import DatabaseError


def add_mock_test(user_id: int, **fields):
    fields["user_id"] = user_id
    fields["test_date"] = fields["test_date"].isoformat()
    try:
        res = supabase.table("mock_tests").insert(fields).execute()
    except Exception as e:
        raise DatabaseError("add_mock_test", e) from e
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
