#!/usr/bin/env python3
"""Build harness209.lua from harness208.lua for round 211 (tuning: the read-only raw unit probe of the test build).
Older harnesses are never edited. Edits: the banner, run_h209 and its call. No pin is rebased.
With DEV=<path> it writes a development copy that runs ONLY run_h209 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_replies2_harness208\harness208.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_rawprobe_harness209\harness209.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h209_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 209 - ROUND 211 (tuning): THE RAW UNIT PROBE of the test build (read-only).
--   Edited vs harness208: this banner, run_h209 and its call. No pin is rebased.
--   RED control: H209_LIVE on docs/backups/round211/pre211_live.lua.
-- ============================================================================
"""


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h208()\n") == 1
    src = src.replace("\nrun_h208()\n", "\nrun_h208()\nrun_h209()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!209)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
