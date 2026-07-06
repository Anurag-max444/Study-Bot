"""
PDF se questions extract karne ka logic — bina kisi AI API ke, sirf regex/pattern matching se.
Ye kaam karta hai un PDFs pe jinme questions kisi standard format me likhe ho, jaise:
  Q1. ...      1. ...      1) ...      Question 1: ...
  (a) option   a) option   A. option
  Ans: b       Answer: (b)   Ans - b

Hindi (Devanagari) aur English dono ek saath support karta hai PDF output me,
bundled Noto Sans / Noto Sans Devanagari fonts ki madad se.
"""
import os
import re

QUESTION_START = re.compile(r"^(?:Q\.?\s?\d+[\.\)]|Question\s+\d+[:\.]|\d+[\.\)])\s*(.*)")
OPTION_LINE = re.compile(r"^\(?([a-dA-D])[\.\)]\s*(.*)")
ANSWER_LINE = re.compile(r"^(?:Ans(?:wer)?)\s*[:\-]?\s*\(?([a-dA-D])\)?", re.IGNORECASE)

_FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

# Known problem characters (present in real PDFs) that even our Unicode fonts miss.
# Mapped to safe equivalents; anything else unsupported gets replaced with '?' per-font
# using the font's own character map, so PDF generation never crashes.
_CHAR_REPLACEMENTS = {
    "\u221a": "sqrt",   # square root
    "\u2192": "->",     # arrow
}

_cmap_cache = {}


def _sanitize_known(text: str) -> str:
    for bad, good in _CHAR_REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text


def _get_cmap(ttf_path: str):
    if ttf_path not in _cmap_cache:
        from fontTools.ttLib import TTFont
        _cmap_cache[ttf_path] = TTFont(ttf_path).getBestCmap()
    return _cmap_cache[ttf_path]


def _filter_for_font(text: str, ttf_path: str) -> str:
    """Replaces any character the given font can't render with '?', so writing never crashes."""
    cmap = _get_cmap(ttf_path)
    return "".join(ch if (ord(ch) in cmap or ch in " \n\t") else "?" for ch in text)


def _is_devanagari(ch: str) -> bool:
    return "\u0900" <= ch <= "\u097f"


def _split_runs(text: str):
    """Splits text into consecutive runs of (is_devanagari, chunk)."""
    if not text:
        return []
    runs = []
    current_script = _is_devanagari(text[0])
    start = 0
    for i in range(1, len(text)):
        script = _is_devanagari(text[i])
        if script != current_script:
            runs.append((current_script, text[start:i]))
            start = i
            current_script = script
    runs.append((current_script, text[start:]))
    return runs


def _write_mixed_line(pdf, text: str, size: int, bold: bool = False, line_h: int = 7):
    """Writes a line of possibly-mixed Hindi+English text, switching fonts per script run."""
    text = _sanitize_known(text)
    style = "B" if bold else ""
    for is_dev, chunk in _split_runs(text):
        if is_dev:
            font_name, ttf_path = "NotoDevanagari", os.path.join(
                _FONTS_DIR, f"NotoSansDevanagari-{'Bold' if bold else 'Regular'}.ttf"
            )
        else:
            font_name, ttf_path = "NotoSans", os.path.join(
                _FONTS_DIR, f"NotoSans-{'Bold' if bold else 'Regular'}.ttf"
            )
        pdf.set_font(font_name, style, size)
        pdf.write(line_h, _filter_for_font(chunk, ttf_path))
    pdf.ln(line_h)


def extract_questions_from_text(raw_text: str):
    """Returns list of dicts: {number, question, options: {a,b,c,d}, answer}"""
    lines = [l.strip() for l in raw_text.split("\n")]
    questions = []
    current = None

    for line in lines:
        if not line:
            continue

        ans_match = ANSWER_LINE.match(line)
        if ans_match and current:
            current["answer"] = ans_match.group(1).lower()
            continue

        opt_match = OPTION_LINE.match(line)
        if opt_match and current:
            letter, text = opt_match.group(1).lower(), opt_match.group(2).strip()
            current["options"][letter] = text
            continue

        q_match = QUESTION_START.match(line)
        if q_match:
            if current and (current["question"] or current["options"]):
                questions.append(current)
            current = {
                "number": len(questions) + 1,
                "question": q_match.group(1).strip(),
                "options": {},
                "answer": None,
            }
            continue

        # Continuation line (question text wrapped to next line)
        if current:
            if current["options"]:
                # append to last option if mid-option wrap
                last_key = list(current["options"].keys())[-1]
                current["options"][last_key] += " " + line
            else:
                current["question"] += " " + line

    if current and (current["question"] or current["options"]):
        questions.append(current)

    # Filter out junk: a "question" needs at least 2 options detected to be considered valid
    valid = [q for q in questions if len(q["options"]) >= 2]
    return valid


def generate_questions_pdf(questions, output_path: str, title: str = "Extracted Questions", include_answers: bool = True):
    """Builds a clean PDF: questions + options, with an answer key at the end. Supports Hindi + English."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_font("NotoSans", "", os.path.join(_FONTS_DIR, "NotoSans-Regular.ttf"))
    pdf.add_font("NotoSans", "B", os.path.join(_FONTS_DIR, "NotoSans-Bold.ttf"))
    pdf.add_font("NotoDevanagari", "", os.path.join(_FONTS_DIR, "NotoSansDevanagari-Regular.ttf"))
    pdf.add_font("NotoDevanagari", "B", os.path.join(_FONTS_DIR, "NotoSansDevanagari-Bold.ttf"))

    pdf.add_page()
    _write_mixed_line(pdf, title, size=16, bold=True, line_h=10)
    pdf.ln(4)

    for q in questions:
        _write_mixed_line(pdf, f"Q{q['number']}. {q['question']}", size=12, bold=True, line_h=8)
        for letter in ["a", "b", "c", "d"]:
            if letter in q["options"]:
                _write_mixed_line(pdf, f"   ({letter}) {q['options'][letter]}", size=11, line_h=7)
        pdf.ln(3)

    if include_answers and any(q["answer"] for q in questions):
        pdf.add_page()
        _write_mixed_line(pdf, "Answer Key", size=14, bold=True, line_h=10)
        pdf.ln(2)
        for q in questions:
            ans = q["answer"] or "-"
            _write_mixed_line(pdf, f"Q{q['number']}: {ans}", size=11, line_h=7)

    pdf.output(output_path)
    return output_path
