"""services/ — business logic and orchestration, one file per domain.

The rule that separates this layer from handlers/: a service function may
accept a `bot` (telegram.Bot) object to send notifications (deciding WHO to
notify and WHAT to say is business logic), but it never touches `Update` or
`CallbackQuery` objects — parsing what the user typed/tapped stays in the
handler layer. Services call repositories/ for data; they never talk to
Supabase directly.
"""
