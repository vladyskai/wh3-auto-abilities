#!/usr/bin/env python3
"""Build harness186.lua from harness185.lua for round 187 (the badges follow the wheel at any resolution or UI
scale). Older harnesses are never edited.

Rebases: see R (each names the pin and why)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_warpstorm_harness185\harness185.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_uiscale_harness186\harness186.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h186_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 186 - ROUND 187: THE BADGES FOLLOW THE WHEEL AT ANY RESOLUTION OR UI SCALE
--   (FOURTH.ui_shift_tick: the wheel's shift minus the bottom centre's shift, added to every
--   badge offset and to the ALL button's).
--   Edited vs harness185: this banner, the rebases listed in tools/make_harness186.py,
--   run_h186 and its call.
--   RED control: H186_LIVE / H186_ANN on docs/backups/round187/pre187_*.lua.
-- ============================================================================
"""
R = [
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h185()\n") == 1
src = src.replace("\nrun_h185()\n", "\nrun_h185()\nrun_h186()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
