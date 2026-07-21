"""exceptions/ — custom exception classes, one concern per file.

These are additive: they give clearer, more diagnosable errors at a few
specific boundary points (database writes, Telegram API interaction), but
deliberately do NOT replace the existing None-return validation contract
used throughout utils/validators.py, utils/parsers.py, and utils/dates.py —
rewriting every call site of those to use exceptions instead would be a
large, risky change with no functional benefit, and the project's own
refactoring rules say not to rewrite working logic without reason.
"""
from exceptions.database import DatabaseError
from exceptions.validation import ValidationError
from exceptions.telegram import TelegramError

__all__ = ["DatabaseError", "ValidationError", "TelegramError"]
