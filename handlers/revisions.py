"""Revision handlers — /revisions list, and the 'mark revision done' callback."""
from telegram import Update
from telegram.ext import ContextTypes

import db
from ui.lang import t
from utils.formatting import esc
from services import revision_service


async def revisions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        from handlers.onboarding import start
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


async def mark_revision_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = db.get_user(user_id)
    if not user:
        await query.message.reply_text(t("stale_callback", "hinglish"))
        return

    revision_id = int(query.data.replace("revdone_", ""))

    await query.edit_message_text(query.message.text + "\n\n✅")
    await revision_service.complete_revision(context.bot, revision_id, user)
