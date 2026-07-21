"""Misc handlers — /cancel (universal escape hatch), /help, /clear, and the
app-wide error handler."""
import logging

from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import TelegramError as PTBTelegramError

import db
from ui.lang import t
from exceptions.database import DatabaseError
from exceptions.validation import ValidationError

_ALL_FLOW_KEYS = ("task_flow", "mocktest_flow", "awaiting_question_pdf", "awaiting_vault_password", "awaiting_vault_photo")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Universal escape hatch — clears any in-progress multi-step flow
    (/addtask, /addmocktest, PDF question extraction, vault prompts) so the
    user is never stuck mid-flow with no way out."""
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    lang = user["language"] if user else "hinglish"

    was_active = any(context.user_data.get(k) for k in _ALL_FLOW_KEYS)
    for key in _ALL_FLOW_KEYS:
        context.user_data.pop(key, None)

    if was_active:
        await update.message.reply_text(t("cancel_done", lang))
    else:
        await update.message.reply_text(t("cancel_nothing_active", lang))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    lang = user["language"] if user else "hinglish"
    await update.message.reply_text(t("help_text", lang), parse_mode="HTML")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Silently deletes recent messages in this chat (both the bot's and the user's,
    since Telegram allows a bot to delete any message in a private chat within 48h).
    No status message is sent before, during, or after — fully silent."""
    chat_id = update.effective_chat.id
    current_id = update.message.message_id

    lookback = 300
    if context.args and context.args[0].isdigit():
        lookback = min(int(context.args[0]), 2000)

    all_ids = list(range(current_id, max(current_id - lookback, 0), -1))

    # Batch delete in chunks of 100 (Telegram's max per deleteMessages call) — this
    # silently skips any IDs that don't exist or can't be deleted, no error raised,
    # and is far faster than deleting one message at a time.
    for i in range(0, len(all_ids), 100):
        chunk = all_ids[i:i + 100]
        try:
            await context.bot.delete_messages(chat_id, chunk)
        except Exception:
            # Fallback for older library/API versions without bulk delete support
            for mid in chunk:
                try:
                    await context.bot.delete_message(chat_id, mid)
                except Exception:
                    pass


async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Catches any unhandled exception anywhere in the bot so nothing fails silently.
    Categorizes the error type in the log line so a database failure, a
    Telegram API failure, and everything else are easy to tell apart at a
    glance — the actual behavior (log and move on, never crash the bot) is
    unchanged either way."""
    error = context.error
    if isinstance(error, DatabaseError):
        logging.error("Database error during '%s': %s", error.operation, error.original_error, exc_info=error)
    elif isinstance(error, ValidationError):
        logging.error("Validation error on '%s': %s", error.field, error.reason, exc_info=error)
    elif isinstance(error, PTBTelegramError):
        logging.error("Telegram API error: %s", error, exc_info=error)
    else:
        logging.error("Unhandled exception while processing update:", exc_info=error)
