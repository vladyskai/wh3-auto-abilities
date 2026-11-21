#!/usr/bin/env python3
"""Build the round-189 build script from the round-188 one (the line of fire: the 35 'Requires line of sight to the
target' entries cast only along a line clear of every other unit and of the ground; user ruling 2026-11-21: "I would
just do the check for terrain on all 35 and units on all 35. Just let's be safe, and if it doesn't fire, that's okay.").

ROUND 189 GATE: FOURTH.LOS_TEXT equals the game data (tools/gen_los_keys.py, 56 keys, 35 ours); the eg_class_ok hook;
the poll's eg_caster / eg_los; the load loop's ability.los; the terrain read and the fail-closed returns; the TEST-ONLY
global ZZ_AUTO_TEST_NO_LOS is only ever read, never assigned."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_rangerule_harness187\build_and_install188.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_lineoffire_harness188\build_and_install189.py"

ANCHOR = 'print("ROUND 188 GATE OK: %d cast bounds on max(70%%, real - 20); named 80/80/55; the Executioner 230" % len(_c188))\n'
ADD = ANCHOR + r'''# ROUND 189: the line of fire (user 2026-11-21: "I would just do the check for terrain on all 35 and units on all 35.
# Just let's be safe, and if it doesn't fire, that's okay.").
import gen_los_keys as _g189
_k189 = _g189.derive()
assert len(_k189) == 56 and ("\n" + _g189.lua_text(_k189) + "\n") in script_txt, \
    "BUILD REFUSED (round 189): the LOS table differs from the game data"
_ours189 = sorted(k for k in _k189 if ('"%s"' % k) in script_txt)
assert len(_ours189) == 35, "BUILD REFUSED (round 189): %d line-of-sight keys are ours, expected 35" % len(_ours189)
for _t189 in ("\tif not FOURTH.eg_los_ok(enemy) then return false end   -- ROUND 189: never an enemy behind a blocked line\n",
              "\t\t\t\t\tFOURTH.eg_caster = unit   -- ROUND 189: the caster the line of fire is drawn from\n",
              "\t\t\t\t\tFOURTH.eg_los = (ability.los == true)   -- ROUND 189: the game's 'Requires line of sight'\n",
              "\tability.los = FOURTH.entry_los(ability)   -- ROUND 189: the line of fire (terrain and units)\n",
              "\tlocal ok, g = pcall(function() return bm:get_terrain_height(x, z) end)\n",
              "\nfunction FOURTH.los_block(caster, enemy)\n", "\nfunction FOURTH.eg_los_ok(enemy)\n",
              'return "the ground is unreadable", "read"', 'return "the flying read is unreadable", "read"',
              'return "a position is unreadable", "read"'):
    assert script_txt.count(_t189) >= 1, "BUILD REFUSED (round 189): missing %r" % _t189[:70]
assert script_txt.count("\tif not FOURTH.eg_los_ok(enemy) then return false end") == 1, \
    "BUILD REFUSED (round 189): the eg_class_ok hook must appear once"
assert "ZZ_AUTO_TEST_NO_LOS = " not in script_txt and script_txt.count("ZZ_AUTO_TEST_NO_LOS == true") == 1, \
    "BUILD REFUSED (round 189): the test-only global must only be read"
print("ROUND 189 GATE OK: the LOS table matches the game (56 keys, 35 ours); terrain and units checked, fail-closed")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
