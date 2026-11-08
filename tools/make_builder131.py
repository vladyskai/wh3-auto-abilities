#!/usr/bin/env python3
"""Build the round-131 build script from the round-130 one.

Gates rebased (the round deliberately moves them):
  entries 709 -> 700 (the nine stances removed), melee_unwavering 373 -> 354,
  ally_range_real fields 42 -> 44 (Deranged Munitions, Entrenchment);
  the roster lists drop the nine stance rows: BLOCK789 66 -> 62 entries / 70 -> 66 keys,
  AUTO327 305 -> 302 / 320 -> 317, FINAL6 6 -> 4.
Adds one gate: the round-131 triggers are wired and no stance is left."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_firing_flag_triggers_harness129\build_and_install130.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_shooting_triggers_harness130\build_and_install131.py"

STANCES = ["master_predator", "immovable_bulwark", "unstoppable_choppas", "the_shadows_coil", "woven_mist",
           "chanson_of_caging", "the_dance_of_dreaming", "the_praise_of_slaanesh", "the_waltz_of_lethargy"]

ANCHOR = 'print("ROUND 130 GATE OK: Restock!, Ballistics Calibration and Skjalandir\'s Fall\'s shooting arm are wired")\n'
ADD = ANCHOR + '''# ROUND 131: the shooting buffs leave the melee trigger; the nine stances leave the mod.
assert "self_or_ally_shooting = FOURTH.evaluate_self_or_ally_shooting," in script_txt \\
    and "melee_or_self_or_ally_shooting = FOURTH.evaluate_melee_or_self_or_ally_shooting," in script_txt \\
    and "no_enemy_in_range_within_boost = FOURTH.evaluate_no_enemy_in_range_within_boost," in script_txt \\
    and "FOURTH.FIRING_AURA_MIN = 1 " in script_txt and "BALLISTICS_MIN_FIRING" not in script_txt \\
    and "FOURTH.FARSIGHT_BAND = 1 + FOURTH.FARSIGHT_BONUS * FOURTH.RANGE_FRACTION" in script_txt \\
    and script_txt.count('trigger = "allies_firing_aura"') == 8, \\
    "the round-131 triggers are missing"
for _st in %r:
    assert _st not in script_txt, "a stance is still automated: " + _st
# the 70%% rule on the new bounds: aura 55 m -> 38, 35 m -> 24 (computed at load);
# Deranged Munitions 100 m -> ALLY_CAST_R100 = 70; Entrenchment 150 m -> ALLY_CAST_R150 = 105
assert "FOURTH.ALLY_CAST_R150 = 105" in script_txt and int(55 * 0.70 + 1e-9) == 38 and int(35 * 0.70 + 1e-9) == 24
print("ROUND 131 GATE OK: 8 firing auras, 3 new triggers, Farsight's 1.21 band, no stance left")
''' % (STANCES,)

RULES = [
    ('script_txt.count("\\t{ marker = ") == 709, "the abilities table is not 709 entries"',
     'script_txt.count("\\t{ marker = ") == 700, "the abilities table is not 700 entries"'),
    ("script_txt.count('trigger = \"melee_unwavering\"') == 373", "script_txt.count('trigger = \"melee_unwavering\"') == 354"),
    ('script_txt.count("\\t\\tally_range_real = ") == 42', 'script_txt.count("\\t\\tally_range_real = ") == 44'),
    ('assert len(BLOCK789) == 66,', 'assert len(BLOCK789) == 62,'),
    ('assert _nk789 == 70,', 'assert _nk789 == 66,'),
    ('assert len(AUTO327) == 305,', 'assert len(AUTO327) == 302,'),
    ('assert _nk327 == 320,', 'assert _nk327 == 317,'),
    ('assert len(FINAL6) == 6,', 'assert len(FINAL6) == 4,'),
    ('assert _nk92 == 6,', 'assert _nk92 == 4,'),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
lines = src.split("\n")
kept, dropped = [], 0
for ln in lines:
    s = ln.strip()
    if s.startswith('("') and any(s.startswith('("%s",' % m) for m in STANCES):
        dropped += 1
        continue
    kept.append(ln)
assert dropped == 9, dropped
src = "\n".join(kept)
for a, b in RULES:
    n = src.count(a)
    assert n >= 1, a
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:70]))
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("dropped %d stance rows; wrote %s" % (dropped, DST))
