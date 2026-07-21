"""
Shared pytest fixtures for the Study Sync test suite.

The most important thing this file does is stub out the `supabase` package
*before* `db.py` (and therefore `bot.py`) gets imported anywhere. `db.py`
calls `create_client()` at module import time, so without this stub every
test file would need real SUPABASE_URL/SUPABASE_KEY credentials just to
import the code under test.

Individual tests should use the `monkeypatch` fixture to replace whichever
`db.*` functions they need for that test (e.g.
`monkeypatch.setattr(db, "get_user", lambda uid: {...})`), so changes never
leak between tests.
"""
import os
import sys
import types

import pytest


def _install_fake_supabase():
    if "supabase" in sys.modules:
        return

    fake_supabase = types.ModuleType("supabase")

    class FakeClient:
        pass

    def create_client(url, key):
        if not url or not key:
            raise Exception("supabase_url is required")
        return FakeClient()

    fake_supabase.Client = FakeClient
    fake_supabase.create_client = create_client
    sys.modules["supabase"] = fake_supabase


_install_fake_supabase()

os.environ.setdefault("SUPABASE_URL", "https://fake.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "fake-key")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123:fake-token")
os.environ.setdefault("VAULT_PASSWORD", "PASS123")

import db  # noqa: E402  (must come after the supabase stub is installed)
import bot  # noqa: E402


@pytest.fixture
def fake_user():
    """A minimal, fully-onboarded user dict, matching db.get_user()'s shape."""
    return {
        "id": 111222333,
        "name": "Rahul",
        "language": "hinglish",
        "exam": "ssc_cgl",
        "daily_hours": 4.0,
        "onboarding_step": "done",
    }


class FakeMessage:
    """Stands in for telegram.Message — records what the bot tried to send."""

    def __init__(self, text=None, photo=None):
        self.text = text
        self.photo = photo
        self.replies = []
        self.photos_sent = []
        self.deleted = False
        self.edits = []

    async def reply_text(self, text, **kwargs):
        self.replies.append(text)

    async def reply_photo(self, photo, caption=None, **kwargs):
        self.photos_sent.append((photo, caption))

    async def edit_text(self, text, **kwargs):
        self.edits.append(text)

    async def delete(self):
        self.deleted = True


class FakeChat:
    def __init__(self, chat_id=999):
        self.id = chat_id


class FakeUpdate:
    """Stands in for telegram.Update for command/message handlers."""

    def __init__(self, user_id, text=None, photo=None, chat_id=999):
        self.effective_user = types.SimpleNamespace(id=user_id)
        self.effective_chat = FakeChat(chat_id)
        self.message = FakeMessage(text=text, photo=photo)


class FakeBot:
    """Stands in for telegram.Bot — records every outbound call instead of
    hitting the real Telegram API."""

    def __init__(self):
        self.chat_actions = []
        self.sent_messages = []
        self.sent_documents = []

    async def send_chat_action(self, chat_id, action):
        self.chat_actions.append(action)

    async def send_message(self, chat_id, text, **kwargs):
        self.sent_messages.append((chat_id, text))
        return FakeMessage()

    async def send_document(self, chat_id, document, filename, caption, parse_mode):
        self.sent_documents.append((chat_id, filename, len(document.read()), caption))


class FakeContext:
    """Stands in for telegram.ext.ContextTypes.DEFAULT_TYPE."""

    def __init__(self, user_data=None, bot_data=None):
        self.user_data = user_data if user_data is not None else {}
        self.bot_data = bot_data if bot_data is not None else {}
        self.bot = FakeBot()


@pytest.fixture
def make_update():
    return FakeUpdate


@pytest.fixture
def make_context():
    return FakeContext
