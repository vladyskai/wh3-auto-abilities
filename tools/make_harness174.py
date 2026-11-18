#!/usr/bin/env python3
"""Build harness174.lua from harness173.lua for round 175 (Master of Mists: before range, else shooting). Older
harnesses are never edited.

Rebases: see R (each names the pin and why)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_review_rows_harness173\harness173.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_master_of_mists_harness174\harness174.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h174_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 174 - ROUND 175: MASTER OF MISTS, BEFORE RANGE ELSE SHOOTING.
--   Edited vs harness173: this banner, the rebases listed in tools/make_harness174.py,
--   run_h174 and its call.
--   RED control: H174_LIVE / H174_ANN on docs/backups/round175/pre175_*.lua.
-- ============================================================================
"""
R = [
    # h93 TIP mirror: the new label
    ('    ground_ally_before_range = "When armed, fires under a friendly missile unit when the enemy is just out of its range",\n',
     '    ground_ally_before_range = "When armed, fires under a friendly missile unit when the enemy is just out of its range, else under the shooting missile units",   -- HARNESS 174\n', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h173()\n") == 1
src = src.replace("\nrun_h173()\n", "\nrun_h173()\nrun_h174()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
