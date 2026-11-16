#!/usr/bin/env python3
"""Build the round-162 build script from the round-161 one.

Gates rebased: entries 860 -> 892 (11 gates); range_real fields 333 -> 365; target classes 33 -> 43.
Adds one gate: 12 waves and 20 wanderers on their families, both wired with the ww pre-cast re-check, neither starting
armed, and the WW table REGENERATED from the game data (the simulated 95% drift, fixed seeds) and found in the script."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_ally_buffs_armed_harness160\build_and_install161.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_wandering_winds_harness161\build_and_install162.py"
ANCHOR = 'print("ROUND 161 GATE OK: the 14 ally melee buffs start armed; the friendly-fire families still start unarmed")\n'
ADD = ANCHOR + r'''# ROUND 162: the wandering winds (user rulings 2026-11-16).
assert script_txt.count('trigger = "enemy_wave"') == 12 and script_txt.count('trigger = "enemy_wander"') == 20, \
    "the waves / wanderers are not on their families"
for _f162 in ("enemy_wave", "enemy_wander"):
    assert ("%s = FOURTH.evaluate_%s," % (_f162, _f162)) in script_txt, "family %s is not wired" % _f162
    assert ("\n\t%s = true," % _f162) not in script_txt.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("\n}", 1)[0], \
        "%s must start unarmed (M)" % _f162
assert 'elseif eg_mode_now == "ww" then' in script_txt and "cond_now = FOURTH.ww_still_ok(enemy, unit)" in script_txt, \
    "the ww pre-cast re-check is missing"
for _k162 in ("wh3_pro10_cataclysm_metal_gehennas_golden_globe_bound", "wh3_main_spell_bound_wall_of_wind_and_fire"):
    assert ('"%s"' % _k162) not in script_txt, "%s was closed by the user" % _k162
import gen_ww_tables as _g162
_kf162 = _g162.keys_in(script_txt)
assert len(_kf162) == 32 and _g162.lua_block(_g162.derive(_kf162)) in script_txt, \
    "BUILD REFUSED (round 162): the WW table differs from the game data"
print("ROUND 162 GATE OK: 12 waves, 20 wanderers, the ww re-check, both unarmed by default; the WW table matches the game")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 860, "the abilities table is not 860 entries"',
     'script_txt.count("\\t{ marker = ") == 892, "the abilities table is not 892 entries"'),
    ('count("\\t\\trange_real = ") == 333', 'count("\\t\\trange_real = ") == 365'),
    ('script_txt.count("\\t\\ttarget_class = ") == 33', 'script_txt.count("\\t\\ttarget_class = ") == 43'),
    # the round-160 gate counts every mod key while it re-derives the wind-up set: 917 -> 949
    ("assert len(_keys160) == 917 and _wu160 == _tab160,", "assert len(_keys160) == 949 and _wu160 == _tab160,"),
    ('"table matches the game (%d of 917 keys have a wind-up)"', '"table matches the game (%d of 949 keys have a wind-up)"'),
    # the round-118 dead-symbol gate searched the bare substring "dwell", which the game's own key
    # wh3_main_spell_bound_the_dwellers_below now carries; narrowed to " dwell" (every deleted form started with a space)
    ('              "dwell", "short crossing", "proj="):', '              " dwell", "short crossing", "proj="):'),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1, src.count(ANCHOR)
src = src.replace(ANCHOR, ADD)
for a, b in RULES:
    n = src.count(a)
    assert n >= 1, (a[:70], n)
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:70]))
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
