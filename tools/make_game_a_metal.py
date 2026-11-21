#!/usr/bin/env python3
"""Metallic finishes for the chosen icon (user 2026-11-21: "Can we give it a 'metallic' look?"): the game's own A
(tools/trace_game_a.py), with a metal gradient (light falling from the top, a bright band across, a darker reflection
below) and a bevel (a light rim on the top-left edges, a dark rim on the bottom-right), over the in-game dark edge and
soft shadow of variation 2.

Bevel construction (no filters, so every renderer draws it the same): inside a clip of the letter, fill the light rim
colour; draw the letter moved down-right by D in the dark rim colour; then draw the gradient only where the letter moved
down-right and the letter moved up-left overlap. What stays light is the top-left rim, what stays dark the bottom-right.

Out: mod_source/workshop/icon/metal/m01.png ... m06.png (256 x 256) and metal.png (the sheet with true 64 / 32 / 16 px).
Run: uv run --with potracer --with pillow --with numpy --with resvg-py python tools/make_game_a_metal.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import trace_game_a as T  # noqa: E402

OUT = os.path.join(T.OUT, "metal")
CHAR = "#16120F"
INK = "#0B0908"
D = 2.6          # bevel width in pixels of the 256 tile

METALS = {
    # name: (gradient stops top -> bottom, light rim, dark rim)
    "gold": (["#FFF3C4", "#E9C46A", "#B8862E", "#F6DA8C", "#8C6220"], "#FFF8DC", "#5A3C10"),
    "bronze": (["#F2C79A", "#C8914F", "#8A5A2B", "#D9A46C", "#5E3A1A"], "#FBE0C2", "#3A2210"),
    "silver": (["#FFFFFF", "#D8DCE0", "#8E959C", "#E4E8EC", "#5C6268"], "#FFFFFF", "#2C3034"),
    "pale_gold": (["#FFFBEA", "#F3E2AE", "#C9A55C", "#F7EBC6", "#A0803E"], "#FFFFFF", "#6B5226"),
}


def place(d, box, height=196, top=30, cx=128):
    return T.placed(d, box, height, cx, top)


def letter(d, m, dx=0.0, dy=0.0, fill="none", extra=""):
    k, tx, ty = m
    return '<path fill="%s" %s transform="matrix(%.4f 0 0 %.4f %.2f %.2f)" d="%s"/>' % (
        fill, extra, k, k, tx + dx, ty + dy, d)


def metal_letter(d, box, metal, tag, height=196, top=30, edge=0.5, shadow=4):
    stops, light, dark = METALS[metal]
    m = place(d, box, height, top)
    # the gradient is read inside the letter's own transform, so it is given in glyph units (the traced box)
    y0, y1 = box[1], box[3]
    offs = [0.0, 0.32, 0.5, 0.62, 1.0]
    grad = '<linearGradient id="g_%s" x1="0" y1="%.1f" x2="0" y2="%.1f" gradientUnits="userSpaceOnUse">%s</linearGradient>' % (
        tag, y0, y1, "".join('<stop offset="%.2f" stop-color="%s"/>' % (o, c) for o, c in zip(offs, stops)))
    clips = ('<clipPath id="c_%s">%s</clipPath><clipPath id="cdr_%s">%s</clipPath>' % (
        tag, letter(d, m), tag, letter(d, m, D, D)))
    body = ""
    if shadow:
        body += letter(d, m, shadow, shadow, INK, 'fill-opacity="0.6"')
    body += letter(d, m, extra='stroke="%s" stroke-width="%.2f" stroke-linejoin="round"' % (INK, edge))
    body += ('<g clip-path="url(#c_%s)"><rect width="256" height="256" fill="%s"/>%s'
             '<g clip-path="url(#cdr_%s)">%s</g></g>') % (
        tag, light, letter(d, m, D, D, dark), tag, letter(d, m, -D, -D, "url(#g_%s)" % tag))
    return grad + clips, body


def svg(defs, body, ground=CHAR, extra_defs=""):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img">'
            "<title>Smart Ability Autocast</title><defs>%s%s</defs><rect width=\"256\" height=\"256\" fill=\"%s\"/>%s</svg>"
            % (extra_defs, defs, ground, body))


def variants(d, box):
    vign = ('<radialGradient id="v" cx="128" cy="118" r="170" gradientUnits="userSpaceOnUse">'
            '<stop offset="0" stop-color="#3A2A1E"/><stop offset="1" stop-color="#0E0B09"/></radialGradient>')
    out = []
    for tag, note, metal, ground, ex in (
            ("m01", "Polished gold", "gold", CHAR, ""),
            ("m02", "Polished gold, warm vignette", "gold", "url(#v)", vign),
            ("m03", "Bronze, like the wheel's frame", "bronze", CHAR, ""),
            ("m04", "Steel / silver", "silver", CHAR, ""),
            ("m05", "Pale gold (near the game's bone)", "pale_gold", CHAR, ""),
            ("m06", "Pale gold, warm vignette", "pale_gold", "url(#v)", vign)):
        defs, body = metal_letter(d, box, metal, tag)
        out.append((tag, note, svg(defs, body, ground, ex)))
    return out


def main():
    d, box, _ = T.traced_path()
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for tag, note, s in variants(d, box):
        open(os.path.join(OUT, tag + ".svg"), "w", encoding="utf-8").write(s)
        img = T.on(T.render(s, 256), CHAR)
        p = os.path.join(OUT, tag + ".png")
        img.save(p, "PNG", optimize=True)
        assert img.size == (256, 256) and os.path.getsize(p) < 1024 * 1024
        rows.append((tag, note, img, T.render(s, 64), T.render(s, 32), T.render(s, 16)))
    cols, cw, chh = 3, 256 + 24, 256 + 110
    sheet = Image.new("RGB", (cols * cw + 16, 2 * chh + 16), (238, 236, 232))
    dr = ImageDraw.Draw(sheet)
    fb = ImageFont.truetype(r"C:\Windows\Fonts\georgiab.ttf", 15)
    for i, (tag, note, img, s64, s32, s16) in enumerate(rows):
        x, y = 16 + (i % cols) * cw, 16 + (i // cols) * chh
        sheet.paste(img, (x, y))
        xx = x
        for im in (s64, s32, s16):
            sheet.paste(T.on(im, CHAR), (xx, y + 262))
            xx += im.size[0] + 10
        dr.text((x, y + 332), "%d. %s" % (i + 1, note), font=fb, fill=(20, 20, 20))
    sp = os.path.join(T.OUT, "metal.png")
    sheet.save(sp, "PNG", optimize=True)
    print("wrote", sp)


if __name__ == "__main__":
    main()
