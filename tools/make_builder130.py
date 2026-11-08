#!/usr/bin/env python3
"""Build the round-130 build script from the round-129 one.

Count gates rebased (the round deliberately moves them):
  entries 707 -> 709 (Restock!, Ballistics Calibration),
  melee_unwavering 374 -> 373 (Skjalandir's Fall moves to melee_or_shooting_into_melee),
  ally_range_real fields 41 -> 42 (Restock!).
Adds one gate: the three firing-flag triggers are wired."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261103_card_veto_harness128\build_and_install129.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261101_firing_flag_triggers_harness129\build_and_install130.py"

ANCHOR = 'print("ROUND 129 GATE OK: a unit whose card reads unselected for 2 polls leaves the selected set")\n'
ADD = ANCHOR + '''# ROUND 130: the first triggers on the firing flag.
assert 'trigger = "ally_ammo_low"' in script_txt and 'trigger = "allies_firing_aura"' in script_txt \\
    and 'trigger = "melee_or_shooting_into_melee"' in script_txt \\
    and "ally_ammo_low = FOURTH.evaluate_ally_ammo_low," in script_txt \\
    and "allies_firing_aura = FOURTH.evaluate_allies_firing_aura," in script_txt \\
    and "melee_or_shooting_into_melee = FOURTH.evaluate_melee_or_shooting_into_melee," in script_txt \\
    and '["wh2_dlc17_hero_abilities_more_powder_generic"] = 60,' in script_txt \\
    and '["wh_main_hero_abilities_ballistics_calibration"] = true,' in script_txt \\
    and "FOURTH.ammo_by_id[tostring(u:unique_ui_id())] = st" in script_txt, \\
    "the round-130 firing-flag triggers are missing"
# the 70% rule on the two new ranges: Restock! 100 m -> 70 m (ALLY_CAST_R100),
# Ballistics Calibration's aura 55 m -> floor(55 * 0.70) = 38 m (computed at load)
assert "FOURTH.ALLY_CAST_R100 = 70" in script_txt and int(55 * 0.70 + 1e-9) == 38
print("ROUND 130 GATE OK: Restock!, Ballistics Calibration and Skjalandir's Fall's shooting arm are wired")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 707, "the abilities table is not 707 entries"',
     'script_txt.count("\\t{ marker = ") == 709, "the abilities table is not 709 entries"'),
    ("script_txt.count('trigger = \"melee_unwavering\"') == 374", "script_txt.count('trigger = \"melee_unwavering\"') == 373"),
    ('script_txt.count("\\t\\tally_range_real = ") == 41', 'script_txt.count("\\t\\tally_range_real = ") == 42'),
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
