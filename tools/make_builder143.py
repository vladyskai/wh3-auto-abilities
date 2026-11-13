#!/usr/bin/env python3
"""Build the round-143 build script from the round-142 one.

Gates rebased: entries 703 -> 712 (11 gates); melee_unwavering 306 -> 307; range_real fields 207 -> 215;
enemy_ground_melee 67 -> 74; target classes 21 -> 24; enemy_ground_keys 115 -> 125.
Adds one gate: the 9 new entries, the 25 m bound (floor(25 x 0.70) = 17) and the new family are wired, and every
batch-2 ground key sits in enemy_ground_keys."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch1_harness141\build_and_install142.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch2_harness142\build_and_install143.py"
ANCHOR = 'print("ROUND 142 GATE OK: 5 new entries / 6 keys; 250 m -> 175 m; Blooood! on self_moving")\n'
ADD = ANCHOR + r'''# ROUND 143: open batch 2 (ground curses, Curse of Djaf, Soulblight, Squig Thinkin', the fanatic releases).
for _m in ("curse_of_anraheir", "transmutation_of_lead", "soulblight", "the_soulstealer", "curse_of_djaf",
           "soulblight_handmaidens", "squig_thinkin", "spinning_loons", "loons_of_eight_peaks"):
    assert '{ marker = "%s", name = ' % _m in script_txt, "round-143 entry missing: " + _m
assert "FOURTH.ENEMY_CAST_R25  = 17" in script_txt and int(25 * 0.70 + 1e-9) == 17 \
    and "\t[25]  = FOURTH.ENEMY_CAST_R25," in script_txt, "the 25 m bound breaks the 70% rule"
assert "enemy_ground_shooting = FOURTH.evaluate_enemy_ground_shooting," in script_txt \
    and "function FOURTH.evaluate_enemy_ground_shooting(unit, routing)" in script_txt, \
    "the round-143 family is missing"
_g0 = script_txt.find("enemy_ground_keys = {")
_g1 = script_txt.find("\t},\n", _g0)
for _k in ("wh2_dlc16_spell_bound_the_curse_of_anraheir", "wh3_main_spell_bound_the_curse_of_anraheir",
           "wh_dlc05_spell_bound_the_curse_of_anraheir", "wh3_main_spell_bound_transmutation_of_lead",
           "wh2_dlc10_spell_bound_soulblight", "wh3_dlc29_spell_bound_undeath_khizaar_the_soulstealer",
           "wh2_dlc09_character_abilities_curse_of_djaf", "wh3_dlc26_character_abilities_squig_thinkin",
           "wh_main_unit_abilities_spinning_loons", "wh_dlc06_unit_abilities_the_loons_of_eight_peaks"):
    assert ('["%s"] = true,' % _k) in script_txt[_g0:_g1], "round-143 key not in enemy_ground_keys: " + _k
assert '["wh3_dlc29_spell_bound_soulblight"] = true,' not in script_txt[_g0:_g1], \
    "the Handmaidens' Soulblight is a self buff, never an enemy-ground key"
print("ROUND 143 GATE OK: 9 new entries / 11 keys; 25 m -> 17 m; enemy_ground_shooting wired")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 703, "the abilities table is not 703 entries"',
     'script_txt.count("\\t{ marker = ") == 712, "the abilities table is not 712 entries"', 11),
    ("count('trigger = \"melee_unwavering\"') == 306", "count('trigger = \"melee_unwavering\"') == 307", 4),
    ('count("\\t\\trange_real = ") == 207', 'count("\\t\\trange_real = ") == 215', 2),
    ("count('trigger = \"enemy_ground_melee\"') == 67", "count('trigger = \"enemy_ground_melee\"') == 74", 1),
    ('script_txt.count("\\t\\ttarget_class = ") == 21', 'script_txt.count("\\t\\ttarget_class = ") == 24', 1),
    ("count('\"] = true,') == 115, \"enemy_ground_keys is not 115 entries",
     "count('\"] = true,') == 125, \"enemy_ground_keys is not 125 entries", 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a[:60], src.count(a))
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:60]))
src = src.replace("20261113_open_batch1_harness141", "20261113_open_batch2_harness142")
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
