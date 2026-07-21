"""Tests for keyboards/reply.py — persistent ReplyKeyboardMarkup builders."""
from keyboards.reply import main_menu_keyboard
import handlers.onboarding as onboarding


class TestMainMenuKeyboard:
    def test_has_exactly_the_four_requested_buttons(self):
        kb = main_menu_keyboard()
        labels = [btn.text for row in kb.keyboard for btn in row]
        assert labels == ["/addtask", "/mytopics", "/mytree", "/help"]

    def test_onboarding_handler_reexport_is_the_same_function(self):
        """handlers/onboarding.py imports main_menu_keyboard from
        keyboards/reply.py — confirms the re-export wasn't accidentally
        dropped during the Phase 6 handlers/ relocation."""
        assert onboarding.main_menu_keyboard is main_menu_keyboard
