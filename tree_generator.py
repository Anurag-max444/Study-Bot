"""
Study Tree — ek visual tree jo user ki consistency ke hisaab se grow hota hai.
Bina kisi API ke, sirf Pillow (PIL) se procedurally draw kiya jata hai.

Growth stages (0-5) total completed activities (topics + sessions) par based hai.
Agar user 2+ din se inactive hai, tree "wilted" (murjha hua) dikhta hai — motivate
karne ke liye ki wapas aa jao.

Rendering notes:
- Everything is drawn at 2x resolution and downsampled at the end (supersampling),
  which is a plain-Pillow trick to get smooth anti-aliased edges without any
  extra dependency.
- A fixed random seed is used for every organic-looking element (canopy clusters,
  flowers, fallen leaves) so the same stage always renders identically — no
  flaky/flickering look between calls.
"""
import random
from PIL import Image, ImageDraw, ImageFilter

STAGE_NAMES = {
    0: {"hindi": "बीज", "english": "Seed", "hinglish": "Beej"},
    1: {"hindi": "अंकुर", "english": "Sprout", "hinglish": "Ankur"},
    2: {"hindi": "पौधा", "english": "Sapling", "hinglish": "Sapling"},
    3: {"hindi": "युवा पेड़", "english": "Young Tree", "hinglish": "Young Tree"},
    4: {"hindi": "परिपक्व पेड़", "english": "Mature Tree", "hinglish": "Mature Tree"},
    5: {"hindi": "खिलता पेड़", "english": "Blooming Tree", "hinglish": "Blooming Tree"},
}

SS = 2  # supersampling factor for anti-aliasing


def get_stage(growth_score: int) -> int:
    if growth_score <= 0:
        return 0
    if growth_score < 5:
        return 1
    if growth_score < 15:
        return 2
    if growth_score < 30:
        return 3
    if growth_score < 60:
        return 4
    return 5


def _lerp_color(c1, c2, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(c1, c2))


def _vertical_gradient(draw, box, top_color, bottom_color):
    x0, y0, x1, y1 = box
    height = max(1, y1 - y0)
    for i in range(height):
        t = i / height
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=_lerp_color(top_color, bottom_color, t))


def _glow_circle(base_img, center, radius, color, blur_radius):
    """Draws a soft glowing circle (used for the sun) by blurring a solid circle
    on its own transparent layer before compositing it onto the scene."""
    glow = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    cx, cy = center
    gdraw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(blur_radius))
    base_img.alpha_composite(glow)


def _canopy_cluster(draw, cx, cy, spread, base_radius, tones, rng, count):
    """A rounded, organic-looking canopy made of overlapping jittered circles
    instead of a few perfect concentric ellipses."""
    for _ in range(count):
        dx = rng.randint(-spread, spread)
        dy = rng.randint(-int(spread * 0.7), int(spread * 0.5))
        r = base_radius + rng.randint(-base_radius // 4, base_radius // 4)
        tone = tones[rng.randint(0, len(tones) - 1)]
        draw.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r], fill=tone)


def generate_tree_image(stage: int, wilted: bool, output_path: str, size=(600, 600)):
    w, h = size[0] * SS, size[1] * SS

    if wilted:
        sky_top, sky_bottom = (0xE8, 0xE1, 0xCE), (0xF5, 0xF1, 0xE4)
        ground_top, ground_bottom = (0xC2, 0xB3, 0x88), (0xA8, 0x99, 0x70)
        trunk_color = (0x8D, 0x7B, 0x6E)
        trunk_shade = (0x74, 0x64, 0x58)
        leaf_tones = [(0xA1, 0x88, 0x7F), (0xB0, 0x9A, 0x8A), (0x8C, 0x7A, 0x6A)]
        sun_color = (0xE8, 0xDE, 0xC0, 90)
    else:
        sky_top, sky_bottom = (0xBF, 0xE3, 0xFF), (0xEC, 0xF8, 0xFF)
        ground_top, ground_bottom = (0x8F, 0xC7, 0x54), (0x6E, 0xA8, 0x3A)
        trunk_color = (0x7A, 0x53, 0x42)
        trunk_shade = (0x5A, 0x3B, 0x2F)
        leaf_tones = [(0x3F, 0x9C, 0x53), (0x5C, 0xB8, 0x6A), (0x2E, 0x7D, 0x42)]
        sun_color = (0xFF, 0xF3, 0xB0, 130)

    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    ground_y = h - int(70 * SS * (size[1] / 600))
    _vertical_gradient(draw, (0, 0, w, ground_y), sky_top, sky_bottom)

    # Soft sun glow tucked in the corner
    sun_center = (int(w * 0.82), int(h * 0.14))
    _glow_circle(img, sun_center, 38 * SS, sun_color, 22 * SS)
    draw.ellipse(
        [sun_center[0] - 20 * SS, sun_center[1] - 20 * SS, sun_center[0] + 20 * SS, sun_center[1] + 20 * SS],
        fill=(sun_color[0], sun_color[1], sun_color[2], 255),
    )

    _vertical_gradient(draw, (0, ground_y, w, h), ground_top, ground_bottom)
    # Horizon highlight so the ground doesn't look like a flat cut line
    draw.line([(0, ground_y), (w, ground_y)], fill=_lerp_color(ground_top, (255, 255, 255), 0.25), width=max(1, SS))

    cx = w // 2
    rng = random.Random(42 + stage)  # deterministic per stage

    # Soft contact shadow under whatever is standing on the ground
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    shadow_w = [26, 40, 70, 110, 150, 150][stage] * SS
    sdraw.ellipse([cx - shadow_w, ground_y - 8 * SS, cx + shadow_w, ground_y + 14 * SS], fill=(0, 0, 0, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6 * SS))
    img.alpha_composite(shadow)

    def tapered_trunk(top_y, base_width, top_width):
        draw.polygon(
            [
                (cx - base_width, ground_y), (cx + base_width, ground_y),
                (cx + top_width, top_y), (cx - top_width, top_y),
            ],
            fill=trunk_color,
        )
        # a thin shaded strip down one side for a touch of depth
        draw.polygon(
            [(cx, ground_y), (cx + base_width, ground_y), (cx + top_width, top_y), (cx, top_y)],
            fill=trunk_shade,
        )

    if stage == 0:
        draw.ellipse([cx - 16 * SS, ground_y - 10 * SS, cx + 16 * SS, ground_y + 10 * SS], fill=(0x6D, 0x4C, 0x41))
        draw.ellipse([cx - 16 * SS, ground_y - 10 * SS, cx, ground_y + 10 * SS], fill=(0x5A, 0x3D, 0x33))

    elif stage == 1:
        tapered_trunk(ground_y - 48 * SS, 5 * SS, 3 * SS)
        _canopy_cluster(draw, cx, ground_y - 62 * SS, 22 * SS, 16 * SS, leaf_tones, rng, 9)

    elif stage == 2:
        tapered_trunk(ground_y - 95 * SS, 8 * SS, 4 * SS)
        _canopy_cluster(draw, cx, ground_y - 120 * SS, 42 * SS, 26 * SS, leaf_tones, rng, 16)

    elif stage == 3:
        tapered_trunk(ground_y - 145 * SS, 11 * SS, 5 * SS)
        _canopy_cluster(draw, cx, ground_y - 165 * SS, 62 * SS, 34 * SS, leaf_tones, rng, 22)
        _canopy_cluster(draw, cx, ground_y - 215 * SS, 40 * SS, 26 * SS, leaf_tones, rng, 14)

    else:  # stage 4 and 5 share the same full canopy
        tapered_trunk(ground_y - 185 * SS, 14 * SS, 6 * SS)
        _canopy_cluster(draw, cx, ground_y - 200 * SS, 90 * SS, 42 * SS, leaf_tones, rng, 30)
        _canopy_cluster(draw, cx, ground_y - 265 * SS, 65 * SS, 34 * SS, leaf_tones, rng, 22)
        _canopy_cluster(draw, cx, ground_y - 310 * SS, 40 * SS, 24 * SS, leaf_tones, rng, 12)

        if stage == 5 and not wilted:
            petal_color = (0xEC, 0x6F, 0x9A)
            center_color = (0xFF, 0xE0, 0x82)
            flower_rng = random.Random(7)
            for _ in range(18):
                fx = cx + flower_rng.randint(-95, 95) * SS
                fy = ground_y - (140 + flower_rng.randint(0, 190)) * SS
                r = 6 * SS
                draw.ellipse([fx - r, fy - r, fx + r, fy + r], fill=petal_color)
                draw.ellipse([fx - r // 3, fy - r // 3, fx + r // 3, fy + r // 3], fill=center_color)

    # A few fallen leaves scattered on the ground when wilted — a small extra
    # visual cue on top of the muted colors, hinting "come back and water me".
    if wilted and stage >= 2:
        leaf_rng = random.Random(99)
        for _ in range(6):
            lx = cx + leaf_rng.randint(-90, 90) * SS
            ly = ground_y + leaf_rng.randint(4, 22) * SS
            r = 5 * SS
            draw.ellipse([lx - r, ly - r // 2, lx + r, ly + r // 2], fill=(0x8C, 0x7A, 0x6A))

    # Downsample for crisp anti-aliased edges (classic supersampling trick)
    scene_rgba = img.resize(size, Image.LANCZOS)
    scene_rgb = Image.new("RGB", size, sky_bottom)
    scene_rgb.paste(scene_rgba, (0, 0), scene_rgba)

    # Composite onto a soft rounded "card" frame so it reads nicely as a Telegram photo
    pad = 14
    card_size = (size[0] + pad * 2, size[1] + pad * 2)
    card = Image.new("RGB", card_size, (0xFA, 0xF7, 0xF0))
    card.paste(scene_rgb, (pad, pad))

    mask = Image.new("L", card_size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card_size[0] - 1, card_size[1] - 1], radius=24, fill=255)
    rounded_card = Image.new("RGB", card_size, (0xFA, 0xF7, 0xF0))
    rounded_card.paste(card, (0, 0), mask)

    rounded_card.save(output_path)
    return output_path


def get_stage_name(stage: int, lang: str) -> str:
    lang = lang if lang in ("hindi", "english", "hinglish") else "hinglish"
    return STAGE_NAMES.get(stage, STAGE_NAMES[0])[lang]
