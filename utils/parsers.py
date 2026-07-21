"""Generic numeric parsers — convert user-typed text to numbers, with only
the most basic sanity checks (non-negative). Domain-specific range rules
(e.g. 'daily study hours must be 0.5-18') belong in validators.py instead."""


def _parse_nonneg_int(text: str):
    """Parses a plain non-negative whole number. Returns None if invalid."""
    text = text.strip()
    if not text.isdigit():
        return None
    return int(text)


def _parse_nonneg_number(text: str):
    """Parses a non-negative whole or decimal number (e.g. total marks). Returns None if invalid."""
    text = text.strip().replace(",", ".")
    try:
        value = float(text)
    except ValueError:
        return None
    if value < 0:
        return None
    return value
