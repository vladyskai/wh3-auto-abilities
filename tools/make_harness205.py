#!/usr/bin/env python3
"""Build harness205.lua from harness204.lua for round 207 (the drifting waves count standing enemies only, a ground-only
wave without an aim holds). Older harnesses are never edited. Edits: the banner, run_h205 and its call. No pin rebased.
With DEV=<path> it writes a development copy that runs ONLY run_h205 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_standing_harness204\harness204.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_review_harness205\harness205.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h205_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 205 - ROUND 207 (tuning, the afternoon code review): THE DRIFTING WAVES COUNT STANDING ENEMIES ONLY, a
--   ground-only wave without an aim holds.
--   Edited vs harness204: this banner, run_h205 and its call.
--   RED control: H205_LIVE / H205_ANN on docs/backups/round207/pre207_*.lua.
-- ============================================================================
"""


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h204()\n") == 1
    src = src.replace("\nrun_h204()\n", "\nrun_h204()\nrun_h205()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!205)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
