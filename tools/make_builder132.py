#!/usr/bin/env python3
"""Build the round-132 build script from the round-131 one.

Gates rebased (the round deliberately moves them):
  melee_unwavering 354 -> 349, metallurgy_melee 8 -> 0 (the 8 keys move to melee_or_shooting_aura;
  the metallurgy evaluator stays as the melee arm), ally_range_real fields 44 -> 46.
Adds one gate: the round-132 triggers and the patch-9.0.5 data are in."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_shooting_triggers_harness130\build_and_install131.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261108_audit1_patch905_harness131\build_and_install132.py"

ANCHOR = 'print("ROUND 131 GATE OK: 8 firing auras, 3 new triggers, Farsight\'s 1.21 band, no stance left")\n'
ADD = ANCHOR + '''# ROUND 132: audit batch 1 and the patch-9.0.5 data.
assert "melee_or_shooting_aura = FOURTH.evaluate_melee_or_shooting_aura," in script_txt \\
    and "melee_or_shooting_self_or_ally = FOURTH.evaluate_melee_or_shooting_self_or_ally," in script_txt \\
    and "self_shooting = FOURTH.evaluate_self_shooting," in script_txt \\
    and script_txt.count('trigger = "melee_or_shooting_aura"') == 10 \\
    and script_txt.count('trigger = "melee_or_shooting_self_or_ally"') == 2 \\
    and script_txt.count('trigger = "self_shooting"') == 1, \\
    "the round-132 triggers are missing"
assert "range_real = 50,   -- patch 9.0.5: 100 -> 50 m" in script_txt \\
    and '["wh3_dlc29_weapon_abilities_aken_seth_the_staff_of_pain"] = 120,' in script_txt \\
    and '["wh3_dlc29_spell_bound_okkams_mindrazor"] = 1,' not in script_txt \\
    and 'if f == "overseer" then' in script_txt, \\
    "the patch-9.0.5 data fixes are missing"
# the 70%% rule: Gaze 50 m -> ENEMY_CAST_R50 = 35; Seerstaff / Harmonic 200 m -> ALLY_CAST_R200 = 140
assert "FOURTH.ENEMY_CAST_R50  = 35" in script_txt and "FOURTH.ALLY_CAST_R200 = 140" in script_txt
print("ROUND 132 GATE OK: 13 entries on the new shooting-aware triggers; patch 9.0.5 data in")
'''
RULES = [
    ("script_txt.count('trigger = \"melee_unwavering\"') == 354", "script_txt.count('trigger = \"melee_unwavering\"') == 349"),
    ("script_txt.count('trigger = \"metallurgy_melee\"') == 8", "script_txt.count('trigger = \"metallurgy_melee\"') == 0"),
    ('script_txt.count("\\t\\tally_range_real = ") == 44', 'script_txt.count("\\t\\tally_range_real = ") == 46'),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b in RULES:
    n = src.count(a)
    assert n >= 1, a
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:70]))
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
