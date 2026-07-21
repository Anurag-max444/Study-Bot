"""
Backward-compatible facade over repositories/.

The actual database code now lives in repositories/ (one file per table —
see that package's docstring). This module exists purely so every existing
caller across the project can keep saying `import db` then `db.get_user(...)`
without needing to know or care which specific repository file a function
lives in. New code is welcome to import directly from repositories/ instead.
"""
from database.client import supabase  # noqa: F401 — re-exported for anything that still expects db.supabase

from repositories.user_repo import get_user, get_all_onboarded_users, create_user, update_user
from repositories.syllabus_repo import add_syllabus_topics
from repositories.streak_repo import get_streak, update_streak_on_completion
from repositories.badge_repo import BADGES, get_user_badges, award_badge, check_and_award_badges
from repositories.progress_repo import process_completion, get_tree_growth_score, get_days_since_active
from repositories.task_repo import (
    add_custom_task, get_custom_tasks, remove_custom_task, delete_custom_task_by_id, get_due_custom_tasks,
)
from repositories.session_repo import (
    create_task_session, mark_session_completed, get_session, get_due_followups,
    mark_followup_sent, get_study_log,
)
from repositories.revision_repo import (
    REVISION_INTERVALS, create_revisions_for_topic, get_due_revisions,
    mark_revision_notified, mark_revision_completed, get_pending_revisions,
)
from repositories.state_repo import get_state, set_state
from repositories.mocktest_repo import add_mock_test, get_mock_tests, get_mock_test
from repositories.vault_repo import add_vault_image, get_vault_images, delete_vault_image
