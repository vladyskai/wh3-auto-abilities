#!/usr/bin/env python3
"""Build the round-141 build script from the round-140 one.

Gates rebased: melee_unwavering 314 -> 306 (4 gates), ushoran_health 20 -> 19, melee_health75 1 -> 2,
ally_range_real fields 51 -> 53. Adds one gate: the casts are remembered, the four reducer families are wired, and
BUILD REFUSED when the embedded lock-time table differs from the game data (tools/gen_recharge_keys.py)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_moving_running_harness139\build_and_install140.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261113_recharge_reducers_harness140\build_and_install141.py"
ANCHOR = 'print("ROUND 140 GATE OK: the moving rule guards every firing-flag read; Blooood! on self_running; fire_move matches the game")\n'
ADD = ANCHOR + r'''# ROUND 141: the nine recharge reducers, one by one.
assert "FOURTH.note_cast(unit, ability_key)" in script_txt \
    and script_txt.count('trigger = "self_recharging"') == 5 \
    and script_txt.count('trigger = "self_recharging_2"') == 1 \
    and script_txt.count('trigger = "recharging_in_reach"') == 1 \
    and script_txt.count('trigger = "melee_self_or_ally"') == 1, \
    "the round-141 recharge-reducer triggers are missing"
import gen_recharge_keys as _g141
assert _g141.lua_block(_g141.derive()) in script_txt, \
    "BUILD REFUSED (round 141): the lock-time table differs from the game data"
print("ROUND 141 GATE OK: casts remembered; 5 + 1 + 1 + 1 reducers on their families; the lock table matches the game")
'''
RULES = [
    ("script_txt.count('trigger = \"melee_unwavering\"') == 314", "script_txt.count('trigger = \"melee_unwavering\"') == 306", 4),
    ("script_txt.count('trigger = \"ushoran_health\"') == 20", "script_txt.count('trigger = \"ushoran_health\"') == 19", 1),
    ("script_txt.count('trigger = \"melee_health75\"') == 1", "script_txt.count('trigger = \"melee_health75\"') == 2", 1),
    ('script_txt.count("\\t\\tally_range_real = ") == 51', 'script_txt.count("\\t\\tally_range_real = ") == 53', 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    assert src.count(a) == n, (a, src.count(a))
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:60]))
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
