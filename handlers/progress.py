"""Progress handlers — /progress, /badges (+ tap-for-detail popup), /mytree."""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import db
from ui.lang import t
from utils.formatting import esc, _progress_bar
from utils.progress_ui import _show_progress


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user or user["onboarding_step"] != "done":
        from handlers.onboarding import start
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
        from handlers.onboarding import start
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
    from ui.tree_generator import generate_tree_image, get_stage, get_stage_name

    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        from handlers.onboarding import start
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
