"""
Personal vault — hidden feature, password-only access (works from any
phone/any Telegram account — not tied to a specific user ID on purpose).
Not registered anywhere visible: no /help entry, no BotFather command-menu
entry, no persistent-keyboard button.

Because a shared password is the ONLY gate (by design), a simple
brute-force lockout is included: 5 wrong attempts in a row locks the vault
for 15 minutes. The image bytes are never stored on disk — only Telegram's
own file_id is kept in the database, so it survives restarts/redeploys on
any host.
"""
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import db
import config
from constants import VAULT_VIEW_COMMAND, VAULT_SAVE_COMMAND, VAULT_MAX_ATTEMPTS, VAULT_LOCKOUT_MINUTES

VAULT_PASSWORD = config.VAULT_PASSWORD


def _vault_locked(context: ContextTypes.DEFAULT_TYPE) -> bool:
    locked_until = context.bot_data.get("vault_locked_until")
    return bool(locked_until and datetime.now() < locked_until)


def _vault_register_failure(context: ContextTypes.DEFAULT_TYPE):
    attempts = context.bot_data.get("vault_failed_attempts", 0) + 1
    context.bot_data["vault_failed_attempts"] = attempts
    if attempts >= VAULT_MAX_ATTEMPTS:
        context.bot_data["vault_locked_until"] = datetime.now() + timedelta(minutes=VAULT_LOCKOUT_MINUTES)
        context.bot_data["vault_failed_attempts"] = 0


def _vault_register_success(context: ContextTypes.DEFAULT_TYPE):
    context.bot_data["vault_failed_attempts"] = 0
    context.bot_data.pop("vault_locked_until", None)


async def vault_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if _vault_locked(context):
        await update.message.reply_text("⏳")
        return
    context.user_data["awaiting_vault_password"] = "view"
    await update.message.reply_text("Password?")


async def vault_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if _vault_locked(context):
        await update.message.reply_text("⏳")
        return
    context.user_data["awaiting_vault_password"] = "save"
    await update.message.reply_text("Password?")


async def vault_photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_vault_photo"):
        return  # not in save-mode — behave as if this bot has no photo handler at all
    context.user_data["awaiting_vault_photo"] = False
    file_id = update.message.photo[-1].file_id
    db.add_vault_image(file_id)
    await update.message.reply_text(f"✅ Saved. Aur bhejni hai to phir /{VAULT_SAVE_COMMAND} use karo.")


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


async def vault_check_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
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


async def vault_delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    image_id = int(query.data.replace("vaultdel_", ""))
    db.delete_vault_image(image_id)
    await query.answer("Deleted")
    try:
        await query.message.delete()
    except Exception:
        pass
