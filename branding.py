"""
Shared visual branding for Study Sync.

A small flat-icon owl mascot (matching the 🦉 Night Owl badge) gets drawn as a
subtle corner watermark on every image the bot generates — the study tree
today, and weekly report cards / achievement certificates later. Having one
shared, deterministic mascot across every generated image is what makes the
bot's output feel like a consistent, designed product rather than a pile of
disconnected scripts.

Pure Pillow, no extra assets — the owl is drawn procedurally so it always
renders identically and never depends on a missing image file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

_FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_BOLD_FONT_PATH = os.path.join(_FONT_DIR, "NotoSans-Bold.ttf")


def render_owl_icon(size: int = 64) -> Image.Image:
    """Returns a transparent-background RGBA image of the Study Sync owl mascot,
    `size` x `size` px. Drawn at 4x and downsampled for crisp, smooth edges
    even at small icon sizes."""
    SS = 4
    s = size * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    body_color = (0x8B, 0x5E, 0x3C, 255)
    belly_color = (0xF0, 0xDD, 0xB8, 255)
    wing_color = (0x6E, 0x48, 0x2D, 255)
    eye_white = (0xFF, 0xFF, 0xFF, 255)
    eye_black = (0x2B, 0x1E, 0x14, 255)
    beak_color = (0xE8, 0x9B, 0x3C, 255)

    cx, cy = s // 2, int(s * 0.54)
    r = int(s * 0.32)

    # Wings, drawn first so the body overlaps them
    wing_w, wing_h = int(r * 0.65), int(r * 1.5)
    draw.ellipse([cx - r - wing_w * 0.35, cy - wing_h * 0.25, cx - r + wing_w * 0.45, cy + wing_h * 0.55], fill=wing_color)
    draw.ellipse([cx + r - wing_w * 0.45, cy - wing_h * 0.25, cx + r + wing_w * 0.35, cy + wing_h * 0.55], fill=wing_color)

    # Ear tufts
    tuft_h = int(r * 0.55)
    draw.polygon(
        [(cx - r * 0.55, cy - r * 0.8), (cx - r * 0.78, cy - r * 0.8 - tuft_h), (cx - r * 0.25, cy - r * 0.95)],
        fill=body_color,
    )
    draw.polygon(
        [(cx + r * 0.55, cy - r * 0.8), (cx + r * 0.78, cy - r * 0.8 - tuft_h), (cx + r * 0.25, cy - r * 0.95)],
        fill=body_color,
    )

    # Round body
    draw.ellipse([cx - r, cy - r * 0.95, cx + r, cy + r * 1.05], fill=body_color)

    # Cream belly patch
    belly_r = r * 0.62
    draw.ellipse([cx - belly_r, cy - belly_r * 0.55, cx + belly_r, cy + belly_r * 1.35], fill=belly_color)

    # Big round eyes (the signature owl look)
    eye_r = r * 0.36
    eye_dx = r * 0.40
    eye_dy = -r * 0.10
    for sign in (-1, 1):
        ex, ey = cx + sign * eye_dx, cy + eye_dy
        draw.ellipse([ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r], fill=eye_white)
        pr = eye_r * 0.5
        draw.ellipse([ex - pr, ey - pr, ex + pr, ey + pr], fill=eye_black)

    # Small triangular beak
    beak_w, beak_h = r * 0.22, r * 0.30
    beak_y = cy + r * 0.08
    draw.polygon([(cx - beak_w, beak_y), (cx + beak_w, beak_y), (cx, beak_y + beak_h)], fill=beak_color)

    return img.resize((size, size), Image.LANCZOS)


def apply_watermark(
    base_img: Image.Image,
    label: str = "Study Sync",
    position: str = "bottom-right",
    icon_size: int = 34,
    margin: int = 16,
    opacity: int = 150,
) -> Image.Image:
    """Pastes the owl mascot + a small text label onto `base_img` at a low
    opacity in the given corner, so it reads as a subtle brand mark rather
    than clutter. Returns a new RGB image; `base_img` is left untouched."""
    base = base_img.convert("RGBA")
    w, h = base.size

    owl = render_owl_icon(icon_size)
    r, g, b, a = owl.split()
    a = a.point(lambda px: int(px * opacity / 255))
    owl.putalpha(a)

    try:
        font = ImageFont.truetype(_BOLD_FONT_PATH, size=max(12, icon_size // 3))
    except OSError:
        font = ImageFont.load_default()

    # Measure the label so the icon+text group can be positioned as one unit
    label_layer = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    bbox = ImageDraw.Draw(label_layer).textbbox((0, 0), label, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    gap = max(4, icon_size // 6)
    group_w = icon_size + gap + text_w
    group_h = max(icon_size, text_h)

    if position == "bottom-right":
        gx, gy = w - group_w - margin, h - group_h - margin
    elif position == "bottom-left":
        gx, gy = margin, h - group_h - margin
    elif position == "top-right":
        gx, gy = w - group_w - margin, margin
    else:  # top-left
        gx, gy = margin, margin

    base.alpha_composite(owl, dest=(gx, gy + (group_h - icon_size) // 2))

    text_layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    tdraw = ImageDraw.Draw(text_layer)
    tdraw.text(
        (gx + icon_size + gap, gy + (group_h - text_h) // 2 - bbox[1]),
        label,
        font=font,
        fill=(0x33, 0x2B, 0x22, opacity),
    )
    base.alpha_composite(text_layer)

    return base.convert("RGB")
