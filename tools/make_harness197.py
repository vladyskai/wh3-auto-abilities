#!/usr/bin/env python3
"""Build harness197.lua from harness196.lua for round 198 (the overnight review's fixes: rows 1, 2, 3, 6, 7, 8, 11).
Older harnesses are never edited. Edits: the banner, run_h197 and its call, and FOUR rebased pins (documented in
docs/WH3_round198_review_fixes.md):
  0zz   the charge-gate table: 347 rows -> 348 (Get Tha Gitz!'s row)
  0zz12 the ab_atarget line: 5 tabs (inside the poll) -> 1 tab (inside FOURTH.entry_reset)
  0zz28 FOURTH.BUGMAN_CLEAR_M = 38 -> 55
  0zz37 the eg_caster / eg_los lines: 5 tabs -> 1 tab (inside FOURTH.entry_reset)
With DEV=<path> it writes a development copy that runs ONLY run_h197 (never used as proof)."""
import os
import re
import sys

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_blobfallback_harness196\harness196.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_reviewfixes_harness197\harness197.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h197_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 197 - ROUND 198: THE OVERNIGHT REVIEW'S FIXES (the serial window re-armed by a repeat, the entry reset shared
--   with the air-drop fast pass, Get Tha Gitz!'s charge hold, the Necromancer on a Nightmare, the two auras on the
--   round-192 fast-enemy read, no self arm for Favour of the Fay and Shielding Swarm, Bugman's 55 m).
--   Edited vs harness196: this banner, four rebased pins (0zz, 0zz12, 0zz28, 0zz37), run_h197 and its call.
--   RED control: H197_LIVE / H197_ANN on docs/backups/round198/pre198_*.lua.
-- ============================================================================
"""
T5 = "\\t" * 5
REBASES = [
    ("blk ~= nil and cp103(blk, '\"] = ') == (RED_MODE and 0 or 347))",
     "blk ~= nil and cp103(blk, '\"] = ') == (RED_MODE and 0 or 348))   -- HARNESS 197: + Get Tha Gitz!"),
    ('and cp(s, "' + T5 + 'FOURTH.ab_atarget = ability.atarget") == 1',
     'and cp(s, "\\tFOURTH.ab_atarget = ability.atarget") == 1   -- HARNESS 197: inside FOURTH.entry_reset'),
    ('and cp(s, "\\nFOURTH.BUGMAN_CLEAR_M = 38") == 1',
     'and cp(s, "\\nFOURTH.BUGMAN_CLEAR_M = 55") == 1'),
    ('and cp(s, "' + T5 + 'FOURTH.eg_caster = unit   -- ROUND 189") == 1',
     'and cp(s, "\\tFOURTH.eg_caster = unit   -- ROUND 189") == 1'),
    ('and cp(s, "' + T5 + 'FOURTH.eg_los = (ability.los == true)") == 1',
     'and cp(s, "\\tFOURTH.eg_los = (ability.los == true)") == 1'),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    for a, b in REBASES:
        assert src.count(a) == 1, (a, src.count(a))
        src = src.replace(a, b)
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h196()\n") == 1
    src = src.replace("\nrun_h196()\n", "\nrun_h196()\nrun_h197()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!197)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
