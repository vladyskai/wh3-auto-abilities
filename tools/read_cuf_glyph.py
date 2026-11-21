#!/usr/bin/env python3
"""Read one glyph from a Total War .cuf font (layout from rpfm_lib's font module: "CUF0", 11 u16 properties, a u16
glyph count, a u32 data size, a u16 map for every code point 0..65535 (0xFFFF = unused), then per used glyph 4 bytes
(alloc_height i8, alloc_width u8, width u8, height u8), a u32 offset table, then width x height 8-bit greyscale bytes
per glyph, all in code order).

    python read_cuf_glyph.py <font.cuf> <char> [out.png]"""
import struct
import sys


def read(path):
    d = open(path, "rb").read()
    assert d[:4] == b"CUF0", d[:4]
    props = struct.unpack_from("<11H", d, 4)
    count, size = struct.unpack_from("<HI", d, 26)
    pos = 32
    codes = struct.unpack_from("<65536H", d, pos)
    pos += 2 * 65536
    used = [c for c in range(65536) if codes[c] != 0xFFFF]
    dims = {}
    for c in used:
        ah, aw, w, h = struct.unpack_from("<bBBB", d, pos)
        dims[c] = (ah, aw, w, h)
        pos += 4
    pos += 4 * len(used)
    data = {}
    for c in used:
        ah, aw, w, h = dims[c]
        n = w * h
        data[c] = d[pos:pos + n]
        pos += n
    return props, dims, data


def main():
    props, dims, data = read(sys.argv[1])
    c = ord(sys.argv[2])
    ah, aw, w, h = dims[c]
    print("props", props, "glyph", repr(sys.argv[2]), "alloc_height", ah, "advance", aw, "w", w, "h", h)
    px = data[c]
    for y in range(h):
        print("".join(" .:-=+*#%@"[min(9, b * 10 // 256)] for b in px[y * w:(y + 1) * w]))
    if len(sys.argv) > 3:
        from PIL import Image
        Image.frombytes("L", (w, h), bytes(px)).save(sys.argv[3])


if __name__ == "__main__":
    main()
