#!/usr/bin/env python3
"""Build harness212.lua from harness211.lua for round 214 (tuning: the timing probe of the test build). Older harnesses
are never edited. Edits: the banner, run_h212 and its call, and ONE line in load_world: the TEST-ONLY global
ZZ_AUTO_TEST_NO_PERF is set unless the world asks for the probe (W.perf_on), so every older world runs without it.
With DEV=<path> it writes a development copy that runs ONLY run_h212 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_selectcost_harness211\harness211.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261128_perfprobe_harness212\harness212.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h212_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 212 - ROUND 214 (tuning): THE TIMING PROBE of the test build (PERF lines, read-only).
--   Edited vs harness211: this banner, run_h212 and its call, load_world sets ZZ_AUTO_TEST_NO_PERF unless W.perf_on.
--   RED control: H212_LIVE on docs/backups/round214/pre214_live.lua.
-- ============================================================================
"""
PINS = [
    ("  ZZ_AUTO_TEST_REMEMBER_FILE = W.remember_file\n",
     "  ZZ_AUTO_TEST_REMEMBER_FILE = W.remember_file\n"
     "  ZZ_AUTO_TEST_NO_PERF = (W.perf_on ~= true)   -- HARNESS 212: the timing probe runs only where a world asks\n", 1),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h211()\n") == 1
    src = src.replace("\nrun_h211()\n", "\nrun_h211()\nrun_h212()\n")
    for old, new, n in PINS:
        assert src.count(old) == n, (old, src.count(old))
        src = src.replace(old, new)
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!212)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
