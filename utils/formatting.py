"""Pure text/visual formatting helpers — no parsing, no validation, no I/O."""
import html


def esc(value) -> str:
    """Escapes user-provided text before it goes into an HTML-parse-mode message,
    so a stray '<', '>' or '&' in someone's name/topic can never break the message
    or get rendered as a tag."""
    return html.escape(str(value))


def _progress_bar(value: float, total: float, length: int = 10) -> str:
    """Renders a simple block progress bar, e.g. '███████░░░'. Safe against total=0."""
    pct = 0 if not total else max(0, min(1, value / total))
    filled = round(pct * length)
    return "█" * filled + "░" * (length - filled)
