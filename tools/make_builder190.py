#!/usr/bin/env python3
"""Build the round-190 build script from the round-189 one (the animation decides in every shot trigger; user
2026-11-21: "Amber Bow canceled his movement, not good" -> "Fix the 8").

ROUND 190 GATE: the 7 ROUND 190 stand-still lines, the old 'if still and not FOURTH.blob_still' line gone, and the 8
animated shot entries are still animated by the game data (FOURTH.ANIM)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_lineoffire_harness188\build_and_install189.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_shotstill_harness189\build_and_install190.py"

ANCHOR = 'print("ROUND 189 GATE OK: the LOS table matches the game (56 keys, 35 ours); terrain and units checked, fail-closed")\n'
ADD = ANCHOR + r'''# ROUND 190: the animation decides in every shot trigger (user 2026-11-21: "Fix the 8").
_t190 = "   -- ROUND 190: the animation decides (Amber Bow stopped a walking Markus)"
assert script_txt.count(_t190) == 7, "BUILD REFUSED (round 190): %d stand-still lines, want 7" % script_txt.count(_t190)
assert "\tif still and not FOURTH.blob_still(unit) then return false end" not in script_txt, \
    "BUILD REFUSED (round 190): the shot caster check must not leave standing to the family"
_anim190 = set(re.search(r'\nFOURTH\.ANIM_TEXT = "([^"]*)"', script_txt).group(1).split(";"))
for _k190 in ("wh2_dlc13_weapon_abilities_amber_bow", "wh2_dlc15_spell_bound_gaze_of_nagash",
              "wh3_main_weapon_abilities_godkiller_pistol", "wh3_dlc27_item_abilities_schalkains_teeth",
              "wh2_dlc15_character_abilities_goggly_glare", "wh3_dlc27_character_abilities_the_black_tongue"):
    assert _k190 in _anim190, "BUILD REFUSED (round 190): %s lost its animation in the table" % _k190
print("ROUND 190 GATE OK: every shot trigger asks the animation before casting on the move (7 lines)")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
