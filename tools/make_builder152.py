#!/usr/bin/env python3
"""Build the round-152 build script from the round-151 one.

Gates rebased: the round-151 gate named blob_large_hold (removed: no whole-map hold) - it now names blob_not_flying; the
default-armed family set gains 'tired'. Adds one gate: no hold, fliers skipped, 90 degrees for every central attack,
the ALL badge's on-screen spot."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round151_large_defaults as R151  # noqa: E402

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261114_large_defaults_harness150\build_and_install151.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_no_hold_harness151\build_and_install152.py"
OLD_SET = repr(sorted(R151.DEFAULT_ON))
NEW_SET = repr(sorted(R151.DEFAULT_ON + ["tired"]))
ANCHOR = 'print("ROUND 151 GATE OK: large first + hold, usage rules, breath band 0.8, 27 default-armed families, ALL badge; tables match")\n'
ADD = ANCHOR + r'''# ROUND 152: no whole-map hold, fliers skipped, 90 degrees for every central attack, 'tired' armed, the ALL spot.
assert "blob_large_hold" not in script_txt, "the whole-map hold is still in the mod"
assert "and FOURTH.blob_not_flying(e.unit) then" in script_txt, "large first does not skip flying targets"
assert "if shot ~= nil and (shot[5] == 1 or shot[6] == 1) then" in script_txt, "the 90-degree rule is not on every central attack"
assert "FOURTH.ALL_OX, FOURTH.ALL_OY = -880, 8" in script_txt and "st.badge:SetDockOffset(FOURTH.ALL_OX, FOURTH.ALL_OY)" in script_txt, \
    "the ALL badge is not at the user's spot"
print("ROUND 152 GATE OK: no hold, fliers skipped, 90 degrees for 53 central attacks, tired armed, ALL badge on screen")
'''
RULES = [
    ('"function FOURTH.blob_pick_large(unit, m, r, key)", "function FOURTH.blob_large_hold(m, key, inf_value)",',
     '"function FOURTH.blob_pick_large(unit, m, r, key)", "function FOURTH.blob_not_flying(u)",', 1),
    (OLD_SET, NEW_SET, 1),
    ('print("ROUND 151 GATE OK: large first + hold, usage rules, breath band 0.8, 27 default-armed families, ALL badge; tables match")',
     'print("ROUND 151 GATE OK: large first, usage rules, breath band 0.8, 28 default-armed families (round 152), ALL badge; tables match")', 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a[:60], src.count(a))
    src = src.replace(a, b)
src = src.replace("20261114_large_defaults_harness150", "20261115_no_hold_harness151")
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
