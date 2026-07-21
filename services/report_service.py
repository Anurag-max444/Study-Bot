"""Report service — aggregates a user's weekly study data, builds+sends the
PDF report card, and runs the Sunday-night broadcast (with per-user retry
and a startup catch-up check for a missed week).

Note: send_weekly_reports_job and catchup_weekly_report_if_needed still
accept a `context` (not just `bot`) because they're registered directly
with python-telegram-bot's JobQueue, which calls its callbacks with a
context object — this will move to a thin scheduler wrapper once
schedulers/ exists (a later phase); the orchestration itself is unchanged."""
import os
import logging
import asyncio
import tempfile
from datetime import date, timedelta

from telegram import Bot
from telegram.ext import ContextTypes

import db
from ui.lang import t
import ui.report_generator as report_generator
from utils.formatting import esc


def daily_minutes_last_7_days(user_id: int):
    """Returns a 7-int list of completed study minutes per day, oldest -> today."""
    sessions = db.get_study_log(user_id, days=7)
    today = date.today()
    by_date = {(today - timedelta(days=i)).isoformat(): 0 for i in range(7)}
    for s in sessions:
        if s["completed"] and s["session_date"] in by_date:
            by_date[s["session_date"]] += s["duration_minutes"]
    ordered_dates = sorted(by_date.keys())
    return [by_date[d] for d in ordered_dates]


async def build_and_send_report(bot: Bot, chat_id: int, user: dict):
    """Builds the weekly PDF report card for one user and sends it. Raises on
    failure so the caller (job or command) can decide how to handle/log it."""
    lang = user["language"]
    daily_minutes = daily_minutes_last_7_days(user["id"])
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


async def send_weekly_reports_job(context: ContextTypes.DEFAULT_TYPE):
    """Runs automatically every Sunday night (and also once at startup if a
    Sunday run was missed — see catchup_weekly_report_if_needed). Each user
    gets one retry on failure (covers transient network hiccups), and one
    user's failure never blocks the rest of the batch. A summary is logged
    at the end, and the last-successful-run date is recorded so a missed
    week can be detected and caught up automatically next time the bot starts."""
    sent, failed = 0, 0
    for user in db.get_all_onboarded_users():
        ok = False
        for attempt in range(2):  # 1 retry on top of the first attempt
            try:
                await build_and_send_report(context.bot, user["id"], user)
                ok = True
                break
            except Exception:
                if attempt == 0:
                    await asyncio.sleep(3)
                else:
                    logging.exception("Weekly report broadcast failed for user %s (after retry)", user["id"])
        if ok:
            sent += 1
        else:
            failed += 1

    total_failure = failed > 0 and sent == 0
    if not total_failure:
        db.set_state("last_weekly_report_run", date.today().isoformat())
    else:
        logging.warning(
            "Weekly report broadcast had zero successful sends (%s failed) — "
            "not marking the run as complete, so catch-up will retry it.", failed
        )
    logging.info("Weekly report broadcast finished: %s sent, %s failed", sent, failed)


async def catchup_weekly_report_if_needed(context: ContextTypes.DEFAULT_TYPE):
    """Runs once, shortly after the bot starts. If more than 7 days have
    passed since the last successful weekly-report broadcast (e.g. the host
    was down at the scheduled Sunday time), runs it immediately instead of
    silently waiting until next Sunday."""
    last_run = db.get_state("last_weekly_report_run")
    if last_run:
        try:
            days_since = (date.today() - date.fromisoformat(last_run)).days
        except ValueError:
            days_since = 8  # malformed state value — treat as overdue rather than crash
        if days_since < 7:
            return
    logging.info("Weekly report catch-up triggered (last run: %s)", last_run or "never")
    await send_weekly_reports_job(context)
