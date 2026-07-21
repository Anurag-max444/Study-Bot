"""Tests for the universal /cancel command — it must clear every possible
multi-step flow state, and tell the user correctly whether anything was
actually cancelled."""
import handlers.misc as misc
from ui.lang import t
import pytest

import bot


@pytest.mark.asyncio
async def test_cancel_clears_mocktest_flow(monkeypatch, fake_user, make_update, make_context):
    monkeypatch.setattr(misc.db, "get_user", lambda uid: fake_user)
    ctx = make_context(user_data={"mocktest_flow": {"step": "attempted"}})
    update = make_update(fake_user["id"])

    await bot.cancel_command(update, ctx)

    assert "mocktest_flow" not in ctx.user_data
    assert update.message.replies


@pytest.mark.asyncio
async def test_cancel_clears_addtask_flow(monkeypatch, fake_user, make_update, make_context):
    monkeypatch.setattr(misc.db, "get_user", lambda uid: fake_user)
    ctx = make_context(user_data={"task_flow": {"step": "time"}})
    update = make_update(fake_user["id"])

    await bot.cancel_command(update, ctx)

    assert "task_flow" not in ctx.user_data


@pytest.mark.asyncio
async def test_cancel_clears_vault_and_pdf_flags_together(monkeypatch, fake_user, make_update, make_context):
    monkeypatch.setattr(misc.db, "get_user", lambda uid: fake_user)
    ctx = make_context(user_data={"awaiting_vault_password": "view", "awaiting_question_pdf": True})
    update = make_update(fake_user["id"])

    await bot.cancel_command(update, ctx)

    assert ctx.user_data == {}


@pytest.mark.asyncio
async def test_cancel_with_nothing_active_says_so(monkeypatch, fake_user, make_update, make_context):
    monkeypatch.setattr(misc.db, "get_user", lambda uid: fake_user)
    ctx = make_context(user_data={})
    update = make_update(fake_user["id"])

    await bot.cancel_command(update, ctx)

    # The "nothing to cancel" message should differ from the "cancelled" message
    assert update.message.replies[0] != t("cancel_done", "hinglish")
