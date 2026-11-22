#!/usr/bin/env python3
"""Build harness201.lua from harness200.lua for round 203 (free aim for the 30 placed straight waves).
Older harnesses are never edited. Edits: the banner, load_world's ZZ_AUTO_TEST_NO_FREE_AIM line (older worlds keep the
caster's line only), the rebases in R (each names the pin and why), run_h201 and its call.
With DEV=<path> it writes a development copy that runs ONLY run_h201 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_waveprobe_harness200\harness200.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_freeaim_harness201\harness201.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h201_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 201 - ROUND 203: FREE AIM FOR THE STRAIGHT WAVES (the 30 enemy_wave entries test 24 headings per standing
--   enemy, the best path goes out in the ground form with its heading as orientation).
--   Edited vs harness200: this banner, load_world's ZZ_AUTO_TEST_NO_FREE_AIM line, the rebases listed in
--   tools/make_harness201.py, run_h201 and its call.
--   RED control: H201_LIVE / H201_ANN on docs/backups/round203/pre203_*.lua.
-- ============================================================================
"""
LOADW = "  ZZ_AUTO_TEST_NO_CLOSING = (W.closing_on ~= true)\n"
LOADW_NEW = (LOADW
             + "  -- ROUND 203: older worlds test the caster's own line only. A world that tests free aim sets W.free_aim_on\n"
             + "  -- (and supplies the game's vector constructor v and bm:get_terrain_height).\n"
             + "  ZZ_AUTO_TEST_NO_FREE_AIM = (W.free_aim_on ~= true)\n")
R = [
]


def main():
    src = open(SRC, encoding="utf-8").read()
    assert src.count(LOADW) == 1
    src = src.replace(LOADW, LOADW_NEW)
    for a, b, n in R:
        assert src.count(a) == n, (a[:80], src.count(a))
        src = src.replace(a, b)
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h200()\n") == 1
    src = src.replace("\nrun_h200()\n", "\nrun_h200()\nrun_h201()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!201)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
