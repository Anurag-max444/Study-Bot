"""Tests for utils/dates.py — date-specific parsing only."""
from datetime import date

from utils import dates


class TestParseTestDate:
    def test_accepts_aaj_today_synonyms(self):
        assert dates._parse_test_date("aaj") == date.today()
        assert dates._parse_test_date("today") == date.today()
        assert dates._parse_test_date("aj") == date.today()

    def test_accepts_dd_mm_yyyy_with_dash_or_slash(self):
        assert dates._parse_test_date("11-07-2026") == date(2026, 7, 11)
        assert dates._parse_test_date("11/07/2026") == date(2026, 7, 11)

    def test_expands_two_digit_year(self):
        assert dates._parse_test_date("11-07-26") == date(2026, 7, 11)

    def test_rejects_garbage(self):
        assert dates._parse_test_date("not a date") is None
        assert dates._parse_test_date("32-13-2026") is None
