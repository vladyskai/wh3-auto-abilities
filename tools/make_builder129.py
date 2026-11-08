#!/usr/bin/env python3
"""Build the round-129 build script from the round-128 one. No count pin moves.
Adds one gate: the unit cards veto a ghost selection (no string.find)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_ready_on_screen_harness127\build_and_install128.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_card_veto_harness128\build_and_install129.py"

ANCHOR = 'print("ROUND 128 GATE OK: fix A (engine-selected unit, READY button) and the NOT FIRING snapshot are in")\n'
ADD = ANCHOR + '''# ROUND 129: the unit cards veto a ghost selection.
assert "FOURTH.CARD_UNSELECTED_STATES = { active = true, hover = true, inactive = true, taking_damage = true, wavering = true }" in script_txt \
    and "if st ~= nil and FOURTH.CARD_UNSELECTED_STATES[st] == true then" in script_txt \
    and "elseif (tick_count - since) >= FOURTH.CARD_DESELECT_CONFIRM_POLLS then" in script_txt, \
    "the round-129 card veto is missing"
print("ROUND 129 GATE OK: a unit whose card reads unselected for 2 polls leaves the selected set")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
