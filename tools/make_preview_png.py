#!/usr/bin/env python3
"""Draw the Steam Workshop preview image for Smart Ability Autocast (user 2026-11-21: "The .png I get from the game are
too pixelated. I want to create it."). Drawn with code at 4x and scaled down, so every edge is smooth.

Out: mod_source/workshop/smart_ability_autocast.png (512 x 512, must stay under 1 MB; the launcher wants the PNG named
exactly like the pack, next to it in the game's data folder at upload time).

Design: a dark battlefield-red background with a vignette, an ability wheel of six gold-rimmed slots around a central
medallion, each slot with a simple ability glyph and the mod's own M/A badge (green A = automatic, grey M = manual), and
the title in gold."""
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\workshop\designs\old_preview_512.png"   # RETIRED 2026-11-21: the Workshop image comes from tools/make_game_a_3d.py (FINAL)
SIZE = 512
S = 4                      # supersampling factor
W = SIZE * S
FONT = r"C:\Windows\Fonts\georgiab.ttf"
GOLD = (222, 184, 104)
GOLD_DARK = (120, 86, 34)
GREEN = (74, 170, 76)
GREY = (90, 90, 96)
INK = (18, 12, 10)


def px(v):
    return int(round(v * S))


def background():
    img = Image.new("RGB", (W, W), INK)
    d = ImageDraw.Draw(img)
    cx = cy = W / 2
    # radial gradient: dark red centre to near black edge
    for r in range(int(W * 0.75), 0, -S * 2):
        t = r / (W * 0.75)
        col = (int(70 * (1 - t) + 14 * t), int(18 * (1 - t) + 8 * t), int(14 * (1 - t) + 8 * t))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    return img


def ring(d, cx, cy, r, width, col):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=width)


def glyph(d, kind, cx, cy, r):
    g = GOLD
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
        d.polygon([(cx - r * 0.4, cy - r * 0.5), (cx + r * 0.4, cy - r * 0.5), (cx + r * 0.4, cy - r * 0.08),
                   (cx, cy + r * 0.55), (cx - r * 0.4, cy - r * 0.08)], fill=(92, 30, 24))
    elif kind == "flame":
        d.ellipse([cx - r * 0.45, cy - r * 0.1, cx + r * 0.45, cy + r * 0.8], fill=g)
        d.polygon([(cx - r * 0.45, cy + r * 0.35), (cx - r * 0.2, cy - r * 0.5), (cx, cy - r * 0.15),
                   (cx + r * 0.15, cy - r * 0.9), (cx + r * 0.45, cy + r * 0.35)], fill=g)
        d.ellipse([cx - r * 0.2, cy + r * 0.25, cx + r * 0.2, cy + r * 0.7], fill=(92, 30, 24))
    elif kind == "arrow":
        d.line([(cx - r * 0.7, cy + r * 0.7), (cx + r * 0.45, cy - r * 0.45)], fill=g, width=max(2, int(r * 0.14)))
        d.polygon([(cx + r * 0.75, cy - r * 0.75), (cx + r * 0.2, cy - r * 0.55), (cx + r * 0.55, cy - r * 0.2)], fill=g)
        # the fletching: two short feathers each side of the tail
        fw = max(2, int(r * 0.1))
        for k in (0.0, 0.22):
            bx, by = cx - r * (0.62 - k), cy + r * (0.62 - k)
            d.line([(bx, by), (bx - r * 0.28, by - r * 0.02)], fill=g, width=fw)
            d.line([(bx, by), (bx + r * 0.02, by + r * 0.28)], fill=g, width=fw)
    elif kind == "heal":
        t = r * 0.22
        d.rectangle([cx - t, cy - r * 0.7, cx + t, cy + r * 0.7], fill=g)
        d.rectangle([cx - r * 0.7, cy - t, cx + r * 0.7, cy + t], fill=g)


def badge(d, cx, cy, r, letter, font):
    fill = GREEN if letter == "A" else GREY
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=(240, 230, 200), width=max(2, int(r * 0.14)))
    bb = d.textbbox((0, 0), letter, font=font)
    d.text((cx - (bb[2] + bb[0]) / 2, cy - (bb[3] + bb[1]) / 2), letter, font=font, fill=(255, 255, 255))


def title(img, text, cy, size):
    font = ImageFont.truetype(FONT, size)
    d = ImageDraw.Draw(img)
    bb = d.textbbox((0, 0), text, font=font)
    x = (W - (bb[2] - bb[0])) / 2 - bb[0]
    y = cy - (bb[3] + bb[1]) / 2
    # a soft dark shadow, then the gold letters with a darker gold edge
    shadow = Image.new("L", (W, W), 0)
    ImageDraw.Draw(shadow).text((x, y + px(3)), text, font=font, fill=255)
    shadow = shadow.filter(ImageFilter.GaussianBlur(px(4)))
    img.paste((0, 0, 0), (0, 0), shadow)
    d.text((x, y), text, font=font, fill=GOLD, stroke_width=px(1.5), stroke_fill=GOLD_DARK)


def main():
    img = background()
    d = ImageDraw.Draw(img)
    cx, cy = W / 2, W / 2 + px(18)
    R = px(128)                        # the wheel's radius
    ring(d, cx, cy, R, px(5), GOLD_DARK)
    ring(d, cx, cy, R - px(6), px(2), GOLD)
    slots = ["sword", "bolt", "shield", "flame", "arrow", "heal"]
    letters = ["A", "A", "M", "A", "A", "M"]
    sr = px(40)
    bfont = ImageFont.truetype(FONT, px(17))
    for i, kind in enumerate(slots):
        a = -math.pi / 2 + i * 2 * math.pi / len(slots)
        sx, sy = cx + R * math.cos(a), cy + R * math.sin(a)
        d.ellipse([sx - sr - px(4), sy - sr - px(4), sx + sr + px(4), sy + sr + px(4)], fill=(10, 6, 5))
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(52, 20, 16), outline=GOLD, width=px(4))
        glyph(d, kind, sx, sy, sr * 0.74)
        badge(d, sx + sr * 0.72, sy - sr * 0.72, px(14), letters[i], bfont)
    # the central medallion: a large A for automatic
    mr = px(58)
    d.ellipse([cx - mr - px(5), cy - mr - px(5), cx + mr + px(5), cy + mr + px(5)], fill=GOLD_DARK)
    d.ellipse([cx - mr, cy - mr, cx + mr, cy + mr], fill=(30, 74, 34), outline=GOLD, width=px(4))
    mfont = ImageFont.truetype(FONT, px(78))
    bb = d.textbbox((0, 0), "A", font=mfont)
    d.text((cx - (bb[2] + bb[0]) / 2, cy - (bb[3] + bb[1]) / 2), "A", font=mfont, fill=(245, 235, 205),
           stroke_width=px(2), stroke_fill=(20, 40, 20))
    title(img, "SMART ABILITY", px(46), px(44))
    title(img, "AUTOCAST", px(478), px(52))
    out = img.resize((SIZE, SIZE), Image.LANCZOS)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
