#!/usr/bin/env python3
"""Build the round-168 build script from the round-167 one (the cast animation decides the stand-still rule; the older
pickers skip hidden enemies).

ROUND 168 GATE:
  * the ANIM table REGENERATED from the game data (tools/gen_anim_keys.py) and equal to the shipped text;
  * the stand-still gate asks FOURTH.cast_stops_caster first;
  * the visibility test is the first line of FOURTH.eg_class_ok and is in the non-commander picker's loop;
  * the visibility test blocks only an exact false (never a guessed hidden enemy).
No count gate moves (946 entries, 1,003 keys). No earlier gate needed a rebase."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_periods_risky_harness166\build_and_install167.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261117_anim_visibility_harness167\build_and_install168.py"
ANCHOR = ('print("ROUND 167 GATE OK: RISKY (%d keys) matches the game and keeps them on M by default; no final period on the "\n'
          '      "cards or the ALL text" % len(_r167))\n')
ADD = ANCHOR + r'''# ROUND 168: the cast animation decides the stand-still rule; the older pickers skip hidden enemies (2026-11-17).
import gen_anim_keys as _ga168
_a168 = _ga168.derive(script_txt)
assert ('FOURTH.ANIM_TEXT = "%s"\n' % _ga168.text(_a168)) in script_txt, \
    "BUILD REFUSED (round 168): the ANIM table differs from the game data"
assert "function FOURTH.blob_still(unit)\n\tif not FOURTH.cast_stops_caster() then return true end\n" in script_txt, \
    "BUILD REFUSED (round 168): the stand-still gate does not ask the cast animation"
assert "function FOURTH.eg_class_ok(enemy)\n\tif not FOURTH.enemy_not_hidden(enemy) then return false end" in script_txt \
    and "\t\t\t\t\t\t\t\tand FOURTH.enemy_not_hidden(enemy) then   -- ROUND 168" in script_txt, \
    "BUILD REFUSED (round 168): a picker lacks the visibility test"
assert "\treturn not (ok and vis == false)\n" in script_txt, \
    "BUILD REFUSED (round 168): the visibility test must block only an exact false"
print("ROUND 168 GATE OK: ANIM (%d of 1003 keys) matches the game; the stand-still gate asks it; both pickers skip "
      "hidden enemies" % len(_a168))
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1, src.count(ANCHOR)
src = src.replace(ANCHOR, ADD)
assert "os.remove(GAME_PACK)" not in src and "\u2014" not in ADD
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
