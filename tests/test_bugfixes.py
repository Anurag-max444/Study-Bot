"""Regression tests for 3 bugs found via manual bug-hunting:

Bug 1: /addtask accepted invalid times like '29:99' (shape-only validation),
       which crashed later in db.add_custom_task's datetime.replace() call.
Bug 2: The weekly report broadcast marked itself as "done" even when every
       single send failed (e.g. a total outage), preventing the startup
       catch-up mechanism from ever retrying that missed week.
Bug 3: Several callback handlers (mark_session_done, exam_chosen,
       mocktest_scope_chosen, mocktest_breadth_chosen) crashed with a
       NoneType error if triggered on a stale inline button after the
       user's DB record no longer existed.
"""
import types

import pytest

import bot
import handlers.tasks as tasks
import handlers.onboarding as onboarding
import handlers.revisions as revisions
import handlers.mocktest as mocktest
from services import report_service


# ---------------------------------------------------------------------
# Bug 1 — invalid time range accepted
# ---------------------------------------------------------------------

class TestBug1InvalidTimeRange:
    @pytest.mark.asyncio
    async def test_hour_out_of_range_is_rejected(self, monkeypatch, fake_user, make_update, make_context):
        ctx = make_context(user_data={"task_flow": {"step": "time"}})
        update = make_update(fake_user["id"], text="29:99")

        await tasks.handle_task_flow_text(update, ctx, fake_user)

        assert ctx.user_data["task_flow"]["step"] == "time"  # stayed on the same step, not advanced
        assert "time" not in ctx.user_data["task_flow"] or ctx.user_data["task_flow"].get("time") is None

    @pytest.mark.asyncio
    async def test_minute_out_of_range_is_rejected(self, fake_user, make_update, make_context):
        ctx = make_context(user_data={"task_flow": {"step": "time"}})
        update = make_update(fake_user["id"], text="14:75")

        await tasks.handle_task_flow_text(update, ctx, fake_user)

        assert ctx.user_data["task_flow"]["step"] == "time"

    @pytest.mark.asyncio
    async def test_valid_boundary_times_are_accepted(self, fake_user, make_update, make_context):
        for valid_time in ("00:00", "23:59", "09:30"):
            ctx = make_context(user_data={"task_flow": {"step": "time"}})
            update = make_update(fake_user["id"], text=valid_time)
            await tasks.handle_task_flow_text(update, ctx, fake_user)
            assert ctx.user_data["task_flow"]["step"] == "topic", f"{valid_time} should have been accepted"

    @pytest.mark.asyncio
    async def test_garbage_input_is_still_rejected(self, fake_user, make_update, make_context):
        ctx = make_context(user_data={"task_flow": {"step": "time"}})
        update = make_update(fake_user["id"], text="hello")
        await tasks.handle_task_flow_text(update, ctx, fake_user)
        assert ctx.user_data["task_flow"]["step"] == "time"


# ---------------------------------------------------------------------
# Bug 2 — weekly report falsely marked complete after total failure
# ---------------------------------------------------------------------

class TestBug2WeeklyReportFalseCompletion:
    @pytest.mark.asyncio
    async def test_total_failure_does_not_update_state(self, monkeypatch, make_context):
        state = {}
        monkeypatch.setattr(report_service.db, "get_state", lambda k: state.get(k))
        monkeypatch.setattr(report_service.db, "set_state", lambda k, v: state.__setitem__(k, v))
        monkeypatch.setattr(report_service.db, "get_all_onboarded_users", lambda: [
            {"id": 1, "name": "user1", "language": "hinglish"},
            {"id": 2, "name": "user2", "language": "hinglish"},
        ])

        async def always_fails(bot_, chat_id, user):
            raise Exception("simulated total outage")

        async def no_sleep(_seconds):
            return None

        monkeypatch.setattr(report_service, "build_and_send_report", always_fails)
        monkeypatch.setattr(report_service.asyncio, "sleep", no_sleep)

        await report_service.send_weekly_reports_job(make_context())

        assert "last_weekly_report_run" not in state, (
            "state must NOT be marked complete when every single send failed, "
            "otherwise a missed week is never caught up"
        )

    @pytest.mark.asyncio
    async def test_partial_success_still_updates_state(self, monkeypatch, make_context):
        state = {}
        monkeypatch.setattr(report_service.db, "get_state", lambda k: state.get(k))
        monkeypatch.setattr(report_service.db, "set_state", lambda k, v: state.__setitem__(k, v))
        monkeypatch.setattr(report_service.db, "get_all_onboarded_users", lambda: [
            {"id": 1, "name": "good", "language": "hinglish"},
            {"id": 2, "name": "bad", "language": "hinglish"},
        ])

        async def mixed(bot_, chat_id, user):
            if user["name"] == "bad":
                raise Exception("this one fails")

        async def no_sleep(_seconds):
            return None

        monkeypatch.setattr(report_service, "build_and_send_report", mixed)
        monkeypatch.setattr(report_service.asyncio, "sleep", no_sleep)

        await report_service.send_weekly_reports_job(make_context())

        assert "last_weekly_report_run" in state, (
            "at least one success should still count the run as complete"
        )

    @pytest.mark.asyncio
    async def test_zero_users_still_updates_state(self, monkeypatch, make_context):
        """Nothing to send is not a failure — should still mark the run complete."""
        state = {}
        monkeypatch.setattr(report_service.db, "get_state", lambda k: state.get(k))
        monkeypatch.setattr(report_service.db, "set_state", lambda k, v: state.__setitem__(k, v))
        monkeypatch.setattr(report_service.db, "get_all_onboarded_users", lambda: [])

        await report_service.send_weekly_reports_job(make_context())

        assert "last_weekly_report_run" in state


# ---------------------------------------------------------------------
# Bug 3 — stale callback crashes with NoneType when the user record is gone
# ---------------------------------------------------------------------

class TestBug3StaleCallbackNoneUser:
    def _make_callback_update(self, make_update, uid, data, text="some message"):
        update = make_update(uid)
        query = types.SimpleNamespace()
        query.data = data
        query.from_user = types.SimpleNamespace(id=uid)
        query.message = update.message
        query.message.text = text

        async def _answer(*a, **kw):
            pass

        async def _edit(*a, **kw):
            pass

        query.answer = _answer
        query.edit_message_text = _edit
        update.callback_query = query
        return update

    @pytest.mark.asyncio
    async def test_mark_session_done_does_not_crash_for_deleted_user(self, monkeypatch, make_update, make_context):
        monkeypatch.setattr(tasks.db, "get_user", lambda uid: None)
        update = self._make_callback_update(make_update, 999, "sessiondone_1")

        await bot.mark_session_done(update, make_context())  # should not raise

        assert update.message.replies  # got a graceful message instead of crashing

    @pytest.mark.asyncio
    async def test_exam_chosen_does_not_crash_for_deleted_user(self, monkeypatch, make_update, make_context):
        monkeypatch.setattr(onboarding.db, "get_user", lambda uid: None)
        update = self._make_callback_update(make_update, 999, "exam_ssc_cgl")

        await bot.exam_chosen(update, make_context())  # should not raise

        assert update.message.replies

    @pytest.mark.asyncio
    async def test_mocktest_scope_chosen_does_not_crash_for_deleted_user(self, monkeypatch, make_update, make_context):
        monkeypatch.setattr(mocktest.db, "get_user", lambda uid: None)
        ctx = make_context(user_data={"mocktest_flow": {"step": "scope_type"}})
        update = self._make_callback_update(make_update, 999, "mtscope_full")

        await mocktest.mocktest_scope_chosen(update, ctx)  # should not raise

        assert update.message.replies

    @pytest.mark.asyncio
    async def test_mocktest_breadth_chosen_does_not_crash_for_deleted_user(self, monkeypatch, make_update, make_context):
        monkeypatch.setattr(mocktest.db, "get_user", lambda uid: None)
        ctx = make_context(user_data={"mocktest_flow": {"step": "scope_breadth"}})
        update = self._make_callback_update(make_update, 999, "mtbreadth_subject")

        await mocktest.mocktest_breadth_chosen(update, ctx)  # should not raise

        assert update.message.replies

    @pytest.mark.asyncio
    async def test_mark_revision_done_does_not_crash_for_deleted_user(self, monkeypatch, make_update, make_context):
        """Added during the Phase 5 services/ extraction: mark_revision_done used
        to tolerate a None user implicitly (never indexed user[...] after the
        fallback), but delegating to revision_service.complete_revision (which
        does index user["id"]/user["language"]) would have reintroduced the
        exact Bug 3 crash pattern without this explicit guard."""
        monkeypatch.setattr(revisions.db, "get_user", lambda uid: None)
        update = self._make_callback_update(make_update, 999, "revdone_1")

        await bot.mark_revision_done(update, make_context())  # should not raise

        assert update.message.replies
