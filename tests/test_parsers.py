"""Tests for utils/parsers.py — generic numeric parsing only, no domain rules."""
from utils import parsers


class TestParseNonnegInt:
    def test_accepts_valid_ints(self):
        assert parsers._parse_nonneg_int("42") == 42
        assert parsers._parse_nonneg_int("0") == 0

    def test_rejects_negative_and_non_numeric(self):
        assert parsers._parse_nonneg_int("-5") is None
        assert parsers._parse_nonneg_int("abc") is None
        assert parsers._parse_nonneg_int("4.5") is None


class TestParseNonnegNumber:
    def test_accepts_ints_and_decimals(self):
        assert parsers._parse_nonneg_number("100") == 100.0
        assert parsers._parse_nonneg_number("95.5") == 95.5

    def test_rejects_negative(self):
        assert parsers._parse_nonneg_number("-1") is None

    def test_rejects_non_numeric(self):
        assert parsers._parse_nonneg_number("abc") is None
