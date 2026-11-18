#!/usr/bin/env python3
"""Build the round-176 build script from the round-175 one (Master of Mists starts armed).
Rebase: plain start_armed lines 8 -> 9. ROUND 176 GATE: the Master of Mists entry carries start_armed."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_master_of_mists_harness174\build_and_install175.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_mists_armed_harness175\build_and_install176.py"
R = [('assert script_txt.count("\\t\\tstart_armed = true,\\n") == 8,',
      'assert script_txt.count("\\t\\tstart_armed = true,\\n") == 9,', 1)]
ANCHOR = 'print("ROUND 175 GATE OK: Master of Mists fires before range, else under the shooting missile units")\n'
ADD = ANCHOR + r'''# ROUND 176: Master of Mists starts armed (user, 2026-11-18: "Start it on A").
assert ('"wh3_dlc27_character_abilities_master_of_mists_custom" },\n\t\tally_range_real = 250,\n'
        '\t\tstart_armed = true,\n\t\tox = 0, oy = 0 },') in script_txt, \
    "BUILD REFUSED (round 176): Master of Mists does not start armed"
print("ROUND 176 GATE OK: Master of Mists starts armed")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:70], src.count(a))
    src = src.replace(a, b)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
