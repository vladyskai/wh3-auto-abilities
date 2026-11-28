#!/usr/bin/env python3
"""Build harness218.lua from harness217.lua for round 220 (sign-off: placed effects do not wait for their caster, the
polls' speed fixes). Older harnesses are never edited. Edits: the banner, run_h218 and its call, the pins in PINS.
With DEV=<path> it writes a development copy that runs ONLY run_h218 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_cover_harness217\harness217.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_placed_harness218\harness218.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h218_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 218 - ROUND 220 (sign-off): a placed effect does not wait for its caster, the evaluator is not called while
--   the cast cannot go out, the blast numbers of a target are worked out once per map.
--   Edited vs harness217: this banner, run_h218 and its call, the rebased pins.
--   RED control: H218_LIVE / H218_ANN on docs/backups/round220/pre220_*.lua.
-- ============================================================================
"""
# the pins rebased in this round: (old text, new text, how many times it occurs)
PINS = [
    # harness 167 CA1 (the stand-still words only on animated casts): Frost Fang was its example of a cast that stops
    # its caster. Frost Fang is a PLACED effect (a vortex, no projectile): since round 220 its caster does not wait,
    # so its card names the target only. Volley of High Arrows (a projectile) stays the animated example.
    ('            and raw_find(by.frost_fang, "Fires when it and the target stand still, where the blast hurts the enemy most", 1, true) == 1\n',
     '            and raw_find(by.frost_fang, "Fires when the target stands still, where the blast hurts the enemy most", 1, true) == 1   -- HARNESS 218\n',
     1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h217()\n") == 1
    src = src.replace("\nrun_h217()\n", "\nrun_h217()\nrun_h218()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!218)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
