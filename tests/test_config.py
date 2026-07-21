"""Sanity tests for the Phase 1 centralization: config.py, constants.py,
logger.py. Mostly guards against someone accidentally re-scattering these
values back into individual feature modules."""
import logging

import config
import constants
import handlers.vault as vault
import handlers.mocktest as mocktest
import bot
import db


def test_config_exposes_all_expected_settings():
    assert hasattr(config, "TELEGRAM_BOT_TOKEN")
    assert hasattr(config, "SUPABASE_URL")
    assert hasattr(config, "SUPABASE_KEY")
    assert hasattr(config, "VAULT_PASSWORD")
    assert hasattr(config, "PORT")
    assert isinstance(config.PORT, int)


def test_vault_password_comes_from_config():
    assert vault.VAULT_PASSWORD == config.VAULT_PASSWORD


def test_bot_token_comes_from_config():
    assert bot.BOT_TOKEN == config.TELEGRAM_BOT_TOKEN


def test_db_client_was_built_from_config_credentials():
    # db.py no longer keeps its own SUPABASE_URL/KEY constants — it should
    # get them from config.py instead.
    assert not hasattr(db, "SUPABASE_URL")
    assert not hasattr(db, "SUPABASE_KEY")


def test_exam_labels_come_from_constants():
    import handlers.onboarding as onboarding
    assert onboarding.EXAM_LABELS is constants.EXAM_LABELS
    assert constants.EXAM_LABELS["ssc_cgl"] == "SSC CGL"


def test_vault_command_names_come_from_constants():
    assert vault.VAULT_VIEW_COMMAND == constants.VAULT_VIEW_COMMAND == "admin"
    assert vault.VAULT_SAVE_COMMAND == constants.VAULT_SAVE_COMMAND == "admins"


def test_mocktest_step_count_comes_from_constants():
    assert mocktest.MOCKTEST_TOTAL_STEPS == constants.MOCKTEST_TOTAL_STEPS == 16
    assert mocktest.MOCKTEST_SKIP_WORDS == constants.MOCKTEST_SKIP_WORDS


def test_logging_was_configured(caplog):
    # logger.py's setup_logging() should have run at import time; a basic
    # sanity check that the root logger accepts INFO-level messages.
    root = logging.getLogger()
    assert root.level <= logging.INFO or root.getEffectiveLevel() <= logging.INFO
