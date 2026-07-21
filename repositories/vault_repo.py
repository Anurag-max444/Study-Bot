"""Vault repository — reads and writes to the `vault_images` table only."""
from database.client import supabase
from exceptions.database import DatabaseError


def add_vault_image(file_id: str):
    try:
        res = supabase.table("vault_images").insert({"file_id": file_id}).execute()
    except Exception as e:
        raise DatabaseError("add_vault_image", e) from e
    return res.data[0] if res.data else None


def get_vault_images():
    res = supabase.table("vault_images").select("*").order("created_at").execute()
    return res.data


def delete_vault_image(image_id: int):
    supabase.table("vault_images").delete().eq("id", image_id).execute()
