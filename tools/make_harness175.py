#!/usr/bin/env python3
"""Build harness175.lua from harness174.lua for round 176 (Master of Mists starts armed). Older harnesses are never edited.

Rebase: the round-170 pin on plain start_armed lines, 8 -> 9 (Master of Mists)."""
import os

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_master_of_mists_harness174\harness174.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_mists_armed_harness175\harness175.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h175_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 175 - ROUND 176: MASTER OF MISTS STARTS ARMED.
--   Edited vs harness174: this banner, the rebase listed in tools/make_harness175.py,
--   run_h175 and its call.
--   RED control: H175_LIVE / H175_ANN on docs/backups/round176/pre176_*.lua.
-- ============================================================================
"""
R = [
    ('        and cp(s, "\\t\\tstart_armed = true,\\n") == 8',
     '        and cp(s, "\\t\\tstart_armed = true,\\n") == 9   -- HARNESS 175: Master of Mists', 1),
]
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
RUNNER_ANCHOR = "\n-- THE RUNNER. The air-drop sections always run;"
assert src.count(RUNNER_ANCHOR) == 1
src = src.replace(RUNNER_ANCHOR, "\n" + SECTION + RUNNER_ANCHOR)
assert src.count("\nrun_h174()\n") == 1
src = src.replace("\nrun_h174()\n", "\nrun_h174()\nrun_h175()\n")
src = BANNER + src
assert "\u2014" not in BANNER + SECTION
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST, len(src), "bytes")
