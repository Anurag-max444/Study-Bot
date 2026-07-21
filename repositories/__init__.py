"""repositories/ — all database read/write operations, one file per table
or tightly-related concern. No Telegram code lives here; these functions
only talk to the database.

A few functions (marked in their docstrings) orchestrate across more than
one repository — e.g. completing a session also updates the streak, checks
for new badges, and schedules a revision. That orchestration logic will
move to a dedicated services/ layer in a later phase; for now it's kept
exactly as it worked before, just relocated.
"""
