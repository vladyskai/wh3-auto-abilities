#!/usr/bin/env python3
"""Build the round-144 build script from the round-143 one.

Gates rebased: entries 712 -> 722 (11 gates); melee_unwavering 307 -> 309 (4); range_real fields 215 -> 217 (2);
ally_range_real 56 -> 57; under_fire 3 -> 4; enemy_fast_near_ally 7 -> 8.
Adds one gate: the 10 new entries, the five new families, both new re-check modes, the 10% line, and the three skipped
abilities (two stances, one stealth item) are NOT in the mod."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch2_harness142\build_and_install143.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch3_harness143\build_and_install144.py"
ANCHOR = 'print("ROUND 143 GATE OK: 9 new entries / 11 keys; 25 m -> 17 m; enemy_ground_shooting wired")\n'
ADD = ANCHOR + r'''# ROUND 144: open batch 3 (the rest of group C).
for _m in ("hags_denial", "ruinshelter", "rock_bottom", "morikhane", "hunters_call", "icon_of_the_king",
           "the_gold_standard", "banner_of_hellfire", "ghostly_howl", "petrifying_gaze"):
    assert '{ marker = "%s", name = ' % _m in script_txt, "round-144 entry missing: " + _m
for _f in ("self_last_stand", "self_out_of_ammo", "health_aura_self_undead", "ally_hurt_melee", "enemy_wavering"):
    assert ("%s = FOURTH.evaluate_%s," % (_f, _f)) in script_txt, "round-144 family not wired: " + _f
assert "FOURTH.LAST_STAND_PCT = 10" in script_txt, "Hag's Denial: the user's 10% line is missing"
assert 'elseif eg_mode_now == "wavering" then' in script_txt and 'if FOURTH.ah_mode == "melee" then' in script_txt \
    and 'if FOURTH.ah_mode == "undead" then' in script_txt, "a round-144 pre-cast re-check mode is missing"
for _k in ("wh_dlc05_unit_abilities_storm_of_blades", "wh2_dlc16_unit_abilities_whirling_death",
           "wh2_dlc09_item_abilities_cloak_of_the_dunes"):
    assert _k not in script_txt, "a skipped ability (stance / stealth) is in the mod: " + _k
print("ROUND 144 GATE OK: 10 new entries / 10 keys; 5 new families; 3 skipped abilities absent")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 712, "the abilities table is not 712 entries"',
     'script_txt.count("\\t{ marker = ") == 722, "the abilities table is not 722 entries"', 11),
    ("count('trigger = \"melee_unwavering\"') == 307", "count('trigger = \"melee_unwavering\"') == 309", 4),
    ('count("\\t\\trange_real = ") == 215', 'count("\\t\\trange_real = ") == 217', 2),
    ('count("\\t\\tally_range_real = ") == 56', 'count("\\t\\tally_range_real = ") == 57', 1),
    ("count('trigger = \"under_fire\"') == 3", "count('trigger = \"under_fire\"') == 4", 1),
    ("count('trigger = \"enemy_fast_near_ally\"') == 7", "count('trigger = \"enemy_fast_near_ally\"') == 8", 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a[:60], src.count(a))
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:60]))
src = src.replace("20261113_open_batch2_harness142", "20261113_open_batch3_harness143")
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
