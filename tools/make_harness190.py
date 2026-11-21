#!/usr/bin/env python3
"""Build harness190.lua from harness189.lua for round 191 (group 1 of the stand-still audit; user 2026-11-21: "For now,
please only implement number 1."). Older harnesses are never edited.
New: run_h190 (tools/h190_section.lua). Rebases: none planned (any found by the full run are listed here)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_shotstill_harness189\harness189.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_still1_harness190\harness190.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h190_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 190 - ROUND 191: THE ANIMATION DECIDES IN GROUP 1 OF THE STAND-STILL AUDIT (user 2026-11-21: "For now,
--   please only implement number 1.").
--   Edited vs harness189: this banner, the rebases listed in tools/make_harness190.py, run_h190 and its call.
--   RED control: H190_LIVE / H190_ANN on docs/backups/round191/pre191_*.lua.
-- ============================================================================
"""
R = []
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h189()\n") == 1
src = src.replace("\nrun_h189()\n", "\nrun_h189()\nrun_h190()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
