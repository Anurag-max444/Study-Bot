"""
Mock test logging — /addmocktest walks through every field the user wants
tracked; /mocktests shows the full list with a tap-for-full-detail button
per test, since a single list message showing all 15 fields for every test
would get unreadable fast once there are more than a few entries.
"""
from datetime import date

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import db
from ui.lang import t
from utils.formatting import esc
from utils.parsers import _parse_nonneg_int, _parse_nonneg_number
from utils.dates import _parse_test_date
from constants import MOCKTEST_TOTAL_STEPS, MOCKTEST_SKIP_WORDS


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


async def addmocktest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        from handlers.onboarding import start  # lazy: avoids a circular import with onboarding.py
        await start(update, context)
        return

    lang = user["language"]
    context.user_data["mocktest_flow"] = {"step": "platform"}
    await update.message.reply_text(t("mt_ask_platform", lang, n=1, total=MOCKTEST_TOTAL_STEPS))


async def mocktest_scope_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    flow = context.user_data.get("mocktest_flow")
    if not flow:
        return
    user = db.get_user(update.effective_user.id)
    if not user:
        await query.message.reply_text(t("stale_callback", "hinglish"))
        return
    lang = user["language"]

    if query.data == "mtscope_full":
        flow["scope"] = "Full Syllabus"
        flow["step"] = "duration"
        await query.edit_message_text(t("mt_ask_duration", lang, n=4, total=MOCKTEST_TOTAL_STEPS))
    elif query.data == "mtscope_skip":
        flow["scope"] = None
        flow["step"] = "duration"
        await query.edit_message_text(t("mt_ask_duration", lang, n=4, total=MOCKTEST_TOTAL_STEPS))
    else:
        flow["step"] = "scope_breadth"
        await query.edit_message_text(
            t("mt_ask_scope_breadth", lang, n=3, total=MOCKTEST_TOTAL_STEPS), reply_markup=_mt_breadth_keyboard()
        )


async def mocktest_breadth_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    flow = context.user_data.get("mocktest_flow")
    if not flow:
        return
    user = db.get_user(update.effective_user.id)
    if not user:
        await query.message.reply_text(t("stale_callback", "hinglish"))
        return
    lang = user["language"]

    if query.data == "mtbreadth_subject":
        flow["step"] = "scope_detail_subject"
        await query.edit_message_text(t("mt_ask_scope_detail_subject", lang, n=3, total=MOCKTEST_TOTAL_STEPS))
    elif query.data == "mtbreadth_skip":
        flow["scope"] = None
        flow["step"] = "duration"
        await query.edit_message_text(t("mt_ask_duration", lang, n=4, total=MOCKTEST_TOTAL_STEPS))
    else:
        flow["step"] = "scope_detail_chapters"
        await query.edit_message_text(t("mt_ask_scope_detail_chapters", lang, n=3, total=MOCKTEST_TOTAL_STEPS))


async def handle_mocktest_flow_text(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    lang = user["language"]
    text = update.message.text.strip()
    is_skip = text.lower() in MOCKTEST_SKIP_WORDS
    flow = context.user_data["mocktest_flow"]
    step = flow["step"]
    N = MOCKTEST_TOTAL_STEPS

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
        from handlers.onboarding import start  # lazy: avoids a circular import with onboarding.py
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
