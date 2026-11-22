#!/usr/bin/env python3
"""Build harness203.lua from harness202.lua for round 205 (the growing waves are tested as the cones they are, enemy
single entities are not counted). Older harnesses are never edited.
Edits: the banner, ONE rebased pin (R), run_h203 and its call.
With DEV=<path> it writes a development copy that runs ONLY run_h203 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_exactwave_harness202\harness202.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_cone_harness203\harness203.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h203_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 203 - ROUND 205: THE GROWING WAVES ARE CONES (generated start radius and growth per metre), ENEMY SINGLE
--   ENTITIES ARE NOT COUNTED in an exact wave's value.
--   Edited vs harness202: this banner, one rebased pin (harness 202 EX5: 120 -> 100, see tools/make_harness203.py),
--   run_h203 and its call.
--   RED control: H203_LIVE / H203_ANN on docs/backups/round205/pre205_*.lua.
-- ============================================================================
"""
R = [
    # harness 202 EX5 measured the chosen path with a 6 m BAND from start to end and asked for 120 of 160 Zombies. The
    # ring is a cone (0.1 m -> 6 m): the path the cone model picks has 114 Zombies under the band measure. Old value
    # 120, new value 100. The cone itself is measured in harness 203.
    ("          good = theirs >= 120\n",
     "          good = theirs >= 100   -- HARNESS 203: 120 -> 100, the band measure of a path chosen for the real cone\n", 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    for a, b, n in R:
        assert src.count(a) == n, (a[:80], src.count(a))
        src = src.replace(a, b)
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h202()\n") == 1
    src = src.replace("\nrun_h202()\n", "\nrun_h202()\nrun_h203()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!203)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
