#!/usr/bin/env python3
"""Build the round-159 build script from the round-158 one.

Gates rebased: entries 834 -> 860; range_real fields 329 -> 333; target classes 31 -> 33; melee_unwavering 288 -> 299;
charge_or_melee 36 -> 37; wavering_self 3 -> 4; health_aura_ground 2 -> 3; enemy_ground_melee 74 -> 75;
enemy_commander_value 1 -> 3 (round-158 gate); the SHOT key count 33 -> 35 (Slann Gold, Deathmaster's Sigil).
Adds one gate: group E on its families (melee_clear 5, fly_dive 2, last_stand_clear 1, enemy_blob_vortex 1), the four
families wired, the commander_ground class on the Sigil, and the VORTEX table REGENERATED from the game data and found in
the script."""
import re

SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_last_group_b_harness157\build_and_install158.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261115_group_e_harness158\build_and_install159.py"
ANCHOR = ('print("ROUND 158 GATE OK: 7 area drains, the Leach Orb proxy, Storm flying-only, the morale hexes; the AREA table '
          'matches the game")\n')
ADD = ANCHOR + r'''# ROUND 159: group E (user rulings 2026-11-15).
for _f, _n in (("melee_clear", 5), ("fly_dive", 2), ("last_stand_clear", 1), ("enemy_blob_vortex", 1)):
    assert script_txt.count('trigger = "%s"' % _f) == _n, "%s does not carry %d entries" % (_f, _n)
for _f in ("melee_clear", "fly_dive", "last_stand_clear"):
    assert ("%s = FOURTH.evaluate_%s," % (_f, _f)) in script_txt, "family %s is not wired" % _f
assert "enemy_blob_vortex = FOURTH.evaluate_enemy_blob," in script_txt, "enemy_blob_vortex is not wired"
for _f in ("melee_clear", "fly_dive", "last_stand_clear", "enemy_blob_vortex"):
    assert ("\t%s = true," % _f) not in script_txt.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("}", 1)[0], \
        "%s must start unarmed (M)" % _f
for _m, _t, _extra in (("deathmasters_sigil", "enemy_commander_value", '\t\ttarget_class = "commander_ground",'),
                       ("slann_gold", "enemy_commander_value", '\t\ttarget_class = "commander",'),
                       ("heavens_flash", "enemy_ground_melee", "\t\trange_real = 75,"),
                       ("slime_smoothie", "health_aura_ground", "\t\taura_real = 35,"),
                       ("maneater_smoke_bomb", "charge_or_melee", ""), ("verminous_valour", "wavering_self", ""),
                       ("burp_of_grom", "melee_unwavering", ""), ("necrotic_explosion", "last_stand_clear", "")):
    _i = script_txt.find('{ marker = "%s", ' % _m)
    assert _i >= 0 and ('trigger = "%s",' % _t) in script_txt[_i:_i + 200] and _extra in script_txt[_i:_i + 400], \
        "%s is not on %s with its fields" % (_m, _t)
assert 'if cls == "commander_ground" then' in script_txt, "the commander_ground class is missing"
import gen_vortex_tables as _g159
_v159 = _g159.derive(_g159.keys_in(script_txt))
assert len(_v159) == 10 and _g159.lua_block(_v159) in script_txt, \
    "BUILD REFUSED (round 159): the VORTEX table differs from the game data"
print("ROUND 159 GATE OK: group E on its families (5 melee_clear, 2 fly_dive, 1 last_stand_clear, 1 enemy_blob_vortex), "
      "the Sigil's commander_ground class; the VORTEX table matches the game (10 keys)")
'''
RULES = [
    ('script_txt.count("\\t{ marker = ") == 834, "the abilities table is not 834 entries"',
     'script_txt.count("\\t{ marker = ") == 860, "the abilities table is not 860 entries"', None),
    ('count("\\t\\trange_real = ") == 329', 'count("\\t\\trange_real = ") == 333', None),
    ('script_txt.count("\\t\\ttarget_class = ") == 31', 'script_txt.count("\\t\\ttarget_class = ") == 33', None),
    ("count('trigger = \"melee_unwavering\"') == 288", "count('trigger = \"melee_unwavering\"') == 299", None),
    ("count('trigger = \"charge_or_melee\"') == 36", "count('trigger = \"charge_or_melee\"') == 37", None),
    ("count('trigger = \"wavering_self\"') == 3", "count('trigger = \"wavering_self\"') == 4", None),
    ("count('trigger = \"health_aura_ground\"') == 2", "count('trigger = \"health_aura_ground\"') == 3", None),
    ("count('trigger = \"enemy_ground_melee\"') == 74", "count('trigger = \"enemy_ground_melee\"') == 75", None),
    ("script_txt.count('trigger = \"enemy_commander_value\"') == 1",
     "script_txt.count('trigger = \"enemy_commander_value\"') == 3", None),
    ('assert len(_k156) == 33,', 'assert len(_k156) == 35,', None),
    ('assert len(_k157) == 33,', 'assert len(_k157) == 35,', None),
    ('assert len(_k158) == 33, "the shot families do not carry 33 keys"',
     'assert len(_k158) == 35, "the shot families do not carry 35 keys (round 159)"', None),
]
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
for a, b, _ in RULES:
    n = src.count(a)
    assert n >= 1, (a[:70], n)
    src = src.replace(a, b)
    print("rebased %d x: %s" % (n, a[:70]))
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
