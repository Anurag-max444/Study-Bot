"""Notification service — decides what gamification notifications (shield
used, new badge) are owed after a completion event, and sends them. This is
business logic (which notification, in what language, to whom) even though
it also performs the actual Telegram send — see services/__init__.py for
why that's still considered a service concern, not a handler concern."""
from telegram import Bot

from ui.lang import t
import db


async def notify_gamification(bot: Bot, user_id: int, lang: str, shield_used: bool, newly_badges: list):
    """Sends shield-used and new-badge notifications after any completion event."""
    if shield_used:
        streak = db.get_streak(user_id)
        remaining = streak["shields_available"] if streak else 0
        await bot.send_message(
            user_id, t("shield_used_notification", lang, remaining=remaining), parse_mode="HTML"
        )

    for badge_name in newly_badges:
        await bot.send_message(
            user_id, t("badge_earned_notification", lang, badge_name=badge_name), parse_mode="HTML"
        )
