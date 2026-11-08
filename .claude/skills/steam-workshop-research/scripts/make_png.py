"""Write RGBA PNGs with the standard library only (zlib + struct) - no Pillow.

A mod's HUD art has to be a real PNG inside the pack, and the build machine may not
have an imaging library; this keeps the generator dependency-free and re-runnable.

    from make_png import write_png

    def draw(u, v):                 # u, v in 0.0-1.0 across the image
        "return (r, g, b, a) 0-255, or None for transparent"
        ...

    write_png(r"ui/zz_auto/auto_badge.png", 24, draw, scale=4)

`scale` supersamples: `draw` is called scale*scale times per output pixel and the
results averaged, which is what keeps a curved edge from stair-stepping. Reserve
this for simple shapes and dots - a letterform is better left to the engine's own
text component (see the skill's layout section); hand-rasterised letters were
rejected at HUD scale however clean the geometry.
"""

import struct
import zlib


def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) % 4294967296))


def write_png(path, size, draw, scale=4, compress=9):
    """Write a square RGBA PNG. size = side in pixels; draw(u, v) -> (r,g,b,a) or None."""
    rows = []
    n = scale * scale
    for y in range(size):
        row = bytearray(b"\x00")                      # filter byte: none
        for x in range(size):
            r = g = b = a = 0
            for sy in range(scale):
                for sx in range(scale):
                    u = (x + (sx + 0.5) / scale) / size
                    v = (y + (sy + 0.5) / scale) / size
                    px = draw(u, v)
                    if px:
                        r += px[0]
                        g += px[1]
                        b += px[2]
                        a += px[3]
            row += bytes((r // n, g // n, b // n, a // n))
        rows.append(bytes(row))
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)     # 8-bit RGBA
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(b"".join(rows), compress))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


if __name__ == "__main__":
    import sys

    def dot(u, v):                      # 16 px gold dot with a dark ring, clear corners
        d = ((u - 0.5) ** 2 + (v - 0.5) ** 2) ** 0.5
        if d < 0.30:
            return (205, 127, 50, 255)
        if d < 0.40:
            return (40, 25, 12, 255)
        return None

    out = sys.argv[1] if len(sys.argv) > 1 else "badge.png"
    print("wrote", write_png(out, 16, dot), "bytes to", out)
