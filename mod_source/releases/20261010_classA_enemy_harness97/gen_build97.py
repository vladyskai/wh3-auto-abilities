# -*- coding: utf-8 -*-
"""Generate build_and_install97.py from the shipped build_and_install96.py.

Changes: the v97 docstring note; RE-BASED v96 asserts (the trigger counts and the
marker-prefixed log tokens); and a new block asserting THE REST OF CLASS A (the
12 named 70% constants, the FOURTH.ENEMY_CAST map, the 98 range_real fields, the
load-loop wiring, the shared picker, the enemy-ground evaluator/helper/key-set,
the moved trigger counts, and that unit_in_range( is still GONE). The build/pack/
install machinery is unchanged.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
H96 = "C:/Users/vlady/Desktop/WH3_mod/mod_source/releases/20261010_accusation_offer_harness96"
NL = chr(10)

src = io.open(H96 + "/build_and_install96.py", encoding="utf-8", newline="").read()


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


# --- docstring -----------------------------------------------------------------
DA = "choice and the pre-cast re-check." + NL + '"""'
DN = ("choice and the pre-cast re-check." + NL + NL
      + "ROUND v97: THE REST OF CLASS A. 97 of the 98 enemy-aimed entries from the" + NL
      + "audit (Accusation 263 already done) now fire at the ENEMY: 88 ride the" + NL
      + "existing enemy_engaged_or_shot trigger and 9 ride the new enemy_ground_area" + NL
      + "trigger (perform_special_ability_ground on the chosen ENEMY's ground). Each" + NL
      + "entry carries its own REAL target_intercept_range (range_real) mapped at load" + NL
      + "to ONE named 70% constant per real range (12 constants, floor(real*0.70)); the" + NL
      + "offer test is unit:unit_distance(enemy) <= that constant ONLY - never the" + NL
      + "engine's unit_in_range. melee_unwavering 480 -> 383." + NL + '"""')
sub(DA, DN, "docstring")

# --- RE-BASE the v96 trigger-count asserts ------------------------------------
sub('assert script_txt.count(\'trigger = "enemy_engaged_or_shot"\') == 1, \\\n'
    '    "the enemy trigger count is not 1"',
    'assert script_txt.count(\'trigger = "enemy_engaged_or_shot"\') == 89, \\\n'
    '    "the enemy trigger count is not 89"',
    "v96 enemy count")
sub('assert script_txt.count(\'trigger = "melee_unwavering"\') == 480, \\\n'
    '    "the melee_unwavering count is not 480"',
    'assert script_txt.count(\'trigger = "melee_unwavering"\') == 383, \\\n'
    '    "the melee_unwavering count is not 383"',
    "v96 melee count")

sub('assert script_txt.count(\'trigger = "melee_unwavering"\') == 480, \\\n'
    '    "the melee_unwavering entry count is not 480 (Accusation moved to enemy_engaged_or_shot)"',
    'assert script_txt.count(\'trigger = "melee_unwavering"\') == 383, \\\n'
    '    "the melee_unwavering entry count is not 383 (97 Class-A entries moved to the enemy triggers)"',
    "v90 melee count")

# --- RE-BASE the v96 marker-prefixed log tokens -------------------------------
sub("assert 'accusation SKIPPED: the chosen enemy lapsed before the cast' in script_txt, \\",
    "assert ' SKIPPED: the chosen enemy lapsed before the cast' in script_txt, \\",
    "v96 lapse token")
sub('assert \'accusation target: \' in script_txt, "the chosen-target line is missing"',
    'assert \'target: \\\'\' in script_txt, "the chosen-target line is missing"',
    "v96 target token")
sub('assert \'.. "m bound=" .. tostring(FOURTH.ACCUSATION_RANGE_M) .. "m")\' in script_txt, \\\n'
    '    "the target-choice log does not print the bound"',
    'assert \'.. "m bound=" .. tostring(bound) .. "m")\' in script_txt, \\\n'
    '    "the target-choice log does not print the bound"',
    "v96 bound token")

# --- the v97 gates (inserted just before the is_firing assert) ----------------
ANCHOR = ('assert "is_firing" not in script_txt and "is_shooting" not in script_txt, \\' + NL
          + '    "an invented firing predicate is in the mod"')
CONSTS = (("FOURTH.ENEMY_CAST_R15  = 10", 15, 10), ("FOURTH.ENEMY_CAST_R20  = 14", 20, 14),
          ("FOURTH.ENEMY_CAST_R30  = 21", 30, 21), ("FOURTH.ENEMY_CAST_R35  = 24", 35, 24),
          ("FOURTH.ENEMY_CAST_R50  = 35", 50, 35), ("FOURTH.ENEMY_CAST_R70  = 49", 70, 49),
          ("FOURTH.ENEMY_CAST_R75  = 52", 75, 52), ("FOURTH.ENEMY_CAST_R100 = 70", 100, 70),
          ("FOURTH.ENEMY_CAST_R150 = 105", 150, 105), ("FOURTH.ENEMY_CAST_R180 = 126", 180, 126),
          ("FOURTH.ENEMY_CAST_R200 = 140", 200, 140), ("FOURTH.ENEMY_CAST_R500 = 350", 500, 350))
G = [NL, "# ROUND v97: THE REST OF CLASS A (nothing above is loosened). The 12 named 70%",
     "# enemy-cast constants, the real->bound map, the 98 range_real fields, the load-loop",
     "# wiring, the shared picker and the enemy-ground evaluator/helper/key-set.",
     'assert "FOURTH.ENEMY_CAST = {" in script_txt, "the real->bound map is missing"',
     'assert "ability.range_m = FOURTH.ENEMY_CAST[ability.range_real]" in script_txt, \\',
     '    "the load-loop real->bound mapping is missing"',
     'assert script_txt.count("\\t\\trange_real = ") == 98, "the range_real fields are not 98"',
     'assert "function FOURTH.eg_pick_enemy(unit, routing, ground)" in script_txt, \\',
     '    "the shared enemy picker is missing"',
     'assert "local bound = FOURTH.eg_range_m" in script_txt and "return gap <= bound" in script_txt, \\',
     '    "the per-ability bound is not read"',
     'assert "function FOURTH.evaluate_enemy_ground_area(unit, routing)" in script_txt, \\',
     '    "the enemy-ground evaluator is missing"',
     'assert "enemy_ground_area = FOURTH.evaluate_enemy_ground_area," in script_txt, \\',
     '    "the enemy-ground trigger is not wired"',
     'assert "function FOURTH.enemy_ground_cast(uc, enemy, ability_key)" in script_txt, \\',
     '    "the enemy-ground cast helper is missing"',
     'assert "enemy_ground_keys = {" in script_txt, "the enemy-ground key set is missing"',
     'assert "FOURTH.eg_range_m = ability.range_m" in script_txt and \\',
     '    "FOURTH.eg_marker = ability.marker" in script_txt, \\',
     '    "the poll does not set the current ability bound/marker"',
     'assert script_txt.count(\'trigger = "enemy_ground_area"\') == 9, "the enemy-ground trigger count is not 9"',
     'assert "unit_in_range(" not in script_txt, "the engine unit_in_range call is back"']
for tok, real, want in CONSTS:
    assert int(real * 0.70 + 1e-9) == want, "the documented 70% target is wrong for " + tok
    G.append('assert "%s" in script_txt, "the 70%% enemy-cast constant is missing: %s"' % (tok, tok))
for _k in ("wh2_dlc09_item_abilities_amulet_of_phastah",
           "wh_dlc03_item_abilities_chalice_of_dark_rain",
           "wh2_dlc09_character_abilities_curse_of_khsar",
           "wh2_dlc10_character_abilities_entangle",
           "wh3_dlc25_character_abilities_get_em",
           "wh2_dlc13_lord_abilities_hunters_snare",
           "wh2_dlc13_lord_abilities_hunters_trap",
           "wh2_main_item_abilities_the_tricksters_pendant",
           "wh_main_item_abilities_tricksters_shard"):
    G.append('assert \'["%s"] = true,\' in script_txt, "enemy-ground key missing: %s"' % (_k, _k))
GATES = NL.join(G)
sub(ANCHOR, GATES + NL + ANCHOR, "v97 gates")

io.open(HERE + "/build_and_install97.py", "w", encoding="utf-8", newline="").write(src)
print("wrote build_and_install97.py", len(src), "bytes")
