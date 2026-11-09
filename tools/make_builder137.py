#!/usr/bin/env python3
"""Build the round-137 build script from the round-136 one.

Gates rebased: melee_unwavering 328 -> 314 (4 gates), wavering_ally_range 1 -> 6, ally_range_real fields 46 -> 51.
Adds one gate: the round-137 morale triggers are wired."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_melee_hexes_harness135\build_and_install136.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_morale_harness136\build_and_install137.py"

ANCHOR = 'print("ROUND 136 GATE OK: enemy_melee 34, enemy_fast_near_ally 7, enemy_engaged_or_shot 47, 16 target classes")\n'
ADD = ANCHOR + r'''# ROUND 137: audit batch 6, morale abilities fire when morale is in danger.
assert "wavering_aura = FOURTH.evaluate_wavering_aura," in script_txt \
    and script_txt.count('trigger = "wavering_aura"') == 9 \
    and "function FOURTH.wavering_ally_in_aura(unit)" in script_txt, \
    "the round-137 wavering_aura trigger is missing"
print("ROUND 137 GATE OK: 9 on wavering_aura, 6 on wavering_ally_range, melee_unwavering 314")
'''
RULES = [
    ("script_txt.count('trigger = \"melee_unwavering\"') == 328", "script_txt.count('trigger = \"melee_unwavering\"') == 314", 4),
    ("script_txt.count('trigger = \"wavering_ally_range\"') == 1, \"the wavering_ally_range entry count is not 1\"",
     "script_txt.count('trigger = \"wavering_ally_range\"') == 6, \"the wavering_ally_range entry count is not 6\"", 1),
    ('script_txt.count("\\t\\tally_range_real = ") == 46', 'script_txt.count("\\t\\tally_range_real = ") == 51', 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a, src.count(a))
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:70]))
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
