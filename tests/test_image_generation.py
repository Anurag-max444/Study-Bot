"""Tests that every tree-image stage/wilted combination and every weekly
report card renders without crashing, and produces images of the expected
shape. These modules have no DB/Telegram dependency, so they're tested
directly."""
import itertools

import pytest
from PIL import Image

import ui.tree_generator as tree_generator
import ui.report_generator as report_generator
import ui.branding as branding


@pytest.mark.parametrize("stage,wilted", list(itertools.product(range(6), [False, True])))
def test_tree_image_renders_for_every_stage_and_wilted_state(tmp_path, stage, wilted):
    out_path = tmp_path / f"tree_{stage}_{wilted}.png"
    result_path = tree_generator.generate_tree_image(stage, wilted, str(out_path))

    assert result_path == str(out_path)
    img = Image.open(out_path)
    assert img.size[0] > 0 and img.size[1] > 0


def test_owl_watermark_renders_without_error():
    icon = branding.render_owl_icon(64)
    assert icon.mode == "RGBA"
    assert icon.size == (64, 64)

    canvas = Image.new("RGB", (300, 300), (255, 255, 255))
    watermarked = branding.apply_watermark(canvas)
    assert watermarked.size == (300, 300)


@pytest.mark.parametrize("lang", ["hindi", "english", "hinglish"])
def test_weekly_report_card_renders_for_every_language(lang):
    img = report_generator.build_weekly_report_image(
        name="Rahul", lang=lang,
        daily_minutes=[45, 0, 90, 60, 30, 120, 75],
        streak=4, longest_streak=9, sessions_done=6,
        badge_count=3, total_badges=8,
    )
    assert img.size == (700, 900)


def test_weekly_report_card_handles_all_zero_week_without_crashing():
    img = report_generator.build_weekly_report_image(
        name="Anurag", lang="hinglish",
        daily_minutes=[0, 0, 0, 0, 0, 0, 0],
        streak=0, longest_streak=0, sessions_done=0,
        badge_count=0, total_badges=8,
    )
    assert img.size == (700, 900)


def test_weekly_report_pdf_generation_produces_a_real_file(tmp_path):
    out_path = tmp_path / "report.pdf"
    report_generator.generate_weekly_report_pdf(
        name="Rahul", lang="hinglish", daily_minutes=[45, 0, 90, 60, 30, 120, 75],
        streak=4, longest_streak=9, sessions_done=6, badge_count=3, total_badges=8,
        output_path=str(out_path),
    )
    assert out_path.exists()
    assert out_path.stat().st_size > 1000
