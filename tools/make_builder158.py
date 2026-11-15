#!/usr/bin/env python3
"""Build the round-158 build script from the round-157 one.

Gates rebased: entries 822 -> 834 (11 gates); range_real fields 317 -> 329 (2); target classes 29 -> 31; enemy_melee
34 -> 35 (2 gates: Preyton Horns); enemy_melee_or_fast 2 -> 4 (Ethrac's Brazier, Storm of the Night); the SHOT key
count 23 -> 33 (2 gates).
Adds one gate: 7 area drains and the Leach Orb on their families, the flying class on Storm of the Night, the
commander class on the Leach Orb, the morale hexes on their families, and the AREA table REGENERATED from the game data
and found in the script."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_drains_harness156\build_and_install157.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_last_group_b_harness157\build_and_install158.py"
ANCHOR = 'print("ROUND 157 GATE OK: 10 drains, 2 executes; the SHOT and EXEC tables match the game; commander class on the base Executioner")\n'
ADD = ANCHOR + r'''# ROUND 158: the last group B attacks (user rulings 2026-11-15).
assert script_txt.count('trigger = "enemy_area_drain"') == 7 and script_txt.count('trigger = "enemy_commander_value"') == 1, \
    "the area drains / the Leach Orb are not on their families"
for _f in ("enemy_area_drain", "enemy_commander_value"):
    assert ("%s = FOURTH.evaluate_%s," % (_f, _f)) in script_txt, "family %s is not wired" % _f
for _m, _t, _extra in (("storm_of_the_night", "enemy_melee_or_fast", '\t\ttarget_class = "flying",'),
                       ("dweomer_leach_orb", "enemy_commander_value", '\t\ttarget_class = "commander",'),
                       ("ethracs_brazier", "enemy_melee_or_fast", ""), ("preyton_horns", "enemy_melee", ""),
                       ("the_amber_trance", "enemy_wavering", "")):
    _i = script_txt.find('{ marker = "%s", ' % _m)
    assert _i >= 0 and ('trigger = "%s",' % _t) in script_txt[_i:_i + 200] and _extra in script_txt[_i:_i + 300], \
        "%s is not on %s with its class" % (_m, _t)
assert 'if cls == "flying" then' in script_txt, "the flying class is missing"
import gen_shot_tables as _g158
_k158 = _g158.keys_in(script_txt)
assert len(_k158) == 33, "the shot families do not carry 33 keys"
import re as _re158
_a158 = set(m.group(1) for m in _re158.finditer(
    r'trigger = "enemy_area_drain",\n\t\tbadge = "[^"]+",\n\t\tkeys = \{ "([^"]+)" \}', script_txt))
assert len(_a158) == 7 and _g158.area_block(_g158.area_rows(_a158)) in script_txt, \
    "BUILD REFUSED (round 158): the AREA table differs from the game data"
print("ROUND 158 GATE OK: 7 area drains, the Leach Orb proxy, Storm flying-only, the morale hexes; the AREA table matches the game")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 822, "the abilities table is not 822 entries"',
     'script_txt.count("\\t{ marker = ") == 834, "the abilities table is not 834 entries"', 11),
    ('count("\\t\\trange_real = ") == 317', 'count("\\t\\trange_real = ") == 329', 2),
    ('script_txt.count("\\t\\ttarget_class = ") == 29', 'script_txt.count("\\t\\ttarget_class = ") == 31', 1),
    ("script_txt.count('trigger = \"enemy_melee\"') == 34", "script_txt.count('trigger = \"enemy_melee\"') == 35", 2),
    ('assert script_txt.count(\'trigger = "enemy_melee"\') == 35, "enemy_melee is not 34 entries"',
     'assert script_txt.count(\'trigger = "enemy_melee"\') == 35, "enemy_melee is not 35 entries"', 0),
    ('("enemy_melee_or_fast", 2)', '("enemy_melee_or_fast", 4)', 1),
    ('assert len(_k156) == 23,', 'assert len(_k156) == 33,', 1),
    ('assert len(_k157) == 23, "the shot families do not carry 23 keys"',
     'assert len(_k157) == 33, "the shot families do not carry 33 keys (round 158)"', 1),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, n in RULES:
    if n == 0:
        continue
    assert src.count(a) == n, (a[:60], src.count(a))
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:60]))
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
