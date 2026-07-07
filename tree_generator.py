"""
Study Tree — ek visual tree jo user ki consistency ke hisaab se grow hota hai.
Bina kisi API ke, sirf Pillow (PIL) se procedurally draw kiya jata hai.

Growth stages (0-5) total completed activities (topics + sessions) par based hai.
Agar user 2+ din se inactive hai, tree "wilted" (murjha hua) dikhta hai — motivate
karne ke liye ki wapas aa jao.
"""
import random
from PIL import Image, ImageDraw

STAGE_NAMES = {
    0: {"hindi": "बीज", "english": "Seed", "hinglish": "Beej"},
    1: {"hindi": "अंकुर", "english": "Sprout", "hinglish": "Ankur"},
    2: {"hindi": "पौधा", "english": "Sapling", "hinglish": "Sapling"},
    3: {"hindi": "युवा पेड़", "english": "Young Tree", "hinglish": "Young Tree"},
    4: {"hindi": "परिपक्व पेड़", "english": "Mature Tree", "hinglish": "Mature Tree"},
    5: {"hindi": "खिलता पेड़", "english": "Blooming Tree", "hinglish": "Blooming Tree"},
}


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


def generate_tree_image(stage: int, wilted: bool, output_path: str, size=(600, 600)):
    w, h = size
    sky_color = "#EAF6FF" if not wilted else "#F2EEE4"
    ground_color = "#7CB342" if not wilted else "#B0A17E"
    trunk_color = "#6D4C41" if not wilted else "#8D7B6E"
    leaf_color = "#43A047" if not wilted else "#A1887F"
    leaf_color2 = "#66BB6A" if not wilted else "#BCAAA4"
    flower_color = "#F06292"

    img = Image.new("RGB", size, sky_color)
    draw = ImageDraw.Draw(img)

    ground_y = h - 70
    draw.rectangle([0, ground_y, w, h], fill=ground_color)

    cx = w // 2

    if stage == 0:
        draw.ellipse([cx - 18, ground_y - 12, cx + 18, ground_y + 12], fill="#5D4037")

    elif stage == 1:
        draw.line([cx, ground_y, cx, ground_y - 50], fill=trunk_color, width=8)
        draw.ellipse([cx - 25, ground_y - 85, cx + 25, ground_y - 35], fill=leaf_color)

    elif stage == 2:
        draw.line([cx, ground_y, cx, ground_y - 100], fill=trunk_color, width=12)
        draw.ellipse([cx - 50, ground_y - 155, cx + 50, ground_y - 65], fill=leaf_color)
        draw.ellipse([cx - 32, ground_y - 175, cx + 32, ground_y - 105], fill=leaf_color2)

    elif stage == 3:
        draw.line([cx, ground_y, cx, ground_y - 150], fill=trunk_color, width=18)
        draw.ellipse([cx - 90, ground_y - 225, cx + 90, ground_y - 95], fill=leaf_color)
        draw.ellipse([cx - 60, ground_y - 255, cx + 60, ground_y - 150], fill=leaf_color2)
        draw.ellipse([cx - 32, ground_y - 275, cx + 32, ground_y - 190], fill=leaf_color)

    elif stage == 4:
        draw.line([cx, ground_y, cx, ground_y - 190], fill=trunk_color, width=24)
        draw.ellipse([cx - 130, ground_y - 300, cx + 130, ground_y - 130], fill=leaf_color)
        draw.ellipse([cx - 95, ground_y - 340, cx + 95, ground_y - 170], fill=leaf_color2)
        draw.ellipse([cx - 55, ground_y - 365, cx + 55, ground_y - 235], fill=leaf_color)

    else:  # stage 5 — blooming
        draw.line([cx, ground_y, cx, ground_y - 190], fill=trunk_color, width=24)
        draw.ellipse([cx - 130, ground_y - 300, cx + 130, ground_y - 130], fill=leaf_color)
        draw.ellipse([cx - 95, ground_y - 340, cx + 95, ground_y - 170], fill=leaf_color2)
        draw.ellipse([cx - 55, ground_y - 365, cx + 55, ground_y - 235], fill=leaf_color)

        if not wilted:
            rng = random.Random(7)  # fixed seed = consistent look each time
            for _ in range(20):
                fx = cx + rng.randint(-115, 115)
                fy = ground_y - 150 - rng.randint(0, 190)
                draw.ellipse([fx - 7, fy - 7, fx + 7, fy + 7], fill=flower_color)

    # Droopy branch lines for wilted look (extra visual cue beyond just color)
    if wilted and stage >= 2:
        for dx in (-30, 30):
            draw.line(
                [cx + dx // 2, ground_y - (40 if stage < 3 else 80),
                 cx + dx, ground_y - (10 if stage < 3 else 30)],
                fill=trunk_color, width=4,
            )

    img.save(output_path)
    return output_path


def get_stage_name(stage: int, lang: str) -> str:
    lang = lang if lang in ("hindi", "english", "hinglish") else "hinglish"
    return STAGE_NAMES.get(stage, STAGE_NAMES[0])[lang]
