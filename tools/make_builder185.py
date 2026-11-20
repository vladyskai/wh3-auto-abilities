#!/usr/bin/env python3
"""Build the round-185 build script from the round-184 one (the rule-shut review, rows 20-64).

Gate rebases: every '955' (entries) becomes 988, the one '1008' (keys) 1041; see R for the family and field pins.
ROUND 185 GATE: the 33 new entries ride the families the user ruled (2026-11-20, the Claude Docs review rev 127) with the
game's ranges and auras; the two new families are wired; the 30-men floor; Fog of the Damned and Mirror of Knowledge are
placed on the ground; Mirror is unbounded; the Immolation rune's bombardment radius is in the VORTEX table."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut2_harness183\build_and_install184.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut3_harness184\build_and_install185.py"
R = [
    # charge_only 4 -> 5 (Swiftness of Itzl)
    ("""assert script_txt.count('trigger = "charge_only"') == 4 \\""", """assert script_txt.count('trigger = "charge_only"') == 5 \\""", 1),
    # enemy_fast_near_ally 19 -> 20 (Mirror of Knowledge); 2 new target_class fields (Bonecrusher, Fog: not_flying)
    ("""    and script_txt.count('trigger = "enemy_fast_near_ally"') == 19 \\""",
     """    and script_txt.count('trigger = "enemy_fast_near_ally"') == 20 \\""", 1),
    ('    and script_txt.count("\\t\\ttarget_class = ") == 55 \\\n', '    and script_txt.count("\\t\\ttarget_class = ") == 57 \\\n', 1),
    # 2 new range_real fields (Bonecrusher, Fog of the Damned)
    ('assert script_txt.count("\\t\\trange_real = ") == 428,', 'assert script_txt.count("\\t\\trange_real = ") == 430,', 2),
    # enemy_ground_keys 126 -> 128 (Fog of the Damned, Mirror of Knowledge)
    ("""assert script_txt[_g0:_g1].count('"] = true,') == 126,""", """assert script_txt[_g0:_g1].count('"] = true,') == 128,""", 1),
    # self_recharging 5 -> 6 (Mad Cap Mushrooms)
    ("""    and script_txt.count('trigger = "self_recharging"') == 5 \\""", """    and script_txt.count('trigger = "self_recharging"') == 6 \\""", 1),
    # the round-159 blast families: melee_clear 4 -> 6, last_stand_clear 1 -> 3, enemy_blob_vortex 1 -> 2
    ('for _f, _n in (("melee_clear", 4), ("fly_dive", 2), ("last_stand_clear", 1), ("enemy_blob_vortex", 1)):',
     'for _f, _n in (("melee_clear", 6), ("fly_dive", 2), ("last_stand_clear", 3), ("enemy_blob_vortex", 2)):', 1),
    # the VORTEX table 10 -> 16 rows (Glacial Blast, Thundermace, Cellular Instability, Splode da Big 'Un!, Bonecrusher,
    # the Immolation rune's bombardment)
    ("assert len(_v159) == 10 and _g159.lua_block(_v159) in script_txt,", "assert len(_v159) == 16 and _g159.lua_block(_v159) in script_txt,", 1),
    # round 181: melee_clear_block is ridden by Land Mine AND Cellular Instability now
    ("""    assert script_txt.count('trigger = "%s"' % _f181) == 1, "BUILD REFUSED (round 181): %s is not ridden once" % _f181""",
     """    assert script_txt.count('trigger = "%s"' % _f181) == {"melee_clear_block": 2}.get(_f181, 1), \\
        "BUILD REFUSED (round 181): %s is not ridden as expected (round 185: melee_clear_block x2)" % _f181""", 1),
    ("""assert script_txt.count('trigger = "charge_only"') == 4, "the charge_only entry count is not 1\"""",
     """assert script_txt.count('trigger = "charge_only"') == 5, "the charge_only entry count is not 5 (round 185: + Swiftness of Itzl)\"""", 1),
    # 3 new ally_range_real fields (Twilight Horn II, Beastlord's Gaze, Offering to the Gods); 1 more unbounded entry
    ('assert script_txt.count("\\t\\tally_range_real = ") == 68,', 'assert script_txt.count("\\t\\tally_range_real = ") == 71,', 1),
    ('assert script_txt.count("\\t\\tunbounded = true,") == 2,', 'assert script_txt.count("\\t\\tunbounded = true,") == 3,', 1),
    # melee_unwavering 268 -> 281 (the 13 safe blasts)
    ("""script_txt.count('trigger = "melee_unwavering"') == 268""", """script_txt.count('trigger = "melee_unwavering"') == 281""", 4),
]
ANCHOR = ('print("ROUND 184 GATE OK: 10 entries on the ruled families with the game\'s ranges; 2 families wired; the 75% gate; "\n'
          '      "Warpstorm flying; Raging Tornado on the ground; 7 holds")\n')
ADD = ANCHOR + r'''# ROUND 185: the rule-shut review, rows 20-64 (user 2026-11-20: "Review ended, implement pls").
import sys as _sy185
_sy185.path.insert(0, r"C:\Users\vlady\Desktop\WH3_mod\tools")
import round185_rows as _rr185
for _row185, _m185, _n185, _t185, _k185, _f185 in _rr185.ROWS:
    _e185 = ('{ marker = "%s", name = ' % _m185)
    assert script_txt.count(_e185) == 1, "BUILD REFUSED (round 185): %s is not one entry" % _m185
    _j185 = script_txt.index(_e185)
    _b185 = script_txt[_j185:script_txt.index("ox = 0, oy = 0 },", _j185)]
    assert ('trigger = "%s",' % _t185) in _b185 and ('keys = { "%s" },' % _k185) in _b185, \
        "BUILD REFUSED (round 185): %s is not on its ruled family %s" % (_m185, _t185)
    for _fld185 in ("range_real", "ally_range_real", "aura_real", "unbounded", "target_class"):
        if _fld185 in _f185:
            assert ("\t\t%s = %s,\n" % (_fld185, _f185[_fld185])) in _b185, "BUILD REFUSED (round 185): %s %s" % (_m185, _fld185)
        else:
            assert ("\t\t%s = " % _fld185) not in _b185, "BUILD REFUSED (round 185): %s carries a stray %s" % (_m185, _fld185)
assert script_txt.count("-- ROUND 185 (rule-shut review row ") == 33, "BUILD REFUSED (round 185): row markers"
for _f185 in ("aura_charge_only", "ally_offering"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f185, _f185)) in script_txt, "BUILD REFUSED (round 185): %s not wired" % _f185
assert "\nFOURTH.OFFERING_MIN_MEN = 30" in script_txt, "BUILD REFUSED (round 185): the 30-men floor (user ruling 2026-11-20)"
for _g185 in _rr185.GROUND:
    assert script_txt.count('\t\t["%s"] = true,\n' % _g185) == 1, "BUILD REFUSED (round 185): %s must be a ground cast" % _g185
assert "wh2_dlc17_rune_abilities_master_rune_of_immolation=10;" in script_txt, \
    "BUILD REFUSED (round 185): the Immolation rune's 10 m bombardment radius"
print("ROUND 185 GATE OK: 33 entries on the ruled families; 2 families wired; the 30-men floor; 2 ground keys; "
      "the rune's 10 m bombardment")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
for old, new, want in (("955", "988", 22), ("1008", "1041", 1)):
    pat = r"(?<!\d)%s(?!\d)" % old
    got = len(re.findall(pat, src))
    assert got == want, (old, got)
    src = re.sub(pat, new, src)
    print(old, "->", new, ":", got)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
