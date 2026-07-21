"""Domain-specific validators — these combine parsing with a business rule
(e.g. 'daily study hours must be between 0.5 and 18'), unlike parsers.py
which only does generic type conversion."""


def _parse_hours(text: str):
    """Parses daily-study-hours input. Accepts whole or decimal numbers (e.g. '4', '3.5').
    Returns a float in a sane 0.5–18 range, or None if invalid."""
    text = text.strip().replace(",", ".")
    try:
        hours = float(text)
    except ValueError:
        return None
    if hours < 0.5 or hours > 18:
        return None
    return round(hours, 1)


def _parse_time_hhmm(text: str):
    """Parses a 24-hour HH:MM time string, validating actual hour/minute ranges
    (not just the shape) — this is the exact validation that used to be missing
    and let '29:99' through to crash later in db.add_custom_task. Returns the
    original 'HH:MM' string if valid, or None."""
    if not (len(text) == 5 and text[2] == ":" and text.replace(":", "").isdigit()):
        return None
    hh, mm = int(text[:2]), int(text[3:])
    if not (0 <= hh < 24 and 0 <= mm < 60):
        return None
    return text


def _parse_duration_to_minutes(text: str):
    """Parses '1h', '90m', '1.5h', '45' into minutes (int). Returns None if invalid."""
    text = text.strip().lower()
    try:
        if text.endswith("h"):
            return round(float(text[:-1]) * 60)
        if text.endswith("m"):
            return int(float(text[:-1]))
        if text.isdigit():
            return int(text)
    except ValueError:
        return None
    return None
