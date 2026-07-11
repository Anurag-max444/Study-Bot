import os
import html
import logging
import threading
import asyncio
from datetime import datetime, date, time as dtime, timedelta
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
import report_generator

# NOTE: Render pe env var TZ=Asia/Kolkata set karna, warna server UTC time use karega
# aur reminders galat time pe jayenge.

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# Personal vault (hidden feature — see near the bottom of this file for the
# commands themselves; deliberately not mentioned in /help, BotFather's
# command menu, or the persistent keyboard). Password-only by design so it
# works from any phone/any Telegram account, not just one fixed user.
VAULT_PASSWORD = os.environ.get("VAULT_PASSWORD", "PASS123")

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


def _parse_nonneg_int(text: str):
    """Parses a plain non-negative whole number. Returns None if invalid."""
    text = text.strip()
    if not text.isdigit():
        return None
    return int(text)


def _parse_nonneg_number(text: str):
    """Parses a non-negative whole or decimal number (e.g. total marks). Returns None if invalid."""
    text = text.strip().replace(",", ".")
    try:
        value = float(text)
    except ValueError:
        return None
    if value < 0:
        return None
    return value


def _parse_test_date(text: str):
    """Accepts 'aaj'/'today'/'aj' for today, or a DD-MM-YYYY / DD/MM/YYYY date.
    Returns a date object, or None if unparseable."""
    from datetime import date as _date

    text = text.strip().lower()
    if text in ("aaj", "today", "aj"):
        return _date.today()
    for sep in ("-", "/"):
        parts = text.split(sep)
        if len(parts) == 3:
            try:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                if year < 100:
                    year += 2000
                return _date(year, month, day)
            except ValueError:
                return None
    return None


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
            t("welcome", user["language"], name=esc(user["name"] or "dost")),
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        return

    db.create_user(user_id)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("हिंदी", callback_data="lang_hindi")],
        [InlineKeyboardButton("English", callback_data="lang_english")],
        [InlineKeyboardButton("Hinglish", callback_data="lang_hinglish")],
    ])
    await update.message.reply_text(t("ask_language", "hinglish"), reply_markup=keyboard, parse_mode="HTML")


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
    if await _vault_check_password(update, context):
        return

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

    # Mock test logging flow (triggered by /addmocktest) takes priority too
    if context.user_data.get("mocktest_flow"):
        await handle_mocktest_flow_text(update, context, user)
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
    await update.message.reply_text(
        t("welcome", lang, name=esc(user["name"] or "dost")), parse_mode="HTML"
    )


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

    progress_msg = await _show_progress(
        update.effective_chat.id, context, lang, t("tree_generating_label", lang), "upload_photo"
    )

    out_path = f"/tmp/{user_id}_tree.png"
    generate_tree_image(stage, wilted, out_path)

    stage_name = get_stage_name(stage, lang)
    bar = _progress_bar(min(growth_score, 60), 60)
    caption = t("tree_caption", lang, stage=stage_name, score=growth_score, bar=bar)
    if wilted:
        caption += "\n\n" + t("tree_wilted_warning", lang)

    with open(out_path, "rb") as f:
        await update.message.reply_photo(photo=f, caption=caption, parse_mode="HTML")

    try:
        await progress_msg.delete()
    except Exception:
        pass


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
    await update.message.reply_text(t("help_text", lang), parse_mode="HTML")


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


# ============================================================
# Mock test logging — /addmocktest walks through every field the user wants
# tracked; /mocktests shows the full list with a tap-for-full-detail button
# per test, since a single list message showing all 15 fields for every test
# would get unreadable fast once there are more than a few entries.
# ============================================================

def _mt_scope_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📘 Full Syllabus Test", callback_data="mtscope_full")],
        [InlineKeyboardButton("📗 Subject/Topic-specific", callback_data="mtscope_subject")],
        [InlineKeyboardButton("⏭ Skip", callback_data="mtscope_skip")],
    ])


def _mt_breadth_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 Pura Subject", callback_data="mtbreadth_subject")],
        [InlineKeyboardButton("📄 1-2 Chapters/Topics", callback_data="mtbreadth_chapters")],
        [InlineKeyboardButton("⏭ Skip", callback_data="mtbreadth_skip")],
    ])


_MT_TOTAL_STEPS = 16
_MT_SKIP_WORDS = ("skip", "none", "na", "n/a", "-")


async def addmocktest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    context.user_data["mocktest_flow"] = {"step": "platform"}
    await update.message.reply_text(t("mt_ask_platform", lang, n=1, total=_MT_TOTAL_STEPS))


async def mocktest_scope_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    flow = context.user_data.get("mocktest_flow")
    if not flow:
        return
    user = db.get_user(update.effective_user.id)
    lang = user["language"]

    if query.data == "mtscope_full":
        flow["scope"] = "Full Syllabus"
        flow["step"] = "duration"
        await query.edit_message_text(t("mt_ask_duration", lang, n=4, total=_MT_TOTAL_STEPS))
    elif query.data == "mtscope_skip":
        flow["scope"] = None
        flow["step"] = "duration"
        await query.edit_message_text(t("mt_ask_duration", lang, n=4, total=_MT_TOTAL_STEPS))
    else:
        flow["step"] = "scope_breadth"
        await query.edit_message_text(
            t("mt_ask_scope_breadth", lang, n=3, total=_MT_TOTAL_STEPS), reply_markup=_mt_breadth_keyboard()
        )


async def mocktest_breadth_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    flow = context.user_data.get("mocktest_flow")
    if not flow:
        return
    user = db.get_user(update.effective_user.id)
    lang = user["language"]

    if query.data == "mtbreadth_subject":
        flow["step"] = "scope_detail_subject"
        await query.edit_message_text(t("mt_ask_scope_detail_subject", lang, n=3, total=_MT_TOTAL_STEPS))
    elif query.data == "mtbreadth_skip":
        flow["scope"] = None
        flow["step"] = "duration"
        await query.edit_message_text(t("mt_ask_duration", lang, n=4, total=_MT_TOTAL_STEPS))
    else:
        flow["step"] = "scope_detail_chapters"
        await query.edit_message_text(t("mt_ask_scope_detail_chapters", lang, n=3, total=_MT_TOTAL_STEPS))


async def handle_mocktest_flow_text(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    lang = user["language"]
    text = update.message.text.strip()
    is_skip = text.lower() in _MT_SKIP_WORDS
    flow = context.user_data["mocktest_flow"]
    step = flow["step"]
    N = _MT_TOTAL_STEPS

    if step == "platform":
        if is_skip:
            flow["platform"] = None
        elif not text or len(text) > 60:
            await update.message.reply_text(t("mt_invalid_text", lang))
            return
        else:
            flow["platform"] = text
        flow["step"] = "scope_type"
        await update.message.reply_text(t("mt_ask_scope_type", lang, n=2, total=N), reply_markup=_mt_scope_keyboard())
        return

    if step == "scope_type":
        if is_skip:
            flow["scope"] = None
            flow["step"] = "duration"
            await update.message.reply_text(t("mt_ask_duration", lang, n=4, total=N))
        else:
            await update.message.reply_text(t("mt_ask_scope_type", lang, n=2, total=N), reply_markup=_mt_scope_keyboard())
        return

    if step == "scope_breadth":
        if is_skip:
            flow["scope"] = None
            flow["step"] = "duration"
            await update.message.reply_text(t("mt_ask_duration", lang, n=4, total=N))
        else:
            await update.message.reply_text(t("mt_ask_scope_breadth", lang, n=3, total=N), reply_markup=_mt_breadth_keyboard())
        return

    if step in ("scope_detail_subject", "scope_detail_chapters"):
        if is_skip:
            flow["scope"] = None
        elif not text or len(text) > 200:
            await update.message.reply_text(t("mt_invalid_text", lang))
            return
        else:
            prefix = "Subject" if step == "scope_detail_subject" else "Chapters/Topics"
            flow["scope"] = f"{prefix}: {text}"
        flow["step"] = "duration"
        await update.message.reply_text(t("mt_ask_duration", lang, n=4, total=N))
        return

    if step == "duration":
        if is_skip:
            flow["duration_minutes"] = None
        else:
            minutes = _parse_nonneg_int(text)
            if not minutes:
                await update.message.reply_text(t("mt_invalid_number", lang))
                return
            flow["duration_minutes"] = minutes
        flow["step"] = "total_questions"
        await update.message.reply_text(t("mt_ask_total_questions", lang, n=5, total=N))
        return

    if step == "total_questions":
        if is_skip:
            flow["total_questions"] = None
        else:
            qs = _parse_nonneg_int(text)
            if not qs:
                await update.message.reply_text(t("mt_invalid_number", lang))
                return
            flow["total_questions"] = qs
        flow["step"] = "total_marks"
        await update.message.reply_text(t("mt_ask_total_marks", lang, n=6, total=N))
        return

    if step == "total_marks":
        if is_skip:
            flow["total_marks"] = None
        else:
            marks = _parse_nonneg_number(text)
            if marks is None:
                await update.message.reply_text(t("mt_invalid_number", lang))
                return
            flow["total_marks"] = marks
        flow["step"] = "negative_marking"
        await update.message.reply_text(t("mt_ask_negative_marking", lang, n=7, total=N))
        return

    if step == "negative_marking":
        flow["negative_marking"] = None if is_skip else text
        flow["step"] = "attempted"
        await update.message.reply_text(t("mt_ask_attempted", lang, n=8, total=N))
        return

    if step == "attempted":
        if is_skip:
            flow["attempted"] = None
        else:
            attempted = _parse_nonneg_int(text)
            total_q = flow.get("total_questions")
            if attempted is None or (total_q is not None and attempted > total_q):
                await update.message.reply_text(t("mt_invalid_attempted", lang, total=total_q if total_q is not None else "?"))
                return
            flow["attempted"] = attempted
        flow["step"] = "wrong"
        await update.message.reply_text(t("mt_ask_wrong", lang, n=9, total=N))
        return

    if step == "wrong":
        if is_skip:
            flow["wrong"] = None
        else:
            wrong = _parse_nonneg_int(text)
            attempted = flow.get("attempted")
            if wrong is None or (attempted is not None and wrong > attempted):
                await update.message.reply_text(t("mt_invalid_wrong", lang, attempted=attempted if attempted is not None else "?"))
                return
            flow["wrong"] = wrong
        flow["step"] = "skipped"
        await update.message.reply_text(t("mt_ask_skipped", lang, n=10, total=N))
        return

    if step == "skipped":
        if is_skip:
            flow["skipped"] = None
        else:
            skipped = _parse_nonneg_int(text)
            if skipped is None:
                await update.message.reply_text(t("mt_invalid_number", lang))
                return
            flow["skipped"] = skipped
        flow["step"] = "percentile"
        await update.message.reply_text(t("mt_ask_percentile", lang, n=11, total=N))
        return

    if step == "percentile":
        if is_skip:
            flow["percentile"] = None
        else:
            pct = _parse_nonneg_number(text)
            if pct is None or pct > 100:
                await update.message.reply_text(t("mt_invalid_percentile", lang))
                return
            flow["percentile"] = pct
        flow["step"] = "rank"
        await update.message.reply_text(t("mt_ask_rank", lang, n=12, total=N))
        return

    if step == "rank":
        if is_skip:
            flow["rank"] = None
        else:
            rank = _parse_nonneg_int(text)
            if rank is None:
                await update.message.reply_text(t("mt_invalid_number", lang))
                return
            flow["rank"] = rank
        flow["step"] = "weak_topics"
        await update.message.reply_text(t("mt_ask_weak_topics", lang, n=13, total=N))
        return

    if step == "weak_topics":
        flow["weak_topics"] = None if is_skip else text
        flow["step"] = "average_topics"
        await update.message.reply_text(t("mt_ask_average_topics", lang, n=14, total=N))
        return

    if step == "average_topics":
        flow["average_topics"] = None if is_skip else text
        flow["step"] = "strong_topics"
        await update.message.reply_text(t("mt_ask_strong_topics", lang, n=15, total=N))
        return

    if step == "strong_topics":
        flow["strong_topics"] = None if is_skip else text
        flow["step"] = "test_date"
        await update.message.reply_text(t("mt_ask_test_date", lang, n=16, total=N))
        return

    if step == "test_date":
        test_date = date.today() if is_skip else _parse_test_date(text)
        if not test_date:
            await update.message.reply_text(t("mt_invalid_test_date", lang))
            return

        row = db.add_mock_test(
            user["id"],
            test_date=test_date, platform=flow.get("platform"), scope=flow.get("scope"),
            duration_minutes=flow.get("duration_minutes"), total_questions=flow.get("total_questions"),
            total_marks=flow.get("total_marks"), negative_marking=flow.get("negative_marking"),
            attempted=flow.get("attempted"), wrong=flow.get("wrong"), skipped=flow.get("skipped"),
            percentile=flow.get("percentile"), rank=flow.get("rank"), weak_topics=flow.get("weak_topics"),
            average_topics=flow.get("average_topics"), strong_topics=flow.get("strong_topics"),
        )
        del context.user_data["mocktest_flow"]

        await update.message.reply_text(t("mt_saved", lang), parse_mode="HTML")
        await update.message.reply_text(_mt_format_detail(row, lang), parse_mode="HTML")
        return


def _mt_or_dash(value):
    return "—" if value is None else value


def _mt_format_detail(row: dict, lang: str) -> str:
    correct = row["attempted"] - row["wrong"] if row["attempted"] is not None and row["wrong"] is not None else None
    return t(
        "mt_detail_block", lang,
        date=row["test_date"], platform=esc(row["platform"] or "—"), scope=esc(row["scope"] or "—"),
        duration=_mt_or_dash(row["duration_minutes"]), total_q=_mt_or_dash(row["total_questions"]),
        total_marks=_mt_or_dash(row["total_marks"]), negative=esc(row["negative_marking"] or "—"),
        attempted=_mt_or_dash(row["attempted"]), correct=_mt_or_dash(correct),
        wrong=_mt_or_dash(row["wrong"]), skipped=_mt_or_dash(row["skipped"]),
        percentile=_mt_or_dash(row["percentile"]), rank=_mt_or_dash(row["rank"]),
        weak=esc(row["weak_topics"] or "—"), average=esc(row["average_topics"] or "—"),
        strong=esc(row["strong_topics"] or "—"),
    )


async def mocktests_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    tests = db.get_mock_tests(user_id)
    if not tests:
        await update.message.reply_text(t("mt_list_empty", lang))
        return

    msg = t("mt_list_header", lang, count=len(tests))
    for i, row in enumerate(tests, start=1):
        correct = row["attempted"] - row["wrong"] if row["attempted"] is not None and row["wrong"] is not None else None
        pct_str = f" • %ile {row['percentile']}" if row["percentile"] is not None else ""
        msg += (
            f"\n{i}. 📅 {row['test_date']} • {esc(row['platform'] or '—')} • {esc(row['scope'] or '—')}\n"
            f"   ✅{_mt_or_dash(correct)}/❌{_mt_or_dash(row['wrong'])}/⏭{_mt_or_dash(row['skipped'])}{pct_str}"
        )

    # Chunk into multiple messages if the list is long (Telegram's ~4096 char limit)
    # and attach a "🔍 view details" button per test, in batches of 20 buttons.
    chunks = [msg[i:i + 3500] for i in range(0, len(msg), 3500)] if len(msg) > 3500 else [msg]
    for chunk in chunks:
        await update.message.reply_text(chunk, parse_mode="HTML")

    for i in range(0, len(tests), 20):
        batch = tests[i:i + 20]
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"🔍 #{i + j + 1}", callback_data=f"mtdetail_{row['id']}")]
             for j, row in enumerate(batch)]
        )
        await update.message.reply_text(t("mt_tap_hint", lang), reply_markup=keyboard)


async def mocktest_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    lang = user["language"] if user else "hinglish"

    test_id = int(query.data.replace("mtdetail_", ""))
    row = db.get_mock_test(test_id, user_id)
    if not row:
        return
    await query.message.reply_text(_mt_format_detail(row, lang), parse_mode="HTML")


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


def _daily_minutes_last_7_days(user_id: int):
    """Returns a 7-int list of completed study minutes per day, oldest -> today."""
    from datetime import date, timedelta

    sessions = db.get_study_log(user_id, days=7)
    today = date.today()
    by_date = {(today - timedelta(days=i)).isoformat(): 0 for i in range(7)}
    for s in sessions:
        if s["completed"] and s["session_date"] in by_date:
            by_date[s["session_date"]] += s["duration_minutes"]
    ordered_dates = sorted(by_date.keys())
    return [by_date[d] for d in ordered_dates]


async def _build_and_send_report(bot, chat_id: int, user: dict):
    """Builds the weekly PDF report card for one user and sends it. Raises on
    failure so the caller (job or command) can decide how to handle/log it."""
    import tempfile

    lang = user["language"]
    daily_minutes = _daily_minutes_last_7_days(user["id"])
    streak = db.get_streak(user["id"])
    streak_count = streak["current_streak"] if streak else 0
    longest = streak["longest_streak"] if streak else 0
    sessions_done = sum(1 for m in daily_minutes if m > 0)
    badge_count = len(db.get_user_badges(user["id"]))
    total_badges = len(db.BADGES)

    with tempfile.TemporaryDirectory() as tmp_dir:
        pdf_path = os.path.join(tmp_dir, f"report_{user['id']}.pdf")
        report_generator.generate_weekly_report_pdf(
            name=user["name"] or "dost", lang=lang, daily_minutes=daily_minutes,
            streak=streak_count, longest_streak=longest, sessions_done=sessions_done,
            badge_count=badge_count, total_badges=total_badges, output_path=pdf_path,
        )
        with open(pdf_path, "rb") as f:
            await bot.send_document(
                chat_id,
                document=f,
                filename="weekly_report.pdf",
                caption=t("report_ready_caption", lang, name=esc(user["name"] or "")),
                parse_mode="HTML",
            )


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        await start(update, context)
        return

    lang = user["language"]
    chat_id = update.effective_chat.id
    progress_msg = await _show_progress(chat_id, context, lang, t("report_generating_label", lang), "upload_document")
    try:
        await _build_and_send_report(context.bot, chat_id, user)
    except Exception:
        logging.exception("Failed to build/send weekly report for user %s", user_id)
        await update.message.reply_text(t("report_failed", lang))
    finally:
        try:
            await progress_msg.delete()
        except Exception:
            pass


async def send_weekly_reports_job(context: ContextTypes.DEFAULT_TYPE):
    """Runs automatically every Sunday night — sends every onboarded user their
    weekly report card. One user's failure never blocks the rest of the batch."""
    for user in db.get_all_onboarded_users():
        try:
            await _build_and_send_report(context.bot, user["id"], user)
        except Exception:
            logging.exception("Weekly report broadcast failed for user %s", user["id"])


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


# ============================================================
# Personal vault — hidden feature, password-only access (works from any
# phone/any Telegram account — not tied to a specific user ID on purpose).
# Not registered anywhere visible: no /help entry, no BotFather command-menu
# entry, no persistent-keyboard button.
#
# Because a shared password is now the ONLY gate (by design), a simple
# brute-force lockout is included: 5 wrong attempts in a row locks the vault
# for 15 minutes. The image bytes are never stored on disk — only Telegram's
# own file_id is kept in the database, so it survives restarts/redeploys on
# any host.
# ============================================================
_VAULT_VIEW_COMMAND = "admin"
_VAULT_SAVE_COMMAND = "admins"
_VAULT_MAX_ATTEMPTS = 5
_VAULT_LOCKOUT_MINUTES = 15


def _vault_locked(context: ContextTypes.DEFAULT_TYPE) -> bool:
    locked_until = context.bot_data.get("vault_locked_until")
    return bool(locked_until and datetime.now() < locked_until)


def _vault_register_failure(context: ContextTypes.DEFAULT_TYPE):
    attempts = context.bot_data.get("vault_failed_attempts", 0) + 1
    context.bot_data["vault_failed_attempts"] = attempts
    if attempts >= _VAULT_MAX_ATTEMPTS:
        context.bot_data["vault_locked_until"] = datetime.now() + timedelta(minutes=_VAULT_LOCKOUT_MINUTES)
        context.bot_data["vault_failed_attempts"] = 0


def _vault_register_success(context: ContextTypes.DEFAULT_TYPE):
    context.bot_data["vault_failed_attempts"] = 0
    context.bot_data.pop("vault_locked_until", None)


async def _vault_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if _vault_locked(context):
        await update.message.reply_text("⏳")
        return
    context.user_data["awaiting_vault_password"] = "view"
    await update.message.reply_text("Password?")


async def _vault_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if _vault_locked(context):
        await update.message.reply_text("⏳")
        return
    context.user_data["awaiting_vault_password"] = "save"
    await update.message.reply_text("Password?")


async def _vault_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_vault_photo"):
        return  # not in save-mode — behave as if this bot has no photo handler at all
    context.user_data["awaiting_vault_photo"] = False
    file_id = update.message.photo[-1].file_id
    db.add_vault_image(file_id)
    await update.message.reply_text(f"✅ Saved. Aur bhejni hai to phir /{_VAULT_SAVE_COMMAND} use karo.")


async def _vault_show_all(update_or_query, context: ContextTypes.DEFAULT_TYPE, send_photo_fn):
    images = db.get_vault_images()
    if not images:
        await send_photo_fn(text_only="Khaali hai.")
        return
    for i, img in enumerate(images, start=1):
        when = img.get("created_at", "")[:10]
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🗑 Delete", callback_data=f"vaultdel_{img['id']}")]]
        )
        await send_photo_fn(file_id=img["file_id"], caption=f"#{i} • {when}", keyboard=keyboard)


async def _vault_check_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Returns True if this text message was consumed as a vault-password attempt
    (so the caller should stop processing it as normal chat text)."""
    mode = context.user_data.get("awaiting_vault_password")
    if not mode:
        return False
    context.user_data["awaiting_vault_password"] = None

    if _vault_locked(context):
        await update.message.reply_text("⏳")
        return True

    if update.message.text.strip() != VAULT_PASSWORD:
        _vault_register_failure(context)
        await update.message.reply_text("❌")
        return True

    _vault_register_success(context)

    if mode == "save":
        context.user_data["awaiting_vault_photo"] = True
        await update.message.reply_text("Bhejo.")
    else:  # mode == "view"
        async def _send(text_only=None, file_id=None, caption=None, keyboard=None):
            if text_only:
                await update.message.reply_text(text_only)
            else:
                await update.message.reply_photo(file_id, caption=caption, reply_markup=keyboard)

        await _vault_show_all(update, context, _send)

    return True


async def _vault_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    image_id = int(query.data.replace("vaultdel_", ""))
    db.delete_vault_image(image_id)
    await query.answer("Deleted")
    try:
        await query.message.delete()
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
    app.add_handler(CommandHandler("report", report_command))
    app.add_handler(CommandHandler("addmocktest", addmocktest_command))
    app.add_handler(CommandHandler("mocktests", mocktests_command))
    app.add_handler(CommandHandler(_VAULT_VIEW_COMMAND, _vault_view))
    app.add_handler(CommandHandler(_VAULT_SAVE_COMMAND, _vault_save))
    app.add_handler(CallbackQueryHandler(language_chosen, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(exam_chosen, pattern="^exam_"))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.PHOTO, _vault_photo_handler))
    app.add_handler(CallbackQueryHandler(mark_session_done, pattern="^sessiondone_"))
    app.add_handler(CallbackQueryHandler(mark_revision_done, pattern="^revdone_"))
    app.add_handler(CallbackQueryHandler(badge_info, pattern="^badgeinfo_"))
    app.add_handler(CallbackQueryHandler(_vault_delete_callback, pattern="^vaultdel_"))
    app.add_handler(CallbackQueryHandler(mocktest_scope_chosen, pattern="^mtscope_"))
    app.add_handler(CallbackQueryHandler(mocktest_breadth_chosen, pattern="^mtbreadth_"))
    app.add_handler(CallbackQueryHandler(mocktest_detail_callback, pattern="^mtdetail_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(global_error_handler)

    app.job_queue.run_repeating(send_custom_task_start, interval=60, first=5)
    app.job_queue.run_repeating(check_due_followups, interval=60, first=5)
    app.job_queue.run_repeating(send_due_revisions, interval=60, first=5)
    # Sunday night, 9 PM server time (see the TZ note near the top of this file)
    app.job_queue.run_daily(send_weekly_reports_job, time=dtime(hour=21, minute=0), days=(6,))

    # Render free Web Service ko port pe response chahiye, warna spin-down/fail ho jata hai.
    # Ye background thread mein ek chhota HTTP server chalata hai jise UptimeRobot ping kar sake.
    threading.Thread(target=_run_health_server, daemon=True).start()

    print("Bot chal raha hai...")
    app.run_polling()


if __name__ == "__main__":
    main()
