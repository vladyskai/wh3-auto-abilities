#!/usr/bin/env python3
"""Build the round-191 build script from the round-190 one (group 1 of the stand-still audit; user 2026-11-21: "For now,
please only implement number 1.").

ROUND 191 GATE: FOURTH.STILL_GATE_TRIGGERS holds exactly the 8 group-1 triggers, each one wired in FOURTH.evaluators;
the wrapper asks FOURTH.blob_still; the load loop wraps the entries; Oil Flask and Celestial Comet are still animated
by the game data (FOURTH.ANIM)."""
SRC = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_shotstill_harness189\build_and_install190.py"
DST = r"C:\Users\vlady\Desktop\WH3_mod\mod_source\releases\20261121_still1_harness190\build_and_install191.py"

ANCHOR = 'print("ROUND 190 GATE OK: every shot trigger asks the animation before casting on the move (7 lines)")\n'
ADD = ANCHOR + r'''# ROUND 191: the animation decides in group 1 (user 2026-11-21: "For now, please only implement number 1.").
_m191 = re.search(r"\nFOURTH\.STILL_GATE_TRIGGERS = \{\n(.*?)\n\}\n", script_txt, re.S)
assert _m191 is not None, "BUILD REFUSED (round 191): FOURTH.STILL_GATE_TRIGGERS is missing"
_set191 = set(re.findall(r"(\w+) = true", _m191.group(1)))
_want191 = {"enemy_ground_melee_infantry", "enemy_ground_melee", "enemy_engaged_or_shot", "enemy_melee",
            "enemy_fast_near_ally", "enemy_melee_or_fast", "enemy_melee_noncommander", "enemy_missile_shooting"}
assert _set191 == _want191, "BUILD REFUSED (round 191): the stand-still set is %s" % sorted(_set191)
for _t191 in sorted(_set191):
    assert ("\t%s = FOURTH.evaluate_" % _t191) in script_txt, "BUILD REFUSED (round 191): %s is not a wired trigger" % _t191
assert script_txt.count("\t\tif not FOURTH.blob_still(unit) then return nil end   -- ROUND 191: a moving caster waits") == 1, \
    "BUILD REFUSED (round 191): the wrapper must ask FOURTH.blob_still"
assert script_txt.count("\t\tability.evaluate = FOURTH.still_wrap(ability.evaluate)   -- ROUND 191") == 1, \
    "BUILD REFUSED (round 191): the load loop must wrap the group-1 entries"
_anim191 = set(re.search(r'\nFOURTH\.ANIM_TEXT = "([^"]*)"', script_txt).group(1).split(";"))
for _k191 in ("wh2_dlc13_lord_abilities_oil_flask", "wh3_main_mount_bound_celestial_comet"):
    assert _k191 in _anim191, "BUILD REFUSED (round 191): %s lost its animation in the table" % _k191
print("ROUND 191 GATE OK: the 8 group-1 triggers wait for an animated caster to stand still")
'''
src = open(SRC, encoding="utf-8").read()
assert src.count(ANCHOR) == 1
src = src.replace(ANCHOR, ADD)
open(DST, "w", encoding="utf-8", newline="\n").write(src)
print("wrote", DST)
