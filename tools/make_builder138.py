#!/usr/bin/env python3
"""Build the round-138 build script from the round-137 one.

Gates rebased: enemy_engaged_or_shot 47 -> 46 (4 gates), target classes 16 -> 21.
Adds one gate: the round-138 classes and Missile Mirror's trigger are wired, and BUILD REFUSED when the embedded
undead table differs from the game data (tools/gen_undead_keys.py)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_morale_harness136\build_and_install137.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_rare_filters_harness137\build_and_install138.py"

ANCHOR = 'print("ROUND 137 GATE OK: 9 on wavering_aura, 6 on wavering_ally_range, melee_unwavering 314")\n'
ADD = ANCHOR + r'''# ROUND 138: the rarer target filters and Missile Mirror's shooting trigger.
assert 'if cls == "not_undead" then' in script_txt and 'if cls == "missile" then' in script_txt \
    and "enemy_missile_shooting = FOURTH.evaluate_enemy_missile_shooting," in script_txt \
    and script_txt.count('trigger = "enemy_missile_shooting"') == 1, \
    "the round-138 classes or the Missile Mirror trigger are missing"
import gen_undead_keys as _g138
assert _g138.lua_block(_g138.derive()) in script_txt, \
    "BUILD REFUSED (round 138): the undead table differs from the game data"
print("ROUND 138 GATE OK: 21 target classes, enemy_missile_shooting 1, the undead table matches the game")
'''
RULES = [
    ("script_txt.count('trigger = \"enemy_engaged_or_shot\"') == 47", "script_txt.count('trigger = \"enemy_engaged_or_shot\"') == 46", 4),
    ('script_txt.count("\\t\\ttarget_class = ") == 16', 'script_txt.count("\\t\\ttarget_class = ") == 21', 1),
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
