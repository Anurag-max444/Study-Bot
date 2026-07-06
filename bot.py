import os
import logging
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters,
)

import db
from lang import t
from default_syllabus import DEFAULT_SYLLABUS

# NOTE: Render pe env var TZ=Asia/Kolkata set karna, warna server UTC time use karega
# aur reminders galat time pe jayenge.

load_dotenv()
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if user:
        await update.message.reply_text(
            t("welcome", user["language"], name=user["name"] or "dost")
        )
        return

    db.create_user(user_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("हिंदी", callback_data="lang_hindi")],
        [InlineKeyboardButton("English", callback_data="lang_english")],
        [InlineKeyboardButton("Hinglish", callback_data="lang_hinglish")],
    ])
    await update.message.reply_text(t("ask_language", "hinglish"), reply_markup=keyboard)


# ---------- Language selection ----------
async def language_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = query.data.replace("lang_", "")  # hindi / english / hinglish

    db.update_user(user_id, language=lang, onboarding_step="ask_name")
    await query.edit_message_text(t("ask_name", lang))


# ---------- Exam selection ----------
async def exam_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    exam = query.data.replace("exam_", "")  # ssc_cgl / jee_mains / custom

    db.update_user(user_id, exam=exam, onboarding_step="ask_syllabus_pdf")

    if exam in DEFAULT_SYLLABUS:
        for subject, topics in DEFAULT_SYLLABUS[exam].items():
            db.add_syllabus_topics(user_id, subject, topics)

    await query.edit_message_text(t("ask_syllabus_pdf", user["language"]))


# ---------- Text message router (handles onboarding steps) ----------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]

    # Custom task scheduling flow (triggered by /addtask) takes priority
    if context.user_data.get("task_flow"):
        await handle_task_flow_text(update, context, user)
        return

    step = user["onboarding_step"]
    text = update.message.text.strip()

    if step == "ask_name":
        db.update_user(user_id, name=text, onboarding_step="ask_exam")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("SSC CGL", callback_data="exam_ssc_cgl")],
            [InlineKeyboardButton("JEE Mains", callback_data="exam_jee_mains")],
            [InlineKeyboardButton("Custom / Other", callback_data="exam_custom")],
        ])
        await update.message.reply_text(t("ask_exam", lang), reply_markup=keyboard)
        return

    if step == "ask_syllabus_pdf":
        if text.lower() == "skip":
            db.update_user(user_id, onboarding_step="ask_hours")
            await update.message.reply_text(t("ask_hours", lang))
        else:
            await update.message.reply_text(t("ask_syllabus_pdf", lang))
        return

    if step == "ask_hours":
        if text.isdigit():
            db.update_user(user_id, daily_hours=int(text), onboarding_step="ask_reminder_time")
            await update.message.reply_text(t("ask_reminder_time", lang))
        else:
            await update.message.reply_text(t("invalid_number", lang))
        return

    if step == "ask_reminder_time":
        if len(text) == 5 and text[2] == ":" and text.replace(":", "").isdigit():
            db.update_user(user_id, reminder_time=text, onboarding_step="ask_evening_time")
            await update.message.reply_text(t("ask_evening_time", lang))
        else:
            await update.message.reply_text(t("invalid_time", lang))
        return

    if step == "ask_evening_time":
        if len(text) == 5 and text[2] == ":" and text.replace(":", "").isdigit():
            db.update_user(user_id, evening_reminder_time=text, onboarding_step="done")
            await update.message.reply_text(t("setup_done", lang, time=user["reminder_time"]))
        else:
            await update.message.reply_text(t("invalid_time", lang))
        return

    # Default fallback once onboarding is done
    await update.message.reply_text(t("welcome", lang, name=user["name"] or "dost"))


# ---------- PDF upload handler (syllabus, during onboarding) ----------
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        return

    # Question-extraction flow (triggered via /extractquestions)
    if context.user_data.get("awaiting_question_pdf"):
        await handle_question_pdf(update, context, user)
        return

    # Syllabus flow (only during onboarding step)
    if user["onboarding_step"] != "ask_syllabus_pdf":
        return

    file = await update.message.document.get_file()
    path = f"/tmp/{user_id}_syllabus.pdf"
    await file.download_to_drive(path)

    import pdfplumber
    topics = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split("\n"):
                line = line.strip()
                if 3 < len(line) < 80:
                    topics.append(line)

    if topics:
        db.add_syllabus_topics(user_id, "Custom (from PDF)", topics[:50])

    db.update_user(user_id, onboarding_step="ask_hours")
    await update.message.reply_text(t("ask_hours", user["language"]))


def _build_checklist_keyboard(plan_items):
    buttons = []
    for item in plan_items:
        topic_name = item["syllabus"]["topic"]
        subject = item["syllabus"]["subject"]
        check = "✅" if item["completed"] else "⬜"
        label = f"{check} {subject}: {topic_name}"[:60]
        buttons.append([InlineKeyboardButton(label, callback_data=f"toggle_{item['id']}")])
    return InlineKeyboardMarkup(buttons)


async def send_morning_plan(context: ContextTypes.DEFAULT_TYPE):
    now_str = datetime.now().strftime("%H:%M")
    users = db.get_users_by_morning_time(now_str)
    today_str = datetime.now().strftime("%Y-%m-%d")

    for user in users:
        lang = user["language"]
        plan_items = db.create_today_plan(user["id"], today_str)

        if not plan_items:
            await context.bot.send_message(user["id"], t("no_topics_left", lang))
            continue

        header = t("morning_plan_header", lang, name=user["name"] or "")
        keyboard = _build_checklist_keyboard(plan_items)
        await context.bot.send_message(user["id"], header, reply_markup=keyboard)


async def send_evening_checklist(context: ContextTypes.DEFAULT_TYPE):
    now_str = datetime.now().strftime("%H:%M")
    users = db.get_users_by_evening_time(now_str)
    today_str = datetime.now().strftime("%Y-%m-%d")

    for user in users:
        lang = user["language"]
        plan_items = db.get_today_plan(user["id"], today_str)

        if not plan_items:
            continue

        header = t("evening_checklist_header", lang)
        if datetime.now().weekday() == 6:  # Sunday
            stats = db.get_progress_stats(user["id"])
            total_done = sum(s["done"] for s in stats.values())
            total_all = sum(s["total"] for s in stats.values())
            header += f"\n\n📅 Weekly wrap: {total_done}/{total_all} topics done overall so far."
        keyboard = _build_checklist_keyboard(plan_items)
        await context.bot.send_message(user["id"], header, reply_markup=keyboard)


async def _notify_gamification(context: ContextTypes.DEFAULT_TYPE, user_id: int, lang: str, shield_used: bool, newly_badges: list):
    """Sends shield-used and new-badge notifications after any completion event."""
    if shield_used:
        streak = db.get_streak(user_id)
        remaining = streak["shields_available"] if streak else 0
        await context.bot.send_message(user_id, t("shield_used_notification", lang, remaining=remaining))

    for badge_name in newly_badges:
        await context.bot.send_message(user_id, t("badge_earned_notification", lang, badge_name=badge_name))


async def toggle_checklist_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    plan_id = int(query.data.replace("toggle_", ""))

    current_markup = query.message.reply_markup
    new_buttons = []
    shield_used, newly_badges = False, []
    for row in current_markup.inline_keyboard:
        btn = row[0]
        if btn.callback_data == query.data:
            is_now_checked = btn.text.startswith("✅")
            new_completed = not is_now_checked
            shield_used, newly_badges = db.toggle_plan_item(
                plan_id, new_completed, today_str=datetime.now().strftime("%Y-%m-%d")
            )
            check = "✅" if new_completed else "⬜"
            new_text = check + btn.text[1:]
            new_buttons.append([InlineKeyboardButton(new_text, callback_data=btn.callback_data)])
        else:
            new_buttons.append(row)

    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(new_buttons))

    if shield_used or newly_badges:
        user = db.get_user(user_id)
        lang = user["language"] if user else "hinglish"
        await _notify_gamification(context, user_id, lang, shield_used, newly_badges)


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user or user["onboarding_step"] != "done":
        await start(update, context)
        return

    lang = user["language"]
    streak = db.get_streak(user_id)
    streak_count = streak["current_streak"] if streak else 0
    longest = streak["longest_streak"] if streak else 0
    shields = streak["shields_available"] if streak else 0

    msg = t("progress_header", lang, name=user["name"] or "", streak=streak_count, longest=longest)
    msg += t("shields_line", lang, shields=shields)

    badge_count = len(db.get_user_badges(user_id))
    msg += t("badges_summary_line", lang, count=badge_count, total=len(db.BADGES))

    stats = db.get_progress_stats(user_id)
    if not stats:
        msg += "\n" + t("no_topics_left", lang)
    else:
        for subject, counts in stats.items():
            done, total = counts["done"], counts["total"]
            pct = int((done / total) * 100) if total else 0
            filled = pct // 10
            bar = "▓" * filled + "░" * (10 - filled)
            msg += f"\n{subject}: {bar} {done}/{total} ({pct}%)"

    await update.message.reply_text(msg)


async def badges_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    earned = db.get_user_badges(user_id)
    earned_codes = {b["badge_code"] for b in earned}

    msg = t("badges_header", lang, count=len(earned_codes), total=len(db.BADGES))
    for code, meta in db.BADGES.items():
        mark = "✅" if code in earned_codes else "🔒"
        msg += f"\n{mark} {meta['name']}"

    await update.message.reply_text(msg)


async def extractquestions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    context.user_data["awaiting_question_pdf"] = True
    await update.message.reply_text(t("ask_question_pdf", lang))


async def handle_question_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    import pdfplumber
    from telegram.error import BadRequest
    from question_extractor import extract_questions_from_text, generate_questions_pdf

    user_id = user["id"]
    lang = user["language"]
    context.user_data["awaiting_question_pdf"] = False

    def _bar(pct):
        filled = pct // 10
        return "▓" * filled + "░" * (10 - filled)

    status_msg = await update.message.reply_text(f"{t('extracting_in_progress', lang)}\n[{_bar(0)}] 0%")

    async def _update_progress(text, pct):
        try:
            await status_msg.edit_text(f"{text}\n[{_bar(pct)}] {pct}%")
        except BadRequest:
            pass  # ignore "message not modified" when % hasn't changed

    in_path = f"/tmp/{user_id}_qsource.pdf"
    file = await update.message.document.get_file()
    await file.download_to_drive(in_path)

    full_text = ""
    with pdfplumber.open(in_path) as pdf:
        total_pages = len(pdf.pages) or 1
        for i, page in enumerate(pdf.pages, start=1):
            full_text += (page.extract_text() or "") + "\n"
            pct = int((i / total_pages) * 70)
            await _update_progress(f"📄 Reading page {i}/{total_pages}...", pct)

    await _update_progress("🔍 Parsing questions...", 80)
    questions = extract_questions_from_text(full_text)

    if not questions:
        await status_msg.edit_text(t("no_questions_found", lang))
        return

    await _update_progress("📝 Formatting PDF...", 95)
    out_path = f"/tmp/{user_id}_questions_output.pdf"
    try:
        generate_questions_pdf(questions, out_path, title="Extracted Questions")
    except Exception as e:
        logging.exception("PDF generation failed")
        await status_msg.edit_text(
            f"❌ Kuch gadbad ho gayi PDF banate waqt. Kripya dobara try kijiye ya alag PDF use kijiye.\n({type(e).__name__})"
        )
        return

    await status_msg.edit_text(f"✅ Done!\n[{_bar(100)}] 100%")

    with open(out_path, "rb") as f:
        await update.message.reply_document(
            document=f,
            filename="extracted_questions.pdf",
            caption=t("extraction_done", lang, count=len(questions)),
        )


class _HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Study Buddy bot is alive!")

    def log_message(self, format, *args):
        pass  # keep logs clean, don't print every ping


def _run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), _HealthCheckHandler)
    server.serve_forever()


async def addreminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(t("addreminder_usage", lang))
        return

    time_str = context.args[0].strip()
    if not (len(time_str) == 5 and time_str[2] == ":" and time_str.replace(":", "").isdigit()):
        await update.message.reply_text(t("invalid_time", lang))
        return

    db.add_reminder_slot(user_id, time_str)
    await update.message.reply_text(t("reminder_added", lang, time=time_str))


async def removereminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(t("addreminder_usage", lang))
        return

    time_str = context.args[0].strip()
    removed = db.remove_reminder_slot(user_id, time_str)
    if removed:
        await update.message.reply_text(t("reminder_removed", lang, time=time_str))
    else:
        await update.message.reply_text(t("reminder_not_found", lang))


async def myreminders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    slots = db.get_reminder_slots(user_id)
    if not slots:
        await update.message.reply_text(t("reminder_list_empty", lang))
        return

    msg = t("reminder_list_header", lang)
    msg += "\n".join(f"⏰ {slot['time']}" for slot in slots)
    await update.message.reply_text(msg)


async def send_task_reminders(context: ContextTypes.DEFAULT_TYPE):
    """Runs every minute. For each user with a reminder_slot matching now, sends ONE next topic."""
    now_str = datetime.now().strftime("%H:%M")
    today_str = datetime.now().strftime("%Y-%m-%d")

    slot_rows = db.get_users_with_slot_at(now_str)
    for slot in slot_rows:
        user = slot.get("users")
        if not user or user.get("onboarding_step") != "done":
            continue

        lang = user["language"]
        task = db.get_or_create_next_task(user["id"], today_str)

        if not task:
            await context.bot.send_message(user["id"], t("task_all_done_today", lang))
            continue

        header = t("task_reminder_header", lang, name=user["name"] or "")
        topic_line = f"\n\n📌 {task['syllabus']['subject']}: {task['syllabus']['topic']}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("mark_done_button", lang), callback_data=f"donetask_{task['id']}")]
        ])
        await context.bot.send_message(user["id"], header + topic_line, reply_markup=keyboard)


async def mark_task_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    lang = user["language"] if user else "hinglish"

    plan_id = int(query.data.replace("donetask_", ""))
    today_str = datetime.now().strftime("%Y-%m-%d")
    shield_used, newly_badges = db.toggle_plan_item(plan_id, True, today_str=today_str)

    await query.edit_message_text(
        query.message.text + "\n\n✅",
    )
    await context.bot.send_message(user_id, t("task_marked_done", lang, name=user["name"] or ""))
    await _notify_gamification(context, user_id, lang, shield_used, newly_badges)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    lang = user["language"] if user else "hinglish"
    await update.message.reply_text(t("help_text", lang), parse_mode="Markdown")


def _parse_duration_to_minutes(text: str):
    """Parses '1h', '90m', '1.5h', '45' into minutes (int). Returns None if invalid."""
    text = text.strip().lower()
    try:
        if text.endswith("h"):
            return round(float(text[:-1]) * 60)
        if text.endswith("m"):
            return int(float(text[:-1]))
        if text.isdigit():
            return int(text)
    except ValueError:
        return None
    return None


async def addtask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
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
        if not (len(text) == 5 and text[2] == ":" and text.replace(":", "").isdigit()):
            await update.message.reply_text(t("invalid_time", lang))
            return
        flow["time"] = text
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
        await update.message.reply_text(
            t("task_scheduled", lang, time=flow["time"], topic=flow["topic"], duration=minutes)
        )
        del context.user_data["task_flow"]
        return


async def mytopics_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    tasks = db.get_custom_tasks(user_id)
    if not tasks:
        await update.message.reply_text(t("mytopics_empty", lang))
        return

    msg = t("mytopics_header", lang)
    msg += "\n".join(f"⏰ {task['time']} — {task['topic']} ({task['duration_minutes']} min)" for task in tasks)
    await update.message.reply_text(msg)


async def removetask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
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
        msg += f"{mark} {s['session_date']} — {s['topic_snapshot']} ({s['duration_minutes']} min)\n"
        if s["completed"]:
            total_minutes += s["duration_minutes"]

    msg += t("studylog_total", lang, hours=round(total_minutes / 60, 1))
    await update.message.reply_text(msg)


async def send_custom_task_start(context: ContextTypes.DEFAULT_TYPE):
    """Runs every minute. Starts any custom task whose time matches now."""
    now_str = datetime.now().strftime("%H:%M")
    today_str = datetime.now().strftime("%Y-%m-%d")

    rows = db.get_users_with_custom_task_at(now_str)
    for row in rows:
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

        await context.bot.send_message(
            user["id"],
            t("task_session_start", lang, name=user["name"] or "", topic=row["topic"], duration=row["duration_minutes"]),
            parse_mode="Markdown",
        )
        # Follow-up ka time database me save ho gaya hai (create_task_session ke andar) —
        # ab yeh check_due_followups job khud uthayega, chahe bot beech me restart bhi ho jaye.


async def check_due_followups(context: ContextTypes.DEFAULT_TYPE):
    """Runs every minute. Sends the 'did you finish?' prompt for any session whose time is up.
    DB-backed (not in-memory) so a Render restart/sleep during the study window can't lose it."""
    due_sessions = db.get_due_followups()
    for session in due_sessions:
        user = session.get("users")
        if not user:
            continue

        lang = user["language"]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("session_done_button", lang), callback_data=f"sessiondone_{session['id']}")]
        ])
        await context.bot.send_message(
            user["id"],
            t("task_session_followup", lang, topic=session["topic_snapshot"]),
            reply_markup=keyboard,
        )
        db.mark_followup_sent(session["id"])


async def mark_session_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    lang = user["language"] if user else "hinglish"

    session_id = int(query.data.replace("sessiondone_", ""))
    shield_used, newly_badges = db.mark_session_completed(session_id)
    session = db.get_session(session_id)
    topic = session["topic_snapshot"] if session else ""

    await query.edit_message_text(query.message.text + "\n\n✅")
    await context.bot.send_message(
        user_id, t("session_marked_done", lang, name=user["name"] or "", topic=topic)
    )
    await _notify_gamification(context, user_id, lang, shield_used, newly_badges)


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("progress", progress_command))
    app.add_handler(CommandHandler("badges", badges_command))
    app.add_handler(CommandHandler("extractquestions", extractquestions_command))
    app.add_handler(CommandHandler("pdf", extractquestions_command))
    app.add_handler(CommandHandler("addreminder", addreminder_command))
    app.add_handler(CommandHandler("removereminder", removereminder_command))
    app.add_handler(CommandHandler("myreminders", myreminders_command))
    app.add_handler(CommandHandler("addtask", addtask_command))
    app.add_handler(CommandHandler("mytopics", mytopics_command))
    app.add_handler(CommandHandler("removetask", removetask_command))
    app.add_handler(CommandHandler("studylog", studylog_command))
    app.add_handler(CallbackQueryHandler(language_chosen, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(exam_chosen, pattern="^exam_"))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(CallbackQueryHandler(toggle_checklist_item, pattern="^toggle_"))
    app.add_handler(CallbackQueryHandler(mark_task_done, pattern="^donetask_"))
    app.add_handler(CallbackQueryHandler(mark_session_done, pattern="^sessiondone_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Har minute check karo ki kisi user ka reminder time ab hua hai kya
    app.job_queue.run_repeating(send_morning_plan, interval=60, first=5)
    app.job_queue.run_repeating(send_evening_checklist, interval=60, first=5)
    app.job_queue.run_repeating(send_task_reminders, interval=60, first=5)
    app.job_queue.run_repeating(send_custom_task_start, interval=60, first=5)
    app.job_queue.run_repeating(check_due_followups, interval=60, first=5)

    # Render free Web Service ko port pe response chahiye, warna spin-down/fail ho jata hai.
    # Ye background thread mein ek chhota HTTP server chalata hai jise UptimeRobot ping kar sake.
    threading.Thread(target=_run_health_server, daemon=True).start()

    print("Bot chal raha hai...")
    app.run_polling()


if __name__ == "__main__":
    main()
