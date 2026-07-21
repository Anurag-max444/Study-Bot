"""Task handlers — /addtask wizard, /mytopics, /removetask, /studylog, and
the 'mark session done' callback."""
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

import db
from ui.lang import t
from utils.formatting import esc
from utils.validators import _parse_time_hhmm, _parse_duration_to_minutes
from services import task_service


async def addtask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        from handlers.onboarding import start  # lazy: avoids a circular import with onboarding.py
        await start(update, context)
        return

    lang = user["language"]
    context.user_data["task_flow"] = {"step": "time"}
    await update.message.reply_text(t("ask_task_time", lang))


async def handle_task_flow_text(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    lang = user["language"]
    text = update.message.text.strip()
    flow = context.user_data["task_flow"]

    if flow["step"] == "time":
        valid_time = _parse_time_hhmm(text)
        if not valid_time:
            await update.message.reply_text(t("invalid_time", lang))
            return
        flow["time"] = valid_time
        flow["step"] = "topic"
        await update.message.reply_text(t("ask_task_topic", lang))
        return

    if flow["step"] == "topic":
        flow["topic"] = text
        flow["step"] = "duration"
        await update.message.reply_text(t("ask_task_duration", lang))
        return

    if flow["step"] == "duration":
        minutes = _parse_duration_to_minutes(text)
        if not minutes or minutes <= 0:
            await update.message.reply_text(t("invalid_duration", lang))
            return

        db.add_custom_task(user["id"], flow["time"], flow["topic"], minutes)
        confirmation = t("task_scheduled", lang, time=flow["time"], topic=flow["topic"], duration=minutes)

        # Agar diya gaya time aaj ke liye pehle hi beet chuka hai, to clearly bata do
        # ki yeh kal fire hoga, warna user confuse ho sakta hai ki bot msg nahi kar raha.
        now_str = datetime.now().strftime("%H:%M")
        if flow["time"] <= now_str:
            confirmation += "\n\n" + t("task_time_already_passed", lang)

        await update.message.reply_text(confirmation)
        del context.user_data["task_flow"]
        return


async def mytopics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        from handlers.onboarding import start
        await start(update, context)
        return

    lang = user["language"]
    tasks = db.get_custom_tasks(user_id)
    if not tasks:
        await update.message.reply_text(t("mytopics_empty", lang))
        return

    msg = t("mytopics_header", lang)
    msg += "\n".join(
        f"⏰ {esc(task['time'])} — <b>{esc(task['topic'])}</b> ({task['duration_minutes']} min)"
        for task in tasks
    )
    await update.message.reply_text(msg, parse_mode="HTML")


async def removetask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        from handlers.onboarding import start
        await start(update, context)
        return

    lang = user["language"]
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(t("invalid_time", lang))
        return

    time_str = context.args[0].strip()
    removed = db.remove_custom_task(user_id, time_str)
    if removed:
        await update.message.reply_text(t("task_removed", lang, time=time_str))
    else:
        await update.message.reply_text(t("task_not_found", lang))


async def studylog_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        from handlers.onboarding import start
        await start(update, context)
        return

    lang = user["language"]
    sessions = db.get_study_log(user_id, days=7)
    if not sessions:
        await update.message.reply_text(t("studylog_empty", lang))
        return

    msg = t("studylog_header", lang, days=7)
    total_minutes = 0
    for s in sessions:
        mark = "✅" if s["completed"] else "⏳"
        msg += f"{mark} {esc(s['session_date'])} — <b>{esc(s['topic_snapshot'])}</b> ({s['duration_minutes']} min)\n"
        if s["completed"]:
            total_minutes += s["duration_minutes"]

    msg += t("studylog_total", lang, hours=round(total_minutes / 60, 1))
    await update.message.reply_text(msg, parse_mode="HTML")


async def mark_session_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    if not user:
        await query.message.reply_text(t("stale_callback", "hinglish"))
        return

    session_id = int(query.data.replace("sessiondone_", ""))
    await query.edit_message_text(query.message.text + "\n\n✅")
    await task_service.complete_session(context.bot, session_id, user)
