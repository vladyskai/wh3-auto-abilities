#!/usr/bin/env python3
"""Realistic 3D metal versions of the chosen icon (user 2026-11-21: "More realistic, the A should have texture and feel
like 3D."). The game's own A (tools/trace_game_a.py) is rendered as a lit metal object, at 1024 px, then scaled to 256:

  1. the traced letter becomes a mask; its inner distance gives a rounded bevel (a height map: raised face, rounded edges),
  2. a metal texture is pressed into that surface: brushed (fine streaks along x) or hammered (soft dents),
  3. normals from the height map are lit by a key light from the top left: diffuse, a Blinn specular highlight and a
     studio reflection band (what makes polished metal read as metal), times the metal's colour,
  4. an extruded side (the letter swept down-right, darker toward the back) gives thickness, a blurred shadow falls
     behind it on a warm vignette ground with a faint texture.

Out: mod_source/workshop/icon/3d/r01.png ... r06.png (256 x 256) and 3d.png (the sheet with true 64 / 32 / 16 px), and
THE WORKSHOP IMAGE mod_source/workshop/smart_ability_autocast.png (the user's pick: version 1, centred).
Run: uv run --with potracer --with pillow --with numpy --with scipy --with resvg-py python tools/make_game_a_3d.py"""
import io
import os
import sys

import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resvg_py  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter, ImageFont  # noqa: E402

import trace_game_a as T  # noqa: E402

OUT = os.path.join(T.OUT, "3d")
FINAL = os.path.join(os.path.dirname(T.OUT), "smart_ability_autocast.png")
FINAL_NUDGE_X = 3.0   # pixels of the 256 tile, to the right of the measured centre (user 2026-11-21)
N = 1024
S = N / 256.0

METALS = {
    #           albedo (base colour)    specular tint        dark (side / deep)
    "gold":   ((0.86, 0.64, 0.26), (1.00, 0.93, 0.70), (0.30, 0.18, 0.05)),
    "pale":   ((0.92, 0.82, 0.58), (1.00, 0.98, 0.88), (0.36, 0.28, 0.14)),
    "bronze": ((0.72, 0.45, 0.24), (1.00, 0.84, 0.66), (0.24, 0.12, 0.05)),
    "steel":  ((0.70, 0.72, 0.75), (1.00, 1.00, 1.00), (0.18, 0.19, 0.21)),
}


def letter_mask(d, box, height=188, top=26, cx=124):
    k, tx, ty = T.placed(d, box, height, cx, top)
    s = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">'
         '<path fill="#FFFFFF" transform="matrix(%.4f 0 0 %.4f %.2f %.2f)" d="%s"/></svg>' % (k, k, tx, ty, d))
    img = Image.open(io.BytesIO(bytes(resvg_py.svg_to_bytes(svg_string=s, width=N, height=N)))).convert("RGBA")
    return np.asarray(img, dtype=np.float32)[:, :, 3] / 255.0


def centred_mask(d, box, extrude, nudge_x=0.0):
    """The letter moved so the solid object (the face, plus its side when extruded) is centred in the tile (user
    2026-11-21: "Number 1, but please center it"). The soft shadow is left out of the measure: it is not part of the
    object, and including it would pull the letter up and left."""
    mask = letter_mask(d, box)
    solid = mask
    if extrude:
        dep = 7 * S
        solid = np.maximum(mask, ndimage.shift(mask, (dep * 0.9, dep * 0.65), order=1))
    ys, xs = np.where(solid > 0.5)
    dx = 128 - (xs.min() + xs.max() + 1) / 2 / S + nudge_x
    dy = 128 - (ys.min() + ys.max() + 1) / 2 / S
    return letter_mask(d, box, top=26 + dy, cx=124 + dx)


def texture(kind, rng):
    if kind == "brushed":
        n = rng.standard_normal((N, N)).astype(np.float32)
        n = ndimage.gaussian_filter(n, sigma=(0.6, 18))          # long streaks along x
        n += 0.35 * ndimage.gaussian_filter(rng.standard_normal((N, N)).astype(np.float32), 1.0)
        return n / (np.abs(n).max() + 1e-6) * 0.9   # scaled again in shade()
    n = ndimage.gaussian_filter(rng.standard_normal((N, N)).astype(np.float32), 11)   # hammered dents (v2: wider, softer)
    n += 0.08 * ndimage.gaussian_filter(rng.standard_normal((N, N)).astype(np.float32), 1.2)
    return n / (np.abs(n).max() + 1e-6) * 1.6


def shade(mask, metal, tex_kind, seed):
    rng = np.random.default_rng(seed)
    albedo, spec_tint, dark = (np.array(c, dtype=np.float32) for c in METALS[metal])
    inside = mask > 0.5
    dist = ndimage.distance_transform_edt(inside)
    bevel = 7.0 * S   # v2: a crisper bevel
    t = np.clip(dist / bevel, 0, 1)
    h = np.sqrt(1 - (1 - t) ** 2) * bevel * 1.5                    # a rounded bevel up to a flat face (v2: steeper rim)
    h = ndimage.gaussian_filter(h, 1.2)
    tex = texture(tex_kind, rng)
    amp = 0.10 * S if tex_kind == "brushed" else 0.30 * S        # v2: subtle, metal is smooth under the texture
    h = h + tex * amp * (0.4 + 0.6 * t)                            # texture deeper on the face than on the rim
    gy, gx = np.gradient(h)
    nx, ny, nz = -gx, -gy, np.ones_like(h)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / ln, ny / ln, nz / ln
    L = np.array([-0.55, -0.62, 0.56], dtype=np.float32)           # key light from the top left (y grows down)
    L /= np.linalg.norm(L)
    V = np.array([0, 0, 1], dtype=np.float32)
    Hv = (L + V) / np.linalg.norm(L + V)
    diff = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    spec = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1) ** 45
    # the studio band: a bright horizon reflected in the metal, bent by the surface normal
    yy = np.linspace(0, 1, N, dtype=np.float32)[:, None]
    band = np.exp(-(((yy - 0.40) + 0.55 * ny) / 0.09) ** 2)
    dark_band = np.exp(-(((yy - 0.62) + 0.55 * ny) / 0.07) ** 2)
    env = 0.75 + 0.95 * band - 0.35 * dark_band   # v2: brighter, more reflective
    col = albedo[None, None, :] * (0.34 + 0.66 * diff[..., None]) * env[..., None]
    col += spec[..., None] * spec_tint[None, None, :] * 1.7
    col += 0.10 * band[..., None] * spec_tint[None, None, :]
    # a touch of the dark tone deep in the corners (ambient occlusion from the bevel)
    occ = np.clip(1 - t, 0, 1) ** 3 * 0.25
    col = col * (1 - occ[..., None]) + dark[None, None, :] * occ[..., None]
    return np.clip(col, 0, 1), dark


def extrusion(mask, dark, depth):
    side = np.zeros_like(mask)
    shade_v = np.zeros_like(mask)
    for i in range(int(depth), 0, -1):
        m = ndimage.shift(mask, (i * 0.9, i * 0.65), order=1)
        upd = m > side
        side = np.maximum(side, m)
        shade_v = np.where(upd, 1 - i / depth, shade_v)
    col = dark[None, None, :] * (0.55 + 0.9 * shade_v[..., None])
    return side, np.clip(col, 0, 1)


def ground(rng):
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    r = np.sqrt((xx - N * 0.5) ** 2 + (yy - N * 0.46) ** 2) / (N * 0.68)
    v = np.clip(1 - r, 0, 1) ** 1.2
    base = np.array([0.055, 0.043, 0.035])
    glow = np.array([0.24, 0.16, 0.10])
    col = base[None, None, :] + glow[None, None, :] * v[..., None]
    grain = ndimage.gaussian_filter(rng.standard_normal((N, N)).astype(np.float32), 1.4) * 0.018
    return np.clip(col + grain[..., None], 0, 1)


def compose(mask, metal, tex_kind, extrude=True, seed=3):
    rng = np.random.default_rng(seed + 100)
    out = ground(rng)
    face, dark = shade(mask, metal, tex_kind, seed)
    depth = 7 * S if extrude else 0
    sh = ndimage.gaussian_filter(ndimage.shift(mask, (depth + 6 * S, depth * 0.7 + 4 * S), order=1), 7 * S) * 0.75
    out = out * (1 - sh[..., None])
    if extrude:
        side, side_col = extrusion(mask, dark, depth)
        out = out * (1 - side[..., None]) + side_col * side[..., None]
    out = out * (1 - mask[..., None]) + face * mask[..., None]
    img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGB")
    small = img.resize((256, 256), Image.LANCZOS)
    return small.filter(ImageFilter.UnsharpMask(radius=0.8, percent=60, threshold=1))


VARIANTS = [("r01", "Gold, brushed", "gold", "brushed", True),
            ("r02", "Gold, hammered", "gold", "hammered", True),
            ("r03", "Pale gold, brushed", "pale", "brushed", True),
            ("r04", "Bronze, hammered", "bronze", "hammered", True),
            ("r05", "Steel, brushed", "steel", "brushed", True),
            ("r06", "Gold, brushed, flat (no side)", "gold", "brushed", False)]


def main():
    d, box, _ = T.traced_path()
    mask = letter_mask(d, box)
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for tag, note, metal, tex, ext in VARIANTS:
        img = compose(mask, metal, tex, ext)
        p = os.path.join(OUT, tag + ".png")
        img.save(p, "PNG", optimize=True)
        assert img.size == (256, 256) and os.path.getsize(p) < 1024 * 1024
        rows.append((note, img))
        print(tag, os.path.getsize(p), "bytes", note)
    cols, cw, chh = 3, 256 + 24, 256 + 110
    sheet = Image.new("RGB", (cols * cw + 16, 2 * chh + 16), (238, 236, 232))
    dr = ImageDraw.Draw(sheet)
    fb = ImageFont.truetype(r"C:\Windows\Fonts\georgiab.ttf", 15)
    for i, (note, img) in enumerate(rows):
        x, y = 16 + (i % cols) * cw, 16 + (i // cols) * chh
        sheet.paste(img, (x, y))
        xx = x
        for sz in (64, 32, 16):
            sheet.paste(img.resize((sz, sz), Image.LANCZOS), (xx, y + 262))
            xx += sz + 10
        dr.text((x, y + 332), "%d. %s" % (i + 1, note), font=fb, fill=(20, 20, 20))
    sp = os.path.join(T.OUT, "3d.png")
    sheet.save(sp, "PNG", optimize=True)
    print("wrote", sp)
    # THE CHOSEN IMAGE (user 2026-11-21: "Number 1, but please center it"): version 1, centred, as the Workshop
    # preview. The launcher wants it named like the pack and placed next to it in data\ at upload time.
    # FINAL_NUDGE_X: tuned by eye by the user ("A bit more to the right please"): the dark side reads as shadow, so
    # the bright face alone looked left of centre.
    final = compose(centred_mask(d, box, True, FINAL_NUDGE_X), "gold", "brushed", True)
    final.save(FINAL, "PNG", optimize=True)
    assert final.size == (256, 256) and os.path.getsize(FINAL) < 1024 * 1024
    print("wrote", FINAL, os.path.getsize(FINAL), "bytes")


if __name__ == "__main__":
    main()
