"""Database-layer errors — raised when a db.py operation fails, wrapping the
original Supabase/postgrest exception with clearer context (which operation,
for which record) so logs are actually useful for debugging instead of a
bare postgrest stack trace."""


class DatabaseError(Exception):
    """Raised when a database read/write fails unexpectedly.

    Attributes:
        operation: short description of what was being attempted,
            e.g. "add_mock_test" or "add_custom_task".
        original_error: the underlying exception that was caught, kept
            around for full detail in logs (via `raise ... from original_error`).
    """

    def __init__(self, operation: str, original_error: Exception):
        self.operation = operation
        self.original_error = original_error
        super().__init__(f"Database operation '{operation}' failed: {original_error}")
