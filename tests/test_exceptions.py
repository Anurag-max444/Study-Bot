"""Tests for exceptions/ — the custom exception classes themselves, plus
their integration points: db.py's write functions (DatabaseError on
Supabase failure, ValidationError as a defense-in-depth guard against the
exact Bug 1 crash), and bot.py's global_error_handler (categorized logging)."""
import logging
from datetime import date

import pytest

from exceptions.database import DatabaseError
from exceptions.validation import ValidationError
from exceptions.telegram import TelegramError
import db
import bot
import repositories.task_repo as task_repo
import repositories.mocktest_repo as mocktest_repo
import repositories.vault_repo as vault_repo


class TestExceptionClasses:
    def test_database_error_carries_operation_and_original_error(self):
        original = Exception("connection reset")
        err = DatabaseError("add_mock_test", original)
        assert err.operation == "add_mock_test"
        assert err.original_error is original
        assert "add_mock_test" in str(err)
        assert "connection reset" in str(err)

    def test_validation_error_carries_field_and_reason(self):
        err = ValidationError("time", "'29:99' is not a valid HH:MM time")
        assert err.field == "time"
        assert "29:99" in str(err)

    def test_telegram_error_carries_action_and_original_error(self):
        original = Exception("chat not found")
        err = TelegramError("send_document", original)
        assert err.action == "send_document"
        assert err.original_error is original
        assert "send_document" in str(err)


class TestDatabaseErrorIntegration:
    def test_add_custom_task_raises_database_error_on_supabase_failure(self, monkeypatch):
        class FakeTable:
            def insert(self, *a, **kw):
                return self

            def execute(self):
                raise Exception("simulated network failure")

        monkeypatch.setattr(task_repo, "supabase", type("S", (), {"table": lambda self, name: FakeTable()})())

        with pytest.raises(DatabaseError) as exc_info:
            db.add_custom_task(1, "09:30", "Algebra", 60)
        assert exc_info.value.operation == "add_custom_task"

    def test_add_custom_task_raises_validation_error_for_invalid_time_defense_in_depth(self, monkeypatch):
        """This is the exact Bug 1 crash point (datetime.replace with an
        out-of-range hour/minute) — bot.py's handle_task_flow_text already
        rejects '29:99' before it gets here, but this confirms the
        defense-in-depth guard also works if that check is ever bypassed."""
        with pytest.raises(ValidationError) as exc_info:
            db.add_custom_task(1, "29:99", "Algebra", 60)
        assert exc_info.value.field == "time"

    def test_add_mock_test_raises_database_error_on_supabase_failure(self, monkeypatch):
        class FakeTable:
            def insert(self, *a, **kw):
                return self

            def execute(self):
                raise Exception("simulated failure")

        monkeypatch.setattr(mocktest_repo, "supabase", type("S", (), {"table": lambda self, name: FakeTable()})())

        with pytest.raises(DatabaseError) as exc_info:
            db.add_mock_test(1, test_date=date.today(), platform="Testbook")
        assert exc_info.value.operation == "add_mock_test"

    def test_add_vault_image_raises_database_error_on_supabase_failure(self, monkeypatch):
        class FakeTable:
            def insert(self, *a, **kw):
                return self

            def execute(self):
                raise Exception("simulated failure")

        monkeypatch.setattr(vault_repo, "supabase", type("S", (), {"table": lambda self, name: FakeTable()})())

        with pytest.raises(DatabaseError) as exc_info:
            db.add_vault_image("some_file_id")
        assert exc_info.value.operation == "add_vault_image"


class TestGlobalErrorHandlerCategorization:
    @pytest.mark.asyncio
    async def test_database_error_is_logged_with_its_category(self, caplog, make_context):
        ctx = make_context()
        ctx.error = DatabaseError("add_mock_test", Exception("boom"))
        with caplog.at_level(logging.ERROR):
            await bot.global_error_handler(None, ctx)
        assert any("Database error" in r.message for r in caplog.records)

    @pytest.mark.asyncio
    async def test_validation_error_is_logged_with_its_category(self, caplog, make_context):
        ctx = make_context()
        ctx.error = ValidationError("time", "bad format")
        with caplog.at_level(logging.ERROR):
            await bot.global_error_handler(None, ctx)
        assert any("Validation error" in r.message for r in caplog.records)

    @pytest.mark.asyncio
    async def test_generic_exception_still_gets_logged_and_does_not_raise(self, caplog, make_context):
        """The catch-all behavior must be unchanged: any other exception
        type is still just logged, never allowed to crash the bot."""
        ctx = make_context()
        ctx.error = RuntimeError("something unexpected")
        with caplog.at_level(logging.ERROR):
            await bot.global_error_handler(None, ctx)  # must not raise
        assert any("Unhandled exception" in r.message for r in caplog.records)
