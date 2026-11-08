#!/usr/bin/env python3
"""Build the round-133 build script from the round-132 one.

Gate rebased: melee_unwavering 349 -> 342 (the 7 R5 abilities move to under_fire / melee_or_under_fire).
Adds one gate: the round-133 triggers are wired."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261108_audit1_patch905_harness131\build_and_install132.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261108_under_fire_harness132\build_and_install133.py"

ANCHOR = 'print("ROUND 132 GATE OK: 13 entries on the new shooting-aware triggers; patch 9.0.5 data in")\n'
ADD = ANCHOR + '''# ROUND 133: audit batch 2, protection against shots fires when under fire.
assert "under_fire = FOURTH.evaluate_under_fire," in script_txt \\
    and "melee_or_under_fire = FOURTH.evaluate_melee_or_under_fire," in script_txt \\
    and script_txt.count('trigger = "under_fire"') == 3 \\
    and script_txt.count('trigger = "melee_or_under_fire"') == 4, \\
    "the round-133 triggers are missing"
print("ROUND 133 GATE OK: 3 on under_fire, 4 on melee_or_under_fire")
'''
OLD = "script_txt.count('trigger = \"melee_unwavering\"') == 349"
NEW = "script_txt.count('trigger = \"melee_unwavering\"') == 342"
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
n = src.count(OLD)
assert n == 4, n
src = src.replace(OLD, NEW)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("rebased %d melee_unwavering gates; wrote %s" % (n, DST))
