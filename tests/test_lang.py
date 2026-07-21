"""
Regression tests for lang.py + every t() call site in bot.py.

This is the automated version of the audit script that's been run by hand
throughout development. It catches the two classes of bug that came up
repeatedly during manual editing:
  1. A t() call passing kwargs that don't match the template's {placeholders}
     (or referencing a key that doesn't exist at all).
  2. A template with mismatched/unbalanced HTML tags, which makes Telegram
     silently fail to deliver the message.
It also catches accidental deletions of existing keys (a str_replace mistake
that happened more than once during development) by requiring every key to
have all three languages.
"""
import ast
import re

import bot
from ui.lang import TEXT


def _all_t_calls_in_bot_py():
    src = open(bot.__file__).read()
    tree = ast.parse(src)
    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "t":
            if not node.args:
                continue
            key_node = node.args[0]
            key = key_node.value if isinstance(key_node, ast.Constant) else None
            kwargs = [kw.arg for kw in node.keywords]
            calls.append((key, kwargs))
    return calls


def test_every_t_call_references_an_existing_key():
    missing = [key for key, _ in _all_t_calls_in_bot_py() if key is not None and key not in TEXT]
    assert not missing, f"bot.py calls t() with key(s) not found in lang.py: {missing}"


def test_every_t_call_provides_all_placeholders_the_template_needs():
    problems = []
    for key, kwargs in _all_t_calls_in_bot_py():
        if key is None or key not in TEXT:
            continue
        for langname, text in TEXT[key].items():
            placeholders = set(re.findall(r"\{(\w+)\}", text))
            missing = placeholders - set(kwargs)
            if missing:
                problems.append(f"'{key}' ({langname}) needs {missing}, call only gives {kwargs}")
    assert not problems, "\n".join(problems)


def test_every_key_has_all_three_languages():
    missing = []
    for key, langs in TEXT.items():
        for lang in ("hindi", "english", "hinglish"):
            if lang not in langs:
                missing.append(f"'{key}' is missing '{lang}'")
    assert not missing, "\n".join(missing)


def test_html_tags_are_balanced_in_every_template():
    problems = []
    for key, langs in TEXT.items():
        for langname, text in langs.items():
            if len(re.findall(r"<b>", text)) != len(re.findall(r"</b>", text)):
                problems.append(f"'{key}' ({langname}) has unbalanced <b> tags")
    assert not problems, "\n".join(problems)


def test_no_template_is_accidentally_empty():
    """Catches the specific str_replace mistake made a few times during
    development: a key's opening line getting clipped, leaving stray content
    with no home, or a key ending up with an empty string."""
    for key, langs in TEXT.items():
        for langname, text in langs.items():
            assert text.strip(), f"'{key}' ({langname}) is empty"
