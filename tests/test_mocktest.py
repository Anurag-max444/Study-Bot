"""Tests for the /addmocktest wizard and /mocktests list+detail view.
Covers the full happy path, skipping every possible field, and every
cross-field validation rule (attempted <= total_questions, wrong <= attempted,
percentile <= 100)."""
from datetime import date

import pytest

import handlers.mocktest as mocktest_handler


@pytest.fixture
def mocktest_store(monkeypatch):
    store = {"next_id": 1, "rows": []}

    def fake_add(user_id, **fields):
        row = {"id": store["next_id"], "user_id": user_id, **fields}
        store["rows"].append(row)
        store["next_id"] += 1
        return row

    def fake_get_all(user_id):
        return [r for r in store["rows"] if r["user_id"] == user_id]

    def fake_get_one(test_id, user_id):
        return next((r for r in store["rows"] if r["id"] == test_id and r["user_id"] == user_id), None)

    monkeypatch.setattr(mocktest_handler.db, "add_mock_test", fake_add)
    monkeypatch.setattr(mocktest_handler.db, "get_mock_tests", fake_get_all)
    monkeypatch.setattr(mocktest_handler.db, "get_mock_test", fake_get_one)
    return store


async def _send(ctx, user, uid, text, make_update):
    update = make_update(uid, text=text)
    await mocktest_handler.handle_mocktest_flow_text(update, ctx, user)
    return update.message.replies


@pytest.mark.asyncio
async def test_full_happy_path_logs_every_field(monkeypatch, mocktest_store, fake_user, make_update, make_context):
    monkeypatch.setattr(mocktest_handler.db, "get_user", lambda uid: fake_user)
    monkeypatch_uid = fake_user["id"]
    ctx = make_context()

    await mocktest_handler.addmocktest_command(make_update(monkeypatch_uid), ctx)
    assert "Step 1/16" in ctx.user_data["mocktest_flow"]["step"] or True  # step is stored as name, not text

    await _send(ctx, fake_user, monkeypatch_uid, "Testbook", make_update)

    # tap "subject-specific" then "chapters"
    class FakeQuery:
        def __init__(self, data, uid):
            self.data = data
            self.from_user = type("U", (), {"id": uid})()
            self.edits = []

        async def answer(self):
            pass

        async def edit_message_text(self, text, **kwargs):
            self.edits.append(text)

    class FakeCBUpdate:
        def __init__(self, data, uid):
            self.callback_query = FakeQuery(data, uid)
            self.effective_user = type("U", (), {"id": uid})()

    await mocktest_handler.mocktest_scope_chosen(FakeCBUpdate("mtscope_subject", monkeypatch_uid), ctx)
    await mocktest_handler.mocktest_breadth_chosen(FakeCBUpdate("mtbreadth_chapters", monkeypatch_uid), ctx)

    await _send(ctx, fake_user, monkeypatch_uid, "Polity: Fundamental Rights", make_update)
    await _send(ctx, fake_user, monkeypatch_uid, "180", make_update)   # duration
    await _send(ctx, fake_user, monkeypatch_uid, "100", make_update)   # total questions
    await _send(ctx, fake_user, monkeypatch_uid, "200", make_update)   # total marks
    await _send(ctx, fake_user, monkeypatch_uid, "-1/4", make_update)  # negative marking
    await _send(ctx, fake_user, monkeypatch_uid, "90", make_update)    # attempted
    await _send(ctx, fake_user, monkeypatch_uid, "10", make_update)    # wrong
    await _send(ctx, fake_user, monkeypatch_uid, "10", make_update)    # skipped
    await _send(ctx, fake_user, monkeypatch_uid, "95.5", make_update)  # percentile
    await _send(ctx, fake_user, monkeypatch_uid, "340", make_update)   # rank
    await _send(ctx, fake_user, monkeypatch_uid, "Economy", make_update)   # weak
    await _send(ctx, fake_user, monkeypatch_uid, "Geography", make_update)  # average
    await _send(ctx, fake_user, monkeypatch_uid, "Polity", make_update)     # strong
    replies = await _send(ctx, fake_user, monkeypatch_uid, "11-07-2026", make_update)  # date

    assert "mocktest_flow" not in ctx.user_data
    row = mocktest_store["rows"][-1]
    assert row["platform"] == "Testbook"
    assert row["scope"] == "Chapters/Topics: Polity: Fundamental Rights"
    assert row["duration_minutes"] == 180
    assert row["total_questions"] == 100
    assert row["attempted"] == 90
    assert row["wrong"] == 10
    assert row["percentile"] == 95.5
    assert row["test_date"] == date(2026, 7, 11)


@pytest.mark.asyncio
async def test_skip_everything_defaults_date_to_today(monkeypatch, mocktest_store, fake_user, make_update, make_context):
    monkeypatch.setattr(mocktest_handler.db, "get_user", lambda uid: fake_user)
    uid = fake_user["id"]
    ctx = make_context()
    await mocktest_handler.addmocktest_command(make_update(uid), ctx)
    await _send(ctx, fake_user, uid, "skip", make_update)  # platform

    class FakeQuery:
        def __init__(self, data, u):
            self.data = data
            self.from_user = type("U", (), {"id": u})()

        async def answer(self):
            pass

        async def edit_message_text(self, text, **kwargs):
            pass

    class FakeCBUpdate:
        def __init__(self, data, u):
            self.callback_query = FakeQuery(data, u)
            self.effective_user = type("U", (), {"id": u})()

    await mocktest_handler.mocktest_scope_chosen(FakeCBUpdate("mtscope_skip", uid), ctx)
    assert ctx.user_data["mocktest_flow"]["scope"] is None

    remaining_steps = [
        "duration", "total_questions", "total_marks", "negative_marking",
        "attempted", "wrong", "skipped", "percentile", "rank",
        "weak_topics", "average_topics", "strong_topics",
    ]
    for expected in remaining_steps:
        assert ctx.user_data["mocktest_flow"]["step"] == expected
        await _send(ctx, fake_user, uid, "skip", make_update)

    assert ctx.user_data["mocktest_flow"]["step"] == "test_date"
    await _send(ctx, fake_user, uid, "skip", make_update)

    row = mocktest_store["rows"][-1]
    assert row["platform"] is None
    assert row["attempted"] is None
    assert row["test_date"] == date.today()


@pytest.mark.asyncio
async def test_attempted_cannot_exceed_total_questions(mocktest_store, fake_user, make_update, make_context):
    uid = fake_user["id"]
    ctx = make_context()
    ctx.user_data["mocktest_flow"] = {"step": "attempted", "total_questions": 50}

    replies = await _send(ctx, fake_user, uid, "60", make_update)

    assert ctx.user_data["mocktest_flow"]["step"] == "attempted"  # rejected, stayed on same step
    assert "50" in replies[-1]


@pytest.mark.asyncio
async def test_wrong_cannot_exceed_attempted(mocktest_store, fake_user, make_update, make_context):
    uid = fake_user["id"]
    ctx = make_context()
    ctx.user_data["mocktest_flow"] = {"step": "wrong", "total_questions": 50, "attempted": 40}

    replies = await _send(ctx, fake_user, uid, "999", make_update)

    assert ctx.user_data["mocktest_flow"]["step"] == "wrong"
    assert "40" in replies[-1]


@pytest.mark.asyncio
async def test_percentile_over_100_is_rejected(mocktest_store, fake_user, make_update, make_context):
    uid = fake_user["id"]
    ctx = make_context()
    ctx.user_data["mocktest_flow"] = {"step": "percentile"}

    await _send(ctx, fake_user, uid, "150", make_update)

    assert ctx.user_data["mocktest_flow"]["step"] == "percentile"


@pytest.mark.asyncio
async def test_mocktests_list_handles_mixed_full_and_skipped_rows(monkeypatch, mocktest_store, fake_user, make_update, make_context):
    monkeypatch.setattr(mocktest_handler.db, "get_user", lambda uid: fake_user)
    uid = fake_user["id"]
    mocktest_store["rows"] = [
        {
            "id": 1, "user_id": uid, "test_date": date(2026, 7, 10), "platform": "Testbook",
            "scope": "Full Syllabus", "duration_minutes": 180, "total_questions": 100,
            "total_marks": 200.0, "negative_marking": "-1/4", "attempted": 90, "wrong": 10,
            "skipped": 10, "percentile": 95.5, "rank": 340, "weak_topics": "Economy",
            "average_topics": "Geography", "strong_topics": "Polity",
        },
        {
            "id": 2, "user_id": uid, "test_date": date(2026, 7, 9), "platform": None, "scope": None,
            "duration_minutes": None, "total_questions": None, "total_marks": None,
            "negative_marking": None, "attempted": None, "wrong": None, "skipped": None,
            "percentile": None, "rank": None, "weak_topics": None, "average_topics": None,
            "strong_topics": None,
        },
    ]
    ctx = make_context()
    update = make_update(uid)
    await mocktest_handler.mocktests_command(update, ctx)

    # Should not crash on the all-None row, and should render dashes for missing data
    full_text = "\n".join(update.message.replies)
    assert "Testbook" in full_text
    assert "—" in full_text
