import os
import logging
import threading
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

    step = user["onboarding_step"]
    lang = user["language"]
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


async def toggle_checklist_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_id = int(query.data.replace("toggle_", ""))

    current_markup = query.message.reply_markup
    new_buttons = []
    for row in current_markup.inline_keyboard:
        btn = row[0]
        if btn.callback_data == query.data:
            is_now_checked = btn.text.startswith("✅")
            new_completed = not is_now_checked
            db.toggle_plan_item(plan_id, new_completed, today_str=datetime.now().strftime("%Y-%m-%d"))
            check = "✅" if new_completed else "⬜"
            new_text = check + btn.text[1:]
            new_buttons.append([InlineKeyboardButton(new_text, callback_data=btn.callback_data)])
        else:
            new_buttons.append(row)

    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(new_buttons))


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

    msg = t("progress_header", lang, name=user["name"] or "", streak=streak_count, longest=longest)

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
    from question_extractor import extract_questions_from_text, generate_questions_pdf

    user_id = user["id"]
    lang = user["language"]
    context.user_data["awaiting_question_pdf"] = False

    await update.message.reply_text(t("extracting_in_progress", lang))

    in_path = f"/tmp/{user_id}_qsource.pdf"
    file = await update.message.document.get_file()
    await file.download_to_drive(in_path)

    full_text = ""
    with pdfplumber.open(in_path) as pdf:
        for page in pdf.pages:
            full_text += (page.extract_text() or "") + "\n"

    questions = extract_questions_from_text(full_text)

    if not questions:
        await update.message.reply_text(t("no_questions_found", lang))
        return

    out_path = f"/tmp/{user_id}_questions_output.pdf"
    generate_questions_pdf(questions, out_path, title="Extracted Questions")

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


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("progress", progress_command))
    app.add_handler(CommandHandler("extractquestions", extractquestions_command))
    app.add_handler(CallbackQueryHandler(language_chosen, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(exam_chosen, pattern="^exam_"))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(CallbackQueryHandler(toggle_checklist_item, pattern="^toggle_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Har minute check karo ki kisi user ka reminder time ab hua hai kya
    app.job_queue.run_repeating(send_morning_plan, interval=60, first=5)
    app.job_queue.run_repeating(send_evening_checklist, interval=60, first=5)

    # Render free Web Service ko port pe response chahiye, warna spin-down/fail ho jata hai.
    # Ye background thread mein ek chhota HTTP server chalata hai jise UptimeRobot ping kar sake.
    threading.Thread(target=_run_health_server, daemon=True).start()

    print("Bot chal raha hai...")
    app.run_polling()


if __name__ == "__main__":
    main()
