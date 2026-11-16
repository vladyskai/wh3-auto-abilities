#!/usr/bin/env python3
"""Build the round-163 build script from the round-162 one.

Gates rebased: entries 892 -> 918 (11 gates); range_real fields 365 -> 389; target classes 43 -> 47; the round-160 key
count 949 -> 975; the round-162 gate's enemy_wander 20 -> 42 and WW keys 32 -> 56; the SHOT key count 35 -> 36
(Winged Staff); enemy_area_drain 7 -> 8; further rebases only where a refused build proves them.
Adds one gate: the two new families wired and unarmed by default, the expendable skip in the map, and the EXPENDABLE
table REGENERATED from the game data."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_wandering_winds_harness161\build_and_install162.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_placed_areas_harness162\build_and_install163.py"
ANCHOR = ('print("ROUND 162 GATE OK: 12 waves, 20 wanderers, the ww re-check, both unarmed by default; the WW table matches '
          'the game")\n')
ADD = ANCHOR + r'''# ROUND 163: the placed areas and the expendable units (user rulings 2026-11-16).
assert script_txt.count('trigger = "enemy_strike"') == 1 and script_txt.count('trigger = "ally_blast"') == 1, \
    "Siegebreaker / Arcane Vassal are not on their families"
_def163 = script_txt.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("\n}", 1)[0]
for _f163 in ("enemy_strike", "ally_blast"):
    assert ("%s = FOURTH.evaluate_%s," % (_f163, _f163)) in script_txt, "family %s is not wired" % _f163
    assert ("\n\t%s = true," % _f163) not in _def163, "%s must start unarmed (M)" % _f163
assert "if s ~= nil and not FOURTH.ff_ignored(s) then m.ours[#m.ours + 1] = s end" in script_txt \
    and "return s.vps ~= nil and s.vps < FOURTH.TRASH_VPS" in script_txt, "the expendable / cheap skip is missing"
for _k163 in ("wh_main_rune_abilities_rune_of_wrath_and_ruin", "wh_dlc06_rune_abilities_master_rune_of_wrath_and_ruin"):
    assert ('"%s"' % _k163) not in script_txt, "%s was closed by the user" % _k163
import gen_expendable_keys as _g163
_e163 = _g163.derive()
assert len(_e163) == 48 and _g163.lua_block(_e163) in script_txt, \
    "BUILD REFUSED (round 163): the EXPENDABLE table differs from the game data"
print("ROUND 163 GATE OK: the strike and the vassal wired and unarmed, the expendable / cheap skip; the EXPENDABLE "
      "table matches the game (48 units)")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 892, "the abilities table is not 892 entries"',
     'script_txt.count("\\t{ marker = ") == 918, "the abilities table is not 918 entries"'),
    ('count("\\t\\trange_real = ") == 365', 'count("\\t\\trange_real = ") == 389'),
    ('script_txt.count("\\t\\ttarget_class = ") == 43', 'script_txt.count("\\t\\ttarget_class = ") == 47'),
    ("assert len(_keys160) == 949 and _wu160 == _tab160,", "assert len(_keys160) == 975 and _wu160 == _tab160,"),
    ('"table matches the game (%d of 949 keys have a wind-up)"', '"table matches the game (%d of 975 keys have a wind-up)"'),
    ("script_txt.count('trigger = \"enemy_wander\"') == 20", "script_txt.count('trigger = \"enemy_wander\"') == 42"),
    ("assert len(_kf162) == 32 and", "assert len(_kf162) == 56 and"),
    ('assert len(_k156) == 35,', 'assert len(_k156) == 36,'),
    ('assert len(_k157) == 35,', 'assert len(_k157) == 36,'),
    ('assert len(_k158) == 35, "the shot families do not carry 35 keys (round 159)"',
     'assert len(_k158) == 36, "the shot families do not carry 36 keys (round 163)"'),
    ("script_txt.count('trigger = \"enemy_area_drain\"') == 7", "script_txt.count('trigger = \"enemy_area_drain\"') == 8"),
    ("assert len(_a158) == 7 and", "assert len(_a158) == 8 and"),
    # found by the first refused build: the round-135 gate counts enemy_fast_near_ally (Befuddlement joins: 8 -> 9)
    ("script_txt.count('trigger = \"enemy_fast_near_ally\"') == 8", "script_txt.count('trigger = \"enemy_fast_near_ally\"') == 9"),
    # Arcane Vassal adds an ally_range_real field (57 -> 58); Magma Storm is a second unbounded entry (1 -> 2)
    ('assert script_txt.count("\\t\\tally_range_real = ") == 57,', 'assert script_txt.count("\\t\\tally_range_real = ") == 58,'),
    ('assert script_txt.count("\\t\\tunbounded = true,") == 1, "the one unbounded entry is not flagged"',
     'assert script_txt.count("\\t\\tunbounded = true,") == 2, "the two unbounded entries are not flagged"'),
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
