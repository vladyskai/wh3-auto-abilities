#!/usr/bin/env python3
"""Build the round-175 build script from the round-174 one (Master of Mists: before range, else shooting).
No count moves. ROUND 175 GATE: the shooting arm is reached from the before-range evaluator, its re-check, the 35 m area
at the 70% rule, the card sentence."""

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_review_rows_harness173\build_and_install174.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261118_master_of_mists_harness174\build_and_install175.py"
ANCHOR = 'print("ROUND 174 COMPILE GATE OK: the script compiles")\n'
ADD = ANCHOR + r'''# ROUND 175: Master of Mists, 'A: before range, else shooting' (user ruling 2026-11-18).
assert "\tif best == nil then return FOURTH.mist_shooting(unit) end   -- ROUND 175: else the shooting units\n" in script_txt, \
    "BUILD REFUSED (round 175): the shooting arm is not reached"
assert 'if FOURTH.ah_mode == "mist_shoot" then   -- ROUND 175: still shooting' in script_txt, \
    "BUILD REFUSED (round 175): the shooting arm is not re-checked before the cast"
assert "FOURTH.MIST_AREA_REAL_M = 35 " in script_txt and \
    "FOURTH.MIST_AREA_M = math.floor(FOURTH.MIST_AREA_REAL_M * 0.70)" in script_txt, \
    "BUILD REFUSED (round 175): the 70% rule is broken for the Master of Mists area"
assert '\tground_ally_before_range = "Fires under missile allies just before their enemy is in range, else while they shoot",' \
    in script_txt, "BUILD REFUSED (round 175): the card sentence differs"
print("ROUND 175 GATE OK: Master of Mists fires before range, else under the shooting missile units")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
