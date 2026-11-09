#!/usr/bin/env python3
"""Build the round-136 build script from the round-135 one (which already carries the 2026-11-09 order fix:
the installed pack is only overwritten after every gate).

Gates rebased: enemy_engaged_or_shot 70 -> 47 (4 gates), enemy_melee 14 -> 34 (2), enemy_fast_near_ally 4 -> 7,
target classes 15 -> 16. Adds one gate: the round-136 moves and Spearfisher's Net's not_flying class."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_enemy_slows_harness134\build_and_install135.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_melee_hexes_harness135\build_and_install136.py"

ANCHOR = 'print("ROUND 135 GATE OK: enemy_melee 14, enemy_fast_near_ally 4, 15 target classes; size tables match the game (%d large, %d single)" % (len(_l135), len(_s135)))\n'
ADD = ANCHOR + r'''# ROUND 136: audit batch 5, the melee hexes leave the missile arm; the immobilisers on the fast-enemy trigger.
for _m in ("gaze_of_fate", "sadistic_snare", "spearfishers_net"):
    assert '{ marker = "%s", name = ' % _m in script_txt, "round-136 marker missing: " + _m
assert 'if cls == "not_flying" then' in script_txt and 'target_class = "not_flying"' in script_txt, \
    "Spearfisher's Net's not_flying class is missing"
print("ROUND 136 GATE OK: enemy_melee 34, enemy_fast_near_ally 7, enemy_engaged_or_shot 47, 16 target classes")
'''
RULES = [
    ("script_txt.count('trigger = \"enemy_engaged_or_shot\"') == 70", "script_txt.count('trigger = \"enemy_engaged_or_shot\"') == 47", 4),
    ("script_txt.count('trigger = \"enemy_melee\"') == 14", "script_txt.count('trigger = \"enemy_melee\"') == 34", 2),
    ('"enemy_melee is not 14 entries"', '"enemy_melee is not 34 entries"', 1),
    ("script_txt.count('trigger = \"enemy_fast_near_ally\"') == 4", "script_txt.count('trigger = \"enemy_fast_near_ally\"') == 7", 1),
    ('script_txt.count("\\t\\ttarget_class = ") == 15', 'script_txt.count("\\t\\ttarget_class = ") == 16', 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a, src.count(a))
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:70]))
assert "os.remove(GAME_PACK)" not in src and "for p in (OUT_PACK, GAME_PACK):" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
