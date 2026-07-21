"""Validation errors — available for validation logic that genuinely needs
to signal *why* something was rejected (not just that it was).

Note: utils/validators.py, utils/parsers.py, and utils/dates.py intentionally
keep their existing "return None on invalid input" contract rather than
raising this, since every one of their call sites across bot.py/mocktest.py
already checks for None — switching that to exceptions would mean rewriting
every call site for no functional benefit. This class exists for new
validation needs where a reason/field is genuinely useful to carry."""


class ValidationError(Exception):
    """Raised when input fails validation and the caller needs to know why.

    Attributes:
        field: the name of the field/input that failed validation.
        reason: a short, human-readable explanation.
    """

    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"Validation failed for '{field}': {reason}")
