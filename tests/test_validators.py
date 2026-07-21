"""Tests for utils/validators.py — domain-rule-aware validation (parse + a
business rule), as opposed to test_parsers.py's generic type conversion."""
from utils import validators


class TestParseHours:
    def test_accepts_whole_and_decimal_numbers(self):
        assert validators._parse_hours("4") == 4.0
        assert validators._parse_hours("3.5") == 3.5

    def test_accepts_comma_as_decimal_separator(self):
        assert validators._parse_hours("3,5") == 3.5

    def test_rejects_out_of_range(self):
        assert validators._parse_hours("0") is None
        assert validators._parse_hours("25") is None

    def test_rejects_non_numeric(self):
        assert validators._parse_hours("abc") is None
        assert validators._parse_hours("") is None
