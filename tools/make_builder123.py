#!/usr/bin/env python3
"""Build the round-123 build script from the round-122 one (the builder of the
installed round-122 pack).

Round 123 (the hex batch) moves these builder count pins with the table:
697 -> 707 entries, melee_unwavering 370 -> 374, charge_or_melee 25 -> 28,
range_real fields 204 -> 207. enemy_engaged_or_shot stays 85 (the upgraded
Hunter of Champions key joined an existing entry). Plus one new content gate:
the enemy_melee evaluator is present and wired. The round-121 army-bar gate,
the five-file identity checks and the probe refusal are carried over untouched.
"""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261027_melee_buffs_harness121\build_and_install122.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261027_hex_batch_harness122\build_and_install123.py"

src = open(SRC, encoding="utf-8").read()

REPS = [
    ('assert script_txt.count("\\t{ marker = ") == 697, "the abilities table is not 697 entries"',
     'assert script_txt.count("\\t{ marker = ") == 707, "the abilities table is not 707 entries"'),
    ("assert script_txt.count('trigger = \"melee_unwavering\"') == 370",
     "assert script_txt.count('trigger = \"melee_unwavering\"') == 374"),
    ("assert script_txt.count('trigger = \"charge_or_melee\"') == 25",
     "assert script_txt.count('trigger = \"charge_or_melee\"') == 28"),
    ('assert script_txt.count("\\t\\trange_real = ") == 204',
     'assert script_txt.count("\\t\\trange_real = ") == 207'),
]
for a, b in REPS:
    n = src.count(a)
    assert n >= 1, ("missing", a[:70])
    src = src.replace(a, b)
    print("  x%-3d %s" % (n, a[:90]))

src = src.replace('"melee_unwavering moved (370 after round 122)"', '"melee_unwavering moved (374 after round 123)"')
src = src.replace("the melee_unwavering entry count is not 370", "the melee_unwavering entry count is not 374")
src = src.replace("the melee_unwavering count is not 370", "the melee_unwavering count is not 374")
src = src.replace("the charge_or_melee entry count is not 26 (3 Class-B entries moved to ally_melee_buff)",
                  "the charge_or_melee entry count is not 28 (round 123: +3 enemy-speed hexes)")
src = src.replace('"the range_real fields are not 204"', '"the range_real fields are not 207"')
src = src.replace('"range_real count is not 204"', '"range_real count is not 207"')

GATE_ANCHOR = 'assert "FOURTH.evaluators = {" in script_txt, "the trigger -> evaluator map is missing"\n'
GATE = GATE_ANCHOR + '''# ROUND 123: the melee-only enemy-unit trigger (No Escape, Transfix dlc29, Flash Bomb).
assert ("function FOURTH.evaluate_enemy_melee(unit, routing)\\n\\tFOURTH.eg_melee_only = true\\n"
        "\\treturn FOURTH.eg_pick_enemy(unit, routing, false)\\nend") in script_txt, \\
    "the enemy_melee evaluator is missing or changed"
assert "\\tenemy_melee = FOURTH.evaluate_enemy_melee," in script_txt, "enemy_melee is not wired in the map"
assert script_txt.count('trigger = "enemy_melee"') == 3, "enemy_melee is not 3 entries"
assert "wh3_main_lord_abilities_daemonic_possession" not in script_txt, \\
    "Daemonic Possession must not be automated (user decision, round 123)"
print("ROUND 123 GATE OK: enemy_melee evaluator wired, 3 entries, no Daemonic Possession")
'''
assert src.count(GATE_ANCHOR) == 1, src.count(GATE_ANCHOR)
src = src.replace(GATE_ANCHOR, GATE)

src = src.replace("ROUND 122: ten self-cast melee buffs added on melee_unwavering; the table is\n",
                  "ROUND 123: the hex batch (4 melee_unwavering, 3 charge_or_melee, 3 on the new\n"
                  "enemy_melee, 1 twin key); the table is 707 entries / 759 keys.\n"
                  "ROUND 122: ten self-cast melee buffs added on melee_unwavering; the table is\n", 1)

open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
