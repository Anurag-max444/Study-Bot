"""Onboarding handlers — /start, language/exam selection callbacks, and the
text-message router that both progresses onboarding steps and dispatches to
other handlers' in-progress flows (task scheduling, mock test logging, vault
password entry)."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import db
from ui.lang import t
from data.default_syllabus import DEFAULT_SYLLABUS
from constants import EXAM_LABELS
from utils.formatting import esc
from utils.validators import _parse_hours
from keyboards.reply import main_menu_keyboard
from handlers.tasks import handle_task_flow_text
from handlers.mocktest import handle_mocktest_flow_text
from handlers.vault import vault_check_password


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


async def language_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    lang = query.data.replace("lang_", "")  # hindi / english / hinglish

    db.update_user(user_id, language=lang, onboarding_step="ask_name")
    await query.edit_message_text(t("ask_name", lang))


async def exam_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    if not user:
        await query.message.reply_text(t("stale_callback", "hinglish"))
        return
    exam = query.data.replace("exam_", "")  # ssc_cgl / jee_mains / custom

    # Default syllabus (if we have one for this exam) loads automatically —
    # no PDF upload step anymore, straight to the last onboarding question.
    db.update_user(user_id, exam=exam, onboarding_step="ask_hours")

    if exam in DEFAULT_SYLLABUS:
        for subject, topics in DEFAULT_SYLLABUS[exam].items():
            db.add_syllabus_topics(user_id, subject, topics)

    await query.edit_message_text(t("ask_hours", user["language"]))


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await vault_check_password(update, context):
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
