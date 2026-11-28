#!/usr/bin/env python3
"""Build harness217.lua from harness216.lua for round 219 (sign-off: the cover rule and cavalry for the placed blasts,
the per-family timer). Older harnesses are never edited. Edits: the banner, run_h217 and its call, the pins in PINS.
With DEV=<path> it writes a development copy that runs ONLY run_h217 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_logcost_harness216\harness216.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_cover_harness217\harness217.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h217_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 217 - ROUND 219 (sign-off): the placed blasts hit most of the target unit, standing cavalry is a target,
--   the timing probe names the trigger families.
--   Edited vs harness216: this banner, run_h217 and its call, the rebased pins.
--   RED control: H217_LIVE / H217_ANN on docs/backups/round219/pre219_*.lua.
-- ============================================================================
"""
PINS = []


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h216()\n") == 1
    src = src.replace("\nrun_h216()\n", "\nrun_h216()\nrun_h217()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!217)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
