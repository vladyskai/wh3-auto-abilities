#!/usr/bin/env python3
"""Build the three icon concepts for Smart Ability Autocast, following the user's guide
(https://github.com/kaankiziltug/logo-design-skill): clean geometric SVG on a 256 grid, black first, then colour;
rendered at true sizes (256, 64, 32, 16) and one colour reversed; one concept sheet for the checkpoint.
The brief and the concept list: mod_source/workshop/icon/BRIEF.md.

  A  Wheel   the game's wheel reduced to geometry: a ring holding a bold A, four button discs on its right arc
  B  Orbit   three ability buttons on a circular track that ends in an arrowhead: the wheel turns by itself
  C  Letter  a letter A whose crossbar is a row of three ability buttons

Run: uv run --with resvg-py --with pillow python tools/make_icon_concepts.py"""
import io
import math
import os

import resvg_py
from PIL import Image, ImageDraw, ImageFont, ImageOps

OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\workshop\icon"
INK = "#000000"
GROUND = "#16120F"
BRONZE = "#C8914F"
GREEN = "#4FAE5A"
BONE = "#F0E6D0"
DARKFACE = "#2A221C"


def f(v):
    return ("%.2f" % v).rstrip("0").rstrip(".")


def svg(body, ground=None, title="Smart Ability Autocast"):
    bg = '<rect width="256" height="256" fill="%s"/>' % ground if ground else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img">'
            "<title>%s</title>%s%s</svg>" % (title, bg, body))


def circle(cx, cy, r, fill):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(cx), f(cy), f(r), fill)


def ring_path(cx, cy, ro, ri, fill):
    """A ring as ONE evenodd path (a real hole, no stroke)."""
    def c(r):
        return "M%s %s A%s %s 0 1 1 %s %s A%s %s 0 1 1 %s %s Z" % (
            f(cx - r), f(cy), f(r), f(r), f(cx + r), f(cy), f(r), f(r), f(cx - r), f(cy))
    return '<path fill-rule="evenodd" fill="%s" d="%s %s"/>' % (fill, c(ro), c(ri))


def letter_a(cx, top, h, w, s, a, bar_top, bar_h, fill, crossbar=True):
    """A constructed A (no font): flat apex a wide, legs s thick (horizontal measure), a crossbar or none.
    Returns (path, x_inner_left(y), x_inner_right(y))."""
    k = (w / 2 - a / 2) / h

    def x_ro(y):
        return cx + a / 2 + k * (y - top)

    def x_ri(y):
        return x_ro(y) - s

    def x_li(y):
        return 2 * cx - x_ri(y)
    y_in = top + (s - a / 2) / k          # where the two inner edges meet
    base = top + h
    pts = [(cx - w / 2, base), (cx - a / 2, top), (cx + a / 2, top), (cx + w / 2, base), (cx + w / 2 - s, base)]
    if crossbar:
        yb = bar_top + bar_h
        pts += [(x_ri(yb), yb), (x_li(yb), yb), (cx - w / 2 + s, base)]
        hole = [(cx, y_in), (x_ri(bar_top), bar_top), (x_li(bar_top), bar_top)]
        d = "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in pts) + " Z M" + " L".join(
            "%s %s" % (f(x), f(y)) for x, y in hole) + " Z"
    else:
        pts += [(cx, y_in), (cx - w / 2 + s, base)]
        d = "M" + " L".join("%s %s" % (f(x), f(y)) for x, y in pts) + " Z"
    return '<path fill-rule="evenodd" fill="%s" d="%s"/>' % (fill, d), x_li, x_ri


def button(cx, cy, r, colour):
    """An ability button. Black: a solid disc. Colour: a bronze rim, a dark face and the green lower band (the badge)."""
    if not colour:
        return circle(cx, cy, r, INK)
    band_y = cy + r * 0.35
    rr = r - 5
    half = math.sqrt(max(0.0, rr * rr - (band_y - cy) ** 2))
    band = '<path fill="%s" d="M%s %s A%s %s 0 0 0 %s %s Z"/>' % (
        GREEN, f(cx - half), f(band_y), f(rr), f(rr), f(cx + half), f(band_y))
    return circle(cx, cy, r, BRONZE) + circle(cx, cy, rr, DARKFACE) + band


# ---------------------------------------------------------------- A: Wheel
def concept_a(colour):
    cx, cy, ro, ri = 98, 128, 76, 60
    body = ring_path(cx, cy, ro, ri, BRONZE if colour else INK)
    if colour:
        body += circle(cx, cy, ri, GREEN)
    a, _, _ = letter_a(cx, 88, 80, 78, 18, 18, 134, 15, BONE if colour else INK)   # v2: taller, heavier crossbar
    body += a
    orbit, b = ro + 8 + 20, 20          # an 8-unit gap between the ring and the buttons
    for deg in (-63, -21, 21, 63):
        t = math.radians(deg)
        body += button(cx + orbit * math.cos(t), cy + orbit * math.sin(t), b, colour)
    return svg(body, GROUND if colour else None)


# ---------------------------------------------------------------- B: Orbit
def concept_b(colour):
    cx, cy, R, sw = 128, 128, 84, 18
    beads = [180, 270, 360]             # left, top, right (degrees, y down: 270 = top)
    start, end, b, halo = 140, 430, 24, 7   # v2: the last piece runs 70 degrees past the right bead
    col = BRONZE if colour else INK
    body = ""
    # the track: arc pieces between the beads, each piece stopping short of a bead by its halo
    stops = [start] + [x for d in beads for x in (d - math.degrees((b + halo) / R), d + math.degrees((b + halo) / R))] + [end]
    for i in range(0, len(stops), 2):
        a0, a1 = math.radians(stops[i]), math.radians(stops[i + 1])
        x0, y0 = cx + R * math.cos(a0), cy + R * math.sin(a0)
        x1, y1 = cx + R * math.cos(a1), cy + R * math.sin(a1)
        large = 1 if (stops[i + 1] - stops[i]) > 180 else 0
        body += '<path fill="none" stroke="%s" stroke-width="%s" d="M%s %s A%s %s 0 %d 1 %s %s"/>' % (
            col, sw, f(x0), f(y0), R, R, large, f(x1), f(y1))
    # the arrowhead at the end, pointing along the clockwise tangent
    t = math.radians(end)
    px, py = cx + R * math.cos(t), cy + R * math.sin(t)
    tx, ty = -math.sin(t), math.cos(t)
    nx, ny = math.cos(t), math.sin(t)
    tip = (px + tx * 34, py + ty * 34)
    w = 22   # v2: the base sits on the track end, so the head grows out of it
    head = [(px + nx * w, py + ny * w), tip, (px - nx * w, py - ny * w)]
    body += '<path fill="%s" d="M%s Z"/>' % (GREEN if colour else INK, " L".join("%s %s" % (f(x), f(y)) for x, y in head))
    for d in beads:
        t = math.radians(d)
        body += button(cx + R * math.cos(t), cy + R * math.sin(t), b, colour)
    return svg(body, GROUND if colour else None)


# ---------------------------------------------------------------- C: Letter
def concept_c(colour):
    cx, top, h, w, s, a = 128, 34, 188, 196, 40, 40
    path, x_li, x_ri = letter_a(cx, top, h, w, s, a, 0, 0, BRONZE if colour else INK, crossbar=False)
    body = path
    yc = top + h * 0.62
    inner = x_ri(yc) - x_li(yc)
    g = 3   # v2: bigger beads, smaller gaps
    r = (inner - 2 * g) / 6
    for i in (-1, 0, 1):
        bx = cx + i * (2 * r + g)
        if colour:
            body += circle(bx, yc, r, GREEN)
        else:
            body += circle(bx, yc, r, INK)
    return svg(body, GROUND if colour else None)


CONCEPTS = [("A", "Wheel", "The game's wheel as pure geometry: a ring holding a bold A, four buttons on its arc", concept_a),
            ("B", "Orbit", "Three ability buttons travelling on a track that ends in an arrow: the wheel turns by itself", concept_b),
            ("C", "Letter", "A letter A whose crossbar is a row of three ability buttons", concept_c)]


def render(svg_text, size):
    data = resvg_py.svg_to_bytes(svg_string=svg_text, width=size, height=size)
    return Image.open(io.BytesIO(bytes(data))).convert("RGBA")


def on(img, colour):
    bg = Image.new("RGBA", img.size, colour)
    bg.alpha_composite(img)
    return bg.convert("RGB")


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for letter, name, idea, fn in CONCEPTS:
        black, col = fn(False), fn(True)
        for tag, txt in (("black", black), ("color", col)):
            open(os.path.join(OUT, "concept-%s-%s.svg" % (letter.lower(), tag)), "w", encoding="utf-8").write(txt)
        png = render(col, 256)
        p = os.path.join(OUT, "concept-%s-256.png" % letter.lower())
        on(png, "#000000").save(p, "PNG", optimize=True)
        assert os.path.getsize(p) < 1024 * 1024
        rows.append((letter, name, idea, render(col, 256), render(black, 256), render(black, 64), render(black, 32),
                     render(black, 16), render(col, 64), render(col, 32)))
    # the concept sheet: colour 256 | black 256 | reversed 128 | true 64 / 32 / 16 (black and colour)
    W, rowh, pad = 1180, 300, 16
    sheet = Image.new("RGB", (W, pad + len(rows) * rowh + 40), (238, 236, 232))
    d = ImageDraw.Draw(sheet)
    fb = ImageFont.truetype(r"C:\Windows\Fonts\georgiab.ttf", 18)
    fr = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 14)
    for i, (letter, name, idea, c256, b256, b64, b32, b16, c64, c32) in enumerate(rows):
        y = pad + i * rowh
        d.text((pad, y), "%s  %s" % (letter, name), font=fb, fill=(20, 20, 20))
        d.text((pad + 120, y + 3), idea, font=fr, fill=(60, 60, 60))
        y += 30
        sheet.paste(on(c256, GROUND), (pad, y))
        sheet.paste(on(b256, "#FFFFFF"), (pad + 266, y))
        rev = ImageOps.invert(on(b256, "#FFFFFF")).resize((128, 128), Image.LANCZOS)
        sheet.paste(rev, (pad + 532, y))
        x = pad + 672
        for im, bgc in ((b64, "#FFFFFF"), (b32, "#FFFFFF"), (b16, "#FFFFFF"), (c64, GROUND), (c32, GROUND)):
            sheet.paste(on(im, bgc), (x, y))
            x += im.size[0] + 14
        d.text((pad + 672, y + 80), "true size: 64, 32, 16 px (black), then 64, 32 (colour)", font=fr, fill=(90, 90, 90))
        d.text((pad + 532, y + 136), "reversed", font=fr, fill=(90, 90, 90))
    d.text((pad, sheet.size[1] - 30), "Colour 256 | black master 256 | reversed | true small sizes. No text in the marks.",
           font=fr, fill=(90, 90, 90))
    sp = os.path.join(OUT, "concepts.png")
    sheet.save(sp, "PNG", optimize=True)
    print("wrote", sp)


if __name__ == "__main__":
    main()
