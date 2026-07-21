"""Persistent ReplyKeyboardMarkup builders (the bottom menu bar), as opposed
to inline.py which holds per-message InlineKeyboardMarkup builders."""
from telegram import ReplyKeyboardMarkup


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Persistent bottom menu with the 4 most-used commands. The button text is the
    literal command string, so Telegram routes a tap straight to the matching
    CommandHandler — no extra routing logic needed."""
    return ReplyKeyboardMarkup(
        [["/addtask", "/mytopics"], ["/mytree", "/help"]],
        resize_keyboard=True,
    )
