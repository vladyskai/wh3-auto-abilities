#!/usr/bin/env python3
"""Build the round-135 build script from the round-134 one.

Gates rebased: enemy_melee 3 -> 14, enemy_engaged_or_shot 85 -> 70 (3 gates).
Adds two gates: the round-135 triggers and filters are wired (enemy_melee 14, enemy_fast_near_ally 4,
enemy_engaged_or_shot 70, 15 target classes, the user's 5 m/s and 40 m), and BUILD REFUSED when the
embedded large / single-entity tables differ from the game data (tools/gen_unit_size_keys.py)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_speed_triggers_harness133\build_and_install134.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_enemy_slows_harness134\build_and_install135.py"

ANCHOR = 'print("ROUND 134 GATE OK: 5 on charge_only, 36 on charge_or_melee, Thunderburner gone")\n'
ADD = ANCHOR + r'''# ROUND 135: audit batch 4, the enemy slows, the fast-enemy trigger and the target filters.
assert "enemy_fast_near_ally = FOURTH.evaluate_enemy_fast_near_ally," in script_txt \
    and script_txt.count('trigger = "enemy_melee"') == 14 \
    and script_txt.count('trigger = "enemy_fast_near_ally"') == 4 \
    and script_txt.count('trigger = "enemy_engaged_or_shot"') == 70 \
    and script_txt.count("\t\ttarget_class = ") == 15 \
    and "FOURTH.FAST_ENEMY_MPS = 5 " in script_txt and "FOURTH.FAST_ENEMY_NEAR_M = 40 " in script_txt \
    and "\t\t\tor not FOURTH.eg_class_ok(enemy) then\n" in script_txt, \
    "the round-135 triggers or filters are missing"
import sys as _sys135
_sys135.path.insert(0, r"C:\Users\vlady\Desktop\WH3_mod\tools")
import gen_unit_size_keys as _g135
_l135, _s135 = _g135.derive()
assert _g135.lua_block(_l135, _s135) in script_txt, \
    "BUILD REFUSED (round 135): the large / single-entity tables differ from the game data"
print("ROUND 135 GATE OK: enemy_melee 14, enemy_fast_near_ally 4, 15 target classes; size tables match the game (%d large, %d single)" % (len(_l135), len(_s135)))
'''
RULES = [
    ("script_txt.count('trigger = \"enemy_engaged_or_shot\"') == 85", "script_txt.count('trigger = \"enemy_engaged_or_shot\"') == 70"),
    ("assert script_txt.count('trigger = \"enemy_melee\"') == 3, \"enemy_melee is not 3 entries\"",
     "assert script_txt.count('trigger = \"enemy_melee\"') == 14, \"enemy_melee is not 14 entries\""),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b in RULES:
    n = src.count(a)
    assert n >= 1, (a, n)
    print('rebased %d x: %s' % (n, a[:60]))
    src = src.replace(a, b)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
