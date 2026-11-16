#!/usr/bin/env python3
"""Build the round-161 build script from the round-160 one. No roster change, so no count gate moves.
Adds one gate: ally_melee_buff is in FOURTH.DEFAULT_ON_TRIGGERS (the 14 ally melee buffs start armed), and the four
round-159 friendly-fire / suicide families still start unarmed."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_beastmen_fixes_harness159\build_and_install160.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261116_ally_buffs_armed_harness160\build_and_install161.py"
ANCHOR = ('print("ROUND 160 GATE OK: when_ready skips a routing unit; instant abilities hold their unit one poll; the wind-up "\n'
          '      "table matches the game (%d of 917 keys have a wind-up)" % len(_wu160))\n')
ADD = ANCHOR + r'''# ROUND 161: the 14 ally melee buffs start armed (user ruling 2026-11-16, "Whole family").
_def161 = script_txt.split("FOURTH.DEFAULT_ON_TRIGGERS = {", 1)[1].split("\n}", 1)[0]
assert "\n\tally_melee_buff = true," in _def161, "ally_melee_buff does not start armed"
for _f161 in ("melee_clear", "fly_dive", "last_stand_clear", "enemy_blob_vortex"):
    assert ("\n\t%s = true," % _f161) not in _def161, "%s must still start unarmed" % _f161
assert script_txt.count('trigger = "ally_melee_buff"') == 14, "ally_melee_buff is not 14 entries"
print("ROUND 161 GATE OK: the 14 ally melee buffs start armed; the friendly-fire families still start unarmed")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1, src.count(ANCHOR)
src = src.replace(ANCHOR, ADD)
# rebase (documented in the round doc): the round-151 gate pins the exact default-armed family set; ally_melee_buff
# joins it by the user's 2026-11-16 ruling
PIN_OLD = "assert _fams == set(['ally_ammo_low', 'ally_heal', 'ally_wavering',"
PIN_NEW = "assert _fams == set(['ally_ammo_low', 'ally_heal', 'ally_melee_buff', 'ally_wavering',"
assert src.count(PIN_OLD) == 1, src.count(PIN_OLD)
src = src.replace(PIN_OLD, PIN_NEW)
assert "os.remove(GAME_PACK)" not in src
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
