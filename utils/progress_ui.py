"""Animated progress-bar UI for slow-feeling operations (tree image / PDF
report generation). Kept separate from formatting.py because this one does
actual Telegram I/O (sends and edits messages), not just string formatting."""
import asyncio

from telegram.ext import ContextTypes

from ui.lang import t
from utils.formatting import _progress_bar


async def _show_progress(chat_id: int, context: ContextTypes.DEFAULT_TYPE, lang: str,
                          label: str, chat_action: str):
    """Sends a small message with an animated progress bar while a file (tree
    image / PDF report) is being generated, plus Telegram's own native
    "uploading..." indicator. Returns the message so the caller can delete it
    once the real file is ready to send. Generation itself is fast, so the
    steps below are intentionally paced — purely a "this is doing something"
    cue rather than a literal progress readout."""
    try:
        await context.bot.send_chat_action(chat_id, action=chat_action)
    except Exception:
        pass

    msg = await context.bot.send_message(
        chat_id, t("generating_progress_line", lang, label=label, bar=_progress_bar(0, 100), pct=0)
    )
    for pct in (40, 75, 100):
        await asyncio.sleep(0.35)
        try:
            await context.bot.send_chat_action(chat_id, action=chat_action)
            await msg.edit_text(
                t("generating_progress_line", lang, label=label, bar=_progress_bar(pct, 100), pct=pct)
            )
        except Exception:
            pass
    return msg
