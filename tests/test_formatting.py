"""Tests for utils/formatting.py — pure text/visual formatting only."""
from utils import formatting


class TestEsc:
    def test_escapes_html_special_characters(self):
        assert formatting.esc("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
        assert formatting.esc("Rahul & Co") == "Rahul &amp; Co"

    def test_leaves_normal_text_untouched(self):
        assert formatting.esc("normal name") == "normal name"


class TestProgressBar:
    def test_zero_and_full(self):
        assert formatting._progress_bar(0, 10) == "░" * 10
        assert formatting._progress_bar(10, 10) == "█" * 10

    def test_partial(self):
        assert formatting._progress_bar(5, 10) == "█████░░░░░"

    def test_never_divides_by_zero(self):
        assert formatting._progress_bar(3, 0) == "░" * 10
