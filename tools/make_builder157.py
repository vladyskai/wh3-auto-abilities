#!/usr/bin/env python3
"""Build the round-157 build script from the round-156 one.

Gates rebased: entries 810 -> 822 (11 gates); range_real fields 305 -> 317 (2); target classes 28 -> 29; the round-156
gate's SHOT key count 11 -> 23 (the drains and the Executioner joined the generated table).
Adds one gate: 10 drains and 2 executes on their families, the base Executioner's commander class, the re-check
kinds, and the SHOT and EXEC tables REGENERATED from the game data and found in the script."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_magic_missiles_harness155\build_and_install156.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_drains_harness156\build_and_install157.py"
ANCHOR = 'print("ROUND 156 GATE OK: 11 magic missiles on 5 families; the SHOT table matches the game; 10 m; 120 m -> 84 m; single class")\n'
ADD = ANCHOR + r'''# ROUND 157: the drains and the Executioner (user rulings 2026-11-15).
assert script_txt.count('trigger = "enemy_single_drain"') == 10 and script_txt.count('trigger = "enemy_execute"') == 2, \
    "the drains / the Executioner are not on their families"
for _f in ("enemy_single_drain", "enemy_execute"):
    assert ("%s = FOURTH.evaluate_%s," % (_f, _f)) in script_txt, "family %s is not wired" % _f
assert ('trigger = "enemy_execute",\n\t\tbadge = "zz_auto_badge_emperors_executioner",\n'
        '\t\tkeys = { "wh3_dlc24_lord_abilities_the_emperors_executioner" },\n\t\trange_real = 50,\n'
        '\t\ttarget_class = "commander",') in script_txt, "the base Executioner lacks the game's commander class"
assert 'if kind == "execute" and not FOURTH.exec_ok(e) then return false end' in script_txt, \
    "the execute re-check is missing"
import gen_shot_tables as _g157
_k157 = _g157.keys_in(script_txt)
assert len(_k157) == 23, "the shot families do not carry 23 keys"
assert _g157.exec_block(_g157.exec_rows(set(_k157))) in script_txt, \
    "BUILD REFUSED (round 157): the EXEC table differs from the game data"
print("ROUND 157 GATE OK: 10 drains, 2 executes; the SHOT and EXEC tables match the game; commander class on the base Executioner")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 810, "the abilities table is not 810 entries"',
     'script_txt.count("\\t{ marker = ") == 822, "the abilities table is not 822 entries"', 11),
    ('count("\\t\\trange_real = ") == 305', 'count("\\t\\trange_real = ") == 317', 2),
    ('script_txt.count("\\t\\ttarget_class = ") == 28', 'script_txt.count("\\t\\ttarget_class = ") == 29', 1),
    ('assert len(_k156) == 11, "the magic-missile families do not carry 11 keys"',
     'assert len(_k156) == 23, "the shot families do not carry 23 keys (round 157: + the drains, the Executioner)"', 1),
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
