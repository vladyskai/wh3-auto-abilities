#!/usr/bin/env python3
"""Build the round-134 build script from the round-133 one.

Gates rebased (the round deliberately moves them):
  entries 700 -> 698 (Thunderburner and Thunderburner Upgraded removed),
  melee_unwavering 342 -> 328, charge_or_melee 28 -> 36, charge_only 1 -> 5;
  the AUTO327 roster list drops the two Thunderburner rows: 302 -> 300 entries / 317 -> 315 keys.
Adds one gate: the round-134 triggers are set and Thunderburner is gone."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261108_under_fire_harness132\build_and_install133.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261109_speed_triggers_harness133\build_and_install134.py"

GONE = ["thunderburner", "thunderburner_upgraded"]
ANCHOR = 'print("ROUND 133 GATE OK: 3 on under_fire, 4 on melee_or_under_fire")\n'
ADD = ANCHOR + '''# ROUND 134: audit batch 3, the speed buffs leave the melee-only trigger; Thunderburner leaves the mod.
for _m in ("apocalyptic_charge", "twilight_horn_i", "potion_of_speed", "blooood"):
    assert '{ marker = "%s", name = ' % _m in script_txt, "round-134 charge-only marker missing: " + _m
assert "thunderburner" not in script_txt, "Thunderburner is still automated"
assert script_txt.count('trigger = "charge_only"') == 5 \\
    and script_txt.count('trigger = "charge_or_melee"') == 36, \\
    "the round-134 trigger counts are wrong"
print("ROUND 134 GATE OK: 5 on charge_only, 36 on charge_or_melee, Thunderburner gone")
'''

RULES = [
    ('script_txt.count("\\t{ marker = ") == 700, "the abilities table is not 700 entries"',
     'script_txt.count("\\t{ marker = ") == 698, "the abilities table is not 698 entries"'),
    ("script_txt.count('trigger = \"melee_unwavering\"') == 342", "script_txt.count('trigger = \"melee_unwavering\"') == 328"),
    ("script_txt.count('trigger = \"charge_or_melee\"') == 28", "script_txt.count('trigger = \"charge_or_melee\"') == 36"),
    ("script_txt.count('trigger = \"charge_only\"') == 1", "script_txt.count('trigger = \"charge_only\"') == 5"),
    ('assert len(AUTO327) == 302,', 'assert len(AUTO327) == 300,'),
    ('assert _nk327 == 317,', 'assert _nk327 == 315,'),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
lines = src.split("\n")
kept, dropped = [], 0
for ln in lines:
    s = ln.strip()
    if s.startswith('("') and any(s.startswith('("%s",' % m) for m in GONE):
        dropped += 1
        continue
    kept.append(ln)
assert dropped == 2, dropped
src = "\n".join(kept)
for a, b in RULES:
    n = src.count(a)
    assert n >= 1, a
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:70]))
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("dropped %d Thunderburner rows; wrote %s" % (dropped, DST))
