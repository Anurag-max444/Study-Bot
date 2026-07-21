"""Tests for the repositories/ split (Phase 4).

Two things are covered:
1. Facade consistency — every name db.py re-exports must be the *same
   object* as the real function in its repository module, so a future
   accidental edit to db.py's import list gets caught immediately instead
   of silently breaking monkeypatch-based tests elsewhere in the suite.
2. A couple of repositories with real (non-trivial) logic — streak_repo's
   shield-consumption rules and badge_repo's award idempotency — get direct
   unit tests here, since most other repositories are thin passthroughs to
   Supabase and are already exercised indirectly via the handler tests.
"""
import db
from repositories import (
    user_repo, syllabus_repo, streak_repo, badge_repo, progress_repo,
    task_repo, session_repo, revision_repo, state_repo, mocktest_repo, vault_repo,
)


class TestFacadeConsistency:
    def test_user_repo_reexports_match(self):
        assert db.get_user is user_repo.get_user
        assert db.get_all_onboarded_users is user_repo.get_all_onboarded_users
        assert db.create_user is user_repo.create_user
        assert db.update_user is user_repo.update_user

    def test_syllabus_repo_reexport_matches(self):
        assert db.add_syllabus_topics is syllabus_repo.add_syllabus_topics

    def test_streak_repo_reexports_match(self):
        assert db.get_streak is streak_repo.get_streak
        assert db.update_streak_on_completion is streak_repo.update_streak_on_completion

    def test_badge_repo_reexports_match(self):
        assert db.BADGES is badge_repo.BADGES
        assert db.get_user_badges is badge_repo.get_user_badges
        assert db.award_badge is badge_repo.award_badge
        assert db.check_and_award_badges is badge_repo.check_and_award_badges

    def test_progress_repo_reexports_match(self):
        assert db.process_completion is progress_repo.process_completion
        assert db.get_tree_growth_score is progress_repo.get_tree_growth_score
        assert db.get_days_since_active is progress_repo.get_days_since_active

    def test_task_repo_reexports_match(self):
        assert db.add_custom_task is task_repo.add_custom_task
        assert db.get_custom_tasks is task_repo.get_custom_tasks
        assert db.remove_custom_task is task_repo.remove_custom_task
        assert db.delete_custom_task_by_id is task_repo.delete_custom_task_by_id
        assert db.get_due_custom_tasks is task_repo.get_due_custom_tasks

    def test_session_repo_reexports_match(self):
        assert db.create_task_session is session_repo.create_task_session
        assert db.mark_session_completed is session_repo.mark_session_completed
        assert db.get_session is session_repo.get_session
        assert db.get_due_followups is session_repo.get_due_followups
        assert db.mark_followup_sent is session_repo.mark_followup_sent
        assert db.get_study_log is session_repo.get_study_log

    def test_revision_repo_reexports_match(self):
        assert db.REVISION_INTERVALS is revision_repo.REVISION_INTERVALS
        assert db.create_revisions_for_topic is revision_repo.create_revisions_for_topic
        assert db.get_due_revisions is revision_repo.get_due_revisions
        assert db.mark_revision_notified is revision_repo.mark_revision_notified
        assert db.mark_revision_completed is revision_repo.mark_revision_completed
        assert db.get_pending_revisions is revision_repo.get_pending_revisions

    def test_state_repo_reexports_match(self):
        assert db.get_state is state_repo.get_state
        assert db.set_state is state_repo.set_state

    def test_mocktest_repo_reexports_match(self):
        assert db.add_mock_test is mocktest_repo.add_mock_test
        assert db.get_mock_tests is mocktest_repo.get_mock_tests
        assert db.get_mock_test is mocktest_repo.get_mock_test

    def test_vault_repo_reexports_match(self):
        assert db.add_vault_image is vault_repo.add_vault_image
        assert db.get_vault_images is vault_repo.get_vault_images
        assert db.delete_vault_image is vault_repo.delete_vault_image


class TestStreakRepoShieldLogic:
    def test_first_ever_completion_starts_streak_at_one(self, monkeypatch):
        monkeypatch.setattr(streak_repo, "get_streak", lambda uid: None)
        captured = {}

        class FakeTable:
            def insert(self, data):
                captured.update(data)
                return self

            def execute(self):
                return self

        monkeypatch.setattr(streak_repo, "supabase", type("S", (), {"table": lambda self, name: FakeTable()})())

        shield_used = streak_repo.update_streak_on_completion(1, "2026-07-15")
        assert shield_used is False
        assert captured["current_streak"] == 1

    def test_consecutive_day_increments_streak(self, monkeypatch):
        monkeypatch.setattr(streak_repo, "get_streak", lambda uid: {
            "current_streak": 4, "longest_streak": 9, "last_active_date": "2026-07-14",
            "shields_available": 1, "shields_used": 0,
        })
        captured = {}

        class FakeTable:
            def update(self, data):
                captured.update(data)
                return self

            def eq(self, *a):
                return self

            def execute(self):
                return self

        monkeypatch.setattr(streak_repo, "supabase", type("S", (), {"table": lambda self, name: FakeTable()})())

        shield_used = streak_repo.update_streak_on_completion(1, "2026-07-15")
        assert shield_used is False
        assert captured["current_streak"] == 5

    def test_missed_one_day_with_shield_available_saves_the_streak(self, monkeypatch):
        monkeypatch.setattr(streak_repo, "get_streak", lambda uid: {
            "current_streak": 4, "longest_streak": 9, "last_active_date": "2026-07-13",  # missed the 14th
            "shields_available": 1, "shields_used": 0,
        })
        captured = {}

        class FakeTable:
            def update(self, data):
                captured.update(data)
                return self

            def eq(self, *a):
                return self

            def execute(self):
                return self

        monkeypatch.setattr(streak_repo, "supabase", type("S", (), {"table": lambda self, name: FakeTable()})())

        shield_used = streak_repo.update_streak_on_completion(1, "2026-07-15")
        assert shield_used is True
        assert captured["current_streak"] == 5  # streak continued, not reset
        assert captured["shields_available"] == 0  # shield consumed

    def test_missed_two_or_more_days_resets_streak(self, monkeypatch):
        monkeypatch.setattr(streak_repo, "get_streak", lambda uid: {
            "current_streak": 4, "longest_streak": 9, "last_active_date": "2026-07-10",  # missed several days
            "shields_available": 1, "shields_used": 0,
        })
        captured = {}

        class FakeTable:
            def update(self, data):
                captured.update(data)
                return self

            def eq(self, *a):
                return self

            def execute(self):
                return self

        monkeypatch.setattr(streak_repo, "supabase", type("S", (), {"table": lambda self, name: FakeTable()})())

        streak_repo.update_streak_on_completion(1, "2026-07-15")
        assert captured["current_streak"] == 1  # streak reset


class TestBadgeRepoAwardIdempotency:
    def test_award_badge_swallows_duplicate_award_errors(self, monkeypatch):
        class FakeTable:
            def insert(self, *a, **kw):
                return self

            def execute(self):
                raise Exception("duplicate key value violates unique constraint")

        monkeypatch.setattr(badge_repo, "supabase", type("S", (), {"table": lambda self, name: FakeTable()})())

        badge_repo.award_badge(1, "streak_7")  # must not raise
