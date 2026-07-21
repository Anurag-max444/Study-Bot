"""Date parsing — kept separate from parsers.py since date formats have
their own rules (multiple accepted formats, 'today' synonyms, 2-digit-year
expansion) that don't belong mixed in with generic numeric parsing."""
from datetime import date as _date


def _parse_test_date(text: str):
    """Accepts 'aaj'/'today'/'aj' for today, or a DD-MM-YYYY / DD/MM/YYYY date.
    Returns a date object, or None if unparseable."""
    text = text.strip().lower()
    if text in ("aaj", "today", "aj"):
        return _date.today()
    for sep in ("-", "/"):
        parts = text.split(sep)
        if len(parts) == 3:
            try:
                day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                if year < 100:
                    year += 2000
                return _date(year, month, day)
            except ValueError:
                return None
    return None
