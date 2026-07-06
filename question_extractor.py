"""
PDF se questions extract karne ka logic — bina kisi AI API ke, sirf regex/pattern matching se.
Ye kaam karta hai un PDFs pe jinme questions kisi standard format me likhe ho, jaise:
  Q1. ...      1. ...      1) ...      Question 1: ...
  (a) option   a) option   A. option
  Ans: b       Answer: (b)   Ans - b
"""
import re

QUESTION_START = re.compile(r"^(?:Q\.?\s?\d+[\.\)]|Question\s+\d+[:\.]|\d+[\.\)])\s*(.*)")
OPTION_LINE = re.compile(r"^\(?([a-dA-D])[\.\)]\s*(.*)")
ANSWER_LINE = re.compile(r"^(?:Ans(?:wer)?)\s*[:\-]?\s*\(?([a-dA-D])\)?", re.IGNORECASE)

# Common characters found in real-world PDFs that the default PDF font (Latin-1 only)
# can't render. Map the common ones to safe equivalents so text stays readable;
# anything left over gets replaced with '?' instead of crashing the whole extraction.
_CHAR_REPLACEMENTS = {
    "\u2018": "'", "\u2019": "'",       # smart single quotes
    "\u201c": '"', "\u201d": '"',       # smart double quotes
    "\u2013": "-", "\u2014": "-",       # en dash, em dash
    "\u2026": "...",                    # ellipsis
    "\u2022": "-",                      # bullet
    "\u00d7": "x",                      # multiplication sign
    "\u00f7": "/",                      # division sign
    "\u221a": "sqrt",                   # square root
    "\u00b0": " deg",                   # degree sign
    "\u2192": "->",                     # arrow
    "\u2264": "<=", "\u2265": ">=",     # less/greater-equal
    "\u00b1": "+/-",                    # plus-minus
}


def _sanitize_for_pdf(text: str) -> str:
    """Makes text safe for the core PDF font: replace known symbols, drop anything else unsupported."""
    for bad, good in _CHAR_REPLACEMENTS.items():
        text = text.replace(bad, good)
    # Anything still outside Latin-1 gets replaced with '?' rather than crashing PDF generation
    return text.encode("latin-1", errors="replace").decode("latin-1")


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
    """Builds a clean PDF: questions + options, with an answer key at the end."""
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, _sanitize_for_pdf(title), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    for q in questions:
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(0, 8, _sanitize_for_pdf(f"Q{q['number']}. {q['question']}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", size=11)
        for letter in ["a", "b", "c", "d"]:
            if letter in q["options"]:
                pdf.multi_cell(0, 7, _sanitize_for_pdf(f"   ({letter}) {q['options'][letter]}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

    if include_answers and any(q["answer"] for q in questions):
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.multi_cell(0, 10, "Answer Key", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)
        pdf.set_font("Helvetica", size=11)
        for q in questions:
            ans = q["answer"] or "-"
            pdf.multi_cell(0, 7, _sanitize_for_pdf(f"Q{q['number']}: {ans}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.output(output_path)
    return output_path
