#!/usr/bin/env python3
"""Build the round-183 build script from the round-182 one (the rule-shut review, rows 1-9).

Gate rebases: every '936' (entries) becomes 945, the one '989' (keys) 998, the four melee_unwavering '265' pins 268
(Shard Blade, Web of Shadows, Warp-Quake).
ROUND 183 GATE: the 9 new entries ride the families the user ruled (2026-11-20, the Claude Docs review rev 44); rows 1-4
carry the game's 35 m aura (effect_range); the 6 multi-use keys are held for their recharge_time; none is risky."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_finishers_harness181\build_and_install182.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_ruleshut1_harness182\build_and_install183.py"
ANCHOR = 'print("ROUND 182 GATE OK: 2 families wired; the Executioner\'s 90% bound (225 m); execute ranks the highest health; Skjalandir moved")\n'
ADD = ANCHOR + r'''# ROUND 183: the rule-shut review, rows 1-9 (user 2026-11-20: "You may start implementing #1-9 for now").
_r183 = [
    ("defiling_deluge", "enemy_melee_near", "wh3_twa08_unit_abilities_defiling_deluge", 35),
    ("murderous_exhortations", "enemy_melee_near", "wh3_dlc26_lord_abilities_murderous_exhortations", 35),
    ("rod_of_corruption", "enemy_melee_near", "wh2_main_item_abilities_rod_of_corruption", 35),
    ("wail_of_malice", "enemy_melee_near", "wh2_dlc14_unit_abilities_wail_of_malice", 35),
    ("plaguereaper", "melee_health75", "wh3_dlc29_item_abilities_plaguereaper", None),
    ("reaper_of_souls", "melee_health75", "wh2_dlc14_lord_abilities_reaper_of_souls", None),
    ("shard_blade", "melee_unwavering", "wh3_main_weapon_abilities_shard_blade", None),
    ("web_of_shadows", "melee_unwavering", "wh2_main_weapon_abilities_web_of_shadows", None),
    ("warp_quake", "melee_unwavering", "wh2_dlc14_unit_abilities_warp_quake", None),
]
for _m183, _t183, _k183, _a183 in _r183:
    _e183 = ('{ marker = "%s", name = ' % _m183)
    assert script_txt.count(_e183) == 1, "BUILD REFUSED (round 183): %s is not one entry" % _m183
    _j183 = script_txt.index(_e183)
    _b183 = script_txt[_j183:script_txt.index("ox = 0, oy = 0 },", _j183)]
    assert ('trigger = "%s",' % _t183) in _b183 and ('keys = { "%s" },' % _k183) in _b183, \
        "BUILD REFUSED (round 183): %s is not on its ruled family %s" % (_m183, _t183)
    assert (_a183 is None) == ("aura_real" not in _b183), "BUILD REFUSED (round 183): %s aura" % _m183
    if _a183 is not None:
        assert ("\t\taura_real = %d,\n" % _a183) in _b183, "BUILD REFUSED (round 183): %s aura is not the game's" % _m183
assert script_txt.count("-- ROUND 183 (rule-shut review row ") == 9, "BUILD REFUSED (round 183): row markers"
for _k183, _v183 in (("wh3_twa08_unit_abilities_defiling_deluge", 120), ("wh3_dlc26_lord_abilities_murderous_exhortations", 120),
                     ("wh2_main_item_abilities_rod_of_corruption", 120), ("wh2_dlc14_unit_abilities_wail_of_malice", 90),
                     ("wh3_dlc29_item_abilities_plaguereaper", 120), ("wh3_main_weapon_abilities_shard_blade", 120)):
    assert script_txt.count('\t\t["%s"] = %d,\n' % (_k183, _v183)) == 1, "BUILD REFUSED (round 183): hold for %s" % _k183
print("ROUND 183 GATE OK: 9 entries on the ruled families (4 enemy_melee_near at 35 m, 2 melee_health75, 3 melee_unwavering); 6 holds")
'''
src = open(SRC, encoding="utf-8").read()
for old, new, want in (("936", "945", 22), ("989", "998", 1), ("265", "268", 4)):
    pat = r"(?<!\d)%s(?!\d)" % old
    got = len(re.findall(pat, src))
    assert got == want, (old, got)
    src = re.sub(pat, new, src)
    print(old, "->", new, ":", got)
_MH_OLD = """assert script_txt.count('trigger = "melee_health75"') == 2, "the melee_health75 entry count is not 1 (Captain of the Phoenix Guard moved to ally_heal_melee)\""""
_MH_NEW = """assert script_txt.count('trigger = "melee_health75"') == 4, "the melee_health75 entry count is not 4 (round 183: + Plaguereaper, Reaper of Souls)\""""
assert src.count(_MH_OLD) == 1
src = src.replace(_MH_OLD, _MH_NEW)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
