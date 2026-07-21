"""Tests for utils/progress_ui.py — the animated progress-bar Telegram UI
helper. Uses a fake bot to verify the message sequence without any real
network calls, and monkeypatches asyncio.sleep so the test doesn't actually
wait ~1 second for the animation."""
import pytest

from utils import progress_ui


@pytest.mark.asyncio
async def test_show_progress_sends_native_chat_action_and_animates_to_100_percent(monkeypatch, make_context):
    async def no_sleep(_seconds):
        return None

    monkeypatch.setattr(progress_ui.asyncio, "sleep", no_sleep)

    ctx = make_context()
    msg = await progress_ui._show_progress(555, ctx, "hinglish", "Test label...", "upload_photo")

    assert ctx.bot.chat_actions.count("upload_photo") == 4  # 1 initial + 3 animation steps
    assert "0%" in ctx.bot.sent_messages[0][1]
    assert "40%" in msg.edits[0]
    assert "75%" in msg.edits[1]
    assert "100%" in msg.edits[2]
