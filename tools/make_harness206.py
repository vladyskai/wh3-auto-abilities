#!/usr/bin/env python3
"""Build harness206.lua from harness205.lua for round 208 (the cost of the free-aim search). Older harnesses are never
edited. Edits: the banner, run_h206 and its call. No pin is rebased.
With DEV=<path> it writes a development copy that runs ONLY run_h206 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_review_harness205\harness205.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_searchcost_harness206\harness206.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h206_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 206 - ROUND 208 (tuning): THE COST OF THE FREE-AIM SEARCH (no search while the ability cannot be cast, the
--   searches of several casters fall on different polls).
--   Edited vs harness205: this banner, run_h206 and its call.
--   RED control: H206_LIVE / H206_ANN on docs/backups/round208/pre208_*.lua.
-- ============================================================================
"""


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h205()\n") == 1
    src = src.replace("\nrun_h205()\n", "\nrun_h205()\nrun_h206()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!206)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
