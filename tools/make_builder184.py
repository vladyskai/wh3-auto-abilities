#!/usr/bin/env python3
"""Build the round-184 build script from the round-183 one (the rule-shut review, rows 10-19).

Gate rebases: every '945' (entries) becomes 955, the one '998' (keys) 1008; see R for the family and table pins.
ROUND 184 GATE: the 10 new entries ride the families the user ruled (2026-11-20, the Claude Docs review rev 83) with the
game's ranges; the two new families are wired; the 75% gate; Warpstorm Scroll's flying class; Raging Tornado is placed
on the ground (enemy_ground_keys); the holds and wind-ups; the SHOT and AREA tables cover the new keys."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut1_harness182\build_and_install183.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut2_harness183\build_and_install184.py"
R = [
    # enemy_area_drain 8 -> 13 (Flock of Doom x3, Sword of Daith, Zefet-nebtar)
    ("""assert script_txt.count('trigger = "enemy_area_drain"') == 8 and""",
     """assert script_txt.count('trigger = "enemy_area_drain"') == 13 and""", 1),
    # enemy_single_drain 12 -> 14 (Ring of Corin, Warpstorm Scroll)
    ("""assert script_txt.count('trigger = "enemy_single_drain"') == 12 and""",
     """assert script_txt.count('trigger = "enemy_single_drain"') == 14 and""", 1),
    # 10 new range_real fields (every row 10-19 entry is aimed)
    ('assert script_txt.count("\\t\\trange_real = ") == 418,', 'assert script_txt.count("\\t\\trange_real = ") == 428,', 2),
    # enemy_ground_keys 125 -> 126 (Raging Tornado, placed on the ground)
    ("""assert script_txt[_g0:_g1].count('"] = true,') == 125,""", """assert script_txt[_g0:_g1].count('"] = true,') == 126,""", 1),
    # one new target_class field (Warpstorm Scroll: flying)
    ('    and script_txt.count("\\t\\ttarget_class = ") == 54 \\\n', '    and script_txt.count("\\t\\ttarget_class = ") == 55 \\\n', 1),
    # the SHOT families carry 70 keys (61 + 5 area + 2 single + 2 hurt)
    ("assert len(_k156) == 61,", "assert len(_k156) == 70,", 1),
    ("assert len(_k157) == 61,", "assert len(_k157) == 70,", 1),
    ("assert len(_k158) == 61,", "assert len(_k158) == 70,", 1),
    # the AREA table: the area families' keys (11 -> 18; the new enemy_area_drain_hurt family joins the regex)
    ("""    r'trigger = "enemy_(?:area_drain|most_models)",\\n\\t\\tbadge = "[^"]+",\\n\\t\\tkeys = \\{ "([^"]+)" \\}', script_txt))
assert len(_a158) == 11 and""",
     """    r'trigger = "enemy_(?:area_drain|area_drain_hurt|most_models)",\\n\\t\\tbadge = "[^"]+",\\n\\t\\tkeys = \\{ "([^"]+)" \\}', script_txt))
assert len(_a158) == 18 and""", 1),
]
ANCHOR = 'print("ROUND 183 GATE OK: 9 entries on the ruled families (4 enemy_melee_near at 35 m, 2 melee_health75, 3 melee_unwavering); 6 holds")\n'
ADD = ANCHOR + r'''# ROUND 184: the rule-shut review, rows 10-19 (user 2026-11-20: "Up to #19 ruled").
_r184 = [
    ("flock_of_doom_runecaller", "enemy_area_drain", "wh3_dlc27_spell_bound_runecaller_flock_of_doom", 100, None),
    ("flock_of_doom_wh3", "enemy_area_drain", "wh3_main_spell_bound_flock_of_doom", 100, None),
    ("flock_of_doom", "enemy_area_drain", "wh_dlc08_spell_bound_flock_of_doom", 100, None),
    ("sword_of_daith", "enemy_area_drain", "wh_dlc05_weapon_abilities_daiths_sword", 100, None),
    ("zefet_nebtar", "enemy_area_drain", "wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade", 100, None),
    ("ring_of_corin", "enemy_single_drain", "wh2_main_spell_bound_ring_of_corin", 200, None),
    ("soul_stealer_ror", "enemy_area_drain_hurt", "wh2_dlc10_spell_bound_soul_stealer_ror", 100, None),
    ("soul_stealer_anointed", "enemy_area_drain_hurt", "wh3_dlc27_spell_bound_soul_stealer", 100, None),
    ("warpstorm_scroll", "enemy_single_drain", "wh2_main_item_abilities_warpstorm_scroll", 100, "flying"),
    ("raging_tornado", "enemy_ground_melee_cluster", "wh3_dlc29_unit_abilities_raging_tornado", 100, None),
]
for _m184, _t184, _k184, _r184r, _c184 in _r184:
    _e184 = ('{ marker = "%s", name = ' % _m184)
    assert script_txt.count(_e184) == 1, "BUILD REFUSED (round 184): %s is not one entry" % _m184
    _j184 = script_txt.index(_e184)
    _b184 = script_txt[_j184:script_txt.index("ox = 0, oy = 0 },", _j184)]
    assert ('trigger = "%s",' % _t184) in _b184 and ('keys = { "%s" },' % _k184) in _b184 \
        and ("\t\trange_real = %d,\n" % _r184r) in _b184, \
        "BUILD REFUSED (round 184): %s is not on its ruled family %s with the game's range" % (_m184, _t184)
    assert (_c184 is None) == ("target_class" not in _b184), "BUILD REFUSED (round 184): %s class" % _m184
    if _c184 is not None:
        assert ('\t\ttarget_class = "%s",\n' % _c184) in _b184, "BUILD REFUSED (round 184): %s class" % _m184
for _f184 in ("enemy_area_drain_hurt", "enemy_ground_melee_cluster"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f184, _f184)) in script_txt, "BUILD REFUSED (round 184): %s not wired" % _f184
assert "\nFOURTH.DRAIN_HURT_PCT = 75" in script_txt, "BUILD REFUSED (round 184): the 75% gate (user ruling 2026-11-20)"
assert script_txt.count('\t\t["wh3_dlc29_unit_abilities_raging_tornado"] = true,\n') == 1, \
    "BUILD REFUSED (round 184): Raging Tornado must be placed on the ground (enemy_ground_keys)"
assert script_txt.count("-- ROUND 184 (rule-shut review row ") == 10, "BUILD REFUSED (round 184): row markers"
for _k184, _v184 in (("wh3_dlc27_spell_bound_runecaller_flock_of_doom", "60"), ("wh3_main_spell_bound_flock_of_doom", "60"),
                     ("wh_dlc08_spell_bound_flock_of_doom", "60"), ("wh_dlc05_weapon_abilities_daiths_sword", "120"),
                     ("wh3_dlc29_item_abilities_zefet_nebtar_the_mortis_blade", "120"),
                     ("wh2_main_spell_bound_ring_of_corin", "90"), ("wh3_dlc29_unit_abilities_raging_tornado", "120")):
    assert script_txt.count('\t\t["%s"] = %s,\n' % (_k184, _v184)) == 1, "BUILD REFUSED (round 184): hold for %s" % _k184
print("ROUND 184 GATE OK: 10 entries on the ruled families with the game's ranges; 2 families wired; the 75% gate; "
      "Warpstorm flying; Raging Tornado on the ground; 7 holds")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
for old, new, want in (("945", "955", 22), ("998", "1008", 1)):
    pat = r"(?<!\d)%s(?!\d)" % old
    got = len(re.findall(pat, src))
    assert got == want, (old, got)
    src = re.sub(pat, new, src)
    print(old, "->", new, ":", got)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
