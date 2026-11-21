#!/usr/bin/env python3
"""Variations of the chosen icon C1 (user 2026-11-21: "I like the C1 design. Make some variations of that one."): the
game's own A (traced by tools/trace_game_a.py from the font brand_header) on the 256 grid. Each variation changes one
or two things: the ground, the letter's colour, an in-game style outline and shadow (the game draws its badge letter
white with a dark edge), a frame, the size.

Out: mod_source/workshop/icon/variations/v01.png ... v08.png (256 x 256) and variations.png (the sheet with true 64 / 32 /
16 px). Run: uv run --with potracer --with pillow --with numpy --with resvg-py python tools/make_game_a_variations.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import trace_game_a as T  # noqa: E402

OUT = os.path.join(T.OUT, "variations")
CHAR = "#16120F"
BONE = "#FFF8D7"
GOLD = "#E2BC6C"
BRONZE = "#C8914F"
GREEN_DEEP = "#1F4A2A"
INK = "#0B0908"


def a(d, box, fill, height=196, top=30, cx=128, extra=""):
    k, tx, ty = T.placed(d, box, height, cx, top)
    return '<path fill="%s" %s transform="matrix(%.4f 0 0 %.4f %.2f %.2f)" d="%s"/>' % (fill, extra, k, k, tx, ty, d)


def edged(d, box, fill, edge, width, shadow=None, **kw):
    """The letter with a dark edge drawn behind it (stroke under the fill), and an optional flat drop shadow."""
    out = ""
    if shadow:
        k, tx, ty = T.placed(d, box, kw.get("height", 196), kw.get("cx", 128), kw.get("top", 30))
        out += '<path fill="%s" fill-opacity="0.55" transform="matrix(%.4f 0 0 %.4f %.2f %.2f)" d="%s"/>' % (
            INK, k, k, tx + shadow, ty + shadow, d)
    out += a(d, box, "none", extra='stroke="%s" stroke-width="%.2f" stroke-linejoin="round"' % (edge, width), **kw)
    out += a(d, box, fill, **kw)
    return out


def svg(body, ground=CHAR, defs=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img">'
            "<title>Smart Ability Autocast</title><defs>%s</defs><rect width=\"256\" height=\"256\" fill=\"%s\"/>%s</svg>"
            % (defs, ground, body))


def variations(d, box):
    radial = ('<radialGradient id="g" cx="128" cy="118" r="170" gradientUnits="userSpaceOnUse">'
              '<stop offset="0" stop-color="#3A2A1E"/><stop offset="1" stop-color="#0E0B09"/></radialGradient>')
    return [
        ("v01", "C1 as chosen", svg(a(d, box, BONE))),
        ("v02", "In-game edge + shadow", svg(edged(d, box, BONE, INK, 0.5, shadow=4))),
        ("v03", "Gold A", svg(a(d, box, GOLD))),
        ("v04", "Warm vignette", svg(edged(d, box, BONE, INK, 0.4, shadow=3), "url(#g)", radial)),
        ("v05", "Deep badge green", svg(edged(d, box, BONE, INK, 0.4, shadow=3), GREEN_DEEP)),
        ("v06", "Bronze panel frame",
         svg('<rect x="10" y="10" width="236" height="236" rx="18" fill="none" stroke="%s" stroke-width="6"/>' % BRONZE
             + a(d, box, BONE, height=172, top=42))),
        ("v07", "Bronze button ring",
         svg('<circle cx="128" cy="128" r="116" fill="none" stroke="%s" stroke-width="8"/>' % BRONZE
             + a(d, box, BONE, height=150, top=52))),
        ("v08", "Big and bold, gold", svg(a(d, box, GOLD, height=236, top=14))),
    ]


def main():
    d, box, _ = T.traced_path()
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for tag, note, s in variations(d, box):
        open(os.path.join(OUT, tag + ".svg"), "w", encoding="utf-8").write(s)
        img = T.on(T.render(s, 256), CHAR)
        p = os.path.join(OUT, tag + ".png")
        img.save(p, "PNG", optimize=True)
        assert img.size == (256, 256) and os.path.getsize(p) < 1024 * 1024
        rows.append((tag, note, img, T.render(s, 64), T.render(s, 32), T.render(s, 16)))
    cols, cw, chh = 4, 256 + 24, 256 + 120
    sheet = Image.new("RGB", (cols * cw + 16, 2 * chh + 16), (238, 236, 232))
    dr = ImageDraw.Draw(sheet)
    fb = ImageFont.truetype(r"C:\Windows\Fonts\georgiab.ttf", 15)
    fr = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 12)
    for i, (tag, note, img, s64, s32, s16) in enumerate(rows):
        x, y = 16 + (i % cols) * cw, 16 + (i // cols) * chh
        sheet.paste(img, (x, y))
        xx = x
        for im in (s64, s32, s16):
            sheet.paste(T.on(im, CHAR), (xx, y + 262))
            xx += im.size[0] + 10
        dr.text((x, y + 330), "%d. %s" % (i + 1, note[:44]), font=fb, fill=(20, 20, 20))
        if len(note) > 44:
            dr.text((x + 18, y + 348), note[44:], font=fr, fill=(60, 60, 60))
    sp = os.path.join(T.OUT, "variations.png")
    sheet.save(sp, "PNG", optimize=True)
    print("wrote", sp)


if __name__ == "__main__":
    main()
