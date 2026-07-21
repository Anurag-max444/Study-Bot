"""handlers/ — Telegram command/callback/message handlers, one file per
domain. A handler's job is: receive the update, validate/parse what the
user sent, call a service (or a repository directly for simple reads), and
send a response. Business logic and orchestration live in services/, not
here — see services/__init__.py for that boundary.
"""
