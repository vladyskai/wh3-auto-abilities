#!/usr/bin/env python3
"""Build the round-169 build script from the round-168 one (every enemy read skips hidden enemies).

ROUND 169 GATE: the air drop (ad_nearest), the 'just beyond range' read (nearest_enemy_gap) and the contact set
(engagement_set) carry the visibility test. No earlier gate needed a rebase."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_anim_visibility_harness167\build_and_install168.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_sensor_visibility_harness168\build_and_install169.py"
ANCHOR = ('print("ROUND 168 GATE OK: ANIM (%d of 1003 keys) matches the game; the stand-still gate asks it; both pickers skip "\n'
          '      "hidden enemies" % len(_a168))\n')
ADD = ANCHOR + r'''# ROUND 169: every enemy read skips hidden enemies (2026-11-17).
_v169 = (script_txt.count("and FOURTH.enemy_not_hidden(enemy) then   -- ROUND 169: never a hidden enemy\n"),
         script_txt.count("and FOURTH.enemy_not_hidden(enemy)   -- ROUND 169: never a hidden enemy\n"))
assert _v169 == (2, 1), "BUILD REFUSED (round 169): an enemy read lacks the visibility test %s" % (_v169,)
for _fn169 in ("function FOURTH.ad_nearest(unit)", "function FOURTH.nearest_enemy_gap(unit, inner)",
               "function FOURTH.engagement_set(unit)"):
    _body169 = script_txt.split(_fn169, 1)[1].split("\nend\n", 1)[0]
    assert "FOURTH.enemy_not_hidden(enemy)" in _body169, "BUILD REFUSED (round 169): %s has no visibility test" % _fn169
print("ROUND 169 GATE OK: the air drop, the 'just beyond range' read and the contact set skip hidden enemies")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1, src.count(ANCHOR)
src = src.replace(ANCHOR, ADD)
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
