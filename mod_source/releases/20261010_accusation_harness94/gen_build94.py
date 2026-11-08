# -*- coding: utf-8 -*-
"""Generate build_and_install94.py from the shipped build_and_install93.py.

Changes: the v94 docstring note; the moved trigger-count pin (melee_unwavering
481 -> 480); and a block of round-94 content asserts (the enemy evaluator,
the wiring, Accusation's move, the range constant, the reason strings, the
lapse skip, the one-time unreadable notice, the enemy enumerator, the
fresh-caster helper). The build/pack/install machinery is unchanged.
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, "build_basis93.py"), encoding="utf-8", newline="").read()


def sub(old, new, label, count=1):
    global src
    n = src.count(old)
    assert n == count, "%s: %d matches (want %d)" % (label, n, count)
    src = src.replace(old, new, count)
    print("patch %s: applied" % label)


sub('sentence is REMOVED from the shipped twui.xml.\n"""',
    'sentence is REMOVED from the shipped twui.xml.\n'
    '\n'
    'ROUND v94: ACCUSATION\'S automatic activation - a new reusable evaluator\n'
    "`enemy_engaged_or_shot` fires when an enemy unit in range is in melee OR\n"
    'under missile fire; the chosen enemy is the CAST TARGET (never the owner),\n'
    'cast via the round-4-proven bench_fresh fresh-handle route. Accusation moves\n'
    'from melee_unwavering (481 -> 480) to the new trigger; the table stays\n'
    '579 entries / 605 keys.\n"""',
    "docstring")

sub('assert script_txt.count(\'trigger = "melee_unwavering"\') == 481, \\\n'
    '    "the melee_unwavering entry count is not 481"',
    'assert script_txt.count(\'trigger = "melee_unwavering"\') == 480, \\\n'
    '    "the melee_unwavering entry count is not 480 (Accusation moved to enemy_engaged_or_shot)"',
    "pin 481->480")

NEW94 = '''assert _nk92 == 6, "the final-roster key count is not 6 (got %d)" % _nk92

# ---------------------------------------------------------------------------
# ROUND v94: ACCUSATION'S ENEMY-TARGETED TRIGGER (enemy_engaged_or_shot).
# ---------------------------------------------------------------------------
assert 'function FOURTH.evaluate_enemy_engaged_or_shot(unit, routing)' in script_txt, \\
    "the enemy-targeted evaluator is missing"
assert 'enemy_engaged_or_shot = FOURTH.evaluate_enemy_engaged_or_shot,' in script_txt, \\
    "the enemy trigger map entry is missing"
assert 'marker = "accusation", name = "Accusation", trigger = "enemy_engaged_or_shot"' in script_txt, \\
    "Accusation does not ride the new trigger"
assert 'enemy_engaged_or_shot = "When armed, fires when an enemy unit in range is in melee or under missile fire",' in script_txt, \\
    "the accusation tooltip wording is missing"
assert 'FOURTH.ACCUSATION_RANGE_M = 75' in script_txt, "the accusation range constant is missing"
assert 'bm:get_scriptunits_for_main_enemy_army_to_local_player()' in script_txt, \\
    "the enemy army enumerator read is missing"
assert 'function FOURTH.eg_fresh_caster_su(unit)' in script_txt, \\
    "the proven fresh-caster re-fetch helper is missing"
assert 'enemy:is_under_missile_attack()' in script_txt, "the enemy missile-read is missing"
assert 'reason = "enemy in melee (targeting " .. etype .. ")"' in script_txt, \\
    "the in-melee arm reason is missing"
assert 'reason = "enemy under missile fire (targeting " .. etype .. ")"' in script_txt, \\
    "the under-fire arm reason is missing"
assert 'accusation SKIPPED: the chosen enemy lapsed before the cast' in script_txt, \\
    "the accusation pre-cast lapse skip is missing"
assert 'accusation: enemy is_under_missile_attack read UNAVAILABLE' in script_txt, \\
    "the one-time unreadable-missile notice is missing"
assert 'accusation target: ' in script_txt, "the chosen-target line is missing"
assert script_txt.count('trigger = "enemy_engaged_or_shot"') == 1, \\
    "the enemy trigger count is not 1"
assert script_txt.count('trigger = "melee_unwavering"') == 480, \\
    "the melee_unwavering count is not 480"
assert script_txt.count("FOURTH.eg_enemy = nil") == 3, "the eg_enemy clears are not exactly three"
assert script_txt.count("FOURTH.eg_caster_su = nil") == 2, "the eg_caster_su clears are not exactly two"
assert script_txt.count("FOURTH.cast_target = unit") == 2, "the self-cast writes are not exactly two"
assert "is_firing" not in script_txt and "is_shooting" not in script_txt, \\
    "an invented firing predicate is in the mod"
assert script_txt.count("\\t{ marker = ") == 579, "the abilities table is not 579 entries"

# HOUSEKEEPING 20261004:'''

sub('assert _nk92 == 6, "the final-roster key count is not 6 (got %d)" % _nk92\n\n# HOUSEKEEPING 20261004:',
    NEW94, "round-94 asserts")

io.open(os.path.join(HERE, "build_and_install94.py"), "w", encoding="utf-8", newline="").write(src)
print("wrote build_and_install94.py", len(src), "bytes")
