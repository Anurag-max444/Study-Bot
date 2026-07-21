# Study Sync

A Telegram bot that helps students preparing for competitive exams (SSC CGL, JEE Mains, and similar) study with consistency — through self-scheduled sessions, automatic revision reminders, and lightweight gamification. Fully multilingual (Hindi / English / Hinglish). No paid APIs used anywhere.

---

## Features

**Problem:** Students plan to study but have no system to hold them to a schedule.
**Solution:** `/addtask` — set a topic, a start time, and a duration. The bot sends a reminder to begin, then checks in automatically once the time is up to confirm completion.

**Problem:** Reminders are useless if the bot silently misses them after a server restart.
**Solution:** All scheduling is timestamp-based and stored server-side — sessions are never lost to a brief downtime, and overdue reminders fire the moment the bot is back up.

**Problem:** Students study a topic once and forget it weeks later.
**Solution:** Every completed session automatically schedules four revision reminders — at 1, 3, 7, and 15 days — based on the spaced-repetition forgetting-curve model.

**Problem:** Practice papers are scattered across long, unformatted PDFs.
**Solution:** `/pdf` extracts MCQ-style questions from any PDF using pattern recognition and rebuilds them into a clean, formatted PDF with a separate answer key — with full support for mixed Hindi–English content.

**Problem:** Motivation drops without visible proof of progress.
**Solution:** A daily streak counter, "shields" that forgive a single missed day, and unlockable achievement badges (Night Owl, Century Club, and others) reward consistency. A procedurally generated Study Tree visually grows with progress — and wilts if the student goes quiet for too long.

**Problem:** Long chat histories get cluttered and slow to navigate.
**Solution:** `/clear` wipes recent messages from the chat instantly, using batched deletion rather than one message at a time.

---

## Command Reference

| Command | Purpose |
|---|---|
| `/start` | Onboarding — language, name, exam, syllabus |
| `/addtask` | Schedule a study session (topic, time, duration) |
| `/mytopics` | View scheduled sessions |
| `/removetask HH:MM` | Cancel a scheduled session |
| `/studylog` | Study history and total hours |
| `/revisions` | Pending spaced-repetition revisions |
| `/progress` | Streak, shields, badge count |
| `/badges` | All achievement badges, earned and locked |
| `/mytree` | Study Tree image |
| `/pdf` | Extract MCQ questions from a PDF |
| `/clear` | Clear recent messages in this chat |
| `/help` | Full command list |

---

## Stack

Python · `python-telegram-bot` · Supabase (Postgres) · `pdfplumber` + `fpdf2` (PDF extraction/generation, bundled Noto Sans / Noto Sans Devanagari fonts) · Pillow (Study Tree rendering)

## Setup

1. Run `database/migrations/ALL_MIGRATIONS.sql` in the Supabase SQL editor.
2. Get a bot token from [@BotFather](https://t.me/BotFather).
3. Copy `.env.example` → `.env`, fill in the three values.
4. `pip install -r requirements.txt && python bot.py`

Long-term hosting and database migration notes: see `docs/HOSTING_PLAYBOOK.md`.
