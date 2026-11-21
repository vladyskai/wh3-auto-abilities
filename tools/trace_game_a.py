#!/usr/bin/env python3
"""Concept C finished with the game's own A (user 2026-11-21: "Letter A, but stylized exactly as in the game").

The mod's badge letter uses the font category header_16 = font "brand_header" (ui/fontcategories.xml), whose file
names its source "WarhammerBETA Display" (Pentagram's bespoke Warhammer III typeface, not published). The game ships
it only as BITMAPS (.cuf, local_en.pack: font/brand_header_<px>.cuf, largest 30 px). This tool:
  1. decodes the A from brand_header_30.cuf (WH3 layout: the rpfm_lib font module's tables, with 5-byte glyph records
     after a 4-byte prefix; records and bitmaps sit one slot behind the character map),
  2. keeps the largest connected shape (drops a neighbour's stray pixels), upsamples it x16 and traces it with potrace
     into smooth Bezier outlines (a faithful vector copy, not a scaled bitmap),
  3. writes the icon variants on the 256 grid and renders them (256 and true small sizes) plus a sheet.

Run: uv run --with potracer --with pillow --with numpy --with resvg-py python tools/trace_game_a.py"""
import io
import os
import struct

import numpy as np
import potrace
import resvg_py
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = r"C:\Users\vlady\Desktop\WH3_mod\gamedata\wh3_layouts\font\brand_header_30.cuf"
OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\workshop\icon"
GROUND = "#16120F"
BRONZE = "#C8914F"
GREEN = "#4FAE5A"
BONE = "#FFF8D7"      # the game's header text colour (fontcategories.xml header_16: #FFF8D7)
UP = 16


def glyph_a():
    d = open(FONT, "rb").read()
    codes = struct.unpack_from("<65536H", d, 32)
    used = [c for c in range(65536) if codes[c] != 0xFFFF]
    n = len(used)
    rec0 = 0x20020 + 4
    offs0 = rec0 + 5 * n
    offs = struct.unpack_from("<%dI" % n, d, offs0)
    data0 = offs0 + 4 * n
    i = used.index(ord("A")) - 1
    r = d[rec0 + 5 * i: rec0 + 5 * i + 5]
    w, h = r[3], r[4]
    assert offs[i + 1] - offs[i] == w * h, (w, h)
    return np.frombuffer(d[data0 + offs[i]: data0 + offs[i] + w * h], dtype=np.uint8).reshape(h, w)


def largest_component(mask):
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    best = None
    for y in range(h):
        for x in range(w):
            if mask[y, x] and not seen[y, x]:
                stack, comp = [(y, x)], []
                seen[y, x] = True
                while stack:
                    cy, cx = stack.pop()
                    comp.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            stack.append((ny, nx))
                if best is None or len(comp) > len(best):
                    best = comp
    keep = np.zeros_like(mask, dtype=bool)
    for y, x in best:
        keep[y, x] = True
    return keep


def traced_path():
    """The A as one SVG path in glyph pixel units (x right, y down), and its bounding box."""
    g = glyph_a().astype(np.float32)
    keep = largest_component(g > 40)
    # grow the kept mask by one pixel so the anti-aliased edge stays, then clear everything else
    grown = np.array(Image.fromarray((keep * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3))) > 0
    g = np.where(grown, g, 0)
    g = np.pad(g, 3)   # v2: room around the glyph, so its edge pixels are traced round, not cut flat
    big = Image.fromarray(g.astype(np.uint8)).resize((g.shape[1] * UP, g.shape[0] * UP), Image.LANCZOS)
    big = big.filter(ImageFilter.GaussianBlur(UP * 0.35))
    # potracer traces DARK pixels (values below its black level) as the shape: the glyph goes in as False
    bm = potrace.Bitmap(np.array(big) <= 112)   # v2: a slightly lower line keeps the thin crossbar readable
    plist = bm.trace(turdsize=UP * UP, alphamax=1.0, opticurve=True, opttolerance=0.2)
    parts, xs, ys = [], [], []
    for curve in plist:
        sp = curve.start_point
        seg = ["M%.2f %.2f" % (sp.x / UP, sp.y / UP)]
        xs.append(sp.x / UP)
        ys.append(sp.y / UP)
        for s in curve.segments:
            if s.is_corner:
                seg.append("L%.2f %.2f L%.2f %.2f" % (s.c.x / UP, s.c.y / UP, s.end_point.x / UP, s.end_point.y / UP))
                xs += [s.c.x / UP, s.end_point.x / UP]
                ys += [s.c.y / UP, s.end_point.y / UP]
            else:
                seg.append("C%.2f %.2f %.2f %.2f %.2f %.2f" % (s.c1.x / UP, s.c1.y / UP, s.c2.x / UP, s.c2.y / UP,
                                                             s.end_point.x / UP, s.end_point.y / UP))
                xs.append(s.end_point.x / UP)
                ys.append(s.end_point.y / UP)
        seg.append("Z")
        parts.append(" ".join(seg))
    return " ".join(parts), (min(xs), min(ys), max(xs), max(ys)), np.pad(keep, 3)


def placed(d, box, height, cx, top):
    """A transform that scales the glyph box to the given height and puts its centre at cx, its top at top."""
    x0, y0, x1, y1 = box
    k = height / (y1 - y0)
    tx = cx - k * (x0 + x1) / 2
    ty = top - k * y0
    return k, tx, ty


def svg(body, ground=None):
    bg = '<rect width="256" height="256" fill="%s"/>' % ground if ground else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256" role="img">'
            "<title>Smart Ability Autocast</title>%s%s</svg>" % (bg, body))


def variants(d, box, keep):
    k, tx, ty = placed(d, box, 196, 128, 30)
    a = lambda fill: '<path fill-rule="nonzero" fill="%s" transform="matrix(%.4f 0 0 %.4f %.2f %.2f)" d="%s"/>' % (
        fill, k, k, tx, ty, d)
    # the crossbar line, measured on the glyph: the row band where the shape spans between the legs
    rows = [y for y in range(keep.shape[0]) if keep[y].sum() >= 14]
    bar_y = (sum(rows) / len(rows)) if rows else keep.shape[0] * 0.62
    cols = np.where(keep[int(round(bar_y))])[0]
    bx0, bx1 = (cols.min(), cols.max()) if len(cols) else (8, 20)
    yb = ty + k * (bar_y + 0.5)
    xl, xr = tx + k * (bx0 + 3.0), tx + k * (bx1 - 2.0)
    r = (xr - xl) / 7.2   # v2: smaller buttons, the crossbar shows between them
    discs = "".join('<circle cx="%.2f" cy="%.2f" r="%.2f" fill="%s" stroke="%s" stroke-width="3"/>' % (
        xl + r + j * (xr - xl - 2 * r) / 2, yb, r, GREEN, GROUND) for j in range(3))
    return [
        ("c1", "The game's A, bone white, as the badge letter", svg(a(BONE), GROUND), svg(a("#000000"))),
        ("c2", "The game's A in bronze, three green ability buttons on its crossbar", svg(a(BRONZE) + discs, GROUND),
         svg(a("#000000") + discs.replace(GREEN, "#000000").replace(GROUND, "#FFFFFF"))),
        ("c3", "The game's A, bone white on the green badge disc", svg(
            '<circle cx="128" cy="128" r="118" fill="%s"/><circle cx="128" cy="128" r="110" fill="%s"/>' % (BRONZE, GREEN)
            + a_small(d, box), GROUND), svg('<circle cx="128" cy="128" r="118" fill="#000"/>'
                                            + a_small(d, box, "#FFFFFF"))),
    ]


def a_small(d, box, fill=BONE):
    k, tx, ty = placed(d, box, 150, 128, 50)
    return '<path fill="%s" transform="matrix(%.4f 0 0 %.4f %.2f %.2f)" d="%s"/>' % (fill, k, k, tx, ty, d)


def render(s, size):
    return Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=s, width=size, height=size)))).convert("RGBA")


def on(img, colour):
    bg = Image.new("RGBA", img.size, colour)
    bg.alpha_composite(img)
    return bg.convert("RGB")


def main():
    d, box, keep = traced_path()
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for tag, note, col, black in variants(d, box, keep):
        open(os.path.join(OUT, "game-a-%s-color.svg" % tag), "w", encoding="utf-8").write(col)
        open(os.path.join(OUT, "game-a-%s-black.svg" % tag), "w", encoding="utf-8").write(black)
        png = on(render(col, 256), GROUND)
        p = os.path.join(OUT, "game-a-%s-256.png" % tag)
        png.save(p, "PNG", optimize=True)
        assert png.size == (256, 256) and os.path.getsize(p) < 1024 * 1024
        rows.append((tag, note, png, render(black, 256), render(col, 64), render(col, 32), render(col, 16)))
    # the source glyph, for comparison, enlarged by pixels (what the game draws)
    src = Image.fromarray(glyph_a()).resize((glyph_a().shape[1] * 6, glyph_a().shape[0] * 6), Image.NEAREST)
    pad, rowh = 16, 300
    sheet = Image.new("RGB", (1120, pad + 40 + len(rows) * rowh), (238, 236, 232))
    dr = ImageDraw.Draw(sheet)
    fb = ImageFont.truetype(r"C:\Windows\Fonts\georgiab.ttf", 18)
    fr = ImageFont.truetype(r"C:\Windows\Fonts\georgia.ttf", 14)
    dr.text((pad, pad), "The game's A (font brand_header, 30 px bitmap, enlarged) and the traced vector versions",
            font=fb, fill=(20, 20, 20))
    sheet.paste(Image.merge("RGB", (src, src, src)), (900, pad + 40))
    for i, (tag, note, png, black, c64, c32, c16) in enumerate(rows):
        y = pad + 40 + i * rowh
        dr.text((pad, y), "%s  %s" % (tag.upper(), note), font=fb, fill=(20, 20, 20))
        y += 28
        sheet.paste(png, (pad, y))
        sheet.paste(on(black, "#FFFFFF"), (pad + 266, y))
        x = pad + 536
        for im in (c64, c32, c16):
            sheet.paste(on(im, GROUND), (x, y))
            x += im.size[0] + 14
        dr.text((pad + 536, y + 72), "true size 64, 32, 16 px", font=fr, fill=(90, 90, 90))
    sp = os.path.join(OUT, "game-a-concepts.png")
    sheet.save(sp, "PNG", optimize=True)
    print("wrote", sp, "box", [round(v, 1) for v in box])


if __name__ == "__main__":
    main()
