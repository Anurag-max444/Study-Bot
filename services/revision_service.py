"""Revision service — sends due spaced-repetition reminders, and marks a
revision complete when the user confirms."""
import logging

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from ui.lang import t
import db
from utils.formatting import esc


async def send_due_revisions(bot: Bot):
    """Runs every minute; sends any revision reminders that are due today."""
    due = db.get_due_revisions()
    for rev in due:
        try:
            user = rev.get("users")
            if not user or user.get("onboarding_step") != "done":
                continue

            lang = user["language"]
            if rev.get("syllabus"):
                label = f"{esc(rev['syllabus']['subject'])}: {esc(rev['syllabus']['topic'])}"
            else:
                label = esc(rev.get("topic_text") or "—")

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(t("revision_done_button", lang), callback_data=f"revdone_{rev['id']}")]
            ])
            await bot.send_message(
                user["id"],
                t("revision_due_message", lang, interval=rev["interval_label"], topic=label),
                reply_markup=keyboard,
                parse_mode="HTML",
            )
            db.mark_revision_notified(rev["id"])
        except Exception:
            logging.exception(f"send_due_revisions failed for revision {rev.get('id')}")


async def complete_revision(bot: Bot, revision_id: int, user: dict):
    """Marks a revision as completed and confirms to the user."""
    db.mark_revision_completed(revision_id)
    await bot.send_message(user["id"], t("revision_marked_done", user["language"]))
