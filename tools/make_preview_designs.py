#!/usr/bin/env python3
"""Twelve Workshop preview designs for Smart Ability Autocast that look like the game's real ability wheel (user
2026-11-21, with a screenshot of the wheel: "change the icon to better represent the actual ability wheel. Produce at
least 10 designs."). Everything is drawn with code at 4x and scaled down (no game art, no pixelation): a bronze portrait
ring with a helmeted silhouette, the ability buttons in an arc on its right, each with the mod's M/A letter, a chain.

Out: mod_source/workshop/designs/design_01.png ... design_12.png (512 x 512, each well under 1 MB) and
contact_sheet.png (all twelve, numbered)."""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\workshop\designs"
SIZE = 512
S = 4
W = SIZE * S
SERIF = r"C:\Windows\Fonts\georgiab.ttf"
GOLD = (226, 188, 108)
GOLD_DARK = (112, 80, 32)
BRONZE = (150, 96, 52)
BRONZE_LIGHT = (214, 160, 96)
BRONZE_DARK = (70, 42, 22)
GREEN = (70, 176, 84)
GREY = (96, 96, 104)


def P(v):
    return v * S


def font(size):
    return ImageFont.truetype(SERIF, int(P(size)))


# ---------------------------------------------------------------- backgrounds
def bg_radial(inner, outer, cx=0.5, cy=0.5):
    img = Image.new("RGB", (W, W), outer)
    d = ImageDraw.Draw(img)
    rmax = int(W * 0.8)
    for r in range(rmax, 0, -S * 2):
        t = r / rmax
        col = tuple(int(inner[i] * (1 - t) + outer[i] * t) for i in range(3))
        d.ellipse([W * cx - r, W * cy - r, W * cx + r, W * cy + r], fill=col)
    return img


def bg_battle():
    """The blue-grey haze of the screenshot's battlefield, with soft cloud blots."""
    img = bg_radial((150, 168, 178), (58, 70, 82), 0.62, 0.45)
    blot = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(blot)
    import random
    rnd = random.Random(7)
    for _ in range(40):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, W), rnd.uniform(P(20), P(90))
        d.ellipse([x - r, y - r, x + r, y + r], fill=rnd.randint(20, 60))
    blot = blot.filter(ImageFilter.GaussianBlur(P(18)))
    img.paste((205, 215, 222), (0, 0), blot)
    return img


def vignette(img, strength=170):
    m = Image.new("L", (W, W), 0)
    d = ImageDraw.Draw(m)
    d.ellipse([-W * 0.25, -W * 0.25, W * 1.25, W * 1.25], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(P(60)))
    dark = Image.new("RGB", (W, W), (0, 0, 0))
    inv = m.point(lambda v: int((255 - v) * strength / 255))
    img.paste(dark, (0, 0), inv)
    return img


# ---------------------------------------------------------------- parts
def disc(d, cx, cy, r, fill=None, outline=None, width=0):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=int(width))


def bronze_ring(d, cx, cy, r, t):
    """A bronze frame of thickness t: dark edge, a warm body, a bright inner highlight, a dark inner line."""
    disc(d, cx, cy, r + t, fill=BRONZE_DARK)
    disc(d, cx, cy, r + t * 0.85, fill=BRONZE)
    disc(d, cx, cy, r + t * 0.45, fill=BRONZE_LIGHT)
    disc(d, cx, cy, r + t * 0.3, fill=BRONZE)
    disc(d, cx, cy, r + t * 0.08, fill=BRONZE_DARK)


def portrait(img, cx, cy, r, tint=(60, 86, 96)):
    """The lord: a helmeted bust silhouette inside the ring (a generic stand-in, no game art)."""
    d = ImageDraw.Draw(img)
    disc(d, cx, cy, r, fill=tint)
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    steel, steel_dark, skin = (190, 196, 204), (110, 116, 126), (198, 156, 128)
    # shoulders and breastplate
    ld.ellipse([cx - r * 0.95, cy + r * 0.35, cx + r * 0.95, cy + r * 1.7], fill=(170, 140, 70))
    ld.ellipse([cx - r * 0.6, cy + r * 0.45, cx + r * 0.6, cy + r * 1.4], fill=(205, 176, 96))
    # face and helmet
    ld.ellipse([cx - r * 0.3, cy - r * 0.35, cx + r * 0.3, cy + r * 0.38], fill=skin)
    ld.pieslice([cx - r * 0.42, cy - r * 0.72, cx + r * 0.42, cy + r * 0.12], 180, 360, fill=steel)
    ld.rectangle([cx - r * 0.42, cy - r * 0.32, cx - r * 0.26, cy + r * 0.32], fill=steel_dark)
    ld.rectangle([cx + r * 0.26, cy - r * 0.32, cx + r * 0.42, cy + r * 0.32], fill=steel_dark)
    ld.rectangle([cx - r * 0.42, cy - r * 0.34, cx + r * 0.42, cy - r * 0.24], fill=(214, 182, 96))
    ld.rectangle([cx - r * 0.05, cy - r * 0.34, cx + r * 0.05, cy + r * 0.02], fill=steel_dark)
    ld.polygon([(cx - r * 0.06, cy - r * 0.72), (cx + r * 0.06, cy - r * 0.72), (cx, cy - r * 0.95)], fill=(214, 182, 96))
    mask = Image.new("L", (W, W), 0)
    ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    img.paste(layer, (0, 0), Image.composite(layer.split()[3], Image.new("L", (W, W), 0), mask))


def glyph(d, kind, cx, cy, r, col=(236, 222, 190)):
    g = col
    if kind == "sword":
        d.polygon([(cx, cy - r * 0.9), (cx + r * 0.16, cy - r * 0.6), (cx + r * 0.12, cy + r * 0.35),
                   (cx - r * 0.12, cy + r * 0.35), (cx - r * 0.16, cy - r * 0.6)], fill=g)
        d.rectangle([cx - r * 0.5, cy + r * 0.35, cx + r * 0.5, cy + r * 0.48], fill=g)
        d.rectangle([cx - r * 0.08, cy + r * 0.48, cx + r * 0.08, cy + r * 0.85], fill=g)
    elif kind == "bolt":
        d.polygon([(cx + r * 0.15, cy - r * 0.9), (cx - r * 0.45, cy + r * 0.1), (cx - r * 0.02, cy + r * 0.1),
                   (cx - r * 0.2, cy + r * 0.9), (cx + r * 0.45, cy - r * 0.15), (cx + r * 0.02, cy - r * 0.15)], fill=g)
    elif kind == "shield":
        d.polygon([(cx - r * 0.6, cy - r * 0.7), (cx + r * 0.6, cy - r * 0.7), (cx + r * 0.6, cy - r * 0.05),
                   (cx, cy + r * 0.85), (cx - r * 0.6, cy - r * 0.05)], fill=g)
        d.line([(cx, cy - r * 0.7), (cx, cy + r * 0.85)], fill=(60, 90, 110), width=max(2, int(r * 0.12)))
        d.line([(cx - r * 0.6, cy - r * 0.2), (cx + r * 0.6, cy - r * 0.2)], fill=(60, 90, 110), width=max(2, int(r * 0.12)))
    elif kind == "flame":
        d.ellipse([cx - r * 0.45, cy - r * 0.1, cx + r * 0.45, cy + r * 0.8], fill=(240, 160, 60))
        d.polygon([(cx - r * 0.45, cy + r * 0.35), (cx - r * 0.2, cy - r * 0.5), (cx, cy - r * 0.15),
                   (cx + r * 0.15, cy - r * 0.9), (cx + r * 0.45, cy + r * 0.35)], fill=(240, 160, 60))
        d.ellipse([cx - r * 0.2, cy + r * 0.25, cx + r * 0.2, cy + r * 0.7], fill=(255, 230, 140))
    elif kind == "star":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            rr = r * (0.9 if i % 2 == 0 else 0.4)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        d.polygon(pts, fill=(255, 236, 160))
    elif kind == "heal":
        t = r * 0.22
        d.rectangle([cx - t, cy - r * 0.7, cx + t, cy + r * 0.7], fill=(150, 230, 150))
        d.rectangle([cx - r * 0.7, cy - t, cx + r * 0.7, cy + t], fill=(150, 230, 150))
    elif kind == "skull":
        d.ellipse([cx - r * 0.55, cy - r * 0.7, cx + r * 0.55, cy + r * 0.35], fill=g)
        d.rectangle([cx - r * 0.3, cy + r * 0.2, cx + r * 0.3, cy + r * 0.6], fill=g)
        disc(d, cx - r * 0.22, cy - r * 0.15, r * 0.16, fill=(30, 24, 20))
        disc(d, cx + r * 0.22, cy - r * 0.15, r * 0.16, fill=(30, 24, 20))


def button(img, cx, cy, r, kind, letter="A", inner=(36, 40, 46), marker=True, glow=False, letter_style="band"):
    """One wheel button: a bronze rim, a dark face with the ability glyph, the mod's letter, the green marker above."""
    d = ImageDraw.Draw(img)
    if glow:
        g = Image.new("L", (W, W), 0)
        disc(ImageDraw.Draw(g), cx, cy, r * 1.55, fill=200)
        g = g.filter(ImageFilter.GaussianBlur(r * 0.35))
        img.paste((120, 255, 140), (0, 0), g)
        d = ImageDraw.Draw(img)
    disc(d, cx, cy, r * 1.14, fill=BRONZE_DARK)
    disc(d, cx, cy, r * 1.08, fill=BRONZE_LIGHT)
    disc(d, cx, cy, r * 1.0, fill=BRONZE_DARK)
    disc(d, cx, cy, r * 0.94, fill=inner)
    glyph(d, kind, cx, cy - r * 0.12, r * 0.55)
    if letter is not None:
        f = font(r / S * 0.5)
        if letter_style == "band":
            band = (230, 226, 214) if letter == "A" else (150, 150, 156)
            d.chord([cx - r * 0.94, cy - r * 0.94, cx + r * 0.94, cy + r * 0.94], 35, 145, fill=(20, 22, 26))
            bb = d.textbbox((0, 0), letter, font=f)
            d.text((cx - (bb[2] + bb[0]) / 2, cy + r * 0.62 - (bb[3] + bb[1]) / 2), letter, font=f, fill=band)
        else:   # a round badge at the top-right, the mod's look on a plain button
            br = r * 0.36
            bx, by = cx + r * 0.78, cy - r * 0.78
            disc(d, bx, by, br, fill=GREEN if letter == "A" else GREY, outline=(240, 232, 210), width=max(2, br * 0.14))
            f2 = font(br / S * 1.1)
            bb = d.textbbox((0, 0), letter, font=f2)
            d.text((bx - (bb[2] + bb[0]) / 2, by - (bb[3] + bb[1]) / 2), letter, font=f2, fill=(255, 255, 255))
    if marker:
        mx, my, mr = cx, cy - r * 1.32, r * 0.24
        disc(d, mx, my, mr, fill=(20, 24, 22), outline=(150, 230, 170), width=max(2, mr * 0.18))
        d.polygon([(mx, my - mr * 0.55), (mx + mr * 0.5, my + mr * 0.35), (mx - mr * 0.5, my + mr * 0.35)], fill=(236, 240, 236))


def chain(d, x0, y0, x1, y1, link):
    n = int(math.hypot(x1 - x0, y1 - y0) / (link * 1.4))
    ang = math.atan2(y1 - y0, x1 - x0)
    for i in range(n + 1):
        t = i / max(1, n)
        x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        ca, sa = math.cos(ang), math.sin(ang)
        if i % 2 == 0:
            w, h = link, link * 0.55
        else:
            w, h = link, link * 0.25
        pts = []
        for k in range(24):
            a = k * 2 * math.pi / 24
            px_, py_ = w * math.cos(a), h * math.sin(a)
            pts.append((x + px_ * ca - py_ * sa, y + px_ * sa + py_ * ca))
        d.polygon(pts, outline=(36, 26, 20), fill=(76, 58, 44))
        inner = [((px_ - x) * 0.55 + x, (py_ - y) * 0.55 + y) for px_, py_ in pts]
        d.polygon(inner, fill=(28, 20, 16))


def ribbon(img, cx, cy, w, h, text, size):
    d = ImageDraw.Draw(img)
    col, dark = (122, 70, 38), (70, 38, 20)
    d.polygon([(cx - w / 2 - h * 0.6, cy - h * 0.2), (cx - w / 2, cy - h * 0.2), (cx - w / 2, cy + h * 0.7),
               (cx - w / 2 - h * 0.6, cy + h * 0.7), (cx - w / 2 - h * 0.35, cy + h * 0.25)], fill=dark)
    d.polygon([(cx + w / 2 + h * 0.6, cy - h * 0.2), (cx + w / 2, cy - h * 0.2), (cx + w / 2, cy + h * 0.7),
               (cx + w / 2 + h * 0.6, cy + h * 0.7), (cx + w / 2 + h * 0.35, cy + h * 0.25)], fill=dark)
    d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=col, outline=(180, 120, 70), width=int(P(2)))
    f = font(size)
    bb = d.textbbox((0, 0), text, font=f)
    d.text((cx - (bb[2] + bb[0]) / 2, cy - (bb[3] + bb[1]) / 2), text, font=f, fill=GOLD,
           stroke_width=int(P(1.2)), stroke_fill=(50, 28, 14))


def title(img, text, cy, size, fill=GOLD, edge=GOLD_DARK, cx=None):
    """size is already in drawing pixels (callers pass P(points))."""
    f = ImageFont.truetype(SERIF, int(size))
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0, 0), text, font=f)
    x = (W if cx is None else 2 * cx) / 2 - (bb[2] + bb[0]) / 2
    y = cy - (bb[3] + bb[1]) / 2
    sh = Image.new("L", (W, W), 0)
    ImageDraw.Draw(sh).text((x, y + P(3)), text, font=f, fill=255)
    sh = sh.filter(ImageFilter.GaussianBlur(P(4)))
    img.paste((0, 0, 0), (0, 0), sh)
    d.text((x, y), text, font=f, fill=fill, stroke_width=int(P(1.5)), stroke_fill=edge)


def wheel(img, cx, cy, pr, n=4, a0=-62, a1=62, br=None, letters=None, kinds=None, orbit=None, **kw):
    """The portrait in its bronze ring and n buttons on an arc to its right (angles in degrees, 0 = straight right)."""
    d = ImageDraw.Draw(img)
    bronze_ring(d, cx, cy, pr, pr * 0.12)
    portrait(img, cx, cy, pr)
    br = br or pr * 0.36
    orbit = orbit or pr * 1.2
    kinds = kinds or ["star", "sword", "shield", "bolt", "flame", "heal", "skull", "star"]
    letters = letters or ["A"] * n
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * (i / max(1, n - 1)))
        button(img, cx + orbit * math.cos(a), cy + orbit * math.sin(a), br, kinds[i % len(kinds)], letters[i], **kw)


# ---------------------------------------------------------------- the designs
def d01():
    img = vignette(bg_battle())
    chain(ImageDraw.Draw(img), P(-10), P(100), P(110), P(145), P(14))
    wheel(img, P(185), P(205), P(112))
    title(img, "SMART ABILITY", P(420), P(40))
    title(img, "AUTOCAST", P(470), P(48))
    return img


def d02():
    img = vignette(bg_battle())
    title(img, "SMART ABILITY AUTOCAST", P(42), P(30))
    chain(ImageDraw.Draw(img), P(-10), P(150), P(120), P(205), P(14))
    wheel(img, P(200), P(285), P(122), n=5, a0=-80, a1=80)
    return img


def d03():
    img = vignette(bg_radial((70, 22, 16), (12, 8, 8)))
    wheel(img, P(110), P(262), P(150), n=4, a0=-44, a1=44, br=P(48), orbit=P(205))
    title(img, "SMART ABILITY", P(30), P(30), cx=P(256))
    title(img, "AUTOCAST", P(488), P(40), cx=P(256))
    return img


def d04():
    img = vignette(bg_battle())
    wheel(img, P(185), P(225), P(115), n=4, letters=["M", "A", "A", "A"])
    ribbon(img, P(256), P(440), P(330), P(64), "AUTOCAST", 34)
    title(img, "SMART ABILITY", P(42), P(36))
    return img


def d05():
    img = vignette(bg_radial((120, 80, 52), (30, 18, 12)))
    chain(ImageDraw.Draw(img), P(-10), P(70), P(150), P(130), P(14))
    wheel(img, P(200), P(220), P(122))
    ribbon(img, P(256), P(436), P(380), P(70), "SMART ABILITY AUTOCAST", 25)
    return img


def d06():
    img = vignette(bg_radial((80, 20, 16), (14, 8, 8)))
    chain(ImageDraw.Draw(img), P(-10), P(100), P(110), P(145), P(14))
    wheel(img, P(185), P(205), P(112))
    title(img, "SMART ABILITY", P(420), P(40))
    title(img, "AUTOCAST", P(470), P(48))
    return img


def d07():
    img = vignette(bg_battle())
    chain(ImageDraw.Draw(img), P(-10), P(60), P(140), P(120), P(16))
    wheel(img, P(200), P(256), P(150), n=4, a0=-60, a1=60, br=P(52), orbit=P(185))
    return img


def d08():
    img = vignette(bg_radial((40, 44, 52), (10, 10, 14)))
    faint = Image.new("RGB", (W, W), (0, 0, 0))
    wheel(faint, P(110), P(256), P(130), n=4, a0=-60, a1=60)
    img = Image.blend(img, faint, 0.35)
    button(img, P(300), P(250), P(120), "bolt", "A", letter_style="badge", glow=True)
    title(img, "SMART ABILITY", P(42), P(36))
    title(img, "AUTOCAST", P(470), P(48))
    return img


def d09():
    img = vignette(bg_battle())
    d = ImageDraw.Draw(img)
    cx, cy, pr = P(256), P(240), P(95)
    bronze_ring(d, cx, cy, pr, pr * 0.12)
    portrait(img, cx, cy, pr)
    kinds = ["star", "sword", "shield", "bolt", "flame", "heal", "skull", "sword"]
    for i in range(8):
        a = -math.pi / 2 + i * 2 * math.pi / 8
        button(img, cx + P(150) * math.cos(a), cy + P(150) * math.sin(a), P(34), kinds[i],
               "A" if i % 3 else "M", marker=False)
    title(img, "SMART ABILITY AUTOCAST", P(478), P(28))
    return img


def d10():
    img = vignette(bg_battle())
    chain(ImageDraw.Draw(img), P(-10), P(100), P(110), P(145), P(14))
    d = ImageDraw.Draw(img)
    cx, cy, pr = P(185), P(205), P(112)
    bronze_ring(d, cx, cy, pr, pr * 0.12)
    portrait(img, cx, cy, pr)
    kinds = ["star", "sword", "shield", "bolt"]
    for i in range(4):
        a = math.radians(-62 + 124 * i / 3)
        bx, by = cx + pr * 1.2 * math.cos(a), cy + pr * 1.2 * math.sin(a)
        if i == 1:   # this one is casting by itself: light rays
            rays = ImageDraw.Draw(img)
            for k in range(12):
                ra = k * math.pi / 6
                rays.line([(bx + P(52) * math.cos(ra), by + P(52) * math.sin(ra)),
                           (bx + P(80) * math.cos(ra), by + P(80) * math.sin(ra))], fill=(200, 255, 200), width=int(P(3)))
        button(img, bx, by, pr * 0.36, kinds[i], "A", glow=(i == 1))
    title(img, "SMART ABILITY", P(420), P(40))
    title(img, "AUTOCAST", P(470), P(48))
    return img


def d11():
    img = vignette(bg_radial((30, 46, 78), (6, 10, 20)))
    wheel(img, P(200), P(220), P(122), inner=(24, 30, 44))
    ribbon(img, P(256), P(436), P(380), P(70), "SMART ABILITY AUTOCAST", 25)
    return img


def d12():
    """Flat and bold: the wheel as a simple arc of rings and one big word."""
    img = Image.new("RGB", (W, W), (24, 20, 18))
    d = ImageDraw.Draw(img)
    cx, cy = P(150), P(250)
    disc(d, cx, cy, P(110), outline=BRONZE_LIGHT, width=P(10))
    disc(d, cx, cy, P(88), fill=(50, 70, 78))
    f = font(64)
    bb = d.textbbox((0, 0), "A", font=f)
    d.text((cx - (bb[2] + bb[0]) / 2, cy - (bb[3] + bb[1]) / 2), "A", font=f, fill=(240, 230, 200))
    for i in range(4):
        a = math.radians(-62 + 124 * i / 3)
        bx, by = cx + P(150) * math.cos(a), cy + P(150) * math.sin(a)
        disc(d, bx, by, P(38), outline=BRONZE_LIGHT, width=P(7))
        disc(d, bx, by, P(30), fill=GREEN)
        f2 = font(30)
        bb = d.textbbox((0, 0), "A", font=f2)
        d.text((bx - (bb[2] + bb[0]) / 2, by - (bb[3] + bb[1]) / 2), "A", font=f2, fill=(255, 255, 255))
    title(img, "AUTOCAST", P(462), P(56))
    title(img, "SMART ABILITY", P(48), P(34))
    return img


DESIGNS = [d01, d02, d03, d04, d05, d06, d07, d08, d09, d10, d11, d12]
NAMES = ["Wheel, title below", "Five buttons, title on top", "Close-up, big buttons", "M then A, ribbon",
         "Warm bronze, ribbon", "Dark red, title below", "Wheel only, no text", "One glowing button",
         "Full circle of eight", "One button casting", "Night blue, ribbon", "Flat and bold"]


def main():
    os.makedirs(OUT, exist_ok=True)
    thumbs = []
    for i, fn in enumerate(DESIGNS, start=1):
        img = fn().resize((SIZE, SIZE), Image.LANCZOS)
        p = os.path.join(OUT, "design_%02d.png" % i)
        img.save(p, "PNG", optimize=True)
        assert os.path.getsize(p) < 1024 * 1024, p
        thumbs.append(img)
        print("design_%02d.png %7d bytes  %s" % (i, os.path.getsize(p), NAMES[i - 1]))
    # the contact sheet: 4 x 3, each 256 px with its number and name
    cell, pad, cap = 256, 12, 34
    sheet = Image.new("RGB", (4 * (cell + pad) + pad, 3 * (cell + pad + cap) + pad), (32, 30, 30))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(SERIF, 15)
    for i, t in enumerate(thumbs):
        x = pad + (i % 4) * (cell + pad)
        y = pad + (i // 4) * (cell + pad + cap)
        sheet.paste(t.resize((cell, cell), Image.LANCZOS), (x, y))
        d.text((x, y + cell + 6), "%d. %s" % (i + 1, NAMES[i]), font=f, fill=(230, 220, 200))
    p = os.path.join(OUT, "contact_sheet.png")
    sheet.save(p, "PNG", optimize=True)
    print("contact_sheet.png", os.path.getsize(p), "bytes")


if __name__ == "__main__":
    main()
