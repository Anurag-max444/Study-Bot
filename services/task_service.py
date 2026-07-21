"""Task service — orchestrates the study-session lifecycle: starting a
scheduled task when its time arrives, following up once the duration has
elapsed, and completing a session (which also triggers streak/badge
processing via notification_service)."""
import logging
from datetime import datetime

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from ui.lang import t
import db
from utils.formatting import esc
from services import notification_service


async def start_due_task_sessions(bot: Bot):
    """Runs every minute. Catch-up safe — fires anything whose time has arrived, even if delayed."""
    today_str = datetime.now().strftime("%Y-%m-%d")

    rows = db.get_due_custom_tasks()
    for row in rows:
        try:
            user = row.get("users")
            if not user or user.get("onboarding_step") != "done":
                continue

            lang = user["language"]
            session, is_new = db.create_task_session(
                user["id"], row["id"], today_str, row["topic"], row["duration_minutes"]
            )
            if not is_new or not session:
                continue  # already started today, avoid duplicate reminders

            # One-time by design: agar dubara padhna ho to /addtask se manually dobara set karo.
            # Study log (task_sessions) me history hamesha safe rehti hai, isse asar nahi padta.
            db.delete_custom_task_by_id(row["id"])

            await bot.send_message(
                user["id"],
                t(
                    "task_session_start", lang,
                    name=esc(user["name"] or ""), topic=esc(row["topic"]),
                    duration=row["duration_minutes"],
                ),
                parse_mode="HTML",
            )
            # Follow-up ka time database me save ho gaya hai (create_task_session ke andar) —
            # ab yeh send_task_followups job khud uthayega, chahe bot beech me restart bhi ho jaye.
        except Exception:
            logging.exception(f"start_due_task_sessions failed for custom_task {row.get('id')}")


async def send_task_followups(bot: Bot):
    """Runs every minute. Sends the 'did you finish?' prompt for any session whose time is up.
    DB-backed (not in-memory) so a Render restart/sleep during the study window can't lose it."""
    due_sessions = db.get_due_followups()
    for session in due_sessions:
        try:
            user = session.get("users")
            if not user:
                continue

            lang = user["language"]
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(t("session_done_button", lang), callback_data=f"sessiondone_{session['id']}")]
            ])
            await bot.send_message(
                user["id"],
                t("task_session_followup", lang, topic=esc(session["topic_snapshot"])),
                reply_markup=keyboard,
                parse_mode="HTML",
            )
            db.mark_followup_sent(session["id"])
        except Exception:
            logging.exception(f"send_task_followups failed for session {session.get('id')}")


async def complete_session(bot: Bot, session_id: int, user: dict):
    """Marks a study session as completed, then sends the confirmation message
    plus any streak/badge notifications that completion earned."""
    lang = user["language"]
    shield_used, newly_badges = db.mark_session_completed(session_id)
    session = db.get_session(session_id)
    topic = session["topic_snapshot"] if session else ""

    await bot.send_message(
        user["id"], t("session_marked_done", lang, name=user["name"] or "", topic=topic)
    )
    await notification_service.notify_gamification(bot, user["id"], lang, shield_used, newly_badges)
