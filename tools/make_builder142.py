#!/usr/bin/env python3
"""Build the round-142 build script from the round-141 one.

Gates rebased: entries 698 -> 703 (11 gates); the round-140 gate: Blooood! rides self_moving since round 142.
Adds one gate: the 5 new entries, the 250 m bound (floor(250 x 0.70) = 175) and the four new families are wired."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_recharge_reducers_harness140\build_and_install141.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_open_batch1_harness141\build_and_install142.py"
ANCHOR = 'print("ROUND 141 GATE OK: casts remembered; 5 + 1 + 1 + 1 reducers on their families; the lock table matches the game")\n'
ADD = ANCHOR + r'''# ROUND 142: open batch 1 (shooting buffs and ammo refills) and Blooood! when moving.
for _m in ("more_powder", "restock_gunnery_school", "master_of_mists", "of_warp_and_ruin", "ominous_powder"):
    assert '{ marker = "%s", name = ' % _m in script_txt, "round-142 entry missing: " + _m
assert "FOURTH.ALLY_CAST_R250 = 175" in script_txt and int(250 * 0.70 + 1e-9) == 175 \
    and "[250] = FOURTH.ALLY_CAST_R250," in script_txt, "the 250 m bound breaks the 70% rule"
assert "ground_ally_before_range = FOURTH.evaluate_ground_ally_before_range," in script_txt \
    and "self_shooting_clear = FOURTH.evaluate_self_shooting_clear," in script_txt \
    and "self_shooting_healthy = FOURTH.evaluate_self_shooting_healthy," in script_txt \
    and "self_moving = FOURTH.evaluate_self_moving," in script_txt \
    and 'name = "Blooood!", trigger = "self_moving",' in script_txt, \
    "the round-142 families are missing"
print("ROUND 142 GATE OK: 5 new entries / 6 keys; 250 m -> 175 m; Blooood! on self_moving")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 698, "the abilities table is not 698 entries"',
     'script_txt.count("\\t{ marker = ") == 703, "the abilities table is not 703 entries"', 11),
    ("    and 'name = \"Blooood!\", trigger = \"self_running\",' in script_txt \\\n",
     "    and 'name = \"Blooood!\", trigger = \"self_moving\",' in script_txt \\\n", 1),
    ('script_txt.count("\\t\\tally_range_real = ") == 53', 'script_txt.count("\\t\\tally_range_real = ") == 56', 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a[:60], src.count(a))
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:60]))
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
