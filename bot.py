import os
import html
import logging
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

# NOTE: load_dotenv() must run BEFORE `import db`, because db.py reads
# SUPABASE_URL/SUPABASE_KEY at module import time (top-level create_client call).
# If db is imported first, those env vars are still unset -> crash.
load_dotenv()

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters,
)

import db
from lang import t
from default_syllabus import DEFAULT_SYLLABUS

# NOTE: Render pe env var TZ=Asia/Kolkata set karna, warna server UTC time use karega
# aur reminders galat time pe jayenge.

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

EXAM_LABELS = {"ssc_cgl": "SSC CGL", "jee_mains": "JEE Mains", "custom": "Custom / Other"}


def esc(value) -> str:
    """Escapes user-provided text before it goes into an HTML-parse-mode message,
    so a stray '<', '>' or '&' in someone's name/topic can never break the message
    or get rendered as a tag."""
    return html.escape(str(value))


def _progress_bar(value: float, total: float, length: int = 10) -> str:
    """Renders a simple block progress bar, e.g. '███████░░░'. Safe against total=0."""
    pct = 0 if not total else max(0, min(1, value / total))
    filled = round(pct * length)
    return "█" * filled + "░" * (length - filled)


def _parse_hours(text: str):
    """Parses daily-study-hours input. Accepts whole or decimal numbers (e.g. '4', '3.5').
    Returns a float in a sane 0.5–18 range, or None if invalid."""
    text = text.strip().replace(",", ".")
    try:
        hours = float(text)
    except ValueError:
        return None
    if hours < 0.5 or hours > 18:
        return None
    return round(hours, 1)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Persistent bottom menu with the 4 most-used commands. The button text is the
    literal command string, so Telegram routes a tap straight to the matching
    CommandHandler — no extra routing logic needed."""
    return ReplyKeyboardMarkup(
        [["/addtask", "/mytopics"], ["/mytree", "/help"]],
        resize_keyboard=True,
    )


# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)

    if user:
        keyboard = main_menu_keyboard() if user["onboarding_step"] == "done" else None
        await update.message.reply_text(
            t("welcome", user["language"], name=user["name"] or "dost"),
            reply_markup=keyboard,
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

    # Default syllabus (if we have one for this exam) loads automatically —
    # no PDF upload step anymore, straight to the last onboarding question.
    db.update_user(user_id, exam=exam, onboarding_step="ask_hours")

    if exam in DEFAULT_SYLLABUS:
        for subject, topics in DEFAULT_SYLLABUS[exam].items():
            db.add_syllabus_topics(user_id, subject, topics)

    await query.edit_message_text(t("ask_hours", user["language"]))


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
        # Name validation: non-empty, reasonable length, not a stray command.
        if not text or len(text) > 40 or text.startswith("/"):
            await update.message.reply_text(t("invalid_name", lang))
            return

        db.update_user(user_id, name=text, onboarding_step="ask_exam")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("SSC CGL", callback_data="exam_ssc_cgl")],
            [InlineKeyboardButton("JEE Mains", callback_data="exam_jee_mains")],
            [InlineKeyboardButton("Custom / Other", callback_data="exam_custom")],
        ])
        await update.message.reply_text(t("ask_exam", lang), reply_markup=keyboard)
        return

    # Legacy fallback: anyone whose account is still stuck on the old
    # (now removed) syllabus-PDF step gets auto-advanced instead of stalling.
    if step == "ask_syllabus_pdf":
        db.update_user(user_id, onboarding_step="ask_hours")
        await update.message.reply_text(t("ask_hours", lang))
        return

    if step == "ask_hours":
        hours = _parse_hours(text)
        if hours is None:
            await update.message.reply_text(t("invalid_hours", lang))
            return

        db.update_user(user_id, daily_hours=hours, onboarding_step="done")
        exam_label = EXAM_LABELS.get(user["exam"], user["exam"] or "-")
        await update.message.reply_text(
            t("setup_done", lang, name=esc(user["name"] or ""), exam=exam_label, hours=hours),
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
        return

    # Default fallback once onboarding is done
    await update.message.reply_text(t("welcome", lang, name=user["name"] or "dost"))


# ---------- PDF upload handler (question extraction, via /extractquestions or /pdf) ----------
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        return

    # Question-extraction flow (triggered via /extractquestions or /pdf)
    if context.user_data.get("awaiting_question_pdf"):
        await handle_question_pdf(update, context, user)
        return

    # No other feature currently expects a PDF upload — quietly ignore it
    # instead of doing nothing with zero feedback.
    await update.message.reply_text(t("ask_question_pdf", user["language"]))


async def _notify_gamification(context: ContextTypes.DEFAULT_TYPE, user_id: int, lang: str, shield_used: bool, newly_badges: list):
    """Sends shield-used and new-badge notifications after any completion event."""
    if shield_used:
        streak = db.get_streak(user_id)
        remaining = streak["shields_available"] if streak else 0
        await context.bot.send_message(
            user_id, t("shield_used_notification", lang, remaining=remaining), parse_mode="HTML"
        )

    for badge_name in newly_badges:
        await context.bot.send_message(
            user_id, t("badge_earned_notification", lang, badge_name=badge_name), parse_mode="HTML"
        )


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

    total_badges = len(db.BADGES)
    badge_count = len(db.get_user_badges(user_id))
    shields_visual = "🛡️" * shields + "▫️" * (3 - shields)
    badges_bar = _progress_bar(badge_count, total_badges)

    msg = t("progress_header", lang, name=esc(user["name"] or ""), streak=streak_count, longest=longest)
    msg += t("shields_line", lang, shields_visual=shields_visual, shields=shields)
    msg += t("badges_summary_line", lang, bar=badges_bar, count=badge_count, total=total_badges)

    await update.message.reply_text(msg, parse_mode="HTML")


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
    msg += t("badges_tap_hint", lang)

    items = list(db.BADGES.items())
    rows = []
    for i in range(0, len(items), 2):
        row = []
        for code, meta in items[i:i + 2]:
            mark = "✅" if code in earned_codes else "🔒"
            row.append(InlineKeyboardButton(f"{mark} {meta['name']}", callback_data=f"badgeinfo_{code}"))
        rows.append(row)

    await update.message.reply_text(msg, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(rows))


async def badge_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tapping a badge in the /badges grid shows its unlock condition as a popup,
    without editing or cluttering the message itself."""
    query = update.callback_query
    user_id = query.from_user.id
    user = db.get_user(user_id)
    lang = user["language"] if user else "hinglish"

    code = query.data.replace("badgeinfo_", "")
    meta = db.BADGES.get(code)
    if not meta:
        await query.answer()
        return

    earned_codes = {b["badge_code"] for b in db.get_user_badges(user_id)} if user else set()
    hint = t(f"badge_hint_{code}", lang)

    if code in earned_codes:
        popup = t("badge_unlocked_popup", lang, name=meta["name"], hint=hint)
    else:
        popup = t("badge_locked_popup", lang, name=meta["name"], hint=hint)

    await query.answer(text=popup, show_alert=True)


async def mytree_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from tree_generator import generate_tree_image, get_stage, get_stage_name

    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    growth_score = db.get_tree_growth_score(user_id)
    stage = get_stage(growth_score)
    days_inactive = db.get_days_since_active(user_id)
    wilted = bool(days_inactive is not None and days_inactive >= 2)

    out_path = f"/tmp/{user_id}_tree.png"
    generate_tree_image(stage, wilted, out_path)

    stage_name = get_stage_name(stage, lang)
    bar = _progress_bar(min(growth_score, 60), 60)
    caption = t("tree_caption", lang, stage=stage_name, score=growth_score, bar=bar)
    if wilted:
        caption += "\n\n" + t("tree_wilted_warning", lang)

    with open(out_path, "rb") as f:
        await update.message.reply_photo(photo=f, caption=caption, parse_mode="HTML")


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
        msg += f"{mark} {esc(s['session_date'])} — <b>{esc(s['topic_snapshot'])}</b> ({s['duration_minutes']} min)\n"
        if s["completed"]:
            total_minutes += s["duration_minutes"]

    msg += t("studylog_total", lang, hours=round(total_minutes / 60, 1))
    await update.message.reply_text(msg, parse_mode="HTML")


async def send_custom_task_start(context: ContextTypes.DEFAULT_TYPE):
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

            await context.bot.send_message(
                user["id"],
                t(
                    "task_session_start", lang,
                    name=esc(user["name"] or ""), topic=esc(row["topic"]),
                    duration=row["duration_minutes"],
                ),
                parse_mode="HTML",
            )
            # Follow-up ka time database me save ho gaya hai (create_task_session ke andar) —
            # ab yeh check_due_followups job khud uthayega, chahe bot beech me restart bhi ho jaye.
        except Exception:
            logging.exception(f"send_custom_task_start failed for custom_task {row.get('id')}")


async def check_due_followups(context: ContextTypes.DEFAULT_TYPE):
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
            await context.bot.send_message(
                user["id"],
                t("task_session_followup", lang, topic=esc(session["topic_snapshot"])),
                reply_markup=keyboard,
                parse_mode="HTML",
            )
            db.mark_followup_sent(session["id"])
        except Exception:
            logging.exception(f"check_due_followups failed for session {session.get('id')}")


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


async def global_error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Catches any unhandled exception anywhere in the bot so nothing fails silently."""
    logging.error("Unhandled exception while processing update:", exc_info=context.error)


async def revisions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    pending = db.get_pending_revisions(user_id)
    if not pending:
        await update.message.reply_text(t("revisions_empty", lang))
        return

    msg = t("revisions_header", lang)
    for r in pending:
        if r.get("syllabus"):
            label = f"{esc(r['syllabus']['subject'])}: {esc(r['syllabus']['topic'])}"
        else:
            label = esc(r.get("topic_text") or "—")
        msg += f"\n📅 {r['due_date']} ({r['interval_label']}) — <b>{label}</b>"

    await update.message.reply_text(msg, parse_mode="HTML")


async def send_due_revisions(context: ContextTypes.DEFAULT_TYPE):
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
            await context.bot.send_message(
                user["id"],
                t("revision_due_message", lang, interval=rev["interval_label"], topic=label),
                reply_markup=keyboard,
                parse_mode="HTML",
            )
            db.mark_revision_notified(rev["id"])
        except Exception:
            logging.exception(f"send_due_revisions failed for revision {rev.get('id')}")


async def mark_revision_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    lang = user["language"] if user else "hinglish"

    revision_id = int(query.data.replace("revdone_", ""))
    db.mark_revision_completed(revision_id)

    await query.edit_message_text(query.message.text + "\n\n✅")
    await context.bot.send_message(user_id, t("revision_marked_done", lang))


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


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("progress", progress_command))
    app.add_handler(CommandHandler("badges", badges_command))
    app.add_handler(CommandHandler("mytree", mytree_command))
    app.add_handler(CommandHandler("revisions", revisions_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("extractquestions", extractquestions_command))
    app.add_handler(CommandHandler("pdf", extractquestions_command))
    app.add_handler(CommandHandler("addtask", addtask_command))
    app.add_handler(CommandHandler("mytopics", mytopics_command))
    app.add_handler(CommandHandler("removetask", removetask_command))
    app.add_handler(CommandHandler("studylog", studylog_command))
    app.add_handler(CallbackQueryHandler(language_chosen, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(exam_chosen, pattern="^exam_"))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(CallbackQueryHandler(mark_session_done, pattern="^sessiondone_"))
    app.add_handler(CallbackQueryHandler(mark_revision_done, pattern="^revdone_"))
    app.add_handler(CallbackQueryHandler(badge_info, pattern="^badgeinfo_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(global_error_handler)

    app.job_queue.run_repeating(send_custom_task_start, interval=60, first=5)
    app.job_queue.run_repeating(check_due_followups, interval=60, first=5)
    app.job_queue.run_repeating(send_due_revisions, interval=60, first=5)

    # Render free Web Service ko port pe response chahiye, warna spin-down/fail ho jata hai.
    # Ye background thread mein ek chhota HTTP server chalata hai jise UptimeRobot ping kar sake.
    threading.Thread(target=_run_health_server, daemon=True).start()

    print("Bot chal raha hai...")
    app.run_polling()


if __name__ == "__main__":
    main()
