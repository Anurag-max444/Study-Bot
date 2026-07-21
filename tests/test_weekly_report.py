"""Tests for weekly report resilience: per-user retry on failure, one user's
total failure never blocking the batch, and the startup catch-up mechanism
that detects a missed Sunday broadcast.

These monkeypatch through the `report_service` module directly (not `report`
or `bot`), because send_weekly_reports_job calls build_and_send_report as a
name inside its own module — patching a re-exported copy elsewhere wouldn't
reach it."""
from datetime import date, timedelta

import pytest

from services import report_service


@pytest.fixture
def fake_state(monkeypatch):
    state = {}
    monkeypatch.setattr(report_service.db, "get_state", lambda k: state.get(k))
    monkeypatch.setattr(report_service.db, "set_state", lambda k, v: state.__setitem__(k, v))
    return state


@pytest.mark.asyncio
async def test_transient_failure_is_retried_once(monkeypatch, fake_state, make_context):
    calls = {"count": 0}

    async def flaky(bot_, chat_id, user):
        calls["count"] += 1
        if calls["count"] == 1:
            raise Exception("simulated transient error")

    monkeypatch.setattr(report_service, "build_and_send_report", flaky)
    monkeypatch.setattr(report_service.db, "get_all_onboarded_users", lambda: [{"id": 1, "name": "user1", "language": "hinglish"}])
    monkeypatch.setattr(report_service.asyncio, "sleep", _no_sleep)

    await report_service.send_weekly_reports_job(make_context())

    assert calls["count"] == 2
    assert fake_state["last_weekly_report_run"] == date.today().isoformat()


@pytest.mark.asyncio
async def test_one_users_total_failure_does_not_block_others(monkeypatch, fake_state, make_context):
    calls = {"bad": 0, "good": 0}

    async def mixed(bot_, chat_id, user):
        calls[user["name"]] += 1
        if user["name"] == "bad":
            raise Exception("always fails")

    monkeypatch.setattr(report_service, "build_and_send_report", mixed)
    monkeypatch.setattr(report_service.db, "get_all_onboarded_users", lambda: [
        {"id": 1, "name": "bad", "language": "hinglish"},
        {"id": 2, "name": "good", "language": "hinglish"},
    ])
    monkeypatch.setattr(report_service.asyncio, "sleep", _no_sleep)

    await report_service.send_weekly_reports_job(make_context())

    assert calls["bad"] == 2   # first attempt + 1 retry, both failed
    assert calls["good"] == 1  # succeeded immediately, no retry needed


@pytest.mark.asyncio
async def test_catchup_triggers_when_never_run_before(monkeypatch, fake_state, make_context):
    triggered = {"count": 0}

    async def fake_broadcast(context):
        triggered["count"] += 1

    monkeypatch.setattr(report_service, "send_weekly_reports_job", fake_broadcast)
    await report_service.catchup_weekly_report_if_needed(make_context())

    assert triggered["count"] == 1


@pytest.mark.asyncio
async def test_catchup_does_not_trigger_if_run_recently(monkeypatch, fake_state, make_context):
    fake_state["last_weekly_report_run"] = (date.today() - timedelta(days=3)).isoformat()
    triggered = {"count": 0}

    async def fake_broadcast(context):
        triggered["count"] += 1

    monkeypatch.setattr(report_service, "send_weekly_reports_job", fake_broadcast)
    await report_service.catchup_weekly_report_if_needed(make_context())

    assert triggered["count"] == 0


@pytest.mark.asyncio
async def test_catchup_triggers_if_a_sunday_was_missed(monkeypatch, fake_state, make_context):
    fake_state["last_weekly_report_run"] = (date.today() - timedelta(days=9)).isoformat()
    triggered = {"count": 0}

    async def fake_broadcast(context):
        triggered["count"] += 1

    monkeypatch.setattr(report_service, "send_weekly_reports_job", fake_broadcast)
    await report_service.catchup_weekly_report_if_needed(make_context())

    assert triggered["count"] == 1


@pytest.mark.asyncio
async def test_catchup_handles_malformed_state_without_crashing(monkeypatch, fake_state, make_context):
    fake_state["last_weekly_report_run"] = "not-a-real-date"
    triggered = {"count": 0}

    async def fake_broadcast(context):
        triggered["count"] += 1

    monkeypatch.setattr(report_service, "send_weekly_reports_job", fake_broadcast)
    await report_service.catchup_weekly_report_if_needed(make_context())

    assert triggered["count"] == 1


async def _no_sleep(_seconds):
    """Replaces asyncio.sleep in tests so the retry-delay doesn't slow the suite down."""
    return None
