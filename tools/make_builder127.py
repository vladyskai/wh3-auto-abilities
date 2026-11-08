#!/usr/bin/env python3
"""Build the round-127 build script from the round-126 one. No count pin moves.
Adds one gate: the OFF window is max(2 x reload, 20 s) with the old default gone,
and a disappeared target logs 'target lost'."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_firing_reload_table_harness125\build_and_install126.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_off_window_target_lost_harness126\build_and_install127.py"

ANCHOR = 'print("ROUND 126 GATE OK: " + _gen.stdout.strip())\n'
ADD = ANCHOR + '''# ROUND 127: OFF window max(2 x reload, 20 s); a disappeared target logs "target lost".
assert "FOURTH.AMMO_OFF_FACTOR = 2 " in script_txt and "FOURTH.AMMO_OFF_MIN_S = 20 " in script_txt \\
    and "AMMO_WINDOW_DEFAULT_S" not in script_txt, "the round-127 OFF window is missing"
assert "target lost (no current target)" in script_txt, "the target-lost fix is missing"
print("ROUND 127 GATE OK: OFF = max(2 x reload, 20 s); a lost target is logged, not formatted")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
