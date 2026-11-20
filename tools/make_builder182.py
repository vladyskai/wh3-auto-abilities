#!/usr/bin/env python3
"""Build the round-182 build script from the round-181 one (the finishers).

Gate rebases: see R.
ROUND 182 GATE: the 2 new families wired and ridden once; the 90% fraction is the user's documented exception (only the
Executioner carries it, and its bound is floor(250 x 0.90) = 225); the execute ranking; Skjalandir's Fall moved; the
SHOT table covers enemy_finisher."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_landmine_squig_harness180\build_and_install181.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261120_finishers_harness181\build_and_install182.py"
R = [
    # round 130's gate named Skjalandir's family; it moved to melee_or_self_shooting (round 182)
    ("""    and 'trigger = "melee_or_shooting_into_melee"' in script_txt \\\n""",
     """    and 'trigger = "melee_or_self_shooting"' in script_txt \\\n""", 1),
    # the Executioner left enemy_blob (69 -> 68) and joined the shot families (60 -> 61 SHOT keys)
    ("""assert script_txt.count('trigger = "enemy_blob"') == 69,""", """assert script_txt.count('trigger = "enemy_blob"') == 68,""", 1),
    ("assert len(_k156) == 60,", "assert len(_k156) == 61,", 1),
    ("assert len(_k157) == 60,", "assert len(_k157) == 61,", 1),
    ("assert len(_k158) == 60,", "assert len(_k158) == 61,", 1),
]
ANCHOR = 'print("ROUND 181 GATE OK: 2 families wired; 60 soldiers; summon blast 21 m matches the game; 0 range mismatches; Lord of Undeath split")\n'
ADD = ANCHOR + r'''# ROUND 182: the finishers (user rulings 2026-11-17 and 2026-11-20).
for _f182 in ("enemy_finisher", "melee_or_self_shooting"):
    assert ("\t%s = FOURTH.evaluate_%s," % (_f182, _f182)) in script_txt, "BUILD REFUSED (round 182): %s not wired" % _f182
    assert script_txt.count('trigger = "%s"' % _f182) == 1, "BUILD REFUSED (round 182): %s is not ridden once" % _f182
assert "\nFOURTH.SINGLE_RANGE_FRACTION = 0.90" in script_txt and script_txt.count("\t\trange_frac = 0.90,\n") == 1, \
    "BUILD REFUSED (round 182): the 90% exception must stay the Executioner's alone (user ruling 2026-11-20)"
_i182 = script_txt.find('{ marker = "lord_abilities_executioner", name = "Executioner", trigger = "enemy_finisher",')
assert _i182 >= 0 and "\t\trange_real = 250,\n\t\trange_frac = 0.90,\n" in script_txt[_i182:_i182 + 300] and int(250 * 0.90) == 225, \
    "BUILD REFUSED (round 182): the Executioner's 90% bound"
assert "\t\t\ts1 = FOURTH.enemy_health_pct(e.unit) or 0\n\t\t\ts2 = e.value or 0\n" in script_txt, \
    "BUILD REFUSED (round 182): the Emperor's Executioner does not rank the highest health below the line"
assert 'trigger = "melee_or_shooting_into_melee"' not in script_txt, "BUILD REFUSED (round 182): Skjalandir's Fall did not move"
print("ROUND 182 GATE OK: 2 families wired; the Executioner's 90% bound (225 m); execute ranks the highest health; Skjalandir moved")
'''
src = open(SRC, encoding="utf-8").read()
for a, b, n in R:
    assert src.count(a) == n, (a[:80], src.count(a))
    src = src.replace(a, b)
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
