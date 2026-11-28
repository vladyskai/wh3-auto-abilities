#!/usr/bin/env python3
"""Build harness216.lua from harness215.lua for round 218 (tuning, live copy only: the log's own cost in the timing
probe). Older harnesses are never edited. Edits: the banner, run_h216 and its call. No rebased pin.
With DEV=<path> it writes a development copy that runs ONLY run_h216 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_groupcards_harness215\harness215.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_logcost_harness216\harness216.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h216_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 216 - ROUND 218 (tuning, live copy only): the timing probe measures the test build's own log.
--   Edited vs harness215: this banner, run_h216 and its call. No rebased pin.
--   RED control: H216_LIVE on docs/backups/round218/pre218_live.lua.
-- ============================================================================
"""
PINS = []


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h215()\n") == 1
    src = src.replace("\nrun_h215()\n", "\nrun_h215()\nrun_h216()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!216)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
