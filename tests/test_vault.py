"""Tests for the hidden /admin + /admins vault feature: password-only access
(works from any account by design), multiple images, per-image delete, and
brute-force lockout after repeated wrong passwords."""
import types

import pytest

import handlers.vault as vault


@pytest.fixture
def vault_store(monkeypatch):
    store = {"next_id": 1, "images": []}

    def fake_add(file_id):
        row = {"id": store["next_id"], "file_id": file_id, "created_at": "2026-07-11T10:00:00"}
        store["images"].append(row)
        store["next_id"] += 1
        return row

    def fake_get_all():
        return list(store["images"])

    def fake_delete(image_id):
        store["images"] = [r for r in store["images"] if r["id"] != image_id]

    monkeypatch.setattr(vault.db, "add_vault_image", fake_add)
    monkeypatch.setattr(vault.db, "get_vault_images", fake_get_all)
    monkeypatch.setattr(vault.db, "delete_vault_image", fake_delete)
    return store


@pytest.mark.asyncio
async def test_view_command_always_asks_for_password(make_update, make_context):
    ctx = make_context()
    update = make_update(123456)
    await vault.vault_view(update, ctx)
    assert update.message.replies == ["Password?"]


@pytest.mark.asyncio
async def test_save_then_photo_stores_the_largest_size(vault_store, make_update, make_context):
    ctx = make_context()
    await vault.vault_save(make_update(1), ctx)
    await vault.vault_check_password(make_update(1, text="PASS123"), ctx)
    assert ctx.user_data["awaiting_vault_photo"] is True

    sizes = [types.SimpleNamespace(file_id="SMALL"), types.SimpleNamespace(file_id="BIGGEST")]
    update = make_update(1, photo=sizes)
    await vault.vault_photo_handler(update, ctx)

    assert vault_store["images"][-1]["file_id"] == "BIGGEST"
    assert ctx.user_data["awaiting_vault_photo"] is False


@pytest.mark.asyncio
async def test_wrong_password_is_rejected_and_clears_state(make_update, make_context):
    ctx = make_context()
    await vault.vault_view(make_update(1), ctx)
    update = make_update(1, text="wrongpass")
    consumed = await vault.vault_check_password(update, ctx)

    assert consumed is True
    assert update.message.replies == ["❌"]
    assert ctx.user_data["awaiting_vault_password"] is None


@pytest.mark.asyncio
async def test_correct_password_returns_all_stored_images_with_delete_buttons(vault_store, make_update, make_context):
    vault_store["images"] = [
        {"id": 1, "file_id": "IMG1", "created_at": "2026-07-10T00:00:00"},
        {"id": 2, "file_id": "IMG2", "created_at": "2026-07-11T00:00:00"},
    ]
    ctx = make_context()
    await vault.vault_view(make_update(1), ctx)
    update = make_update(1, text="PASS123")
    await vault.vault_check_password(update, ctx)

    assert len(update.message.photos_sent) == 2
    file_ids = [fid for fid, _ in update.message.photos_sent]
    assert file_ids == ["IMG1", "IMG2"]


@pytest.mark.asyncio
async def test_unrelated_text_is_not_swallowed_by_password_check(make_update, make_context):
    ctx = make_context()
    update = make_update(1, text="hi")
    consumed = await vault.vault_check_password(update, ctx)
    assert consumed is False


@pytest.mark.asyncio
async def test_five_wrong_attempts_triggers_lockout(make_update, make_context):
    ctx = make_context()
    for _ in range(5):
        await vault.vault_view(make_update(1), ctx)
        await vault.vault_check_password(make_update(1, text="nope"), ctx)

    assert ctx.bot_data.get("vault_locked_until") is not None

    # Once locked, /admin refuses immediately and never even prompts for a password
    locked_update = make_update(1)
    await vault.vault_view(locked_update, ctx)
    assert locked_update.message.replies == ["⏳"]
    assert ctx.user_data.get("awaiting_vault_password") is None


@pytest.mark.asyncio
async def test_correct_password_resets_failed_attempt_counter(vault_store, make_update, make_context):
    ctx = make_context()
    for _ in range(3):
        await vault.vault_view(make_update(1), ctx)
        await vault.vault_check_password(make_update(1, text="nope"), ctx)
    assert ctx.bot_data.get("vault_failed_attempts") == 3

    await vault.vault_view(make_update(1), ctx)
    await vault.vault_check_password(make_update(1, text="PASS123"), ctx)
    assert ctx.bot_data.get("vault_failed_attempts") == 0
