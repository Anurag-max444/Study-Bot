"""Telegram-interaction errors raised by *our own* code.

Note: this is deliberately a different class from `telegram.error.TelegramError`
(python-telegram-bot's own base exception for API-level failures like rate
limits or bad requests). This one is for wrapping failures in *our* logic
around Telegram calls — e.g. "tried to send a file but it didn't exist" —
so global_error_handler can tell "our code broke" apart from "Telegram's API
rejected us"."""


class TelegramError(Exception):
    """Raised when our own code's interaction with the Telegram API fails
    in a way that's not just a bare API-level error.

    Attributes:
        action: short description of what we were trying to do,
            e.g. "send_document" or "edit_message_text".
        original_error: the underlying exception that was caught.
    """

    def __init__(self, action: str, original_error: Exception):
        self.action = action
        self.original_error = original_error
        super().__init__(f"Telegram action '{action}' failed: {original_error}")
