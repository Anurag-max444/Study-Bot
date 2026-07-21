"""
Weekly PDF report handler — just the /report command itself. The actual
business logic (data aggregation, PDF building, the Sunday broadcast, and
the startup catch-up check) lives in services/report_service.py; this file
re-exports the job functions too, purely so bot.py's main() can register
them without needing to know they live in the services layer.
"""
import logging

from telegram import Update
from telegram.ext import ContextTypes

import db
from ui.lang import t
from utils.progress_ui import _show_progress
from services.report_service import (
    send_weekly_reports_job, catchup_weekly_report_if_needed, build_and_send_report,
)

_catchup_weekly_report_if_needed = catchup_weekly_report_if_needed  # backward-compatible alias


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        from handlers.onboarding import start  # lazy: avoids a circular import with onboarding.py
        await start(update, context)
        return

    lang = user["language"]
    chat_id = update.effective_chat.id
    progress_msg = await _show_progress(chat_id, context, lang, t("report_generating_label", lang), "upload_document")
    try:
        await build_and_send_report(context.bot, chat_id, user)
    except Exception:
        logging.exception("Failed to build/send weekly report for user %s", user_id)
        await update.message.reply_text(t("report_failed", lang))
    finally:
        try:
            await progress_msg.delete()
        except Exception:
            pass
