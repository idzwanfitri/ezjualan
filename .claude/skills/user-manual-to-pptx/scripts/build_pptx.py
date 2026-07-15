#!/usr/bin/env python3
"""Render a slide-spec JSON (see SKILL.md for schema) into a .pptx file.

Usage:
    python build_pptx.py <slides.json> <output.pptx> [--base-dir <dir>]

`--base-dir` resolves relative image paths in the JSON (defaults to the
JSON file's own directory, which matches how the source Markdown manual
references its images).
"""

import argparse
import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

NAVY = RGBColor(0x1E, 0x2A, 0x4A)
ACCENT = RGBColor(0x2F, 0x6F, 0xED)
INK = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x5A, 0x5A, 0x5A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PANEL_BG = RGBColor(0xF4, 0xF6, 0xFA)


def set_background(slide, color):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def add_rect(slide, x, y, w, h, color, line=False):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if line:
        shape.line.color.rgb = color
        shape.line.width = Pt(0.5)
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def add_text(slide, x, y, w, h, text, size=18, color=INK, bold=False,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, font="Calibri"):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font
    return box


def add_bullets(slide, x, y, w, h, bullets, size=16, color=INK, font="Calibri"):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, bullet in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(10)
        run = p.add_run()
        run.text = f"•  {bullet}"
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.name = font
    return box


def add_picture_fit(slide, image_path, x, y, max_w, max_h):
    """Place an image inside a box, centered, preserving aspect ratio."""
    if not image_path or not Path(image_path).is_file():
        placeholder = add_rect(slide, x, y, max_w, max_h, PANEL_BG)
        add_text(slide, x, y, max_w, max_h,
                  f"[imej tiada: {Path(image_path).name if image_path else '?'}]",
                  size=12, color=MUTED, align=PP_ALIGN.CENTER,
                  anchor=MSO_ANCHOR.MIDDLE)
        return placeholder

    from PIL import Image
    with Image.open(image_path) as im:
        iw, ih = im.size
    ratio = min(max_w / iw, max_h / ih)
    w = int(iw * ratio)
    h = int(ih * ratio)
    px = x + (max_w - w) // 2
    py = y + (max_h - h) // 2
    return slide.shapes.add_picture(image_path, px, py, width=w, height=h)


def add_footer(slide, page_num, footer_text):
    add_text(slide, Inches(0.5), SLIDE_H - Inches(0.4), Inches(8), Inches(0.35),
              footer_text, size=10, color=MUTED)
    add_text(slide, SLIDE_W - Inches(1.2), SLIDE_H - Inches(0.4), Inches(0.8), Inches(0.35),
              str(page_num), size=10, color=MUTED, align=PP_ALIGN.RIGHT)


def build(spec: dict, out_path: Path, base_dir: Path):
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]
    footer_text = spec.get("footer", spec.get("title", ""))
    page = 0

    def resolve(img):
        if not img:
            return None
        p = Path(img)
        return str(p if p.is_absolute() else (base_dir / p))

    # --- Title slide ---
    slide = prs.slides.add_slide(blank)
    set_background(slide, NAVY)
    add_rect(slide, 0, Inches(4.6), SLIDE_W, Inches(0.06), ACCENT)
    add_text(slide, Inches(1), Inches(2.7), Inches(11.3), Inches(1.3),
              spec.get("title", "Panduan Pengguna"), size=40, bold=True,
              color=WHITE, align=PP_ALIGN.LEFT)
    if spec.get("subtitle"):
        add_text(slide, Inches(1), Inches(3.9), Inches(11.3), Inches(0.6),
                  spec["subtitle"], size=20, color=RGBColor(0xC9, 0xD6, 0xF0))

    # --- Intro / ringkasan slide ---
    if spec.get("intro_bullets"):
        page += 1
        slide = prs.slides.add_slide(blank)
        set_background(slide, WHITE)
        add_rect(slide, 0, 0, Inches(0.25), SLIDE_H, ACCENT)
        add_text(slide, Inches(0.8), Inches(0.5), Inches(11), Inches(0.9),
                  "Pengenalan", size=30, bold=True, color=NAVY)
        add_bullets(slide, Inches(0.9), Inches(1.6), Inches(11.5), Inches(5),
                     spec["intro_bullets"], size=20)
        add_footer(slide, page, footer_text)

    # --- Content slides ---
    for item in spec.get("slides", []):
        page += 1
        slide = prs.slides.add_slide(blank)
        set_background(slide, WHITE)
        add_rect(slide, 0, 0, Inches(0.25), SLIDE_H, ACCENT)
        add_text(slide, Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.8),
                  item.get("heading", ""), size=28, bold=True, color=NAVY)

        layout = item.get("layout", "single")

        if layout == "single":
            img = resolve(item.get("image"))
            bullets = item.get("bullets", [])
            text_w = Inches(4.6)
            add_bullets(slide, Inches(0.8), Inches(1.5), text_w, Inches(5.3), bullets, size=17)
            img_x = Inches(5.7)
            add_picture_fit(slide, img, img_x, Inches(1.4), Inches(7.0), Inches(5.4))

        elif layout == "combined":
            entries = item.get("items", [])
            n = max(len(entries), 1)
            gap = Inches(0.3)
            total_w = SLIDE_W - Inches(1.6)
            col_w = int((total_w - gap * (n - 1)) / n)
            x = Inches(0.8)
            for entry in entries:
                add_text(slide, x, Inches(1.35), col_w, Inches(0.5),
                          entry.get("label", ""), size=16, bold=True, color=ACCENT)
                add_picture_fit(slide, resolve(entry.get("image")), x, Inches(1.9),
                                 col_w, Inches(3.6))
                add_text(slide, x, Inches(5.6), col_w, Inches(1.2),
                          entry.get("text", ""), size=14, color=INK,
                          anchor=MSO_ANCHOR.TOP)
                x = x + col_w + gap

        add_footer(slide, page, footer_text)

    # --- Closing slide ---
    if spec.get("closing_bullets"):
        page += 1
        slide = prs.slides.add_slide(blank)
        set_background(slide, NAVY)
        add_text(slide, Inches(1), Inches(0.8), Inches(11), Inches(0.9),
                  "Selesai", size=32, bold=True, color=WHITE)
        add_bullets(slide, Inches(1), Inches(2.0), Inches(11.3), Inches(4.5),
                     spec["closing_bullets"], size=18, color=RGBColor(0xE8, 0xEC, 0xF6))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out_path))
    print(f"Saved {len(prs.slides)} slides -> {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", help="Path to slides.json")
    parser.add_argument("out", help="Path to output .pptx")
    parser.add_argument("--base-dir", default=None,
                         help="Base directory to resolve relative image paths (default: spec file's directory)")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    base_dir = Path(args.base_dir) if args.base_dir else spec_path.parent
    build(spec, Path(args.out), base_dir)


if __name__ == "__main__":
    main()
