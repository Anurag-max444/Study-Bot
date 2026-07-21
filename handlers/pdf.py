"""PDF handlers — /extractquestions (or /pdf), and the document-upload flow
that extracts MCQ questions from a practice-paper PDF."""
import logging

from telegram import Update
from telegram.ext import ContextTypes

import db
from ui.lang import t


async def extractquestions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    if not user:
        from handlers.onboarding import start
        await start(update, context)
        return

    lang = user["language"]
    context.user_data["awaiting_question_pdf"] = True
    await update.message.reply_text(t("ask_question_pdf", lang))


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


async def handle_question_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE, user):
    import pdfplumber
    from telegram.error import BadRequest
    from services.pdf_service import extract_questions_from_text, generate_questions_pdf

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
