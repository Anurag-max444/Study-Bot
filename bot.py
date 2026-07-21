"""
Entry point. This file's only job now is: import every handler from
handlers/, run the tiny health-check server Render needs, and wire
everything up in main(). All actual command/callback logic lives in
handlers/; all business logic lives in services/; all database access
lives in repositories/.
"""
import threading
from datetime import time as dtime
from http.server import BaseHTTPRequestHandler, HTTPServer

import logger  # noqa: F401 — importing this sets up logging.basicConfig() once, centrally
import config

from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters,
)

# NOTE: Render pe env var TZ=Asia/Kolkata set karna, warna server UTC time use karega
# aur reminders galat time pe jayenge.

BOT_TOKEN = config.TELEGRAM_BOT_TOKEN

from handlers.onboarding import start, language_chosen, exam_chosen, handle_text
from handlers.tasks import (
    addtask_command, mytopics_command, removetask_command, studylog_command, mark_session_done,
)
from handlers.progress import progress_command, badges_command, badge_info, mytree_command
from handlers.revisions import revisions_command, mark_revision_done
from handlers.pdf import extractquestions_command, handle_pdf
from handlers.misc import cancel_command, help_command, clear_command, global_error_handler
from handlers.mocktest import (
    addmocktest_command, mocktest_scope_chosen, mocktest_breadth_chosen, mocktests_command,
    mocktest_detail_callback,
)
from handlers.vault import VAULT_VIEW_COMMAND, VAULT_SAVE_COMMAND, vault_view, vault_save, vault_photo_handler, vault_delete_callback
from handlers.reports import report_command, send_weekly_reports_job, _catchup_weekly_report_if_needed

from services import task_service, revision_service


# ---------- Scheduler job wrappers ----------
# Thin on purpose — real orchestration lives in services/. These will move
# to a dedicated schedulers/ package in a later phase; the job_queue
# registrations in main() below need *some* module to import them from in
# the meantime.

async def send_custom_task_start(context):
    await task_service.start_due_task_sessions(context.bot)


async def check_due_followups(context):
    await task_service.send_task_followups(context.bot)


async def send_due_revisions(context):
    await revision_service.send_due_revisions(context.bot)


# ---------- Health-check server (Render needs a port bound to stay alive) ----------
class _HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._send_headers()
        self.wfile.write(b"Study Buddy bot is alive!")

    def do_HEAD(self):
        # UptimeRobot's default "HTTP(s)" monitor sends HEAD requests, not GET —
        # a HEAD response must have the same headers as GET but no body.
        self._send_headers()

    def _send_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

    def log_message(self, format, *args):
        pass  # keep logs clean, don't print every ping


def _run_health_server():
    port = config.PORT
    server = HTTPServer(("0.0.0.0", port), _HealthCheckHandler)
    server.serve_forever()


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel_command))
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
    app.add_handler(CommandHandler(VAULT_VIEW_COMMAND, vault_view))
    app.add_handler(CommandHandler(VAULT_SAVE_COMMAND, vault_save))
    app.add_handler(CallbackQueryHandler(language_chosen, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(exam_chosen, pattern="^exam_"))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.PHOTO, vault_photo_handler))
    app.add_handler(CallbackQueryHandler(mark_session_done, pattern="^sessiondone_"))
    app.add_handler(CallbackQueryHandler(mark_revision_done, pattern="^revdone_"))
    app.add_handler(CallbackQueryHandler(badge_info, pattern="^badgeinfo_"))
    app.add_handler(CallbackQueryHandler(vault_delete_callback, pattern="^vaultdel_"))
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
    # Catches up a missed Sunday broadcast (e.g. host was down) shortly after startup
    app.job_queue.run_once(_catchup_weekly_report_if_needed, when=20)

    # Render free Web Service ko port pe response chahiye, warna spin-down/fail ho jata hai.
    # Ye background thread mein ek chhota HTTP server chalata hai jise UptimeRobot ping sake.
    threading.Thread(target=_run_health_server, daemon=True).start()

    print("Bot chal raha hai...")
    app.run_polling()


if __name__ == "__main__":
    main()
