#!/usr/bin/env python3
"""Build harness198.lua from harness197.lua for round 199 (the overnight review's second replies: rows 5, 9, 10, 12).
Older harnesses are never edited. Edits: the banner, run_h198 and its call, and THREE rebased count pins (the ten
ally-arm entries carry ally_range_real: 71 fields -> 81), documented in docs/WH3_round199_review_fixes2.md.
With DEV=<path> it writes a development copy that runs ONLY run_h198 (never used as proof)."""
import os
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_reviewfixes_harness197\harness197.lua"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261122_reviewfixes2_harness198\harness198.lua"
SECTION = open(r"C:\Users\vlady\Desktop\WH3_mod\tools\h198_section.lua", encoding="utf-8").read()
BANNER = """-- ============================================================================
-- HARNESS 198 - ROUND 199: THE OVERNIGHT REVIEW'S SECOND REPLIES (a key with a capital letter is claimed, the ally arm
--   of ten ally-targeted abilities, the bombardments' infantry test refuses large and flying units, the remembered
--   M/A choice sets the start of a battle only).
--   Edited vs harness197: this banner, three rebased count pins (ally_range_real 71 -> 81), run_h198 and its call.
--   RED control: H198_LIVE / H198_ANN on docs/backups/round199/pre199_*.lua.
-- ============================================================================
"""
REBASES = [
    ('cp98(s, "\\t\\tally_range_real = ") == 71)', 'cp98(s, "\\t\\tally_range_real = ") == 81)   -- HARNESS 198: + the ten ally arms'),
    ('and cp99(s, "\\t\\tally_range_real = ") == 71)', 'and cp99(s, "\\t\\tally_range_real = ") == 81)'),
    ('cp104(s, "\\t\\tally_range_real = ") == 71)', 'cp104(s, "\\t\\tally_range_real = ") == 81)'),
]


def main():
    src = open(SRC, encoding="utf-8").read()
    for a, b in REBASES:
        assert src.count(a) == 1, (a, src.count(a))
        src = src.replace(a, b)
    anchor = "\n-- THE RUNNER. The air-drop sections always run;"
    assert src.count(anchor) == 1
    src = src.replace(anchor, "\n" + SECTION + anchor)
    assert src.count("\nrun_h197()\n") == 1
    src = src.replace("\nrun_h197()\n", "\nrun_h197()\nrun_h198()\n")
    src = BANNER + src
    assert "\u2014" not in BANNER + SECTION
    dst = DST
    dev = os.environ.get("DEV")
    if dev:
        head, tail = src.split(anchor)
        tail = re.sub(r"\nrun_h(?!198)\d+\(\)", "", tail)
        src = head + anchor + tail
        dst = dev
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    open(dst, "w", encoding="utf-8", newline="\n").write(src)
    print("wrote", dst, len(src), "bytes")


if __name__ == "__main__":
    main()
