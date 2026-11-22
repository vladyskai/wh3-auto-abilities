#!/usr/bin/env python3
"""Build harness200.lua from harness199.lua for round 202 (the wave probe, the console command zz_wave).
Older harnesses are never edited. Edits: the banner, run_h200 and its call. No pin is rebased.
With DEV=<path> it writes a development copy that runs ONLY run_h200 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_masterrunes_harness199\harness199.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_waveprobe_harness200\harness200.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h200_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 200 - ROUND 202: THE WAVE PROBE (the console command zz_wave of the test build: a ground-form cast with the
--   orientation argument, called by nothing).
--   Edited vs harness199: this banner, run_h200 and its call.
--   RED control: H200_LIVE / H200_ANN on docs/backups/round202/pre202_*.lua.
-- ============================================================================
"""


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h199()\n") == 1
    src = src.replace("\nrun_h199()\n", "\nrun_h199()\nrun_h200()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!200)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
