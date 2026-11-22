#!/usr/bin/env python3
"""Build harness204.lua from harness203.lua for round 206 (an exact wave's value counts standing enemies only).
Older harnesses are never edited. Edits: the banner, run_h204 and its call. No pin is rebased.
With DEV=<path> it writes a development copy that runs ONLY run_h204 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_cone_harness203\harness203.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_standing_harness204\harness204.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h204_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 204 - ROUND 206 (tuning): AN EXACT WAVE'S VALUE COUNTS STANDING ENEMIES ONLY (a unit still walking in will
--   have moved on when the fire arrives).
--   Edited vs harness203: this banner, run_h204 and its call.
--   RED control: H204_LIVE / H204_ANN on docs/backups/round206/pre206_*.lua.
-- ============================================================================
"""


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h203()\n") == 1
    src = src.replace("\nrun_h203()\n", "\nrun_h203()\nrun_h204()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!204)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
