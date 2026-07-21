"""
Centralized configuration — the only place in the whole project that reads
raw environment variables or calls load_dotenv(). Every other module gets
its settings by importing from here (e.g. `import config` then
`config.TELEGRAM_BOT_TOKEN`), so all configuration is visible in one place
instead of scattered os.environ.get() calls across a dozen files.

Import-order note: db.py imports this module at its own top, which means
load_dotenv() below is guaranteed to run before db.py's create_client() call
executes — regardless of which module happens to import db.py first. This
is more robust than the old approach, which depended on bot.py always being
the first thing to import db.py.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE_DIR, "assets", "fonts")

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# --- Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# --- Personal vault (hidden feature) ---
VAULT_PASSWORD = os.environ.get("VAULT_PASSWORD", "PASS123")

# --- Hosting ---
# Render (and similar hosts) expect the web service to bind to $PORT; the
# health-check server in bot.py listens on this.
PORT = int(os.environ.get("PORT", 10000))
