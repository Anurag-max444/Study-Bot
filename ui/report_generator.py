"""
Weekly PDF Report Card — ek visual summary jo har user ko uske pichhle 7 din
ki study activity dikhata hai: daily study-minutes bar chart, current streak,
is hafte ke completed sessions, aur total badges.

Do tarah se milta hai:
  1. Manual: /report command se turant.
  2. Automatic: har Sunday raat scheduler khud bhej deta hai (bot.py mein).

Design ek hi flat-illustration style follow karta hai jo /mytree image mein hai
(gradient background, rounded card, owl watermark) — taaki har generated file
ek hi product ka hissa lage, alag-alag script jaisa nahi.
"""
import os
from datetime import date, timedelta
from PIL import Image, ImageDraw, ImageFont

import config
from ui.branding import apply_watermark

_FONT_DIR = config.FONTS_DIR

WEEKDAY_SHORT = {
    "hindi": ["सोम", "मंगल", "बुध", "गुरु", "शुक्र", "शनि", "रवि"],
    "english": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    "hinglish": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
}

LABELS = {
    "title": {"hindi": "साप्ताहिक रिपोर्ट", "english": "Weekly Report", "hinglish": "Weekly Report"},
    "streak": {"hindi": "स्ट्रीक", "english": "Streak", "hinglish": "Streak"},
    "hours": {"hindi": "इस हफ्ते", "english": "This week", "hinglish": "Is hafte"},
    "sessions": {"hindi": "सेशन पूरे", "english": "Sessions done", "hinglish": "Sessions done"},
    "badges": {"hindi": "बैज", "english": "Badges", "hinglish": "Badges"},
    "no_data": {
        "hindi": "इस हफ्ते कोई सेशन दर्ज नहीं — /addtask से शुरुआत कीजिए!",
        "english": "No sessions logged this week — start with /addtask!",
        "hinglish": "Is hafte koi session log nahi hua — /addtask se shuru kijiye!",
    },
}


def _font(name: str, size: int, lang: str):
    devanagari = lang == "hindi"
    fname = {
        ("regular", False): "NotoSans-Regular.ttf",
        ("bold", False): "NotoSans-Bold.ttf",
        ("regular", True): "NotoSansDevanagari-Regular.ttf",
        ("bold", True): "NotoSansDevanagari-Bold.ttf",
    }[(name, devanagari)]
    return ImageFont.truetype(os.path.join(_FONT_DIR, fname), size=size)


def _text_w(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


def _rounded_card(draw, box, fill, radius=16):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def build_weekly_report_image(
    name: str,
    lang: str,
    daily_minutes: list,  # 7 ints, oldest -> newest (today last)
    streak: int,
    longest_streak: int,
    sessions_done: int,
    badge_count: int,
    total_badges: int,
    size=(700, 900),
) -> Image.Image:
    lang = lang if lang in ("hindi", "english", "hinglish") else "hinglish"
    W, H = size
    bg = (0xFA, 0xF7, 0xF0)
    accent = (0x3F, 0x9C, 0x53)
    accent_light = (0x5C, 0xB8, 0x6A)
    text_dark = (0x2B, 0x2B, 0x2B)
    text_muted = (0x7A, 0x7A, 0x74)
    card_bg = (0xFF, 0xFF, 0xFF)

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    title_font = _font("bold", 34, lang)
    sub_font = _font("regular", 18, lang)
    stat_num_font = _font("bold", 30, lang)
    stat_label_font = _font("regular", 15, lang)
    bar_label_font = _font("regular", 15, lang)
    bar_value_font = _font("bold", 14, lang)

    # Header
    today = date.today()
    week_start = today - timedelta(days=6)
    date_range = f"{week_start.strftime('%d %b')} – {today.strftime('%d %b')}"

    draw.rectangle([0, 0, W, 140], fill=accent)
    draw.text((40, 34), f"📊 {LABELS['title'][lang]}", font=title_font, fill=(255, 255, 255))
    draw.text((40, 82), f"{name}  •  {date_range}", font=sub_font, fill=(230, 245, 234))

    # Bar chart
    chart_top, chart_bottom = 190, 430
    chart_left, chart_right = 60, W - 60
    max_minutes = max([*daily_minutes, 30])  # never let a single session look "full height"
    n = len(daily_minutes)
    slot_w = (chart_right - chart_left) / n
    bar_w = slot_w * 0.5

    _rounded_card(draw, [30, 170, W - 30, chart_bottom + 50], card_bg)
    chart_title = {"hindi": "रोज़ाना पढ़ाई (मिनट)", "english": "Daily study time (minutes)",
                   "hinglish": "Daily study time (minutes)"}[lang]
    draw.text((50, 185), "🗓️  " + chart_title, font=sub_font, fill=text_dark)

    weekday_names = WEEKDAY_SHORT[lang]
    for i, minutes in enumerate(daily_minutes):
        day_idx = (today - timedelta(days=n - 1 - i)).weekday()  # 0=Mon
        cx = chart_left + slot_w * i + slot_w / 2
        bar_h = 0 if max_minutes == 0 else (minutes / max_minutes) * (chart_bottom - chart_top)
        top = chart_bottom - bar_h
        color = accent if minutes > 0 else (0xE4, 0xE0, 0xD5)
        draw.rounded_rectangle([cx - bar_w / 2, top, cx + bar_w / 2, chart_bottom], radius=8, fill=color)
        if minutes > 0:
            label = f"{minutes}"
            lw = _text_w(draw, label, bar_value_font)
            draw.text((cx - lw / 2, top - 20), label, font=bar_value_font, fill=accent)
        wd = weekday_names[day_idx]
        ww = _text_w(draw, wd, bar_label_font)
        draw.text((cx - ww / 2, chart_bottom + 12), wd, font=bar_label_font, fill=text_muted)

    if sum(daily_minutes) == 0:
        msg = LABELS["no_data"][lang]
        mw = _text_w(draw, msg, sub_font)
        draw.text(((W - mw) / 2, (chart_top + chart_bottom) / 2), msg, font=sub_font, fill=text_muted)

    # Stat cards row
    stats = [
        ("🔥", str(streak), f"{LABELS['streak'][lang]} ({longest_streak} best)"),
        ("⏱️", f"{round(sum(daily_minutes) / 60, 1)}h", LABELS["hours"][lang]),
        ("✅", str(sessions_done), LABELS["sessions"][lang]),
        ("🎖️", f"{badge_count}/{total_badges}", LABELS["badges"][lang]),
    ]
    card_top = chart_bottom + 90
    card_h = 150
    gap = 20
    card_w = (W - 60 - gap * 3) / 4
    for i, (icon, value, label) in enumerate(stats):
        x0 = 30 + i * (card_w + gap)
        _rounded_card(draw, [x0, card_top, x0 + card_w, card_top + card_h], card_bg)
        draw.text((x0 + card_w / 2 - 16, card_top + 16), icon, font=_font("regular", 26, lang), fill=text_dark)
        vw = _text_w(draw, value, stat_num_font)
        draw.text((x0 + card_w / 2 - vw / 2, card_top + 58), value, font=stat_num_font, fill=accent_light)
        # label may wrap onto two lines if it's a touch too wide for the card
        words = label.split(" ")
        line1, line2 = label, ""
        if _text_w(draw, label, stat_label_font) > card_w - 12 and len(words) > 1:
            mid = len(words) // 2
            line1, line2 = " ".join(words[:mid]), " ".join(words[mid:])
        lw1 = _text_w(draw, line1, stat_label_font)
        draw.text((x0 + card_w / 2 - lw1 / 2, card_top + 105), line1, font=stat_label_font, fill=text_muted)
        if line2:
            lw2 = _text_w(draw, line2, stat_label_font)
            draw.text((x0 + card_w / 2 - lw2 / 2, card_top + 124), line2, font=stat_label_font, fill=text_muted)

    return apply_watermark(img, position="bottom-right")


def generate_weekly_report_pdf(name, lang, daily_minutes, streak, longest_streak,
                                sessions_done, badge_count, total_badges, output_path):
    """Renders the report card as an image, then wraps it in a single-page PDF."""
    img = build_weekly_report_image(
        name, lang, daily_minutes, streak, longest_streak, sessions_done, badge_count, total_badges
    )
    png_path = output_path.rsplit(".", 1)[0] + "_card.png"
    img.save(png_path)

    from fpdf import FPDF
    pdf = FPDF(unit="pt", format=[img.width, img.height])
    pdf.add_page()
    pdf.image(png_path, x=0, y=0, w=img.width, h=img.height)
    pdf.output(output_path)

    try:
        os.remove(png_path)
    except OSError:
        pass

    return output_path
